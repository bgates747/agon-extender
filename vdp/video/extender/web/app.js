import {
  BrowserCreditState,
  PixelFormat,
  FrameProtocolError,
  makeDemoFrame,
  parseFrame,
} from "./frame_protocol.js";
import { WebGL2Presenter } from "./webgl2_presenter.js";

const canvas = document.querySelector("#screen");
const connectButton = document.querySelector("#connect");
const demoButton = document.querySelector("#demo");
const stateNode = document.querySelector("#state");
const sequenceNode = document.querySelector("#sequence");
const surfaceNode = document.querySelector("#surface");
const strideNode = document.querySelector("#stride");
const periodNode = document.querySelector("#period");
const receivedNode = document.querySelector("#received");
const presentedNode = document.querySelector("#presented");
const fpsNode = document.querySelector("#fps");
const gapsNode = document.querySelector("#gaps");

const presenter = new WebGL2Presenter(canvas);
const credit = new BrowserCreditState();

let socket = null;
let pendingFrame = null;
let received = 0;
let presented = 0;
let sequenceGaps = 0;
let lastSequence = null;
let demoTimer = null;
let demoSequence = 0;
let rateStart = performance.now();
let rateFrames = 0;
let statusAbort = null;
let statusTimer = null;

function stopDisplayStatus() {
  clearTimeout(statusTimer);
  statusTimer = null;
  statusAbort?.abort();
  statusAbort = null;
  connectButton.classList.remove("connected");
  surfaceNode.textContent = "Display status unavailable";
}

async function pollDisplayStatus(owner) {
  if (socket !== owner || owner.readyState !== WebSocket.OPEN) return;
  const request = new AbortController();
  statusAbort = request;
  const timeout = setTimeout(() => request.abort(), 2000);
  try {
    const response = await fetch("/display/status", {cache:"no-store", signal:request.signal});
    if (!response.ok) throw new Error("status unavailable");
    const value = await response.json();
    if (!value.available || !Number.isInteger(value.mode) || value.mode < 0 ||
        ![value.width,value.height,value.colors,value.refresh_hz].every(n => Number.isInteger(n) && n > 0) ||
        typeof value.double_buffered !== "boolean") throw new Error("invalid display status");
    if (socket === owner) surfaceNode.textContent =
      `Mode ${value.mode} ${value.width}x${value.height} ${value.colors} colors ${value.refresh_hz} Hz ${value.double_buffered ? "double" : "single"}-buffered`;
  } catch (error) {
    if (socket === owner) surfaceNode.textContent = "Display status unavailable";
  } finally {
    clearTimeout(timeout);
    if (statusAbort === request) statusAbort = null;
    if (socket === owner && owner.readyState === WebSocket.OPEN)
      statusTimer = setTimeout(() => pollDisplayStatus(owner), 1000);
  }
}

function defaultEndpoint() {
  const scheme = location.protocol === "https:" ? "wss:" : "ws:";
  return `${scheme}//${location.host}/video`;
}

function setState(text) {
  stateNode.textContent = text;
}

function resetStats() {
  pendingFrame = null;
  received = 0;
  presented = 0;
  sequenceGaps = 0;
  lastSequence = null;
  receivedNode.textContent = "0";
  presentedNode.textContent = "0";
  gapsNode.textContent = "0";
  fpsNode.textContent = "—";
  rateStart = performance.now();
  rateFrames = 0;
}

function updateStats(frame) {
  sequenceNode.textContent = String(frame.sequence);
  if (demoTimer !== null) surfaceNode.textContent = `Local pattern ${frame.width}x${frame.height}`;
  strideNode.textContent = `${frame.strideBytes} B`;
  periodNode.textContent = frame.presentPeriodUs
    ? `${frame.presentPeriodUs} µs`
    : "unspecified";
  receivedNode.textContent = String(received);
  presentedNode.textContent = String(presented);
  gapsNode.textContent = String(sequenceGaps);
}

function accountSequence(sequence) {
  if (lastSequence !== null) {
    const expected = (lastSequence + 1) >>> 0;
    const delta = (sequence - expected) >>> 0;
    if (delta < 0x80000000) sequenceGaps += delta;
  }
  lastSequence = sequence;
}

