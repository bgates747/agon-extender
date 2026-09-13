# Evaluación de una placa P4 alternativa — 2026-09-13

## Dictamen

La Waveshare ESP32-P4-Module-DEV-KIT documentada es una candidata viable para
Extender, sujeta a una nueva configuración de placa, un mapa de conexiones y
pruebas de validación física. No se puede dar por compatible con la imagen de
firmware ni con el cableado actual de Olimex sin revisarlos. Esta evaluación es
documental: no constituye una medición de rendimiento ni una garantía sobre el
producto que entregue el vendedor.

## Evidencia del anuncio

El Autor proporcionó una copia completa de la página guardada en el navegador:
https://www.aliexpress.us/item/3256809591936741.html .
El título identifica Waveshare ESP32-P4-Module-DEV-KIT; el campo de marca indica
ICMILES y la tienda es IClemon Store. Esto identifica la familia de productos
anunciada, pero no demuestra su autenticidad. La variante seleccionada en la
copia es ESP32-P4-Module, con un precio mostrado de US$12,03: no debe confundirse
con el precio del conjunto completo con placa base. No se verificaron el envío
ni la compra con destino a Chile. El resumen generado por IA de la plataforma
se excluyó de la evidencia técnica. Los productos recomendados y las anécdotas
de compradores no son especificaciones del artículo seleccionado.

El HTML y su carpeta complementaria se conservan aquí, excluidos de Git. No se
deben incorporar al repositorio scripts del navegador ni datos de sesión de
la página. No se ejecutó código de la página externa.

## Comparación

| Área | Extender actual / evidencia de la candidata | Evaluación |
| --- | --- | --- |
| Memoria | La arquitectura actual selecciona 16 MB de flash y 32 MB de PSRAM; Waveshare especifica las mismas capacidades. | La capacidad es adecuada; verificar el dispositivo real, el modo del bus y la integridad de la memoria. |
| Silicio y herramientas | La Olimex D1 actual usa P4 v1.3, esp32p4_es, con revisiones admitidas de 100 a 199. Versiones fijadas: pioarduino 55.03.311 / Arduino 3.3.11 / IDF 5.5.5. El anuncio no determina la revisión del chip. | No grabar la imagen existente sin comprobarla. Leer la revisión y seleccionar un destino de compilación compatible. |
| Ethernet | Nuestro ETH.begin utiliza IP101, dirección 1, MDC31, MDIO52, reset51 y reloj RMII externo. Waveshare documenta IP101GRI con las mismas señales de gestión y reinicio, y reloj de referencia en GPIO50. | Coincidencia favorable; confirmar de forma independiente la configuración física de la dirección del PHY y la revisión real de la PCB antes de validarla. |
| UART de Agon | Actualmente UART1 TX12/RX22/RTS11/CTS23 a 1.152.000 baudios, 8N1, con control de flujo por hardware. El esquema de Waveshare asigna GPIO9–13 al audio I2S, incluidos nuestros TX12/RTS11; estos no están en el conector GPIO habitual de 40 pines. | Reasignar la UART a cuatro GPIO cuya disponibilidad se haya verificado y elaborar un nuevo mapa de cableado. No se debe presuponer que sea necesario soldar a las señales de audio. |
| Inicialización de otros pines | La inicialización actual de la consola también restablece un grupo más amplio de GPIO, además de los cuatro de la UART. La candidata asigna pines al audio, C6, SD y otros periféricos. | Revisar cada inicialización y resistencia de polarización configurada frente al esquema de la candidata; cambiar solo uart_set_pin no basta. |
| Teclado | La conexión Olimex actual utiliza USB_DP/DN dedicados en EXT2.19/20, no GPIO27/26. Waveshare ofrece USB OTG tipo A y puentes de selección del modo anfitrión. | Vía prometedora para USB anfitrión nativo; comprobar la selección del PHY, los puentes y la alimentación VBUS antes de probar. La numeración de los conectores no es intercambiable. |
| Programación | La candidata incluye CH343P USB-UART y conectividad USB separada. | Adaptar la identificación de puertos serie y las herramientas de reinicio/arranque. Las suposiciones USB de Olimex no se trasladan automáticamente. |
| SD de la placa principal | EMOS da acceso a la tarjeta de Agon mediante UART y sdserve ejecutándose en primer plano. | No depende de una ranura de tarjeta en la P4. La ranura TF de la candidata no sustituye ese servicio. |
| Wi-Fi | La candidata incluye un C6 conectado mediante SDIO. | Capacidad futura opcional; el servicio cableado actual de HTTP/SD/teclado/video no se convierte automáticamente en una implementación Wi-Fi para C6. |
| Pantalla | La candidata anuncia MIPI DSI de dos carriles. | Posible salida de pantalla futura; no demuestra que exista un controlador de panel operativo en Extender ni compatibilidad con cables o paneles de Olimex. |
| Alimentación | La candidata tiene un conector para módulo PoE y circuitos de alimentación USB anfitrión. | El conector PoE no implica una fuente PoE incluida. Verificar el paquete seleccionado y las funciones de alimentación; mantener separadas las líneas positivas de Agon y P4, con masa de señal común. |

