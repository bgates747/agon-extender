import { PixelFormat } from "./frame_protocol.js";

const VERTEX_SHADER = `#version 300 es
precision highp float;

out vec2 v_uv;

void main() {
  vec2 positions[3] = vec2[](
    vec2(-1.0, -1.0),
    vec2( 3.0, -1.0),
    vec2(-1.0,  3.0)
  );
  vec2 p = positions[gl_VertexID];
  gl_Position = vec4(p, 0.0, 1.0);
  v_uv = p * 0.5 + 0.5;
  v_uv.y = 1.0 - v_uv.y;
}
`;

const FRAGMENT_SHADER = `#version 300 es
precision highp float;

uniform sampler2D u_frame;
uniform bool u_rgb222;
in vec2 v_uv;
out vec4 out_color;

void main() {
  vec3 colour = texture(u_frame, v_uv).rgb;
  if (u_rgb222) {
    // R8 holds the complete packed byte; nearest sampling preserves its bits.
    // Decode final colour only. Palette/Copper/sprite rules remain on P4.
    highp uint pixel = uint(round(colour.r * 255.0));
    colour = vec3(float(pixel & 3u), float((pixel >> 2u) & 3u),
                  float((pixel >> 4u) & 3u)) / 3.0;
  }
  out_color = vec4(colour, 1.0);
}
`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(`shader compile failed: ${log}`);
  }
  return shader;
}

function link(gl, vertex, fragment) {
  const program = gl.createProgram();
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(program);
    gl.deleteProgram(program);
    throw new Error(`program link failed: ${log}`);
  }
  return program;
}

export class WebGL2Presenter {
  constructor(canvas) {
    this.canvas = canvas;
    this.gl = canvas.getContext("webgl2", {
      alpha: false,
      antialias: false,
      depth: false,
      stencil: false,
      preserveDrawingBuffer: false,
    });
    if (!this.gl) {
      throw new Error("WebGL2 is unavailable");
    }

    const gl = this.gl;
    const vertex = compile(gl, gl.VERTEX_SHADER, VERTEX_SHADER);
    const fragment = compile(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
    this.program = link(gl, vertex, fragment);
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);

    this.vao = gl.createVertexArray();
    this.texture = gl.createTexture();
    this.textureWidth = 0;
    this.textureHeight = 0;
    this.pixelFormat = null;
    this.formatUniform = gl.getUniformLocation(this.program, "u_rgb222");
    this.staging = null;

    gl.bindVertexArray(this.vao);
    gl.useProgram(this.program);
    gl.uniform1i(gl.getUniformLocation(this.program, "u_frame"), 0);
    this.configureTexture();
    gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
  }

  configureTexture() {
    const gl = this.gl;
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  }

  present(frame) {
    const gl = this.gl;
    const { width, height, strideBytes, pixels, pixelFormat } = frame;
    const rgb222 = pixelFormat === PixelFormat.RGB222;
    const uploadFormat = rgb222 ? gl.RED : gl.RGB;
    const packedStride = width * (rgb222 ? 1 : 3);

    if (this.canvas.width !== width) this.canvas.width = width;
    if (this.canvas.height !== height) this.canvas.height = height;

    if (this.textureWidth !== width || this.textureHeight !== height ||
        this.pixelFormat !== pixelFormat) {
      // WebGL immutable texture storage cannot be resized. Recreate the one
      // texture on a VDU mode change; steady-state presentation allocates none.
      gl.deleteTexture(this.texture);
      this.texture = gl.createTexture();
      this.configureTexture();
      gl.texImage2D(
        gl.TEXTURE_2D,
        0,
        rgb222 ? gl.R8 : gl.RGB8,
        width,
        height,
        0,
        uploadFormat,
        gl.UNSIGNED_BYTE,
        null,
      );
      this.textureWidth = width;
      this.textureHeight = height;
      this.pixelFormat = pixelFormat;
    }

    let upload = pixels;
    if (strideBytes !== packedStride) {
      const needed = packedStride * height;
      if (!this.staging || this.staging.length !== needed) {
        this.staging = new Uint8Array(needed);
      }
      for (let y = 0; y < height; ++y) {
        this.staging.set(
          pixels.subarray(y * strideBytes, y * strideBytes + packedStride),
          y * packedStride,
        );
      }
      upload = this.staging;
    }

    gl.viewport(0, 0, width, height);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texture);
    gl.texSubImage2D(
      gl.TEXTURE_2D,
      0,
      0,
      0,
      width,
      height,
      uploadFormat,
      gl.UNSIGNED_BYTE,
      upload,
    );
    gl.useProgram(this.program);
    gl.uniform1i(this.formatUniform, rgb222 ? 1 : 0);
    gl.bindVertexArray(this.vao);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
}
