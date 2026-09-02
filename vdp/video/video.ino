//
// Title:			Agon Video BIOS
// Author:			Dean Belfield
// Contributors:	Jeroen Venema (Sprite Code, VGA Mode Switching)
//					Damien Guard (Fonts)
//					Igor Chaves Cananea (vdp-gl maintenance)
//					Steve Sims (Audio enhancements, refactoring, bug fixes)
// Created:			22/03/2022
// Last Updated:	12/09/2023
//
// Modinfo:
// 11/07/2022:		Baud rate tweaked for Agon Light, HW Flow Control temporarily commented out
// 26/07/2022:		Added VDU 29 support
// 03/08/2022:		Set codepage 1252, fixed keyboard mappings for AGON, added cursorTab, VDP serial protocol
// 06/08/2022:		Added a custom font, fixed UART initialisation, flow control
// 10/08/2022:		Improved keyboard mappings, added sprites, audio, new font
// 05/09/2022:		Moved the audio class to agon_audio.h, added function prototypes in agon.h
// 02/10/2022:		Version 1.00: Tweaked the sprite code, changed bootup title to Quark
// 04/10/2022:		Version 1.01: Can now change keyboard layout, origin and sprites reset on mode change, available modes tweaked
// 23/10/2022:		Version 1.02: Bug fixes, cursor visibility and scrolling
// 15/02/2023:		Version 1.03: Improved mode, colour handling and international support
// 04/03/2023:					+ Added logical screen resolution, sendScreenPixel now sends palette index as well as RGB values
// 09/03/2023:					+ Keyboard now sends virtual key data, improved VDU 19 to handle COLOUR l,p as well as COLOUR l,r,g,b
// 15/03/2023:					+ Added terminal support for CP/M, RTC support for MOS
// 21/03/2023:				RC2 + Added keyboard repeat delay and rate, logical coords now selectable
// 22/03/2023:					+ VDP control codes now indexed from 0x80, added paged mode (VDU 14/VDU 15)
// 23/03/2023:					+ Added VDP_GP
// 26/03/2023:				RC3 + Potential fixes for FabGL being overwhelmed by faster comms
// 27/03/2023:					+ Fix for sprite system crash
// 29/03/2023:					+ Typo in boot screen fixed
// 01/04/2023:					+ Added resetPalette to MODE, timeouts to VDU commands
// 08/04/2023:				RC4 + Removed delay in readbyte_t, fixed VDP_SCRCHAR, VDP_SCRPIXEL
// 12/04/2023:					+ Fixed bug in playNote
// 13/04/2023:					+ Fixed bootup fail with no keyboard
// 17/04/2023:				RC5 + Moved wait_completion in vdu so that it only executes after graphical operations
// 18/04/2023:					+ Minor tweaks to wait completion logic
// 12/05/2023:		Version 1.04: Now uses vdp-gl instead of FabGL, implemented GCOL mode, sendModeInformation now sends video mode
// 19/05/2023:					+ Added VDU 4/5 support
// 25/05/2023:					+ Added VDU 24, VDU 26 and VDU 28, fixed inverted text colour settings
// 30/05/2023:					+ Added VDU 23,16 (cursor movement control)
// 28/06/2023:					+ Improved get_screen_char, fixed vdu_textViewport, cursorHome, changed modeline for Mode 2
// 30/06/2023:					+ Fixed vdu_sys_sprites to correctly discard serial input if bitmap allocation fails
// 13/08/2023:				RC2	+ New video modes, mode change resets page mode
// 05/09/2023:					+ New audio enhancements, improved mode change code
// 12/09/2023:					+ Refactored
// 17/09/2023:					+ Added ZDI mode