La candidata no elimina un cuello de botella de renderizado simplemente por
usar el mismo procesador P4 u ofrecer MIPI. El renderizado en el framebuffer y
la salida deben medirse por separado, tal como pidió el Autor. Esta evaluación
no modifica QUAL-003 ni reanuda sus pruebas.

## Pasos posteriores necesarios si se aprueban

HW-003.md mantiene las decisiones pendientes. Una adaptación autorizada
posteriormente debería introducir un perfil de placa separado, conservar el
soporte de Olimex y revisar todos los GPIO ocupados antes de asignar la UART.
EMOS debe seguir siendo responsable del enrutamiento y del transporte. Conservar
las dos particiones OTA existentes de 7 MiB si los 16 MB de flash confirmados
permiten la misma distribución. Comprobar en la unidad recibida la revisión del
chip, el funcionamiento de flash/PSRAM, la recuperación mediante grabación, el
arranque en frío y la reversión OTA. Después, validar Ethernet, teclado USB,
UART con control de flujo, CLI y servicio SD antes de los gráficos. Medir el
trabajo sobre el framebuffer con la salida al navegador desactivada antes de
probar la entrega de imágenes. Cualquier trabajo con un panel MIPI requiere su
propia revisión de conector, alimentación y temporización.

## Fuentes consultadas

