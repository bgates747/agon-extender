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
in vec2 v_uv;
out vec4 out_color;

void main() {
  out_color = vec4(texture(u_frame, v_uv).rgb, 1.0);
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
    const { width, height, strideBytes, pixels } = frame;
    const packedStride = width * 3;

    this.canvas.width = width;
    this.canvas.height = height;

    if (this.textureWidth !== width || this.textureHeight !== height) {
      // WebGL immutable texture storage cannot be resized. Recreate the one
      // texture on a VDU mode change; steady-state presentation allocates none.
      gl.deleteTexture(this.texture);
      this.texture = gl.createTexture();
      this.configureTexture();
      gl.texImage2D(
        gl.TEXTURE_2D,
        0,
        gl.RGB8,
        width,
        height,
        0,
        gl.RGB,
        gl.UNSIGNED_BYTE,
        null,
      );
      this.textureWidth = width;
      this.textureHeight = height;
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
      gl.RGB,
      gl.UNSIGNED_BYTE,
      upload,
    );
    gl.useProgram(this.program);
    gl.bindVertexArray(this.vao);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
}