#include <HardwareSerial.h>
#ifndef AGON_EXTENDER_P4_BOOT
#include <WiFi.h>
#endif
#ifdef AGON_EXTENDER_P4_BOOT
#include "extender/compat/p4_vdp_gl.hpp"
#else
#include <fabgl.h>
#endif
#include <ESP32Time.h>
#ifdef AGON_EXTENDER_P4_BOOT
#include <esp_log.h>
#include <esp_heap_caps.h>
#if !defined(AGON_EXTENDER_SOURCE_IDENTITY) || \
      !defined(AGON_EXTENDER_BUILD_ID) || \
      !defined(AGON_EXTENDER_ARTIFACT_STATUS)
#error "The P4 boot target requires explicit build-identity definitions"
#endif
#ifdef AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION
#ifndef AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY
#error "The P4 qualification target requires an explicit composition identity"
#endif
#elif defined(AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY)
#error "Ordinary P4 boot targets must not carry a qualification composition identity"
#endif
#endif

// Serial Debug Mode: 1 = enable
// Always enabled on the emulator, to support --verbose mode
#ifdef USERSPACE
#undef DEBUG
# define	DEBUG			1
#else /* !USERSPACE */
#undef DEBUG
# define	DEBUG			0
#endif /* USERSPACE */

#define SERIALBAUDRATE	115200

#ifdef USERSPACE
extern uint32_t startup_screen_mode; /* in rust_glue.cpp */
#else /* !USERSPACE */
#define startup_screen_mode 0
#endif /* !USERSPACE */

HardwareSerial	DBGSerial(0);

#include "agon.h"								// Configuration file

TerminalState	terminalState = TerminalState::Disabled;		// Terminal state (for CP/M, etc)
bool			consoleMode = false;			// Serial console mode (0 = off, 1 = console enabled)
bool			printerOn = false;				// Output "printer" to debug serial link
bool			controlKeys = true;				// Control keys enabled
ESP32Time		rtc(0);							// The RTC

#include "version.h"							// Version information
#ifdef AGON_EXTENDER_P4_BOOT
#include "extender/input/unavailable_input_adapter.hpp"
#include "extender/port/p4_task_watchdog.hpp"
#else
#include "agon_ps2.h"							// Keyboard support
#include "agon_audio.h"							// Audio support
#endif
#include "agon_screen.h"						// Screen support
#include "agon_ttxt.h"
#ifdef AGON_EXTENDER_P4_BOOT
#include "extender/network/wired_network_service.hpp"
#if defined(AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION)
#include "extender/transport/p4_parallel_qualification.hpp"
#elif defined(AGON_EXTENDER_PORT008_FORWARD)
#include "extender/transport/forward_parallel_stream.hpp"
#else
#include "extender/transport/disconnected_stream.hpp"
#endif
#include "extender/web/browser_video_provider.hpp"
#else
#include "vdp_protocol.h"						// VDP Protocol
#endif
#include "vdu_stream_processor.h"
#ifndef AGON_EXTENDER_P4_BOOT
#include "hexload.h"
#endif

#ifndef AGON_EXTENDER_P4_BOOT
std::unique_ptr<fabgl::Terminal>	Terminal;	// Used for Terminal emulation mode (for CP/M, etc)
#endif
VDUStreamProcessor *	processor;				// VDU Stream Processor

#if !defined(USERSPACE) && !defined(AGON_EXTENDER_P4_BOOT)
#include "zdi.h"								// ZDI debugging console
#endif /* !USERSPACE */

#ifdef AGON_EXTENDER_P4_BOOT
#if defined(AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION)
// The qualification composition owns its production objects and returns the
// one heap Stream that VDUStreamProcessor adopts below.
#elif defined(AGON_EXTENDER_PORT008_FORWARD)
// Rejected predecessor branch.  p4-forward-vdp is blocked by its retired
// source-selection record; retain this binding only to keep old source and
// evidence intelligible.
agon::extender::transport::ForwardParallelStream forwardVDPStream;
#else
agon::extender::transport::DisconnectedStream disconnectedVDPStream;
#endif
std::unique_ptr<agon::extender::web::BrowserVideoProvider>	browserVideoProvider;
std::unique_ptr<agon::extender::network::WiredNetworkService>	wiredNetworkService;
#endif

