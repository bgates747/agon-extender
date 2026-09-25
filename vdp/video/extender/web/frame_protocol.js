// EVQ1 pair-RLE, reconstructing canonical EVF1 final RGB222 pixels.
function unpackPairFrame(buffer){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<4)return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVQ1")return buffer;
 const fail=()=>{throw new Error("Invalid EVQ1 pair-RLE frame");};
 if(a.length<33||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const w=v.getUint16(12,true),h=v.getUint16(14,true),n=v.getUint32(20,true);
 if(!w||!h||w>1024||h>768||n!==w*h||v.getUint32(16,true)!==w||a.length>32+n)fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 let i=32,p=32;const end=32+(n&~1);
 while(p<end){
  if(i+2>a.length)fail();const word=a[i]|(a[i+1]<<8);i+=2;
  const count=(word>>>12)+1,x=(word>>>6)&63,y=word&63;
  if(p+count*2>end)fail();
  for(let j=0;j<count;++j){out[p++]=x;out[p++]=y;}
 }
 if(n&1){if(i>=a.length||a[i]>63)fail();out[p++]=a[i++];}
 if(i!==a.length)fail();return out.buffer;
}

// EVP1 experimental final-colour palette packing. Produces canonical EVF1.
function unpackPackedFrame(buffer) {
 if (!(buffer instanceof ArrayBuffer) || buffer.byteLength<4)return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVP1")return buffer;
 const fail=()=>{throw new Error("Invalid EVP1 packed frame");};
 if(a.length<38||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const n=v.getUint32(20,true),w=v.getUint16(12,true),h=v.getUint16(14,true);
 if(!w||!h||w>1024||h>768||n!==w*h||v.getUint32(16,true)!==w)fail();
 const bits=a[32],count=a[33];
 if(bits===6){
  if(count||a[34]||a[35]||a.length!==36+Math.ceil(n*6/8))fail();
  const unused=(8-(n*6)%8)%8;
  if(unused&&(a[a.length-1]&((1<<unused)-1)))fail();
  const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
  let p=0,j=36;
  for(;p+4<=n;p+=4,j+=3){const x=a[j],y=a[j+1],z=a[j+2];
   out[32+p]=x>>2;out[33+p]=((x&3)<<4)|(y>>4);
   out[34+p]=((y&15)<<2)|(z>>6);out[35+p]=z&63;}
  for(;p<n;++p){const bit=p*6,k=36+(bit>>3),shift=bit&7;
   out[32+p]=(((a[k]<<8)|(a[k+1]||0))>>(10-shift))&63;}
  return out.buffer;
 }

 if(![1,2,4].includes(bits)||!count||count>(1<<bits)||a[34]||a[35])fail();
 const start=36+count,bytes=Math.ceil(n*bits/8);
 if(a.length!==start+bytes)fail();
 const seen=new Set();for(let i=36;i<start;++i){if(a[i]>63||seen.has(a[i]))fail();seen.add(a[i]);}
 const unused=(8-(n*bits)%8)%8;if(unused&&(a[a.length-1]&((1<<unused)-1)))fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 const mask=(1<<bits)-1;
 for(let p=0;p<n;++p){const bit=p*bits,index=(a[start+(bit>>3)]>>(8-bits-(bit&7)))&mask;
  if(index>=count)fail();out[32+p]=a[36+index];}
 return out.buffer;
}

// P01h clean-sheet RLE2 v1 decoder. Returns a standard EVF1 ArrayBuffer.
function unpackRLE2Frame(buffer) {
 if (!(buffer instanceof ArrayBuffer) || buffer.byteLength<4) return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVR1")return buffer;
 const fail=()=>{throw new Error("Invalid EVR1/RLE2 frame");};
 if(a.length<46||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const n=v.getUint32(20,true),w=v.getUint16(12,true),h=v.getUint16(14,true);
 if(!w||!h||n>786432||n!==w*h||v.getUint32(16,true)!==w)fail();
 if(String.fromCharCode(...a.subarray(32,36))!=="Cmpr"||v.getUint32(36,true)!==n||String.fromCharCode(...a.subarray(40,44))!=="RLE2"||a[44]!==1||a[45]!==0)fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 let i=46,o=32;
 while(i<a.length){const t=a[i++];if(t&128){if(!(t&64)||o===out.length)fail();out[o++]=t&63;}
 else{const count=t+3;if(i===a.length||count>out.length-o)fail();const p=a[i++];if((p&192)!==192)fail();out.fill(p&63,o,o+count);o+=count;}}
 if(o!==out.length)fail();return out.buffer;
}

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
  buffer=unpackRLE2Frame(unpackPackedFrame(unpackPairFrame(buffer)));
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
