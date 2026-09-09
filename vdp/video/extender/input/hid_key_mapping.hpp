// Existing US-key subset shared by browser and native USB acquisition.
// Numeric virtual keys match the pinned FabGL enum (browser_keyboard_test.py).
// Physical usage IDs are USB HID Keyboard/Keypad page values. Layout selection,
// additional keys and LEDs are separate from this deliberately bounded mapping.
#pragma once
#include "processed_keyboard.hpp"
namespace agon::extender::input {
  inline uint8_t hidAsciiVirtual(uint8_t c) {
    if (c>='a'&&c<='z') return 22+c-'a';
    if (c>='A'&&c<='Z') return 48+c-'A';
    if (c>='0'&&c<='9') return 2+c-'0';
    if (c==' ') return 1;
    constexpr char chars[]="`'\"=-+*\\/.:,;&|#@^$%! ?{}[]()<>_~";
    constexpr uint8_t codes[]={74,76,77,78,79,81,84,85,87,89,90,91,92,93,94,95,96,97,98,101,102,1,103,104,105,106,107,108,109,110,111,112,115};
    for (unsigned i=0;i<sizeof(chars)-1;++i) if (chars[i]==c) return codes[i];
    return 0;
  }
  inline bool hidKeySupported(uint8_t p) { return (p>=4 && p<=56 && p!=50) || p==57 || (p>=224&&p<=231); }
  inline ProcessedKey mapHidKey(uint8_t physical,uint8_t modifiers) {
    uint8_t c=0,vk=0; const auto p=physical;
    const bool shift=modifiers&2, caps=modifiers&16;
    if (p>=4 && p<=29) c=(shift!=caps?'A':'a')+p-4;
    else if (p>=30 && p<=39) c=shift ? "!@#$%^&*()"[p-30] : "1234567890"[p-30];
    else if (p==40) { c=13; vk=143; }
    else if (p==41) { c=27; vk=125; }
    else if (p==42) { c=8; vk=132; }
    else if (p==43) { c=9; vk=142; }
    else if (p==44) c=' ';
    else if (p>=45&&p<=56) c=(shift ? "_+{}| :\"~<>?" : "-=[]\\ ;'`,./")[p-45];
    else if (p==57) vk=141;
    else if (p>=224&&p<=231) { constexpr uint8_t modifiers[]={121,117,119,123,122,118,120,124}; vk=modifiers[p-224]; }
    if (!vk) vk=hidAsciiVirtual(c);
    auto keycode=c;
    if ((modifiers&1) && ((c>='a'&&c<='z')||(c>='A'&&c<='Z'))) keycode=c&31;
    return {keycode,modifiers,vk,1,keycode};
  }
}
