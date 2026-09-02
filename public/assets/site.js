(() => {
  'use strict';

  const euroFmt = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 });
  const nf = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 2 });
  const n0 = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 });
  const pct = (v) => `${nf.format(v)} %`;
  const money = (v) => euroFmt.format(Number.isFinite(v) ? v : 0);
  const number = (v) => nf.format(Number.isFinite(v) ? v : 0);
  const integer = (v) => n0.format(Number.isFinite(v) ? v : 0);
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const ADVANCED_IDS = new Set(['pdf-merge','pdf-split','pdf-organize','images-to-pdf','pdf-to-jpg','image-compress','image-resize','image-convert','image-crop','remove-exif','word-counter','case-converter','text-diff','qr-generator','wifi-qr']);

  const menuButton = document.querySelector('.menu-button');
  const nav = document.querySelector('.nav');
  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }

  function initCatalog() {
    const search = document.querySelector('.catalog-search');
    const cards = [...document.querySelectorAll('.tool-card[data-search]')];
    const filters = [...document.querySelectorAll('.filter[data-filter]')];
    const empty = document.querySelector('.empty-state');
    if (!cards.length) return;
    let active = 'all';
    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      let shown = 0;
      cards.forEach(card => {
        const matchText = !q || card.dataset.search.includes(q);
        const matchCat = active === 'all' || card.dataset.category === active;
        const show = matchText && matchCat;
        card.classList.toggle('hidden', !show);
        if (show) shown++;
      });
      if (empty) empty.style.display = shown ? 'none' : 'block';
    };
    search?.addEventListener('input', apply);
    filters.forEach(btn => btn.addEventListener('click', () => {
      filters.forEach(b => b.classList.remove('active'));
      btn.classList.add('active'); active = btn.dataset.filter; apply();
    }));
    const q = new URLSearchParams(location.search).get('q');
    if (q && search) { search.value = q; apply(); }
  }

  const track = (event, details = {}) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, { page_path: location.pathname, ...details });
    }
  };

  function initAnalyticsInteractions() {
    document.addEventListener('click', event => {
      const affiliate = event.target.closest('[data-affiliate]');
      if (affiliate) track('affiliate_click', { affiliate: affiliate.dataset.affiliate });
      const related = event.target.closest('[data-related-tool]');
      if (related) track('related_tool_click', { target_tool: related.dataset.relatedTool });
      const card = event.target.closest('[data-tool-card]');
      if (card) track('tool_card_click', { target_tool: card.dataset.toolCard });
      const guide = event.target.closest('[data-guide-click]');
      if (guide) track('guide_click', { guide_id: guide.dataset.guideClick });
      const suiteLink = event.target.closest('[data-suite-click],[data-suite-card]');
      if (suiteLink) track('suite_click', { suite_id: suiteLink.dataset.suiteClick || suiteLink.dataset.suiteCard });
    });
    const search = document.querySelector('.catalog-search');
    let timer = null;
    search?.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const term = search.value.trim();
        if (term.length >= 2) track('catalog_search', { search_term: term.slice(0, 80) });
      }, 700);
    });
    document.querySelectorAll('.filter[data-filter]').forEach(button => {
      button.addEventListener('click', () => track('catalog_filter', { filter_name: button.dataset.filter }));
    });
    document.querySelector('[data-home-search]')?.addEventListener('submit', event => {
      const term = event.currentTarget.querySelector('input[name="q"]')?.value?.trim() || '';
      track('home_search_submit', { search_term: term.slice(0,80) });
    });
    document.querySelectorAll('[data-home-quick]').forEach(link => link.addEventListener('click', () => {
      track('home_quick_click', { target_tool: link.dataset.homeQuick });
    }));
  }

  function initScrollDepthAnalytics() {
    if (typeof window.addEventListener !== 'function') return;
    const fired = new Set();
    const check = () => {
      const doc = document.documentElement;
      const max = Math.max(1, doc.scrollHeight - window.innerHeight);
      const pctScrolled = Math.min(100, Math.round(window.scrollY / max * 100));
      [50,90].forEach(mark => {
        if (pctScrolled >= mark && !fired.has(mark)) {
          fired.add(mark);
          track('scroll_depth', { percent: mark });
        }
      });
    };
    window.addEventListener('scroll', check, { passive:true });
  }

  const item = (label, value) => `<div class="result-item"><span>${label}</span><b>${value}</b></div>`;
  const hero = (label, value) => `<div class="result-hero"><span>${label}</span><strong>${value}</strong></div>`;
  const note = (text) => `<p class="result-note">${text}</p>`;
  const result = (label, value, items = [], noteText = '', extra = '') => `${hero(label, value)}<div class="result-grid">${items.join('')}</div>${extra}${noteText ? note(noteText) : ''}`;
  const chart = values => {
    if (!values.length) return '';
    const max = Math.max(...values.map(v => Math.max(0, v)), 1);
    return `<div class="mini-chart" aria-label="Evolución visual">${values.map(v => `<i style="height:${Math.max(3, v / max * 100)}%" title="${money(v)}"></i>`).join('')}</div>`;
  };
  const table = (headers, rows) => `<div style="overflow:auto"><table class="data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;

  function formValues(form) {
    const data = {};
    new FormData(form).forEach((value, key) => { data[key] = value; });
    form.querySelectorAll('input[type="number"], input[type="range"]').forEach(el => { data[el.name] = Number(el.value); });
    form.querySelectorAll('input[type="checkbox"]').forEach(el => { data[el.name] = el.checked; });
    return data;
  }

  function validate(form) {
    const error = form.querySelector('.error-message');
    error.textContent = '';
    for (const el of form.querySelectorAll('[required]')) {
      if (!el.value || (el.type === 'number' && !Number.isFinite(Number(el.value)))) {
        error.textContent = `Revisa el campo «${form.querySelector(`label[for="${el.id}"]`)?.textContent || el.name}».`;
        el.focus(); return false;
      }
      if (el.type === 'number' && el.min !== '' && Number(el.value) < Number(el.min)) {
        error.textContent = `El valor de «${form.querySelector(`label[for="${el.id}"]`)?.textContent || el.name}» es demasiado bajo.`;
        el.focus(); return false;
      }
      if (el.type === 'number' && el.max !== '' && Number(el.value) > Number(el.max)) {
        error.textContent = `El valor de «${form.querySelector(`label[for="${el.id}"]`)?.textContent || el.name}» es demasiado alto.`;
        el.focus(); return false;
      }
    }
    return true;
  }

  function loanPayment(principal, annualRate, months) {
    if (months <= 0) return 0;
    const r = annualRate / 100 / 12;
    if (Math.abs(r) < 1e-12) return principal / months;
    return principal * r / (1 - Math.pow(1 + r, -months));
  }

  function loanSchedule(principal, annualRate, months, paymentOverride = null) {
    const r = annualRate / 100 / 12;
    const scheduled = paymentOverride || loanPayment(principal, annualRate, months);
    let balance = principal, totalInterest = 0, rows = [], m = 0;
    const maxMonths = Math.max(months * 4, 1200);
    while (balance > 0.005 && m < maxMonths) {
      m++;
      const interest = balance * r;
      const payment = Math.min(scheduled, balance + interest);
      const principalPart = payment - interest;
      balance = Math.max(0, balance - principalPart);
      totalInterest += interest;
      rows.push([m, payment, interest, principalPart, balance]);
      if (payment <= interest && balance > 0) break;
    }
    return { months: m, payment: scheduled, interest: totalInterest, rows, balance };
  }

  function simulateCompound(initial, monthly, annualRate, years, timing = 'end') {
    const months = Math.round(years * 12);
    if (annualRate <= -100) throw new Error('La rentabilidad neta debe ser superior a −100 %.');
    const r = Math.pow(1 + annualRate / 100, 1 / 12) - 1;
    let balance = initial; const yearly = [initial];
    for (let m = 1; m <= months; m++) {
      if (timing === 'beginning') balance += monthly;
      balance *= 1 + r;
      if (timing !== 'beginning') balance += monthly;
      if (m % 12 === 0) yearly.push(balance);
    }
    return { balance, yearly };
  }

  function daysBetween(a, b, inclusive = false) {
    const start = new Date(`${a}T00:00:00Z`), end = new Date(`${b}T00:00:00Z`);
    if (!Number.isFinite(start.getTime()) || !Number.isFinite(end.getTime())) return NaN;
    return (end - start) / 86400000 + (inclusive ? 1 : 0);
  }

  function formatMonths(months) {
    months = Math.max(0, Math.round(months));
    const y = Math.floor(months / 12), m = months % 12;
    return [y ? `${y} ${y === 1 ? 'año' : 'años'}` : '', m ? `${m} ${m === 1 ? 'mes' : 'meses'}` : ''].filter(Boolean).join(' y ') || '0 meses';
  }

  function calculate(id, v) {
    switch (id) {
      case 'instagram-growth': {
        if (v.initial <= 0) throw new Error('Los seguidores iniciales deben ser mayores que cero.');
        if (v.days <= 0) throw new Error('El periodo debe ser mayor que cero.');
        const change = v.final - v.initial, growth = change / v.initial * 100, daily = change / v.days;
        const remaining = Math.max(0, Number(v.target || 0) - v.final);
        const daysToTarget = daily > 0 && remaining > 0 ? Math.ceil(remaining / daily) : 0;
        const needed30 = remaining > 0 ? remaining / 30 : 0;
        const needed90 = remaining > 0 ? remaining / 90 : 0;
        const pace30 = remaining <= 0 ? 'Objetivo alcanzado' : daily > 0 ? pct(daily / needed30 * 100) : '0 %';
        const pace90 = remaining <= 0 ? 'Objetivo alcanzado' : daily > 0 ? pct(daily / needed90 * 100) : '0 %';
        let targetValue = 'Sin estimación';
        if (remaining <= 0 && v.target > 0) targetValue = 'Objetivo alcanzado';
        else if (daysToTarget) {
          const date = new Date(); date.setDate(date.getDate() + daysToTarget);
          targetValue = date.toLocaleDateString('es-ES', { day:'2-digit', month:'short', year:'numeric' });
        }
        const rows = [
          ['7 días', `${daily >= 0 ? '+' : ''}${integer(daily * 7)}`, integer(v.final + daily * 7)],
          ['30 días', `${daily >= 0 ? '+' : ''}${integer(daily * 30)}`, integer(v.final + daily * 30)],
          ['90 días', `${daily >= 0 ? '+' : ''}${integer(daily * 90)}`, integer(v.final + daily * 90)],
        ];
        return result('Crecimiento del periodo', pct(growth), [
          item('Cambio neto', `${change >= 0 ? '+' : ''}${integer(change)}`),
          item('Ritmo diario actual', `${number(daily)} seguidores`),
          item('Ritmo necesario para meta en 30 días', remaining > 0 ? `${number(needed30)} seguidores/día` : '—'),
          item('Ritmo necesario para meta en 90 días', remaining > 0 ? `${number(needed90)} seguidores/día` : '—'),
          item('Cobertura del ritmo necesario · 30 días', pace30),
          item('Cobertura del ritmo necesario · 90 días', pace90),
          item('Fecha orientativa del objetivo', targetValue),
          item('Días estimados al objetivo', daysToTarget ? integer(daysToTarget) : '—')
        ], 'La proyección mantiene exactamente el ritmo observado; no contempla campañas, estacionalidad, viralidad ni pérdidas futuras.', table(['Horizonte','Cambio proyectado','Seguidores estimados'], rows));
      }
      case 'instagram-engagement-followers': {
        if (v.followers <= 0) throw new Error('Los seguidores deben ser mayores que cero.');
        const interactions = v.likes + v.comments + v.saves + v.shares, rate = interactions / v.followers * 100;
        return result('Engagement por seguidores', pct(rate), [item('Interacciones medias', integer(interactions)), item('Muestra', `${integer(v.posts)} publicaciones`), item('Interacciones por 1.000 seguidores', number(interactions / v.followers * 1000)), item('Peso de guardados y compartidos', pct(interactions ? (v.saves + v.shares) / interactions * 100 : 0))], 'Compara siempre periodos y formatos equivalentes.');
      }
      case 'instagram-engagement-reach': {
        if (v.reach <= 0) throw new Error('El alcance debe ser mayor que cero.');
        const interactions = v.likes + v.comments + v.saves + v.shares, rate = interactions / v.reach * 100;
        return result('Engagement por alcance', pct(rate), [item('Interacciones', integer(interactions)), item('Alcance', integer(v.reach)), item('Interacciones por 1.000 cuentas', number(rate * 10)), item('Guardados + compartidos', integer(v.saves + v.shares))], 'El alcance representa cuentas únicas; no debe confundirse con impresiones.');
      }
      case 'tiktok-engagement': {
        if (v.base <= 0) throw new Error('La base debe ser mayor que cero.');
        const interactions = v.likes + v.comments + v.shares + v.saves, rate = interactions / v.base * 100;
        const basis = v.basis === 'views' ? 'visualizaciones' : 'seguidores';
        return result(`Engagement por ${basis}`, pct(rate), [item('Interacciones totales', integer(interactions)), item('Base', integer(v.base)), item('Compartidos', integer(v.shares)), item('Guardados', integer(v.saves))], 'Usa el mismo criterio de interacciones al comparar vídeos.');
      }
      case 'tiktok-income': {
        if (!(v.rpmLow <= v.rpm && v.rpm <= v.rpmHigh)) throw new Error('Ordena los escenarios: RPM bajo ≤ central ≤ alto.');
        if (v.months <= 0) throw new Error('El periodo debe ser mayor que cero.');
        if (v.totalViews > 0 && v.views > v.totalViews) throw new Error('Las visualizaciones cualificadas no pueden superar las visualizaciones totales introducidas.');
        const low = v.views / 1000 * v.rpmLow;
        const base = v.views / 1000 * v.rpm;
        const high = v.views / 1000 * v.rpmHigh;
        const monthly = base / v.months;
        const targetViews = v.rpm > 0 ? v.targetIncome / v.rpm * 1000 : 0;
        const qualifiedRate = v.totalViews > 0 ? v.views / v.totalViews * 100 : 0;
        const rows = [10000,100000,500000,1000000,5000000].map(views => [
          integer(views), money(views/1000*v.rpmLow), money(views/1000*v.rpm), money(views/1000*v.rpmHigh)
        ]);
        return result('Ingresos del periodo · escenario central', money(base), [
          item('Escenario bajo', money(low)),
          item('Escenario alto', money(high)),
          item('Vistas cualificadas sobre vistas totales', v.totalViews > 0 ? pct(qualifiedRate) : '—'),
          item('Vistas no cualificadas estimadas', v.totalViews > 0 ? integer(Math.max(0,v.totalViews-v.views)) : '—'),
          item('Media mensual central', money(monthly)),
          item('Proyección anual central', money(monthly * 12)),
          item('Vistas cualificadas para la meta', targetViews ? integer(targetViews) : '—'),
          item('Objetivo introducido', money(v.targetIncome))
        ], 'Estimación matemática basada en visualizaciones cualificadas y en los RPM introducidos. La elegibilidad y el pago final dependen de TikTok.', table(['Visualizaciones cualificadas','RPM bajo','RPM central','RPM alto'], rows));
      }
      case 'tiktok-rpm': {
        if (v.qualifiedViews <= 0) throw new Error('Las visualizaciones cualificadas deben ser mayores que cero.');
        const rpm = v.rewards / v.qualifiedViews * 1000;
        const projected = v.targetViews / 1000 * rpm;
        return result('RPM calculado', money(rpm), [
          item('Recompensas del periodo', money(v.rewards)),
          item('Visualizaciones cualificadas', integer(v.qualifiedViews)),
          item('Recompensa por visualización', money(v.rewards / v.qualifiedViews)),
          item(`Con ${integer(v.targetViews)} vistas cualificadas`, money(projected)),
          item('Con 100.000 vistas cualificadas', money(rpm * 100)),
          item('Con 1 millón de vistas cualificadas', money(rpm * 1000))
        ], 'La proyección mantiene el RPM calculado como hipótesis. TikTok puede modificar la elegibilidad y el RPM según el contenido, el periodo y el programa.');
      }
      case 'youtube-rpm-revenue': {
        if (v.views <= 0) throw new Error('Las visualizaciones deben ser mayores que cero.');
        const rpm = v.revenue / v.views * 1000;
        const projectedIncome = v.targetViews / 1000 * rpm;
        const neededRpm = v.targetViews > 0 ? v.targetIncome / v.targetViews * 1000 : 0;
        const rpmGap = neededRpm - rpm;
        return result('RPM calculado', money(rpm), [
          item('Ingresos del periodo', money(v.revenue)),
          item('Visualizaciones del periodo', integer(v.views)),
          item('Ingreso por visualización', money(v.revenue / v.views)),
          item(`Ingreso con ${integer(v.targetViews)} vistas`, money(projectedIncome)),
          item('RPM necesario para tu objetivo', neededRpm ? money(neededRpm) : '—'),
          item('Diferencia frente a tu RPM actual', neededRpm ? `${rpmGap >= 0 ? '+' : ''}${money(rpmGap)}` : '—'),
          item('Con 100.000 vistas', money(rpm * 100)),
          item('Con 1 millón de vistas', money(rpm * 1000))
        ], 'Usa ingresos y visualizaciones del mismo periodo y analiza Shorts y vídeos largos por separado.');
      }
      case 'youtube-cpm': {
        if (v.adImpressions <= 0 || v.monetizedPlaybacks <= 0) throw new Error('Impresiones y reproducciones monetizadas deben ser mayores que cero.');
        const cpm = v.cost / v.adImpressions * 1000;
        const playbackCpm = v.cost / v.monetizedPlaybacks * 1000;
        const targetCost = v.targetImpressions / 1000 * cpm;
        return result('CPM por impresiones', money(cpm), [
          item('CPM basado en reproducciones', money(playbackCpm)),
          item('Coste publicitario', money(v.cost)),
          item('Impresiones de anuncio', integer(v.adImpressions)),
          item('Reproducciones monetizadas', integer(v.monetizedPlaybacks)),
          item(`Coste estimado con ${integer(v.targetImpressions)} impresiones`, money(targetCost)),
          item('Diferencia playback CPM vs CPM', money(playbackCpm - cpm))
        ], 'CPM es una métrica enfocada en anunciantes y no equivale al RPM ni al ingreso final del creador.');
      }
      case 'youtube-watch-hours': {
        const hours = v.views * v.duration * v.retention / 100 / 60;
        const target = v.target === 'custom' ? v.customTarget : Number(v.target);
        const progress = target ? hours / target * 100 : 0;
        const neededViews = v.duration * v.retention > 0 ? Math.max(0, (target - hours) * 60 / (v.duration * v.retention / 100)) : 0;
        const extra = `<div class="progress"><span style="width:${clamp(progress,0,100)}%"></span></div>`;
        return result('Horas estimadas', `${number(hours)} h`, [item('Avance sobre objetivo', pct(progress)), item('Objetivo', `${integer(target)} h`), item('Vistas adicionales estimadas', integer(neededViews)), item('Minutos vistos', integer(hours * 60))], 'Solo cuentan las horas públicas válidas conforme a las reglas de YouTube.', extra);
      }
      case 'youtube-shorts-income': {
        if (!(v.rpmLow <= v.rpm && v.rpm <= v.rpmHigh)) throw new Error('Ordena los escenarios: RPM bajo ≤ central ≤ alto.');
        if (v.months <= 0) throw new Error('El periodo debe ser mayor que cero.');
        const low=v.views/1000*v.rpmLow, base=v.views/1000*v.rpm, high=v.views/1000*v.rpmHigh;
        const monthly=base/v.months;
        const targetViews=v.rpm>0?v.targetIncome/v.rpm*1000:0;
        const rows=[100000,500000,1000000,5000000,10000000].map(views=>[
          integer(views),money(views/1000*v.rpmLow),money(views/1000*v.rpm),money(views/1000*v.rpmHigh)
        ]);
        return result('Ingresos del periodo · escenario central',money(base),[
          item('Escenario bajo',money(low)),
          item('Escenario alto',money(high)),
          item('Media mensual central',money(monthly)),
          item('Proyección anual central',money(monthly*12)),
          item('Vistas interesadas para la meta',targetViews?integer(targetViews):'—'),
          item('Objetivo introducido',money(v.targetIncome))
        ],'El RPM real de Shorts puede cambiar por audiencia, país, temporada y rendimiento. Usa tu dato de Analytics cuando esté disponible.',table(['Visualizaciones interesadas','RPM bajo','RPM central','RPM alto'],rows));
      }
      case 'youtube-income': {
        if (!(v.rpmLow <= v.rpm && v.rpm <= v.rpmHigh)) throw new Error('Ordena los escenarios: RPM bajo ≤ central ≤ alto.');
        if (v.months <= 0) throw new Error('El periodo debe ser mayor que cero.');
        const low = v.views / 1000 * v.rpmLow, base = v.views / 1000 * v.rpm, high = v.views / 1000 * v.rpmHigh, monthly = base / v.months;
        const targetViews = v.rpm > 0 ? v.targetIncome / v.rpm * 1000 : 0;
        const rpmNeeded = v.views > 0 ? v.targetIncome / v.views * 1000 : 0;
        const viewsGap = Math.max(0,targetViews-v.views);
        const rows = [10000,100000,250000,500000,1000000].map(views => [
          integer(views), money(views/1000*v.rpmLow), money(views/1000*v.rpm), money(views/1000*v.rpmHigh)
        ]);
        return result('Ingresos del periodo · escenario central', money(base), [
          item('Escenario bajo', money(low)),
          item('Escenario alto', money(high)),
          item('Media mensual central', money(monthly)),
          item('Proyección anual central', money(monthly * 12)),
          item('Vistas para el objetivo', targetViews ? integer(targetViews) : '—'),
          item('Vistas adicionales frente al volumen actual', targetViews ? integer(viewsGap) : '—'),
          item('RPM necesario con tus vistas actuales', rpmNeeded ? money(rpmNeeded) : '—'),
          item('Objetivo introducido', money(v.targetIncome))
        ], 'La estimación se basa únicamente en las visualizaciones y los RPM introducidos; no incluye patrocinios, afiliación ni venta de productos.', table(['Visualizaciones','RPM bajo','RPM central','RPM alto'], rows));
      }
      case 'youtube-rpm-monthly': {
        const views = v.dailyViews * v.days, income = views / 1000 * v.rpm;
        return result('Ingresos estimados', money(income), [item('Visualizaciones del periodo', integer(views)), item('Media semanal', money(v.dailyViews * 7 / 1000 * v.rpm)), item('Escenario −20 % RPM', money(income * .8)), item('Escenario +20 % RPM', money(income * 1.2))], 'El RPM puede cambiar por audiencia, formato, temática y temporada.');
      }
      case 'youtube-views-goal': {
        if (v.rpm <= 0) throw new Error('El RPM debe ser mayor que cero.');
        const views = v.targetIncome / v.rpm * 1000;
        return result('Visualizaciones necesarias', integer(views), [item('Vistas diarias', integer(views / v.days)), item('Vistas semanales', integer(views / v.days * 7)), item('Objetivo', money(v.targetIncome)), item('RPM', money(v.rpm))], 'Equivalencia matemática; el RPM puede cambiar antes de alcanzar el objetivo.');
      }
      case 'compound-interest': {
        const netRate = v.rate - v.fee;
        const sim = simulateCompound(v.initial, v.monthly, netRate, v.years, v.timing || 'end');
        const contributed = v.initial + v.monthly * v.years * 12, gains = sim.balance - contributed;
        const real = v.inflation <= -100 ? sim.balance : sim.balance / Math.pow(1 + v.inflation / 100, v.years);
        const rows = sim.yearly.slice(1).map((value, i) => [i + 1, money(value), money(v.initial + v.monthly * (i + 1) * 12), money(value - (v.initial + v.monthly * (i + 1) * 12))]);
        const effective = Math.pow(1 + netRate / 100, 1) - 1;
        return result('Capital final estimado', money(sim.balance), [item('Total aportado', money(contributed)), item('Ganancia estimada', money(gains)), item('Valor real tras inflación', money(real)), item('Rentabilidad neta usada', pct(effective * 100))], `Capitalización mensual, aportación al ${v.timing === 'beginning' ? 'inicio' : 'final'} del mes y tasa constante.`, chart(sim.yearly) + table(['Año','Capital','Aportado','Ganancia'], rows.slice(-10)));
      }
      case 'mortgage': {
        const months = Math.max(1, Math.round(v.years * 12)), schedule = loanSchedule(v.principal, v.rate, months);
        const total = schedule.payment * months, rows = schedule.rows.map(r => [r[0], money(r[1]), money(r[2]), money(r[3]), money(r[4])]);
        const yearsSet=[Math.max(1,v.years-5),v.years,v.years+5].filter((x,i,a)=>a.indexOf(x)===i);
        const scenarios=yearsSet.map(y=>{const sc=loanSchedule(v.principal,v.rate,Math.max(1,Math.round(y*12)));return [`${number(y)} años`,money(sc.payment),money(sc.interest),money(sc.payment*sc.months+v.fees)];});
        const extra=`<h3 class="result-subheading">Compara el efecto del plazo</h3>${table(['Plazo','Cuota','Intereses','Coste con gastos'],scenarios)}<h3 class="result-subheading">Tabla completa de amortización</h3>${table(['Mes','Cuota','Interés','Capital','Pendiente'], rows)}`;
        return result('Cuota mensual estimada', money(schedule.payment), [item('Intereses totales', money(schedule.interest)), item('Total de cuotas', money(total)), item('Coste con gastos iniciales', money(total + v.fees)), item('Número de cuotas', integer(months))], 'Sistema francés a tipo fijo; no incluye seguros ni variaciones contractuales.', extra);
      }
      case 'personal-loan': {
        const months = Math.max(1, Math.round(v.years * 12)), schedule = loanSchedule(v.principal, v.rate, months);
        const opening = v.principal * v.commission / 100, total = schedule.payment * months + opening;
        const rows=schedule.rows.map(r=>[r[0],money(r[1]),money(r[2]),money(r[3]),money(r[4])]);
        const yearsSet=[Math.max(1,v.years-1),v.years,v.years+1].filter((x,i,a)=>a.indexOf(x)===i);
        const scenarios=yearsSet.map(y=>{const sc=loanSchedule(v.principal,v.rate,Math.max(1,Math.round(y*12)));return [`${number(y)} años`,money(sc.payment),money(sc.interest),money(sc.payment*sc.months+opening)];});
        const extra=`<h3 class="result-subheading">Compara plazos</h3>${table(['Plazo','Cuota','Intereses','Coste total'],scenarios)}<h3 class="result-subheading">Tabla completa de amortización</h3>${table(['Mes','Cuota','Interés','Capital','Pendiente'],rows)}`;
        return result('Cuota mensual estimada', money(schedule.payment), [item('Intereses', money(schedule.interest)), item('Comisión apertura', money(opening)), item('Coste total', money(total)), item('Cuotas', integer(months))], 'La TAE de una oferta puede incorporar otros costes y calendarios de pago.',extra);
      }
      case 'monthly-savings': {
        if (v.months <= 0) throw new Error('El plazo debe ser mayor que cero.');
        if (v.rate <= -100) throw new Error('La rentabilidad debe ser superior a −100 %.');
        const r = Math.pow(1 + v.rate / 100, 1 / 12) - 1;
        const currentFuture = v.current * Math.pow(1 + r, v.months);
        const factor = Math.abs(r) < 1e-12 ? v.months : (Math.pow(1 + r, v.months) - 1) / r;
        const monthly = Math.max(0, (v.goal - currentFuture) / factor);
        const noReturn = Math.max(0, (v.goal - v.current) / v.months);
        return result('Ahorro mensual necesario', money(monthly), [item('Sin rentabilidad', money(noReturn)), item('Ahorro actual al final', money(currentFuture)), item('Total aportaciones nuevas', money(monthly * v.months)), item('Plazo', formatMonths(v.months))], 'La rentabilidad, si se usa, es una hipótesis constante.');
      }
      case 'index-funds': {
        const withFee = simulateCompound(v.initial, v.monthly, v.return - v.fee, v.years);
        const noFee = simulateCompound(v.initial, v.monthly, v.return, v.years);
        const contributed = v.initial + v.monthly * v.years * 12;
        const real = v.inflation <= -100 ? withFee.balance : withFee.balance / Math.pow(1 + v.inflation / 100, v.years);
        return result('Capital final con comisión', money(withFee.balance), [item('Total aportado', money(contributed)), item('Ganancia estimada', money(withFee.balance - contributed)), item('Impacto de comisión', money(noFee.balance - withFee.balance)), item('Valor real', money(real))], 'No incluye impuestos y no predice la rentabilidad de ningún fondo.', chart(withFee.yearly));
      }
      case 'mortgage-prepayment': {
        if (v.extra >= v.principal) throw new Error('La amortización debe ser menor que el capital pendiente para comparar escenarios.');
        const months = Math.max(1, Math.round(v.years * 12));
        const base = loanSchedule(v.principal, v.rate, months);
        const newPrincipal = v.principal - v.extra;
        const commission = v.extra * v.commission / 100;
        const reducePayment = loanSchedule(newPrincipal, v.rate, months);
        const reduceTerm = loanSchedule(newPrincipal, v.rate, months, base.payment);
        const savePay = base.interest - reducePayment.interest - commission;
        const saveTerm = base.interest - reduceTerm.interest - commission;
        return result('Ahorro neto estimado reduciendo plazo', money(saveTerm), [item('Cuota nueva si reduces cuota', money(reducePayment.payment)), item('Ahorro neto reduciendo cuota', money(savePay)), item('Plazo nuevo si reduces plazo', formatMonths(reduceTerm.months)), item('Meses ahorrados', integer(months - reduceTerm.months)), item('Comisión introducida', money(commission)), item('Cuota actual estimada', money(base.payment))], 'El banco puede aplicar redondeos, fechas y condiciones diferentes.');
      }
      case 'freelance-rate': {
        if (v.reserve >= 100) throw new Error('La reserva debe ser inferior al 100 %.');
        const annualNeed = (v.net * 12 + v.expenses * 12) / (1 - v.reserve / 100);
        const annualWithMargin = annualNeed * (1 + v.margin / 100);
        const hours = v.billable * v.weeks, rate = annualWithMargin / hours;
        return result('Tarifa recomendada por hora', money(rate), [item('Tarifa diaria (8 h)', money(rate * 8)), item('Facturación anual objetivo', money(annualWithMargin)), item('Facturación mensual media', money(annualWithMargin / 12)), item('Horas facturables anuales', integer(hours))], 'Hipótesis de planificación: revisa impuestos y cotizaciones reales con asesoría.');
      }
      case 'profit-margin': {
        if (v.price <= 0) throw new Error('El precio debe ser mayor que cero.');
        const profit = v.price - v.cost, margin = profit / v.price * 100, markup = v.cost ? profit / v.cost * 100 : Infinity;
        const targetPrice = v.targetMargin >= 100 ? Infinity : v.cost / (1 - v.targetMargin / 100);
        const margins=[20,30,40,50,60].map(m=>[`${m} %`,money(v.cost/(1-m/100)),money(v.cost/(1-m/100)-v.cost)]);
        return result('Margen sobre ventas', pct(margin), [item('Beneficio unitario', money(profit)), item('Markup sobre coste', Number.isFinite(markup) ? pct(markup) : '∞'), item('Beneficio total', money(profit * v.units)), item('Precio para margen objetivo', Number.isFinite(targetPrice) ? money(targetPrice) : 'No definido')], 'Compara siempre coste y precio con el mismo criterio de impuestos.', `<h3 class="result-subheading">Escenarios de precio por margen</h3>${table(['Margen objetivo','Precio necesario','Beneficio/unidad'],margins)}`);
      }
      case 'break-even': {
        const contribution = v.price - v.variable;
        if (contribution <= 0) throw new Error('El precio debe ser mayor que el coste variable unitario.');
        const units = v.fixed / contribution, revenue = Math.ceil(units) * v.price;
        const projectedProfit = v.expected * contribution - v.fixed;
        const safety = v.expected ? (v.expected - units) / v.expected * 100 : 0;
        return result('Unidades para equilibrio', integer(Math.ceil(units)), [item('Ventas para equilibrio', money(revenue)), item('Margen contribución/unidad', money(contribution)), item('Beneficio con ventas previstas', money(projectedProfit)), item('Margen de seguridad', pct(safety))], 'Redondea hacia arriba porque una fracción de unidad no cubre el coste completo.');
      }
      case 'dismissal-compensation': {
        const totalDaysWorked = daysBetween(v.start, v.end, false);
        if (!(totalDaysWorked > 0)) throw new Error('La fecha final debe ser posterior a la inicial.');
        const years = totalDaysWorked / 365.2425, salaryDay = v.salary / 365;
        let days = 0, detail = '';
        if (v.type === 'objective') { days = Math.min(years * 20, 360); detail = '20 días por año, tope aproximado de 12 mensualidades.'; }
        else if (v.type === 'temporary') { days = years * 12; detail = 'Escenario orientativo de 12 días por año cuando resulte aplicable.'; }
        else {
          const cut = '2012-02-12';
          if (v.start < cut) {
            const preEnd = v.end < cut ? v.end : cut;
            const pre = Math.max(0, daysBetween(v.start, preEnd) / 365.2425 * 45);
            const post = v.end > cut ? Math.max(0, daysBetween(cut, v.end) / 365.2425 * 33) : 0;
            const cap = pre > 720 ? Math.min(pre, 1260) : 720;
            days = Math.min(pre + post, cap); detail = `Tramo anterior: ${number(pre)} días; tramo posterior: ${number(post)} días.`;
          } else { days = Math.min(years * 33, 720); detail = '33 días por año, tope aproximado de 24 mensualidades.'; }
        }
        const amount = salaryDay * days;
        return result('Indemnización estimada', money(amount), [item('Antigüedad', `${number(years)} años`), item('Días indemnizatorios', number(days)), item('Salario diario usado', money(salaryDay)), item('Periodo trabajado', `${integer(totalDaysWorked)} días`)], detail + ' Estimación no vinculante.');
      }
      case 'severance': {
        const daily = v.monthly / 30, salaryPending = daily * v.salaryDays, vacation = daily * v.vacationDays;
        const compensation = v.includeCompensation ? Number(v.compensation || 0) : 0;
        const settlement = salaryPending + vacation + v.extraPay + v.other - v.deductions;
        const total = settlement + compensation;
        const rows = [
          ['Salario pendiente', money(salaryPending)],
          ['Vacaciones no disfrutadas', money(vacation)],
          ['Pagas extra devengadas', money(v.extraPay)],
          ['Otros conceptos', money(v.other)],
          ['Deducciones', `−${money(v.deductions)}`],
          ['Finiquito sin indemnización', money(settlement)],
          ['Indemnización añadida', money(compensation)],
        ];
        return result('Total bruto orientativo', money(total), [
          item('Finiquito sin indemnización', money(settlement)),
          item('Salario diario aproximado', money(daily)),
          item('Vacaciones', money(vacation)),
          item('Indemnización añadida', money(compensation))
        ], 'Resultado bruto orientativo. No calcula IRPF, cotizaciones ni verifica el documento de liquidación.', table(['Partida','Importe'], rows));
      }
      case 'net-salary': {
        const rate=(v.irpf+v.ss)/100;
        if (rate >= 1) throw new Error('La suma de IRPF y cotización debe ser inferior al 100 %.');
        const pays=Number(v.payments);
        if(v.direction==='net-to-gross'){
          const net=v.gross;
          const gross=(net+v.other)/(1-rate);
          const irpf=gross*v.irpf/100,ss=gross*v.ss/100,totalDeductions=irpf+ss+v.other;
          return result('Bruto anual estimado',money(gross),[
            item(`Bruto por paga (${pays})`,money(gross/pays)),
            item('Neto anual objetivo',money(net)),
            item('IRPF estimado',money(irpf)),
            item('Cotización estimada',money(ss)),
            item('Deducciones totales',money(totalDeductions)),
            item('Tipo efectivo total',pct(gross?totalDeductions/gross*100:0))
          ],'Conversión inversa orientativa usando porcentajes editables. No sustituye una nómina real ni el cálculo oficial de retenciones.');
        }
        const gross=v.gross,irpf=gross*v.irpf/100,ss=gross*v.ss/100,net=gross-irpf-ss-v.other,totalDeductions=irpf+ss+v.other;
        return result('Neto anual estimado',money(net),[
          item(`Neto por paga (${pays})`,money(net/pays)),
          item('Neto mensual equivalente',money(net/12)),
          item('IRPF estimado',money(irpf)),
          item('Cotización estimada',money(ss)),
          item('Deducciones totales',money(totalDeductions)),
          item('Tipo efectivo total',pct(gross?totalDeductions/gross*100:0))
        ],'Porcentajes editables; no sustituye una nómina real ni el cálculo oficial de retenciones.');
      }
      case 'vacation-days': {
        const worked = daysBetween(v.start, v.end, true);
        if (!(worked > 0)) throw new Error('La fecha final debe ser igual o posterior a la inicial.');
        const accrued = v.annual * worked / 365.2425, pending = accrued - v.taken;
        return result('Vacaciones pendientes estimadas', `${number(pending)} días`, [item('Generadas', `${number(accrued)} días`), item('Ya disfrutadas', `${number(v.taken)} días`), item('Días trabajados', integer(worked)), item('Referencia anual', `${number(v.annual)} días`), item('Ritmo mensual orientativo', `${number(v.annual/12)} días`), item('Parte del año trabajada', pct(worked/365.2425*100))], 'El convenio, el contrato y la política de redondeo pueden modificar el resultado.');
      }
      case 'employer-cost': {
        const contribution = v.gross * v.rate / 100, total = v.gross + contribution + v.other + v.bonus;
        const rates=[Math.max(0,v.rate-2),v.rate,v.rate+2].filter((x,i,a)=>a.indexOf(x)===i);
        const rows=rates.map(rate=>{const cont=v.gross*rate/100;const cost=v.gross+cont+v.other+v.bonus;return [pct(rate),money(cont),money(cost),money(cost/12)];});
        const breakdown=[['Salario bruto',money(v.gross)],['Cotización empresarial',money(contribution)],['Otros costes',money(v.other)],['Bonus / variable',money(v.bonus)],['Coste total',money(total)]];
        return result('Coste anual estimado', money(total), [item('Coste mensual medio', money(total / 12)), item('Cotización empresarial estimada', money(contribution)), item('Otros costes + variable', money(v.other + v.bonus)), item('Coste adicional sobre bruto', pct(v.gross ? (total - v.gross) / v.gross * 100 : 0))], 'La tasa empresarial es una hipótesis editable y no una cotización universal.', `<h3 class="result-subheading">Desglose del escenario</h3>${table(['Partida','Importe'],breakdown)}<h3 class="result-subheading">Sensibilidad de la cotización</h3>${table(['Tasa','Cotización','Coste anual','Coste mensual'],rows)}`);
      }
      case 'marketing-roas-cac': {
        if (v.spend <= 0) throw new Error('La inversión publicitaria debe ser mayor que cero.');
        const roas = v.revenue / v.spend;
        const roi = (v.revenue - v.spend - v.otherCosts) / (v.spend + v.otherCosts) * 100;
        const cac = v.customers > 0 ? v.spend / v.customers : 0;
        const grossContribution = v.revenue * v.grossMargin / 100 - v.spend - v.otherCosts;
        const breakEvenRoas = v.grossMargin > 0 ? 100 / v.grossMargin : 0;
        return result('ROAS de la campaña', `${number(roas)}x`, [item('Ingresos atribuidos', money(v.revenue)), item('CAC publicitario', v.customers > 0 ? money(cac) : '—'), item('ROI antes de costes generales', pct(roi)), item('Contribución tras margen y campaña', money(grossContribution)), item('ROAS de equilibrio aproximado', `${number(breakEvenRoas)}x`)], 'El ROAS mide ingresos atribuidos por euro invertido; no equivale a beneficio. La atribución y el margen bruto cambian la lectura.');
      }
      case 'customer-profitability': {
        if (v.customers <= 0) throw new Error('El número de clientes debe ser mayor que cero.');
        const costs = v.directCosts + v.acquisition + v.otherCosts;
        const profit = v.revenue - costs;
        const per = profit / v.customers;
        const revenuePer = v.revenue / v.customers;
        const costPer = costs / v.customers;
        const margin = v.revenue > 0 ? profit / v.revenue * 100 : 0;
        return result('Beneficio medio por cliente', money(per), [item('Beneficio total estimado', money(profit)), item('Ingresos por cliente', money(revenuePer)), item('Coste total por cliente', money(costPer)), item('Margen después de costes atribuidos', pct(margin)), item('Clientes analizados', integer(v.customers))], 'Incluye solo costes atribuibles de forma coherente al mismo grupo y periodo.');
      }
      case 'vat-calculator': {
        const rate = v.ratePreset === 'custom' ? Number(v.customRate) : Number(v.ratePreset);
        if (!(rate >= 0 && rate <= 100)) throw new Error('El tipo de IVA debe estar entre 0 y 100 %.');
        const factor = 1 + rate / 100;
        let base, total;
        if (v.direction === 'remove') { total = v.amount; base = factor ? total / factor : total; }
        else { base = v.amount; total = base * factor; }
        const vat = total - base;
        return result(v.direction === 'remove' ? 'Base sin IVA' : 'Total con IVA', money(v.direction === 'remove' ? base : total), [item('Base imponible', money(base)), item(`IVA · ${number(rate)} %`, money(vat)), item('Total', money(total))], 'Comprueba que el tipo elegido corresponde realmente a la operación. La herramienta no determina qué tipo fiscal es aplicable.');
      }
      case 'percentage-calculator': {
        let value = 0, label = 'Resultado';
        if (v.mode === 'of') { value = v.a / 100 * v.b; label = `${number(v.a)} % de ${number(v.b)}`; }
        else if (v.mode === 'ratio') { if (v.b === 0) throw new Error('El valor B no puede ser cero.'); value = v.a / v.b * 100; label = 'Porcentaje'; }
        else if (v.mode === 'change') { if (v.a === 0) throw new Error('El valor inicial no puede ser cero.'); value = (v.b - v.a) / v.a * 100; label = 'Variación porcentual'; }
        else if (v.mode === 'increase') { value = v.a * (1 + v.b/100); label = 'Valor tras aumentar'; }
        else if (v.mode === 'discount') { value = v.a * (1 - v.b/100); label = 'Valor tras reducir'; }
        else if (v.mode === 'original') { const factor = 1 + v.b/100; if (Math.abs(factor) < 1e-12) throw new Error('Ese porcentaje no permite recuperar un valor original.'); value = v.a / factor; label = 'Valor original'; }
        const isPct = ['ratio','change'].includes(v.mode);
        return result(label, isPct ? pct(value) : number(value), [item('Valor A', number(v.a)), item('Valor B', number(v.b)), item('Modo', String(v.mode))], 'Elige el modo que corresponda a tu pregunta; porcentajes y puntos porcentuales no son equivalentes.');
      }
      case 'unit-converter': {
        const defs = {
          length:{m:{label:'Metros',factor:1},km:{label:'Kilómetros',factor:1000},cm:{label:'Centímetros',factor:.01},mm:{label:'Milímetros',factor:.001},mi:{label:'Millas',factor:1609.344},yd:{label:'Yardas',factor:.9144},ft:{label:'Pies',factor:.3048},in:{label:'Pulgadas',factor:.0254}},
          mass:{kg:{label:'Kilogramos',factor:1},g:{label:'Gramos',factor:.001},mg:{label:'Miligramos',factor:.000001},lb:{label:'Libras',factor:.45359237},oz:{label:'Onzas',factor:.028349523125},t:{label:'Toneladas',factor:1000}},
          volume:{l:{label:'Litros',factor:1},ml:{label:'Mililitros',factor:.001},m3:{label:'Metros cúbicos',factor:1000},gal_us:{label:'Galones US',factor:3.785411784},qt_us:{label:'Cuartos US',factor:.946352946},cup_us:{label:'Tazas US',factor:.2365882365}},
          speed:{ms:{label:'m/s',factor:1},kmh:{label:'km/h',factor:1/3.6},mph:{label:'mph',factor:.44704},knot:{label:'Nudos',factor:.5144444444}},
          data:{B:{label:'Bytes',factor:1},KB:{label:'KB · decimal',factor:1000},MB:{label:'MB · decimal',factor:1e6},GB:{label:'GB · decimal',factor:1e9},KiB:{label:'KiB · binario',factor:1024},MiB:{label:'MiB · binario',factor:1048576},GiB:{label:'GiB · binario',factor:1073741824}},
          temperature:{C:{label:'°C'},F:{label:'°F'},K:{label:'K'}}
        };
        const dim=defs[v.dimension]; if(!dim || !dim[v.from] || !dim[v.to]) throw new Error('Selecciona unidades compatibles con la magnitud elegida.');
        const dimensionLabels={length:'Longitud',mass:'Masa',volume:'Volumen',temperature:'Temperatura',speed:'Velocidad',data:'Datos / almacenamiento'};
        let converted, factorText='';
        if(v.dimension==='temperature'){
          let c;if(v.from==='C')c=v.value;else if(v.from==='F')c=(v.value-32)*5/9;else c=v.value-273.15;
          if(v.to==='C')converted=c;else if(v.to==='F')converted=c*9/5+32;else converted=c+273.15; factorText='Transformación de temperatura';
        } else { const factor=dim[v.from].factor/dim[v.to].factor; const base=v.value*dim[v.from].factor; converted=base/dim[v.to].factor; factorText=`Factor de conversión: × ${number(factor)}`; }
        return result('Valor convertido', number(converted), [item('Origen', `${number(v.value)} ${dim[v.from].label}`), item('Destino', `${number(converted)} ${dim[v.to].label}`), item('Magnitud', dimensionLabels[v.dimension] || v.dimension), item('Relación', factorText)], 'El valor mostrado se redondea para lectura; el cálculo utiliza los factores definidos en la herramienta.');
      }
      case 'date-difference': {
        const rawDays = daysBetween(v.start, v.end, Boolean(v.inclusive));
        if (!(rawDays >= 0)) throw new Error('La fecha final debe ser igual o posterior a la inicial.');
        const start = new Date(`${v.start}T12:00:00`), end = new Date(`${v.end}T12:00:00`);
        let business = 0;
        const cursor = new Date(start);
        while (cursor <= end) {
          const day = cursor.getDay();
          if (day !== 0 && day !== 6) business++;
          cursor.setDate(cursor.getDate()+1);
        }
        if (!v.inclusive && start <= end) {
          const day=end.getDay(); if (day!==0 && day!==6) business=Math.max(0,business-1);
        }
        business = Math.max(0, business - Number(v.holidays || 0));
        const weeks = rawDays / 7;
        return result('Días entre fechas', `${integer(rawDays)} días`, [item('Semanas equivalentes', number(weeks)), item('Días laborables estimados', integer(business)), item('Festivos restados', integer(v.holidays || 0)), item('Conteo inclusivo', v.inclusive ? 'Sí' : 'No')], 'Los días laborables se estiman de lunes a viernes y restan los festivos que tú indiques; no consulta calendarios oficiales.');
      }
      default: throw new Error('Herramienta no reconocida.');
    }
  }

  function transformStyle(text, caps, lower, digits = null) {
    return Array.from(text).map(ch => {
      const code = ch.codePointAt(0);
      if (code >= 65 && code <= 90) return String.fromCodePoint(caps + code - 65);
      if (code >= 97 && code <= 122) return String.fromCodePoint(lower + code - 97);
      if (digits && code >= 48 && code <= 57) return String.fromCodePoint(digits + code - 48);
      return ch;
    }).join('');
  }

  function renderFonts(text) {
    const styles = [
      ['Negrita con serifas', transformStyle(text, 0x1D400, 0x1D41A, 0x1D7CE)],
      ['Negrita sin serifas', transformStyle(text, 0x1D5D4, 0x1D5EE, 0x1D7EC)],
      ['Negrita cursiva', transformStyle(text, 0x1D468, 0x1D482)],
      ['Negrita cursiva sin serifas', transformStyle(text, 0x1D63C, 0x1D656)],
      ['Monoespaciada', transformStyle(text, 0x1D670, 0x1D68A, 0x1D7F6)],
      ['Ancho completo', transformStyle(text, 0xFF21, 0xFF41, 0xFF10)],
    ];
    return styles.map(([name, value]) => `<div class="font-result"><small>${name}</small><output>${escapeHtml(value)}</output><button class="btn btn-secondary js-copy-output" type="button">Copiar</button></div>`).join('') + note('Los acentos y caracteres sin equivalente especial se conservan.');
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function renderCounter(v) {
    const text = v.text || '';
    const limit = v.preset === 'custom' ? Number(v.customLimit) : Number(v.preset);
    const chars = Array.from(text).length, noSpaces = Array.from(text.replace(/\s/g,'')).length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0, lines = text ? text.split(/\r?\n/).length : 0;
    const remaining = limit - chars, progress = limit ? chars / limit * 100 : 0;
    return `${hero('Caracteres', integer(chars))}<div class="result-grid">${item('Restantes', `<span class="${remaining < 0 ? 'negative' : 'positive'}">${integer(remaining)}</span>`)}${item('Sin espacios', integer(noSpaces))}${item('Palabras', integer(words))}${item('Líneas', integer(lines))}</div><div class="progress"><span style="width:${clamp(progress,0,100)}%"></span></div>${note(`Referencia seleccionada: ${integer(limit)} caracteres. Confirma siempre el límite que muestre la aplicación.`)}`;
  }

  function formatInstagramText(text) {
    return String(text || '').split(/\r?\n/).map(line => line.trim()).map(line => line === '' ? '\u2800' : line).join('\n').trim();
  }

  async function copyText(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      const old = button.textContent; button.textContent = 'Copiado';
      setTimeout(() => button.textContent = old, 1400);
    } catch {
      const area = document.createElement('textarea'); area.value = text; document.body.appendChild(area); area.select(); document.execCommand('copy'); area.remove();
    }
  }

  function cleanReportText(text) {
    return String(text || '').replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
  }

  function fieldLabel(element) {
    if (!element?.id) return element?.name || 'Dato';
    return document.querySelector(`label[for="${element.id}"]`)?.textContent?.trim() || element.name || 'Dato';
  }

  function collectInputs(form) {
    if (!form) return [];
    return Array.from(form.elements || []).filter(el => el.name && !['submit','reset','button','file'].includes(el.type)).map(el => {
      if (el.type === 'checkbox') return [fieldLabel(el), el.checked ? 'Sí' : 'No'];
      const value = el.tagName === 'SELECT' ? el.options[el.selectedIndex]?.text : el.value;
      return [fieldLabel(el), String(value ?? '').trim()];
    }).filter(([, value]) => value !== '');
  }

  function buildClientReport(panel, output) {
    const form = document.querySelector('.tool-form');
    const title = panel?.dataset.reportTitle || form?.dataset.toolTitle || document.querySelector('h1')?.textContent || 'Resultado Clicivo';
    const inputs = collectInputs(form);
    const lines = [title, `Fecha: ${new Date().toLocaleDateString('es-ES')}`, ''];
    if (inputs.length) {
      lines.push('DATOS UTILIZADOS');
      inputs.forEach(([label, value]) => lines.push(`• ${label}: ${value}`));
      lines.push('');
    }
    lines.push('RESULTADO');
    lines.push(cleanReportText(output?.innerText));
    lines.push('', 'Resultado orientativo generado con Clicivo. Revisa los datos y contrasta documentación oficial o asesoramiento profesional cuando corresponda.', `Fuente: ${location.origin}${panel?.dataset.reportPath || location.pathname}`);
    return lines.join('\n');
  }

  function reportSlug(text) {
    return String(text || 'resultado').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 65);
  }

  function downloadResultPdf(panel, output) {
    const jsPDF = window.jspdf?.jsPDF;
    if (!jsPDF) {
      window.print();
      return false;
    }
    const form = document.querySelector('.tool-form');
    const title = panel?.dataset.reportTitle || form?.dataset.toolTitle || 'Resultado Clicivo';
    const inputs = collectInputs(form);
    const result = cleanReportText(output?.innerText);
    const doc = new jsPDF({ unit:'mm', format:'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 18;
    let y = 22;
    const ensureSpace = needed => {
      if (y + needed > pageHeight - 20) {
        doc.addPage();
        y = 22;
      }
    };
    const write = (text, size=10, options={}) => {
      doc.setFont('helvetica', options.bold ? 'bold' : 'normal');
      doc.setFontSize(size);
      doc.setTextColor(...(options.color || [48,57,79]));
      const lines = doc.splitTextToSize(String(text), pageWidth - margin*2);
      ensureSpace(lines.length * (size * .43) + 4);
      doc.text(lines, margin, y);
      y += lines.length * (size * .43) + (options.gap ?? 4);
    };
    doc.setFillColor(22,36,82);
    doc.roundedRect(12, 12, pageWidth-24, 42, 5, 5, 'F');
    doc.setTextColor(255,255,255);
    doc.setFont('helvetica','bold');
    doc.setFontSize(11);
    doc.text('CLICIVO · INFORME DE RESULTADO', margin, 25);
    doc.setFontSize(17);
    const titleLines = doc.splitTextToSize(title, pageWidth-margin*2);
    doc.text(titleLines, margin, 36);
    doc.setFont('helvetica','normal');
    doc.setFontSize(9);
    doc.text(`Generado el ${new Date().toLocaleDateString('es-ES')}`, margin, 49);
    y = 66;
    if (inputs.length) {
      write('Datos utilizados', 13, {bold:true, color:[22,36,82], gap:5});
      inputs.forEach(([label,value]) => write(`${label}: ${value}`, 9.5, {gap:2.5}));
      y += 4;
    }
    write('Resultado', 13, {bold:true, color:[22,36,82], gap:5});
    const blocks = result.split('\n').filter(Boolean);
    blocks.forEach((line, index) => write(line, index === 0 ? 12 : 9.5, {bold:index === 0, gap:3.5}));
    y += 4;
    write('Cómo interpretar este informe', 12, {bold:true, color:[22,36,82], gap:5});
    write('El resultado depende de los datos introducidos y de los supuestos visibles en la herramienta. Úsalo para comparar escenarios y contrasta documentación oficial o asesoramiento profesional cuando corresponda.', 8.8, {color:[92,102,124], gap:4});
    write(`${location.origin}${panel?.dataset.reportPath || location.pathname}`, 8.2, {color:[37,99,235], gap:2});
    const pages = doc.getNumberOfPages();
    for (let i=1;i<=pages;i++) {
      doc.setPage(i);
      doc.setDrawColor(225,230,240);
      doc.line(margin, pageHeight-14, pageWidth-margin, pageHeight-14);
      doc.setTextColor(120,128,145);
      doc.setFontSize(8);
      doc.text(`Clicivo · página ${i} de ${pages}`, margin, pageHeight-9);
    }
    doc.save(`clicivo-${reportSlug(title)}.pdf`);
    return true;
  }

  const FAVORITES_KEY = 'clicivo:favorites:v1';
  const RECENTS_KEY = 'clicivo:recent:v1';
  const SCENARIO_PREFIX = 'clicivo:scenario:v1:';

  function safeJsonRead(key, fallback = []) {
    try { const value = JSON.parse(localStorage.getItem(key) || 'null'); return value ?? fallback; } catch { return fallback; }
  }

  function downloadCsv(filename, rows) {
    const csv = rows.map(row => row.map(value => `"${String(value ?? '').replace(/"/g,'""')}"`).join(',')).join('\r\n');
    const blob = new Blob(['﻿'+csv], { type:'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=filename; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),500);
  }

  function scenarioData(form) {
    const values = {};
    Array.from(form?.elements || []).forEach(el => {
      if (!el.name || ['submit','reset','button','file'].includes(el.type)) return;
      values[el.name] = el.type === 'checkbox' ? el.checked : el.value;
    });
    return values;
  }

  function restoreScenario(form, values) {
    if (!form || !values) return;
    Object.entries(values).forEach(([name,value]) => {
      const el=form.elements.namedItem(name); if (!el) return;
      if (el.type === 'checkbox') el.checked=Boolean(value); else el.value=value;
      el.dispatchEvent(new Event('change',{bubbles:true}));
    });
  }

  function currentToolMeta() {
    const main=document.querySelector('[data-tool-page]');
    if (!main) return null;
    return { id:main.dataset.toolPage, title:main.dataset.toolTitle || document.querySelector('h1')?.textContent || 'Herramienta', path:main.dataset.toolPath || location.pathname };
  }

  function rememberRecentTool() {
    const meta=currentToolMeta(); if (!meta) return;
    const recent=safeJsonRead(RECENTS_KEY,[]).filter(x=>x.id!==meta.id); recent.unshift(meta); localStorage.setItem(RECENTS_KEY,JSON.stringify(recent.slice(0,8)));
  }

  function renderRecentTools() {
    const section=document.querySelector('[data-recent-section]'); const box=document.querySelector('[data-recent-tools]'); if (!section || !box) return;
    const favorites=safeJsonRead(FAVORITES_KEY,[]); const recent=safeJsonRead(RECENTS_KEY,[]);
    const items=[]; const seen=new Set();
    [...favorites,...recent].forEach(x=>{ if (x?.id && !seen.has(x.id)) { seen.add(x.id); items.push(x); } });
    if (!items.length) return;
    box.innerHTML=items.slice(0,8).map(x=>`<a class="recent-tool" href="${x.path}"><span>${favorites.some(f=>f.id===x.id)?'★ Favorita':'Reciente'}</span><strong>${escapeHtml(x.title)}</strong><b>→</b></a>`).join('');
    section.hidden=false;
  }

  function initFavorites() {
    const meta=currentToolMeta(); if (!meta) return;
    const buttons=[...document.querySelectorAll('.js-favorite-tool,.js-favorite-inline')];
    const sync=()=>{ const saved=safeJsonRead(FAVORITES_KEY,[]).some(x=>x.id===meta.id); buttons.forEach(btn=>{ btn.setAttribute('aria-pressed',String(saved)); btn.textContent=saved?'★ Guardada':'☆ Guardar'; }); };
    buttons.forEach(btn=>btn.addEventListener('click',()=>{
      let saved=safeJsonRead(FAVORITES_KEY,[]); const exists=saved.some(x=>x.id===meta.id);
      saved=exists?saved.filter(x=>x.id!==meta.id):[meta,...saved.filter(x=>x.id!==meta.id)].slice(0,20);
      localStorage.setItem(FAVORITES_KEY,JSON.stringify(saved)); track('favorite_tool',{tool_id:meta.id,state:exists?'removed':'added'}); sync();
    })); sync();
  }

  function initWebVitals() {
    if (!('PerformanceObserver' in window)) return;
    try {
      let cls=0;
      const poCls=new PerformanceObserver(list=>{ list.getEntries().forEach(e=>{ if (!e.hadRecentInput) cls += e.value; }); });
      poCls.observe({type:'layout-shift',buffered:true});
      const poLcp=new PerformanceObserver(list=>{ const entries=list.getEntries(); const last=entries[entries.length-1]; if (last) window.__clicivoLcp=Math.round(last.startTime); });
      poLcp.observe({type:'largest-contentful-paint',buffered:true});
      addEventListener('pagehide',()=>track('web_vitals',{lcp_ms:window.__clicivoLcp||0,cls:Number(cls.toFixed(3))}),{once:true});
    } catch {}
  }

  function initResultActions() {
    const panel = document.querySelector('.result-panel');
    const output = document.querySelector('#result-body');
    if (!panel || !output) return;
    const form=document.querySelector('.tool-form');
    const update = () => panel.classList.toggle('has-result', !output.classList.contains('result-placeholder') && Boolean(output.textContent.trim()));
    new MutationObserver(update).observe(output, { childList:true, subtree:true, attributes:true, attributeFilter:['class'] }); update();
    document.addEventListener('click', async event => {
      const toolId = form?.dataset.tool || 'unknown';
      const copy = event.target.closest('.js-copy-result');
      if (copy) { copyText(cleanReportText(output.innerText), copy); track('result_copy', { tool_id:toolId, copy_type:'summary' }); }
      const clientCopy = event.target.closest('.js-copy-client');
      if (clientCopy) { copyText(buildClientReport(panel, output), clientCopy); track('result_copy_client', { tool_id:toolId }); }
      const pdf = event.target.closest('.js-download-pdf');
      if (pdf) { const generated = downloadResultPdf(panel, output); track(generated ? 'result_pdf_download' : 'result_print_fallback', { tool_id:toolId }); }
      const csv = event.target.closest('.js-download-csv');
      if (csv) {
        const rows=[['Clicivo',panel.dataset.reportTitle||form?.dataset.toolTitle||'Resultado'],['Fecha',new Date().toLocaleDateString('es-ES')],[],['DATOS UTILIZADOS',''],...collectInputs(form),[],['RESULTADO',''],...cleanReportText(output.innerText).split('\n').filter(Boolean).map(line=>[line,'']),[],['URL',location.href]];
        downloadCsv(`clicivo-${reportSlug(panel.dataset.reportTitle||toolId)}.csv`,rows); track('result_csv_download',{tool_id:toolId});
      }
      const save = event.target.closest('.js-save-scenario');
      if (save && form) { localStorage.setItem(SCENARIO_PREFIX+toolId,JSON.stringify(scenarioData(form))); save.textContent='Guardado ✓'; setTimeout(()=>save.textContent='Guardar escenario',1400); track('scenario_save',{tool_id:toolId}); }
      const load = event.target.closest('.js-load-scenario');
      if (load && form) { const data=safeJsonRead(SCENARIO_PREFIX+toolId,null); if (data) { restoreScenario(form,data); form.requestSubmit?.(); track('scenario_load',{tool_id:toolId}); } else { load.textContent='Sin escenario'; setTimeout(()=>load.textContent='Recuperar',1400); } }
      const share = event.target.closest('.js-share-result');
      if (share) {
        const text=buildClientReport(panel,output); let used='clipboard';
        try { if (navigator.share) { await navigator.share({title:panel.dataset.reportTitle||'Resultado Clicivo',text,url:location.href}); used='native'; } else { await navigator.clipboard.writeText(text); share.textContent='Copiado'; setTimeout(()=>share.textContent='Compartir',1400); } } catch { return; }
        track('result_share',{tool_id:toolId,share_method:used});
      }
      const print = event.target.closest('.js-print-result'); if (print) { track('result_print',{tool_id:toolId}); window.print(); }
    });
  }

  const UNIT_GROUPS = {
    length:[['m','Metros'],['km','Kilómetros'],['cm','Centímetros'],['mm','Milímetros'],['mi','Millas'],['yd','Yardas'],['ft','Pies'],['in','Pulgadas']],
    mass:[['kg','Kilogramos'],['g','Gramos'],['mg','Miligramos'],['lb','Libras'],['oz','Onzas'],['t','Toneladas']],
    volume:[['l','Litros'],['ml','Mililitros'],['m3','Metros cúbicos'],['gal_us','Galones US'],['qt_us','Cuartos US'],['cup_us','Tazas US']],
    temperature:[['C','Celsius · °C'],['F','Fahrenheit · °F'],['K','Kelvin · K']],
    speed:[['ms','Metros/segundo'],['kmh','Kilómetros/hora'],['mph','Millas/hora'],['knot','Nudos']],
    data:[['B','Bytes'],['KB','KB · decimal'],['MB','MB · decimal'],['GB','GB · decimal'],['KiB','KiB · binario'],['MiB','MiB · binario'],['GiB','GiB · binario']]
  };
  function initUnitConverter(form) {
    if (form?.dataset.tool !== 'unit-converter') return;
    const dimension=form.elements.dimension, from=form.elements.from, to=form.elements.to;
    const defaults={length:['km','mi'],mass:['kg','lb'],volume:['l','gal_us'],temperature:['C','F'],speed:['kmh','mph'],data:['GB','GiB']};
    const rebuild=(preserve=true)=>{
      const group=UNIT_GROUPS[dimension.value]||UNIT_GROUPS.length; const oldFrom=from.value,oldTo=to.value;
      const html=group.map(([value,label])=>`<option value="${value}">${label}</option>`).join(''); from.innerHTML=html;to.innerHTML=html;
      const [df,dt]=defaults[dimension.value]||group.slice(0,2).map(x=>x[0]);
      from.value=preserve&&group.some(x=>x[0]===oldFrom)?oldFrom:df; to.value=preserve&&group.some(x=>x[0]===oldTo)?oldTo:dt;
    };
    dimension.addEventListener('change',()=>rebuild(false)); rebuild(false);
    form.querySelector('.js-swap-units')?.addEventListener('click',()=>{const a=from.value;from.value=to.value;to.value=a;form.requestSubmit();track('unit_swap',{tool_id:'unit-converter'});});
  }

  function initTool() {
    const form = document.querySelector('.tool-form');
    const output = document.querySelector('#result-body');
    if (!form || !output) return;
    const id = form.dataset.tool;
    initUnitConverter(form);
    const deviceClass = window.innerWidth <= 720 ? 'mobile' : window.innerWidth <= 1024 ? 'tablet' : 'desktop';
    track('tool_view', { tool_id: id, device_class: deviceClass });
    let started = false;
    let startedAt = 0;
    const markStarted = () => {
      if (!started) {
        started = true;
        startedAt = Date.now();
        track('tool_start', { tool_id: id, device_class: deviceClass });
      }
    };
    form.addEventListener('input', markStarted, { once:false });
    form.addEventListener('change', markStarted, { once:false });
    if (ADVANCED_IDS.has(id)) return;
    const live = ['instagram-fonts','instagram-counter','instagram-spaces'].includes(id);
    const run = (userTriggered = false) => {
      if (!live && !validate(form)) {
        if (userTriggered) track('tool_error', { tool_id:id, error_type:'validation' });
        return;
      }
      try {
        const v = formValues(form);
        if (id === 'instagram-fonts') output.innerHTML = renderFonts(v.text || '');
        else if (id === 'instagram-counter') output.innerHTML = renderCounter(v);
        else if (id === 'instagram-spaces') {
          const formatted = formatInstagramText(v.text);
          output.innerHTML = `${hero('Texto preparado', `${Array.from(formatted).length} caracteres`)}<textarea id="formatted-output" readonly style="width:100%;min-height:180px;border:1px solid #dfe5ef;border-radius:14px;padding:12px">${escapeHtml(formatted)}</textarea>${note('Copia el resultado y pégalo en Instagram. El comportamiento puede variar según la versión de la aplicación.')}`;
        } else output.innerHTML = calculate(id, v);
        output.classList.remove('result-placeholder');
        form.querySelector('.error-message').textContent = '';
        if (userTriggered) {
          const elapsed = startedAt ? Math.max(0, Date.now() - startedAt) : 0;
          track('tool_complete', { tool_id:id, device_class:deviceClass, time_to_result_ms:elapsed });
          track('result_view', { tool_id:id, device_class:deviceClass });
          if (window.innerWidth <= 960) document.querySelector('.result-panel')?.scrollIntoView({ behavior:'smooth', block:'start' });
        }
      } catch (err) {
        const message = err.message || 'No se ha podido calcular. Revisa los datos.';
        form.querySelector('.error-message').textContent = message;
        if (userTriggered) track('tool_error', { tool_id:id, error_message:message.slice(0,100) });
      }
    };
    form.addEventListener('submit', e => { e.preventDefault(); markStarted(); run(true); });
    form.addEventListener('reset', () => { track('tool_reset', { tool_id:id }); setTimeout(() => run(false), 0); });
    if (live) form.addEventListener('input', () => run(started));
    run(false);

    document.addEventListener('click', e => {
      const btn = e.target.closest('.js-copy-output');
      if (btn) {
        copyText(btn.closest('.font-result').querySelector('output').textContent, btn);
        track('result_copy', { tool_id:id, result_type:'font' });
      }
      const main = e.target.closest('.js-copy-main');
      if (main) {
        copyText(document.querySelector('#formatted-output')?.value || '', main);
        track('result_copy', { tool_id:id, result_type:'formatted_text' });
      }
    });
  }

  if (typeof window !== 'undefined' && typeof location !== 'undefined' && ['localhost','127.0.0.1'].includes(location.hostname)) {
    window.ClicivoDebug = { calculate, loanPayment, loanSchedule, simulateCompound, formatInstagramText, renderFonts, renderCounter, UNIT_GROUPS };
  }

  rememberRecentTool();
  renderRecentTools();
  initFavorites();
  initCatalog();
  initAnalyticsInteractions();
  initScrollDepthAnalytics();
  initWebVitals();
  initResultActions();
  initTool();
})();
