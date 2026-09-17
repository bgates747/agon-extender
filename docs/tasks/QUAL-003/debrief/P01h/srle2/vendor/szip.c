/* szip.c                                                                   *
*                                                                           *
*  written by Michael Schindler michael@compressconsult.com                 *
*  1997,1998                                                                *
*  http://www.compressconsult.com/                                         */

static char vmayor=1, vminor=12;

#include <stdio.h>
#include <stdlib.h>
#ifndef unix
// #include <io.h>
#include <fcntl.h>
#endif
#include <string.h>
#include <ctype.h>
#include "szip.h"
#include <sys/stat.h>

#define BLOCK_SIZE (1 << SIZE_SHIFT)
#define COMPRESSION_TYPE_SZIP 'S'

static void usage()
{   fprintf(stderr,"szip %d.%d (c)1997-2000 Michael Schindler, szip@compressconsult.com\n",
        vmayor, vminor);
    fprintf(stderr,"homepage: http://www.compressconsult.com/szip/\n");
    fprintf(stderr,"usage: szip [options] [inputfile [outputfile]]\n");
    fprintf(stderr,"option           meaning              default   range\n");
    fprintf(stderr,"-d               decompress\n");
    fprintf(stderr,"-b<blocksize>    blocksize in 100kB   -b1      1-41\n"); // default block size to minimum for ESP32-friendly decompression
    fprintf(stderr,"-o<order>        order of context     -o6       0, 3-255\n");
    fprintf(stderr,"-r<recordsize>   recordsize           -r1       1-127\n");
    fprintf(stderr,"-i               incremental          -i\n");
    fprintf(stderr,"-v<level>        verbositylevel       -v0       0-255\n");
    fprintf(stderr,"options may be combined into one, like -r3i\n");
    exit(1);
}

static int readnum(char **s, int min, int max)
{	int j=0;
	while (isdigit(**s))
	{	j=10*j+**s-'0';
		*s += 1;
	}
	if (j<min || j>max)
		usage();
	return j;
}

/* parameter values */
// uint4 blocksize=1703936;
uint4 blocksize = 32768; // 32 KB = 0x8000, ESP32-friendly default
uint order=6, verbosity=0, compress=1;
unsigned char recordsize=1;

static void no_szip()
{   fprintf(stderr, "probably not an szip file; could be szip version prior to 1.10\n");
    exit(1);
}

static void writeglobalheader(uint4 orig_size) 
{   /* Write Agon compression header prefix: "Cmp" and COMPRESSION_TYPE_SZIP */
    putchar('C');
    putchar('m');
    putchar('p');
    putchar(COMPRESSION_TYPE_SZIP);
    /* Write original file size (4 bytes, little-endian order) */
    putchar(orig_size & 0xFF);
    putchar((orig_size >> 8) & 0xFF);
    putchar((orig_size >> 16) & 0xFF);
    putchar((orig_size >> 24) & 0xFF);
    /* write SZIP magic SZ\012\004 and version numbers */
    putchar(0x53); // S
    putchar(0x5a); // Z
    putchar(0x0a); // \n
    putchar(0x04); // \004
    putchar(vmayor); /* version mayor of first version using the format */
    putchar(vminor); /* version minor of first version using the format */
}

static void readglobalheader()
{   /* Verify the Agon compression header prefix */
    if (getchar() != 'C') no_szip();
    if (getchar() != 'm') no_szip();
    if (getchar() != 'p') no_szip();
    if (getchar() != COMPRESSION_TYPE_SZIP) no_szip();
    /* Read the original file size (4 bytes, little-endian order).
       We could store this value if needed; for now we just read and ignore it. */
    uint4 orig_size = 0;
    orig_size |= (uint4)(unsigned char)getchar();
    orig_size |= (uint4)(unsigned char)getchar() << 8;
    orig_size |= (uint4)(unsigned char)getchar() << 16;
    orig_size |= (uint4)(unsigned char)getchar() << 24;

    /* Verify the SZIP magic SZ\012\004 and version numbers */
    int ch, vmay;
    ch = getchar();
    if (ch == EOF) return;
    if (ch == 0x42) {ungetc(ch, stdin); return;} /* maybe blockheader */
    if (ch != 0x53) no_szip();
    if (getchar() != 0x5a) no_szip();
    if (getchar() != 0x0a) no_szip();
    if (getchar() != 0x04) no_szip();
    vmay = getchar();
    if (vmay == EOF || vmay==0) no_szip();
    ch = getchar();
    if (ch == EOF) no_szip();
    if (vmay>vmayor || (vmay==vmayor && ch>vminor))
    {   fprintf(stderr, "This file is szip version %d.%d, this program is %d.%d.\n Please update\n",
        vmay, ch, vmayor, vminor);
        exit(1);
    }
    if (vmay==1 && ch==10)
    {   fprintf(stderr, "This file is szip version 1.10ALPHAi");
        fprintf(stderr, "A decoder is available at the website http://www.compressconsult.com");
        exit(1);
    }
}


