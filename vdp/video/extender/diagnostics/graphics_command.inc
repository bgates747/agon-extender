// Included only inside VDUStreamProcessor::vdu_sys_video switch.
// Private QUAL-003 request: 23,0,EF,op,token(lo,hi),flags. Reply ID 0C.
// No production callback ABI is established by this temporary probe.
case 0xEF: {
    int op = readByte_t(), token = readWord_t(), flags = readByte_t();
    if (op < 1 || op > 10 || token < 0 || flags < 0 ||
        (op == 4 ? (flags < 2 || flags > 8) : op == 8 ? (flags < 1 || flags > 3) : flags > 1)) break;
    using namespace agon_graphics_timing;
    static uint16_t current_token;
    static bool armed, saved;
    static Result result;
    auto reply = [&](uint8_t metric, uint32_t value, uint32_t count) {
        uint8_t packet[16] = {'Q','T','G',0xA1,uint8_t(token),uint8_t(token>>8),metric,
#if defined(AGON_EXTENDER_CONSOLE) || defined(AGON_GRAPHICS_TIMING_PEER)
            1,
#else
            0,
#endif
            uint8_t(value),uint8_t(value>>8),uint8_t(value>>16),uint8_t(value>>24),
            uint8_t(count),uint8_t(count>>8),uint8_t(count>>16),uint8_t(count>>24)};
        send_packet(0x0C,sizeof packet,packet);
    };
    auto fence = [&]() {
        uint16_t t=issue();
        fabgl::Primitive marker; marker.cmd=fabgl::PrimitiveCmd::GraphicsFence;
        marker.ivalue=t; _VGAController->addPrimitive(marker);
        uint32_t start=now();
        while (!complete(t) && uint32_t(now()-start)<10000000U) delay(1);
        return complete(t);
    };
    // Reusable game timing: batch records, no success reply in a frame hot loop.
    // Diagnostic barriers deliberately remain normal-worker operations. They
    // perturb pipelining; the package requires pacing-only/empty controls.
    static agon_frame_records::Recorder frames;
    static uint16_t frame_session;
    if (op >= 5) {
        if (op == 5) {
            frames.reset();frame_session=uint16_t(token);
            if (!fence()) { frames.fail(); reply(8,1,0); }
            else reply(0,0x475431,agon_frame_records::Capacity);
        }
        else if (op == 6) {
            // Reset / preceding end already completed its normal-worker fence.
            // Do not add a second per-update vblank barrier at begin.
            frames.begin(uint16_t(token),now());
        } else if (op == 7) {
            uint32_t submitted=now();
            if (!fence()) frames.fail();
            else frames.end(uint16_t(token),submitted,now());
        } else if (op == 9) {
            if(uint16_t(token)!=frame_session){reply(8,2,frames.size());break;}
            bool ok=frames.stop();reply(0,ok?0:1,frames.size());
        } else if (op == 8) {
            auto r=frames.get(unsigned(token));
            if (!r) reply(8,1,frames.size());
            else reply(uint8_t(flags),flags==1?r->submitted_us:flags==2?r->completed_us:r->drain_us,frames.size());
        } else if (op == 10) {
            // Post-capture only. The stock debug logger uses the board's configured
            // diagnostic console, not the keyboard port or EMOS VDU stream.
            if (frames.fault() || !frames.get(0)) reply(8,1,frames.size());
            else {
                force_debug_log("GT1,id,submitted_us,completed_us,drain_us\n");
                for(unsigned i=0;i<frames.size();++i) {
                    auto r=frames.get(i);
                    force_debug_log("GT1,%u,%lu,%lu,%lu\n",i,(unsigned long)r->submitted_us,
                      (unsigned long)r->completed_us,(unsigned long)r->drain_us);
                }
                reply(0,0,frames.size());
            }
        }
        break;
    }
    if (op == 1) {
        if (!fence()) { reply(8,0,1); break; } // normal worker, never forced drain
        current_token = token; armed = true; saved = false;
        reply(0,1,flags);     // admission reply precedes the measured interval
        begin(flags != 0);
    } else if (op != 4 && armed && token == current_token) {
        uint32_t t = now();
        if (op == 2 && !fence()) { armed=false; (void)finish(now()-t); reply(8,0,1); break; }
        // op 3 observes recurring output without introducing any flush/refresh.
        result = finish(now()-t); armed = false; saved = true;
        reply(1,result.elapsed,result.drain);
    } else if (op == 4 && saved && token == current_token) {
        // One outstanding response. A burst of eight records can overrun the
        // eZ80 callback/receive path and manufacture a measurement failure.
        if (flags == 8) reply(8,result.overhead,256);
        else {
            unsigned i=(flags-2)/2;
            const auto &c=result.count[i];
            if (flags & 1) reply(flags,c.maximum,c.crossing);
            else reply(flags,c.us,c.calls);
        }
    }
} break;
