const S={bootstrap:null,currentState:null,formFields:new Map(),selectedOperations:new Set(),lang:localStorage.getItem("sim-lang")||"zh"};
const METRICS=["population","food","water","energy","materials","morale","health","knowledge"];
const COLORS={population:"#b75b3a",food:"#78a54c",water:"#3b90bf",energy:"#e08c50",materials:"#7f70b4",morale:"#2f7b4a",health:"#c94d3b",knowledge:"#2f7b7a"};
const T={en:{brand:"Simulation Lab",title:"Settlement Simulator",sub:"Choose a language, a policy, and up to two tactical operations each turn.",mission:"Mission Brief",missionSub:"Clear goals and failure conditions.",setup:"Scenario Setup",setupSub:"Load a preset or build your own world.",preset:"Preset",loadPreset:"Load Preset",reset:"Reset World",params:"World Parameters",paramsSub:"These values define the opening state.",deck:"Command Deck",policy:"Policy",runTurns:"Auto-Run Turns",schedule:"Policy Schedule",scheduleHelp:"Optional comma-separated policy ids.",step:"Advance One Turn",run:"Run Batch",ops:"Tactical Operations",opsSub:"Pick up to two direct actions each turn.",opsHelp:"Operations are concrete interventions. Blocked cards cannot currently be executed.",opsEmpty:"No operation selected.",opsCount:"Selected operations: {n}/2",guide:"How To Read The World",guideSub:"Stabilize survival first, then invest for the future.",adviser:"Settlement Adviser",adviserSub:"System judgement and live recommendations.",timeline:"Timeline",timelineSub:"Population, resources, morale, health, and knowledge.",turn:"Turn Breakdown",turnSub:"What changed this turn and why.",event:"Event Log",eventSub:"Recent turn summaries.",ongoing:"Ongoing",victory:"Victory",defeat:"Collapse",objective:"Immediate Objective",fail:"Failure Threshold",viability:"Current Viability",survive:"Survive {n} more turn{s}",failText:"Population, morale, or health cannot hit zero",alive:"Population intact",lost:"Population lost",policyChosen:"Policy chosen",opsUsed:"Operations used",noOps:"No tactical operation",plain:"Plain-language result",noEvents:"No major events",production:"Production",consumption:"Consumption",selected:"Selected",available:"Available",blocked:"Blocked",healthy:"Healthy",watch:"Watch",critical:"Critical",judgement:"System Judgement",ready:"Ready",noReport:"No turns played yet. Pick a policy and start.",noLog:"No events yet. Start the simulation first.",noChart:"Run the simulation to draw the timeline."},zh:{brand:"模擬控制室",title:"聚落生存模擬",sub:"每回合同時選擇語言、政策與最多兩個戰術操作，直接改變局勢。",mission:"任務說明",missionSub:"先看懂怎麼贏、怎麼輸。",setup:"場景設定",setupSub:"載入預設，或自己建立世界。",preset:"預設場景",loadPreset:"載入預設",reset:"重置世界",params:"世界參數",paramsSub:"這些數值決定開局狀態。",deck:"指揮甲板",policy:"本回合政策",runTurns:"自動執行回合數",schedule:"政策排程",scheduleHelp:"可選，用逗號輸入政策 id。",step:"推進一回合",run:"批次執行",ops:"戰術操作",opsSub:"每回合最多選兩個直接行動。",opsHelp:"操作是玩家的即時干預。不能執行的卡片會直接標示原因。",opsEmpty:"目前沒有選擇操作。",opsCount:"已選操作：{n}/2",guide:"怎麼看懂世界",guideSub:"先穩住生存，再追求長線。",adviser:"聚落顧問",adviserSub:"系統判定與即時建議。",timeline:"時間走勢",timelineSub:"人口、資源、士氣、健康與知識。",turn:"回合解析",turnSub:"這一回合變了什麼，為什麼重要。",event:"事件紀錄",eventSub:"最近幾回合的摘要。",ongoing:"進行中",victory:"勝利",defeat:"崩潰",objective:"目前目標",fail:"失敗條件",viability:"目前存續性",survive:"再撐 {n} 回合",failText:"人口、士氣或健康不能掉到 0",alive:"人口仍在",lost:"人口已失守",policyChosen:"本回合政策",opsUsed:"使用的操作",noOps:"沒有戰術操作",plain:"白話結論",noEvents:"沒有重大事件",production:"生產",consumption:"消耗",selected:"已選擇",available:"可選",blocked:"不可執行",healthy:"健康",watch:"注意",critical:"危急",judgement:"系統判定",ready:"可執行",noReport:"還沒有跑過任何回合。先選政策再開始。",noLog:"目前沒有事件。先開始模擬。",noChart:"先跑幾個回合，這裡才會畫出走勢。"}};
const POLICY_ZH={balanced:"平衡治理",agriculture:"農業優先",industry:"工業推進",welfare:"民生穩定",research:"研究衝刺",rationing:"配給管制",quarantine:"隔離管制",infrastructure:"基建擴張"};
const OP_ZH={emergency_rations:"緊急配給",repair_grid:"修復電網",medical_outreach:"醫療外展",trade_convoy:"貿易車隊",drill_wells:"鑽井取水",festival:"舉辦慶典",survey_expedition:"勘查遠征",housing_drive:"住宅擴建"};
const FIELD_ZH={settlement_name:"聚落名稱",seed:"隨機種子",target_turns:"勝利回合",initial_population:"起始人口",starting_morale:"起始士氣",starting_health:"起始健康",starting_food:"起始食物",starting_water:"起始飲水",starting_energy:"起始能源",starting_materials:"起始建材",farmland:"農地",water_infrastructure:"供水設施",generator_capacity:"發電容量",medical_capacity:"醫療容量",housing_capacity:"住房容量",climate_severity:"氣候嚴酷度",disease_risk:"疾病風險",trade_access:"貿易通達度",hazard_frequency:"災害頻率",research_rate:"研究效率"};
const GROUP_ZH={Scenario:"場景",Population:"人口",Resources:"資源",Infrastructure:"基礎建設","World Conditions":"世界條件"};

