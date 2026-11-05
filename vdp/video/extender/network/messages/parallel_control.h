/* NET-004 bounded carrier metadata on the existing F7 control channel.
 * No NM bytes, CRC/checksum or game fields. Fields4..7 token,8..9 block sequence,
 *10..11 length/capacity,12 direction,13 status;14..15 zero padding (not checked).
 * Version4 selects the existing CRC-free serializer, not console version1.
 */
#ifndef AGON_NETP_CONTROL_H
#define AGON_NETP_CONTROL_H
#define NETP_CONTROL_VERSION 4
#define NETP_CONTROL_OPEN 0x20
#define NETP_CONTROL_SUBMIT 0x21
#define NETP_CONTROL_TAKE 0x22
#define NETP_CONTROL_RELEASE 0x23
#endif
