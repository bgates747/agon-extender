// Optional NM diagnostics. Inclusive elapsed intervals overlap and are NOT CPU
// time. No transport operation, allocation, clock, lock or wire access here.
#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
namespace agon::extender::network::messages::accounting {
enum class Metric : unsigned { Submit, TakeReply, QueueWait, WorkCompleteAttempt,
    PeerRequest, PeerTick, SocketRead, SocketWrite, TxEnqueue, TxIdlePoll, Count };
enum class Outcome : unsigned { Ok, Rejected, WouldBlock, Closed, Error };
constexpr unsigned metricCount=unsigned(Metric::Count);
struct Row {
    std::uint64_t calls{},units{},rejected{},wouldBlock{},closed{},errors{},elapsedUs{},maxUs{};
    std::uint32_t highwater{},active{};
};
struct Snapshot {
    std::uint64_t epochUs{},sampleUs{};
    std::array<Row,metricCount> rows{};
    bool saturated{},clockInvalid{},lifecycleInvalid{};
};
class Model {
    Snapshot state_{};bool epochSet_{};
    void epoch(std::uint64_t now) noexcept {if(!epochSet_||now<state_.epochUs){state_.epochUs=now;epochSet_=true;}}
    template<class T> void add(T &dest,T n) noexcept {
        if(n>std::numeric_limits<T>::max()-dest){dest=std::numeric_limits<T>::max();state_.saturated=true;}
        else dest+=n;
    }
    Row &row(Metric m) noexcept {return state_.rows[unsigned(m)];}
public:
    void begin(Metric m,std::uint64_t now) noexcept {
        epoch(now);
        add(row(m).active,std::uint32_t(1));
    }
    void end(Metric m,std::uint64_t start,std::uint64_t now,std::uint64_t units,
             Outcome result=Outcome::Ok,std::uint32_t highwater=0) noexcept {
        auto &r=row(m);
        if(!r.active)state_.lifecycleInvalid=true;else --r.active;
        event(m,start,now,units,result,highwater);
    }
    void event(Metric m,std::uint64_t start,std::uint64_t now,std::uint64_t units,
               Outcome result=Outcome::Ok,std::uint32_t highwater=0) noexcept {
        epoch(start);
        auto &r=row(m);add(r.calls,std::uint64_t(1));add(r.units,units);
        if(result==Outcome::Rejected)add(r.rejected,std::uint64_t(1));
        if(result==Outcome::WouldBlock)add(r.wouldBlock,std::uint64_t(1));
        if(result==Outcome::Closed)add(r.closed,std::uint64_t(1));
        if(result==Outcome::Error)add(r.errors,std::uint64_t(1));
        if(now<start)state_.clockInvalid=true;
        else {const auto dt=now-start;add(r.elapsedUs,dt);if(dt>r.maxUs)r.maxUs=dt;}
        if(highwater>r.highwater)r.highwater=highwater;
    }
    Snapshot snapshot(std::uint64_t now) const noexcept {
        auto s=state_;s.sampleUs=now;
        if(s.epochUs && now<s.epochUs)s.clockInvalid=true;
        return s;
    }
};
} // namespace agon::extender::network::messages::accounting
