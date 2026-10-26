'use strict';
const $=selector=>document.querySelector(selector);
const labels=['Median Filter','Adaptive Median','Gaussian Filter'];
const state={name:null,noise:null,session:null,busy:false,results:[null,null,null]};
const num=(value,digits=3)=>value===null?'∞':new Intl.NumberFormat('id-ID',{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(value);
const esc=text=>String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const descriptions=['Median 3×3 · urutkan, pilih tengah','Adaptif 3×3–7×7 · uji A dan B','Gaussian 3×3 · konvolusi berbobot'];
function status(message,error=false){$('#status').textContent=message;$('#status').classList.toggle('error',error);}
function setBusy(value){
  state.busy=value;$('#configuration').disabled=value;
  $('#prepare-button').disabled=value||!state.name||state.noise===null;
  document.querySelectorAll('[data-noise]').forEach(b=>b.disabled=value||!state.name);
  $('#download-csv').disabled=value||!state.session;
  $('#download-chart-csv').disabled=value||!state.session;
}
function renderCards(){
  $('#method-cards').innerHTML=labels.map((label,i)=>`<article class="method-card" id="method-${i}" aria-labelledby="method-title-${i}" aria-busy="false"><div class="method-card-heading"><span class="method-number">0${i+1}</span><span id="method-state-${i}" class="method-state">Menunggu noise</span></div><h3 id="method-title-${i}">${esc(label)}</h3><p class="method-config">${descriptions[i]}</p><div class="image-frame restoration-frame"><img id="result-${i}" alt="Hasil ${esc(label)}" hidden><span id="placeholder-${i}">Belum diproses</span><span id="scan-${i}" class="scan-line" hidden aria-hidden="true"></span></div><label class="method-progress-label" for="progress-${i}" id="progress-label-${i}">Belum dimulai</label><progress id="progress-${i}" value="0" max="100"></progress><p id="scores-${i}" class="card-scores">MSE —<br>PSNR —<br>SSIM —</p><button class="quiet full compare-method" data-compare="${i}" disabled>Bandingkan grafik →</button></article>`).join('');
  document.querySelectorAll('[data-compare]').forEach(b=>b.onclick=()=>{
    $('#analysis-method').value=b.dataset.compare;renderCombinedAnalysis();$('#summary-panel').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  });
}
function clearResults(){
  state.session=null;state.results=[null,null,null];$('#summary-panel').hidden=true;$('#run-count').textContent='0 / 3 selesai';
  renderCards();$('#noisy-image').hidden=true;$('#noise-placeholder').hidden=false;$('#noise-caption').textContent='Belum dibuat';
  $('#noise-description').textContent='Pilih persentase noise untuk memulai perbandingan.';setBusy(false);
}
async function loadGallery(){
  try{
    const response=await fetch('/api/images');if(!response.ok)throw new Error('Galeri tidak dapat dimuat.');
    const data=await response.json();if(!data.images.length)throw new Error('Dataset Set12 belum tersedia.');
    $('#gallery-count').textContent=`${data.images.length} gambar`;
    $('#image-gallery').innerHTML=data.images.map(name=>`<button class="gallery-item" type="button" data-image="${esc(name)}" aria-label="Pilih citra ${esc(name)}" aria-pressed="false"><img loading="lazy" src="/data/Set12/${encodeURIComponent(name)}" alt="Citra Set12 ${esc(name)}"><span>${esc(name)}</span></button>`).join('');
  }catch(error){$('#gallery-count').textContent='Tidak tersedia';status(error.message,true);}
}
async function post(path,body){
  const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data=await response.json();if(!response.ok)throw new Error(data.error||'Permintaan gagal.');return data;
}
function showFrame(method,event){
  const img=$('#result-'+method);img.src=event.image;img.hidden=false;$('#placeholder-'+method).hidden=true;
  if(event.type==='preview'){
    const line=$('#scan-'+method);line.hidden=event.done>=event.total;line.style.top=(100*event.done/event.total)+'%';
  }
}
async function processMethod(method){
  const card=$('#method-'+method);card.classList.add('processing');card.setAttribute('aria-busy','true');
  $('#method-state-'+method).textContent='Memfilter';status(`Memulihkan citra dengan ${labels[method]}…`);
  const response=await fetch('/api/process',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:state.session.session,method})});
  if(!response.ok){const data=await response.json();throw new Error(data.error||'Filter gagal dimulai.');}
  const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='',received=false;
  const consume=event=>{
    if(event.type==='error')throw new Error(event.error);
    if(event.type==='preview'||event.type==='filtered')showFrame(method,event);
    if(event.type==='progress'){
      const progress=$('#progress-'+method);progress.max=event.total;progress.value=event.done;
      const phase={filter:'Filter',mse:'MSE',ssim:'SSIM'}[event.phase];
      $('#progress-label-'+method).textContent=`${phase} · ${num(event.done,0)} / ${num(event.total,0)} ${event.phase==='ssim'?'blok':'baris'}`;
      $('#method-state-'+method).textContent=event.phase==='filter'?'Memfilter':'Mengukur kualitas';
    }
    if(event.type==='result'){
      received=true;state.results[method]=event;showFrame(method,event);$('#scan-'+method).hidden=true;
      const m=event.metrics;$('#scores-'+method).textContent=`MSE ${num(m.mse,3)}\nPSNR ${num(m.psnr,3)} dB\nSSIM ${num(m.ssim,5)}`;
    }
  };
  try{
    while(true){
      const {value,done}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!done});
      let cut;while((cut=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,cut);buffer=buffer.slice(cut+1);if(line.trim())consume(JSON.parse(line));}
      if(done)break;await new Promise(requestAnimationFrame);
    }
    if(buffer.trim())consume(JSON.parse(buffer));if(!received)throw new Error('Koneksi terputus sebelum hasil lengkap diterima.');
    card.classList.add('complete');$('#method-state-'+method).textContent='Selesai';$('#progress-label-'+method).textContent='Filter dan evaluasi selesai';
    $('#run-count').textContent=`${state.results.filter(Boolean).length} / 3 selesai`;
  }finally{reader.releaseLock();card.classList.remove('processing');card.setAttribute('aria-busy','false');$('#scan-'+method).hidden=true;}
}
async function runExperiment(){
  if(state.busy||!state.name||state.noise===null)return;
  const input=$('#seed-input'),seed=Number(input.value);
  if(input.value===''||!Number.isInteger(seed)||seed<0||seed>2147483647){status('Seed harus bilangan bulat antara 0 dan 2147483647.',true);return;}
  clearResults();setBusy(true);$('#state-label').textContent='Membuat noise';status('Membuat salt-and-pepper noise…');let active=-1;
  try{
    const data=await post('/api/prepare',{image:state.name,noise:state.noise,seed});state.session=data;
    $('#original-image').src=data.original;$('#original-image').hidden=false;$('#original-placeholder').hidden=true;
    $('#noisy-image').src=data.noisy;$('#noisy-image').hidden=false;$('#noise-placeholder').hidden=true;$('#noisy-image').classList.remove('reveal-image');void $('#noisy-image').offsetWidth;$('#noisy-image').classList.add('reveal-image');
    $('#noise-caption').textContent=`${data.noise}% · seed ${data.seed}`;
    $('#experiment-meta').textContent=`${data.image} · ${data.width} × ${data.height} · noise ${data.noise}%`;
    $('#noise-description').textContent=`${num(data.count,0)} dari ${num(data.width*data.height,0)} lokasi dipilih untuk diganti 0 atau 255. Lokasi yang sudah bernilai sama mungkin tidak berubah.`;
    for(let method=0;method<3;method++){
      $('#result-'+method).src=data.noisy;$('#result-'+method).hidden=false;$('#placeholder-'+method).hidden=true;$('#method-state-'+method).textContent='Menunggu giliran';
    }
    await new Promise(requestAnimationFrame);
    for(let method=0;method<3;method++){active=method;$('#state-label').textContent=labels[method];await processMethod(method);}
    renderSummary();$('#state-label').textContent='Perbandingan siap';status('Ketiga metode selesai. Bandingkan visual, metrik, dan grafik di bawah.');
  }catch(error){
    if(active>=0){$('#method-state-'+active).textContent='Terhenti';$('#method-'+active).classList.add('failed');$('#method-'+active).classList.remove('processing');$('#method-'+active).setAttribute('aria-busy','false');}
    $('#state-label').textContent='Perlu dijalankan ulang';status(error.message+' Tekan Jalankan ulang untuk mencoba lagi.',true);
    if(state.results.some(Boolean))renderSummary();
  }finally{setBusy(false);document.querySelectorAll('[data-compare]').forEach(b=>b.disabled=!state.results[Number(b.dataset.compare)]);}
}
function renderSummary(){
  $('#summary-panel').hidden=false;
  $('#score-body').innerHTML=analysisSeries().map(s=>`<tr><td>${esc(s.label)}</td><td>${num(s.metrics.mse,4)}</td><td>${num(s.metrics.psnr,3)}</td><td>${num(s.metrics.ssim,5)}</td></tr>`).join('');
  const selected=$('#analysis-method').value;
  if(selected!=='all'&&!state.results[Number(selected)])$('#analysis-method').value='all';
  document.querySelectorAll('#analysis-method option').forEach(o=>o.disabled=o.value!=='all'&&!state.results[Number(o.value)]);
  renderCombinedAnalysis();
}
function saveCsv(rows,prefix){
  const csv='\ufeff'+rows.map(row=>row.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(',')).join('\r\n');
  const a=document.createElement('a'),url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.href=url;a.download=`${prefix}_${state.session.image.replace('.png','')}_noise${state.session.noise}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function downloadCsv(){
  saveCsv([['image','noise_percent','seed','method','mse','psnr_db','ssim_block8'],...analysisSeries().map(s=>[state.session.image,state.session.noise,state.session.seed,s.label,s.metrics.mse,s.metrics.psnr===null?'Infinity':s.metrics.psnr,s.metrics.ssim])],'hasil');
}
$('#image-gallery').onclick=event=>{
  const button=event.target.closest('[data-image]');if(!button||state.busy)return;
  state.name=button.dataset.image;state.noise=null;clearResults();
  document.querySelectorAll('[data-image]').forEach(b=>{b.classList.toggle('selected',b===button);b.setAttribute('aria-pressed',String(b===button));});
  document.querySelectorAll('[data-noise]').forEach(b=>{b.classList.remove('selected');b.setAttribute('aria-pressed','false');});
  $('#selected-name').textContent=`Terpilih: ${state.name}`;$('#original-image').src='/data/Set12/'+encodeURIComponent(state.name);$('#original-image').hidden=false;$('#original-placeholder').hidden=true;
  $('#experiment-meta').textContent=state.name;$('#state-label').textContent='Pilih noise';status('Citra asli siap. Pilih persentase noise untuk menjalankan perbandingan.');
};
document.querySelectorAll('[data-noise]').forEach(b=>b.onclick=()=>{
  if(state.busy||!state.name)return;state.noise=Number(b.dataset.noise);
  document.querySelectorAll('[data-noise]').forEach(x=>{x.classList.toggle('selected',x===b);x.setAttribute('aria-pressed',String(x===b));});return runExperiment();
});
$('#seed-input').oninput=()=>{if(!state.busy){clearResults();$('#state-label').textContent='Seed berubah';status('Seed berubah. Tekan Jalankan ulang atau pilih noise untuk membuat hasil baru.');}};
$('#prepare-button').onclick=runExperiment;$('#analysis-method').onchange=()=>renderCombinedAnalysis();$('#download-csv').onclick=downloadCsv;$('#download-chart-csv').onclick=()=>downloadChartCsv();
renderCards();loadGallery();
