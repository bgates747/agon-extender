import {
  BrowserCreditState,
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
const gapsNode = document.querySelector("#gaps");

// Opt-in diagnostic page (?timing=on, or off for overhead comparison).
// Same-clock durations only. rAF submission is not physical display scanout.
const timingMode = new URLSearchParams(location.search).get('timing');
const timingRows = new Array(8192);
let timingCount = 0, timingStarted = false, timingStartUTC = null;
let videoSession = 0;
function timing(event, data = {}) {
  if (timingMode === null) return;
  timingRows[timingCount++ % timingRows.length] = {ms:performance.now(), event, ...data};
}
function sessionId() { return crypto.getRandomValues(new Uint32Array(1))[0] || 1; }
function timingSnapshot() {
  const start = Math.max(0,timingCount-timingRows.length);
  return {schema:1, mode:timingMode, start_utc:timingStartUTC,
    clock:'browser performance.now milliseconds; draw submission is not scanout',
    total:timingCount, overwritten:start,
    rows:Array.from({length:timingCount-start},(_,i)=>timingRows[(start+i)%timingRows.length])};
}

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
}

function updateStats(frame) {
  sequenceNode.textContent = String(frame.sequence);
  surfaceNode.textContent = `${frame.width}×${frame.height} RGB888`;
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
  if(pendingFrame) timing("frame_superseded",{sid:videoSession,seq:pendingFrame.frame.sequence});
  timing("frame_received",{sid:videoSession,seq:frame.sequence});
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
      timing("frame_submitted",{sid:videoSession,seq:accepted.frame.sequence});
      ++presented;
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
  if (oldSocket && oldSocket.readyState < WebSocket.CLOSING) { timing("video_close_local",{sid:videoSession}); oldSocket.close(); }
}

function stopDemo() {
  if (demoTimer !== null) {
    clearInterval(demoTimer);
    demoTimer = null;
  }
}