document.addEventListener("DOMContentLoaded",async()=>{bind();await boot();});
const id=(x)=>document.getElementById(x),zh=()=>S.lang==="zh",t=(k)=>T[S.lang][k];

function bind(){
  id("load-preset-btn").onclick=()=>applyPreset(id("preset-select").value);
  id("reset-btn").onclick=resetWorld;
  id("step-btn").onclick=stepWorld;
  id("run-btn").onclick=runWorld;
  id("policy-select").onchange=renderPolicyDetail;
  id("lang-zh").onclick=()=>setLang("zh");
  id("lang-en").onclick=()=>setLang("en");
}

async function boot(){
  S.bootstrap=await api("/api/bootstrap");
  refreshUi();
  renderState(S.bootstrap.state);
}

function setLang(lang){
  S.lang=lang;
  localStorage.setItem("sim-lang",lang);
  document.documentElement.lang=lang==="zh"?"zh-Hant":"en";
  refreshUi();
}

function refreshUi(){
  if(!S.bootstrap)return;
  const selectedPreset=id("preset-select")?.value||S.bootstrap.defaultPreset;
  const selectedPolicy=id("policy-select")?.value||"balanced";
  const values=S.formFields.size?collectConfig():S.bootstrap.presets[selectedPreset];
  renderStatic();
  renderPresetOptions(selectedPreset);
  renderPolicyOptions(selectedPolicy);
  renderForm(values);
  renderPolicyDetail();
  if(S.currentState)renderState(S.currentState);
}

