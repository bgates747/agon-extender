#include "extender/network/messages/pump.hpp"
#include <cassert>
#include <cstdio>
#include <vector>
using namespace agon::extender::network::messages;
using Bytes = std::vector<std::uint8_t>;
static Bytes frame(const Bytes& payload) {
    const auto n = payload.size();
    Bytes out{std::uint8_t(n), std::uint8_t(n >> 8), std::uint8_t(n >> 16), std::uint8_t(n >> 24)};
    out.insert(out.end(), payload.begin(), payload.end()); return out;
}
static Bytes binary(unsigned n) { Bytes b(n); for(unsigned i=0;i<n;++i)b[i]=std::uint8_t(i); return b; }

template<std::size_t M, std::size_t D>
static void take(Channel<M,D>& c, std::uint32_t token, const Bytes& want) {
    Bytes out(want.size() + 1, 0xee); std::size_t size = 99;
    assert(c.receive(token, out.data(), out.size(), size) == Result::Ok);
    assert(size == want.size()); assert(std::equal(want.begin(),want.end(),out.begin()));
    assert(out.back() == 0xee);
}
static void splitAndCoalesced() {
    const Bytes payload{0,13,10,17,19,255,128,0}; const auto encoded = frame(payload);
    // Independent wire bytes, every possible split including empty segments.
    assert(encoded == Bytes({8,0,0,0,0,13,10,17,19,255,128,0}));
    for(std::size_t split=0;split<=encoded.size();++split) {
        Channel<8,3> c; std::uint32_t t; assert(c.open(t)==Result::Ok);
        auto a=c.feed(t,encoded.data(),split); assert(a.result==Result::Ok&&a.consumed==split);
        auto b=c.feed(t,encoded.data()+split,encoded.size()-split);
        assert(b.result==Result::Ok&&b.consumed==encoded.size()-split); take(c,t,payload);
    }
    Channel<8,3> c; std::uint32_t t; assert(c.open(t)==Result::Ok);
    Bytes coalesced=frame({}); for(auto p:{payload,Bytes{3}}){auto e=frame(p);coalesced.insert(coalesced.end(),e.begin(),e.end());}
    assert(c.feed(t,coalesced.data(),coalesced.size()).consumed==coalesced.size());
    take(c,t,{}); take(c,t,payload); take(c,t,{3});
}
static void backpressure() {
    Channel<8,2> c; std::uint32_t t; assert(c.open(t)==Result::Ok);
    Bytes bytes=frame({1}); auto second=frame({2});auto third=frame({3});
    bytes.insert(bytes.end(),second.begin(),second.end()); bytes.insert(bytes.end(),third.begin(),third.end());
    const auto progress=c.feed(t,bytes.data(),bytes.size());
    assert(progress.result==Result::Busy&&progress.consumed==10&&c.readCapacity(t)==0);
    std::size_t needed; assert(c.receive(t,nullptr,0,needed)==Result::TooSmall&&needed==1);
    take(c,t,{1}); assert(c.feed(t,bytes.data()+10,5).consumed==5);take(c,t,{2});take(c,t,{3});
    assert(c.send(t,bytes.data(),8)==Result::Ok); assert(c.send(t,nullptr,0)==Result::Ok);
    const auto before=c.pending(t);Bytes first(before.data,before.data+before.size);
    assert(c.send(t,bytes.data(),1)==Result::Busy); assert(c.pendingSends()==2);
    assert(c.sent(t,first.size()+1)==Result::Invalid&&c.sent(t,0)==Result::Invalid);
    Bytes sent;
    while(c.pendingSends()) {auto v=c.pending(t);const auto n=std::min<std::size_t>(3,v.size);sent.insert(sent.end(),v.data,v.data+n);assert(c.sent(t,n)==Result::Ok);}
    auto expected=frame(Bytes(bytes.begin(),bytes.begin()+8));auto empty=frame({});expected.insert(expected.end(),empty.begin(),empty.end());
    assert(sent==expected);
}
static void lifetimeAndFaults() {
    Channel<8,2> c;std::uint32_t t,other;assert(c.open(t)==Result::Ok&&t);
    assert(c.open(other)==Result::Busy&&other==0);
    assert(c.send(t,nullptr,1)==Result::Invalid&&c.send(t,nullptr,9)==Result::TooLarge);
    assert(c.feed(t,nullptr,1).result==Result::Invalid);
    auto good=frame({7});assert(c.feed(t,good.data(),good.size()).result==Result::Ok);
    const std::uint8_t huge[]={255,255,255,255};
    assert(c.feed(t,huge,4).result==Result::Faulted&&c.fault()==Fault::InvalidLength);
    take(c,t,{7});std::size_t n;assert(c.receive(t,nullptr,0,n)==Result::Faulted);
    assert(c.fail(t,Fault::Io)==Result::Faulted&&c.fault()==Fault::InvalidLength);
    assert(c.close(t)==Result::Ok&&c.close(t)==Result::Stale);
    assert(c.open(other)==Result::Ok&&other!=t);
    assert(c.feed(t,good.data(),good.size()).result==Result::Stale&&c.sent(t,1)==Result::Stale);
    assert(c.fail(t,Fault::Io)==Result::Stale&&c.state()==State::Open);
    assert(c.send(other,good.data(),1)==Result::Ok);assert(c.fail(other,Fault::Io)==Result::Faulted);
    assert(c.pendingSends()==1&&c.pending(other).size==0); // uncertainty retained, no replay
    assert(c.open(t)==Result::Busy);assert(c.close(other)==Result::Ok);
    assert(c.open(t)==Result::Ok&&c.pendingSends()==0);
    Channel<1,1> last(UINT32_MAX-1);assert(last.open(t)==Result::Ok&&t==UINT32_MAX);
    assert(last.close(t)==Result::Ok&&last.open(t)==Result::Exhausted&&t==0);
}
struct Fake final : Io {
    Bytes incoming, outgoing;std::size_t position{},quantum{1};unsigned reads{},writes{};
    IoState terminal=IoState::WouldBlock;bool blocked=false;unsigned invalid=0;
    IoResult read(std::uint8_t* p,std::size_t n) noexcept override {
        ++reads;if(invalid==1)return {IoState::Progress,n+1};
        if(invalid==2)return {IoState::Progress,0};
        if(invalid==3)return {IoState::WouldBlock,1};
        if(blocked)return {IoState::WouldBlock};
        n=std::min({n,quantum,incoming.size()-position});if(!n)return {terminal};
        std::copy_n(incoming.data()+position,n,p);position+=n;return {IoState::Progress,n};
    }
    IoResult write(const std::uint8_t* p,std::size_t n) noexcept override {
        ++writes;if(blocked)return {IoState::WouldBlock};
        n=std::min(n,quantum);outgoing.insert(outgoing.end(),p,p+n);return {IoState::Progress,n};
    }
};
static void budgetsAndFailures() {
    Channel<256,2> c;std::uint32_t t;assert(c.open(t)==Result::Ok);
    Fake io;io.incoming=frame(binary(256));auto payload=binary(256);assert(c.send(t,payload.data(),payload.size())==Result::Ok);
    PumpCursor cursor;
    for(unsigned i=0;i<520;++i){auto p=pump(c,t,io,cursor,1,1);assert(p.calls==1&&p.bytes==1);}
    assert(io.reads==260&&io.writes==260&&io.outgoing==frame(payload));take(c,t,payload);
    io.blocked=true;const auto blocked=pump(c,t,io,cursor,100,1000);assert(blocked.calls==1&&blocked.bytes==0);
    io.blocked=false;io.terminal=IoState::Closed;
    assert(pump(c,t,io,cursor,8,100).result==Result::Faulted&&c.fault()==Fault::PeerClosed);
    assert(c.close(t)==Result::Ok);const auto old=t;assert(c.open(t)==Result::Ok);
    auto reads=io.reads,writes=io.writes;assert(pump(c,old,io,cursor,8,100).result==Result::Stale);
    assert(io.reads==reads&&io.writes==writes);
    io.incoming={3,0};io.position=0;io.quantum=256;
    assert(pump(c,t,io,cursor,8,100).result==Result::Faulted&&c.fault()==Fault::Truncated);
    assert(c.close(t)==Result::Ok&&c.open(t)==Result::Ok);io.invalid=1;
    assert(pump(c,t,io,cursor,8,100).result==Result::Faulted&&c.fault()==Fault::InvalidIo);
    for(unsigned bad:{2u,3u}){assert(c.close(t)==Result::Ok&&c.open(t)==Result::Ok);io.invalid=bad;
        assert(pump(c,t,io,cursor,8,100).result==Result::Faulted&&c.fault()==Fault::InvalidIo);}
    assert(c.close(t)==Result::Ok&&c.open(t)==Result::Ok);io.invalid=0;io.incoming.clear();io.position=0;io.terminal=IoState::Error;
    assert(pump(c,t,io,cursor,8,100).result==Result::Faulted&&c.fault()==Fault::Io);
}
static void largerCapacity() {
    Channel<1024,4> c;std::uint32_t t;assert(c.open(t)==Result::Ok);
    auto payload=binary(1024),input=frame(payload);
    for(unsigned i=0;i<4;++i)assert(c.feed(t,input.data(),input.size()).consumed==input.size());
    assert(c.feed(t,input.data(),input.size()).result==Result::Busy);
    for(unsigned i=0;i<4;++i)take(c,t,payload);
    std::printf("storage: Channel<256,2>=%zu; Channel<1024,4>=%zu bytes (host ABI)\n",sizeof(Channel<256,2>),sizeof(c));
}
int main(){splitAndCoalesced();backpressure();lifetimeAndFaults();budgetsAndFailures();largerCapacity();std::puts("message core: 5 scenario groups passed");}
