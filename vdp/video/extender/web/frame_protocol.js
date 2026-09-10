export const FRAME_MAGIC = "EVF1";
export const FRAME_VERSION = 1;
export const FRAME_HEADER_BYTES = 32;
export const MAXIMUM_WIDTH = 1024;
export const MAXIMUM_HEIGHT = 768;
export const MAXIMUM_PAYLOAD_BYTES = 1024 * 768 * 3;
export const FRAME_REQUEST = "frame";

export const PixelFormat = Object.freeze({
  RGB888: 1,
  RGB222: 2, // One byte: 00BBGGRR, final P4-composed colour.
});

export const FrameFlags = Object.freeze({
  FULL_FRAME: 1 << 0,
  PRESENT_BOUNDARY: 1 << 1,
  KNOWN_MASK: (1 << 0) | (1 << 1),
});

export class FrameProtocolError extends Error {
  constructor(reason, message) {
    super(message);
    this.name = "FrameProtocolError";
    this.reason = reason;
  }
}

function reject(reason, message) {
  throw new FrameProtocolError(reason, message);
}

function magicAt(view) {
  return String.fromCharCode(
    view.getUint8(0),
    view.getUint8(1),
    view.getUint8(2),
    view.getUint8(3),
  );
}

export function parseFrame(buffer) {
  if (!(buffer instanceof ArrayBuffer)) {
    reject("message-type", "frame must be one binary ArrayBuffer");
  }
  if (buffer.byteLength < FRAME_HEADER_BYTES) {
    reject("truncated-header", `short EVF1 header: ${buffer.byteLength} bytes`);
  }

  const view = new DataView(buffer);
  if (magicAt(view) !== FRAME_MAGIC) {
    reject("magic", "bad EVF1 magic");
  }

  const version = view.getUint8(4);
  const headerBytes = view.getUint8(5);
  const pixelFormat = view.getUint8(6);
  const flags = view.getUint8(7);
  const sequence = view.getUint32(8, true);
  const width = view.getUint16(12, true);
  const height = view.getUint16(14, true);
  const strideBytes = view.getUint32(16, true);
  const payloadBytes = view.getUint32(20, true);
  const presentPeriodUs = view.getUint32(24, true);
  const reserved = view.getUint32(28, true);

  if (version !== FRAME_VERSION) {
    reject("version", `unsupported EVF1 version ${version}`);
  }
  if (headerBytes !== FRAME_HEADER_BYTES) {
    reject("header-bytes", `EVF1 v1 header must be 32 bytes, not ${headerBytes}`);
  }
  if (pixelFormat !== PixelFormat.RGB888 && pixelFormat !== PixelFormat.RGB222) {
    reject("pixel-format", `unsupported EVF1 pixel format ${pixelFormat}`);
  }
  if ((flags & ~FrameFlags.KNOWN_MASK) !== 0) {
    reject("unknown-flags", `unknown EVF1 flags 0x${flags.toString(16)}`);
  }
  if ((flags & FrameFlags.FULL_FRAME) === 0) {
    reject("full-frame-required", "EVF1 v1 requires a complete frame");
  }
  if (width === 0 || height === 0) {
    reject("zero-dimension", "EVF1 dimensions must be nonzero");
  }
  if (width > MAXIMUM_WIDTH || height > MAXIMUM_HEIGHT) {
    reject("dimension-limit", `EVF1 surface ${width}×${height} exceeds limits`);
  }

  const minimumStride = width * (pixelFormat === PixelFormat.RGB222 ? 1 : 3);
  if (strideBytes < minimumStride) {
    reject("stride-too-small", `pixel stride ${strideBytes} < ${minimumStride}`);
  }
  const expectedPayload = strideBytes * height;
  if (expectedPayload > MAXIMUM_PAYLOAD_BYTES) {
    reject("payload-limit", `EVF1 payload ${expectedPayload} exceeds limit`);
  }
  if (payloadBytes !== expectedPayload) {
    reject(
      "payload-arithmetic",
      `EVF1 payload ${payloadBytes} != stride*height ${expectedPayload}`,
    );
  }
  if (reserved !== 0) {
    reject("reserved", "EVF1 reserved field must be zero");
  }
  if (headerBytes + payloadBytes !== buffer.byteLength) {
    reject("message-length", "EVF1 message is truncated or has trailing bytes");
  }

  return Object.freeze({
    version,
    headerBytes,
    pixelFormat,
    flags,
    sequence,
    width,
    height,
    strideBytes,
    payloadBytes,
    presentPeriodUs,
    pixels: new Uint8Array(buffer, headerBytes, payloadBytes),
  });
}