function renderStatic(){
  id("lang-zh").textContent="中文";
  id("lang-en").textContent="EN";
  id("lang-zh").classList.toggle("active",zh());
  id("lang-en").classList.toggle("active",!zh());
  const pairs=[["brand-eyebrow","brand"],["app-title","title"],["app-subtitle","sub"],["mission-title","mission"],["mission-subtitle","missionSub"],["setup-title","setup"],["setup-subtitle","setupSub"],["preset-label","preset"],["load-preset-btn","loadPreset"],["reset-btn","reset"],["parameters-title","params"],["parameters-subtitle","paramsSub"],["control-eyebrow","deck"],["policy-label","policy"],["run-turns-label","runTurns"],["schedule-label","schedule"],["schedule-help","scheduleHelp"],["step-btn","step"],["run-btn","run"],["operations-title","ops"],["operations-subtitle","opsSub"],["operations-help","opsHelp"],["guide-title","guide"],["guide-subtitle","guideSub"],["adviser-title","adviser"],["adviser-subtitle","adviserSub"],["timeline-title","timeline"],["timeline-subtitle","timelineSub"],["turn-title","turn"],["turn-subtitle","turnSub"],["event-title","event"],["event-subtitle","eventSub"]];
  pairs.forEach(([dom,key])=>id(dom).textContent=t(key));
  id("schedule-input").placeholder="agriculture, welfare, research";
  id("mission-cards").innerHTML=(zh()?[["勝利","撐到目標回合，且人口、士氣、健康沒有崩掉。"],["失敗","人口、士氣或健康任一項掉到 0 就輸。"],["玩家掌控","每回合不只選政策，還能額外下最多兩個戰術操作。"]]:[["Win","Reach the target turn without population, morale, or health collapsing."],["Lose","If population, morale, or health hits zero, the settlement collapses."],["Player Agency","Each turn you choose one policy and up to two tactical operations."]]).map(x=>`<div class="brief-item fade-in"><strong>${x[0]}</strong><p>${x[1]}</p></div>`).join("");
  id("guide-cards").innerHTML=(zh()?[["食物與水","這是生存底線，先穩住這兩項。"],["士氣與健康","居民狀態差時，所有問題都會放大。"],["建材與能源","支撐修復、擴建與即時操作。"],["知識","長線很強，但不能取代短期生存。"]]:[["Food and Water","These are the survival floor. Stabilize them first."],["Morale and Health","When people degrade, every other problem gets worse."],["Materials and Energy","They support repair, expansion, and tactical action."],["Knowledge","Powerful long-term, but never a substitute for survival stockpiles."]]).map(x=>`<div class="guide-card fade-in"><strong>${x[0]}</strong><p>${x[1]}</p></div>`).join("");
}

function renderPresetOptions(selected){
  id("preset-select").innerHTML=Object.keys(S.bootstrap.presets).map(name=>`<option value="${name}" ${name===selected?"selected":""}>${zh()?presetZh(name):name.replaceAll("_"," ")}</option>`).join("");
}

function renderPolicyOptions(selected){
  id("policy-select").innerHTML=S.bootstrap.policies.map(item=>`<option value="${item.name}" ${item.name===selected?"selected":""}>${policyLabel(item.name)}</option>`).join("");
}

function renderForm(values){
  const form=id("config-form");
  form.innerHTML="";
  S.formFields.clear();
  const groups=S.bootstrap.fieldSchema.reduce((acc,field)=>((acc[field.group]??=[]).push(field),acc),{});
  Object.entries(groups).forEach(([group,fields])=>{
    const section=document.createElement("section");
    section.className="form-group fade-in";
    section.innerHTML=`<h3>${zh()?(GROUP_ZH[group]||group):group}</h3>`;
    fields.forEach(field=>{
      const label=document.createElement("label");
      label.className="field";
      const input=document.createElement("input");
      input.type=field.type==="text"?"text":"number";
      input.name=field.name;
      if(field.min!==undefined)input.min=field.min;
      if(field.max!==undefined)input.max=field.max;
      if(field.step!==undefined)input.step=field.step;
      input.value=values[field.name];
      label.innerHTML=`<span>${zh()?(FIELD_ZH[field.name]||field.label):field.label}</span>`;
      label.appendChild(input);
      const help=document.createElement("small");
      help.textContent=field.help;
      label.appendChild(help);
      section.appendChild(label);
      S.formFields.set(field.name,{input,field});
    });
    form.appendChild(section);
  });
}

function renderPolicyDetail(){
  const name=id("policy-select").value;
  const hints=zh()?{balanced:"局勢不明時最安全。",agriculture:"缺糧缺水時優先。",industry:"缺建材時很有力。",welfare:"士氣或健康下滑時使用。",research:"局勢穩定時才值得壓。",rationing:"短期止血用。",quarantine:"疫情風險高時有價值。",infrastructure:"把現有庫存換成未來韌性。"}:{balanced:"Best default when unsure.",agriculture:"Use when food or water is low.",industry:"Use when you need more materials.",welfare:"Use when morale or health is slipping.",research:"Best when already stable.",rationing:"Emergency brake for shortages.",quarantine:"Useful against disease pressure.",infrastructure:"Convert stockpiles into future strength."};
  id("policy-detail").innerHTML=`<strong>${policyLabel(name)}</strong><p>${hints[name]||""}</p>`;
}

