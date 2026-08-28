// PORT-003 Phase F accepted maintenance carve-out.
//
// Extender v1 does not retain stock Intel HEX, YMODEM, UART0 updater, terminal,
// or ZDI maintenance paths. The retained parser's dispatch table still names
// these member functions, so this adapter closes only their unreachable Gate-F
// references without linking their physical implementations.
#pragma once

inline void VDUStreamProcessor::vdu_sys_hexload() {}
inline void VDUStreamProcessor::vdu_sys_ymodem_receive() {}
inline void VDUStreamProcessor::vdu_sys_ymodem_send() {}
inline void VDUStreamProcessor::vdu_sys_updater() {}
