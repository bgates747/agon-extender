# Source and distribution notices

Original utility state-machine, configuration, logging, tests and packaging:
Agon Extender project, GPL-3.0-only. Full license: bundled `LICENSE`.

UART baseline and prior art: Radiotux, **Agon-Software**, commit
`e265db1de57c49142420324945c666049dc1ec53`, `ifconfig/src/ifconfig.c` and
`minicom/src/terminal.c`. Source: https://github.com/Radiotux/Agon-Software
The upstream README says:

> This project is released as **Free Software**. You are free to use, study,
> modify, and redistribute the source code under the terms of open-source
> development.

No precise named upstream license was found in that baseline. Do not assign one
on Radiotux's behalf. Clarify redistribution terms before publishing binaries;
this first local/manual package makes no public-release claim.

AgonDev supplies the linked C/MOS runtime and native compiler. Retain its exact
build identity and applicable runtime/toolchain notices for eventual public
binary distribution. This package contains no compiler/SDK firmware or private
configuration. Source builds require a separately obtained compatible AgonDev
installation. No private Wi-Fi credentials are embedded.

ESP8266 firmware is neither modified nor distributed. AT command contracts:
Espressif ESP8266 AT Instruction Set v1.5.4 (2016). Reference availability does
not establish physical compatibility with every ESP8266 image.