function applyPreset(name){
  const preset=S.bootstrap.presets[name];
  if(preset)renderForm(preset);
}

function collectConfig(){
  const config={};
  S.formFields.forEach(({input,field},key)=>{
    config[key]=field.type==="text"?input.value.trim():field.type==="int"?Number.parseInt(input.value,10):Number.parseFloat(input.value);
  });
  return config;
}

async function resetWorld(){renderState(await api("/api/reset",{method:"POST",body:{config:collectConfig()}}));}
async function stepWorld(){renderState(await api("/api/step",{method:"POST",body:{policy:id("policy-select").value,operations:[...S.selectedOperations]}}));}
async function runWorld(){const schedule=id("schedule-input").value.split(",").map(v=>v.trim()).filter(Boolean);renderState(await api("/api/run",{method:"POST",body:{turns:Number.parseInt(id("run-turns").value,10)||1,policy:id("policy-select").value,schedule,operations:[...S.selectedOperations]}}));}

function renderState(state){
  S.currentState=state;
  dropBlockedSelections(state.operationStatuses||[]);
  id("settlement-title").textContent=`${state.settlementName} - ${state.turn}/${state.targetTurns}`;
  id("status-text").textContent=translateStatus(state.statusText);
  renderOutcome(state);
  renderJudgement(state);
  renderObjectives(state);
  renderOperations(state);
  renderSummary(state);
  renderReport(state);
  renderLog(state.history||[]);
  renderAdvice(state);
  renderChart(state.history||[]);
}

function renderOutcome(state){
  const pill=id("outcome-pill");
  pill.className="outcome-pill";
  if(state.outcome==="victory")pill.classList.add("success");
  if(state.outcome==="defeat")pill.classList.add("danger");
  pill.textContent=t(state.outcome);
}

function renderJudgement(state){
  const j=state.judgement||{level:"stable",alerts:[]};
  const label=zh()?({stable:"穩定",warning:"警戒",critical:"危急",victory:"已達標",defeat:"崩潰"}[j.level]||j.level):titleCase(j.level);
  const alerts=(j.alerts||[]).length?(j.alerts||[]).map(x=>`<li>${translateJudgement(x)}</li>`).join(""):`<li>${zh()?"目前沒有立即性危機。":"No immediate crisis detected."}</li>`;
  id("judgement-panel").innerHTML=`<strong>${t("judgement")}: <span class="${j.level==="critical"||j.level==="defeat"?"danger":j.level==="warning"?"warning":"success"}">${label}</span></strong><ul>${alerts}</ul>`;
}

function renderObjectives(state){
  const left=Math.max(0,state.turnsRemaining??(state.targetTurns-state.turn));
  id("objective-banner").innerHTML=`<div class="objective-card"><p>${t("objective")}</p><strong>${t("survive").replace("{n}",left).replace("{s}",left===1?"":"s")}</strong></div><div class="objective-card"><p>${t("fail")}</p><strong>${t("failText")}</strong></div><div class="objective-card"><p>${t("viability")}</p><strong>${state.population>0?t("alive"):t("lost")}</strong></div>`;
}

function renderOperations(state){
  const statusMap=new Map((state.operationStatuses||[]).map(item=>[item.name,item]));
  const grid=id("operation-grid");
  grid.innerHTML=S.bootstrap.operations.map(op=>{
    const status=statusMap.get(op.name)||{canExecute:true,reason:"Ready."};
    const selected=S.selectedOperations.has(op.name);
    const label=opLabel(op.name);
    const effect=translateOperationEffect(op.name,op.effects);
    const reason=translateReason(status.reason);
    const badge=selected?t("selected"):status.canExecute?t("ready"):t("blocked");
    const cls=selected?"selected":status.canExecute?"ready":"blocked";
    return `<button type="button" class="operation-card fade-in ${selected?"selected":""} ${status.canExecute?"":"blocked"}" data-op="${op.name}"><strong>${label}</strong><p>${effect}</p><div class="operation-meta"><span class="operation-state ${cls}">${badge}</span></div><div class="operation-reason">${reason}</div></button>`;
  }).join("");
  grid.querySelectorAll("[data-op]").forEach(btn=>btn.onclick=()=>toggleOperation(btn.dataset.op,statusMap));
  id("operation-selection-note").textContent=S.selectedOperations.size?t("opsCount").replace("{n}",S.selectedOperations.size):t("opsEmpty");
}

