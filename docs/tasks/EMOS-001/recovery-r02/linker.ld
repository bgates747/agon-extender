ENTRY(entry)
SECTIONS {
  . = 0x0b0000;
  .text : { *(.text) }
  /DISCARD/ : { *(.comment) *(.note*) }
}
