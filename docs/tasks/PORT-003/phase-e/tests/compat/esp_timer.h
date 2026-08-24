// PORT-003 Phase E declaration-only host surface for P4FrameService.
// The Teletext host harness supplies a synchronous service implementation and
// does not compile or pretend to exercise the ESP timer/task adapter.
#pragma once

using esp_timer_handle_t = void *;