function toggleOperation(name,statusMap){
  const status=statusMap.get(name);
  if(status&&!status.canExecute){alert(translateReason(status.reason));return;}
  if(S.selectedOperations.has(name))S.selectedOperations.delete(name);
  else{
    if(S.selectedOperations.size>=2){alert(t("opsCount").replace("{n}",2));return;}
    S.selectedOperations.add(name);
  }
  renderOperations(S.currentState);
}

function dropBlockedSelections(statuses){
  const blocked=new Set(statuses.filter(x=>!x.canExecute).map(x=>x.name));
  [...S.selectedOperations].forEach(name=>{if(blocked.has(name))S.selectedOperations.delete(name);});
}

function renderSummary(state){
  id("summary-cards").innerHTML=METRICS.map(key=>{
    const tone=toneFor(key,state);
    return `<article class="summary-card fade-in"><div class="summary-header"><span class="summary-label">${metricLabel(key)}</span><span class="${tone.cls}">${tone.label}</span></div><strong>${formatMetric(key,state[key])}</strong><div class="meter"><div class="meter-fill" style="width:${fillFor(key,state)}%; background:${COLORS[key]};"></div></div><p class="metric-hint">${metricHint(key,state)}</p></article>`;
  }).join("");
}

function renderReport(state){
  const report=state.lastReport;
  if(!report){id("last-report").innerHTML=`<div class="log-card"><p>${t("noReport")}</p></div>`;return;}
  const ops=report.operations.length?report.operations.map(name=>`<span class="chip operation-chip">${opLabel(name)}</span>`).join(""):`<span class="chip operation-chip">${t("noOps")}</span>`;
  const events=report.events.length?report.events.map(name=>`<span class="chip">${translateEvent(name)}</span>`).join(""):`<span class="chip">${t("noEvents")}</span>`;
  const prod=Object.entries(report.production).map(([k,v])=>row(metricLabel(k),`+${v}`,"success")).join("");
  const cons=Object.entries(report.consumption).map(([k,v])=>row(metricLabel(k),`-${v}`,"danger")).join("");
  const notes=(report.notes||[]).length?`<ul>${report.notes.map(n=>`<li>${translateNote(n)}</li>`).join("")}</ul>`:"";
  const evalAlerts=(report.evaluation?.alerts||[]).length?`<p class="metric-hint">${report.evaluation.alerts.map(translateJudgement).join(" / ")}</p>`:"";
  id("last-report").innerHTML=`<div class="log-card fade-in"><p><strong>${t("policyChosen")}:</strong> ${policyLabel(report.policyName||"balanced")}</p><p><strong>${t("opsUsed")}:</strong> ${ops}</p><p><strong>${t("plain")}:</strong> ${translateStatus(report.status)}</p><p>${events}</p><div><strong>${t("production")}</strong>${prod}</div><div><strong>${t("consumption")}</strong>${cons}</div>${notes}${evalAlerts}</div>`;
}

function renderLog(history){
  if(!history.length){id("event-log").innerHTML=`<div class="log-card"><p>${t("noLog")}</p></div>`;return;}
  id("event-log").innerHTML=[...history].reverse().slice(0,12).map(item=>`<div class="log-card fade-in"><p><strong>${zh()?`第 ${item.turn} 回合`:`Turn ${item.turn}`}</strong> - ${policyLabel(item.policy)}</p><p>${item.events.length?item.events.map(translateEvent).join(" / "):t("noEvents")}</p><p>${t("opsUsed")}: ${item.operations?.length?item.operations.map(opLabel).join(" / "):t("noOps")}</p><p>${metricLabel("population")} ${item.population} | ${metricLabel("food")} ${Math.round(item.food)} | ${metricLabel("water")} ${Math.round(item.water)} | ${metricLabel("morale")} ${item.morale}</p></div>`).join("");
}

