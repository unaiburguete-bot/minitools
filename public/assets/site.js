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
      if (m <= 12) rows.push([m, payment, interest, principalPart, balance]);
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
          item('Ritmo diario', `${number(daily)} seguidores`),
          item('Ritmo semanal', `${daily >= 0 ? '+' : ''}${integer(daily * 7)}`),
          item('Ritmo cada 30 días', `${daily >= 0 ? '+' : ''}${integer(daily * 30)}`),
          item('Fecha orientativa del objetivo', targetValue),
          item('Días estimados al objetivo', daysToTarget ? integer(daysToTarget) : '—')
        ], 'La proyección mantiene exactamente el ritmo observado; no contempla campañas, estacionalidad ni pérdidas futuras.', table(['Horizonte','Cambio proyectado','Seguidores estimados'], rows));
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
        const low = v.views / 1000 * v.rpmLow;
        const base = v.views / 1000 * v.rpm;
        const high = v.views / 1000 * v.rpmHigh;
        const monthly = base / v.months;
        const targetViews = v.rpm > 0 ? v.targetIncome / v.rpm * 1000 : 0;
        const rows = [10000,100000,500000,1000000,5000000].map(views => [
          integer(views), money(views/1000*v.rpmLow), money(views/1000*v.rpm), money(views/1000*v.rpmHigh)
        ]);
        return result('Ingresos del periodo · escenario central', money(base), [
          item('Escenario bajo', money(low)),
          item('Escenario alto', money(high)),
          item('Media mensual central', money(monthly)),
          item('Proyección anual central', money(monthly * 12)),
          item('Vistas cualificadas para la meta', targetViews ? integer(targetViews) : '—'),
          item('Objetivo introducido', money(v.targetIncome))
        ], 'Estimación matemática basada en visualizaciones cualificadas y en los RPM introducidos. La elegibilidad y el pago final dependen de TikTok.', table(['Visualizaciones cualificadas','RPM bajo','RPM central','RPM alto'], rows));
      }
      case 'youtube-rpm-revenue': {
        if (v.views <= 0) throw new Error('Las visualizaciones deben ser mayores que cero.');
        const rpm = v.revenue / v.views * 1000;
        const targetIncome = v.targetViews / 1000 * rpm;
        return result('RPM calculado', money(rpm), [
          item('Ingresos del periodo', money(v.revenue)),
          item('Visualizaciones del periodo', integer(v.views)),
          item('Ingreso por visualización', money(v.revenue / v.views)),
          item('Con 100.000 vistas', money(rpm * 100)),
          item('Con 1 millón de vistas', money(rpm * 1000)),
          item(`Con ${integer(v.targetViews)} vistas`, money(targetIncome))
        ], 'Usa ingresos y visualizaciones del mismo periodo y analiza Shorts y vídeos largos por separado.');
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
        const income = v.views / 1000 * v.rpm;
        return result('Ingresos estimados', money(income), [item('Visualizaciones', integer(v.views)), item('RPM introducido', money(v.rpm)), item('Por 100.000 vistas', money(v.rpm * 100)), item('Por 1 millón de vistas', money(v.rpm * 1000))], 'El RPM real de Shorts puede variar ampliamente.');
      }
      case 'youtube-income': {
        if (!(v.rpmLow <= v.rpm && v.rpm <= v.rpmHigh)) throw new Error('Ordena los escenarios: RPM bajo ≤ central ≤ alto.');
        if (v.months <= 0) throw new Error('El periodo debe ser mayor que cero.');
        const low = v.views / 1000 * v.rpmLow, base = v.views / 1000 * v.rpm, high = v.views / 1000 * v.rpmHigh, monthly = base / v.months;
        const targetViews = v.rpm > 0 ? v.targetIncome / v.rpm * 1000 : 0;
        const rows = [10000,100000,250000,500000,1000000].map(views => [
          integer(views), money(views/1000*v.rpmLow), money(views/1000*v.rpm), money(views/1000*v.rpmHigh)
        ]);
        return result('Ingresos del periodo · escenario central', money(base), [
          item('Escenario bajo', money(low)),
          item('Escenario alto', money(high)),
          item('Media mensual central', money(monthly)),
          item('Proyección anual central', money(monthly * 12)),
          item('Vistas para el objetivo', targetViews ? integer(targetViews) : '—'),
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
        const months = Math.round(v.years * 12), schedule = loanSchedule(v.principal, v.rate, months);
        const total = schedule.payment * months, rows = schedule.rows.map(r => [r[0], money(r[1]), money(r[2]), money(r[3]), money(r[4])]);
        return result('Cuota mensual estimada', money(schedule.payment), [item('Intereses totales', money(schedule.interest)), item('Total de cuotas', money(total)), item('Coste con gastos iniciales', money(total + v.fees)), item('Número de cuotas', integer(months))], 'Sistema francés a tipo fijo; no incluye seguros ni variaciones contractuales.', table(['Mes','Cuota','Interés','Capital','Pendiente'], rows));
      }
      case 'personal-loan': {
        const months = Math.max(1, Math.round(v.years * 12)), schedule = loanSchedule(v.principal, v.rate, months);
        const opening = v.principal * v.commission / 100, total = schedule.payment * months + opening;
        return result('Cuota mensual estimada', money(schedule.payment), [item('Intereses', money(schedule.interest)), item('Comisión apertura', money(opening)), item('Coste total', money(total)), item('Cuotas', integer(months))], 'La TAE de una oferta puede incorporar otros costes y calendarios de pago.');
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
        return result('Margen sobre ventas', pct(margin), [item('Beneficio unitario', money(profit)), item('Markup sobre coste', Number.isFinite(markup) ? pct(markup) : '∞'), item('Beneficio total', money(profit * v.units)), item('Precio para margen objetivo', Number.isFinite(targetPrice) ? money(targetPrice) : 'No definido')], 'Compara siempre coste y precio con el mismo criterio de impuestos.');
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
        const irpf = v.gross * v.irpf / 100, ss = v.gross * v.ss / 100, net = v.gross - irpf - ss - v.other;
        const pays = Number(v.payments), totalDeductions = irpf + ss + v.other;
        return result('Neto anual estimado', money(net), [
          item(`Neto por paga (${pays})`, money(net / pays)),
          item('Neto mensual equivalente', money(net / 12)),
          item('IRPF estimado', money(irpf)),
          item('Cotización estimada', money(ss)),
          item('Deducciones totales', money(totalDeductions)),
          item('Tipo efectivo total', pct(v.gross ? totalDeductions / v.gross * 100 : 0))
        ], 'Porcentajes editables; no sustituye una nómina real ni el cálculo oficial de retenciones.');
      }
      case 'vacation-days': {
        const worked = daysBetween(v.start, v.end, true);
        if (!(worked > 0)) throw new Error('La fecha final debe ser igual o posterior a la inicial.');
        const accrued = v.annual * worked / 365.2425, pending = accrued - v.taken;
        return result('Vacaciones pendientes estimadas', `${number(pending)} días`, [item('Generadas', `${number(accrued)} días`), item('Ya disfrutadas', `${number(v.taken)} días`), item('Días trabajados', integer(worked)), item('Referencia anual', `${number(v.annual)} días`)], 'El convenio, el contrato y la política de redondeo pueden modificar el resultado.');
      }
      case 'employer-cost': {
        const contribution = v.gross * v.rate / 100, total = v.gross + contribution + v.other + v.bonus;
        return result('Coste anual estimado', money(total), [item('Coste mensual medio', money(total / 12)), item('Cotización empresarial estimada', money(contribution)), item('Otros costes + variable', money(v.other + v.bonus)), item('Coste adicional sobre bruto', pct(v.gross ? (total - v.gross) / v.gross * 100 : 0))], 'La tasa empresarial es una hipótesis editable y no una cotización universal.');
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

  function initResultActions() {
    const panel = document.querySelector('.result-panel');
    const output = document.querySelector('#result-body');
    if (!panel || !output) return;
    const update = () => panel.classList.toggle('has-result', !output.classList.contains('result-placeholder') && Boolean(output.textContent.trim()));
    new MutationObserver(update).observe(output, { childList:true, subtree:true, attributes:true, attributeFilter:['class'] });
    update();
    document.addEventListener('click', event => {
      const toolId = document.querySelector('.tool-form')?.dataset.tool || 'unknown';
      const copy = event.target.closest('.js-copy-result');
      if (copy) {
        copyText(cleanReportText(output.innerText), copy);
        track('result_copy', { tool_id:toolId, copy_type:'summary' });
      }
      const clientCopy = event.target.closest('.js-copy-client');
      if (clientCopy) {
        copyText(buildClientReport(panel, output), clientCopy);
        track('result_copy_client', { tool_id:toolId });
      }
      const pdf = event.target.closest('.js-download-pdf');
      if (pdf) {
        const generated = downloadResultPdf(panel, output);
        track(generated ? 'result_pdf_download' : 'result_print_fallback', { tool_id:toolId });
      }
      const print = event.target.closest('.js-print-result');
      if (print) {
        track('result_print', { tool_id:toolId });
        window.print();
      }
    });
  }

  function initTool() {
    const form = document.querySelector('.tool-form');
    const output = document.querySelector('#result-body');
    if (!form || !output) return;
    const id = form.dataset.tool;
    track('tool_view', { tool_id: id });
    let started = false;
    const markStarted = () => {
      if (!started) {
        started = true;
        track('tool_start', { tool_id: id });
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
        if (userTriggered) track('tool_complete', { tool_id:id });
      } catch (err) {
        const message = err.message || 'No se ha podido calcular. Revisa los datos.';
        form.querySelector('.error-message').textContent = message;
        if (userTriggered) track('tool_error', { tool_id:id, error_message:message.slice(0,100) });
      }
    };
    form.addEventListener('submit', e => { e.preventDefault(); markStarted(); run(true); });
    form.addEventListener('reset', () => setTimeout(() => run(false), 0));
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
    window.ClicivoDebug = { calculate, loanPayment, simulateCompound, formatInstagramText, renderFonts, renderCounter };
  }

  initCatalog();
  initAnalyticsInteractions();
  initResultActions();
  initTool();
})();
