// Headless only: ordinary key packets using the maintained USB CLI mapping.
#include <cstdio>
#include "extender/input/usb_cli_keyboard.hpp"
int main() {
    using agon::extender::input::mapUsbCliKey;
    auto key=[](unsigned usage) {
        auto k=mapUsbCliKey(usage,0,1);
        if(!k.virtual_key) return false;
        for(unsigned down: {1u,0u}) {
            unsigned char p[]={0x81,4,k.keycode,0,k.virtual_key,static_cast<unsigned char>(down)};
            if(std::fwrite(p,1,sizeof(p),stdout)!=sizeof(p))return false;
        }
        return true;
    };
    if(!key(41))return 1; // Escape
    for(char c: "run . /\r") {
        if(!c)break;
        unsigned usage=c>='a' && c<='z'?4+c-'a':c==' '?44:c=='.'?55:c=='/'?56:c=='\r'?40:0;
        if(!key(usage))return 1;
    }
}
