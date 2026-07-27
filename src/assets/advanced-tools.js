(() => {
  'use strict';

  const ADVANCED_IDS = new Set([
    'pdf-merge','pdf-split','pdf-organize','images-to-pdf','pdf-to-jpg',
    'image-compress','image-resize','image-convert','image-crop','remove-exif',
    'word-counter','case-converter','text-diff','qr-generator','wifi-qr',
  ]);

  const form = document.querySelector('.tool-form');
  const output = document.querySelector('#result-body');
  if (!form || !output || !ADVANCED_IDS.has(form.dataset.tool)) return;
  const id = form.dataset.tool;
  const errorBox = form.querySelector('.error-message');
  const fileState = new Map();
  let organizeState = null;
  let cropState = null;

  const nf = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 2 });
  const n0 = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 });
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const item = (label, value) => `<div class="result-item"><span>${label}</span><b>${value}</b></div>`;
  const hero = (label, value) => `<div class="result-hero"><span>${label}</span><strong>${value}</strong></div>`;
  const note = (text) => `<p class="result-note">${text}</p>`;
  const result = (label, value, items = [], noteText = '', extra = '') => `${hero(label, value)}<div class="result-grid">${items.join('')}</div>${extra}${noteText ? note(noteText) : ''}`;
  const bytes = (size) => {
    const units = ['B','KB','MB','GB']; let n = Number(size) || 0; let i = 0;
    while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
    return `${nf.format(n)} ${units[i]}`;
  };
  const cleanBase = (name) => String(name || 'archivo').replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]+/g, '-').replace(/^-+|-+$/g, '') || 'archivo';
  const extensionFor = (mime) => ({'image/jpeg':'jpg','image/png':'png','image/webp':'webp','application/pdf':'pdf'}[mime] || 'bin');
  const setError = (message = '') => { errorBox.textContent = message; };
  const setOutput = (html) => { output.innerHTML = html; output.classList.remove('result-placeholder'); };
  const placeholder = (text = 'Completa los campos para ver el resultado.') => { output.className = 'result-placeholder'; output.textContent = text; };
  const setBusy = (busy, label = 'Procesando…') => {
    form.querySelectorAll('button').forEach(btn => {
      if (!btn.dataset.originalText) btn.dataset.originalText = btn.textContent;
      btn.disabled = busy;
      if (busy && btn.type === 'submit') btn.textContent = label;
      if (!busy) btn.textContent = btn.dataset.originalText;
    });
    form.classList.toggle('is-busy', busy);
  };
  const track = (event, details = {}) => {
    if (window.gtag) window.gtag('event', event, { tool_id: id, page_path: location.pathname, ...details });
  };

  function formValues() {
    const values = {};
    form.querySelectorAll('input,select,textarea').forEach(el => {
      if (!el.name || el.type === 'file') return;
      if (el.type === 'checkbox') values[el.name] = el.checked;
      else if (['number','range'].includes(el.type)) values[el.name] = Number(el.value);
      else values[el.name] = el.value;
    });
    return values;
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = filename; link.style.display = 'none';
    document.body.appendChild(link); link.click(); link.remove();
    track('file_download', { file_name: filename.slice(0, 90), file_size: blob.size || 0 });
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  async function downloadFiles(files, zipName, forceZip = false) {
    if (!files.length) throw new Error('No se ha generado ningún archivo.');
    if (files.length === 1 && !forceZip) {
      downloadBlob(files[0].blob, files[0].name); return;
    }
    if (!window.JSZip) throw new Error('No se ha podido cargar el componente ZIP. Recarga la página e inténtalo de nuevo.');
    const zip = new JSZip();
    files.forEach(file => zip.file(file.name, file.blob));
    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } });
    downloadBlob(blob, zipName);
  }

  function getFiles(name) {
    if (fileState.has(name)) return [...fileState.get(name)];
    return [...(form.elements[name]?.files || [])];
  }

  function renderFileSelection(input) {
    const name = input.name;
    const files = getFiles(name);
    const box = form.querySelector(`[data-file-selection="${CSS.escape(name)}"]`);
    if (!box) return;
    if (!files.length) { box.innerHTML = 'Ningún archivo seleccionado.'; return; }
    const reorder = input.multiple && ['pdf-merge','images-to-pdf'].includes(id);
    box.innerHTML = `<div class="selected-files">${files.map((file, index) => `
      <div class="selected-file" data-file-index="${index}">
        <span><b>${escapeHtml(file.name)}</b><small>${bytes(file.size)}</small></span>
        <span class="file-actions">
          ${reorder ? `<button type="button" data-file-action="up" aria-label="Subir ${escapeHtml(file.name)}">↑</button><button type="button" data-file-action="down" aria-label="Bajar ${escapeHtml(file.name)}">↓</button>` : ''}
          ${input.multiple ? `<button type="button" data-file-action="remove" aria-label="Eliminar ${escapeHtml(file.name)}">×</button>` : ''}
        </span>
      </div>`).join('')}</div>`;
  }

  function setFiles(input, files) {
    const accepted = [...files].filter(file => {
      if (input.accept.includes('pdf')) return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      if (input.accept.includes('image')) return file.type.startsWith('image/');
      return true;
    });
    const selected = input.multiple ? accepted : accepted.slice(0,1);
    fileState.set(input.name, selected);
    renderFileSelection(input);
    if (selected.length) track('file_upload', { files: selected.length, total_size: selected.reduce((sum,file)=>sum+(file.size||0),0) });
  }

  function initFileInputs() {
    form.querySelectorAll('input[type="file"]').forEach(input => {
      input.addEventListener('change', () => {
        setFiles(input, input.files);
        if (id === 'pdf-organize') loadOrganizerPreview().catch(showError);
        if (id === 'image-crop') loadCropPreview().catch(showError);
      });
      const drop = input.closest('.file-drop');
      if (drop) {
        ['dragenter','dragover'].forEach(type => drop.addEventListener(type, event => { event.preventDefault(); drop.classList.add('dragging'); }));
        ['dragleave','drop'].forEach(type => drop.addEventListener(type, event => { event.preventDefault(); drop.classList.remove('dragging'); }));
        drop.addEventListener('drop', event => {
          setFiles(input, event.dataTransfer.files);
          if (id === 'pdf-organize') loadOrganizerPreview().catch(showError);
          if (id === 'image-crop') loadCropPreview().catch(showError);
        });
      }
      renderFileSelection(input);
    });
    form.addEventListener('click', event => {
      const button = event.target.closest('[data-file-action]');
      if (!button) return;
      const row = button.closest('[data-file-index]');
      const input = form.querySelector('input[type="file"][multiple]');
      if (!row || !input) return;
      const files = getFiles(input.name); const index = Number(row.dataset.fileIndex);
      if (button.dataset.fileAction === 'remove') files.splice(index,1);
      if (button.dataset.fileAction === 'up' && index > 0) [files[index-1],files[index]] = [files[index],files[index-1]];
      if (button.dataset.fileAction === 'down' && index < files.length-1) [files[index+1],files[index]] = [files[index],files[index+1]];
      fileState.set(input.name, files); renderFileSelection(input);
    });
  }

  function showError(error) {
    console.error(error);
    const message = error?.message || 'No se ha podido completar la operación. Revisa los archivos y vuelve a intentarlo.';
    setError(message);
    track('tool_error', { error_message: message.slice(0,100) });
    setBusy(false);
  }

  function requireFiles(name, minimum = 1) {
    const files = getFiles(name);
    if (files.length < minimum) throw new Error(minimum > 1 ? `Selecciona al menos ${minimum} archivos.` : 'Selecciona un archivo.');
    return files;
  }

  function parsePageGroups(text, count) {
    const raw = String(text || '').trim().toLowerCase();
    if (!raw || raw === 'todas' || raw === 'todo' || raw === 'all') return [Array.from({length:count},(_,i)=>i)];
    return raw.split(',').map(part => {
      const token = part.trim();
      if (!token) throw new Error('Revisa los rangos: hay un bloque vacío.');
      const match = token.match(/^(\d+)\s*-\s*(\d+)$/);
      let pages;
      if (match) {
        const a=Number(match[1]), b=Number(match[2]);
        if (a > b) throw new Error(`El rango ${token} está invertido.`);
        pages=Array.from({length:b-a+1},(_,i)=>a+i);
      } else if (/^\d+$/.test(token)) pages=[Number(token)];
      else throw new Error(`No se entiende el rango «${token}». Usa ejemplos como 1-3, 5, 8-10.`);
      pages.forEach(page => { if (page < 1 || page > count) throw new Error(`La página ${page} no existe. El PDF tiene ${count} páginas.`); });
      return pages.map(page => page-1);
    });
  }

  function uniquePageSelection(text, count) {
    const groups=parsePageGroups(text,count); const seen=new Set(); const result=[];
    groups.flat().forEach(page => { if (!seen.has(page)) { seen.add(page); result.push(page); } });
    return result;
  }

  async function mergePdf() {
    const files=requireFiles('files',2);
    if (!window.PDFLib) throw new Error('No se ha podido cargar el motor PDF. Recarga la página.');
    const out=await PDFLib.PDFDocument.create(); let pages=0;
    for (const file of files) {
      const doc=await PDFLib.PDFDocument.load(await file.arrayBuffer());
      const copied=await out.copyPages(doc,doc.getPageIndices()); copied.forEach(page=>out.addPage(page)); pages+=copied.length;
    }
    out.setTitle('PDF unido con Clicivo'); out.setCreator('Clicivo');
    const data=await out.save(); const blob=new Blob([data],{type:'application/pdf'});
    downloadBlob(blob,'pdf-unido-clicivo.pdf');
    setOutput(result('PDF unido',`${n0.format(pages)} páginas`,[item('Archivos combinados',n0.format(files.length)),item('Tamaño final',bytes(blob.size)),item('Calidad','Contenido original'),item('Procesamiento','Local')],'El archivo se ha generado y descargado.'));
    track('tool_complete',{files:files.length,pages});
  }

  async function splitPdf() {
    const file=requireFiles('file')[0]; const v=formValues();
    if (!window.PDFLib || !window.JSZip) throw new Error('No se han podido cargar los componentes PDF y ZIP. Recarga la página.');
    const source=await PDFLib.PDFDocument.load(await file.arrayBuffer()); const count=source.getPageCount();
    const groups=v.mode==='each' ? Array.from({length:count},(_,i)=>[i]) : parsePageGroups(v.ranges,count);
    if (groups.length > 250) throw new Error('Este PDF generaría más de 250 archivos. Divide la operación en varios lotes.');
    const generated=[];
    for (let i=0;i<groups.length;i++) {
      const doc=await PDFLib.PDFDocument.create(); const copied=await doc.copyPages(source,groups[i]); copied.forEach(p=>doc.addPage(p));
      const data=await doc.save(); const label=groups[i].length===1 ? `pagina-${groups[i][0]+1}` : `paginas-${groups[i][0]+1}-${groups[i][groups[i].length-1]+1}`;
      generated.push({name:`${cleanBase(file.name)}-${label}.pdf`,blob:new Blob([data],{type:'application/pdf'})});
    }
    await downloadFiles(generated,`${cleanBase(file.name)}-dividido.zip`,true);
    setOutput(result('PDF dividido',`${n0.format(generated.length)} archivos`,[item('Páginas originales',n0.format(count)),item('Modo',v.mode==='each'?'Una por archivo':'Rangos'),item('Descarga','ZIP'),item('Procesamiento','Local')],'La descarga incluye todos los PDF generados.'));
    track('tool_complete',{files:generated.length,pages:count});
  }

  async function getPdfJsDocument(file) {
    if (!window.pdfjsLib) throw new Error('No se ha podido cargar el visor PDF. Recarga la página.');
    pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    const bytes=new Uint8Array(await file.arrayBuffer());
    return {bytes,doc:await pdfjsLib.getDocument({data:bytes.slice()}).promise};
  }

  async function loadOrganizerPreview() {
    const files=getFiles('file'); if (!files.length) { organizeState=null; placeholder('Selecciona un PDF para ver sus páginas.'); return; }
    setError(''); setBusy(true,'Preparando páginas…');
    const {bytes:raw,doc}=await getPdfJsDocument(files[0]);
    if (doc.numPages > 200) throw new Error('El organizador admite hasta 200 páginas por operación para proteger la memoria del navegador.');
    const pages=[];
    setOutput(`${hero('Preparando vista previa',`${doc.numPages} páginas`)}${note('Generando miniaturas…')}`);
    for (let i=1;i<=doc.numPages;i++) {
      const page=await doc.getPage(i); const first=page.getViewport({scale:1}); const scale=Math.min(.32,150/first.width); const viewport=page.getViewport({scale});
      const canvas=document.createElement('canvas'); canvas.width=Math.ceil(viewport.width); canvas.height=Math.ceil(viewport.height);
      await page.render({canvasContext:canvas.getContext('2d'),viewport}).promise;
      pages.push({original:i-1,rotation:0,thumb:canvas.toDataURL('image/jpeg',.75)});
    }
    organizeState={file:files[0],raw,pages}; renderOrganizer(); setBusy(false);
  }

  function renderOrganizer() {
    if (!organizeState) return;
    setOutput(`${hero('Páginas activas',n0.format(organizeState.pages.length))}<p class="result-note">Arrastra las tarjetas para reordenar. Usa los botones para girar o eliminar.</p><div class="page-organizer">${organizeState.pages.map((page,index)=>`<article class="page-card" draggable="true" data-page-position="${index}"><div class="page-thumb-wrap"><img src="${page.thumb}" alt="Vista previa página ${page.original+1}" style="transform:rotate(${page.rotation}deg)"></div><b>Página ${page.original+1}</b><div class="page-actions"><button type="button" data-page-action="left" aria-label="Girar a la izquierda">↺</button><button type="button" data-page-action="right" aria-label="Girar a la derecha">↻</button><button type="button" data-page-action="delete" aria-label="Eliminar página">×</button></div></article>`).join('')}</div>${note('El orden mostrado será el orden del PDF exportado.')}`);
  }

  function initOrganizerEvents() {
    let dragged=null;
    output.addEventListener('dragstart',event=>{ const card=event.target.closest('.page-card'); if(card) dragged=Number(card.dataset.pagePosition); });
    output.addEventListener('dragover',event=>{ if(event.target.closest('.page-card')) event.preventDefault(); });
    output.addEventListener('drop',event=>{
      const card=event.target.closest('.page-card'); if(!card||dragged===null||!organizeState)return; event.preventDefault();
      const target=Number(card.dataset.pagePosition); const [moved]=organizeState.pages.splice(dragged,1); organizeState.pages.splice(target,0,moved); dragged=null; renderOrganizer();
    });
    output.addEventListener('click',event=>{
      const btn=event.target.closest('[data-page-action]'); if(!btn||!organizeState)return;
      const card=btn.closest('.page-card'); const index=Number(card.dataset.pagePosition); const action=btn.dataset.pageAction;
      if(action==='delete') organizeState.pages.splice(index,1);
      if(action==='left') organizeState.pages[index].rotation=(organizeState.pages[index].rotation+270)%360;
      if(action==='right') organizeState.pages[index].rotation=(organizeState.pages[index].rotation+90)%360;
      renderOrganizer();
    });
  }

  async function exportOrganizer() {
    if (!organizeState) throw new Error('Selecciona y prepara un PDF primero.');
    if (!organizeState.pages.length) throw new Error('Debe quedar al menos una página.');
    if (!window.PDFLib) throw new Error('No se ha podido cargar el motor PDF.');
    const source=await PDFLib.PDFDocument.load(organizeState.raw.slice().buffer); const out=await PDFLib.PDFDocument.create();
    for (const entry of organizeState.pages) {
      const [page]=await out.copyPages(source,[entry.original]); const originalAngle=page.getRotation().angle || 0;
      page.setRotation(PDFLib.degrees((originalAngle+entry.rotation)%360)); out.addPage(page);
    }
    const data=await out.save(); const blob=new Blob([data],{type:'application/pdf'}); downloadBlob(blob,`${cleanBase(organizeState.file.name)}-organizado.pdf`);
    setOutput(result('PDF organizado',`${organizeState.pages.length} páginas`,[item('Archivo',escapeHtml(organizeState.file.name)),item('Tamaño final',bytes(blob.size)),item('Páginas eliminadas',n0.format((await source.getPageCount())-organizeState.pages.length)),item('Procesamiento','Local')],'El PDF organizado se ha descargado.'));
    track('tool_complete',{pages:organizeState.pages.length});
  }

  function decodeImage(file) {
    return new Promise(async (resolve,reject)=>{
      try {
        if ('createImageBitmap' in window) {
          try { const bitmap=await createImageBitmap(file,{imageOrientation:'from-image'}); resolve({source:bitmap,width:bitmap.width,height:bitmap.height,close:()=>bitmap.close()}); return; } catch (_) {}
        }
        const url=URL.createObjectURL(file); const img=new Image();
        img.onload=()=>resolve({source:img,width:img.naturalWidth,height:img.naturalHeight,close:()=>URL.revokeObjectURL(url)});
        img.onerror=()=>{URL.revokeObjectURL(url);reject(new Error(`No se puede abrir ${file.name}.`));}; img.src=url;
      } catch(error){reject(error);}
    });
  }

  function canvasBlob(canvas,mime,quality=.9) {
    return new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('El navegador no ha podido crear la imagen.')),mime,quality));
  }

  function mimeFor(format,file) {
    if (format==='same') return ['image/jpeg','image/png','image/webp'].includes(file.type) ? file.type : 'image/png';
    return `image/${format}`;
  }

  function createCanvas(width,height,mime) {
    const canvas=document.createElement('canvas'); canvas.width=Math.max(1,Math.round(width)); canvas.height=Math.max(1,Math.round(height));
    const ctx=canvas.getContext('2d',{alpha:mime!=='image/jpeg'});
    if(mime==='image/jpeg'){ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);}
    return {canvas,ctx};
  }

  async function imagesToPdf() {
    const files=requireFiles('files'); const v=formValues();
    if (!window.PDFLib) throw new Error('No se ha podido cargar el motor PDF.');
    const pdf=await PDFLib.PDFDocument.create(); const margin=v.margin*72/25.4;
    for (const file of files) {
      const img=await decodeImage(file);
      try {
        const {canvas,ctx}=createCanvas(img.width,img.height,file.type==='image/png'?'image/png':'image/jpeg'); ctx.drawImage(img.source,0,0);
        const usePng=file.type==='image/png'; const blob=await canvasBlob(canvas,usePng?'image/png':'image/jpeg',.92); const embedded=usePng?await pdf.embedPng(await blob.arrayBuffer()):await pdf.embedJpg(await blob.arrayBuffer());
        let pageW,pageH;
        if(v.pageSize==='a4'){pageW=595.28;pageH=841.89;} else if(v.pageSize==='letter'){pageW=612;pageH=792;} else {pageW=img.width*.75+margin*2;pageH=img.height*.75+margin*2;}
        if(v.orientation==='landscape'&&pageH>pageW)[pageW,pageH]=[pageH,pageW];
        if(v.orientation==='portrait'&&pageW>pageH)[pageW,pageH]=[pageH,pageW];
        const page=pdf.addPage([pageW,pageH]); const maxW=Math.max(1,pageW-margin*2),maxH=Math.max(1,pageH-margin*2); const scale=Math.min(maxW/embedded.width,maxH/embedded.height);
        const width=embedded.width*scale,height=embedded.height*scale; page.drawImage(embedded,{x:(pageW-width)/2,y:(pageH-height)/2,width,height});
      } finally { img.close(); }
    }
    const data=await pdf.save(); const blob=new Blob([data],{type:'application/pdf'}); downloadBlob(blob,'imagenes-clicivo.pdf');
    setOutput(result('PDF creado',`${files.length} páginas`,[item('Imágenes',n0.format(files.length)),item('Tamaño',bytes(blob.size)),item('Página',v.pageSize.toUpperCase()),item('Procesamiento','Local')],'Las imágenes se han convertido y descargado como PDF.'));
    track('tool_complete',{files:files.length});
  }

  async function pdfToJpg() {
    const file=requireFiles('file')[0]; const v=formValues(); const {doc}=await getPdfJsDocument(file);
    const pages=uniquePageSelection(v.pages,doc.numPages); if(pages.length>100)throw new Error('Convierte un máximo de 100 páginas por operación.');
    const generated=[];
    for(let i=0;i<pages.length;i++){
      const pageNumber=pages[i]+1; const page=await doc.getPage(pageNumber); const viewport=page.getViewport({scale:Number(v.scale)}); const {canvas,ctx}=createCanvas(viewport.width,viewport.height,'image/jpeg');
      await page.render({canvasContext:ctx,viewport}).promise; const blob=await canvasBlob(canvas,'image/jpeg',v.quality/100);
      generated.push({name:`${cleanBase(file.name)}-pagina-${pageNumber}.jpg`,blob});
      setOutput(`${hero('Convirtiendo',`${i+1} / ${pages.length}`)}${note(`Procesando página ${pageNumber}.`)}`);
    }
    await downloadFiles(generated,`${cleanBase(file.name)}-jpg.zip`,generated.length>1);
    const total=generated.reduce((sum,f)=>sum+f.blob.size,0);
    setOutput(result('Conversión completada',`${generated.length} imágenes`,[item('Páginas del PDF',n0.format(doc.numPages)),item('Páginas convertidas',n0.format(generated.length)),item('Peso total',bytes(total)),item('Resolución',`${v.scale}×`)],'Las páginas convertidas se han descargado.'));
    track('tool_complete',{pages:generated.length});
  }

  async function processImageBatch(mode) {
    const files=requireFiles('files'); const v=formValues(); const generated=[]; const rows=[];
    for(let i=0;i<files.length;i++){
      const file=files[i]; const img=await decodeImage(file);
      try {
        const mime=mimeFor(v.format,file); let width=img.width,height=img.height;
        if(mode==='compress'&&v.maxDimension>0&&Math.max(width,height)>v.maxDimension){const scale=v.maxDimension/Math.max(width,height);width*=scale;height*=scale;}
        if(mode==='resize'){
          if(v.maxWidth<=0&&v.maxHeight<=0)throw new Error('Indica un ancho máximo, un alto máximo o ambos.');
          const scaleW=v.maxWidth>0?v.maxWidth/width:Infinity,scaleH=v.maxHeight>0?v.maxHeight/height:Infinity; let scale=Math.min(scaleW,scaleH);
          if(!v.upscale)scale=Math.min(1,scale); width*=scale;height*=scale;
        }
        const {canvas,ctx}=createCanvas(width,height,mime); ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(img.source,0,0,canvas.width,canvas.height);
        const blob=await canvasBlob(canvas,mime,(v.quality||90)/100); const suffix=mode==='compress'?'comprimida':mode==='resize'?'redimensionada':mode==='convert'?'convertida':'sin-metadatos';
        const name=`${cleanBase(file.name)}-${suffix}.${extensionFor(mime)}`; generated.push({name,blob});
        const saving=file.size?((file.size-blob.size)/file.size*100):0; rows.push([escapeHtml(file.name),`${canvas.width}×${canvas.height}`,bytes(file.size),bytes(blob.size),`${nf.format(saving)} %`]);
        setOutput(`${hero('Procesando',`${i+1} / ${files.length}`)}${note(escapeHtml(file.name))}`);
      } finally {img.close();}
    }
    await downloadFiles(generated,`imagenes-${mode}-clicivo.zip`,generated.length>1);
    const totalBefore=files.reduce((s,f)=>s+f.size,0),totalAfter=generated.reduce((s,f)=>s+f.blob.size,0),saving=totalBefore?(totalBefore-totalAfter)/totalBefore*100:0;
    const table=`<div class="table-scroll"><table class="data-table"><thead><tr><th>Archivo</th><th>Dimensiones</th><th>Original</th><th>Resultado</th><th>Ahorro</th></tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    setOutput(result('Imágenes procesadas',n0.format(generated.length),[item('Peso original',bytes(totalBefore)),item('Peso final',bytes(totalAfter)),item('Variación',`${nf.format(saving)} %`),item('Procesamiento','Local')],'Los archivos se han descargado.',table));
    track('tool_complete',{files:files.length,mode});
  }

  function cropGeometry(img,v) {
    const ratios={'1:1':1,'4:5':4/5,'16:9':16/9,'9:16':9/16}; const target=ratios[v.aspect]||img.width/img.height;
    let baseW=img.width,baseH=baseW/target; if(baseH>img.height){baseH=img.height;baseW=baseH*target;}
    const factor=Math.max(1,v.zoom/100); const w=baseW/factor,h=baseH/factor; const sx=(img.width-w)*(v.positionX/100),sy=(img.height-h)*(v.positionY/100);
    return {sx,sy,w,h,target};
  }

  async function loadCropPreview() {
    const files=getFiles('file'); if(!files.length){cropState=null;placeholder('Selecciona una imagen para ver la vista previa.');return;}
    cropState?.image?.close?.(); const image=await decodeImage(files[0]); cropState={file:files[0],image}; renderCropPreview();
  }

  function renderCropPreview() {
    if(!cropState)return; const v=formValues(); const g=cropGeometry(cropState.image,v); const max=560; let width=max,height=max/g.target;
    if(height>520){height=520;width=height*g.target;}
    const {canvas,ctx}=createCanvas(width,height,'image/jpeg'); ctx.drawImage(cropState.image.source,g.sx,g.sy,g.w,g.h,0,0,canvas.width,canvas.height);
    setOutput(`${hero('Vista previa',`${n0.format(g.w)} × ${n0.format(g.h)} px`)}<canvas class="crop-preview" width="${canvas.width}" height="${canvas.height}"></canvas>${note('Ajusta zoom y posición. La descarga utiliza la resolución disponible del recorte.')}`);
    output.querySelector('.crop-preview').getContext('2d').drawImage(canvas,0,0);
  }

  async function exportCrop() {
    if(!cropState)throw new Error('Selecciona una imagen.'); const v=formValues(); const g=cropGeometry(cropState.image,v); const maxDim=5000; const scale=Math.min(1,maxDim/Math.max(g.w,g.h));
    const mime=`image/${v.format}`; const {canvas,ctx}=createCanvas(g.w*scale,g.h*scale,mime);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(cropState.image.source,g.sx,g.sy,g.w,g.h,0,0,canvas.width,canvas.height);
    const blob=await canvasBlob(canvas,mime,v.quality/100); const name=`${cleanBase(cropState.file.name)}-recortada.${extensionFor(mime)}`;downloadBlob(blob,name);
    setOutput(result('Imagen recortada',`${canvas.width} × ${canvas.height} px`,[item('Formato',extensionFor(mime).toUpperCase()),item('Tamaño',bytes(blob.size)),item('Proporción',v.aspect==='free'?'Original':v.aspect),item('Procesamiento','Local')],'La imagen recortada se ha descargado.'));
    track('tool_complete',{width:canvas.width,height:canvas.height});
  }

  function wordsIn(text) { return String(text||'').match(/[\p{L}\p{N}]+(?:['’\-][\p{L}\p{N}]+)*/gu)||[]; }
  function renderWordCounter() {
    const text=form.elements.text.value||''; const words=wordsIn(text); const chars=[...text].length,charsNoSpaces=[...text.replace(/\s/g,'')].length;
    const sentences=(text.match(/[^.!?…]+[.!?…]+|[^.!?…]+$/g)||[]).filter(s=>s.trim()).length; const paragraphs=text.trim()?text.trim().split(/\n\s*\n/).length:0; const lines=text?text.split(/\r?\n/).length:0;
    const stop=new Set(['de','la','el','y','en','a','los','las','un','una','que','por','para','con','del','se','al','es','lo','su','sus','o','como','más','mi','tu']); const freq=new Map();
    words.map(w=>w.toLocaleLowerCase('es-ES')).filter(w=>w.length>2&&!stop.has(w)).forEach(w=>freq.set(w,(freq.get(w)||0)+1));
    const top=[...freq.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,6);
    const extra=top.length?`<div class="keyword-chips">${top.map(([w,c])=>`<span>${escapeHtml(w)} <b>${c}</b></span>`).join('')}</div>`:'';
    setOutput(result('Palabras',n0.format(words.length),[item('Caracteres',n0.format(chars)),item('Sin espacios',n0.format(charsNoSpaces)),item('Frases',n0.format(sentences)),item('Párrafos',n0.format(paragraphs)),item('Líneas',n0.format(lines)),item('Lectura estimada',`${nf.format(words.length/200)} min`),item('Locución estimada',`${nf.format(words.length/130)} min`),item('Media por frase',sentences?nf.format(words.length/sentences):'0')],'Referencia: 200 palabras/minuto para lectura y 130 para locución.',extra));
  }

  function transformCase(text,mode) {
    if(mode==='upper')return text.toLocaleUpperCase('es-ES'); if(mode==='lower')return text.toLocaleLowerCase('es-ES');
    if(mode==='title')return text.toLocaleLowerCase('es-ES').replace(/(^|[\s\-–—([{¿¡])([\p{L}\p{N}])/gu,(m,p,c)=>p+c.toLocaleUpperCase('es-ES'));
    if(mode==='sentence')return text.toLocaleLowerCase('es-ES').replace(/(^|[.!?…]\s+)([\p{L}])/gu,(m,p,c)=>p+c.toLocaleUpperCase('es-ES'));
    let upper=false;return [...text].map(ch=>/\p{L}/u.test(ch)?((upper=!upper)?ch.toLocaleUpperCase('es-ES'):ch.toLocaleLowerCase('es-ES')):ch).join('');
  }

  function renderCaseConverter() {
    const v=formValues(); const converted=transformCase(v.text||'',v.mode);
    setOutput(`${hero('Resultado',`${[...converted].length} caracteres`)}<textarea class="text-output" id="case-output" readonly>${escapeHtml(converted)}</textarea><div class="form-actions"><button class="btn btn-primary" type="button" data-copy-target="case-output">Copiar texto</button><button class="btn btn-secondary" type="button" data-download-text="case-output">Descargar TXT</button></div>${note('Revisa nombres propios, siglas y criterios editoriales antes de publicar.')}`);
  }

  function lineDiff(a,b) {
    const A=a.replace(/\r/g,'').split('\n'),B=b.replace(/\r/g,'').split('\n');
    if(A.length>600||B.length>600){const max=Math.max(A.length,B.length);return Array.from({length:max},(_,i)=>A[i]===B[i]?['same',A[i]??'']:A[i]===undefined?['add',B[i]]:B[i]===undefined?['remove',A[i]]:[ 'remove',A[i], 'paired', B[i] ]).flatMap(x=>x[2]==='paired'?[['remove',x[1]],['add',x[3]]]:[x]);}
    const dp=Array.from({length:A.length+1},()=>new Uint16Array(B.length+1));
    for(let i=A.length-1;i>=0;i--)for(let j=B.length-1;j>=0;j--)dp[i][j]=A[i]===B[j]?dp[i+1][j+1]+1:Math.max(dp[i+1][j],dp[i][j+1]);
    const out=[];let i=0,j=0;while(i<A.length||j<B.length){if(i<A.length&&j<B.length&&A[i]===B[j]){out.push(['same',A[i]]);i++;j++;}else if(j<B.length&&(i===A.length||dp[i][j+1]>=dp[i+1][j])){out.push(['add',B[j++]]);}else{out.push(['remove',A[i++]]);}}return out;
  }

  function renderTextDiff() {
    const v=formValues(); const diff=lineDiff(v.original||'',v.revised||''); const counts={add:0,remove:0,same:0}; diff.forEach(([type])=>counts[type]++);
    const lines=diff.map(([type,text])=>`<div class="diff-line diff-${type}"><span>${type==='add'?'+':type==='remove'?'−':' '}</span><code>${escapeHtml(text)||'&nbsp;'}</code></div>`).join('');
    setOutput(result('Diferencias',n0.format(counts.add+counts.remove),[item('Líneas añadidas',n0.format(counts.add)),item('Líneas eliminadas',n0.format(counts.remove)),item('Sin cambios',n0.format(counts.same)),item('Método','Comparación por líneas')],'Verde indica contenido añadido y rojo contenido eliminado.',`<div class="diff-view">${lines}</div>`));
    track('tool_complete',{added:counts.add,removed:counts.remove});
  }

  function qrLevel(level) { return window.QRCode?.CorrectLevel?.[level] ?? window.QRCode?.CorrectLevel?.M; }
  function luminance(hex){const rgb=hex.replace('#','').match(/.{2}/g).map(x=>parseInt(x,16)/255).map(c=>c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4));return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];}
  function contrast(a,b){const l1=luminance(a),l2=luminance(b);return (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);}

  function renderQr(content,v,label='Código QR') {
    if(!window.QRCode)throw new Error('No se ha podido cargar el generador QR. Recarga la página.'); if(!content.trim())throw new Error('Introduce contenido para el código QR.');
    const ratio=contrast(v.foreground,v.background); setOutput(`${hero(label,`${v.size} × ${v.size} px`)}<div class="qr-stage"><div id="qr-output"></div></div><div class="form-actions"><button class="btn btn-primary" type="button" id="download-qr">Descargar PNG</button></div>${note(`${ratio<4.5?'⚠ Contraste bajo. Usa colores más diferentes.':'Contraste adecuado.'} Prueba el QR antes de imprimirlo.`)}`);
    new QRCode(output.querySelector('#qr-output'),{text:content,width:v.size,height:v.size,colorDark:v.foreground,colorLight:v.background,correctLevel:qrLevel(v.level||'M')});
    output.querySelector('#download-qr').addEventListener('click',()=>{
      const canvas=output.querySelector('#qr-output canvas'),img=output.querySelector('#qr-output img');
      if(canvas)canvas.toBlob(blob=>downloadBlob(blob,'codigo-qr-clicivo.png'),'image/png'); else if(img){const a=document.createElement('a');a.href=img.src;a.download='codigo-qr-clicivo.png';a.click();}
    });
    track('tool_complete',{type:id});
  }

  function escapeWifi(value){return String(value||'').replace(/([\\;,:"])/g,'\\$1');}

  async function runTool(event) {
    event?.preventDefault(); setError(''); setBusy(true);
    try {
      if(id==='pdf-merge')await mergePdf();
      else if(id==='pdf-split')await splitPdf();
      else if(id==='pdf-organize')await exportOrganizer();
      else if(id==='images-to-pdf')await imagesToPdf();
      else if(id==='pdf-to-jpg')await pdfToJpg();
      else if(id==='image-compress')await processImageBatch('compress');
      else if(id==='image-resize')await processImageBatch('resize');
      else if(id==='image-convert')await processImageBatch('convert');
      else if(id==='remove-exif')await processImageBatch('exif');
      else if(id==='image-crop')await exportCrop();
      else if(id==='text-diff')renderTextDiff();
      else if(id==='qr-generator'){const v=formValues();renderQr(v.content,v);}
      else if(id==='wifi-qr'){const v=formValues();if(!v.ssid.trim())throw new Error('Introduce el nombre de la red.');if(v.security!=='nopass'&&!v.password)throw new Error('Introduce la contraseña o selecciona una red sin contraseña.');const code=`WIFI:T:${v.security};S:${escapeWifi(v.ssid)};P:${v.security==='nopass'?'':escapeWifi(v.password)};H:${v.hidden?'true':'false'};;`;renderQr(code,{...v,level:'M'},'QR Wi-Fi');}
    } catch(error){showError(error);} finally {setBusy(false);}
  }

  initFileInputs(); initOrganizerEvents();
  form.addEventListener('submit',runTool);
  form.addEventListener('reset',()=>setTimeout(()=>{
    fileState.clear(); organizeState=null; cropState?.image?.close?.(); cropState=null; setError('');
    form.querySelectorAll('input[type="file"]').forEach(renderFileSelection); placeholder();
    if(id==='word-counter')renderWordCounter(); if(id==='case-converter')renderCaseConverter();
  },0));

  if(id==='word-counter'){form.addEventListener('input',renderWordCounter);renderWordCounter();}
  if(id==='case-converter'){form.addEventListener('input',renderCaseConverter);renderCaseConverter();}
  if(id==='image-crop')form.addEventListener('input',event=>{if(event.target.type!=='file'&&cropState)renderCropPreview();});
  if(['qr-generator','wifi-qr'].includes(id))runTool();
  if(id==='text-diff')renderTextDiff();

  output.addEventListener('click',async event=>{
    const copy=event.target.closest('[data-copy-target]'); if(copy){const target=document.getElementById(copy.dataset.copyTarget);await navigator.clipboard.writeText(target.value||target.textContent);const old=copy.textContent;copy.textContent='Copiado';setTimeout(()=>copy.textContent=old,1200);}
    const download=event.target.closest('[data-download-text]');if(download){const target=document.getElementById(download.dataset.downloadText);downloadBlob(new Blob([target.value||target.textContent],{type:'text/plain;charset=utf-8'}),'texto-clicivo.txt');}
  });
})();
