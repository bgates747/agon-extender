// Compile the actual native fixture's pure matrix on host for a byte oracle.
#include <cstdio>
#include "../../fixtures/network/repeat_matrix.hpp"
int main(){
    for(unsigned s=0;s<probe_repeat::sessions;++s)
        for(unsigned i=0;i<probe_repeat::records_per_session;++i){
            const unsigned n=probe_repeat::size(i);
            const unsigned char h[]={static_cast<unsigned char>(s),static_cast<unsigned char>(i),static_cast<unsigned char>(n)};
            if(std::fwrite(h,1,sizeof(h),stdout)!=sizeof(h))return 1;
            for(unsigned j=0;j<n;++j)if(std::putchar(probe_repeat::byte(s,i,j))==EOF)return 1;
        }
}
