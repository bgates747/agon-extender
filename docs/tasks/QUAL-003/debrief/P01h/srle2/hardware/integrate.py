"""Add qualified browser decoder and bounded P4 probes to an isolated SRLE2 build."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--decoder',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;v=a.candidate/'source/vdp';web=v/'video/extender/web';codec=v/'video/extender/diagnostics/srle2'
shutil.copy2(root/'codec_probe.hpp',codec/'codec_probe.hpp')
staged=a.candidate/'web-staged'
subprocess.run([sys.executable,str(root.parent/'web/prepare_client.py'),str(web),str(a.decoder),str(staged)],check=True)
for f in staged.iterdir():
 if f.is_file():shutil.copy2(f,web/f.name)
extras=[('decoder.js','text/javascript; charset=utf-8',False),('decoder-worker.js','text/javascript; charset=utf-8',False),('web_decode.js','text/javascript; charset=utf-8',False),('szip.js','text/javascript; charset=utf-8',False),('szip.wasm','application/wasm',True),('COPYING.GPL-2','text/plain; charset=utf-8',False),('codec-source.json','application/json',False)]
f=v/'pio/p4-console-source-selection.json';selection=json.loads(f.read_text())
for name,_,binary in extras:selection.setdefault('embedded_binary_files' if binary else 'embedded_text_files',[]).append('video/extender/web/'+name)
f.write_text(json.dumps(selection,indent=2)+'\n')
f=v/'pio/select_sources.py';s=f.read_text();needle='\ncmake_text += ")\\n"';assert s.count(needle)==1
s=s.replace(needle,'''
binary_files=selection.get("embedded_binary_files", [])
if binary_files:
    cmake_text += "  EMBED_FILES\\n"
    for relative in binary_files:
        source=project_dir/relative
        if not source.is_file():raise FileNotFoundError(source)
        path=source.relative_to(project_dir/"video").as_posix()
        cmake_text += f'    "${{CMAKE_CURRENT_LIST_DIR}}/{path}"\\n'
'''+needle);f.write_text(s)
f=web/'embedded_assets.cpp';s=f.read_text();declarations=[];entries=[]
for name,mime,binary in extras:
 symbol=''.join(c if c.isalnum() else '_' for c in name)
 declarations.extend([f'extern std::uint8_t const {symbol}_start[] asm("_binary_{symbol}_start");',f'extern std::uint8_t const {symbol}_end[] asm("_binary_{symbol}_end");'])
 size=f'static_cast<std::size_t>({symbol}_end-{symbol}_start)' if binary else f'textSize({symbol}_start,{symbol}_end)'
 entries.append(f'      {{"/{name}", "{mime}", {symbol}_start, {size}}},')
s=s.replace('std::size_t textSize(', '\n'.join(declarations)+'\n\nstd::size_t textSize(').replace('EmbeddedAsset, 5','EmbeddedAsset, 12').replace('  }};', '\n'.join(entries)+'\n  }};');f.write_text(s)
f=web/'embedded_assets.hpp';f.write_text(f.read_text().replace('EmbeddedAsset, 5','EmbeddedAsset, 12'))
f=v/'video/extender/network/wired_network_service.cpp';s=f.read_text();s='#include "extender/diagnostics/srle2/codec_probe.hpp"\n'+s
s=s.replace('static bool rle2_requested=false;', 'static bool rle2_requested=false,srle2_requested=false;\nstatic uint8_t *srle2_scratch=nullptr;\nstatic uint64_t srle2_encode_us=0,srle2_attempts=0,srle2_frames=0,srle2_failures=0;')
s=s.replace('  config.max_uri_handlers = 7;', '''  config.max_uri_handlers = 16; // Seven additional assets + two SRLE2 diagnostics.
  // Original entropy functions have nested 1–2KiB local arrays. Qualify with
  // explicit stack headroom, equal across raw/RLE2/SRLE2 controls; no priority change.
  config.stack_size = 16384;''')
s=s.replace('  httpd_config_t config = HTTPD_DEFAULT_CONFIG();','  if(!srle2_scratch)srle2_scratch=(uint8_t*)heap_caps_malloc(393244,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);\n  httpd_config_t config = HTTPD_DEFAULT_CONFIG();')
s=s.replace('  httpd_uri_t video{};', '''  httpd_uri_t srle{};srle.uri="/diagnostics/srle2";srle.method=HTTP_POST;srle.handler=&srle2probe::handler;
  if(httpd_register_uri_handler(server,&srle)!=ESP_OK){stopHttp();return false;}
  httpd_uri_t codec_stats{};codec_stats.uri="/diagnostics/codec-stats";codec_stats.method=HTTP_GET;
  codec_stats.handler=[](httpd_req_t *req)->esp_err_t {
    char reply[512];int n=snprintf(reply,sizeof reply,
      "{\\"rle2_us\\":%llu,\\"rle2_attempts\\":%llu,\\"rle2_frames\\":%llu,\\"srle2_us\\":%llu,\\"srle2_attempts\\":%llu,\\"srle2_frames\\":%llu,\\"srle2_failures\\":%llu,\\"stack_min_bytes\\":%u}",
      (unsigned long long)rle2_encode_us,(unsigned long long)rle2_attempts,(unsigned long long)rle2_frames,
      (unsigned long long)srle2_encode_us,(unsigned long long)srle2_attempts,(unsigned long long)srle2_frames,
      (unsigned long long)srle2_failures,unsigned(uxTaskGetStackHighWaterMark(nullptr)));
    if(n<0||size_t(n)>=sizeof reply)return httpd_resp_send_500(req);
    httpd_resp_set_type(req,"application/json");return httpd_resp_send(req,reply,n);
  };
  if(httpd_register_uri_handler(server,&codec_stats)!=ESP_OK){stopHttp();return false;}
  httpd_uri_t video{};''')
needle='  rle2_requested=httpd_req_get_url_query_str(request,query,sizeof(query))==ESP_OK && std::strcmp(query,"rle2=1")==0;';assert s.count(needle)==1
s=s.replace(needle,needle+'\n  srle2_requested=std::strcmp(query,"srle2=1")==0;')
a0=s.index('  // HTTP task serializes negotiation');b0=s.index('  esp_err_t result = ESP_OK;',a0);s=s[:a0]+(root/'web_send.inc').read_text()+s[b0:];f.write_text(s)
(a.candidate/'hardware-integration.json').write_text(json.dumps(dict(contract='P01h-SRLE2-H02',http_stack_bytes=16384,priority_changed=False,web='EVS1-v1',mainboard_vdp_changed=False,emos_source_changed=False),indent=2)+'\n')
