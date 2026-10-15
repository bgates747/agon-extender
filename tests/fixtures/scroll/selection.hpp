// One dispatch path for both individual tests and the batch. No drawing here.
#pragma once
#include <string.h>
namespace scroll_fixture {
inline const char *const names[]={"full-up","full-down","full-left","full-right",
                                  "partial-up","partial-down","partial-left","partial-right"};
inline int select(const char *name) {
    if(!strcmp(name,"all"))return 8;
    for(unsigned i=0;i<8;++i)if(!strcmp(name,names[i]))return i;
    return -1;
}
inline bool valid_label(const char *label) {
    unsigned n=0;
    for(;label[n];++n) {
        char c=label[n];
        if(n>=24||!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
                   (c>='0'&&c<='9')||c=='-'||c=='_'))return false;
    }
    return n!=0;
}
template<class Run> bool dispatch(int selected,Run run) {
    if(selected<0||selected>8)return false;
    if(selected<8)return run(unsigned(selected));
    for(unsigned id=0;id<8;++id)if(!run(id))return false;
    return true;
}
}