1. Copia del anuncio proporcionada por el Autor, recibida el 2026-09-13; HTML local excluido de Git en esta carpeta.
2. [Documentación actual de Waveshare](https://docs.waveshare.com/ESP32-P4-Module-DEV-KIT): memoria, identificación del kit, conectores y selección del modo anfitrión.
3. [Wiki de Waveshare y ejemplo Ethernet](https://www.waveshare.com/wiki/ESP32-P4-Module-DEV-KIT-StartPage): IP101GRI y asignaciones RMII.
4. [Esquema del fabricante, tres páginas](https://files.waveshare.com/wiki/ESP32-P4-Module-DEV-KIT/ESP32-P4-Module-DEV-KIT.pdf): conector, USB-UART y señales I2S en la página 1. El esquema público es una referencia, no una prueba de la revisión vendida. Consultado el 2026-09-13.
5. Referencia local de Extender en el commit 73c25d1: docs/architecture.md (plataforma, silicio y memoria), vdp/video/extender/transport/console_hardware.inc (UART), vdp/video/extender/network/wired_network_service.cpp (Ethernet).
6. hardware/designs/light2-harness-r03/README.md: UART existente y mapa corregido del teclado USB; distingue el borrador del esquema del cableado de teclado aceptado posteriormente.

Para esta evaluación no se compiló ni se grabó firmware, no se modificó el
cableado ni se realizaron mediciones de hardware. No se contactó al vendedor
ni se efectuó ninguna compra como parte de la evaluación.

---

# Alternate P4 board assessment — 2026-09-13

## Verdict

The documented Waveshare ESP32-P4-Module-DEV-KIT is a credible candidate for
Extender, subject to a new board configuration, wiring map and physical
qualification. It is not compatible with the existing Olimex image/harness
without review. This is a desk assessment, not a measured performance result
or a guarantee about the seller's supplied goods.

## Listing evidence

The Author supplied a complete browser save of
https://www.aliexpress.us/item/3256809591936741.html .
Its product title identifies Waveshare ESP32-P4-Module-DEV-KIT; the structured
brand field says ICMILES and the shop is IClemon Store. This establishes a
claimed product family, not authenticity. The saved selected variant is
ESP32-P4-Module, with a displayed $12.03 price: do not treat that as the full
carrier-board price. Shipping/checkout for Chile is unverified. The platform's
AI overview was excluded from technical evidence. Recommendation tiles and
customer anecdotes are not specifications for the selected item.

The HTML and companion directory remain ignored in this folder. Do not commit
browser scripts or session-bearing page data. No external page code was run.

## Comparison

| Area | Current Extender / candidate evidence | Assessment |
| --- | --- | --- |
| Memory | Current architecture selects 16 MB flash and 32 MB PSRAM; Waveshare specifies the same capacities. | Capacity is suitable; verify actual device, bus mode and memory integrity. |
| Silicon/toolchain | Current Olimex D1 is P4 v1.3, esp32p4_es, accepted revision range 100–199. Pinned pioarduino 55.03.311 / Arduino 3.3.11 / IDF 5.5.5. Listing does not establish chip revision. | Do not flash the existing image blindly. Read revision and select a compatible build target. |
| Ethernet | Our ETH.begin uses IP101, address 1, MDC31, MDIO52, reset51, external RMII clock. Waveshare documents IP101GRI with the same management/reset signals and GPIO50 reference clock. | Strong match; independently confirm PHY address strapping and actual PCB revision before qualification. |
| Agon UART | Current UART1 TX12/RX22/RTS11/CTS23 at 1,152,000 baud, 8N1 with hardware flow control. Waveshare schematic assigns GPIO9–13 to I2S audio, including our TX12/RTS11; these are absent from the ordinary 40-pin GPIO header. | Remap UART to four verified available GPIOs and make a new harness map. No soldering to audio nets should be assumed necessary. |
| Other pin initialization | Current console initialization also resets a wider group of GPIOs, beyond the four UART pins. Candidate has audio, C6, SD and other peripheral assignments. | Audit every initialization and pull setting against the candidate schematic; changing uart_set_pin alone is insufficient. |
| Keyboard | Current Olimex connection uses dedicated USB_DP/DN at EXT2.19/20, not GPIO27/26. Waveshare provides Type-A USB OTG and host-selection jumpers. | Promising native host path; check PHY selection, jumper position and VBUS supply before testing. Header numbering is not transferable. |
| Programming | Candidate includes CH343P USB-UART and separate USB connectivity. | Adapt serial identities and reset/boot tooling. Existing Olimex USB assumptions do not carry over. |
| Mainboard SD | EMOS serves the Agon card through UART and foreground sdserve. | No dependency on a P4 onboard card slot. Candidate TF slot does not replace that service. |
| Wi-Fi | Candidate includes a C6 connected through SDIO. | Optional future capability; current wired HTTP/SD/keyboard/video service is not automatically a C6 Wi-Fi implementation. |
| Display | Candidate advertises two-lane MIPI DSI. | Potential future display output, not proof of a working Extender panel backend or Olimex cable/panel compatibility. |
| Power | Candidate has a PoE module header and host USB power arrangements. | PoE header is not an included PoE supply. Verify selected package and power roles; preserve separate Agon/P4 positive rails and common signal ground. |

The candidate does not remove a renderer bottleneck merely by sharing the P4
processor or offering MIPI. Framebuffer rendering and output must still be
measured separately, as the Author requested. This assessment does not amend
QUAL-003 or resume its tests.

## Required follow-through if approved

HW-003.md owns the pending decisions. A subsequently authorized adaptation
should introduce a separate board profile, preserving Olimex support, and audit
all occupied GPIOs before selecting a UART mapping. Retain EMOS ownership of
routing and transport. Preserve the existing two 7 MiB OTA slots if confirmed
16 MB flash permits the same layout. Check chip revision, flash/PSRAM operation,
recovery flashing, cold boot and OTA rollback on the specimen. Then qualify
Ethernet, USB keyboard, flow-controlled UART, CLI and SD service before graphics.
Measure framebuffer work with browser output disabled before testing delivery.
Any MIPI panel work needs its own connector, power and timing review.

## Sources inspected

1. Author's saved listing, received 2026-09-13, local ignored HTML in this folder.
2. [Waveshare current documentation](https://docs.waveshare.com/ESP32-P4-Module-DEV-KIT): memory, kit identity, connectors and host selection.
3. [Waveshare wiki and Ethernet example](https://www.waveshare.com/wiki/ESP32-P4-Module-DEV-KIT-StartPage): IP101GRI and RMII assignments.
4. [Manufacturer schematic, three pages](https://files.waveshare.com/wiki/ESP32-P4-Module-DEV-KIT/ESP32-P4-Module-DEV-KIT.pdf): page 1 header, USB-UART and I2S signal assignments. Public schematic is a reference, not proof of the seller's revision. Retrieved 2026-09-13.
5. Local baseline at Extender commit 73c25d1: docs/architecture.md (platform, silicon and memory), vdp/video/extender/transport/console_hardware.inc (UART), vdp/video/extender/network/wired_network_service.cpp (Ethernet).
6. hardware/designs/light2-harness-r03/README.md: existing UART and corrected USB keyboard mapping; this document distinguishes the schematic draft from later accepted keyboard wiring.

No firmware build, flash, wiring alteration or hardware measurement was made
for this assessment. No seller contact or purchase was performed.