async function connect() {
  if(timingMode!==null && !timingStarted) {
    timingStartUTC=new Date().toISOString();
    try {
      const r=await fetch(`/diagnostics?${timingMode==='off'?'off':'on'}`,{cache:'no-store'});
      if(!r.ok || (await r.text())!=='ok') throw new Error('P4 timing setup failed');
      timingStarted=true;
    } catch(e) { setState(e.message); return; }
  }
  stopDemo();
  disconnect();
  resetStats();

  videoSession=sessionId();
  const endpoint = defaultEndpoint()+(timingMode!==null?`?sid=${videoSession}`:'');
  setState(`connecting ${endpoint}`);
  const candidate = new WebSocket(endpoint);
  candidate.binaryType = "arraybuffer";
  socket = candidate;

  candidate.addEventListener("open", () => {
    if (socket !== candidate) return;
    timing("video_open",{sid:videoSession});
    setState(`connected ${endpoint}`);
    credit.opened(sendCredit);
  });
  candidate.addEventListener("message", (event) => {
    if (socket === candidate) onSocketMessage(event);
  });
  const thisVideoSession=videoSession;
  candidate.addEventListener("close", event => {
    timing("video_close",{sid:thisVideoSession,code:event.code,reason:event.reason,clean:event.wasClean});
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
  setState("local EVF1 RGB888 test pattern");
  demoSequence = 0;
  const queueDemoFrame = () => {
    if (pendingFrame) return;
    const frame = parseFrame(makeDemoFrame({ sequence: demoSequence++ }));
    acceptFrame(frame, false);
  };
  queueDemoFrame();
  demoTimer = setInterval(queueDemoFrame, 200);
}

connectButton.addEventListener("click", connect);
demoButton.addEventListener("click", startDemo);

if (new URLSearchParams(location.search).has("demo")) startDemo();

// Focused keyboard experiment: no local echo. P4 renders only bytes returned
// by EMOS. Browser repeat supplies repeated down events; P4 retains key-up
// identity when Shift/Caps changes while a physical key is held.
const keyButton = document.querySelector('#keyboard');
const keyState = document.querySelector('#keyboard-state');
let keySocket = null;
let keyQueue = [];
let keyPending = false;
let keyCaptured = false;
let keyAckAt = 0;
let keySession=0, keyOrdinal=0, keyEventOrdinal=0;
function physicalKey(code) {
  if (/^Key[A-Z]$/.test(code)) return 4 + code.charCodeAt(3) - 65;
  if (/^Digit[0-9]$/.test(code)) return code[5] === '0' ? 39 : 29 + Number(code[5]);
  return ({Enter:40,Escape:41,Backspace:42,Tab:43,Space:44,Minus:45,Equal:46,
    BracketLeft:47,BracketRight:48,Backslash:49,Semicolon:51,Quote:52,
    Backquote:53,Comma:54,Period:55,Slash:56,CapsLock:57,
    ControlLeft:224,ShiftLeft:225,AltLeft:226,MetaLeft:227,
    ControlRight:228,ShiftRight:229,AltRight:230,MetaRight:231})[code] || 0;
}
function releaseKeyboard(reason = 'Keyboard released; click Capture keyboard to resume') {
  keyCaptured = false;
  keyQueue = [];
  const old = keySocket;
  keySocket = null;
  keyPending = false;
  if (old) { timing("key_release_local",{sid:keySession,reason}); old.close(); } // P4 disconnect or independent two-second lease releases keys.
  keyState.textContent = reason;
  canvas.classList.remove('keyboard-focus');
}
function pumpKeyboard() {
  if (!keySocket || keySocket.readyState !== WebSocket.OPEN || keyPending || !keyQueue.length) return;
  if (keySocket.bufferedAmount) { releaseKeyboard('Keyboard congestion; capture again'); return; }
  keyPending = true;
  keyAckAt = performance.now();
  const queued=keyQueue.shift();
  ++keyOrdinal;
  timing("key_send",{sid:keySession,ordinal:keyOrdinal,event_id:queued.event_id,bytes:queued.bytes});
  keySocket.send(new Uint8Array(queued.bytes));
}
function queueKeyboard(bytes, event_id = 0) {
  if (keyQueue.length >= 64) { releaseKeyboard('Keyboard queue full; capture again'); return; }
  keyQueue.push({bytes,event_id}); pumpKeyboard();
}
keyButton.addEventListener('click', () => {
  releaseKeyboard();
  if (!socket || socket.readyState !== WebSocket.OPEN || demoTimer) {
    keyState.textContent = 'Connect the live display first'; return;
  }
  canvas.focus();
  keySession=sessionId(); keyOrdinal=0;
  const thisKeySession=keySession;
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/keyboard${timingMode!==null?`?sid=${keySession}`:''}`);
  ws.binaryType = 'arraybuffer';
  keySocket = ws;
  keyState.textContent = 'Requesting keyboard capture…';
  ws.onopen = () => { if (keySocket===ws && document.activeElement===canvas) queueKeyboard([84]); else ws.close(); };
  ws.onmessage = event => {
    if (keySocket!==ws) return;
    const ack = new Uint8Array(event.data);
    if (!keyPending || ack.length!==1 || ack[0]!==65) { releaseKeyboard('Keyboard protocol error'); return; }
    timing("key_ack",{sid:keySession,ordinal:keyOrdinal});
    keyPending = false; keyCaptured = true;
    canvas.classList.add('keyboard-focus');
    keyState.textContent = 'Keyboard captured · US layout · Escape exits the Agon sample';
    pumpKeyboard();
  };
  ws.onclose = event => { timing('key_close',{sid:thisKeySession,code:event.code,reason:event.reason,clean:event.wasClean}); if (keySocket===ws) releaseKeyboard('Keyboard unavailable or released; start the Agon sample, then capture again'); };
  ws.onerror = () => { if (keySocket===ws) releaseKeyboard('Keyboard connection failed'); };
});
function forwardKey(event, down) {
  if (!keyCaptured || document.activeElement!==canvas || event.isComposing) return;
  // Tab remains browser navigation, and operating-system shortcuts remain
  // local. Revoke instead of leaving a modifier held remotely.
  if (event.code==='Tab' || event.metaKey || event.altKey) { releaseKeyboard(); return; }
  const physical = physicalKey(event.code);
  if (!physical) return;
  event.preventDefault();
  const mods = (event.ctrlKey?1:0)|(event.shiftKey?2:0)|
    (event.getModifierState('CapsLock')?16:0)|(event.getModifierState('NumLock')?32:0);
  const event_id=++keyEventOrdinal;
  timing("key_event",{sid:keySession,event_id,physical,mods,down,repeat:event.repeat});
  queueKeyboard([75,physical,mods,down],event_id);
}
canvas.addEventListener('keydown', event => forwardKey(event,1));
canvas.addEventListener('keyup', event => forwardKey(event,0));
canvas.addEventListener('compositionstart', () => releaseKeyboard('Composition input is unavailable in this US typing test'));
canvas.addEventListener('blur', () => { timing('canvas_blur'); releaseKeyboard(); });
window.addEventListener('blur', () => { timing('window_blur'); releaseKeyboard(); });
document.addEventListener('visibilitychange', () => { timing('visibility',{hidden:document.hidden}); if (document.hidden) releaseKeyboard(); });
setInterval(() => {
  if (!keySocket) return;
  if (!socket || socket.readyState!==WebSocket.OPEN || document.activeElement!==canvas) { releaseKeyboard(); return; }
  if (keyPending && performance.now()-keyAckAt>1500) { releaseKeyboard('Keyboard acknowledgement timeout'); return; }
  if (keyCaptured && !keyPending && !keyQueue.length) queueKeyboard([72]);
}, 500);

canvas.addEventListener('click', () => { if (!keyCaptured && !keySocket) keyButton.click(); });

const timingButton=document.querySelector('#timing-download');
timingButton.hidden=timingMode===null;
timingButton.addEventListener('click',async()=>{
  releaseKeyboard('Keyboard released for timing export'); disconnect();
  timing('export_requested');
  // Always save browser evidence, even if P4 is unreachable after a failure.
  let p4=null, error=null;
  try {
    const r=await fetch('/diagnostics',{cache:'no-store',signal:AbortSignal.timeout(15000)});
    if(!r.ok) throw new Error(`P4 export HTTP ${r.status}`);
    p4=await r.text();
  } catch(e) { error=String(e); }
  const report={...timingSnapshot(),p4,p4_export_error:error};
  const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob), a=document.createElement('a');
  const stamp=(timingStartUTC||new Date().toISOString()).replace(/\.\d+Z$/,'Z').replace('T','-').replaceAll(':','-');
  a.href=url; a.download=`REMOTE-001-${stamp}.json`; a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
  setState(error?'Browser timing saved; P4 export failed':'Timing saved; reload this page before a new measurement');
});