static void writeuint3(uint4 x)
{   putchar((char)((x>>16)&0xff));
    putchar((char)((x>>8)&0xff));
    putchar((char)(x&0xff));
}


static uint4 readuint3()
{   uint4 x;
    x = getchar();
    x = x<<8 | getchar();
    x = x<<8 | getchar();
    return x;
}


static uint writeblockdir(uint4 buflen)
{   /* write magic */
    putchar(0x42);
    putchar(0x48);
    writeuint3(buflen);
    putchar(0);   /* FIXME: empty filename to indicate end of dir */
    return 6;
}


static uint readblockdir(uint4 *buflen)
{   int ch;
    ch = getchar();
    if (ch == EOF) {*buflen = 0; return 0;}
    if (ch == 0x53)
    {   ungetc(ch, stdin);
        readglobalheader();
        ch=getchar();
        if (ch == EOF) {*buflen = 0; return 0;}
    }
    if (ch != 0x42) no_szip();
    if (getchar() != 0x48) no_szip();
    *buflen = readuint3();
    if (getchar() != 0) no_szip();  /* FIXME: read until empty filename */
    return 6;
} 


static void writestorblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   unsigned char *end;
    if (verbosity&1) fprintf( stderr, "Storing %d bytes ...", buflen);
    putchar(0); /* 0 means stored block */
    end = buffer + buflen;
    while (buffer<end)
    {   putchar(*buffer);
        buffer++;
    }
    writeuint3(dirsize+4+buflen);
}


static void readstorblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   if (verbosity&1) fprintf( stderr, "Reading %d bytes ...", buflen);
    if (fread(buffer,1,buflen,stdin) != buflen)
    {   fprintf(stderr,"Error reading input\n"); exit(1);}
    if (fwrite(buffer,1,buflen,stdout) != buflen)
    {   fprintf(stderr,"Error writing output\n"); exit(1);}
    if (readuint3() != dirsize+3+buflen) no_szip();
}

   
static void writeszipblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   uint4 indexlast;
#ifndef MODELGLOBAL
    sz_model m;
#endif
    if (verbosity&1) fprintf( stderr, "Processing %d bytes ...", buflen);
    putchar(1); /* 1 means szip block */
    if ((recordsize&0x7f) != 1)
    {	unsigned char *tmp;
		tmp = (unsigned char*) malloc(buflen+order);
		if (tmp==NULL)
		{	fprintf(stderr, "memory allocation error\n");
			exit(1);
		}
		reorder(buffer,tmp,buflen,recordsize&0x7f);
        memcpy(buffer,tmp,buflen);
		free(tmp);
	}

    if (recordsize &0x80)
	{	unsigned char tmp = *buffer;
        uint4 i;
		for (i=1; i<buflen; i++)
		{	unsigned char tmp1 = buffer[i];
			buffer[i] = (0x100 + tmp1 - tmp) & 0xff;
			tmp = tmp1;
		}
	}

    if (order==4)
		sz_srt_o4(buffer,buflen,&indexlast);
	else if (order==0)
		sz_srt_BW(buffer,buflen,&indexlast);
	else
		sz_srt(buffer,buflen,&indexlast,order);

    if (verbosity&1) fprintf(stderr," coding ...");

    writeuint3(indexlast);
    putchar((char)(order&0xff));

    initmodel(&m, dirsize+5, &recordsize);
    /* FIXME: write recordsize with putchar with planned output */

  { unsigned char *end;
    end = buffer+buflen;
    *end = ~*(end-1); /* to make sure we end a run at end */
   {unsigned char ch, *begin;
    begin = buffer;
    ch = *(buffer++);
    while (*buffer==ch)
       buffer++;
    sz_encode(&m, ch, (uint4)(buffer-begin));
   }
    fixafterfirst(&m);
    while (buffer<end)
    {   unsigned char ch, *begin;
        begin = buffer;
        ch = *(buffer++);
        while (*buffer==ch)
            buffer++;
        sz_encode(&m, ch, (uint4)(buffer-begin));
    }
  }

    // #ifndef MODELGLOBAL
    //     FILE *model_file = fopen("0szip_model.bin", "wb");
    //     fwrite(&m, sizeof(sz_model), 1, model_file);
    //     fclose(model_file);
    // #else
    //     fwrite(m, sizeof(sz_model), 1, model_file);
    // #endif // MODELGLOBAL

    deletemodel(&m);
}


