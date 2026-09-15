	.file	"cast.cpp"
	.text
	.align	4
	.global	stock16
	.type	stock16, @function
stock16:
.LFB0:
	entry	sp, 32
.LCFI0:
	wfr	f0, a2
	utrunc.s	a2, f0, 0
	extui	a2, a2, 0, 16
	retw.n
.LFE0:
	.size	stock16, .-stock16
	.align	4
	.global	stock32
	.type	stock32, @function
stock32:
.LFB1:
	entry	sp, 32
.LCFI1:
	wfr	f0, a2
	utrunc.s	a2, f0, 0
	retw.n
.LFE1:
	.size	stock32, .-stock32
	.align	4
	.global	signed16_candidate
	.type	signed16_candidate, @function
signed16_candidate:
.LFB2:
	entry	sp, 32
.LCFI2:
	wfr	f0, a2
	trunc.s	a2, f0, 0
	extui	a2, a2, 0, 16
	retw.n
.LFE2:
	.size	signed16_candidate, .-signed16_candidate
	.ident	"GCC: (crosstool-NG esp-12.2.0_20230208) 12.2.0"
