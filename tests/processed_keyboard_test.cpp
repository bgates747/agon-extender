// The runner includes actual maintained method bodies and actual coalescing
// event queue. Only display context and the documented variable side effects
// are faked here; this is not a full native VDP or hardware timing test.
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <map>
#include <vector>
#include "extender/input/processed_keyboard.hpp"
#include "utils/thread_safe_variant_deque.h"
#include "constants.inc"
#define AGON_EXTENDER_P4_BOOT 1
#define AGON_EXTENDER_PROCESSED_KEYBOARD 1
namespace fabgl {
enum VirtualKey { VK_NONE=0, VK_LAST=248 };
struct VirtualKeyItem {
  uint8_t ASCII{}; VirtualKey vk{}; bool down{};
  bool CTRL{},SHIFT{},LALT{},RALT{},CAPSLOCK{},NUMLOCK{},SCROLLLOCK{},GUI{};
  alignas(2) uint8_t scancode[8]{};
};
}
struct MouseDelta {};
bool mouseMoved(MouseDelta *) { return false; }
enum class KeyboardEvent {}; enum class MouseEvent {};
using EventQueue=ThreadSafeVariantDeque<KeyboardEvent,MouseEvent>;
EventQueue eventQueue;
template<class... T> struct overloaded:T... { using T::operator()...; };
template<class... T> overloaded(T...)->overloaded<T...>;
enum class VDUProcessorState { Active, PagedModePaused };
struct Context {
  VDUProcessorState state=VDUProcessorState::Active;
  unsigned shown{};
  auto getProcessorState() { return state; }
  void setProcessorState(VDUProcessorState s) { state=s; }
  void showCursor() { ++shown; }
};
bool controlKeys=true,printerOn=false;
uint8_t _keycode{},kbRegion{};
uint16_t kbRepeatDelay=500,kbRepeatRate=100;
struct LEDs {
  bool n{},c{},s{};
  void setLEDs(bool a,bool b,bool d) { n=a;c=b;s=d; }
  void getLEDs(bool *a,bool *b,bool *d) { *a=n;*b=c;*d=s; }
} leds;
LEDs *getKeyboard() { return &leds; }
std::map<uint16_t,uint16_t> vars;
uint16_t getVDPVariable(uint16_t k) { return vars[k]; }
bool isVDPVariableSet(uint16_t k) { return vars[k]!=0; }
void clearVDPVariable(uint16_t k) { vars[k]=0; }
void setVDPVariable(uint16_t k,uint16_t v) {
  vars[k]=v;
  if (k==VDPVAR_KEYEVENT_VK || k==VDPVAR_KEYEVENT_DOWN)
    eventQueue.pushUnique(KeyboardEvent{});
  if (k==VDPVAR_KEYEVENT_MODIFIERS)
    for (unsigned b=0;b<8;++b) vars[VDPVAR_KEYEVENT_CTRL+b]=(v>>b)&1;
}
void debug_log(const char *,...) {}
class VDUStreamProcessor {
 public:
  Context c; Context *context=&c;
  std::vector<uint8_t> bytes,controls;
  std::vector<uint16_t> callbacks;
  bool edit{},suppress{},initialised{};
  int token=167;
  int readByte_t() { return token; }
  void writeByte(uint8_t b) { bytes.push_back(b); }
  void bufferCallCallbacks(uint16_t code) {
    callbacks.push_back(code);
    if (edit && code==CALLBACK_KEYBOARD) {
      // A retained callback edits the wire key and raw control-code byte.
      setVDPVariable(VDPVAR_KEYEVENT_KEYCODE,'z' | (12<<8));
      setVDPVariable(VDPVAR_KEYEVENT_VK,47);
    }
    if (suppress && code==(CALLBACK_SENDING_VDPP|PACKET_KEYCODE))
      setVDPVariable(VDPVAR_VDPP_SUPPRESSNEXT,1);
  }
  void vdu(uint8_t b,bool) { controls.push_back(b); }
  void updateMouseVars(MouseDelta *) { assert(false); }
  void send_packet(uint8_t,uint16_t,uint8_t[]);
  void sendKeyboardData(); void processEventQueue(); void handleKeyboardAndMouse();
  void sendGeneralPoll();
};
#include "retained.inc"
#include "extender/input/browser_keyboard.hpp"
#include "extender/input/usb_cli_keyboard.hpp"
using agon::extender::input::ProcessedKey;
int main(int argc,char **argv) {
  auto &q=agon::extender::input::processedKeyboard();
  ProcessedKey out;
  if (argc==3 && std::string(argv[2])=="usb-cli") {
    VDUStreamProcessor p;
    agon::extender::input::UsbCliKeyboard keyboard;
    keyboard.locale=1;keyboard.admit();
    uint32_t now=0;
    auto emit=[&](ProcessedKey key) {assert(q.push(key));p.handleKeyboardAndMouse();};
    auto tap=[&](uint8_t usage,uint8_t modifiers=0) {
      uint8_t report[]={modifiers,0,usage,0,0,0,0,0};
      keyboard.report(report,8,now++,emit);
      report[0]=report[2]=0;keyboard.report(report,8,now++,emit);
    };
    auto type=[&](const char *text) {
      for(;*text;++text) {
        bool found=false;
        for(unsigned mods:{0,2}) for(unsigned usage=4;usage<=56 && !found;++usage) {
          auto key=agon::extender::input::mapUsbCliKey(usage,mods,1);
          if(key.keycode==uint8_t(*text)) {tap(usage,mods);found=true;}
        }
        assert(found);
      }
    };
    // Real ordinary MOS line editing: replace x, move left/right, then submit.
    type("echo USB clx");tap(42);type("i");tap(80);tap(79);tap(40);
    type("echo Shift 1!");tap(40);
    type("EmOs KeYiNpUt");tap(40);
    type("echo USB CLI REVIEW COMPLETE");tap(40);
    type("emos keyinput mainboard");tap(40);
    assert(!p.bytes.empty() && p.bytes.size()%6==0);
    std::ofstream file(argv[1],std::ios::binary);
    file.write(reinterpret_cast<const char *>(p.bytes.data()),p.bytes.size());
    assert(file.good());return 0;
  }
  if (argc==3 && std::string(argv[2])=="typing") {
    VDUStreamProcessor p;
    agon::extender::input::BrowserKeyboard browser;
    browser.ready(true); assert(browser.take(1,0));
    // aB3! Backspace ? Enter z Escape, with explicit Shift transitions.
    const agon::extender::input::BrowserKeyboard::Event events[]={
      {4,0,1},{4,0,0},{225,2,1},{5,2,1},{5,2,0},{225,0,0},
      {32,0,1},{32,0,0},{225,2,1},{30,2,1},{30,2,0},{225,0,0},
      {42,0,1},{42,0,0},{225,2,1},{56,2,1},{56,2,0},{225,0,0},
      {40,0,1},{40,0,0},{29,0,1},{29,0,0},{41,0,1},{41,0,0}};
    for (auto e:events) {
      assert(browser.push(1,e,0)); assert(browser.pop(out,0));
      assert(q.push(out)); p.handleKeyboardAndMouse();
    }
    assert(p.bytes.size()==sizeof(events)/sizeof(events[0])*6);
    std::ofstream file(argv[1],std::ios::binary);
    file.write(reinterpret_cast<const char *>(p.bytes.data()),p.bytes.size());
    return 0;
  }
  assert(!q.pop(out) && !q.push({0,0,249,1,0}) && !q.push({0,0,22,2,0}));
  for (unsigned i=0;i<q.capacity;++i) assert(q.push({uint8_t(i),0,22,uint8_t(i&1),0}));
  assert(!q.push({99,0,22,1,99}));
  for (unsigned i=0;i<q.capacity;++i) { assert(q.pop(out)); assert(out.keycode==i && out.down==(i&1)); }
  assert(!q.pop(out));
  // Submit an entire burst before draining. Actual retained queue is unique by
  // event type; the per-input drain must preserve every repeated down and up.
  const ProcessedKey sequence[]={
    {'a',0,22,1,'a'},{'a',0,22,0,'a'},{0,2,117,1,0},
    {'B',2,49,1,'B'},{'B',2,49,1,'B'},{'B',2,49,1,'B'},
    {'B',2,49,0,'B'},{0,0,117,0,0},{'7',0,9,1,'7'},
    {'7',0,9,0,'7'},{13,0,143,1,13},{13,0,143,0,13}};
  VDUStreamProcessor p;
  static_assert(std::size(keyboardProbeEvents)==std::size(sequence));
  for (auto key:keyboardProbeEvents) assert(q.push(key));
  p.handleKeyboardAndMouse();
  assert(q.size()==0 && eventQueue.empty() && p.bytes.size()==72);
  for (unsigned i=0;i<12;++i) {
    const auto &key=sequence[i];
    const uint8_t expected[]={0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down};
    assert(!std::memcmp(p.bytes.data()+6*i,expected,6));
    assert(p.callbacks[3*i]==CALLBACK_KEYBOARD);
    assert(p.callbacks[3*i+1]==(CALLBACK_SENDING_VDPP|PACKET_KEYCODE));
    assert(p.callbacks[3*i+2]==(CALLBACK_SENT_VDPP|PACKET_KEYCODE));
  }
  if (argc==2) { std::ofstream file(argv[1],std::ios::binary); file.write(reinterpret_cast<char*>(p.bytes.data()),p.bytes.size()); assert(file.good()); }
  p.bytes.clear(); p.callbacks.clear(); p.sendGeneralPoll();
  assert(p.bytes==std::vector<uint8_t>({0x80,1,167}) && p.initialised);
  p.bytes.clear(); p.edit=true;
  assert(q.push({'x',0,45,1,'x'})); p.handleKeyboardAndMouse();
  assert(p.bytes==std::vector<uint8_t>({0x81,4,'z',0,47,1}));
  assert(p.controls.back()==12); // callback edits precede control handling
  p.bytes.clear(); p.edit=false; p.suppress=true;
  assert(q.push({'x',0,45,0,'x'})); p.handleKeyboardAndMouse();
  assert(p.bytes.empty() && eventQueue.empty() && !isVDPVariableSet(VDPVAR_VDPP_SUPPRESSNEXT));
  p.suppress=false; p.c.state=VDUProcessorState::PagedModePaused;
  assert(q.push({27,0,125,1,27})); p.handleKeyboardAndMouse();
  assert(p.c.state==VDUProcessorState::Active && p.c.shown==1);
  setKeyboardLayout(1); assert(kbRegion==1); setKeyboardLayout(250); assert(!kbRegion);
  setKeyboardState(799,33,5); uint16_t delay,rate; uint8_t led;
  getKeyboardState(&delay,&rate,&led); assert(delay==750 && rate==33 && led==5);
  setKeyboardState(0,0,255); getKeyboardState(&delay,&rate,&led);
  assert(delay==750 && rate==33 && led==5);
  assert(q.push({0,3,117,1,0})); p.handleKeyboardAndMouse();
  assert(shiftKeyPressed() && ctrlKeyPressed()); q.reset();
  assert(!shiftKeyPressed() && !ctrlKeyPressed());
}
