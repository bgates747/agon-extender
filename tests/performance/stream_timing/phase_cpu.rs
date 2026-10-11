//! Execute the actual diagnostic ROM gate and RAM recorder; no hardware timing.
use ez80::{Cpu,Machine,Reg16};
use std::{collections::HashMap,env,fs,path::Path};
const SP:u32=0xaff00;const EXIT:u32=0xa0000;
struct Board{mem:Vec<u8>,reads:Vec<u16>,iff:bool,raw:u16}
impl Machine for Board{
 fn peek(&self,a:u32)->u8{self.mem[a as usize]}
 fn poke(&mut self,a:u32,v:u8){self.mem[a as usize]=v;}
 fn use_cycles(&self,_:i32){}
 fn port_in(&mut self,a:u16)->u8{
  assert!(!self.iff,"recorder latch/append must be atomic");
  assert_eq!(a,if self.reads.len()%2==0{0x84}else{0x85});self.reads.push(a);
  if a==0x84{self.raw as u8}else{(self.raw>>8)as u8}
 }
 fn port_out(&mut self,a:u16,_:u8){panic!("recorder must not write I/O {a:x}")}
}
fn symbols(p:&Path)->HashMap<String,u32>{fs::read_to_string(p).unwrap().lines().filter_map(|l|{
 let v:Vec<_>=l.split_whitespace().collect();if v.len()!=3{None}else{Some((v[2].into(),u32::from_str_radix(v[0],16).unwrap()))}
}).collect()}
fn main(){
 let a:Vec<_>=env::args().collect();assert_eq!(a.len(),3);
 let owner=Path::new(&a[1]);let fixture=Path::new(&a[2]);let s=symbols(&owner.join("nm.txt"));let f=symbols(&fixture.join("nm.txt"));
 let rom=fs::read(owner.join("MOS.bin")).unwrap();let app=fs::read(fixture.join("bin/stream.bin")).unwrap();
 let mut b=Board{mem:vec![0xa5;0x100000],reads:vec![],iff:false,raw:0x1234};
 b.mem[..rom.len()].copy_from_slice(&rom);b.mem[0xb0000..0xb0000+app.len()].copy_from_slice(&app);
 let mut cases=0;let mut max_masked=0;
 for iff in [false,true]{for armed in [false,true]{for count in [0,511,512]{for flags in 0..256{
  b.reads.clear();b.raw=if flags==0{0}else{0x1234};
  b.poke(s["_emos_phase_armed"],if armed{1}else{0});b._poke24(f["_phase_count"],count);
  b.poke(f["_phase_overflow"],0);b._poke24(s["_offer"]+10,0x010123);
  let base=f["_phase_records"] as usize;b.mem[base..base+4100].fill(0xa5);
  let mut c=Cpu::new_ez80();c.state.reg.adl=true;c.state.reg.madl=true;
  c.state.reg.iff1=iff;c.state.reg.iff2=iff;c.state.reg.pc=s["_emos_phase_reserve_begin"];
  c.state.reg.set24(Reg16::SP,SP);b._poke24(SP,EXIT);
  let regs=[(Reg16::BC,0x234567),(Reg16::DE,0x345678),(Reg16::HL,0x456789),(Reg16::IX,0x123456),(Reg16::IY,0x654321)];
  for (r,v) in regs{c.state.reg.set24(r,v);}
  c.state.reg.set16(Reg16::AF,0x5a00|flags);
  let mut steps=0;let mut masked=0;
  while c.state.reg.pc!=EXIT{
   b.iff=c.state.reg.iff1;if !b.iff{masked+=1;}c.execute_instruction(&mut b);steps+=1;assert!(steps<150);
  }
  max_masked=max_masked.max(masked);
  for(r,v)in regs{assert_eq!(c.state.reg.get24(r),v);}
  assert_eq!(c.state.reg.get16(Reg16::AF),0x5a00|flags);
  assert_eq!(c.state.reg.get24(Reg16::SP),SP+3);assert_eq!(c.state.reg.iff1,iff);assert_eq!(c.state.reg.iff2,iff);
  assert_eq!(b.reads.len(),if armed{2}else{0});
  assert_eq!(b._peek24(f["_phase_count"]),count+if armed&&count<512{1}else{0});
  assert_eq!(b.peek(f["_phase_overflow"]),if armed&&count==512{1}else{0});
  if armed&&count<512{
   let offset=count as usize*8;
   let expected=[0,0,10,b.raw as u8,(b.raw>>8)as u8,0x23,1,1];
   assert_eq!(&b.mem[base+offset..base+offset+8],&expected);
   assert!(b.mem[base..base+offset].iter().all(|v|*v==0xa5));
   assert!(b.mem[base+offset+8..base+4100].iter().all(|v|*v==0xa5));
  }else{assert!(b.mem[base..base+4100].iter().all(|v|*v==0xa5));}
  assert_eq!(b.peek(s["_emos_phase_armed"]),if armed&&count<512{1}else{0});cases+=1;
 }}}}
 println!("PASS {cases} actual ROM/RAM probe cases: all AF flags, registers/SP/IFF, disabled no-read, low/high latch, saturation raw, append/overflow/disarm, storage guards; max masked path {max_masked} instructions, not physical time");
}
