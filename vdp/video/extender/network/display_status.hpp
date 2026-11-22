// Additive read-only browser metadata; independent of video/keyboard ownership.
#pragma once
#include "extender/display/mode_status.hpp"
#include <cstdio>
#include <cstring>
#include <esp_http_server.h>
#ifdef AGON_EXTENDER_HDMI
#include "extender/display/hdmi_output.hpp"
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
#include "extender/display/rgb888_pixel.hpp"
#endif
#ifdef AGON_EXTENDER_NATIVE_SCANOUT
#include "extender/display/native_scanout/native_scanout.h"
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
#include "extender/display/native_scanout/native_trace.h"
#endif
#include "extender/display/native_scanout/native_row_profile.h"
#include <cstring>
#include "esp_heap_caps.h"
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "extender/display/rolling/strip_probe.h"
#include "esp_heap_caps.h"
#endif
namespace agon::extender::display_status {
#ifdef AGON_EXTENDER_NATIVE_SCANOUT
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
// The worker/ISR only seal raw words. Translate them to JSON on request.
inline esp_err_t startupTrace(httpd_req_t *request) {
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  httpd_resp_set_type(request, "application/json");
  agon_native_trace_t trace;
  if (!agon_native_get_startup_trace(&trace))
    return httpd_resp_sendstr(request, "{\"available\":false}");

  static constexpr const char *events[] = {
    "third_last_retired", "penultimate_retired", "final_retired", "enqueued", "dequeued",
    "wake_lock_wait", "wake_lock_held", "wake_begin", "wake_end",
    "gate_wait", "gate_open", "gate_bypass", "read_lock_wait", "read_lock_held", "owned", "bound",
    "render_begin", "render_end", "clear", "already_black", "cache_begin", "cache_end", "cache_skip",
    "publish_wait", "publish_held", "published", "decision"
  };
  static_assert(sizeof(events) / sizeof(*events) == NR_T_COUNT);
  static constexpr const char *sites[] = {
    "rearm", "retire", "successor", "enqueue", "invalid", "underrun", "ownership", "publish"
  };
  static constexpr const char *phases[] = {"none", "active", "inactive", "row_lock", "compose", "expand"};
  static constexpr const char *admissions[] = {"unknown", "unbound_black", "inactive", "live"};
  static_assert(sizeof(sites) / sizeof(*sites) == NR_SITE_PUBLISH + 1);
  static_assert(sizeof(phases) / sizeof(*phases) == NR_ROW_EXPAND + 1);
  static_assert(sizeof(admissions) / sizeof(*admissions) == NR_ADMIT_LIVE + 1);
  const unsigned phase = trace.row_cursor >> 16;
  if (phase >= sizeof(phases)/sizeof(*phases) || trace.site >= sizeof(sites)/sizeof(*sites))
    return ESP_FAIL;
  const bool armed = trace.target_armed != 0;
  const bool fault = trace.fault != AGON_NATIVE_OK;
  const bool eof = trace.site == NR_SITE_REARM;
  const bool published = trace.stamp[NR_T_PUBLISHED] != UINT32_MAX;
  const bool lower_bound = eof && fault && !published && trace.stamp[NR_T_DECISION] != UINT32_MAX;
  const char *budget = "unknown";
  if (published) budget = trace.stamp[NR_T_PUBLISHED] <= trace.limit_us ? "met" : "exceeded";
  else if (lower_bound && trace.stamp[NR_T_DECISION] > trace.limit_us) budget = "exceeded";
  else if (armed && trace.site == NR_SITE_PUBLISH && trace.fault == AGON_NATIVE_BUDGET &&
           trace.fault_frame == trace.target_frame && trace.fault_block == 0) {
    // The worker can reject at the pre-VALID reserve or revoke a late VALID.
    // Neither path supplies a successful publication time.
    budget = "rejected";
  }

  // Worker milestones are ordered along its single request. DMA retirement
  // interrupts and the seal decision have their own concurrent timestamps.
  const char *last = armed ? events[NR_T_RETIRE_12] : "none";
  for (unsigned i = NR_T_ENQUEUED; i <= NR_T_PUBLISHED; ++i) {
    if (trace.stamp[i] != UINT32_MAX) last = events[i];
  }
  if (trace.stamp[NR_T_RENDER_BEGIN] != UINT32_MAX &&
      trace.stamp[NR_T_RENDER_END] == UINT32_MAX && phase != NR_ROW_NONE)
    last = phases[phase];

  char header[400];
  int n = snprintf(header, sizeof(header),
      "{\"available\":true,\"epoch\":%u,\"retired\":%u,"
      "\"queue_depth\":%u,\"slot_frame\":%u,\"slot_block\":%u,\"slot_ready\":%u,"
      "\"fault\":%u,\"site\":\"%s\",\"admission\":\"%s\",\"row_phase\":\"%s\","
      "\"last_stage\":\"%s\",\"limit_us\":%u,\"budget\":\"%s\"",
      unsigned(trace.epoch), unsigned(trace.retired), unsigned(trace.queue_depth),
      unsigned(trace.slot_frame), unsigned(trace.slot_block), unsigned(trace.slot_ready),
      unsigned(trace.fault), sites[trace.site], admissions[nr_admission(trace.row_cursor, trace.stamp)],
      phases[phase], last, unsigned(trace.limit_us), budget);
  if (n < 0 || size_t(n) >= sizeof(header) ||
      httpd_resp_send_chunk(request, header, n) != ESP_OK) return ESP_FAIL;
  const struct { const char *key; uint32_t value; bool known; } fields[] = {
    {"frame", trace.target_frame, armed}, {"block", 0, armed},
    {"fault_frame", trace.fault_frame, fault}, {"fault_block", trace.fault_block, fault},
    {"rearmed", trace.rearmed, eof}, {"row", trace.row_cursor & 0xffffu, phase >= NR_ROW_LOCK},
    {"refill_us", trace.stamp[NR_T_PUBLISHED], published},
    {"refill_lower_bound_us", trace.stamp[NR_T_DECISION], lower_bound}
  };
  char field[64];
  for (const auto &f : fields) {
    n = f.known ? snprintf(field, sizeof(field), ",\"%s\":%u", f.key, unsigned(f.value))
                : snprintf(field, sizeof(field), ",\"%s\":null", f.key);
    if (n < 0 || size_t(n) >= sizeof(field) ||
        httpd_resp_send_chunk(request, field, n) != ESP_OK) return ESP_FAIL;
  }
  constexpr char elapsed[] = ",\"elapsed_us\":{";
  if (httpd_resp_send_chunk(request, elapsed, sizeof(elapsed) - 1) != ESP_OK) return ESP_FAIL;
  bool first = true;
  for (unsigned i = 0; i < NR_T_COUNT; ++i) {
    if (trace.stamp[i] == UINT32_MAX) continue;
    n = snprintf(field, sizeof(field), "%s\"%s\":%u", first ? "" : ",", events[i], unsigned(trace.stamp[i]));
    if (n < 0 || size_t(n) >= sizeof(field) ||
        httpd_resp_send_chunk(request, field, n) != ESP_OK) return ESP_FAIL;
    first = false;
  }
  if (httpd_resp_send_chunk(request, "}}", 2) != ESP_OK) return ESP_FAIL;
  return httpd_resp_send_chunk(request, nullptr, 0);
}
#endif
// Independent of mode publication: a failed first mode must leave its DMA
// evidence readable. Formatting runs on the HTTP task after a bounded snapshot.
inline esp_err_t nativeScanout(httpd_req_t *request) {
  agon_native_stats_t v{};
  char query[24]{};
  if (httpd_req_get_url_query_len(request) != 0) {
    if (httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK)
      return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Unknown scanout query");
#ifdef AGON_EXTENDER_NATIVE_STARTUP_TRACE
    if (std::strcmp(query, "startup_trace=1") == 0) return startupTrace(request);
#endif
    if (std::strcmp(query, "last_fault=1") != 0) {
      return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Unknown scanout query");
    }
    if (!agon_native_get_last_fault(&v)) {
      httpd_resp_set_hdr(request, "Cache-Control", "no-store");
      httpd_resp_set_type(request, "application/json");
      return httpd_resp_sendstr(request, "{\"available\":false}");
    }
  } else {
    agon_native_get_stats(&v);
  }
  agon_native_row_profile_t sample{};
  // Profiles describe the live logical mode. A saved hardware fault has its own epoch.
  if (!query[0]) agon_native_get_row_profile(&sample);
  char bins[17 * 12]{};
  size_t used = 0;
  for (auto count : v.histogram) {
    const int n = snprintf(bins + used, sizeof(bins) - used, "%s%u", used ? "," : "", unsigned(count));
    if (n < 0 || size_t(n) >= sizeof(bins) - used) return ESP_FAIL;
    used += size_t(n);
  }
  char body[1600];
  const int n = snprintf(body, sizeof(body),
      "{\"epoch\":%u,\"width\":%u,\"height\":%u,\"frames\":%u,\"blocks\":%u,"
      "\"ready\":%u,\"draw_wakes\":%u,\"max_queue\":%u,\"max_refill_us\":%u,"
      "\"min_sw_lead_us\":%u,\"max_queue_us\":%u,\"max_render_us\":%u,\"max_sync_us\":%u,"
      "\"worst\":{\"frame\":%u,\"block\":%u,\"queue_us\":%u,\"render_us\":%u,\"sync_us\":%u},"
      "\"fault\":%u,\"fault_frame\":%u,\"fault_block\":%u,\"fault_elapsed_us\":%u,"
      "\"fault_queue_us\":%u,\"fault_render_us\":%u,\"fault_sync_us\":%u,"
      "\"underruns\":%u,\"invalid\":%u,\"rejected\":%u,\"free_internal_bytes\":%u,"
      "\"largest_internal_bytes\":%u,\"largest_internal_dma_bytes\":%u,\"free_psram_bytes\":%u,\"refill_histogram_100us\":[%s],"
      "\"min_draw_gap_us\":%u,\"sampled_rows\":{\"generation\":%u,\"samples\":%u,\"frame\":%u,"
      "\"block\":%u,\"source_rows\":%u,\"total_cycles\":%u,\"lock_wait_cycles\":%u,"
      "\"stock_cycles\":%u,\"expand_cycles\":%u}}",
      unsigned(v.epoch), unsigned(v.width), unsigned(v.height), unsigned(v.frames),
      unsigned(v.blocks), unsigned(v.ready), unsigned(v.ticks), unsigned(v.max_queue),
      unsigned(v.max_refill_us), unsigned(v.min_lead_us), unsigned(v.max_queue_us),
      unsigned(v.max_render_us), unsigned(v.max_sync_us), unsigned(v.worst_frame),
      unsigned(v.worst_block), unsigned(v.worst_queue_us), unsigned(v.worst_render_us),
      unsigned(v.worst_sync_us), unsigned(v.fault), unsigned(v.fault_frame),
      unsigned(v.fault_block), unsigned(v.fault_elapsed_us), unsigned(v.fault_queue_us),
      unsigned(v.fault_render_us), unsigned(v.fault_sync_us), unsigned(v.underruns),
      unsigned(v.invalid), unsigned(v.rejected), unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
      unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL)),
      unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT)),
      unsigned(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)), bins, unsigned(v.min_draw_gap_us),
      unsigned(sample.generation), unsigned(sample.samples), unsigned(sample.frame),
      unsigned(sample.block), unsigned(sample.source_rows), unsigned(sample.total_cycles),
      unsigned(sample.lock_wait_cycles), unsigned(sample.stock_cycles), unsigned(sample.expand_cycles));
  if (n < 0 || size_t(n) >= sizeof(body)) return ESP_FAIL;
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  httpd_resp_set_type(request, "application/json");
  return httpd_resp_send(request, body, n);
}
#endif
inline esp_err_t handle(httpd_req_t *request) {
  display::ModeStatus value{};
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  httpd_resp_set_type(request,"application/json");
  if (!display::modeStatus.read(value)) {
    httpd_resp_set_status(request,"503 Service Unavailable");
    return httpd_resp_sendstr(request,"{\"available\":false}");
  }
#ifdef AGON_EXTENDER_HDMI
  const unsigned outputSize=display::hdmiOutput().outputSize();
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  // HDMI02-F: read-only fault evidence must remain reachable if a stopped DMA
  // prevents the output worker reaching its normal periodic serial report.
  strip_probe_stats strips{}; strip_async_stats copy{};
  strip_probe_read(&strips); strip_async_read(&copy);
  strip_fault_stats fault{}; strip_fault_read(&fault);
  strip_budget_stats budget{}; strip_budget_read(&budget);
#endif
  char body[1536];
  const int length=snprintf(body,sizeof(body),
      "{\"available\":true,\"mode\":%u,\"width\":%u,\"height\":%u,"
      "\"colors\":%u,\"refresh_hz\":%u,\"double_buffered\":%s"
#if defined(AGON_EXTENDER_HDMI)
      ",\"output\":\"hdmi\",\"output_width\":%d,\"output_height\":%d,"
      "\"output_nominal_refresh_hz\":60,\"frame_clock\":\"dma-frame-complete\""
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
      ",\"render_storage\":\"%s\",\"render_memory\":\"%s\""
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      ",\"rolling\":{\"frames\":%u,\"faults\":%u,\"late\":%u,"
      "\"over_budget\":%u,\"underruns\":%u,\"refill_max_us\":%u,\"free_internal\":%u,"
      "\"invalid_blocks\":%u,\"sequence_errors\":%u,\"cache_errors\":%u,\"overlap\":%u,"
      "\"first_fault\":%u,\"first_error\":%u,\"queued\":%u,\"queue_wait_max_us\":%u,"
      "\"budget_phases\":{\"available\":%u,\"queue_us\":%u,\"prepare_us\":%u,"
      "\"source_cache_us\":%u,\"submit_to_callback_us\":%u,\"finish_us\":%u,"
      "\"driver_phases_valid\":%u,\"descriptor_us\":%u,\"admission_us\":%u,"
      "\"channel_setup_us\":%u,\"dma_and_irq_us\":%u,\"handoff_us\":%u}}"
#endif
      "}",
      value.mode,value.width,value.height,value.colors,value.refresh_hz,
      value.double_buffered?"true":"false"
#ifdef AGON_EXTENDER_HDMI
      ,int(outputSize >> 16),int(outputSize & 65535)
#endif
#ifdef AGON_EXTENDER_DIRECT_RGB888
#ifdef AGON_EXTENDER_INDEXED_PPA
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"linear-rgb222":"native"
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"psram-linear":"native"
#else
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"rgb888":"native"
      ,display::rgb888ExperimentGeometry(value.colors,value.width,value.height)?"panel-direct":"native"
#endif
#endif
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
      ,unsigned(strips.frames),unsigned(copy.faults),unsigned(copy.late),
      unsigned(strips.over_budget),unsigned(strips.underruns),unsigned(strips.max_us),
      unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
      unsigned(strips.invalid),unsigned(strips.sequence_errors),unsigned(strips.cache_errors),
      unsigned(copy.overlap),unsigned(fault.first_fault),unsigned(fault.first_error),
      unsigned(fault.queued),unsigned(fault.queue_wait_max_us),
      unsigned(budget.available),unsigned(budget.queue_us),unsigned(budget.prepare_us),
      unsigned(budget.source_cache_us),unsigned(budget.submit_to_callback_us),unsigned(budget.finish_us),
      unsigned(budget.driver_phases_valid),unsigned(budget.descriptor_us),unsigned(budget.admission_us),
      unsigned(budget.channel_setup_us),unsigned(budget.dma_and_irq_us),unsigned(budget.handoff_us)
#endif
      );
  if (length<0 || length>=int(sizeof(body)))
    return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Display status overflow");
  return httpd_resp_send(request,body,length);
}
}
