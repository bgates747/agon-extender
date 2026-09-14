/* Scrolling-only adaptation of the accepted hardware voice player.
 * No mode switch, clear-screen, cursor positioning or measured work here. */
#include <agon/mos.h>
#include <agon/vdp.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define VOICE_PATH "/extender/attention.wav"

#define SAMPLE_BUFFER 24000
static uint8_t block[4096];
static uint32_t sample_bytes;
static uint16_t sample_rate;

static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1]<<8 |
           (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
static uint16_t le16(const uint8_t *p) { return p[0] | (uint16_t)p[1]<<8; }
static int read_exact(uint8_t f, unsigned n) {
    return mos_fread(f, (char *)block, n) == n;
}
static void wait_ticks(uint32_t ticks) {
    uint32_t start=getsysvar_time();
    while ((uint32_t)(getsysvar_time()-start)<ticks) {}
}
static void audio_begin(void) {
    volatile uint8_t *sv=mos_sysvars();
    sv[sysvar_vdp_pflags]&=(uint8_t)~0x08;
}
static int audio_ok(void) {
    uint32_t start=getsysvar_time();
    while (!(getsysvar_vdp_pflags()&0x08))
        if ((uint32_t)(getsysvar_time()-start)>240) return 0;
    return getsysvar_audioSuccess()==1;
}
static int play_wav(void) {
    uint8_t f=mos_fopen(VOICE_PATH, FA_READ);
    int ok=0, have_format=0;
    uint32_t offset=12, end=0;
    if (!f) return 0;
    if (!read_exact(f,12) || memcmp(block,"RIFF",4) || memcmp(block+8,"WAVE",4)) goto done;
    end=le32(block+4)+8;
    if (end<44 || end>300000) goto done;
    while (offset+8<=end) {
        mos_flseek(f,offset);
        if (!read_exact(f,8)) goto done;
        uint32_t size=le32(block+4);
        offset+=8;
        if (size>end-offset) goto done;
        if (!memcmp(block,"fmt ",4)) {
            if (have_format || size<16 || !read_exact(f,16)) goto done;
            uint32_t rate=le32(block+4);
            if (le16(block)!=1 || le16(block+2)!=1 || !rate || rate>65535 ||
                le32(block+8)!=rate || le16(block+12)!=1 || le16(block+14)!=8) goto done;
            sample_rate=(uint16_t)rate; have_format=1;
        } else if (!memcmp(block,"data",4)) {
            if (!have_format || !size) goto done;
            sample_bytes=size;
            vdp_adv_clear_buffer(SAMPLE_BUFFER);
            while (size) {
                unsigned n=size>sizeof(block)?sizeof(block):(unsigned)size;
                /* Read before emitting a buffer length: a short SD read cannot
                 * leave the VDP waiting for bytes that never arrive. */
                if (!read_exact(f,n)) goto done;
                vdp_adv_write_block_data(SAMPLE_BUFFER,n,(char *)block);
                size-=n;
            }
            ok=1; break;
        }
        offset+=size+(size&1);
    }
done:
    mos_fclose(f);
    if (!ok) { vdp_adv_clear_buffer(SAMPLE_BUFFER); return 0; }
    vdp_audio_reset_channel(0);
    vdp_audio_enable_channel(0);
    wait_ticks(6);
    vdp_adv_consolidate(SAMPLE_BUFFER);
    /* AgonDev's helper omits the optional rate, so emit the documented packet. */
    const uint8_t create[]={23,0,0x85,0,5,2,SAMPLE_BUFFER&255,SAMPLE_BUFFER>>8,
                            1|8,sample_rate&255,sample_rate>>8};
    audio_begin(); mos_puts((const char *)create,sizeof(create),0);
    if (!audio_ok()) return 0;
    audio_begin(); vdp_audio_set_sample(0,SAMPLE_BUFFER);
    if (!audio_ok()) return 0;
    audio_begin(); vdp_audio_play_sample(0,100);
    if (!audio_ok()) return 0;
    wait_ticks((sample_bytes*120+sample_rate-1)/sample_rate+60);
    vdp_audio_reset_channel(0);
    vdp_adv_clear_buffer(SAMPLE_BUFFER);
    return 1;
}

int main(void) {
    puts("Graphics suite attention requested. Preparing speech...");
    int audio=play_wav();
    puts(audio?"Speech playback completed.":"Speech playback failed: attention required.");
    const char *receipt=audio?"audio_commands=pass\r\n":"audio_commands=fail\r\n";
    uint8_t f=mos_fopen("/extender/gqt/voice.txt",FA_WRITE|FA_CREATE_ALWAYS);
    if(f) { mos_fwrite(f,(char *)receipt,strlen(receipt));mos_fclose(f); }
    /* Always permit the launch script to restore foreground SD service. */
    return 0;
}