TaskHandle_t		Core0Task;					// Core 0 task handle

void setup() {
	#ifndef VDP_USE_WDT
		#ifdef AGON_EXTENDER_P4_BOOT
		// Official VDP v2.16.0 disables each classic-ESP32 IDLE watchdog
		// below. Arduino-ESP32 3.3.11 removes those P4 tasks but leaves
		// ESP-IDF 5.5.5's feed hooks active, producing a continuous error
		// flood. Use the hook-aware public ESP-IDF path on P4, retain the
		// original total delay, and fail closed if reconfiguration fails.
		if (!agon::extender::port::disableRetainedVdpIdleWatchdogs()) {
			ESP_LOGE("extender_boot", "retained VDP watchdog setup failed");
			return;
		}
		delay(200); delay(200);
		#else
		disableCore0WDT(); delay(200);				// Disable the watchdog timers
		disableCore1WDT(); delay(200);
		#endif
	#endif
	#ifdef AGON_EXTENDER_P4_BOOT
		// Stock UART0 GPIO 3/1 is inapplicable on the DevKit. ESP-IDF logging is
		// routed to the sdkconfig-selected USB Serial/JTAG console instead.
		#ifdef AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION
			ESP_LOGW("extender_identity",
				"NON-RELEASE COMPILE/LINK QUALIFICATION TARGET; DO NOT DEPLOY");
			ESP_LOGW("extender_identity", "qualification_composition=%s",
				AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY);
			#endif
		ESP_LOGI("extender_identity", "source_identity=%s",
			AGON_EXTENDER_SOURCE_IDENTITY);
		ESP_LOGI("extender_identity", "build_id=%s", AGON_EXTENDER_BUILD_ID);
		ESP_LOGI("extender_identity", "artifact_status=%s",
			AGON_EXTENDER_ARTIFACT_STATUS);
		ESP_LOGI("extender_boot", "retained VDP setup starting");
	#else
		DBGSerial.begin(SERIALBAUDRATE, SERIAL_8N1, 3, 1);
	#endif
	changeMode(startup_screen_mode);
	copy_font();
	#ifdef AGON_EXTENDER_P4_BOOT
		#if defined(AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION)
		auto *qualificationVDPStream =
			agon::extender::transport::
				beginP4ParallelNonreleaseQualification();
		if (qualificationVDPStream == nullptr) {
			ESP_LOGE("extender_boot",
				"non-release production transport composition failed");
			return;
		}
		processor = new VDUStreamProcessor(qualificationVDPStream);
		#elif defined(AGON_EXTENDER_PORT008_FORWARD)
		if (!forwardVDPStream.begin()) {
			ESP_LOGE("extender_boot", "forward transport start failed");
			return;
		}
		processor = new VDUStreamProcessor(&forwardVDPStream);
		#else
		processor = new VDUStreamProcessor(&disconnectedVDPStream);
		#endif
	#else
		setupVDPProtocol();
		processor = new VDUStreamProcessor(&VDPSerial);
	#endif
	auto processTaskResult = xTaskCreatePinnedToCore(
		processLoop,
		"processLoop",
		4096,		// Stack size - highwater mark checks show this generally still leaves about 2000 words free
		NULL,
		3,			// Priority
		&Core0Task,
		0			// Core 0
	);
	#ifdef AGON_EXTENDER_P4_BOOT
			if (processTaskResult != pdPASS) {
				ESP_LOGE("extender_boot", "retained process task creation failed");
				#ifdef AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION
				agon::extender::transport::
					requestP4ParallelNonreleaseQualificationStop();
				#endif
				return;
			}
	#else
		(void)processTaskResult;
		initAudio();
	#endif
	boot_screen();
	#ifdef AGON_EXTENDER_P4_BOOT
		if (_VGAController == nullptr) {
			ESP_LOGE("extender_boot", "browser service has no display controller");
		} else {
			browserVideoProvider.reset(
				new agon::extender::web::BrowserVideoProvider(
					_VGAController->snapshotPool()));
			wiredNetworkService.reset(
				new agon::extender::network::WiredNetworkService(
					*browserVideoProvider));
			if (!wiredNetworkService->start()) {
				ESP_LOGE("extender_boot", "wired browser service start failed");
			}
		}
	#endif
	debug_log("Setup ran on core %d, busy core is %d\n\r", xPortGetCoreID(), CoreUsage::busiestCore());
}

