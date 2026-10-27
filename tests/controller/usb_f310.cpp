#include "extender/input/controller/usb_f310.hpp"
#include <cassert>
#include <cstdio>
using namespace agon::extender::controller;
static void decoder(){
  std::array<std::uint8_t,20>p{};p[1]=20;State s{};
  assert(decodeF310(p.data(),p.size(),s)==UsbReport::state);
  assert((s.sticks==std::array<std::int16_t,4>{0,-1,0,-1}));
  put16(p.data()+6,32768);put16(p.data()+8,32768);
  put16(p.data()+10,32767);put16(p.data()+12,32767);
  p[4]=0;p[5]=255;
  assert(decodeF310(p.data(),20,s)==UsbReport::state);
  assert((s.sticks==std::array<std::int16_t,4>{-32768,32767,32767,-32768}));
  assert(s.triggers[0]==0&&s.triggers[1]==255);
  // Every button is mapped independently, including Guide and stick clicks.
  constexpr unsigned byte[]={3,3,3,3,3,3,2,2,3,2,2,2,2,2,2};
  constexpr unsigned mask[]={16,32,128,64,1,2,32,16,4,64,128,4,8,1,2};
  for(unsigned i=0;i<15;++i){
    p[2]=p[3]=0;p[byte[i]]=mask[i];
    assert(decodeF310(p.data(),20,s)==UsbReport::state);assert(s.held==(1u<<i));
  }
  // Explicit expected hats, including diagonals and opposite contact overlap.
  // Non-hat buttons, triggers and analog axes must survive normalization.
  constexpr std::uint16_t hats[]={0,0x2000,0x4000,0,0x0800,0x2800,0x4800,0x0800,
                                0x1000,0x3000,0x5000,0x1000,0,0x2000,0x4000,0};
  for(unsigned hat=0;hat<16;++hat){
    p[2]=0xf0|hat;p[3]=0xf7;
    assert(decodeF310(p.data(),20,s)==UsbReport::state);
    assert(s.held==(0x07ff|hats[hat])&&validHeld(s.held));
    assert(s.triggers[1]==255&&s.sticks[0]==-32768&&s.sticks[1]==32767);
    assert(f310DpadConflict(hat)==(hat==3||hat==7||hat==11||hat>=12));
  }
  const auto before=s;
  p[2]=0;p[1]=19;assert(decodeF310(p.data(),20,s)==UsbReport::invalid);
  assert(s.held==before.held);
  p[1]=20;assert(decodeF310(p.data(),19,s)==UsbReport::invalid);
  assert(decodeF310(p.data(),0,s)==UsbReport::invalid);
  p[0]=1;assert(decodeF310(p.data(),3,s)==UsbReport::ignored);
  // Exhaust all signed inputs: the X axis is identity and Y is complement.
  p[0]=0;p[2]=p[3]=0;
  for(unsigned v=0;v<65536;++v){
    put16(p.data()+6,v);put16(p.data()+8,v);
    assert(decodeF310(p.data(),20,s)==UsbReport::state);
    const int signed_value=v>=32768?int(v)-65536:int(v);
    assert(s.sticks[0]==signed_value&&s.sticks[1]==-1-signed_value);
  }
}
static void dpadTransitions(){
  Receiver r;r.begin(321);UsbSource usb;usb.connect(r);
  std::array<std::uint8_t,20>p{};p[1]=20;State s{};
  // Roll through up-left, opposing horizontal/vertical contacts and release.
  // Keep A held: no invented A release/press when a hat axis cancels.
  constexpr unsigned raw[]={0,1,5,13,15,10,0};
  constexpr unsigned expected[]={1,0x2001,0x2801,0x2001,1,0x5001,1};
  constexpr unsigned counts[]={0,1,2,3,4,6,8};
  for(unsigned i=0;i<7;++i){
    p[2]=raw[i];p[3]=16;
    assert(decodeF310(p.data(),20,s)==UsbReport::state);
    usb.report(s);usb.tick(r,i*8,77);
    const auto snap=r.snapshot(i*8);
    assert(snap.active&&snap.valid&&snap.state.held==expected[i]);
    assert(snap.queued==counts[i]&&snap.session==77);
  }
  for(unsigned i=0;i<8;++i){Edge e{};assert(r.peek(i,e)&&e.sequence==i+1&&e.control>=11);}
}
static void descriptors(){
  std::array<std::uint8_t,25>c{9,2,25,0,1,1,0,0x80,50,9,4,2,0,1,0xff,0x5d,1,0,7,5,0x81,3,32,0,4};
  F310Interface f{};assert(f310Interface(c.data(),c.size(),f));
  assert(f.number==2&&f.endpoint==0x81&&f.packet==32&&f.interval==4);
  for(unsigned bad:{0u,1u,19u,65u}){
    c[22]=bad;assert(!f310Interface(c.data(),c.size(),f));
  }
  c[22]=32;c[20]=1;assert(!f310Interface(c.data(),c.size(),f));
  c[20]=0x81;c[15]=3;assert(!f310Interface(c.data(),c.size(),f));
  c[15]=0xff;c[9]=0;assert(!f310Interface(c.data(),c.size(),f));
}
static void lifecycle(){
  Receiver r;r.begin(123);UsbSource usb;State s{};s.held=1;
  usb.connect(r);usb.report(s);usb.tick(r,0,700);
  assert(usb.owns(r)&&r.snapshot(0).active&&r.snapshot(0).state.held==1);
  assert(r.snapshot(0).queued==0); // initial held state is not a new press.
  s.held=0;usb.report(s);usb.tick(r,8,701);Edge e{};
  assert(r.peek(0,e)&&e.sequence==1&&e.control==0&&!e.down);
  s.held=1u<<14;usb.report(s);usb.tick(r,16,701);
  assert(r.peek(1,e)&&e.sequence==2&&e.control==14&&e.down);
  usb.tick(r,24,701);assert(r.snapshot(24).queued==2);
  assert(r.retire(1)&&r.snapshot(24).queued==1);
  usb.disconnect(r);assert(!r.snapshot(24).active&&r.snapshot(24).state.held==0);
  usb.connect(r);usb.report(s);usb.tick(r,32,702);assert(r.session()==702);
  usb.fail(r);usb.report(s);usb.tick(r,40,703);
  assert(!r.snapshot(40).valid&&!r.snapshot(40).state.held);
  usb.rearm(r,20,48);usb.tick(r,48,704);assert(!r.snapshot(48).active);
  // A newly attached USB pad cannot take over a live UDP owner.
  Receiver lan;lan.begin(321);assert(lan.open(321,1,{2,3},250,55,0)==200);
  UsbSource blocked;blocked.connect(lan);blocked.report(s);blocked.tick(lan,8,56);
  assert(lan.session()==55&&!blocked.owns(lan));blocked.disconnect(lan);
  assert(lan.snapshot(8).active);
  blocked.connect(lan);blocked.report(s);assert(lan.close(321,55)==200);
  blocked.tick(lan,16,57);assert(blocked.owns(lan)&&lan.session()==57);
  // A stopped worker expires; it cannot revive input on its next heartbeat.
  assert(!lan.snapshot(266).valid);blocked.tick(lan,267,58);
  assert(!lan.snapshot(267).active);
  blocked.rearm(lan,44,268);blocked.tick(lan,268,59);assert(lan.snapshot(268).valid);
  // The new caller itself may be the first observer after worker starvation;
  // do not evaluate expiry using the USB task's previous (stale) timestamp.
  Receiver stalled;stalled.begin(999);UsbSource resumed;
  resumed.connect(stalled);resumed.report(s);resumed.tick(stalled,0,800);
  resumed.rearm(stalled,17,300);resumed.tick(stalled,300,801);
  assert(stalled.snapshot(300).valid&&stalled.session()==801);
  // Overflow invalidates input and remains latched until explicit new caller.
  Receiver full;full.begin(3);UsbSource fast;fast.connect(full);s.held=0;
  fast.report(s);fast.tick(full,0,600);fast.rearm(full,1,0);
  for(unsigned i=1;i<=129;++i){s.held=i&1;fast.report(s);fast.tick(full,i,600);}
  assert(full.snapshot(129).fault==Fault::Overflow&&!full.snapshot(129).valid);
  fast.tick(full,130,601);fast.rearm(full,1,131);fast.tick(full,131,601);
  assert(!full.snapshot(131).active);
  fast.rearm(full,2,132);fast.tick(full,132,602);
  assert(full.snapshot(132).valid&&full.snapshot(132).queued==0);
  // Old network/USB identities cannot publish into the new source session.
  Packet old{};old.instance=3;old.session=600;old.sequence=500;
  std::array<std::uint8_t,40>ack{};assert(!full.receive(old,{0,1},133,ack));
}
int main(){decoder();dpadTransitions();descriptors();lifecycle();puts("F310 decoder, D-pad transitions, descriptors, source exclusion and lifecycle PASS");}
