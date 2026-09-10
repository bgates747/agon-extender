/* AUDIT-005 paired pathway measurement, running wholly as an SD application.
 * No new resident MOS code, direct peripheral access, interrupt masking or
 * video-mode selection. Autoexec configures mode 0 on both endpoints.
 *
 * Deliberate measurement qualifications: the CLI row includes buffer copying
 * and resident parsing, not just putch; output-return is not wire completion;
 * pixel replies bound logical drawing, not browser presentation. The pinned
 * delimiter and CLI paths do not reliably propagate partial-send failures.
 * Their reported zero status must be read alongside reply/pixel/wire evidence.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"

extern uint24_t bench_clock(const volatile uint8_t *clock);
extern uint24_t bench_count(const uint8_t *data, uint24_t length);
extern uint24_t bench_bytes(const uint8_t *data);
extern uint24_t bench_delimiter(const uint8_t *data);

#define CHUNKS 512u
#define CHUNK_SIZE 64u
#define PIXEL_FLAG 4u
#define MODE_FLAG 16u
#define REPLY_DEADLINE_TICKS 600u /* Five seconds on the selected 60 Hz board. */
#define REPLY_MAX_WAITS 24u       /* CPU-loop backstop if the clock stops. */
static const char *const entries[] = {"byte", "count", "delimiter", "cli-putch"};
static const char *const payloads[] = {"null", "points"};
static volatile uint8_t *sv;
static uint8_t data[65];
static char command_template[256], command[256], line[768], filename[80];
static FIL file;
static unsigned row_number, saved_rows;
static unsigned trace_entry, trace_payload;
static int trace_only;
static int probe_only;
static int file_created;
static const char *phase = "startup";
static unsigned active_route;
/* Capture before SD timestamp queries can change other VDP flags. Probe mode
 * keeps the first timeout as failure. Suite mode measures completion within
 * its declared five-second bound and separately records the stock timeout. */
static struct {
    unsigned flag, send_status, first_status, final_status, flags;
    uint24_t start, sent, first, final;
    uint8_t r, g, b, index;
} observation;
/* Exported debugger observation, not a communication path to the device. */
volatile unsigned bench_exit_status = 1;
__attribute__((noinline)) void bench_done(void) { __asm__ volatile("nop"); }

typedef struct {
    unsigned repeat, route, entry, payload, chunks;
    uint24_t t0, t1, t2;
    unsigned send_status, reply_status;
    uint8_t r, g, b, index, mode, colours;
    unsigned width, height, valid;
    unsigned setup_first_status, first_reply_status;
    uint24_t setup_reply_ticks, reply_wait_ticks;
} Row;

static uint24_t elapsed(uint24_t end, uint24_t start) { return end - start; }
static unsigned word_at(unsigned offset) { return sv[offset] | ((unsigned)sv[offset+1] << 8); }

static unsigned cli(const char *text) {
    if (strlen(text) >= sizeof(command)) return FR_INVALID_PARAMETER;
    strcpy(command, text);
    return mos_oscli(command, NULL, 0);
}

static unsigned query(const uint8_t *bytes, unsigned length, unsigned flag) {
    memset(&observation, 0, sizeof(observation));
    observation.flag = flag;
    mos_clearvdpflags(flag);
    observation.start = bench_clock(sv);
    unsigned status = bench_count(bytes, length);
    observation.sent = bench_clock(sv);
    observation.send_status = status;
    observation.first_status = status ? status : mos_waitforvdpflags(flag);
    observation.first = bench_clock(sv);
    observation.final_status = observation.first_status;
    /* Probe only: observe the SAME outstanding reply for nine further API
     * waits. Do not retransmit, clear its flag again or accept a late PASS.
     * Ten bounded stock API calls also escape if the VBlank clock stalls. */
    if (probe_only && !status && observation.first_status == FR_TIMEOUT)
        for (unsigned i=0; i<9 && observation.final_status == FR_TIMEOUT; ++i)
            observation.final_status = mos_waitforvdpflags(flag);
    /* r03 measurement remedy: hardware returned the post-clear pixel at
     * 66 ticks, after stock wait_VDP expired at 30. Continue observing that
     * single request for BOTH routes, preserving the initial timeout in CSV.
     * This measures latency; it does not repair or qualify ordinary MOS waits. */
    if (!probe_only && !status)
        for (unsigned i=1; observation.final_status == FR_TIMEOUT &&
             elapsed(bench_clock(sv),observation.sent)<REPLY_DEADLINE_TICKS &&
             i<REPLY_MAX_WAITS; ++i)
            observation.final_status = mos_waitforvdpflags(flag);
    observation.final = bench_clock(sv);
    observation.flags = getsysvar_vdp_pflags();
    observation.r = sv[sysvar_scrpixel];
    observation.g = sv[sysvar_scrpixel+1];
    observation.b = sv[sysvar_scrpixel+2];
    observation.index = sv[sysvar_scrpixelIndex];
    if (probe_only) return observation.first_status;
    if (elapsed(observation.final,observation.sent)>REPLY_DEADLINE_TICKS) return FR_TIMEOUT;
    return observation.final_status;
}

