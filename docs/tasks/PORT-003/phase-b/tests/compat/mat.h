// PORT-003 host-only 3x3 matrix needed by Canvas transformed-bitmap calls.
#pragma once

#include <array>
#include <stdexcept>

namespace dspm {
class Mat {
 public:
  Mat(int rows, int columns) : rows_(rows), columns_(columns) {
    if (rows != 3 || columns != 3) throw std::invalid_argument("only 3x3 matrices are supported");
    data = values_.data();
  }
  Mat(Mat const &other) : rows_(other.rows_), columns_(other.columns_), values_(other.values_) {
    data = values_.data();
  }
  Mat &operator=(Mat const &other) {
    rows_ = other.rows_;
    columns_ = other.columns_;
    values_ = other.values_;
    data = values_.data();
    return *this;
  }
  float &operator()(int row, int column) { return values_[row * 3 + column]; }
  Mat inverse() const {
    float const *m = values_.data();
    float determinant = m[0] * (m[4] * m[8] - m[5] * m[7]) -
                        m[1] * (m[3] * m[8] - m[5] * m[6]) +
                        m[2] * (m[3] * m[7] - m[4] * m[6]);
    if (determinant == 0.0f) throw std::runtime_error("singular matrix");
    Mat result(3, 3);
    result.values_ = {{
        (m[4] * m[8] - m[5] * m[7]) / determinant,
        (m[2] * m[7] - m[1] * m[8]) / determinant,
        (m[1] * m[5] - m[2] * m[4]) / determinant,
        (m[5] * m[6] - m[3] * m[8]) / determinant,
        (m[0] * m[8] - m[2] * m[6]) / determinant,
        (m[2] * m[3] - m[0] * m[5]) / determinant,
        (m[3] * m[7] - m[4] * m[6]) / determinant,
        (m[1] * m[6] - m[0] * m[7]) / determinant,
        (m[0] * m[4] - m[1] * m[3]) / determinant,
    }};
    return result;
  }
  float *data;

 private:
  int rows_;
  int columns_;
  std::array<float, 9> values_{};
};
}  // namespace dspm
