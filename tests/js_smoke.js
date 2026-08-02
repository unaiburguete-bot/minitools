'use strict';
global.window = global;
global.document = {querySelector:()=>null,querySelectorAll:()=>[],addEventListener:()=>{},head:{appendChild:()=>{}},body:{appendChild:()=>{}}};
global.localStorage = {getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
global.location = {search:'',pathname:'/',hostname:'localhost'};
Object.defineProperty(global, 'navigator', {value:{clipboard:{writeText:async()=>{}}}, configurable:true});
require('../public/assets/site.js');
const t = global.ClicivoDebug;
if (!t) throw new Error('Debug helpers were not exposed.');
const compound = t.calculate('compound-interest',{initial:10000,monthly:200,rate:6,fee:.3,inflation:2,years:15});
if (!compound.includes('Capital final estimado')) throw new Error('Compound interest smoke test failed.');
const mortgage = t.calculate('mortgage',{principal:200000,rate:3,years:25,fees:0});
if (!mortgage.includes('Cuota mensual estimada')) throw new Error('Mortgage smoke test failed.');
const vacation = t.calculate('vacation-days',{start:'2026-01-01',end:'2026-07-22',annual:30,taken:5});
if (!vacation.includes('Vacaciones pendientes estimadas')) throw new Error('Vacation smoke test failed.');

const tiktokIncome = t.calculate('tiktok-income',{views:500000,rpmLow:0.3,rpm:0.5,rpmHigh:0.8,months:1,targetIncome:500});
if (!tiktokIncome.includes('Ingresos del periodo') || !tiktokIncome.includes('Vistas cualificadas para la meta')) throw new Error('TikTok income smoke test failed.');

const youtubeIncome = t.calculate('youtube-income',{views:250000,rpmLow:2,rpm:3.5,rpmHigh:5,months:1,targetIncome:1000});
if (!youtubeIncome.includes('Ingresos del periodo') || !youtubeIncome.includes('Vistas para el objetivo')) throw new Error('YouTube income smoke test failed.');
const youtubeRpm = t.calculate('youtube-rpm-revenue',{revenue:425,views:100000,targetViews:250000});
if (!youtubeRpm.includes('RPM calculado') || !youtubeRpm.includes('250.000')) throw new Error('YouTube RPM smoke test failed.');
const severance = t.calculate('severance',{monthly:2200,salaryDays:15,vacationDays:8,extraPay:500,other:0,includeCompensation:true,compensation:3000,deductions:0});
if (!severance.includes('Total bruto orientativo') || !severance.includes('Indemnización añadida')) throw new Error('Finiquito smoke test failed.');

const formatted = t.formatInstagramText('Uno\n\nDos');
if (!formatted.includes('\u2800')) throw new Error('Instagram spacing smoke test failed.');
console.log('JavaScript smoke tests passed.');
