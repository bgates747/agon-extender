// AUDIT-010 RP06: selected P4 display prepare/commit boundary.
//
// All factory/configuration callbacks run before commit and unwind through
// unique ownership on failure. commitPreparedMode contains no resource factory;
// after retire() it can only bind, activate and publish the complete candidate.
#pragma once

#include <cassert>
#include <cstdint>
#include <memory>
#include <utility>

namespace agon::extender::display {

template<class Controller, class Canvas, class Service>
struct PreparedModeCandidate {
  std::unique_ptr<Controller> controller;
  std::unique_ptr<Canvas> canvas;
  std::unique_ptr<Service> service;
  std::uint16_t width{};
  std::uint16_t height{};
  std::uint8_t colours{};
  unsigned refresh_hz{};
  bool double_buffered{};

  bool complete() const noexcept {
    return controller != nullptr && canvas != nullptr && service != nullptr &&
           width != 0 && height != 0 && refresh_hz != 0;
  }
};

template<class Candidate, class MakeController, class ConfigureController,
         class MakeCanvas, class MakeService, class PrepareService>
bool prepareModeCandidate(Candidate &candidate,
                          MakeController makeController,
                          ConfigureController configureController,
                          MakeCanvas makeCanvas,
                          MakeService makeService,
                          PrepareService prepareService) {
  candidate.controller = makeController();
  if (!candidate.controller || !configureController(*candidate.controller))
    return false;
  candidate.canvas = makeCanvas(*candidate.controller);
  if (!candidate.canvas) return false;
  candidate.service = makeService();
  if (!candidate.service ||
      !prepareService(*candidate.service, *candidate.controller))
    return false;
  return candidate.complete();
}

template<class Candidate, class Retire, class Bind, class Activate,
         class Publish>
void commitPreparedMode(Candidate &&candidate, Retire retire, Bind bind,
                        Activate activate, Publish publish) {
  assert(candidate.complete());
  retire();
  bind(*candidate.controller);
  activate(*candidate.service);
  publish(std::move(candidate));
}

}  // namespace agon::extender::display
