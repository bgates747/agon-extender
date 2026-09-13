#include "mat.h"
#include <cassert>
#include <cmath>
#include <cstdio>
int main() {
  float cases[][9]={{1,0,0,0,1,0,0,0,1},{2,0,7,0,3,-4,0,0,1},{-1,0,102,0,1,0,0,0,1},{1,2,3,0,1,4,5,6,0}};
  for(int pass=0;pass<64;++pass) {
    for(auto &values:cases) {
      dspm::Mat matrix(values,3,3); auto inverse=matrix.inverse();
      for(int row=0;row<3;++row) for(int col=0;col<3;++col) {
        float product=0;for(int k=0;k<3;++k) product+=matrix(row,k)*inverse(k,col);
        assert(std::fabs(product-(row==col?1.0f:0.0f))<0.0001f);
        assert(matrix(row,col)==values[row*3+col]);
      }
    }
    dspm::Mat zero(3,3);assert(zero.det(3)==0);auto inverse=zero.inverse();
    for(int i=0;i<9;++i)assert(inverse.data[i]==0);
  }
  std::puts("matrix numerical and source-preservation checks passed");
}