static unsigned route_to(unsigned route) {
    phase = "route-command";
    unsigned status = cli(route ? "emos excom --keep-display" : "emos legacy --keep-display");
    if (status) return status;
    active_route = route;
    phase = "route-mode-query";
    const uint8_t mode_query[] = {23,0,0x86};
    status = query(mode_query, sizeof(mode_query), MODE_FLAG);
    if (status) return status;
    if (sv[sysvar_scrMode] != 0 || word_at(sysvar_scrWidth) != 640 ||
        word_at(sysvar_scrHeight) != 480 || sv[sysvar_scrColours] != 16)
        return FR_INVALID_PARAMETER;
    return 0;
}

static unsigned pixel(unsigned x, unsigned y) {
    const uint8_t bytes[] = {23,0,0x84,x,x >> 8,y,y >> 8};
    return query(bytes, sizeof(bytes), PIXEL_FLAG);
}

static unsigned prepare_screen(void) {
    /* Text/graphics defaults and physical top-left coordinates. Mode stays put. */
    const uint8_t setup[] = {4,26,20,17,15,17,128,18,0,128,18,0,15,
                            29,0,0,0,0,23,0,0xc0,0,23,1,0,12,16};
    phase = "screen-setup";
    unsigned status = bench_count(setup, sizeof(setup));
    if (status) return status;
    /* This text is above, and does not intersect, the target pixel y=24. */
    if (probe_only) puts("Pixel reply diagnostic - leave keys released");
    else printf("UART benchmark %u/48 - leave keys released\r\n", row_number);
    phase = "cleared-pixel-query";
    status = pixel(64,24);
    if (status) return status;
    phase = "cleared-pixel-value";
    return (sv[sysvar_scrpixel] | sv[sysvar_scrpixel+1] | sv[sysvar_scrpixel+2]) ? 1 : 0;
}

static void prepare_payload(unsigned payload) {
    memset(data, 0, sizeof(data));
    if (payload) {
        for (unsigned i=0; i<8; ++i) {
            uint8_t *p=data+i*8;
            p[0]=25; p[1]=69; p[2]=(i+1)*8; p[4]=24;
        }
    }
    data[64]=255;
    strcpy(command_template, "VDU");
    for (unsigned i=0; i<64; ++i)
        snprintf(command_template+strlen(command_template),
                 sizeof(command_template)-strlen(command_template), " %u", (unsigned)data[i]);
}

static unsigned write_open(const char *text) {
    unsigned size = strlen(text);
    unsigned status = ffs_fwrite(&file, text, size) == size ? 0 : FR_DISK_ERR;
    unsigned sync_status = ffs_fsync(&file);
    unsigned close_status = ffs_fclose(&file);
    return status ? status : (sync_status ? sync_status : close_status);
}

static unsigned append(const char *text) {
    unsigned status = ffs_fopen(&file, filename, FA_WRITE | FA_OPEN_APPEND);
    return status ? status : write_open(text);
}

static unsigned save_observation(unsigned status) {
    snprintf(line,sizeof(line),
        "# query;route=%s;phase=%s;status=%u;flag=%u;send_status=%u;first_status=%u;"
        "final_status=%u;send_ticks=%u;first_wait_ticks=%u;total_wait_ticks=%u;"
        "flags=%u;rgb=%u/%u/%u;index=%u\r\n",
        active_route ? "excom" : "legacy",phase,status,observation.flag,
        observation.send_status,observation.first_status,observation.final_status,
        elapsed(observation.sent,observation.start),elapsed(observation.first,observation.sent),
        elapsed(observation.final,observation.sent),observation.flags,
        (unsigned)observation.r,(unsigned)observation.g,(unsigned)observation.b,(unsigned)observation.index);
    return append(line);
}