// The main loop
//
void loop() {
	while (true) {
		delay(1000);
		#ifdef AGON_EXTENDER_P4_BOOT
			// Phase F target qualification reads only thread-safe, sink-owned
			// counters here. Do not sample LogicalFrameService::metrics() while
			// its task is running: that interface is intentionally post-stop.
			static uint8_t diagnosticSeconds = 0;
			if (++diagnosticSeconds >= 10) {
				diagnosticSeconds = 0;
				#ifdef AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION
				agon::extender::transport::logP4QualificationStatus();
				#endif
				if (_VGAController != nullptr) {
					auto const snapshot = _VGAController->snapshotPool().metrics();
					ESP_LOGI("extender_snapshot",
						"enabled=%u alloc_fail=%u cadence=%u transition=%u "
						"producer_busy=%u no_slot=%u compose_fail=%u "
						"published=%u no_new=%u",
						static_cast<unsigned>(snapshot.enabled),
						static_cast<unsigned>(snapshot.allocation_failures),
						static_cast<unsigned>(snapshot.cadence_skips),
						static_cast<unsigned>(snapshot.transition_busy),
						static_cast<unsigned>(snapshot.producer_busy),
						static_cast<unsigned>(snapshot.producer_no_slot),
						static_cast<unsigned>(snapshot.composition_failures),
						static_cast<unsigned>(snapshot.publications),
						static_cast<unsigned>(snapshot.consumer_no_new));
				}
				if (wiredNetworkService != nullptr) {
					auto const network = wiredNetworkService->metrics();
					ESP_LOGI("extender_network",
						"state=%u clients=%u refused=%u credits=%u protocol=%u "
						"sent=%u send_fail=%u disconnect_release=%u http=%u/%u "
						"http_fail=%u queued=%u queue_fail=%u socket_fail=%u",
						static_cast<unsigned>(wiredNetworkService->state()),
						static_cast<unsigned>(network.video.clients_accepted),
						static_cast<unsigned>(network.video.clients_refused),
						static_cast<unsigned>(network.video.credits_accepted),
						static_cast<unsigned>(network.video.protocol_errors),
						static_cast<unsigned>(network.video.sends_completed),
						static_cast<unsigned>(network.video.sends_failed),
						static_cast<unsigned>(network.video.disconnect_releases),
						static_cast<unsigned>(network.http_starts),
						static_cast<unsigned>(network.http_stops),
						static_cast<unsigned>(network.http_start_failures),
						static_cast<unsigned>(network.queued_sends),
						static_cast<unsigned>(network.queue_failures),
						static_cast<unsigned>(network.socket_send_failures));
				}
				if (browserVideoProvider != nullptr) {
					auto const provider = browserVideoProvider->metrics();
					ESP_LOGI("extender_provider",
						"acquired=%u no_new=%u invalid=%u sent=%u failed=%u "
						"disconnected=%u",
						static_cast<unsigned>(provider.acquired),
						static_cast<unsigned>(provider.no_new_message),
						static_cast<unsigned>(provider.invalid_snapshot),
						static_cast<unsigned>(provider.released_sent),
						static_cast<unsigned>(provider.released_failed),
						static_cast<unsigned>(provider.released_disconnected));
				}
				ESP_LOGI("extender_heap",
					"free_8bit=%u minimum_8bit=%u free_psram=%u minimum_psram=%u",
					static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_8BIT)),
					static_cast<unsigned>(heap_caps_get_minimum_free_size(MALLOC_CAP_8BIT)),
					static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)),
					static_cast<unsigned>(heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM)));
			}
		#endif
	};
}

