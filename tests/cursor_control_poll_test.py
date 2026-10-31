"""Run retained cursor/idle/parser bodies against timed control-only traffic.

The three dispatcher prologues are compiled from source; leaf command effects
are controlled substitutes. This verifies cursor state, not UART framing,
SDK scheduling, rendered pixels or optical flashing. Optional baseline input
must reproduce the original starvation, without mutating production methods.
"""
from pathlib import Path
import argparse,importlib.util,json,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mode_lifecycle',ROOT/'docs/tasks/PORT-003/phase-e/scripts/run-official-mode-lifecycle.py')
extractor=importlib.util.module_from_spec(spec);spec.loader.exec_module(extractor)

HARNESS=r'''
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <memory>
#define AGON_STOCK_NATIVE_GUARD ((void)0)
#define AGON_EXTENDER_CONSOLE 1
#define AGON_EXTENDER_SD_SERVICE 1
constexpr int CONSOLE_OPCODE=0xF7, CALLBACK_VSYNC=1;
enum class VDUProcessorState {Active,WaitingForFrames,PagedModePaused,CtrlShiftPaused};
uint32_t ticks{},lastFrameCounter{};
uint32_t xTaskGetTickCountFromISR(){return ticks;}
bool ttxtMode=false;
struct {void flash(){}} ttxt_instance;
bool shiftKeyPressed(){return false;} bool ctrlKeyPressed(){return false;}
struct {uint32_t frameCounter{};} display;
auto *_VGAController=&display;
struct Sprite {bool visible=true;};
struct Context {
 bool cursorEnabled=true,cursorFlashing=true,cursorTemporarilyHidden=false,text=true;
 uint32_t cursorTime=ticks;uint16_t cursorFlashRate=640;
 unsigned idleFrameCount{},waitForFrames{};int position{};
 VDUProcessorState processorState=VDUProcessorState::Active;
 std::shared_ptr<Sprite> textCursorSprite=std::make_shared<Sprite>();
 bool textCursorActive(){return text;}
 void clearTempPagedMode(){} void resetPagedModeCount(){}
 auto getProcessorState(){return processorState;}
 void setProcessorState(VDUProcessorState s){processorState=s;}
 bool checkForVSYNC();bool checkForVSYNC(bool);
 void updateTextCursorVisibility();void doCursorFlash();
 void hideCursor();void showCursor();void enableCursor(uint8_t);
};
struct VDUStreamProcessor {
 Context *context;std::deque<uint8_t> bytes;
 void *outputStream{},*originalOutputStream{};unsigned controls{},callbacks{};
 bool byteAvailable(){return !bytes.empty();}
 int readByte(){assert(!bytes.empty());int n=bytes.front();bytes.pop_front();return n;}
 int readByte_t(){return bytes.empty()?-1:readByte();}
 void processEventQueue(){} void handleKeyboardAndMouse(){} void flushEcho(){}
 void bufferCallCallbacks(int){++callbacks;}
 void processNext();void vdu(uint8_t,bool=true);void vdu_sys();void vdu_sys_video();
 void send(std::initializer_list<uint8_t> data){bytes.insert(bytes.end(),data);processNext();}
};
@FUNCTIONS@
// Real cursor-classification prologues, controlled leaf handlers only.
void VDUStreamProcessor::vdu(uint8_t c,bool usePeek){
 @VDU@
 if(c==23)vdu_sys();else if(c==8){if(context->position)--context->position;}
 else if(c==12)context->position=0;else if(c>=32)++context->position;
}
void VDUStreamProcessor::vdu_sys(){
 @SYS@
 if(mode==0)vdu_sys_video();else if(mode==1)context->enableCursor(readByte_t());
}
void VDUStreamProcessor::vdu_sys_video(){
 @VIDEO@
 if(mode==0xF6 || mode==0xF7)++controls;
}
unsigned run(VDUStreamProcessor &p,unsigned duration,bool control,bool draw=false){
 bool previous=p.context->textCursorSprite->visible;unsigned changes=0;
 for(unsigned elapsed=0;elapsed<duration;++elapsed){
  ++ticks;if(elapsed%17==0)++display.frameCounter;
  if(draw && elapsed%10==0)p.send({'A'});
  else if(control && (elapsed+1)*120/1000!=elapsed*120/1000)
   p.send({23,0,uint8_t(p.controls&1?0xF6:0xF7)});
  else p.processNext();
  bool next=p.context->textCursorSprite->visible;changes+=next!=previous;previous=next;
 }
 return changes;
}
int main(){
 Context c;VDUStreamProcessor p{};p.context=&c;
 p.send({12}); // last display command before an empty CLI line
 auto changes=run(p,4096,true);
 if(changes<4 || c.cursorTemporarilyHidden){puts("REPRODUCED: control polling starves cursor restoration");return 40;}
 assert(p.controls>400 && p.callbacks>200);
 // Empty->nonempty->backspace-to-empty, and left-arrow with text retained.
 p.send({'A'});assert(c.position==1);assert(run(p,2200,false)>=3);
 p.send({8});assert(c.position==0);assert(run(p,2200,true)>=3);
 p.send({'A'});p.send({8});assert(c.position==0);assert(run(p,2200,false)>=3);
 // Drawing still suppresses the cursor; controls alone release it afterward.
 run(p,1200,true,true);assert(c.cursorTemporarilyHidden && !c.textCursorSprite->visible);
 assert(run(p,2200,true)>=3);
 p.send({23,1,2});assert(!c.cursorFlashing && c.cursorEnabled);
 assert(run(p,2200,true)==0 && c.textCursorSprite->visible);
 p.send({23,1,0});assert(run(p,2200,true)==0 && !c.textCursorSprite->visible);
 p.send({23,1,3});assert(run(p,2200,true)>=3);
 c.text=false;c.updateTextCursorVisibility();
 assert(run(p,2200,true)==0 && !c.textCursorSprite->visible);
 c.text=true;c.updateTextCursorVisibility();
 ticks=UINT32_MAX-1500;c.cursorTime=ticks;
 assert(run(p,4096,true)>=4); // actual unsigned tick subtraction through wrap
 // Frame waits still complete while only control traffic is arriving.
 c.waitForFrames=3;c.processorState=VDUProcessorState::WaitingForFrames;
 run(p,100,true);assert(c.processorState==VDUProcessorState::Active && p.bytes.empty());
 puts("PASS: actual cursor/idle/processNext and dispatcher prologues: continuous controls, edit paths, drawing, steady/hidden/graphics, tick wrap and frame wait");
}
'''

