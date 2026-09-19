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
  surfaceNode.textContent = `${frame.width}×${frame.height} ${frame.pixelFormat === PixelFormat.RGB222 ? "RGB222" : "RGB888"}`;
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

  const endpoint = defaultEndpoint();
  setState(`connecting ${endpoint}`);
  const candidate = new WebSocket(endpoint);
  candidate.binaryType = "arraybuffer";
  socket = candidate;

  candidate.addEventListener("open", () => {
    if (socket !== candidate) return;
    setState(`connected ${endpoint}`);
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
fullscreenButton.disabled = !document.fullscreenEnabled;
fullscreenButton.addEventListener("click", async () => {
  try {
    if (document.fullscreenElement === videoPanel) await document.exitFullscreen();
    else await videoPanel.requestFullscreen();
    fullscreenButton.blur();
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
  const locksPanel = document.querySelector('#keyboard-locks');
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
  const locks = ['CapsLock', 'NumLock', 'ScrollLock'].map((name, i) => {
    const label = document.createElement('label');
    const select = document.createElement('select');
    for (const [value,text] of [['auto','Host state (unknown)'],['off','Manual off'],['on','Manual on']]) {
      const option=document.createElement('option'); option.value=value; option.textContent=text; select.append(option);
    }
    label.append(`${name}: `,select); locksPanel.append(label);
    const lock={name,bit:16<<i,known:false,value:false,select};
    select.addEventListener('change', () => { if(captured) send(5); });
    return lock;
  });
  function snapshot() {
    let known=0, value=0;
    for(const lock of locks) {
      if(lock.select.value!=='auto' || lock.known) {
        known|=lock.bit;
        if(lock.select.value==='on' || (lock.select.value==='auto' && lock.value)) value|=lock.bit;
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
        lock.select.options[0].textContent=`Host state (${value?'on':'off'})`;
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
  button.addEventListener('click', event => {
    if(captured || requested) { release();return; }
    for(const lock of locks) { lock.known=false;lock.select.options[0].textContent='Host state (unknown)'; }
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
      const manualLock=locks.find(lock=>lock.name===event.code && lock.select.value!=='auto');
      if(manualLock)manualLock.select.value=manualLock.select.value==='on'?'off':'on';
      const {known}=snapshot();
      if((usage>=4 && usage<=29 && !(known&16)) || (usage>=89 && usage<=99 && !(known&32))) {
        status.textContent='Choose a manual lock state below; this key was not sent';return;
      }
      if(send(2,usage,1))held.add(usage);
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
  document.querySelector('#exit-fullscreen').addEventListener('click',()=>{
    release();if(document.fullscreenElement)document.exitFullscreen();
  });
  setInterval(()=>{
    if(requested && performance.now()-lastReply>5000)release('Keyboard admission timed out');
    if(captured) {
      if(performance.now()-lastReply>5000)release('Keyboard heartbeat lost');
      else send(3);
    }
  },1000);
})();
