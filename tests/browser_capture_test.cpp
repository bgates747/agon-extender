#include <cassert>
#include "extender/input/browser_capture.hpp"
using namespace agon::extender::input;
void put(uint8_t *p,uint32_t n){for(int i=0;i<4;++i)p[i]=uint8_t(n>>(8*i));}
int main(){
 InputOwner r;r.begin(9);r.admit(1);uint32_t gen{};uint8_t p[16]={'B','K',1,1};put(p+8,1);
 auto send=[&](unsigned owner,uint32_t now){return r.browserRequest(owner,p,16,now,gen);};
 assert(send(1,100)==200);put(p+4,gen);p[3]=2;put(p+8,2);p[12]=4;p[13]=1;
 assert(send(1,101)==409); // unknown Caps is not silently off
 p[14]=0x70;assert(send(1,101)==200);
 ProcessedKey key;assert(r.take(key,101)&&key.keycode=='a'&&key.down);
 assert(!r.take(key,102));assert(r.take(key,601)&&key.down);assert(!r.take(key,601));
 p[13]=0;put(p+8,3);assert(send(1,602)==200);assert(r.take(key,602)&&!key.down);
 p[12]=5;p[13]=1;put(p+8,4);assert(send(1,603)==200);assert(r.take(key,603)&&key.keycode=='b');
 // Renewal racing an earlier console timestamp, and timer wrap.
 p[3]=3;put(p+8,5);assert(send(1,604)==200);r.tick(603);assert(!r.take(key,604));
 r.physicalKey({0,0,22,1,0});assert(r.release(key)&&!key.down&&key.keycode=='b');
 put(p+8,6);assert(send(1,605)==409);
 r.physicalKey({0,0,22,0,0});r.physicalNeutral(true);
 p[3]=1;put(p+4,0);put(p+8,1);p[12]=p[13]=p[14]=p[15]=0;
 assert(send(2,0xfffffff0)==200);put(p+4,gen);p[3]=3;put(p+8,2);assert(send(2,20)==200);
 r.tick(19);put(p+8,3);assert(send(2,21)==200);
 // Latest explicit capture wins; stale close cannot revoke the replacement.
 p[3]=1;put(p+4,0);put(p+8,1);assert(send(3,22)==200);r.browserDisconnect(2);
 p[3]=2;put(p+4,gen);put(p+8,2);p[12]=43;p[13]=1;
 assert(send(3,23)==200);assert(r.take(key,23)&&key.keycode==9);
 r.tick(5023);assert(r.take(key,5023)&&!key.down);assert(!r.take(key,5023));
 // Lock/keypad mapping and physical state remain independent.
 assert(mapUsbCliKey(89,32,1).keycode=='1');assert(mapUsbCliKey(89,0,1).virtual_key==136);
 assert(mapUsbCliKey(89,34,1).virtual_key==136); // stock Num+Shift navigation
 // Browser explicitly cancels agent held state before its own first event.
 r.begin(9);r.admit(1);
 uint8_t agent[28]={'K','Y',1,1};put(agent+4,9);put(agent+8,33);put(agent+12,1);
 put(agent+20,remoteCrc(agent,24));assert(r.post(agent,24,0)==200);
 agent[3]=2;put(agent+12,2);agent[16]=4;agent[24]=4;agent[25]=1;agent[26]=5;agent[27]=1;
 put(agent+20,remoteCrc(agent,28));assert(r.post(agent,28,0)==200);
 assert(r.take(key,0)&&key.keycode=='a');
 p[3]=1;put(p+4,0);put(p+8,1);p[12]=p[13]=p[14]=p[15]=0;
 assert(send(4,1)==200);assert(r.post(agent,28,1)==503);
 p[3]=2;put(p+4,gen);put(p+8,2);p[12]=6;p[13]=1;p[14]=0x70;
 assert(send(4,2)==200);assert(r.take(key,2)&&!key.down&&key.keycode=='a');
 assert(r.take(key,2)&&key.down&&key.keycode=='c'); // no agent pacing on humans
 r.physicalNeutral(false);assert(r.take(key,3)&&!key.down);
 assert(!r.take(key,20)); // queued agent b was discarded, not replayed
 UsbCliKeyboard usb;usb.admit();uint8_t report[8]={0,0,83};
 usb.report(report,8,0,[](ProcessedKey){});assert(usb.ledState()==1);
 report[2]=57;usb.report(report,8,1,[](ProcessedKey){});assert(usb.ledState()==3);
}
