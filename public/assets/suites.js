(() => {
  'use strict';

  const root = document.querySelector('[data-suite]');
  if (!root) return;
  const suite = root.dataset.suite;
  const nf = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 2 });
  const n0 = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 });
  const eur = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 });
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const track = (event, details = {}) => { if (window.gtag) window.gtag('event', event, { suite_id: suite, page_path: location.pathname, ...details }); };
  const money = value => Number.isFinite(Number(value)) ? eur.format(Number(value)) : '—';
  const pct = value => Number.isFinite(Number(value)) ? `${nf.format(Number(value))} %` : '—';
  const num = value => Number.isFinite(Number(value)) ? nf.format(Number(value)) : '—';
  const int = value => Number.isFinite(Number(value)) ? n0.format(Number(value)) : '—';
  const card = (label, value, hint='') => `<div class="suite-kpi"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${hint ? `<small>${escapeHtml(hint)}</small>` : ''}</div>`;
  const resultBox = root.querySelector('[data-suite-result]');
  const errorBox = root.querySelector('[data-suite-error]');
  const STORAGE_KEY = `clicivo:suite:v1:${suite}`;
  let firstInteraction = true;

  function values(form) {
    const out = {};
    [...form.elements].forEach(el => {
      if (!el.name || ['button','submit','reset','file'].includes(el.type)) return;
      out[el.name] = el.type === 'checkbox' ? el.checked : (el.type === 'number' ? Number(el.value) : el.value);
    });
    return out;
  }
  function saveValues(form) {
    const data = {};
    [...form.elements].forEach(el => {
      if (!el.name || ['button','submit','reset','file'].includes(el.type)) return;
      data[el.name] = el.type === 'checkbox' ? el.checked : el.value;
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }
  function restoreValues(form) {
    let data = null;
    try { data = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch {}
    if (!data) return false;
    Object.entries(data).forEach(([name, value]) => {
      const el = form.elements.namedItem(name);
      if (!el) return;
      if (el.type === 'checkbox') el.checked = Boolean(value); else el.value = value;
    });
    return true;
  }
  function copyText(text, button) {
    navigator.clipboard?.writeText(text).then(() => {
      const old = button.textContent; button.textContent = 'Copiado ✓'; setTimeout(() => button.textContent = old, 1400);
    }).catch(() => {});
  }
  function printableText() {
    return `${document.querySelector('h1')?.textContent || 'Suite Clicivo'}\n${new Date().toLocaleDateString('es-ES')}\n\n${resultBox?.innerText || ''}\n\n${location.href}`;
  }
  function downloadPdf() {
    if (!window.jspdf?.jsPDF) { window.print(); track('suite_print_fallback'); return; }
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ unit:'mm', format:'a4' });
    const lines = doc.splitTextToSize(printableText(), 178);
    doc.setFont('helvetica','bold'); doc.setFontSize(18); doc.text('Clicivo', 16, 18);
    doc.setFont('helvetica','normal'); doc.setFontSize(10);
    let y = 28;
    lines.forEach(line => { if (y > 282) { doc.addPage(); y = 18; } doc.text(line, 16, y); y += 5; });
    doc.save(`clicivo-suite-${suite}.pdf`); track('suite_pdf_download');
  }
  function daysBetween(a,b,inclusive=false) {
    const start = new Date(`${a}T12:00:00`), end = new Date(`${b}T12:00:00`);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return NaN;
    return Math.floor((end-start)/86400000) + (inclusive ? 1 : 0);
  }

  function calculateCreators(form) {
    const v = values(form);
    if (v.ytViews <= 0 || v.ttViews <= 0 || v.igInitial <= 0 || v.igDays <= 0) throw new Error('Revisa vistas, seguidores iniciales y días: deben ser mayores que cero.');
    const ytRpm = v.ytRevenue / v.ytViews * 1000;
    const ytTargetRevenue = v.ytTargetViews / 1000 * ytRpm;
    const ttRpm = v.ttRewards / v.ttViews * 1000;
    const ttTargetRewards = v.ttTargetViews / 1000 * ttRpm;
    const igNet = v.igFinal - v.igInitial;
    const igGrowth = igNet / v.igInitial * 100;
    const igDaily = igNet / v.igDays;
    const igDaysToTarget = igDaily > 0 && v.igTarget > v.igFinal ? (v.igTarget-v.igFinal)/igDaily : null;
    resultBox.innerHTML = `<div class="suite-result-head"><span>Fotografía multicanal</span><h2>Tres plataformas, una sola lectura</h2><p>Todos los datos se mantienen en este navegador.</p></div><div class="suite-kpi-grid">
      ${card('RPM YouTube',money(ytRpm),'Ingreso por 1.000 vistas')}
      ${card(`YouTube con ${int(v.ytTargetViews)} vistas`,money(ytTargetRevenue),'Manteniendo tu RPM')}
      ${card('RPM TikTok',money(ttRpm),'Por 1.000 vistas cualificadas')}
      ${card(`TikTok con ${int(v.ttTargetViews)} vistas`,money(ttTargetRewards),'Manteniendo tu RPM')}
      ${card('Crecimiento Instagram',pct(igGrowth),`${int(igNet)} seguidores netos`)}
      ${card('Ritmo diario Instagram',`${num(igDaily)} seg./día`,igDaysToTarget ? `Meta en ~${int(Math.ceil(igDaysToTarget))} días` : 'Sin fecha proyectable')}
    </div><div class="suite-insight"><strong>Lectura recomendada</strong><p>Compara el RPM de cada plataforma con su propio histórico y usa el crecimiento de Instagram como tendencia, no como predicción. Guarda esta fotografía y repite el mismo criterio en el siguiente periodo.</p></div>`;
    track('suite_complete', { suite_type:'creators' });
  }

  function dismissalDays(type, start, end) {
    const totalDays = daysBetween(start,end,false); if (!(totalDays > 0)) return {days:0,years:0};
    const years = totalDays / 365.2425;
    if (type === 'objective') return { days:Math.min(years*20,360), years };
    if (type === 'temporary') return { days:years*12, years };
    const cut='2012-02-12';
    if (start < cut) {
      const preEnd = end < cut ? end : cut;
      const pre = Math.max(0, daysBetween(start,preEnd,false)/365.2425*45);
      const post = end > cut ? Math.max(0,daysBetween(cut,end,false)/365.2425*33) : 0;
      const cap = pre > 720 ? Math.min(pre,1260) : 720;
      return {days:Math.min(pre+post,cap),years};
    }
    return {days:Math.min(years*33,720),years};
  }

  function calculateLabor(form) {
    const v = values(form);
    if (v.gross <= 0) throw new Error('El salario bruto anual debe ser mayor que cero.');
    const dedRate=(v.irpf+v.workerSs)/100; if (dedRate >= 1) throw new Error('IRPF y cotización no pueden sumar 100 % o más.');
    const net = v.gross*(1-dedRate);
    const contribution = v.gross*v.employerRate/100;
    const employerTotal = v.gross+contribution+v.otherCosts;
    const worked = daysBetween(v.start,v.end,true); if (!(worked>0)) throw new Error('La fecha final debe ser igual o posterior a la inicial.');
    const accrued = v.annualVacation*worked/365.2425;
    const pending = Math.max(0,accrued-v.takenVacation);
    const monthly = v.gross/12, daily = monthly/30;
    const ind = dismissalDays(v.terminationType,v.start,v.end);
    const compensation = v.includeCompensation ? (v.gross/365)*ind.days : 0;
    const settlement = daily*v.finalSalaryDays + daily*pending + v.extraPay;
    const totalExit = settlement + compensation;
    resultBox.innerHTML = `<div class="suite-result-head"><span>Escenario laboral conectado</span><h2>Del salario al coste y a la salida</h2><p>Estimación orientativa para España. Revisa convenio, nóminas y causa real de extinción.</p></div><div class="suite-kpi-grid">
      ${card('Neto anual estimado',money(net),`${money(net/Number(v.payments))} por paga`)}
      ${card('Coste empresa anual',money(employerTotal),`${money(employerTotal/12)} al mes`)}
      ${card('Vacaciones pendientes',`${num(pending)} días`,`${num(accrued)} generadas`)}
      ${card('Finiquito sin indemnización',money(settlement),'Salario + vacaciones + paga extra')}
      ${card('Indemnización orientativa',money(compensation),`${num(ind.days)} días indemnizatorios`)}
      ${card('Salida total orientativa',money(totalExit),'Finiquito + indemnización seleccionada')}
    </div><div class="suite-table-wrap"><table class="data-table"><thead><tr><th>Concepto</th><th>Base</th><th>Resultado</th></tr></thead><tbody>
      <tr><td>Salario bruto</td><td>Anual</td><td>${money(v.gross)}</td></tr>
      <tr><td>IRPF + cotización trabajador</td><td>${pct(v.irpf+v.workerSs)}</td><td>${money(v.gross*dedRate)}</td></tr>
      <tr><td>Cotización empresa</td><td>${pct(v.employerRate)}</td><td>${money(contribution)}</td></tr>
      <tr><td>Periodo trabajado</td><td>${int(worked)} días</td><td>${num(ind.years)} años</td></tr>
      <tr><td>Vacaciones</td><td>${num(v.annualVacation)} / año</td><td>${num(pending)} pendientes</td></tr>
    </tbody></table></div>`;
    track('suite_complete', { suite_type:'labor' });
  }

  function initFormSuite(type, calculator) {
    const form = root.querySelector('[data-suite-form]'); if (!form) return;
    const run = (user=true) => {
      try { errorBox.textContent=''; calculator(form); if (user) track('suite_result_view',{suite_type:type}); }
      catch (e) { errorBox.textContent=e.message || 'Revisa los datos.'; if (user) track('suite_error',{suite_type:type}); }
    };
    form.addEventListener('input',()=>{ if (firstInteraction) { firstInteraction=false; track('suite_start',{suite_type:type}); } });
    form.addEventListener('submit',e=>{e.preventDefault();run(true);});
    root.addEventListener('click',e=>{
      const save=e.target.closest('[data-suite-save]'); if(save){saveValues(form);save.textContent='Guardado ✓';setTimeout(()=>save.textContent='Guardar fotografía',1200);track('suite_save');}
      const load=e.target.closest('[data-suite-load]'); if(load){if(restoreValues(form)){run(true);load.textContent='Recuperado ✓';setTimeout(()=>load.textContent='Recuperar',1200);track('suite_load');}else{load.textContent='Sin datos guardados';setTimeout(()=>load.textContent='Recuperar',1200);}}
      const copy=e.target.closest('[data-suite-copy]'); if(copy){copyText(printableText(),copy);track('suite_copy');}
      if(e.target.closest('[data-suite-pdf]')) downloadPdf();
    });
    run(false);
  }

  // ---- File workspace -----------------------------------------------------
  let pdfFile=null, pdfPageCount=null, imageFiles=[], imagePreviewUrl=null;
  const bytes = size => { const u=['B','KB','MB','GB']; let n=Number(size)||0,i=0; while(n>=1024&&i<u.length-1){n/=1024;i++;} return `${nf.format(n)} ${u[i]}`; };
  const cleanBase = name => String(name||'archivo').replace(/\.[^.]+$/,'').replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]+/g,'-') || 'archivo';
  function blobDownload(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);track('file_download',{file_name:name,file_size:blob.size||0});}
  async function zipDownload(files,name){if(files.length===1){blobDownload(files[0].blob,files[0].name);return;}const zip=new JSZip();files.forEach(f=>zip.file(f.name,f.blob));blobDownload(await zip.generateAsync({type:'blob',compression:'DEFLATE',compressionOptions:{level:6}}),name);}
  function parsePages(text,count){const raw=String(text||'').trim().toLowerCase();if(!raw||raw==='todas')return Array.from({length:count},(_,i)=>i);const out=[];raw.split(',').forEach(part=>{const t=part.trim(),m=t.match(/^(\d+)\s*-\s*(\d+)$/);if(m){let a=Number(m[1]),b=Number(m[2]);if(a>b)throw new Error(`Rango invertido: ${t}`);for(let i=a;i<=b;i++)out.push(i-1);}else if(/^\d+$/.test(t))out.push(Number(t)-1);else throw new Error(`No se entiende «${t}».`);});const uniq=[...new Set(out)];uniq.forEach(i=>{if(i<0||i>=count)throw new Error(`La página ${i+1} no existe.`);});return uniq;}
  function renderFileStatus(){
    const pdfStatus=root.querySelector('[data-pdf-status]'); if(pdfStatus) pdfStatus.innerHTML=pdfFile?`<strong>${escapeHtml(pdfFile.name)}</strong><span>${bytes(pdfFile.size)}${Number.isFinite(pdfPageCount)?` · ${int(pdfPageCount)} páginas`:''}</span>`:'Ningún PDF seleccionado.';
    const imgStatus=root.querySelector('[data-image-status]'); if(imgStatus) imgStatus.innerHTML=imageFiles.length?`<strong>${imageFiles.length} imágenes</strong><span>${bytes(imageFiles.reduce((s,f)=>s+f.size,0))}</span>`:'Ninguna imagen seleccionada.';
    const preview=root.querySelector('[data-image-preview]');
    if(preview){if(imagePreviewUrl)URL.revokeObjectURL(imagePreviewUrl);imagePreviewUrl=imageFiles[0]?URL.createObjectURL(imageFiles[0]):null;preview.innerHTML=imagePreviewUrl?`<img src="${imagePreviewUrl}" alt="Vista previa de la primera imagen"><span>Primera imagen del lote</span>`:'<span>La vista previa aparecerá aquí.</span>';}
  }
  async function pdfExtract(action){
    if(!pdfFile)throw new Error('Selecciona un PDF primero.'); if(!window.PDFLib)throw new Error('No se ha cargado el componente PDF.');
    const src=await PDFLib.PDFDocument.load(await pdfFile.arrayBuffer(),{ignoreEncryption:false});
    const pages=parsePages(root.querySelector('[name="pdfPages"]').value,src.getPageCount());
    if(action==='extract'){
      const out=await PDFLib.PDFDocument.create(); const copied=await out.copyPages(src,pages); copied.forEach(p=>out.addPage(p)); blobDownload(new Blob([await out.save()],{type:'application/pdf'}),`${cleanBase(pdfFile.name)}-seleccion.pdf`);
      resultBox.innerHTML=`${card('Páginas extraídas',int(pages.length),`de ${int(src.getPageCount())}`)}<p class="suite-result-note">El PDF original no se ha subido a Clicivo.</p>`;
    } else if(action==='split') {
      const generated=[];for(const index of pages){const out=await PDFLib.PDFDocument.create();const [p]=await out.copyPages(src,[index]);out.addPage(p);generated.push({name:`${cleanBase(pdfFile.name)}-pagina-${index+1}.pdf`,blob:new Blob([await out.save()],{type:'application/pdf'})});}
      await zipDownload(generated,`${cleanBase(pdfFile.name)}-paginas.zip`); resultBox.innerHTML=`${card('Páginas separadas',int(generated.length),'Descarga ZIP o PDF individual')}<p class="suite-result-note">Puedes cambiar la selección y volver a procesar sin subir de nuevo el archivo.</p>`;
    } else if(action==='jpg') {
      if(!window.pdfjsLib)throw new Error('No se ha cargado el componente de vista PDF.');window.pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
      const doc=await window.pdfjsLib.getDocument({data:await pdfFile.arrayBuffer()}).promise;const generated=[];
      for(const index of pages){const page=await doc.getPage(index+1);const viewport=page.getViewport({scale:2});const canvas=document.createElement('canvas');canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);await page.render({canvasContext:canvas.getContext('2d'),viewport}).promise;const blob=await new Promise(r=>canvas.toBlob(r,'image/jpeg',.9));generated.push({name:`${cleanBase(pdfFile.name)}-pagina-${index+1}.jpg`,blob});}
      await zipDownload(generated,`${cleanBase(pdfFile.name)}-jpg.zip`);resultBox.innerHTML=`${card('Páginas convertidas',int(generated.length),'JPG a escala 2×')}<p class="suite-result-note">La selección permanece cargada para otra operación.</p>`;
    }
    track('suite_complete',{suite_type:'files',operation:`pdf_${action}`,pages:pages.length});
  }
  async function imageProcess(action){
    if(!imageFiles.length)throw new Error('Selecciona una o varias imágenes.');
    const w=Number(root.querySelector('[name="maxWidth"]').value)||0,h=Number(root.querySelector('[name="maxHeight"]').value)||0,q=(Number(root.querySelector('[name="quality"]').value)||85)/100,format=root.querySelector('[name="imageFormat"]').value;
    const mime=format==='jpeg'?'image/jpeg':format==='png'?'image/png':'image/webp';const ext=format==='jpeg'?'jpg':format;const out=[];let before=0,after=0;let comparison='';
    for(let i=0;i<imageFiles.length;i++){
      const file=imageFiles[i];before+=file.size;const bmp=await createImageBitmap(file);let tw=bmp.width,th=bmp.height;
      if(action==='optimize'&& (w>0||h>0)){const sw=w>0?w/tw:Infinity,sh=h>0?h/th:Infinity,scale=Math.min(1,sw,sh);tw=Math.max(1,Math.round(tw*scale));th=Math.max(1,Math.round(th*scale));}
      const canvas=document.createElement('canvas');canvas.width=tw;canvas.height=th;const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(bmp,0,0,tw,th);bmp.close();const blob=await new Promise(r=>canvas.toBlob(r,mime,format==='png'?undefined:q));after+=blob.size;const suffix=action==='clean'?'limpia':action==='convert'?'convertida':'optimizada';out.push({name:`${cleanBase(file.name)}-${suffix}.${ext}`,blob});
      if(i===0){const original=URL.createObjectURL(file),processed=URL.createObjectURL(blob);comparison=`<div class="image-compare"><figure><img src="${original}" alt="Imagen original"><figcaption>Antes · ${bytes(file.size)}</figcaption></figure><figure><img src="${processed}" alt="Imagen procesada"><figcaption>Después · ${bytes(blob.size)} · ${tw}×${th}</figcaption></figure></div>`;setTimeout(()=>{URL.revokeObjectURL(original);URL.revokeObjectURL(processed);},60000);}
    }
    await zipDownload(out,`imagenes-clicivo-${action}.zip`);const saving=before?(before-after)/before*100:0;resultBox.innerHTML=`<div class="suite-kpi-grid">${card('Archivos',int(out.length),'Procesados en el navegador')}${card('Peso original',bytes(before))}${card('Peso final',bytes(after))}${card('Ahorro',pct(saving))}</div>${comparison}<p class="suite-result-note">Puedes cambiar calidad, dimensiones o formato y volver a procesar el mismo lote sin seleccionarlo otra vez.</p>`;track('suite_complete',{suite_type:'files',operation:`image_${action}`,files:out.length});
  }
  function initFilesSuite(){
    const pdfInput=root.querySelector('[name="pdfFile"]'),imgInput=root.querySelector('[name="imageFiles"]');
    pdfInput?.addEventListener('change',async()=>{pdfFile=pdfInput.files[0]||null;pdfPageCount=null;renderFileStatus();if(pdfFile){track('file_upload',{file_type:'pdf',files:1,total_size:pdfFile.size});try{if(window.PDFLib){const doc=await PDFLib.PDFDocument.load(await pdfFile.arrayBuffer(),{ignoreEncryption:false});pdfPageCount=doc.getPageCount();renderFileStatus();}}catch{pdfPageCount=null;renderFileStatus();}}});
    imgInput?.addEventListener('change',()=>{imageFiles=[...imgInput.files];renderFileStatus();if(imageFiles.length)track('file_upload',{file_type:'image',files:imageFiles.length,total_size:imageFiles.reduce((s,f)=>s+f.size,0)});});
    root.addEventListener('click',async e=>{
      try{errorBox.textContent='';const p=e.target.closest('[data-pdf-action]');if(p){if(firstInteraction){firstInteraction=false;track('suite_start',{suite_type:'files'});}await pdfExtract(p.dataset.pdfAction);}const im=e.target.closest('[data-image-action]');if(im){if(firstInteraction){firstInteraction=false;track('suite_start',{suite_type:'files'});}await imageProcess(im.dataset.imageAction);}}
      catch(err){errorBox.textContent=err.message||'No se ha podido procesar el archivo.';track('suite_error',{suite_type:'files',message:(err.message||'').slice(0,90)});}
    });
    renderFileStatus();
  }

  track('suite_view');
  if (suite === 'creadores') initFormSuite('creators', calculateCreators);
  else if (suite === 'laboral') initFormSuite('labor', calculateLabor);
  else if (suite === 'documentos') initFilesSuite();
})();
