// Viewer adapter only; the public include owns all controller interpretation.
#pragma once
#include <agon/controller.hpp>
#include "view.hpp"
namespace controller_view {
#if defined(AGON_CONTROLLER_VIEW_BINDING)
using LiveBinding=AGON_CONTROLLER_VIEW_BINDING;
#else
using LiveBinding=agon::controller::Gateway;
#endif
class Live {
    agon::controller::Client<LiveBinding> client;
    void status(){
        error=client.error;
        // Preserve the viewer's existing read/request diagnostic labels.
        error_operation=client.error_operation==agon::controller::Receive?1:
                        client.error_operation==agon::controller::Send?2:client.error_operation;
    }
 public:
    unsigned error=0;
    uint8_t error_operation=0;
    bool open(){const bool ok=client.open();status();return ok;}
    bool update(Sample&s){
        const bool ok=client.update();const auto&v=client.state();status();
        memcpy(s.stick,v.stick,sizeof(s.stick));memcpy(s.trigger,v.trigger,sizeof(s.trigger));
        memcpy(s.presses,v.presses,sizeof(s.presses));
        s.held=v.held;s.sequence=v.sequence;s.age_ms=v.age_ms;s.generation=v.generation;
        s.connected=v.connected;s.valid=v.valid;s.replay=false;
        return ok;
    }
    bool close(){const bool ok=client.close();status();return ok;}
};
}
