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
  if (old) old.close(); // P4 disconnect or independent two-second lease releases keys.
  keyState.textContent = reason;
  canvas.classList.remove('keyboard-focus');
}
function pumpKeyboard() {
  if (!keySocket || keySocket.readyState !== WebSocket.OPEN || keyPending || !keyQueue.length) return;
  if (keySocket.bufferedAmount) { releaseKeyboard('Keyboard congestion; capture again'); return; }
  keyPending = true;
  keyAckAt = performance.now();
  keySocket.send(new Uint8Array(keyQueue.shift()));
}
function queueKeyboard(bytes) {
  if (keyQueue.length >= 64) { releaseKeyboard('Keyboard queue full; capture again'); return; }
  keyQueue.push(bytes); pumpKeyboard();
}
keyButton.addEventListener('click', () => {
  releaseKeyboard();
  if (!socket || socket.readyState !== WebSocket.OPEN || demoTimer) {
    keyState.textContent = 'Connect the live display first'; return;
  }
  canvas.focus();
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/keyboard`);
  ws.binaryType = 'arraybuffer';
  keySocket = ws;
  keyState.textContent = 'Requesting keyboard capture…';
  ws.onopen = () => { if (keySocket===ws && document.activeElement===canvas) queueKeyboard([84]); else ws.close(); };
  ws.onmessage = event => {
    if (keySocket!==ws) return;
    const ack = new Uint8Array(event.data);
    if (!keyPending || ack.length!==1 || ack[0]!==65) { releaseKeyboard('Keyboard protocol error'); return; }
    keyPending = false; keyCaptured = true;
    canvas.classList.add('keyboard-focus');
    keyState.textContent = 'Keyboard captured · US layout · Escape exits the Agon sample';
    pumpKeyboard();
  };
  ws.onclose = () => { if (keySocket===ws) releaseKeyboard('Keyboard unavailable or released; start the Agon sample, then capture again'); };
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
  queueKeyboard([75,physical,mods,down]);
}
canvas.addEventListener('keydown', event => forwardKey(event,1));
canvas.addEventListener('keyup', event => forwardKey(event,0));
canvas.addEventListener('compositionstart', () => releaseKeyboard('Composition input is unavailable in this US typing test'));
canvas.addEventListener('blur', () => releaseKeyboard());
window.addEventListener('blur', () => releaseKeyboard());
document.addEventListener('visibilitychange', () => { if (document.hidden) releaseKeyboard(); });
setInterval(() => {
  if (!keySocket) return;
  if (!socket || socket.readyState!==WebSocket.OPEN || document.activeElement!==canvas) { releaseKeyboard(); return; }
  if (keyPending && performance.now()-keyAckAt>1500) { releaseKeyboard('Keyboard acknowledgement timeout'); return; }
  if (keyCaptured && !keyPending && !keyQueue.length) queueKeyboard([72]);
}, 500);

canvas.addEventListener('click', () => { if (!keyCaptured && !keySocket) keyButton.click(); });
