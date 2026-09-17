import {header,simple} from './envelope.js';
export class Decoder{
 constructor(timeoutMs=2000,workerUrl=new URL('./worker.js',import.meta.url)){this.workerUrl=workerUrl;this.timeoutMs=timeoutMs;this.worker=null;this.pending=null;this.next=0;}
 reset(reason='reset'){if(this.worker)this.worker.terminate();this.worker=null;if(this.pending){clearTimeout(this.pending.timer);this.pending.reject(Error(reason));this.pending=null;}}
 async decode(buffer,verify=false){let h=header(buffer);if(h.kind<2)return simple(buffer);if(this.pending)throw Error('Decoder busy');
  if(!this.worker){this.worker=new Worker(this.workerUrl,{type:'module'});this.worker.onerror=()=>this.reset('Worker error');this.worker.onmessage=e=>{const p=this.pending;if(!p||e.data.id!==p.id)return;clearTimeout(p.timer);this.pending=null;if(e.data.error){this.worker.terminate();this.worker=null;p.reject(Error(e.data.error));}else p.resolve(e.data);};}
  return new Promise((resolve,reject)=>{const id=++this.next,timer=setTimeout(()=>this.reset('Decoder timeout'),this.timeoutMs);this.pending={id,timer,resolve,reject};this.worker.postMessage({id,buffer,verify},[buffer]);});
 }
}