function acceptFrame(frame, usesCredit) {
  if (usesCredit) credit.acceptedFrame();
  ++received;
  accountSequence(frame.sequence);
  pendingFrame = { frame, usesCredit };
  updateStats(frame);
}

function sendCredit(request) {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send(request);
}

function closeForProtocol(error) {
  console.error(error);
  setState(`frame error: ${error.message}`);
  if (socket && socket.readyState < WebSocket.CLOSING) {
    socket.close(1002, "invalid EVF1 frame");
  }
}

function animationLoop() {
  if (pendingFrame) {
    const accepted = pendingFrame;
    pendingFrame = null;
    try {
      presenter.present(accepted.frame);
      ++presented;
      ++rateFrames;
      const now = performance.now();
      if (now - rateStart >= 1000) {
        fpsNode.textContent = (rateFrames * 1000 / (now - rateStart)).toFixed(1);
        rateStart = now;
        rateFrames = 0;
      }
      updateStats(accepted.frame);
      if (accepted.usesCredit) credit.presented(sendCredit);
    } catch (error) {
      console.error(error);
      setState(`presentation error: ${error.message}`);
      if (socket && socket.readyState < WebSocket.CLOSING) {
        socket.close(1011, "browser presentation failure");
      }
    }
  }
  requestAnimationFrame(animationLoop);
}
requestAnimationFrame(animationLoop);

function onSocketMessage(event) {
  try {
    if (!(event.data instanceof ArrayBuffer)) {
      throw new FrameProtocolError("message-type", "video message is not binary");
    }
    acceptFrame(parseFrame(event.data), true);
  } catch (error) {
    closeForProtocol(error);
  }
}

function disconnect() {
  stopDisplayStatus();
  const oldSocket = socket;
  socket = null;
  pendingFrame = null;
  credit.disconnected();
  if (oldSocket && oldSocket.readyState < WebSocket.CLOSING) oldSocket.close();
}

function stopDemo() {
  if (demoTimer !== null) {
    clearInterval(demoTimer);
    demoTimer = null;
  }
}

function connect() {
  stopDemo();
  disconnect();
  resetStats();

  // Negotiate the installed lossless codecs; presentation-credit pacing is unchanged.
  const endpoint = defaultEndpoint() + "?rle2=1&packed=2";
  setState(`connecting ${endpoint}`);
  const candidate = new WebSocket(endpoint);
  candidate.binaryType = "arraybuffer";
  socket = candidate;

  candidate.addEventListener("open", () => {
    if (socket !== candidate) return;
    setState(`connected ${endpoint}`);
    connectButton.classList.add("connected");
    pollDisplayStatus(candidate);
    credit.opened(sendCredit);
  });
  candidate.addEventListener("message", (event) => {
    if (socket === candidate) onSocketMessage(event);
  });
  candidate.addEventListener("close", () => {
    if (socket !== candidate) return;
    socket = null;
    pendingFrame = null;
    credit.disconnected();
    stopDisplayStatus();
    setState("disconnected");
  });
  candidate.addEventListener("error", () => {
    if (socket === candidate) setState("websocket error");
  });
}

function startDemo() {
  disconnect();
  stopDemo();
  resetStats();
  setState("local RGB222 test pattern");
  demoSequence = 0;
  const queueDemoFrame = () => {
    if (pendingFrame) return;
    const frame = parseFrame(makeDemoFrame({ sequence: demoSequence++, pixelFormat: PixelFormat.RGB222 }));
    acceptFrame(frame, false);
  };
  queueDemoFrame();
  demoTimer = setInterval(queueDemoFrame, 1000 / 60);
}

connectButton.addEventListener("click", connect);
demoButton.addEventListener("click", startDemo);

if (new URLSearchParams(location.search).has("demo")) startDemo();


const videoPanel = document.querySelector("#video-panel");
const fullscreenButton = document.querySelector("#fullscreen");
const videoViewport = document.querySelector("#video-viewport");
new ResizeObserver(([entry]) => {
  videoViewport.style.setProperty("--view-width", `${entry.contentRect.width}px`);
  videoViewport.style.setProperty("--view-height", `${entry.contentRect.height}px`);
}).observe(videoViewport);
fullscreenButton.disabled = !document.fullscreenEnabled;
fullscreenButton.addEventListener("click", async () => {
  try {
    if (document.fullscreenElement === videoPanel) await document.exitFullscreen();
    else await videoPanel.requestFullscreen();
    // Transfer focus within the panel. Blurring to no destination makes the
    // focusout handler revoke capture before fullscreenchange can restore it.
    canvas.focus();
  } catch (error) {
    setState(`Fullscreen unavailable: ${error.message}`);
  }
});
document.addEventListener("fullscreenchange", () => {
  const active = document.fullscreenElement === videoPanel;
  fullscreenButton.textContent = active ? "Exit fullscreen" : "Fullscreen";
  fullscreenButton.setAttribute("aria-label", active ? "Exit fullscreen" : "Enter fullscreen");
});

