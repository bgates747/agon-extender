// Contract model, not real CPU occupation, receiver or transport measurement.
#pragma once
#include "../fixtures/comms_performance/engine.hpp"
struct PerformanceModel {
    unsigned prepared=0,submitted=0,validated=0,cleaned=0,clock_reads=0;
    uint32_t tick=10;
    comms_performance::Admission admission=comms_performance::submit_accepted;
    comms_performance::Witness source{true,true},done{true,true};
    bool prepare_ok=true,validation_ok=true;
    bool prepare(const comms_performance::Corpus&){++prepared;return prepare_ok;}
    uint32_t clock(){++clock_reads;return tick;}
    comms_performance::Admission submit(const comms_performance::Corpus&){++submitted;tick+=2;return admission;}
    comms_performance::Witness wait_source(){tick+=3;return source;}
    comms_performance::Witness wait_complete(){tick+=7;return done;}
    bool validate(const comms_performance::Corpus&){++validated;tick+=100;return validation_ok;}
    bool cleanup(){++cleaned;tick+=100;return true;}
};