function renderAdvice(state){
  const f=state.food/Math.max(1,state.population*.94),w=state.water/Math.max(1,state.population*1.08),cards=[];
  if(f<1.5||w<1.5)cards.push(zh()?["先止血","糧水已接近失控，先補生存資源。"]:["Stop the bleed first","Food or water is close to failure. Stabilize survival first."]);
  if(state.morale<45)cards.push(zh()?["士氣成為瓶頸","考慮民生穩定、緊急配給或慶典。"]:["Morale is the bottleneck","Consider Welfare, Emergency Rations, or Festival."]);
  if(state.health<45)cards.push(zh()?["健康進入危險區","醫療外展和隔離的價值在上升。"]:["Health is in danger","Medical Outreach and quarantine-style play are more valuable now."]);
  if(state.materials>180&&state.housingCapacity-state.population<18)cards.push(zh()?["可以鋪未來","住宅擴建或基建擴張都合理。"]:["You can build ahead","Housing Drive or Infrastructure Build now makes sense."]);
  if(!cards.length)cards.push(zh()?["目前判斷","聚落暫時穩定，你可以保守續推或主動出招。"]:["Current assessment","The settlement is stable. You can play safe or intervene more aggressively."]);
  id("adviser-notes").innerHTML=cards.slice(0,4).map(([a,b])=>`<div class="adviser-card fade-in"><strong>${a}</strong><p>${b}</p></div>`).join("");
}

function renderChart(history){
  const canvas=id("history-chart"),ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);ctx.fillStyle="rgba(255,255,255,0.5)";ctx.fillRect(0,0,w,h);
  if(!history.length){ctx.fillStyle="#56646c";ctx.font="18px Cambria";ctx.fillText(t("noChart"),30,40);return;}
  const p={top:24,right:20,bottom:38,left:44},cw=w-p.left-p.right,ch=h-p.top-p.bottom,maxTurn=Math.max(...history.map(x=>x.turn),1),keys=["population","food","water","morale","health","knowledge"],maxVal=Math.max(100,...history.flatMap(x=>keys.map(k=>Number(x[k])||0)));
  ctx.strokeStyle="rgba(0,0,0,0.1)";
  for(let i=0;i<=4;i+=1){const y=p.top+(ch/4)*i;ctx.beginPath();ctx.moveTo(p.left,y);ctx.lineTo(w-p.right,y);ctx.stroke();}
  keys.forEach(k=>{ctx.strokeStyle=COLORS[k];ctx.lineWidth=2.4;ctx.beginPath();history.forEach((item,index)=>{const x=p.left+((item.turn-1)/Math.max(1,maxTurn-1))*cw;const y=p.top+ch-((Number(item[k])||0)/maxVal)*ch;index===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});ctx.stroke();});
  let lx=p.left;ctx.fillStyle="#1a2328";ctx.font="12px Consolas";keys.forEach(k=>{ctx.fillStyle=COLORS[k];ctx.fillRect(lx,h-20,10,10);ctx.fillStyle="#1a2328";ctx.fillText(metricLabel(k),lx+14,h-11);lx+=92;});
}

