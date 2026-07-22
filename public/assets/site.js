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

  function initCookies() {
    const banner = document.querySelector('.cookie-banner');
    if (!banner) return;
    const key = 'clicivo-cookie-choice';
    const measurementId = 'G-B3DXJWJHYG';
    const loadAnalytics = () => {
      if (window.gtag) return;
      window.dataLayer = window.dataLayer || [];
      window.gtag = function(){ dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', measurementId, { anonymize_ip: true });
      const s = document.createElement('script');
      s.async = true; s.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
      document.head.appendChild(s);
    };
    const apply = choice => {
      banner.classList.remove('show');
      if (choice === 'accept') loadAnalytics();
    };
    const choice = localStorage.getItem(key);
    if (!choice) banner.classList.add('show'); else apply(choice);
    banner.querySelectorAll('[data-cookie]').forEach(btn => btn.addEventListener('click', () => {
      const value = btn.dataset.cookie;
      localStorage.setItem(key, value); apply(value);
    }));
    document.querySelectorAll('.js-cookie-settings').forEach(btn => btn.addEventListener('click', () => {
      localStorage.removeItem(key); banner.classList.add('show');
    }));
    document.addEventListener('click', e => {
      const link = e.target.closest('[data-affiliate]');
      if (link && window.gtag) window.gtag('event', 'affiliate_click', { affiliate: link.dataset.affiliate, page_path: location.pathname });
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
    form.querySelectorAll('input[type="number"]').forEach(el => { data[el.name] = Number(el.value); });
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

  function simulateCompound(initial, monthly, annualRate, years) {
    const months = Math.round(years * 12);
    if (annualRate <= -100) throw new Error('La rentabilidad neta debe ser superior a −100 %.');
    const r = Math.pow(1 + annualRate / 100, 1 / 12) - 1;
    let balance = initial; const yearly = [initial];
    for (let m = 1; m <= months; m++) {
      balance *= 1 + r; balance += monthly;
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
        const change = v.final - v.initial, growth = change / v.initial * 100, daily = change / v.days;
        return result('Crecimiento del periodo', pct(growth), [item('Cambio absoluto', `${change >= 0 ? '+' : ''}${integer(change)}`), item('Ritmo diario', `${number(daily)} seguidores`), item('Proyección 30 días', `${daily >= 0 ? '+' : ''}${integer(daily * 30)}`), item('Seguidores finales', integer(v.final))], 'La proyección mantiene el ritmo observado; no es una predicción.');
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
        const income = v.views / 1000 * v.rpm, monthly = income / v.months;
        return result('Ingresos estimados del periodo', money(income), [item('RPM introducido', money(v.rpm)), item('Ingreso mensual equivalente', money(monthly)), item('Proyección anual equivalente', money(monthly * 12)), item('Visualizaciones cualificadas', integer(v.views))], 'Escenario matemático basado en visualizaciones cualificadas y el RPM introducido.');
      }
      case 'youtube-rpm-revenue': {
        if (v.views <= 0) throw new Error('Las visualizaciones deben ser mayores que cero.');
        const rpm = v.revenue / v.views * 1000;
        return result('RPM calculado', money(rpm), [item('Ingresos', money(v.revenue)), item('Visualizaciones', integer(v.views)), item('Ingreso por visualización', money(v.revenue / v.views)), item('Ingresos por 100.000 vistas', money(rpm * 100))], 'Usa ingresos y visualizaciones del mismo periodo.');
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
        const base = v.views / 1000 * v.rpm, monthly = base / v.months;
        return result('Ingresos del periodo', money(base), [item('Escenario prudente (−25 %)', money(base * .75)), item('Escenario central', money(base)), item('Escenario optimista (+25 %)', money(base * 1.25)), item('Proyección anual equivalente', money(monthly * 12))], 'Escenarios basados únicamente en las visualizaciones y el RPM introducidos.');
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
        const sim = simulateCompound(v.initial, v.monthly, netRate, v.years);
        const contributed = v.initial + v.monthly * v.years * 12, gains = sim.balance - contributed;
        const real = v.inflation <= -100 ? sim.balance : sim.balance / Math.pow(1 + v.inflation / 100, v.years);
        const rows = sim.yearly.slice(1).map((value, i) => [i + 1, money(value), money(v.initial + v.monthly * (i + 1) * 12), money(value - (v.initial + v.monthly * (i + 1) * 12))]);
        return result('Capital final estimado', money(sim.balance), [item('Total aportado', money(contributed)), item('Ganancia estimada', money(gains)), item('Valor real tras inflación', money(real)), item('Rentabilidad neta usada', pct(netRate))], 'Simulación con capitalización mensual y tasa constante.', chart(sim.yearly) + table(['Año','Capital','Aportado','Ganancia'], rows.slice(-10)));
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
        const gross = salaryPending + vacation + v.extraPay + v.other - v.deductions;
        return result('Finiquito bruto estimado', money(gross), [item('Salario pendiente', money(salaryPending)), item('Vacaciones', money(vacation)), item('Pagas extra', money(v.extraPay)), item('Otros menos deducciones', money(v.other - v.deductions))], 'No incluye una indemnización por extinción ni calcula retenciones finales.');
      }
      case 'net-salary': {
        const irpf = v.gross * v.irpf / 100, ss = v.gross * v.ss / 100, net = v.gross - irpf - ss - v.other;
        const pays = Number(v.payments);
        return result('Neto anual estimado', money(net), [item(`Neto por paga (${pays})`, money(net / pays)), item('Neto mensual equivalente', money(net / 12)), item('IRPF estimado', money(irpf)), item('Cotización estimada', money(ss))], 'Porcentajes editables; no sustituye el cálculo real de nómina.');
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

  function initTool() {
    const form = document.querySelector('.tool-form');
    const output = document.querySelector('#result-body');
    if (!form || !output) return;
    const id = form.dataset.tool;
    const live = ['instagram-fonts','instagram-counter','instagram-spaces'].includes(id);
    const run = () => {
      if (!live && !validate(form)) return;
      try {
        const v = formValues(form);
        if (id === 'instagram-fonts') output.innerHTML = renderFonts(v.text || '');
        else if (id === 'instagram-counter') output.innerHTML = renderCounter(v);
        else if (id === 'instagram-spaces') {
          const formatted = formatInstagramText(v.text);
          output.innerHTML = `${hero('Texto preparado', `${Array.from(formatted).length} caracteres`)}<textarea id="formatted-output" readonly style="width:100%;min-height:180px;border:1px solid #dfe5ef;border-radius:14px;padding:12px">${escapeHtml(formatted)}</textarea>${note('Copia el resultado y pégalo en Instagram. El comportamiento puede variar según la versión de la aplicación.')}`;
        } else output.innerHTML = calculate(id, v);
        output.classList.remove('result-placeholder');
      } catch (err) {
        form.querySelector('.error-message').textContent = err.message || 'No se ha podido calcular. Revisa los datos.';
      }
    };
    form.addEventListener('submit', e => { e.preventDefault(); run(); });
    form.addEventListener('reset', () => setTimeout(run, 0));
    if (live) form.addEventListener('input', run);
    run();

    document.addEventListener('click', e => {
      const btn = e.target.closest('.js-copy-output');
      if (btn) copyText(btn.closest('.font-result').querySelector('output').textContent, btn);
      const main = e.target.closest('.js-copy-main');
      if (main) copyText(document.querySelector('#formatted-output')?.value || '', main);
    });
  }

  if (typeof window !== 'undefined' && typeof location !== 'undefined' && ['localhost','127.0.0.1'].includes(location.hostname)) {
    window.ClicivoDebug = { calculate, loanPayment, simulateCompound, formatInstagramText, renderFonts, renderCounter };
  }

  initCatalog();
  initCookies();
  initTool();
})();
