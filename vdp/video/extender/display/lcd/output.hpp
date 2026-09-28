#pragma once
#include "config.hpp"
#if AGON_EXTENDER_LCD
#include "extender/display/presentation_snapshot_pool.hpp"
namespace agon::extender::display { bool startLcdOutput(PresentationSnapshotPool &pool); }
#endif