static void readszipblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   unsigned char *tmp;
    uint4 indexlast, charcount[256], bytesleft;
#ifndef MODELGLOBAL
    sz_model m;
#endif
    if (verbosity&1) fprintf( stderr, "Decoding %d bytes ", buflen);
    indexlast = readuint3();
    order = getchar();

	memset(charcount, 0, 256*sizeof(uint4));
    initmodel(&m, -1, &recordsize);

    if (verbosity&1)
    {   if (order != 6)
            fprintf( stderr, "-o%d ",order);
        if ((recordsize & 0x7f) != 1)
            fprintf( stderr, "-r%d ",recordsize&0x7f);
        if (recordsize & 0x80)
            fprintf( stderr, "-i ");
        fprintf( stderr, "...");
    }

    tmp = buffer;
    bytesleft = buflen;
    {   uint4 runlength;
        uint ch;
        sz_decode(&m, &ch, &runlength);
        if (runlength>bytesleft)
        {	fprintf(stderr, "input file corrupt");
			exit(1);
		}
        bytesleft -= runlength;
        charcount[ch] += runlength;
        while (runlength)
        {   *(tmp++) = ch;
            runlength--;
        }
    }
    fixafterfirst(&m);
    while (bytesleft)
    {   uint4 runlength;
        uint ch;
        sz_decode(&m, &ch, &runlength);
        if (runlength>bytesleft)
        {	fprintf(stderr, "input file corrupt");
			exit(1);
		}
        bytesleft -= runlength;
        charcount[ch] += runlength;
        while (runlength)
        {   *(tmp++) = ch;
            runlength--;
        }
    }
    deletemodel(&m);

    if (verbosity&1) fprintf( stderr, " processing ...");

	if (recordsize == 1)
	{	if (order==0)
			sz_unsrt_BW(buffer, NULL, buflen, indexlast, charcount);
		else
			sz_unsrt(buffer, NULL, buflen, indexlast, charcount, order);
//fwrite(buffer,1,buflen,stdout);
    }
	else
	{	tmp = (unsigned char*) malloc(buflen);
		if (tmp==NULL)
		{	fprintf(stderr, "memory allocation failure");
			exit(1);
		}
		if (order==0)
			sz_unsrt_BW(buffer, tmp, buflen, indexlast, charcount);
		else
			sz_unsrt(buffer, tmp, buflen, indexlast, charcount, order);
		if (recordsize & 0x80)
		{	uint4 i;
            unsigned char c = *tmp;
			for (i=1; i<buflen; i++)
			{	c = (c+tmp[i])&0xff;
				tmp[i] = c;
			}
		}
		unreorder(tmp,buffer,buflen,recordsize&0x7f);
		free(tmp);

        bytesleft = fwrite(buffer,1,buflen,stdout);
        if (bytesleft != buflen)
		{	fprintf(stderr, "error writing output");
			exit(1);
		}
    }
}