function presetZh(name){return {balanced:"平衡起點",dry_badlands:"乾旱荒原",trade_hub:"商路中樞",frozen_frontier:"冰封前線",science_arcology:"科研穹頂"}[name]||name;}
function policyLabel(name){return zh()?(POLICY_ZH[name]||name):titleCase(name.replaceAll("_"," "));}
function opLabel(name){return zh()?(OP_ZH[name]||name):titleCase(name.replaceAll("_"," "));}
function metricLabel(key){return zh()?{population:"人口",food:"食物",water:"水",energy:"能源",materials:"建材",morale:"士氣",health:"健康",knowledge:"知識"}[key]||key:titleCase(key);}
function titleCase(value){return value.replaceAll("_"," ").replace(/\b\w/g,m=>m.toUpperCase());}
function toneFor(key,state){const value=Number(state[key]),bands={population:[40,90],food:[state.population*2,state.population*4],water:[state.population*2,state.population*4],energy:[state.population*1,state.population*2],materials:[60,180],morale:[40,70],health:[40,70],knowledge:[10,40]}[key];if(value<bands[0])return{label:t("critical"),cls:"danger"};if(value<bands[1])return{label:t("watch"),cls:"warning"};return{label:t("healthy"),cls:"success"};}
function fillFor(key,state){const value=Number(state[key]),cap={population:Math.max(state.population,state.housingCapacity,100),food:Math.max(state.population*5,200),water:Math.max(state.population*5,200),energy:Math.max(state.population*3,150),materials:300,morale:100,health:100,knowledge:Math.max(100,state.targetTurns*8)}[key];return Math.max(4,Math.min(100,(value/cap)*100));}
function metricHint(key,state){if(zh()){return {population:"人口是聚落的勞動力底盤。",food:state.food<state.population*2?"食物已接近短缺線。":"食物至少要維持數個回合的緩衝。",water:state.water<state.population*2?"飲水已接近短缺線。":"缺水通常比缺糧更危險。",energy:"能源支撐修復、醫療與公用系統。",materials:"建材決定你能不能修、換、擴。",morale:state.morale<40?"士氣太低，效率會惡化。":"士氣影響效率與承壓力。",health:state.health<40?"健康太低，危機會更致命。":"健康越高，居民越能撐住危機。",knowledge:"知識是長線優勢，不是短期救命藥。"}[key];}return {population:"Population is your workforce base.",food:state.food<state.population*2?"Food is near the shortage line.":"Keep food buffered for multiple turns.",water:state.water<state.population*2?"Water is near the shortage line.":"Water failures break settlements quickly.",energy:"Energy supports repair, medicine, and utilities.",materials:"Materials decide whether you can repair, trade, or build.",morale:state.morale<40?"Low morale is hurting output.":"Morale affects efficiency and resilience.",health:state.health<40?"Low health makes crises deadlier.":"Health determines how well people survive crises.",knowledge:"Knowledge is long-run leverage."}[key];}
function translateStatus(text){if(!zh())return text;return({"Victory. The settlement reached its horizon in stable condition.":"勝利。聚落在可維持狀態下撐到了目標時點。","Collapse. The settlement can no longer sustain itself.":"崩潰。聚落已無法再維持自身運作。","Fragile. Immediate stabilization is needed.":"脆弱。現在必須立刻止血穩局。","Strained. Resource shortages are approaching.":"吃緊。資源短缺已經逼近。","Stable. The colony is holding together.":"穩定。聚落目前還撐得住。"}[text]||text);}
function translateEvent(text){if(!zh())return text;return({Drought:"乾旱","Storm Damage":"風暴破壞","Disease Outbreak":"疫情爆發","Civil Dispute":"內部衝突","Market Windfall":"市場紅利","Bountiful Harvest":"豐收","Research Breakthrough":"研究突破","Migrant Arrival":"移民到來"}[text]||text);}
function translateJudgement(text){if(!zh())return text;return({"Food will run out very soon.":"食物很快就會耗盡。","Water is at immediate collapse risk.":"水資源已經接近立刻崩盤。","Health is in a lethal zone.":"健康已經進入致命區。","Morale is low enough to suppress output.":"士氣已經低到會拖垮產能。","Housing is overcrowded.":"住房已經過度擁擠。","Target horizon reached.":"已達成目標回合。"}[text]||text);}
function translateReason(text){if(!zh())return text;return({"Ready.":"可立即執行。","Needs 20 food and 8 materials.":"需要 20 食物與 8 建材。","Needs 16 materials.":"需要 16 建材。","Needs 18 materials and 10 energy.":"需要 18 建材與 10 能源。","Needs 18 food and 18 water.":"需要 18 食物與 18 水。","Needs 20 materials and 12 energy.":"需要 20 建材與 12 能源。","Needs 24 food and 12 energy.":"需要 24 食物與 12 能源。","Needs 8 materials and 14 energy.":"需要 8 建材與 14 能源。","Needs 28 materials and 6 energy.":"需要 28 建材與 6 能源。"}[text]||text);}
function translateOperationEffect(name,fallback){if(!zh())return fallback;return({emergency_rations:"消耗食物與建材，回補士氣與健康。",repair_grid:"消耗建材，快速恢復能源。",medical_outreach:"消耗建材與能源，提高健康與士氣。",trade_convoy:"用食物與水換外來建材。",drill_wells:"消耗建材與能源換取水與少量知識。",festival:"消耗食物與能源，大幅提升士氣。",survey_expedition:"用風險換知識與額外收益。",housing_drive:"消耗資源提高住房容量。"}[name]||fallback);}
function translateNote(text){if(!zh())return text;const patterns=[[/^Trade Convoy converted supplies into (\d+) imported materials\.$/,m=>`「貿易車隊」換回了 ${m[1]} 建材。`],[/^A drought consumed (\d+) water reserves\.$/,m=>`乾旱吃掉了 ${m[1]} 水儲備。`],[/^Storms destroyed (\d+) energy and (\d+) materials\.$/,m=>`風暴摧毀了 ${m[1]} 能源與 ${m[2]} 建材。`],[/^Infections reduced health by ([\d.]+) and cost (\d+) settlers\.$/,m=>`疫情讓健康下降 ${m[1]}，並失去 ${m[2]} 名居民。`],[/^Internal conflict cut morale by (\d+) and wasted (\d+) materials\.$/,m=>`內部衝突讓士氣下降 ${m[1]}，並浪費 ${m[2]} 建材。`],[/^Trading caravans added (\d+) materials and (\d+) food\.$/,m=>`商隊帶來了 ${m[1]} 建材與 ${m[2]} 食物。`],[/^An exceptional harvest brought in (\d+) food\.$/,m=>`豐收多帶來了 ${m[1]} 食物。`],[/^Researchers added (\d+) knowledge\.$/,m=>`研究人員增加了 ${m[1]} 點知識。`],[/^(\d+) migrants joined the settlement\.$/,m=>`${m[1]} 名移民加入了聚落。`],[/^Food shortage caused (\d+) starvation deaths\.$/,m=>`食物短缺造成 ${m[1]} 人餓死。`],[/^Water shortage caused (\d+) dehydration deaths\.$/,m=>`缺水造成 ${m[1]} 人脫水死亡。`],[/^(\d+) new settlers joined the population\.$/,m=>`新增了 ${m[1]} 名新居民。`],[/^(\d+) settlers were lost to ordinary attrition\.$/,m=>`有 ${m[1]} 名居民在日常消耗中流失。`]];for(const [re,fn]of patterns){const m=text.match(re);if(m)return fn(m);}return({"Emergency Rations could not be executed due to insufficient food or materials.":"「緊急配給」因食物或建材不足而無法執行。","Emergency Rations spent 20 food and 8 materials to calm the settlement.":"「緊急配給」消耗食物與建材，穩住了聚落情緒。","Repair Grid could not be executed due to insufficient materials.":"「修復電網」因建材不足而無法執行。","Repair Grid restored 50 energy at a cost of 16 materials.":"「修復電網」花 16 建材，恢復了 50 能源。","Medical Outreach could not be executed due to insufficient materials or energy.":"「醫療外展」因建材或能源不足而無法執行。","Medical Outreach spent 18 materials and 10 energy to improve health and morale.":"「醫療外展」消耗建材與能源，提升了健康與士氣。","Drill Wells could not be executed due to insufficient materials or energy.":"「鑽井取水」因建材或能源不足而無法執行。","Drill Wells added 60 water and 2 knowledge at the cost of materials and energy.":"「鑽井取水」消耗資源後帶來了 60 水與 2 知識。","Festival could not be executed due to insufficient food or energy.":"「舉辦慶典」因食物或能源不足而無法執行。","Festival lifted morale by spending 24 food and 12 energy.":"「舉辦慶典」消耗食物與能源，大幅提高士氣。","Survey Expedition could not be executed due to insufficient materials or energy.":"「勘查遠征」因建材或能源不足而無法執行。","Housing Drive could not be executed due to insufficient materials or energy.":"「住宅擴建」因建材或能源不足而無法執行。","Housing Drive increased housing capacity by 10.":"「住宅擴建」讓住房容量增加了 10。","Infrastructure teams lacked the 35 materials needed to expand capacity.":"基建隊缺少擴建所需的 35 建材。","Builders spent 35 materials to expand farms, utilities, medicine, and housing.":"建設隊花了 35 建材擴充農地、公用系統、醫療與住房。","Crowded housing reduced morale and health.":"住房過度擁擠，拉低了士氣與健康。","Energy shortages disrupted daily life and healthcare.":"能源不足打亂了日常生活與醫療系統。"}[text]||text);}
function formatMetric(key,value){return["morale","health","knowledge"].includes(key)?Number(value).toFixed(1):Math.round(Number(value));}
function row(label,value,cls){return `<div class="metric-row"><span>${label}</span><span class="${cls}">${value}</span></div>`;}
async function api(url,opt={}){const res=await fetch(url,{method:opt.method||"GET",headers:{"Content-Type":"application/json"},body:opt.body?JSON.stringify(opt.body):undefined});if(!res.ok)throw new Error(`Request failed: ${res.status}`);return res.json();}
