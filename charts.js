'use strict';
// Plotting only: all pixel statistics and quality metrics come from manual Python loops.
const seriesNames=['Citra asli','Citra noisy',...labels];
function analysisSeries(){
  const s=state.session;
  return [
    {key:0,label:seriesNames[0],image:s.original,analysis:s.analysis.original,metrics:s.baseline.original},
    {key:1,label:seriesNames[1],image:s.noisy,analysis:s.analysis.noisy,metrics:s.baseline.noisy},
    ...state.results.flatMap((r,i)=>r?[{key:i+2,label:labels[i],...r}]:[])
  ];
}
function seriesStyle(key){return `var(--series-${key})`;}
function dash(key){return ['','2 4','9 4','5 3 1 3','12 3 2 3'][key];}
function legend(series){return `<ul class="chart-legend">${series.map(s=>`<li><svg width="28" height="12" aria-hidden="true"><path d="M0 6H28" stroke="${seriesStyle(s.key)}" stroke-width="2" stroke-dasharray="${dash(s.key)}"/></svg>${esc(s.label)}</li>`).join('')}</ul>`;}
function lineChart(series,kind,id){
  const profile=kind==='profile', count=profile?series[0].analysis.profile.length:256;
  let maximum=profile?255:1;
  if(!profile)for(const s of series)for(const v of s.analysis.histogram)if(v>maximum)maximum=v;
  const left=62,top=22,width=600,height=210;
  const px=x=>left+x/Math.max(1,count-1)*width, py=y=>top+height-y/maximum*height;
  const title=profile?'Profil intensitas pada satu baris':'Histogram seluruh citra';
  let svg=`<svg class="analysis-chart" viewBox="0 0 690 286" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${title}</title><desc id="${id}-desc">${profile?'Intensitas 0 sampai 255 pada koordinat x yang sama.':'Jumlah piksel untuk setiap intensitas 0 sampai 255.'} ${esc(series.map(s=>s.label).join(', '))}.</desc>`;
  for(let i=0;i<5;i++){
    const v=maximum*i/4,y=py(v),x=(count-1)*i/4;
    svg+=`<path class="chart-grid" d="M${left} ${y}H${left+width}"/><text class="chart-tick" x="${left-9}" y="${y+4}" text-anchor="end">${num(v,0)}</text><text class="chart-tick" x="${px(x)}" y="${top+height+22}" text-anchor="middle">${num(x,0)}</text>`;
  }
  for(const s of series){
    const values=s.analysis[kind];
    const points=values.map((v,x)=>`${x?'L':'M'}${px(x).toFixed(2)} ${py(v).toFixed(2)}`).join(' ');
    svg+=`<path d="${points}" fill="none" stroke="${seriesStyle(s.key)}" stroke-width="1.6" stroke-dasharray="${dash(s.key)}"/>`;
  }
  return svg+`<text class="chart-tick" x="${left}" y="13">${profile?'Intensitas':'Jumlah piksel'}</text><text class="chart-tick" x="362" y="278" text-anchor="middle">${profile?'Koordinat x (piksel)':'Intensitas grayscale'}</text></svg>`;
}
function metricChart(series,metric){
  const spec={mse:['MSE','Lebih kecil lebih baik'],psnr:['PSNR (dB)','Lebih besar lebih baik'],ssim:['SSIM','Lebih dekat ke 1 lebih baik']}[metric];
  let high=metric==='ssim'?1:Math.max(1,...series.map(s=>s.metrics[metric]===null?0:s.metrics[metric]));
  const low=metric==='ssim'?-1:0,position=v=>(v-low)/(high-low)*100,zero=position(0);
  return `<p class="metric-direction">${spec[0]} · ${spec[1]} · sumbu ${num(low,metric==='ssim'?1:0)}–${num(high,metric==='ssim'?1:2)}</p><div class="metric-bars">${series.map(s=>{
    const v=s.metrics[metric],end=v===null?zero:position(v);
    return `<div class="metric-row"><span>${esc(s.label)}</span><div class="metric-track"><span class="metric-zero" style="left:${zero}%"></span>${v===null?'':`<span class="metric-fill" style="left:${Math.min(zero,end)}%;width:${Math.abs(end-zero)}%;background:${seriesStyle(s.key)}"></span>`}</div><strong>${num(v,metric==='ssim'?5:3)}</strong></div>`;
  }).join('')}</div><p class="support">${metric==='psnr'?'∞ berarti MSE = 0; tidak digambar sebagai batang dengan panjang terbatas.':metric==='ssim'?'Skala −1 hingga 1. Garis tegak menandai nol.':'Acuan identik memiliki MSE = 0; batangnya memang tidak memiliki panjang.'}</p>`;
}
function analysisMarkup(series,id){
  return `<div class="analysis-section"><h3>Analisis citra</h3>${legend(series)}<h4>Profil intensitas · y = ${series[0].analysis.profile_row}</h4><p class="support">Satu baris horizontal yang sama pada semua citra. Garis yang mendekati acuan menunjukkan intensitas lokal yang lebih mirip; ini bukan skor seluruh citra.</p>${lineChart(series,'profile',id+'-profile')}<h4>Distribusi intensitas</h4><p class="support">Histogram dihitung dari seluruh piksel. Sumbu x adalah intensitas, bukan posisi piksel. Histogram serupa belum menjamin struktur citra serupa.</p>${lineChart(series,'histogram',id+'-histogram')}<h4>Kualitas terhadap citra asli</h4><label class="chart-control">Metrik <select data-metric="${id}"><option value="mse">MSE</option><option value="psnr">PSNR (dB)</option><option value="ssim">SSIM</option></select></label><div id="${id}-metrics">${metricChart(series,'mse')}</div></div>`;
}
function mountAnalysis(target,series,id){
  target.innerHTML=analysisMarkup(series,id);
  target.querySelector('[data-metric]').onchange=e=>{document.getElementById(id+'-metrics').innerHTML=metricChart(series,e.target.value);};
}
function renderCombinedAnalysis(){
  const selected=$('#analysis-method').value;
  const series=analysisSeries().filter(s=>s.key<2||selected==='all'||s.key===Number(selected)+2);
  mountAnalysis($('#summary-analysis'),series,'summary');
}
function downloadChartCsv(){
  const series=analysisSeries(),rows=[['image','noise_percent','seed','series','data','row_y','x_or_intensity','value']];
  for(const s of series)for(const kind of ['profile','histogram'])for(let x=0;x<s.analysis[kind].length;x++)rows.push([state.session.image,state.session.noise,state.session.seed,s.label,kind,kind==='profile'?s.analysis.profile_row:'',x,s.analysis[kind][x]]);
  saveCsv(rows,'grafik');
}
