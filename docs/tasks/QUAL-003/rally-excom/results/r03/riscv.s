	.file	"cast.cpp"
	.option nopic
	.attribute arch, "rv32i2p1_m2p0_a2p1_f2p2_c2p0_zicsr2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	stock16
	.type	stock16, @function
stock16:
.LFB0:
	.cfi_startproc
	fcvt.wu.s a0,fa0,rtz
	slli	a0,a0,16
	srli	a0,a0,16
	ret
	.cfi_endproc
.LFE0:
	.size	stock16, .-stock16
	.align	1
	.globl	stock32
	.type	stock32, @function
stock32:
.LFB1:
	.cfi_startproc
	fcvt.wu.s a0,fa0,rtz
	ret
	.cfi_endproc
.LFE1:
	.size	stock32, .-stock32
	.align	1
	.globl	signed16_candidate
	.type	signed16_candidate, @function
signed16_candidate:
.LFB2:
	.cfi_startproc
	fcvt.w.s a0,fa0,rtz
	slli	a0,a0,16
	srli	a0,a0,16
	ret
	.cfi_endproc
.LFE2:
	.size	signed16_candidate, .-signed16_candidate
	.ident	"GCC: (crosstool-NG esp-14.2.0_20260121) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
