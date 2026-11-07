#include "accounting.hpp"
#if defined(AGON_EXTENDER_NM_ACCOUNTING)
#include <freertos/FreeRTOS.h>
#include <esp_timer.h>
#include <cstdio>
#include <cinttypes>
namespace agon::extender::network::messages::accounting {
namespace {
portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
Model model;
constexpr const char *names[]={"submit","take_reply","queue_wait","work_complete_attempt",
    "peer_request","peer_tick","socket_read","socket_write","tx_enqueue","tx_idle_poll"};
static_assert(sizeof(names)/sizeof(*names)==metricCount);
constexpr const char *actors[]={"console","console","nm_worker","nm_worker","nm_worker","nm_worker","nm_worker","nm_worker","shared_uart_console","shared_uart_console"};
constexpr const char *units[]={"accepted_nm_body_bytes","reply_body_bytes","dequeued_nm_body_bytes","candidate_reply_bytes","reply_body_bytes","none","socket_bytes","socket_bytes","accepted_uart_bytes","none"};
}
std::uint64_t nowUs() noexcept {return std::uint64_t(esp_timer_get_time());}
void begin(Metric m,std::uint64_t start) noexcept {
    portENTER_CRITICAL(&mutex);model.begin(m,start);portEXIT_CRITICAL(&mutex);
}
void end(Metric m,std::uint64_t start,std::uint64_t units,Outcome outcome,std::uint32_t highwater) noexcept {
    const auto now=nowUs();
    portENTER_CRITICAL(&mutex);model.end(m,start,now,units,outcome,highwater);portEXIT_CRITICAL(&mutex);
}
void event(Metric m,std::uint64_t start,std::uint64_t units,Outcome outcome,std::uint32_t highwater) noexcept {
    const auto now=nowUs();
    portENTER_CRITICAL(&mutex);model.event(m,start,now,units,outcome,highwater);portEXIT_CRITICAL(&mutex);
}
std::string json() {
    // Lock order is existing Runtime mailbox -> recorder; this reader never
    // takes a Runtime/driver/socket lock and never formats JSON under the lock.
    portENTER_CRITICAL(&mutex);const auto s=model.snapshot(nowUs());portEXIT_CRITICAL(&mutex);
    std::string out="{\"schema\":\"p4-nm-accounting-r01\",\"clock\":\"esp_timer_us64\",\"cpu_accounting\":false,\"inclusive_nonadditive\":true,\"quiescence_proven\":false,\"physical_cts_observed\":false,";
    char b[512];
    const int length=std::snprintf(b,sizeof b,"\"epoch_us\":%llu,\"sample_us\":%llu,\"saturated\":%s,\"clock_invalid\":%s,\"lifecycle_invalid\":%s,\"rows\":[",
        (unsigned long long)s.epochUs,(unsigned long long)s.sampleUs,
        s.saturated?"true":"false",s.clockInvalid?"true":"false",s.lifecycleInvalid?"true":"false");if(length<0||unsigned(length)>=sizeof b)return {};out+=b;
    for(unsigned i=0;i<metricCount;++i){const auto &r=s.rows[i];
        const int rowLength=std::snprintf(b,sizeof b,"%s{\"metric\":\"%s\",\"actor\":\"%s\",\"unit\":\"%s\",\"calls\":%llu,\"units\":%llu,\"rejected\":%llu,\"would_block\":%llu,\"closed\":%llu,\"errors\":%llu,\"inclusive_us\":%llu,\"max_us\":%llu,\"sampled_highwater\":%" PRIu32 ",\"active\":%" PRIu32 "}",
            i?",":"",names[i],actors[i],units[i],(unsigned long long)r.calls,(unsigned long long)r.units,
            (unsigned long long)r.rejected,(unsigned long long)r.wouldBlock,(unsigned long long)r.closed,(unsigned long long)r.errors,
            (unsigned long long)r.elapsedUs,(unsigned long long)r.maxUs,r.highwater,r.active);if(rowLength<0||unsigned(rowLength)>=sizeof b)return {};out+=b;
    }
    return out+"]}";
}
} // namespace agon::extender::network::messages::accounting
#endif