FILES=['context.h','context/cursor.h','vdu_stream_processor.h','vdu.h','vdu_sys.h']
def source_tree(root,ref,temp):
    if ref is None:return root/'vdp/video'
    for rel in FILES:
        path=temp/rel;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(subprocess.check_output(['git','show',ref+':vdp/video/'+rel],cwd=root))
    return temp
def function(tree,path,name):return extractor.extract_function_text(tree/path,name)[0]
def body(text):return text[text.index('{')+1:]
def compile_run(root,ref,directory):
    tree=source_tree(root,ref,directory/'source')
    functions=[function(tree,'context.h','Context::checkForVSYNC'),
        function(tree,'context.h','updateTextCursorVisibility'),
        *[function(tree,'context/cursor.h','Context::'+n) for n in ['doCursorFlash','hideCursor','showCursor','enableCursor']],
        function(tree,'vdu_stream_processor.h','VDUStreamProcessor::processNext')]
    # The inline class member needs its scope when compiled outside Context.
    functions[1]=functions[1].replace('void updateTextCursorVisibility','void Context::updateTextCursorVisibility',1)
    prologues=[body(function(tree,'vdu.h','VDUStreamProcessor::vdu')).split('// We want to send raw chars back',1)[0],
        body(function(tree,'vdu_sys.h','VDUStreamProcessor::vdu_sys')).split('// If mode is -1',1)[0],
        body(function(tree,'vdu_sys.h','VDUStreamProcessor::vdu_sys_video')).split('// TODO - consider whether',1)[0]]
    code=HARNESS.replace('@FUNCTIONS@','\n'.join(functions))
    for key,value in zip(['@VDU@','@SYS@','@VIDEO@'],prologues):code=code.replace(key,value)
    cpp=directory/'test.cpp';cpp.write_text(code);binary=directory/'test'
    subprocess.run(['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter',
        '-fsanitize=address,undefined','-fno-sanitize-recover=all',str(cpp),'-o',str(binary)],check=True)
    return subprocess.run([str(binary)],text=True,capture_output=True,timeout=15)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-root',type=Path,default=ROOT)
    parser.add_argument('--baseline-ref');parser.add_argument('--report',type=Path);args=parser.parse_args()
    results={}
    with tempfile.TemporaryDirectory(prefix='cursor-control-poll-') as name:
        for label,ref,expected in [('current',None,0),*([('old',args.baseline_ref,40)] if args.baseline_ref else [])]:
            folder=Path(name)/label;folder.mkdir();r=compile_run(args.source_root,ref,folder)
            print(r.stdout,end='');print(r.stderr,end='');assert r.returncode==expected,(label,r.returncode,expected)
            results[label]={'exit_code':r.returncode,'expected_exit_code':expected,'passed':True,'stdout':r.stdout}
    if args.report:args.report.write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
