const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=new Map(),requests=[];
function el(key){
  if(!nodes.has(key)){
    let src='';const classes=new Set();
    nodes.set(key,{innerHTML:'',textContent:'',value:key==='#seed-input'?'42':key==='#analysis-method'?'all':'',hidden:true,disabled:false,dataset:{},style:{},sources:[],
      get src(){return src},set src(value){src=value;this.sources.push(value)},
      classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),toggle:(x,v)=>v?classes.add(x):classes.delete(x),contains:x=>classes.has(x)},
      setAttribute(k,v){this[k]=v},querySelector:k=>el(key+' '+k),scrollIntoView(){}});
  }return nodes.get(key);
}
const noise=[5,10,20,30].map(n=>Object.assign(el('noise'+n),{dataset:{noise:String(n)}}));
const compare=[0,1,2].map(n=>Object.assign(el('compare'+n),{dataset:{compare:String(n)}}));
const photo=Object.assign(el('photo'),{dataset:{image:'01.png'}});
const options=['all','0','1','2'].map(value=>({value}));
const queryAll=key=>({'[data-noise]':noise,'[data-compare]':compare,'[data-image]':[photo],'#analysis-method option':options}[key]||[]);
const analysis={profile_row:1,profile:[0,128,255],histogram:Array.from({length:256},(_,i)=>i===0?3:0),pixel_count:3};
let failure=-1;
const responseJson=data=>({ok:true,json:async()=>data});
const sandbox={Intl,Blob,URL,TextDecoder,Uint8Array,setTimeout,clearTimeout,console,matchMedia:()=>({matches:true}),requestAnimationFrame:callback=>setImmediate(callback),
  document:{querySelector:el,querySelectorAll:queryAll,getElementById:id=>el('#'+id)},
  fetch:async(path,options)=>{
    const body=options?JSON.parse(options.body):{};requests.push({path,body});
    if(path==='/api/images')return responseJson({images:['01.png']});
    if(path==='/api/prepare')return responseJson({session:'test',image:'01.png',noise:body.noise,seed:body.seed,width:3,height:3,count:1,original:'original',noisy:'noisy',analysis:{original:analysis,noisy:analysis},baseline:{original:{mse:0,psnr:null,ssim:1},noisy:{mse:50,psnr:31,ssim:-.1}}});
    const m=body.method;
    if(m===failure)return {ok:false,json:async()=>({error:'Test failure'})};
    const events=[{type:'progress',phase:'filter',done:1,total:3},
      {type:'preview',image:'partial-'+m,done:1,total:3},
      {type:'filtered',image:'final-'+m},
      {type:'progress',phase:'mse',done:3,total:3},
      {type:'result',method:m,image:'final-'+m,analysis,metrics:{mse:10+m,psnr:38-m,ssim:.9-m*.1}}];
    const bytes=new TextEncoder().encode(events.map(e=>JSON.stringify(e)).join('\n')+'\n');
    let start=0;
    return {ok:true,body:new ReadableStream({pull(controller){if(start>=bytes.length){controller.close();return}controller.enqueue(bytes.slice(start,start+47));start+=47;}})};
  }};
const rootDir=path.resolve(__dirname,'..');
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(rootDir,'app.js'),'utf8')+'\n'+fs.readFileSync(path.join(rootDir,'charts.js'),'utf8'),sandbox);
const evaluate=code=>vm.runInContext(code,sandbox);
async function main(){
  await new Promise(setImmediate);requests.length=0;
  el('#image-gallery').onclick({target:{closest:()=>photo}});
  assert.equal(el('#original-image').src,'/data/Set12/01.png');assert.equal(requests.length,0);
  await noise[1].onclick();
  assert.deepEqual(requests.map(r=>r.path),['/api/prepare','/api/process','/api/process','/api/process']);
  assert.deepEqual(requests.slice(1).map(r=>r.body.method),[0,1,2]);
  assert.equal(el('#run-count').textContent,'3 / 3 selesai');
  assert.equal(el('#summary-panel').hidden,false);
  assert.equal((el('#score-body').innerHTML.match(/<tr>/g)||[]).length,5);
  for(let m=0;m<3;m++){
    assert(el('#result-'+m).sources.includes('partial-'+m));assert.equal(el('#result-'+m).src,'final-'+m);
    assert.equal(el('#method-'+m)['aria-busy'],'false');assert.equal(el('#scan-'+m).hidden,true);
  }
  el('#analysis-method').value='1';el('#analysis-method').onchange();
  assert(el('#summary-analysis').innerHTML.includes('Adaptive Median'));
  assert(!el('#summary-analysis').innerHTML.includes('Gaussian Filter'));
  const psnr=evaluate("metricChart(analysisSeries(),'psnr')");assert(psnr.includes('∞'));assert(!/NaN|undefined|Infinity%/.test(psnr));
  failure=1;await noise[2].onclick();
  assert.equal(el('#method-state-1').textContent,'Terhenti');assert.equal(evaluate('state.busy'),false);
  assert.equal((el('#score-body').innerHTML.match(/<tr>/g)||[]).length,3);
  assert.equal(compare[1].disabled,true);
  failure=-1;await el('#prepare-button').onclick();assert.equal(el('#run-count').textContent,'3 / 3 selesai');
  requests.length=0;el('#seed-input').value='-1';await el('#prepare-button').onclick();assert.equal(requests.length,0);
  el('#seed-input').value='42';el('#seed-input').oninput();assert.equal(el('#summary-panel').hidden,true);assert.equal(evaluate('state.session'),null);
  el('#image-gallery').onclick({target:{closest:()=>photo}});assert.equal(evaluate('state.noise'),null);
  console.log('Visual flow checks passed: photo/noise auto-run, 3 streams, actual previews, five-series chart, error recovery, invalid seed and reset.');
}
main().catch(error=>{console.error(error);process.exitCode=1});