function validateDemoDimensions(width, height) {
  if (!Number.isInteger(width) || !Number.isInteger(height) ||
      width <= 0 || height <= 0 ||
      width > MAXIMUM_WIDTH || height > MAXIMUM_HEIGHT) {
    throw new RangeError("demo dimensions exceed the EVF1 contract");
  }
}

export function makeDemoFrame({
  sequence,
  width = 320,
  height = 240,
  presentPeriodUs = 16667,
  pixelFormat = PixelFormat.RGB888,
}) {
  validateDemoDimensions(width, height);
  if (pixelFormat !== PixelFormat.RGB888 && pixelFormat !== PixelFormat.RGB222) {
    throw new RangeError("unsupported demo pixel format");
  }
  const bytesPerPixel = pixelFormat === PixelFormat.RGB222 ? 1 : 3;
  const strideBytes = width * bytesPerPixel;
  const payloadBytes = strideBytes * height;
  const buffer = new ArrayBuffer(FRAME_HEADER_BYTES + payloadBytes);
  const view = new DataView(buffer);

  for (let index = 0; index < FRAME_MAGIC.length; ++index) {
    view.setUint8(index, FRAME_MAGIC.charCodeAt(index));
  }
  view.setUint8(4, FRAME_VERSION);
  view.setUint8(5, FRAME_HEADER_BYTES);
  view.setUint8(6, pixelFormat);
  view.setUint8(
    7,
    FrameFlags.FULL_FRAME | FrameFlags.PRESENT_BOUNDARY,
  );
  view.setUint32(8, sequence >>> 0, true);
  view.setUint16(12, width, true);
  view.setUint16(14, height, true);
  view.setUint32(16, strideBytes, true);
  view.setUint32(20, payloadBytes, true);
  view.setUint32(24, presentPeriodUs >>> 0, true);
  view.setUint32(28, 0, true);

  const pixels = new Uint8Array(buffer, FRAME_HEADER_BYTES, payloadBytes);
  for (let y = 0; y < height; ++y) {
    for (let x = 0; x < width; ++x) {
      const offset = y * strideBytes + x * bytesPerPixel;
      const red = (x + sequence) & 0xff;
      const green = (y * 2) & 0xff;
      const blue = ((x ^ y) + sequence * 3) & 0xff;
      if (pixelFormat === PixelFormat.RGB222) {
        pixels[offset] = (red >> 6) | ((green >> 6) << 2) | ((blue >> 6) << 4);
      } else {
        pixels[offset] = red;
        pixels[offset + 1] = green;
        pixels[offset + 2] = blue;
      }
    }
  }
  return buffer;
}

export class BrowserCreditState {
  constructor() {
    this.state = "disconnected";
  }

  opened(sendCredit) {
    if (this.state !== "disconnected") {
      throw new Error(`cannot open browser credit from ${this.state}`);
    }
    this.state = "waiting_for_frame";
    sendCredit(FRAME_REQUEST);
  }

  acceptedFrame() {
    if (this.state !== "waiting_for_frame") {
      throw new FrameProtocolError(
        "unexpected-frame",
        `frame arrived while browser state is ${this.state}`,
      );
    }
    this.state = "pending_present";
  }

  presented(sendCredit) {
    if (this.state !== "pending_present") {
      throw new Error(`cannot present browser frame from ${this.state}`);
    }
    this.state = "waiting_for_frame";
    sendCredit(FRAME_REQUEST);
  }

  disconnected() {
    this.state = "disconnected";
  }
}
