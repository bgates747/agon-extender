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