static unsigned probe_route(unsigned route) {
    unsigned status=route_to(route);
    unsigned saved=save_observation(status);
    if (status || saved) return status ? status : saved;
    phase="initial-pixel-query";
    status=pixel(64,24);
    saved=save_observation(status);
    if (status || saved) return status ? status : saved;
    status=prepare_screen();
    saved=save_observation(status);
    if (status || saved) return status ? status : saved;
    prepare_payload(1);
    phase="point-output";
    status=bench_count(data,CHUNK_SIZE);
    if (!status) {
        phase="white-pixel-query";
        status=pixel(64,24);
        if (!status && (observation.r!=255 || observation.g!=255 || observation.b!=255)) status=1;
    }
    saved=save_observation(status);
    return status ? status : saved;
}

static unsigned start_file(void) {
    for (unsigned i=1; i<=99999; ++i) {
        snprintf(filename, sizeof(filename), "/extender/uartbench/results/%08u.CSV", i);
        unsigned status = ffs_fopen(&file, filename, FA_WRITE | FA_CREATE_NEW);
        if (status == FR_EXIST) continue;
        if (status) return status;
        snprintf(line, sizeof(line),
            "# build=%s;status=%s\r\n# emos=%s;edp=%s;mainboard_vdp=2.16.0\r\n"
            "# mode=%s;baud=1152000;clock_units_per_second=120;clock_resolution_units=2\r\n"
            "# browser=one_visible_connected_client_operator_required;entries_include_caller_cost\r\n"
            "# completion_deadline_ticks=600;max_wait_calls=24;probe_retains_first_timeout=1\r\n"
            "row,repeat,route,entry,payload,chunks,bytes,t0,t1,t2,send_ticks,tail_ticks,total_ticks,"
            "send_status,reply_status,pixel_r,pixel_g,pixel_b,pixel_index,mode,width,height,colours,valid,"
            "setup_first_status,setup_reply_ticks,first_reply_status,reply_wait_ticks\r\n",
            BENCH_BUILD_ID, BENCH_STATUS, BENCH_EMOS, BENCH_EDP,
            probe_only ? "probe" : (trace_only ? "trace" : "suite"));
        status=write_open(line);
        if (!status) file_created=1;
        return status;
    }
    return FR_EXIST;
}

static unsigned save_row(const Row *r) {
    snprintf(line, sizeof(line),
        "%u,%u,%s,%s,%s,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\r\n",
        row_number,r->repeat,r->route ? "excom" : "legacy",entries[r->entry],payloads[r->payload],
        r->chunks,r->chunks*64,r->t0,r->t1,r->t2,elapsed(r->t1,r->t0),elapsed(r->t2,r->t1),
        elapsed(r->t2,r->t0),r->send_status,r->reply_status,(unsigned)r->r,(unsigned)r->g,
        (unsigned)r->b,(unsigned)r->index,(unsigned)r->mode,r->width,r->height,
        (unsigned)r->colours,r->valid,r->setup_first_status,r->setup_reply_ticks,
        r->first_reply_status,r->reply_wait_ticks);
    unsigned status=append(line);
    if (!status) ++saved_rows;
    return status;
}

