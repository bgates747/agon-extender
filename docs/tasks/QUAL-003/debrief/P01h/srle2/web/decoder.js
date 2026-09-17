// Shared client decoder. Worker lifetime bounds malformed original-C execution.
export class FrameDecoder {
 constructor({timeoutMs=2000,workerURL=new URL('./decoder-worker.js',import.meta.url)}={}){this.timeoutMs=timeoutMs;this.workerURL=workerURL;this.worker=null;this.pending=null;this.sequence=0;}
 reset(reason='Decoder reset'){
  if(this.worker)this.worker.terminate();this.worker=null;
  if(this.pending){clearTimeout(this.pending.timer);this.pending.reject(new Error(reason));this.pending=null;}
 }
 async decode(buffer){
  if(!(buffer instanceof ArrayBuffer))throw new Error('Frame must be binary');
  if(buffer.byteLength<4||String.fromCharCode(...new Uint8Array(buffer,0,4))!=='EVS1')return {buffer,metrics:{szipMs:0,rleMs:0,totalMs:0}};
  if(this.pending)throw new Error('Decoder busy');
  if(!this.worker){this.worker=new Worker(this.workerURL,{type:'module'});this.worker.onerror=()=>this.reset('Decoder worker error');this.worker.onmessage=e=>{
   const p=this.pending;if(!p||e.data.id!==p.id)return;clearTimeout(p.timer);this.pending=null;
   if(e.data.error){this.worker.terminate();this.worker=null;p.reject(new Error(e.data.error));}else p.resolve(e.data);
  };}
  return new Promise((resolve,reject)=>{const id=++this.sequence,timer=setTimeout(()=>this.reset('Decoder timeout'),this.timeoutMs);this.pending={id,timer,resolve,reject};this.worker.postMessage({id,buffer},[buffer]);});
 }
}
