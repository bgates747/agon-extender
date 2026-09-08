#pragma once
// PORT-011 fixed diagnostic exchange, not an EDP protocol. Driver actions are
// explicit so host tests exercise the actual stage/deadline/error logic.
#include <cstddef>
#include <cstdint>

class UartFlowPeer {
 public:
  enum class State { waiting, hold_forward, request, return_stop, hold_return,
                     ack_send, final_stop, blocked_return, quiet, pass, fail };
  enum class Action { none, allow_forward, stop_forward, queue_ack, ack_sent,
                      queue_blocked, cancel_tx, failed, passed };
  static constexpr char request[] = "FLOW\r\n";
  static constexpr char ack[] = "FLOWACK\r\n";
  State state = State::waiting;
  const char* reason = "none";
  size_t received = 0;
  uint32_t since = 0;

  Action fail(const char* why) {
    if (state != State::fail) { state = State::fail; reason = why; }
    return Action::failed;
  }
  Action tick(uint32_t now, bool cts_stop, bool tx_idle, const uint8_t* rx, size_t n) {
    if (state == State::fail) return Action::none;
    if (n && state != State::request) return fail("unexpected request bytes");
    if (state == State::request) {
      for (size_t i = 0; i < n; ++i) {
        if (received == sizeof(request)-1 || rx[i] != uint8_t(request[received]))
          return fail("wrong or extra request bytes");
        ++received;
      }
    }
    const uint32_t elapsed = now - since;
    switch (state) {
      case State::waiting:
        if (!cts_stop) { state = State::hold_forward; since = now; }
        else if (elapsed >= 180000) return fail("Agon start timeout");
        break;
      case State::hold_forward:
        if (cts_stop) return fail("Agon start withdrawn");
        if (elapsed >= 1000) {
          state = State::request; since = now; return Action::allow_forward;
        }
        break;
      case State::request:
        if (received == sizeof(request)-1) {
          state = State::return_stop; since = now; return Action::stop_forward;
        }
        if (elapsed >= 3000) return fail("request timeout");
        break;
      case State::return_stop:
        if (cts_stop) {
          state = State::hold_return; since = now; return Action::queue_ack;
        }
        if (elapsed >= 3000) return fail("no return stop edge");
        break;
      case State::hold_return:
        if (!cts_stop) {
          if (elapsed < 500) return fail("return hold too short");
          state = State::ack_send; since = now;
        } else {
          if (tx_idle) return fail("ACK escaped stopped CTS");
          if (elapsed >= 3000) return fail("return CTS never released");
        }
        break;
      case State::ack_send:
        if (tx_idle) { state = State::final_stop; since = now; return Action::ack_sent; }
        if (elapsed >= 3000) return fail("ACK transmit timeout");
        break;
      case State::final_stop:
        if (cts_stop) {
          state = State::blocked_return; since = now; return Action::queue_blocked;
        }
        if (elapsed >= 3000) return fail("no final stop edge");
        break;
      case State::blocked_return:
        if (!cts_stop || tx_idle) return fail("blocked byte escaped CTS");
        if (elapsed >= 1000) {
          state = State::quiet; since = now; return Action::cancel_tx;
        }
        break;
      case State::quiet:
        if (elapsed >= 5000) { state = State::pass; return Action::passed; }
        break;
      case State::pass: break; // Keep checking late RX/errors for the full capture.
      case State::fail: break;
    }
    return Action::none;
  }
};