void processLoop(void * parameter) {
#ifdef USERSPACE
	uint32_t count = 0;
#endif /* USERSPACE */

	setupKeyboardAndMouse();
	processor->wait_eZ80();

	while (true) {
#ifdef USERSPACE
 		if ((count & 0x7f) == 0) {
			delay(1 /* -TM- ms */);
		}
 		count++;
#endif /* USERSPACE */

		#ifdef VDP_USE_WDT
			esp_task_wdt_reset();
		#endif
		if (processTerminal()) {
			continue;
		}

		processor->processNext();
	}
}

// The boot screen
//
void boot_screen() {
	printFmt("Agon %s VDP Version %d.%d.%d", VERSION_VARIANT, VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH);
	#if VERSION_CANDIDATE > 0
		printFmt(" %s%d", VERSION_TYPE, VERSION_CANDIDATE);
	#endif
	#ifdef VERSION_SUBTITLE
		printFmt(" %s", VERSION_SUBTITLE);
	#endif
	// Show build if defined (intended to be auto-generated string from build script from git commit hash)
	#ifdef VERSION_BUILD
		printFmt(" Build %s", VERSION_BUILD);
	#endif
	printFmt("\n\r");
}

// Debug printf to PC
//
#ifndef USERSPACE
void debug_log(const char *format, ...) {
	#if DEBUG == 1
	va_list ap;
	va_start(ap, format);
	auto size = vsnprintf(nullptr, 0, format, ap) + 1;
	if (size > 0) {
		va_end(ap);
		va_start(ap, format);
		char buf[size + 1];
		vsnprintf(buf, size, format, ap);
		DBGSerial.print(buf);
	}
	va_end(ap);
	#endif
}
#endif

void force_debug_log(const char *format, ...) {
	va_list ap;
	va_start(ap, format);
	auto size = vsnprintf(nullptr, 0, format, ap) + 1;
	if (size > 0) {
		va_end(ap);
		va_start(ap, format);
		char buf[size + 1];
		vsnprintf(buf, size, format, ap);
		#ifdef AGON_EXTENDER_P4_BOOT
			ESP_LOGI("extender_vdp", "%s", buf);
		#else
			DBGSerial.print(buf);
		#endif
	}
	va_end(ap);
}

// Set console mode
// Parameters:
// - mode: 0 = off, 1 = on
//
void setConsoleMode(bool mode) {
	#ifdef AGON_EXTENDER_P4_BOOT
		(void)mode;
		consoleMode = false;
	#else
	consoleMode = mode;
	#endif
}

// Terminal mode state machine transition calls
//
void startTerminal() {
	#ifdef AGON_EXTENDER_P4_BOOT
		terminalState = TerminalState::Disabled;
		return;
	#else
	switch (terminalState) {
		case TerminalState::Disabled: {
			terminalState = TerminalState::Enabling;
		} break;
		case TerminalState::Suspending: {
			terminalState = TerminalState::Enabled;
		} break;
		case TerminalState::Suspended: {
			terminalState = TerminalState::Resuming;
		} break;
	}
	#endif
}

void stopTerminal() {
	#ifdef AGON_EXTENDER_P4_BOOT
		terminalState = TerminalState::Disabled;
		return;
	#else
	switch (terminalState) {
		case TerminalState::Enabled:
		case TerminalState::Resuming: 
		case TerminalState::Suspended:
		case TerminalState::Suspending: {
			terminalState = TerminalState::Disabling;
		} break;
		case TerminalState::Enabling: {
			terminalState = TerminalState::Disabled;
		} break;
	}
	#endif
}

