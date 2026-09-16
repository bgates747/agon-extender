"""Add task-only EVR1 integration to a freshly prepared isolated candidate."""
from pathlib import Path
import sys,json,hashlib
out=Path(sys.argv[1]);code=Path(__file__).resolve().parent;v=out/'source/vdp/video'
f=v/'extender/network/wired_network_service.cpp';s=f.read_text();needle='namespace agon::extender::network {';s=s.replace(needle,needle+'''
// Only HTTP task accesses these after startup; one active video connection.
static uint8_t *rle2_scratch=nullptr;
static bool rle2_requested=false;
static uint64_t rle2_encode_us=0,rle2_attempts=0,rle2_frames=0;
''')
s=s.replace('  httpd_config_t config = HTTPD_DEFAULT_CONFIG();','  if(!rle2_scratch)rle2_scratch=(uint8_t*)heap_caps_malloc(196622,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);\n  httpd_config_t config = HTTPD_DEFAULT_CONFIG();')
start=s.index('esp_err_t WiredNetworkService::videoPostHandshake(');pos=s.index('  auto const socket =',start);s=s[:pos]+'''  char query[32]{};
  rle2_requested=httpd_req_get_url_query_str(request,query,sizeof(query))==ESP_OK && std::strcmp(query,"rle2=1")==0;
'''+s[pos:]
start=s.index('  esp_err_t result = ESP_OK;',s.index('void WiredNetworkService::performQueuedSend()'));end=s.index('\n  timing.finish(',start);s=s[:start]+(code/'web_send.inc').read_text()+s[end:];s=s.replace('result == ESP_OK ? view.total_bytes : 0','result == ESP_OK ? transmitted : 0');f.write_text(s)
f=v/'extender/web/frame_protocol.js';s=f.read_text();decoder=(code/'web_decode.js').read_text().replace('export function unpackRLE2Frame','function unpackRLE2Frame');s=decoder+'\n'+s;s=s.replace('export function parseFrame(buffer) {','export function parseFrame(buffer) {\n  buffer=unpackRLE2Frame(buffer);');f.write_text(s)
f=v/'extender/web/app.js';s=f.read_text().replace('const endpoint = defaultEndpoint();','const endpoint = defaultEndpoint()+"?rle2=1";')
s=s.replace('function sendCredit(request) {\n  if (socket && socket.readyState === WebSocket.OPEN) socket.send(request);\n}', '''let lastCreditAt=0;
function sendCredit(request) {
  const owner=socket;
  const delay=Math.max(0,lastCreditAt+1000/30-performance.now());
  setTimeout(()=>{if(socket===owner && owner && owner.readyState===WebSocket.OPEN){lastCreditAt=performance.now();owner.send(request);}},delay);
}''');f.write_text(s)
m=json.loads((out/'manifest.json').read_text());m['build_id']=m['build_id'].replace('r01-','r02-');m['web_contract']='EVR1-v1-task-candidate';m['web_inputs']={n:hashlib.sha256((code/n).read_bytes()).hexdigest() for n in ('add_web.py','web_send.inc','web_decode.js')};(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
