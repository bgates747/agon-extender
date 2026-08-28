// This is a browser-native test of the production EVF1 parser and browser
// credit state. It deliberately needs no Node package tree or test framework.
import {
  BrowserCreditState,
  FRAME_HEADER_BYTES,
  FRAME_REQUEST,
  FrameProtocolError,
  makeDemoFrame,
  parseFrame,
} from "/vdp/video/extender/web/frame_protocol.js";
import { WebGL2Presenter } from "/vdp/video/extender/web/webgl2_presenter.js";

const result = document.querySelector("#result");
let checks = 0;

function assert(condition, message) {
  ++checks;
  if (!condition) throw new Error(message);
}

function fromHex(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let index = 0; index < bytes.length; ++index) {
    bytes[index] = Number.parseInt(hex.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes.buffer;
}

function expectRejection(input, reason) {
  try {
    parseFrame(input);
  } catch (error) {
    assert(error instanceof FrameProtocolError, `${reason}: wrong error type`);
    assert(error.reason === reason, `${reason}: got ${error.reason}`);
    return;
  }
  throw new Error(`${reason}: frame was accepted`);
}

function fixtureMessage(vector) {
  if (vector.message_hex) return fromHex(vector.message_hex);
  const header = new Uint8Array(fromHex(vector.header_hex));
  if (vector.id === "payload-limit") return header.buffer;
  const message = new Uint8Array(FRAME_HEADER_BYTES + vector.payload_bytes);
  message.set(header);
  for (let y = 0; y < vector.height; ++y) {
    for (let x = 0; x < vector.width; ++x) {
      const offset = FRAME_HEADER_BYTES + y * vector.stride_bytes + x * 3;
      message[offset] = (x + vector.sequence) & 0xff;
      message[offset + 1] = (2 * y) & 0xff;
      message[offset + 2] = ((x ^ y) + 3 * vector.sequence) & 0xff;
    }
  }
  return message.buffer;
}

async function report(status, detail) {
  try {
    await fetch("/__phase_f_result", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ status, checks, detail }),
    });
  } catch (_error) {
    // The page remains useful under an ordinary static server. The qualified
    // runner supplies this endpoint and treats a missing report as failure.
  }
}

try {
  const compact = fromHex(
    "45564631012001030700000002000200060000000c0000001b41000000000000" +
    "070015080016070216080215",
  );
  const parsed = parseFrame(compact);
  assert(parsed.headerBytes === FRAME_HEADER_BYTES, "header size");
  assert(parsed.sequence === 7, "sequence");
  assert(parsed.width === 2 && parsed.height === 2, "dimensions");
  assert(parsed.strideBytes === 6 && parsed.payloadBytes === 12, "layout");
  assert(parsed.presentPeriodUs === 16667, "period");
  assert(
    [...parsed.pixels].join(",") === "7,0,21,8,0,22,7,2,22,8,2,21",
    "compact fixture pixels",
  );

  const demo = parseFrame(makeDemoFrame({ sequence: 7, width: 2, height: 2 }));
  assert(
    [...demo.pixels].join(",") === [...parsed.pixels].join(","),
    "demo generator follows independent formula",
  );

  const presenter = new WebGL2Presenter(document.querySelector("#presenter-test"));
  presenter.present(parsed);
  const observedPixel = new Uint8Array(4);
  presenter.gl.readPixels(
    0,
    0,
    1,
    1,
    presenter.gl.RGBA,
    presenter.gl.UNSIGNED_BYTE,
    observedPixel,
  );
  assert(observedPixel[3] === 255, "WebGL presenter emitted an opaque pixel");
  assert(
    observedPixel[0] !== 0 || observedPixel[1] !== 0 || observedPixel[2] !== 0,
    "WebGL presenter emitted fixture color",
  );

  expectRejection("not binary", "message-type");
  expectRejection(compact.slice(0, 31), "truncated-header");
  const badMagic = compact.slice(0);
  new Uint8Array(badMagic)[3] = 0x30;
  expectRejection(badMagic, "magic");
  const unknownFlags = compact.slice(0);
  new Uint8Array(unknownFlags)[7] = 0x07;
  expectRejection(unknownFlags, "unknown-flags");
  expectRejection(compact.slice(0, compact.byteLength - 1), "message-length");

  const fixturesResponse = await fetch("/__phase_f_vectors");
  assert(fixturesResponse.ok, "independent browser fixtures available");
  const fixtures = await fixturesResponse.json();
  for (const vector of fixtures.valid_vectors) {
    const frame = parseFrame(fixtureMessage(vector));
    assert(frame.sequence === vector.sequence, `${vector.id}: sequence`);
    assert(frame.width === vector.width && frame.height === vector.height,
      `${vector.id}: dimensions`);
    assert(frame.strideBytes === vector.stride_bytes,
      `${vector.id}: stride`);
    assert(frame.payloadBytes === vector.payload_bytes,
      `${vector.id}: payload`);
  }
  for (const vector of fixtures.malformed_vectors) {
    const message = vector.message_type === "text"
      ? "text fixture"
      : fixtureMessage(vector);
    expectRejection(message, vector.expected_rejection);
  }

  const sent = [];
  const credit = new BrowserCreditState();
  credit.opened((message) => sent.push(message));
  assert(sent.length === 1 && sent[0] === FRAME_REQUEST, "initial credit");
  credit.acceptedFrame();
  assert(sent.length === 1, "no credit before presentation");
  credit.presented((message) => sent.push(message));
  assert(sent.length === 2 && sent[1] === FRAME_REQUEST, "next credit after presentation");
  credit.disconnected();
  credit.opened((message) => sent.push(message));
  assert(sent.length === 3, "reconnect credit");

  credit.acceptedFrame();
  try {
    credit.acceptedFrame();
    throw new Error("duplicate frame was accepted");
  } catch (error) {
    assert(error instanceof FrameProtocolError, "duplicate frame error type");
    assert(error.reason === "unexpected-frame", "duplicate frame reason");
  }

  result.className = "pass";
  result.textContent = `PASS: ${checks} browser protocol checks`;
  document.title = `PASS ${checks} — PORT-003 browser protocol`;
  document.documentElement.dataset.testResult = "pass";
  await report("pass", `PASS: ${checks} browser protocol checks`);
} catch (error) {
  result.className = "fail";
  result.textContent = `FAIL after ${checks} checks\n${error.stack || error}`;
  document.title = "FAIL — PORT-003 browser protocol";
  document.documentElement.dataset.testResult = "fail";
  await report("fail", error.stack || String(error));
  throw error;
}