void suspendTerminal() {
	#ifdef AGON_EXTENDER_P4_BOOT
		terminalState = TerminalState::Disabled;
		return;
	#else
	switch (terminalState) {
		case TerminalState::Enabled:
		case TerminalState::Resuming: {
			terminalState = TerminalState::Suspending;
			processTerminal();
		} break;
		case TerminalState::Enabling: {
			// Finish enabling, then suspend
			processTerminal();
			terminalState = TerminalState::Suspending;
		} break;
	}
	#endif
}

// Process terminal state machine
//
bool processTerminal() {
	#ifdef AGON_EXTENDER_P4_BOOT
		return false;
	#else
	switch (terminalState) {
		case TerminalState::Disabled: {
			// Terminal is not currently active, so pass on to VDU system
			return false;
		} break;
		case TerminalState::Suspended: {
			// Terminal temporarily deactivated, so pass on to VDU system
			return false;
		} break;
		case TerminalState::Enabling: {
			// Turn on the terminal
			Terminal = std::unique_ptr<fabgl::Terminal>(new fabgl::Terminal());
			Terminal->begin(_VGAController.get());
			Terminal->connectSerialPort(VDPSerial);
			Terminal->enableCursor(true);
			// onVirtualKey is triggered whenever a key is pressed or released
			Terminal->onVirtualKeyItem = [&](VirtualKeyItem * vkItem) {
				if (vkItem->vk == VirtualKey::VK_F12) {
					if (vkItem->CTRL && (vkItem->LALT || vkItem->RALT)) {
						// CTRL + ALT + F12: emergency exit terminal mode
						stopTerminal();
					}
				}
			};

			// onUserSequence is triggered whenever a User Sequence has been received (ESC + '_#' ... '$'), where '...' is sent here
			Terminal->onUserSequence = [&](char const * seq) {
				// 'Q!': exit terminal mode
				if (strcmp("Q!", seq) == 0) {
					stopTerminal();
				}
				if (strcmp("S!", seq) == 0) {
					suspendTerminal();
				}
				if (seq[0] == 'F') {
					uint32_t fontnum = textToWord(seq + 1);
					if (fontnum >= 0) {
						auto font = fonts[fontnum]; 	// get shared_ptr to font -- was fonts[bufferID]
						if (font != nullptr && font->chptr == nullptr) {	// check it's defined
							Terminal->loadFont(font.get());
						}
					}
				}
			};
			debug_log("Terminal enabled\n\r");
			terminalState = TerminalState::Enabled;
		} break;
		case TerminalState::Enabled: {
			// Write anything read from z80 to the screen
			// but do this a byte at a time, as VDU commands after a "suspend" will get lost
			if (processor->byteAvailable()) {
				Terminal->write(processor->readByte());
			}
		} break;
		case TerminalState::Disabling: {
			Terminal->deactivate();
			Terminal = nullptr;
			auto context = processor->getContext();
			// reset our screen mode
			processor->vdu_mode(videoMode);
			debug_log("Terminal disabled\n\r");
			terminalState = TerminalState::Disabled;
		} break;
		case TerminalState::Suspending: {
			// No need to deactivate terminal here... we just stop sending it serial data
			debug_log("Terminal suspended\n\r");
			terminalState = TerminalState::Suspended;
		} break;
		case TerminalState::Resuming: {
			// As we're not deactivating the terminal, we don't need to re-activate it here
			debug_log("Terminal resumed\n\r");
			terminalState = TerminalState::Enabled;
		} break;
		default: {
			debug_log("processTerminal: unknown terminal state %d\n\r", terminalState);
			return false;
		} break;
	}
	return true;
	#endif
}

void print(char const * text) {
	for (auto i = 0; i < strlen(text); i++) {
		processor->vdu(text[i], false);
	}
}

void printFmt(const char *format, ...) {
	va_list ap;
	va_start(ap, format);
	int size = vsnprintf(nullptr, 0, format, ap) + 1;
	if (size > 0) {
		va_end(ap);
		va_start(ap, format);
		char buf[size + 1];
		vsnprintf(buf, size, format, ap);
		print(buf);
	}
	va_end(ap);
}
