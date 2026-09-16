// Private diagnostic opcode; not a supported VDP API extension.
case 0xEE: {
  int lo=readByte(), hi=readByte();
  if (lo<0 || hi<0) break;
  unsigned token=unsigned(lo)|(unsigned(hi)<<8);
  waitPlotCompletion();
  int w=_VGAController->getViewPortWidth(), h=_VGAController->getViewPortHeight();
  DBGSerial.printf("\nQ4BEGIN %u %d %d\n",token,w,h);
  bool ok=w>0 && w<=1024 && h>0 && h<=1024;
  for(int y=0;ok && y<h;++y) {
    qual004::ready_width=0;
    __sync_synchronize();
    qual004::requested_row=y;
    uint32_t start=millis();
    while(qual004::requested_row>=0 && millis()-start<1000) delay(1);
    if(qual004::requested_row>=0 || qual004::ready_width!=w) {ok=false;break;}
    uint32_t hash=2166136261UL;
    // Native I2S word byte order; output canonical BBGGRR in increasing x.
    uint8_t packed[1024];
    for(int x=0;x<w;++x) {packed[x]=qual004::row[x^2]&63;hash=(hash^packed[x])*16777619UL;}
    DBGSerial.printf("Q4ROW %u %d %d %08lx\n",token,y,w,(unsigned long)hash);
    DBGSerial.write(packed,w);DBGSerial.write('\n');
  }
  qual004::requested_row=-1;
  DBGSerial.printf("Q4END %u %d\n",token,int(ok));
  DBGSerial.flush();
  break;
}
