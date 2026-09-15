// PORT-004 framing-only backend for the retained stock v2.16.0 dispatcher.
// No synthesizer, audio tasks or samples exist on P4. Operations fail honestly;
// status/volume use the stock disabled/failure value255. The dispatcher still
// consumes fields and emits its normal protocol replies through EMOS.
#pragma once
#include <cstdint>

inline std::uint8_t playNote(std::uint8_t,std::uint8_t,std::uint16_t,std::uint16_t) noexcept {return 0;}
inline std::uint8_t clearSample(std::uint16_t) noexcept {return 0;}
inline void resetSamples() noexcept {}
inline bool channelEnabled(std::uint8_t) noexcept {return false;}
inline std::uint8_t getChannelStatus(std::uint8_t) noexcept {return 255;}
inline std::uint8_t setVolume(std::uint8_t,std::uint8_t) noexcept {return 255;}
inline std::uint8_t setFrequency(std::uint8_t,std::uint16_t) noexcept {return 0;}
inline std::uint8_t setWaveform(std::uint8_t,std::int8_t,std::uint16_t) noexcept {return 0;}
inline std::uint8_t seekTo(std::uint8_t,std::uint32_t) noexcept {return 0;}
inline std::uint8_t setDuration(std::uint8_t,std::uint16_t) noexcept {return 0;}
inline std::uint8_t setSampleRate(std::uint8_t,std::uint16_t) noexcept {return 0;}
inline std::uint8_t enableChannel(std::uint8_t) noexcept {return 0;}
inline std::uint8_t disableChannel(std::uint8_t) noexcept {return 0;}
inline void audioTaskKill(int) noexcept {}

inline uint8_t VDUStreamProcessor::loadSample(uint16_t, uint32_t length) {
    // Stock readIntoBuffer owns streaming reads/echo/timeouts. A fixed stack
    // sink cannot fail allocation and leak a legitimate sample into VDU parsing.
    // A timed-out/truncated unframed stream still cannot be resynchronized.
    uint8_t sink[64];
    while (length) {
        const auto count = length < sizeof(sink) ? length : sizeof(sink);
        if (readIntoBuffer(sink, count) != 0) return 0;
        length -= count;
    }
    return 0;
}
inline uint8_t VDUStreamProcessor::createSampleFromBuffer(uint16_t,uint8_t,uint16_t) {return 0;}
inline uint8_t VDUStreamProcessor::setSampleFrequency(uint16_t,uint16_t) {return 0;}
inline uint8_t VDUStreamProcessor::setSampleRepeatStart(uint16_t,uint32_t) {return 0;}
inline uint8_t VDUStreamProcessor::setSampleRepeatLength(uint16_t,uint32_t) {return 0;}
inline uint8_t VDUStreamProcessor::setParameter(uint8_t,uint8_t,uint16_t) {return 0;}

inline uint8_t VDUStreamProcessor::setVolumeEnvelope(uint8_t, uint8_t type) {
    // Stock backend reads these only for enabled channels. Our unavailable
    // channels must nevertheless consume the documented wire grammar. Keep
    // field order aligned with stock, without allocating envelope objects.
    switch (type) {
        case AUDIO_ENVELOPE_ADSR:
            if (readWord_t() == -1) return 0;
            if (readWord_t() == -1) return 0;
            if (readByte_t() == -1) return 0;
            if (readWord_t() == -1) return 0;
            break;
        case AUDIO_ENVELOPE_MULTIPHASE_ADSR:
            for (unsigned group = 0; group < 3; ++group) {
                const auto count = readByte_t(); if (count == -1) return 0;
                for (int phase = 0; phase < count; ++phase) {
                    if (readByte_t() == -1) return 0;
                    if (readWord_t() == -1) return 0;
                }
            }
            break;
    }
    return 0;
}
inline uint8_t VDUStreamProcessor::setFrequencyEnvelope(uint8_t, uint8_t type) {
    if (type == AUDIO_FREQUENCY_ENVELOPE_STEPPED) {
        const auto count = readByte_t(); if (count == -1) return 0;
        if (readByte_t() == -1) return 0;
        if (readWord_t() == -1) return 0;
        for (int phase = 0; phase < count; ++phase) {
            if (readWord_t() == -1) return 0;
            if (readWord_t() == -1) return 0;
        }
    }
    return 0;
}
