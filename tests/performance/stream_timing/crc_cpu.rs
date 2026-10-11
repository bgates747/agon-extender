//! Count instructions in the retained ROM's CRC leaf; never physical cycles/time.
//! ZDS stack ABI, fourteen control bytes, no GPIO or transport invocation.
use ez80::{Cpu, Machine, Reg16};
use std::{env, fs, path::Path};

struct Board { mem: Vec<u8> }
impl Machine for Board {
    fn peek(&self, a: u32) -> u8 { self.mem[a as usize] }
    fn poke(&mut self, a: u32, v: u8) { self.mem[a as usize] = v; }
    fn use_cycles(&self, _: i32) {}
    fn port_in(&mut self, a: u16) -> u8 { panic!("unexpected I/O {a:x}") }
    fn port_out(&mut self, a: u16, _: u8) { panic!("unexpected I/O {a:x}") }
}

fn main() {
    let args: Vec<_> = env::args().collect();
    assert_eq!(args.len(), 2, "supply exact EMOS artifact directory");
    let owner = Path::new(&args[1]);
    let rom = fs::read(owner.join("MOS.bin")).unwrap();
    let symbols = fs::read_to_string(owner.join("nm.txt")).unwrap();
    let pc = u32::from_str_radix(symbols.lines()
        .find(|s| s.ends_with(" _console_crc")).unwrap()
        .split_whitespace().next().unwrap(), 16).unwrap();
    for seed in [0u8, 19, 73, 255] {
        let mut b = Board { mem: vec![0; 0x1000000] };
        b.mem[..rom.len()].copy_from_slice(&rom);
        let (sp, exit, data) = (0xaff00, 0xa0000, 0xa1000);
        b._poke24(sp, exit); b._poke24(sp + 3, data);
        let mut expected = 65535u16;
        for i in 0u8..14 {
            let v = seed.wrapping_add(i.wrapping_mul(73));
            b.mem[data as usize + i as usize] = v;
            expected ^= (v as u16) << 8;
            for _ in 0..8 {
                expected = (expected << 1) ^
                    if expected & 0x8000 != 0 { 0x1021 } else { 0 };
            }
        }
        let mut cpu = Cpu::new_ez80();
        cpu.state.reg.adl = true; cpu.state.reg.madl = true;
        cpu.state.reg.pc = pc; cpu.state.reg.set24(Reg16::SP, sp);
        let mut instructions = 0;
        while cpu.state.reg.pc != exit {
            cpu.execute_instruction(&mut b); instructions += 1;
            assert!(instructions < 30000);
        }
        let actual = cpu.state.reg.get24(Reg16::HL) as u16;
        assert_eq!(actual, expected);
        assert_eq!(cpu.state.reg.get24(Reg16::SP), sp + 3);
        println!("seed={seed} crc={actual:04x} instructions={instructions}; instruction count only, not physical cycles/time");
    }
}
