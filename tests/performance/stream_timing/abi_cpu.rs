//! Actual MOSlet-to-ZDS ABI bridge: compile/link checks, not physical timing.
use ez80::{Cpu,Machine,Reg16};
use std::{collections::HashMap,env,fs,path::Path};
const SP:u32=0xaff00;const EXIT:u32=0xa0000;
struct Board{mem:Vec<u8>}
impl Machine for Board{
 fn peek(&self,a:u32)->u8{self.mem[a as usize]}
 fn poke(&mut self,a:u32,v:u8){self.mem[a as usize]=v;}
 fn use_cycles(&self,_:i32){}
 fn port_in(&mut self,a:u16)->u8{panic!("unexpected empty-drain input {a:x}")}
 fn port_out(&mut self,a:u16,_:u8){panic!("unexpected empty-drain output {a:x}")}
}
fn symbols(p:&Path)->HashMap<String,u32>{fs::read_to_string(p).unwrap().lines().filter_map(|l|{
 let v:Vec<_>=l.split_whitespace().collect();if v.len()!=3{None}else{Some((v[2].into(),u32::from_str_radix(v[0],16).unwrap()))}
}).collect()}
fn run(b:&mut Board,pc:u32,iff:bool)->u32{
 let mut c=Cpu::new_ez80();c.state.reg.adl=true;c.state.reg.madl=true;
 c.state.reg.iff1=iff;c.state.reg.iff2=iff;c.state.reg.pc=pc;
 c.state.reg.set24(Reg16::SP,SP);b._poke24(SP,EXIT);
 c.state.reg.set24(Reg16::IX,0x123456);c.state.reg.set24(Reg16::IY,0x654321);
 let mut n=0;while c.state.reg.pc!=EXIT{c.execute_instruction(b);n+=1;assert!(n<10000);}
 assert_eq!(c.state.reg.get24(Reg16::SP),SP+3);
 assert_eq!(c.state.reg.get24(Reg16::IX),0x123456);assert_eq!(c.state.reg.get24(Reg16::IY),0x654321);
 assert_eq!(c.state.reg.iff1,iff);assert_eq!(c.state.reg.iff2,iff);
 c.state.reg.get24(Reg16::HL)
}
fn main(){
 let a:Vec<_>=env::args().collect();assert_eq!(a.len(),3);
 let owner=Path::new(&a[1]);let fixture=Path::new(&a[2]);let s=symbols(&owner.join("nm.txt"));let f=symbols(&fixture.join("nm.txt"));
 let rom=fs::read(owner.join("MOS.bin")).unwrap();let app=fs::read(fixture.join("bin/stream.bin")).unwrap();
 let mut b=Board{mem:vec![0;0x1000000]};b.mem[..rom.len()].copy_from_slice(&rom);b.mem[0xb0000..0xb0000+app.len()].copy_from_slice(&app);
 for kind in 0..5{
  b.poke(s["_emos_exext_owned"],if kind==1{0}else{1});b.poke(s["_emosVduBackend"],if kind==2{1}else{2});b.poke(s["_emos_exext_busy"],if kind==3{1}else{0});
  let result=run(&mut b,f["_st_flush"],kind!=4);
  assert_eq!(result,if kind==0{0}else{0xe2});
  assert_eq!(b.peek(s["_queued"]),0);assert_eq!(b.peek(s["_queued"]+1),0);
 }
 if s.contains_key("_emos_stream_timing_last_raw") {
 for raw in [0u16,1,0x1234,65534,65535]{
  b.poke(s["_emos_stream_timing_last_raw"],raw as u8);b.poke(s["_emos_stream_timing_last_raw"]+1,(raw>>8)as u8);
  assert_eq!(run(&mut b,f["_st_wire_read"],true),65535-u32::from(raw));
 }
 }
 println!("PASS actual MOSlet/ZDS ABI: empty drain, four refusals, raw timer values when present, HL status, IX/IY/SP/IFF; no physical timing");
}
