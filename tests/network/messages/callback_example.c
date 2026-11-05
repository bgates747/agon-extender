/* Application-owned example: link net_callback.asm once. No direct vector
 * address or peripheral access. All callback work completes before ISR return.
 * Integrate the same classifier into an existing app callback instead if used. */
#include <agon/mos.h>
#include <agon/net.h>
static agon_net_client client;
void (*agon_net_callback_previous)(void);
extern void agon_net_callback(void);
unsigned agon_net_callback_packet(const uint8_t*p){
    if(!agon_net_is_reply(p))return 0; /* Router chains prior callback. */
    agon_net_receive(&client,p);return 1; /* Never publish NM as a key. */
}
unsigned net003_example_open(void){
    unsigned r=agon_net_begin(&client);if(r)return r;
    agon_net_callback_previous=(void(*)(void))agon_net_previous(&client);
    mos_setkbvector(agon_net_callback,0);
    /* CONNECT/SEND/poll are foreground calls after all initial asset uploads. */
    return 0;
}
unsigned net003_example_close(void){
    unsigned r=agon_net_release(&client); /* Disable NM delivery first. */
    mos_setkbvector(agon_net_callback_previous,0);return r;
}
