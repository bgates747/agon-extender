// Default OFF. No recorder, clock call, allocation, lock or HTTP reader exists in
// the disabled composition. Enabled scopes report inclusive wall microseconds,
// including preemption; they must never be summed as processor utilization.
#pragma once
#include "accounting_model.hpp"
#if defined(AGON_EXTENDER_NM_ACCOUNTING) && defined(AGON_EXTENDER_NETWORK_PARALLEL)
#error "NM accounting r01 is restricted to the UART mailbox composition"
#endif
#if defined(AGON_EXTENDER_NM_ACCOUNTING)
#include <string>
#endif
namespace agon::extender::network::messages::accounting {
#if defined(AGON_EXTENDER_NM_ACCOUNTING)
std::uint64_t nowUs() noexcept;
void begin(Metric,std::uint64_t) noexcept;
void end(Metric,std::uint64_t,std::uint64_t,Outcome,std::uint32_t) noexcept;
void event(Metric,std::uint64_t,std::uint64_t,Outcome,std::uint32_t=0) noexcept;
std::string json(); // HTTP task only; coherent copy, formatting outside the lock.
class Scope {
    Metric metric_;std::uint64_t start_,units_{};Outcome outcome_{Outcome::Ok};
    std::uint32_t highwater_{};
public:
    explicit Scope(Metric m) noexcept:metric_(m),start_(nowUs()){begin(metric_,start_);}
    ~Scope(){end(metric_,start_,units_,outcome_,highwater_);}
    void result(std::uint64_t units,Outcome outcome=Outcome::Ok,std::uint32_t highwater=0) noexcept {
        units_=units;outcome_=outcome;highwater_=highwater;
    }
    Scope(const Scope&)=delete;Scope&operator=(const Scope&)=delete;
};
#else
inline std::uint64_t nowUs() noexcept {return 0;}
inline void event(Metric,std::uint64_t,std::uint64_t,Outcome,std::uint32_t=0) noexcept {}
class Scope {
public:
    explicit Scope(Metric) noexcept {}
    void result(std::uint64_t,Outcome=Outcome::Ok,std::uint32_t=0) noexcept {}
};
#endif
} // namespace agon::extender::network::messages::accounting
