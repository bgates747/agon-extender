# Discord transcript — PerryZi and Agon network compatibility

Source: Agon & Console8 Community, #software. Captured through the Chrome Discord UI on 2026-09-23 (America/New_York). Nine messages, starting with the requested message and ending at the latest message visible at capture, September 23 at 18:16. Times below match the browser display (America/New_York). Message text is transcribed; reactions, server badges, repeated reply previews and generated link previews are omitted. Image attachments are listed but were not downloaded or transcribed. No analysis is added.

## 2026-09-23 15:49 — pollito

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552406628589109308)

My ESP8266 firmware, PerryZi, is now compatible with the MOD-WIFI-ESP8266 module. It is based on Zimodem, so it has powerful features like SLIP / PPP, and now it also implements the official Espressif AT command set to maintain compatibility with existing software.

https://github.com/SanPollo/PerryZi

## 2026-09-23 16:55 — rafd_electrotux

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552423232336953474)

Reply to [message 1552406628589109308](https://discord.com/channels/1158535358624039014/1158753764224802877/1552406628589109308).

Almost all existing networking software for the Agon runs on the standard AT firmware for the ESP-01S and its derivatives. The modules used include the one supplied by OLIMEX and the standard Chinese ESP-01S module—both connected to the same UART1 port—as well as the ESP-12S module I have been using recently. Honestly, I find it unlikely that users would choose to replace the existing firmware, given that most currently use the first two modules mentioned; these have much more limited memory than the ESP-12F—the specific flash capacity that, I imagine, is required to support the two firmware versions you are developing.

Attachments (three images; links without temporary signature parameters):

- [UEXT_WIFI.jpeg](https://cdn.discordapp.com/attachments/1158753764224802877/1552423229400944700/UEXT_WIFI.jpeg)
- [ESP8266_ESP-01s.webp](https://cdn.discordapp.com/attachments/1158753764224802877/1552423230709563533/ESP8266_ESP-01s.webp)
- [D_NQ_NP_996757-MLB72885852185_112023-O.webp](https://cdn.discordapp.com/attachments/1158753764224802877/1552423231439241267/D_NQ_NP_996757-MLB72885852185_112023-O.webp)

Discord may require opening the parent message to obtain fresh attachment links.

## 2026-09-23 17:33 — pollito

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552432752131842139)

Reply to [message 1552423232336953474](https://discord.com/channels/1158535358624039014/1158753764224802877/1552423232336953474).

The standard firmware for the MOD-WIFI-ESP8266 is an old v1.x Espressif firmware. My firmware implements those AT commands, and also gives users access to the Zimodem features. The main reason for choosing Zimodem for PerryZi is the built in SLIP and PPP functionality, and I am sure some people will be interested in this. I'm not forcing anyone to use it, I am just sharing my work here to present it as an option. I've tested it on my AgonLight 2 with the Snail, and the Radiotux tools, and they work fine.

I am only developing one firmware version, not two - depending on which target you choose, Arduino IDE produces a binary for that module. I will get around to explaining this in the project wiki at some point, but it is documented in the source for people who are interested.

## 2026-09-23 17:39 — rafd_electrotux

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434178254176307)

Reply to [message 1552432752131842139](https://discord.com/channels/1158535358624039014/1158753764224802877/1552432752131842139).

This version of the get (zget) utility runs on Zimodem, albeit at 115,200 bps. It might be useful for you when running compatibility tests: https://github.com/Radiotux/Agon-Software/tree/main/zget

## 2026-09-23 17:41 — pollito

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434804778213460)

Reply to [message 1552434178254176307](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434178254176307).

I tried that - it was super fast compared to the normal get program! 🙂

## 2026-09-23 17:44 — rafd_electrotux

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552435461279060042)

Reply to [message 1552434804778213460](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434804778213460).

I’m going to test your firmware this coming weekend. I’m interested in PPP (specifically LCP), and I’ll let you know the results afterwards. Thank you very much for sharing your work. Best regards.

## 2026-09-23 17:49 — pollito

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552436725547008171)

Reply to [message 1552435461279060042](https://discord.com/channels/1158535358624039014/1158753764224802877/1552435461279060042).

That would be great - please let me know if you come across anything. I also need to test it with the Neo6502 software (but I think there are only a couple of programs that use it). Also, if you know of any other Agon network tools I can test then I'd love to give them a try.

## 2026-09-23 18:13 — rafd_electrotux

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552442733506068610)

Reply to [message 1552436725547008171](https://discord.com/channels/1158535358624039014/1158753764224802877/1552436725547008171).

For the ESP-01S, in addition to the Telnet and Snail utilities, the ntpsync, ping, route, ipconfig, nslookup, arp, get, and zget utilities are the only ones I am aware of so far. https://github.com/Radiotux/Agon-Software

## 2026-09-23 18:16 — pollito

[Message](https://discord.com/channels/1158535358624039014/1158753764224802877/1552443600330301491)

Reply to [message 1552442733506068610](https://discord.com/channels/1158535358624039014/1158753764224802877/1552442733506068610).

I tested all of these before I released the firmware. I wanted to make sure it was compatible with everything Agon I could find

