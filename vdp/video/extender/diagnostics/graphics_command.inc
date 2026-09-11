// Included only inside VDUStreamProcessor::vdu_sys_video switch.
// Private QUAL-003 request: 23,0,EF,op,token(lo,hi),flags. Reply ID 0C.
// No production callback ABI is established by this temporary probe.
case 0xEF: {
    int op = readByte_t(), token = readWord_t(), flags = readByte_t();
    if (op < 1 || op > 4 || token < 0 || flags < 0 ||
        (op == 4 ? (flags < 2 || flags > 8) : flags > 1)) break;
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