static unsigned measure(unsigned repeat, unsigned route, unsigned entry, unsigned payload) {
    Row r={0};
    r.repeat=repeat; r.route=route; r.entry=entry; r.payload=payload;
    ++row_number;
    unsigned status=prepare_screen();
    if (status) {
        save_observation(status);
        snprintf(line,sizeof(line),"# failure;row=%u;route=%s;phase=%s;status=%u\r\n",
                 row_number,route ? "excom" : "legacy",phase,status);
        append(line);
        return status;
    }
    r.setup_first_status=observation.first_status;
    r.setup_reply_ticks=elapsed(observation.final,observation.sent);
    prepare_payload(payload);
    r.mode=sv[sysvar_scrMode]; r.width=word_at(sysvar_scrWidth);
    r.height=word_at(sysvar_scrHeight); r.colours=sv[sysvar_scrColours];
    if (trace_only && (status=pixel(200,400))) return status;
    phase="workload-output";
    r.t0=bench_clock(sv);
    for (unsigned i=0; i<CHUNKS; ++i) {
        switch (entry) {
        case 0: r.send_status=bench_bytes(data); break;
        case 1: r.send_status=bench_count(data,CHUNK_SIZE); break;
        case 2: r.send_status=bench_delimiter(data); break;
        default:
            /* Copy is intentionally inside the CLI row's measured interval. */
            strcpy(command,command_template);
            r.send_status=mos_oscli(command,NULL,0);
            break;
        }
        if (r.send_status) break;
        ++r.chunks;
    }
    r.t1=bench_clock(sv);
    if (!r.send_status) { phase="completion-pixel-query"; r.reply_status=pixel(64,24); }
    else r.reply_status=255; /* not issued after a known partial send */
    r.t2=bench_clock(sv);
    r.first_reply_status=r.send_status ? 255 : observation.first_status;
    r.reply_wait_ticks=r.send_status ? 0 : elapsed(observation.final,observation.sent);
    r.r=sv[sysvar_scrpixel]; r.g=sv[sysvar_scrpixel+1]; r.b=sv[sysvar_scrpixel+2];
    r.index=sv[sysvar_scrpixelIndex];
    unsigned expected=payload ? 255 : 0;
    r.valid=!r.send_status && !r.reply_status && r.chunks==CHUNKS &&
            r.r==expected && r.g==expected && r.b==expected && elapsed(r.t1,r.t0)>0;
    status=save_row(&r);
    if (status) return status;
    if (!r.valid) return r.send_status ? r.send_status : (r.reply_status ? r.reply_status : 1);
    printf("Saved %s/%s: send %u ticks, complete %u ticks\r\n",
           entries[entry],payloads[payload],elapsed(r.t1,r.t0),elapsed(r.t2,r.t0));
    return 0;
}

int main(int argc, char **argv) {
    unsigned status=0;
    sv=mos_sysvars();
    printf("UART benchmark %s (%s)\r\n",BENCH_BUILD_ID,BENCH_STATUS);
    if (argc==2 && !strcmp(argv[1],"probe")) probe_only=1;
    else if (argc>1) {
        if (argc!=4 || strcmp(argv[1],"trace")) {
            puts("Usage: RUN . [probe | trace byte|count|delimiter|cli-putch null|points]");
            return FR_INVALID_PARAMETER;
        }
        for (trace_entry=0;trace_entry<4;++trace_entry)
            if (!strcmp(argv[2],entries[trace_entry])) break;
        for (trace_payload=0;trace_payload<2;++trace_payload)
            if (!strcmp(argv[3],payloads[trace_payload])) break;
        if (trace_entry==4 || trace_payload==2) return FR_INVALID_PARAMETER;
        trace_only=1;
    }
    status=start_file();
    if (status) { printf("Cannot create results file: %u\r\n",status); goto finish; }
    if (probe_only) {
        status=probe_route(0);
        if (!status) status=probe_route(1);
    } else if (trace_only) {
        status=route_to(1);
        if (!status) status=measure(1,1,trace_entry,trace_payload);
    } else {
        for (unsigned repeat=1;repeat<=3 && !status;++repeat)
            for (unsigned route=0;route<2 && !status;++route) {
                status=route_to(route);
                for (unsigned entry=0;entry<4 && !status;++entry)
                    for (unsigned payload=0;payload<2 && !status;++payload)
                        status=measure(repeat,route,entry,payload);
            }
    }
finish:;
    const char *failed_phase=phase;
    unsigned failed_route=active_route;
    unsigned recovery=route_to(0);
    if (!status) status=recovery;
    if (file_created) {
        snprintf(line,sizeof(line),"# %s;rows=%u;status=%u;legacy_return=%u\r\n",
                 status ? "failed" : "complete",saved_rows,status,recovery);
        unsigned saved=append(line);
        if (saved) status=saved;
    }
    const uint8_t cursor_on[]={4,23,1,1,13,10};
    if (!recovery) bench_count(cursor_on,sizeof(cursor_on));
    if (probe_only || status)
        printf("%s: %s, %s, status %u\r\n",probe_only ? "Pixel reply diagnostic" : "Stopped",
               failed_route ? "ExCom" : "Legacy",failed_phase,status);
    if (probe_only)
        printf("Pixel reply diagnostic %s\r\n%s\r\n",status ? "FAILED" : "PASS",filename);
    else
        printf("UART benchmark %s: %u rows saved\r\n%s\r\n",
               status ? "FAILED / INCOMPLETE" : "PASS",saved_rows,filename);
    puts("Return the SD card to the PC for the timing comparison.");
    bench_exit_status=status;
    bench_done();
    return status;
}