static void compressit()
{   unsigned char *inoutbuffer;

    inoutbuffer = (unsigned char*) malloc(blocksize+order+1);
	if (inoutbuffer==NULL)
	{	fprintf(stderr, "memory allocation error\n");
		exit(1);
	}

    /* Attempt to get the original file size from stdin */
    uint4 orig_size = 0;
    struct stat st;
    if (fstat(fileno(stdin), &st) == 0) {
        orig_size = (uint4) st.st_size;
        /* If stdin is a regular file, rewind to the beginning */
        if (S_ISREG(st.st_mode)) {
            rewind(stdin);
        }
    } else {
        fprintf(stderr, "Warning: unable to determine file size; using 0\n");
    }

    writeglobalheader(orig_size);

    while (1)
    {   uint4 buflen;
        uint i;
        buflen = fread( (char *)inoutbuffer, 1, (size_t)blocksize, stdin);
        if (buflen == 0) break;

        i = writeblockdir(buflen);

        if (buflen<=order || buflen<=5)
            writestorblock(i, buflen, inoutbuffer);
        else
            writeszipblock(i, buflen, inoutbuffer);

		if (verbosity&1) fprintf(stderr," done\n");
	}
    free(inoutbuffer);
}


static void decompressit()
{   unsigned char *inoutbuffer=NULL;

    blocksize = 0;
    readglobalheader();

    while (1)
    {   uint4 blocklen;
        uint dirsize;
        int ch;
        dirsize = readblockdir(&blocklen);
        if (dirsize==0) break;
        if (blocklen>blocksize)
        {   if (inoutbuffer != NULL)
                free(inoutbuffer);
            inoutbuffer = (unsigned char *) malloc(blocklen);
            blocksize = blocklen;
        	if (inoutbuffer==NULL)
        	{	fprintf(stderr, "memory allocation error\n");
        		exit(1);
	        }
        }
        ch = getchar();
        if (ch==0)
            readstorblock(dirsize+1, blocklen, inoutbuffer);
        else if (ch==1)
            readszipblock(dirsize+1, blocklen, inoutbuffer);
        else
            no_szip();
		if (verbosity&1) fprintf(stderr," done\n");
	}
    free(inoutbuffer);
}


int main( int argc, char *argv[] )
{	char *infilename=NULL, *outfilename=NULL;
    uint i;

    for (i=1; i<(unsigned)argc; i++)
	{	char *s=argv[i];
	    if (*s == '-')
		{	s++;
			while (*s)
				switch (*(s++))
				{	
                    case 'o': {
                        order = readnum(&s, 0, 255);
                        if (order == 1 || order == 2) {
                            usage();
                        }
                        break;
                    }                    
					case 'r': {recordsize = (recordsize & 0x80) | 
								  readnum(&s,1,255); break;}
					// case 'b': {blocksize = (100000*readnum(&s,1,41)+0x7fff) & 0x7fff8000L; break;}
                    case 'b': { // modification for ESP32-friendly block size
                        uint custom_size = readnum(&s, 1, 41) * 100000; // User-specified size in 100 KB units
                        if (custom_size < 32768) { // Ensure blocksize never goes below 32 KB
                            custom_size = 32768;
                        }
                        blocksize = (custom_size + 0x7fff) & 0x7FFF8000L; // Align to 32 KB boundary
                        break;
                    } // end modification for ESP32-friendly block size
					case 'i': {recordsize |= 0x80; break;}
                    case 'v': {verbosity = readnum(&s,0,255); break;}
                    case 'd': {compress = 0; break;}
					default: usage();
				}
		} else if (infilename == NULL)
			infilename = s;
		else if (outfilename == NULL)
			outfilename = s;
		else
			usage();
	}

	if (verbosity) fprintf( stderr, "szip Version %d.%d on ", vmayor, vminor);

    if (infilename == NULL) {
        if (verbosity) fprintf(stderr, "stdin");
    } else {
        if (!freopen(infilename, "rb", stdin)) {
            fprintf(stderr, "Error opening input file: %s\n", infilename);
            exit(1);
        }
        if (verbosity) fprintf(stderr, "%s", infilename);
    }
    
    if (outfilename == NULL) {
        if (verbosity) fprintf(stderr, " to stdout\n");
    } else {
        if (!freopen(outfilename, "wb", stdout)) {
            fprintf(stderr, "Error opening output file: %s\n", outfilename);
            exit(1);
        }
        if (verbosity) fprintf(stderr, " to %s\n", outfilename);
    }    

#ifndef unix
    setmode( fileno( stdin ), O_BINARY );
    setmode( fileno( stdout ), O_BINARY );
#endif

    if (compress) {
        compressit();
    } else {
        decompressit();
    }

    return 0;
}