// Browser input has its own socket and lifecycle. Video reconnect/credits never
// acquire or release it. Only P4 acknowledgements establish capture ownership.
(() => {
  const panel = document.querySelector('#video-panel');
  const canvas = document.querySelector('#screen');
  const button = document.querySelector('#capture-keyboard');
  const status = document.querySelector('#keyboard-state');
  let socket, generation = 0, sequence = 0, requested = false, captured = false;
  let lastReply = 0;
  const held = new Set();
  const codes = {Enter:40, Escape:41, Backspace:42, Tab:43, Space:44,
    Minus:45, Equal:46, BracketLeft:47, BracketRight:48, Backslash:49,
    Semicolon:51, Quote:52, Backquote:53, Comma:54, Period:55, Slash:56,
    CapsLock:57, ScrollLock:71, Insert:73, Home:74, PageUp:75, Delete:76,
    End:77, PageDown:78, ArrowRight:79, ArrowLeft:80, ArrowDown:81, ArrowUp:82,
    NumLock:83, NumpadDivide:84, NumpadMultiply:85, NumpadSubtract:86,
    NumpadAdd:87, NumpadEnter:88, Numpad0:98, NumpadDecimal:99, IntlBackslash:100,
    ControlLeft:224, ShiftLeft:225, AltLeft:226, MetaLeft:227,
    ControlRight:228, ShiftRight:229, AltRight:230, MetaRight:231};
  for (let i=0; i<26; ++i) codes[`Key${String.fromCharCode(65+i)}`]=4+i;
  for (let i=1; i<=9; ++i) { codes[`Digit${i}`]=29+i; codes[`Numpad${i}`]=88+i; }
  codes.Digit0=39;
  for (let i=1; i<=12; ++i) codes[`F${i}`]=57+i;
  const locks = ['CapsLock', 'NumLock', 'ScrollLock'].map((name, i) =>
    ({name, bit:16<<i, known:false, value:false}));
  function snapshot() {
    let known=0, value=0;
    for(const lock of locks) {
      if(lock.known) {
        known|=lock.bit;
        if(lock.value) value|=lock.bit;
      }
    }
    return {known,value};
  }
  function observe(event) {
    for(const lock of locks) {
      // false alone cannot distinguish unsupported reporting from an off lock.
      // A true observation establishes support. Letters also corroborate Caps.
      const value=event.getModifierState?.(lock.name);
      let reliable=value===true || lock.known;
      if(lock.name==='CapsLock' && /^Key[A-Z]$/.test(event.code || '') && /^[a-zA-Z]$/.test(event.key || '')) {
        const inferred=(event.key===event.key.toUpperCase())!==event.shiftKey;
        reliable=typeof value==='boolean' && value===inferred;
      }
      if(reliable && typeof value==='boolean') {
        lock.known=true;lock.value=value;
      }
    }
  }
  function reset(message) {
    captured=requested=false;held.clear();generation=sequence=0;
    button.textContent='Capture keyboard';button.setAttribute('aria-pressed','false');
    status.textContent=message;
  }
  function send(op, usage=0, down=0) {
    if(socket?.readyState!==WebSocket.OPEN) return false;
    if(socket.bufferedAmount>4096) { release('Keyboard released: input queue full'); return false; }
    const data=new Uint8Array(16), view=new DataView(data.buffer);
    data.set([66,75,1,op]);view.setUint32(4,generation,true);view.setUint32(8,++sequence,true);
    data[12]=usage;data[13]=down;
    if(op!==1) { const s=snapshot();data[14]=s.known;data[15]=s.value; }
    socket.send(data);return true;
  }
  function release(message='Keyboard released') {
    // Close also covers an admission reply still in flight; never auto-recapture.
    if(socket) { const old=socket;socket=undefined;old.close(); }
    reset(message);
  }
  window.addEventListener('agon-reset-request',()=>release('Keyboard released for reset'));
  button.addEventListener('click', event => {
    if(captured || requested) { release();return; }
    for(const lock of locks) { lock.known=false;lock.value=false; }
    observe(event);requested=true;lastReply=performance.now();status.textContent='Requesting keyboard…';
    canvas.focus();
    const ws=new WebSocket(`${location.protocol==='https:'?'wss':'ws'}://${location.host}/keyboard/browser`);
    socket=ws;ws.binaryType='arraybuffer';
    ws.onopen=()=>{if(socket===ws)send(1);};
    ws.onmessage=event=>{
      if(socket!==ws)return;
      const data=new Uint8Array(event.data);
      if(data.length!==16 || data[0]!==66 || data[1]!==75 || data[2]!==1) { release('Keyboard protocol error');return; }
      if(data[3]!==0) { release(data[3]===2?'Keyboard unavailable: select Extender input and release physical keys':'Keyboard released by P4; capture again');return; }
      lastReply=performance.now();
      if(requested) {
        generation=new DataView(data.buffer).getUint32(4,true);requested=false;captured=true;
        button.textContent='Release keyboard';button.setAttribute('aria-pressed','true');
        status.textContent='Keyboard captured';canvas.focus();
      }
    };
    ws.onclose=()=>{if(socket===ws){socket=undefined;reset('Keyboard disconnected; capture again');}};
    ws.onerror=()=>{if(socket===ws)release('Keyboard connection failed');};
  });
  function key(event, down) {
    if(!captured || event.isComposing)return;
    const usage=codes[event.code];
    if(usage===undefined) { status.textContent=`Unsupported key: ${event.code || event.key}`;return; }
    event.preventDefault();event.stopPropagation();
    if(event.repeat)return;
    observe(event);
    if(down) {
      if(held.has(usage))return;
      const {known}=snapshot();
      if((usage>=4 && usage<=29 && !(known&16)) || (usage>=89 && usage<=99 && !(known&32))) {
        status.textContent='Host lock state unavailable; this key was not sent';return;
      }
      if(send(2,usage,1)) { held.add(usage);status.textContent='Keyboard captured'; }
    } else if(held.delete(usage)) send(2,usage,0);
  }
  canvas.addEventListener('blur',()=>{
    if(captured) { for(const usage of held)send(2,usage,0);held.clear(); }
  });
  canvas.addEventListener('keydown',e=>key(e,true));
  canvas.addEventListener('keyup',e=>key(e,false));
  window.addEventListener('blur',()=>release());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)release();});
  panel.addEventListener('focusout',event=>{
    if(!panel.contains(event.relatedTarget) && (captured || requested))release();
  });
  window.addEventListener('pagehide',()=>release());
  document.addEventListener('fullscreenchange',()=>{
    if(captured)canvas.focus();
  });
  setInterval(()=>{
    if(requested && performance.now()-lastReply>5000)release('Keyboard admission timed out');
    if(captured) {
      if(performance.now()-lastReply>5000)release('Keyboard heartbeat lost');
      else send(3);
    }
  },1000);
})();

// Optional bench actuator. Endpoint is supplied only by the deployment profile.
{
  const button=document.querySelector('#reset-agon');
  const endpoint=document.querySelector('meta[name="agon-reset-url"]')?.content;
  button.disabled=!endpoint;
  button.title=endpoint?'Reset Agon through the bench Pi':'Reset bridge not configured';
  button.addEventListener('click',async()=>{
    if(!confirm('Reset Agon now? This interrupts the running program.'))return;
    window.dispatchEvent(new Event('agon-reset-request'));
    button.disabled=true;
    const bytes=crypto.getRandomValues(new Uint8Array(16));
    bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;
    const h=Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
    const id=`${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),7000);
    try {
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','X-Agon-Reset':'1'},body:JSON.stringify({id}),signal:controller.signal});
      const result=await response.json();
      if(!response.ok||result.pulse!=='released')throw Error(result.error||'Reset not confirmed');
    } catch(error) {
      alert('Reset not confirmed. Check Agon before trying again.');
    } finally {clearTimeout(timer);button.disabled=false;}
  });
}
