// PORT-003 host implementation of the retained renderer's 3x3 multiply.
#pragma once
inline void dspm_mult_3x3x1_f32(float const *matrix, float const *input,
                                float *output) {
  for (int row = 0; row < 3; ++row) {
    output[row] = matrix[row * 3] * input[0] +
                  matrix[row * 3 + 1] * input[1] +
                  matrix[row * 3 + 2] * input[2];
  }
}
