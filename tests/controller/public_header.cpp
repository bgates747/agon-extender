// Standalone public include with a foreground transport model. No Agon SDK,
// low-address mapping, P4 runtime, hardware or application callback is needed.
#include <agon/controller.hpp>
#include <cassert>
#include <cstring>
#include <limits>
using namespace agon::controller;
struct Model {
    uint32_t ticks=0,token=0,ack=0,send_error=0,open_error=0,close_error=0;
    uint32_t request_ticks=0,wire_close_ticks=0;
    uint16_t query=0;
    unsigned sends=0,opens=0,closes=0,wire_closes=0;
    unsigned receive_length=TransportResultSize,open_length=4;
    bool admitted=false,waiting=false,ready=false,available=true;
    uint8_t reply[TransportResultSize]{};
    void sample(uint32_t source=100,uint16_t age=0,uint8_t rtt=0,uint8_t cache=0){
        memset(reply,0,sizeof(reply));memcpy(reply,CONTROLLER_RESULT_MAGIC,4);
        controller_put32(reply+4,token);controller_put16(reply+8,query);
        reply[10]=3;controller_put32(reply+12,1);controller_put32(reply+20,source);
        controller_put32(reply+28,1);controller_put16(reply+32,age);
        controller_put16(reply+36,32767);reply[44]=255;
        reply[96]=rtt;reply[97]=cache;ready=true;waiting=false;
    }
    void edge(unsigned index,uint32_t id,uint8_t control,uint8_t down){
        assert(index<8);reply[11]=index+1;auto*p=reply+48+index*6;
        controller_put32(p,id);p[4]=control;p[5]=down;
    }
};
struct Binding {
    Model*m;
    bool available(){return m->available;}
    uint32_t clock(){return m->ticks;}
    uint32_t exchange(uint8_t*in,unsigned length,uint8_t*out,unsigned cap,unsigned&received){
        received=0;
        if(in[0]==Open){
            assert(length==1&&cap==4);++m->opens;
            if(m->open_error)return m->open_error;
            if(m->admitted)return Busy;
            m->admitted=true;controller_put32(out,++m->token);received=m->open_length;
            return Ok;
        }
        if(in[0]==Close){
            assert(length==1&&!cap);++m->closes;m->admitted=m->waiting=m->ready=false;
            return m->close_error;
        }
        if(!m->admitted)return Unavailable;
        if(in[0]==Receive){
            assert(length==1&&cap==TransportResultSize);
            if(!m->ready)return Busy;
            memcpy(out,m->reply,TransportResultSize);received=m->receive_length;m->ready=false;
            return Ok;
        }
        assert(in[0]==Send&&length==20&&!cap);
        assert(in[1]==23&&!in[2]&&in[3]==0xf7);
        const auto*p=in+4;
        assert(p[0]=='C'&&p[1]=='I'&&p[2]==2&&controller_u32(p+4)==m->token);
        assert(!p[14]&&!p[15]);
        if(p[3]==1&&(m->waiting||m->ready))return Busy;
        if(m->send_error)return m->send_error;
        assert(controller_u16(p+12)>m->query||controller_u16(p+12)==1);
        m->query=controller_u16(p+12);m->ack=controller_u32(p+8);
        if(p[3]==2){++m->wire_closes;m->waiting=m->ready=false;m->ticks+=m->wire_close_ticks;}
        else{assert(p[3]==1);++m->sends;m->waiting=true;m->ticks+=m->request_ticks;}
        return Ok;
    }
};
using Controller=Client<Binding>;
static void taps_and_full_validation(){
    Model m;Controller c{Binding{&m}};
    assert(c.open()&&c.update());m.sample();m.edge(0,1,0,1);m.edge(1,2,0,0);
    assert(c.update());assert(c.state().valid&&c.state().presses[0]==1&&m.ack==2);
    assert(c.state().stick8(Axis::LeftX)==255&&c.state().trigger[0]==255);
    assert(!c.state().down(Control::A));
    m.sample();m.edge(0,1,0,1);m.edge(1,2,0,0);assert(c.update());
    assert(c.state().presses[0]==1&&m.ack==2);
    // A valid first transition followed by malformed content must not commit
    // a press, source generation or ACK for the valid prefix.
    const auto generation=c.state().generation;
    m.sample(200);m.edge(0,1,5,1);m.edge(1,2,15,0);
    const auto sends=m.sends;assert(!c.update()&&c.error==Invalid);
    assert(c.state().presses[0]==1&&!c.state().presses[5]);
    assert(c.state().generation==generation&&m.ack==2&&m.sends==sends);
    assert(!c.state().valid&&!c.state().connected&&!c.state().held);
    assert(!c.update()&&m.sends==sends); // No automatic recovery.
    assert(c.close()&&m.closes==1&&!m.wire_closes);
    assert(c.open()&&c.update());m.sample(200);m.edge(0,1,5,1);assert(c.update());
    assert(!c.state().presses[0]&&c.state().presses[5]==1&&m.ack==1);
    assert(c.close());
}
static void source_change(){
    Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
    m.sample();m.edge(0,7,0,1);assert(c.update());const auto generation=c.state().generation;
    assert(m.ack==7&&c.state().presses[0]==1);
    m.sample(200);m.edge(0,1,5,1);assert(c.update());
    assert(c.state().generation==generation+1&&!c.state().presses[0]);
    assert(c.state().presses[5]==1&&m.ack==1);assert(c.close());
}
static void freshness_and_clock_wrap(){
    Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
    m.ticks=std::numeric_limits<uint32_t>::max()-3;
    m.sample(100,100,2,2);m.edge(0,1,0,1);assert(c.update());
    assert(c.state().age_ms==172&&c.state().valid&&m.ack==1);
    m.ticks+=9;assert(c.update());
    assert(c.state().age_ms==253&&!c.state().valid&&c.state().connected);
    assert(!c.state().stick[0]&&!c.state().trigger[0]&&c.state().presses[0]==1);
    m.sample(100,214);m.edge(0,2,1,1);assert(c.update());
    assert(c.state().age_ms==250&&!c.state().valid&&m.ack==1&&!c.state().presses[1]);
    assert(c.close());
}
static void blocking_send_freshness(){
    {
        Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
        m.sample();m.edge(0,1,0,1);m.request_ticks=24;
        // The decoded sample starts at36 nominal ms. A successful refresh
        // SEND can then wait24 clock units, making it252 before update returns.
        assert(c.update()&&c.error==Ok);
        assert(c.state().age_ms==252&&!c.state().valid&&c.state().connected);
        assert(!c.state().held&&!c.state().stick[0]&&!c.state().trigger[0]);
        assert(c.state().presses[0]==1&&m.ack==1&&c.state().generation==1);
        assert(c.close());
    }
    {
        Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
        for(uint32_t id=1;id<65000;++id){
            m.sample();m.edge(0,id,0,1);assert(c.update());
        }
        m.sample();m.edge(0,65000,0,1);m.wire_close_ticks=24;
        // Healthy query renewal preserves source/counts, but its best-effort
        // wire CLOSE can consume the same freshness budget as a normal SEND.
        assert(c.update()&&c.error==Ok&&m.opens==2&&m.wire_closes==1);
        assert(c.state().age_ms==252&&!c.state().valid&&c.state().connected);
        assert(!c.state().held&&!c.state().stick[0]&&!c.state().trigger[0]);
        assert(c.state().presses[0]==65000&&m.ack==65000&&c.state().generation==1);
        assert(c.close());
    }
}
static void malformed(){
    for(unsigned defect=0;defect<13;++defect){
        Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
        m.sample();m.edge(0,1,0,1);m.edge(1,2,0,0);
        switch(defect){
            case 0:m.reply[0]='X';break;
            case 1:m.reply[10]=2;break;
            case 2:m.reply[11]=9;break;
            case 3:controller_put16(m.reply+34,0x1800);break;
            case 4:controller_put16(m.reply+34,0x8000);break;
            case 5:m.reply[46]=1;break;
            case 6:m.reply[59]=2;break;
            case 7:controller_put32(m.reply+54,3);break;
            case 8:controller_put32(m.reply+48,0);break;
            case 9:m.reply[60]=1;break;
            case 10:m.reply[96]=30;break;
            case 11:m.reply[10]=1;break;
            case 12:m.receive_length=97;break;
        }
        assert(!c.update()&&c.error==Invalid&&m.ack==0&&m.sends==1);
        assert(!c.state().valid&&!c.state().presses[0]);assert(c.close());
    }
}
static void failure_cleanup_and_old_service(){
    {Model m;m.available=false;Controller c{Binding{&m}};
     assert(!c.open()&&c.error==Unavailable&&!m.opens);}
    {Model m;m.open_error=Invalid;Controller c{Binding{&m}};
     assert(!c.open()&&c.error==Invalid&&!m.closes);}
    {Model m;m.admitted=true;Controller c{Binding{&m}};
     assert(!c.open()&&c.error==Busy&&!m.closes&&m.admitted);}
    {Model m;m.open_length=3;Controller c{Binding{&m}};
     assert(!c.open()&&c.error==Invalid&&m.closes==1&&!m.admitted);}
    {Model m;Controller c{Binding{&m}};assert(c.open()&&c.update());
     m.send_error=15;assert(!c.close()&&c.error==15&&m.closes==1&&!m.admitted);}
    {Model m;Controller c{Binding{&m}};assert(c.open());m.send_error=15;
     assert(!c.update()&&c.error==15);assert(c.close()&&m.closes==1);}
}
static void healthy_renewal_and_saturation(){
    Model m;Controller c{Binding{&m}};assert(c.open());
    for(uint32_t id=1;id<=65538;++id){
        assert(c.update());m.sample();m.edge(0,id,0,1);assert(c.update());
    }
    assert(m.opens==2&&m.wire_closes==1&&c.state().presses[0]==65535);
    assert(c.state().valid&&c.state().generation==1);
    assert(c.close()&&m.closes==2);
}
int main(){
    assert(axis8(-32768)==0&&axis8(0)==128&&axis8(32767)==255);
    taps_and_full_validation();source_change();freshness_and_clock_wrap();blocking_send_freshness();
    malformed();failure_cleanup_and_old_service();healthy_renewal_and_saturation();
}
