/* Ars Magna Defluens — local coordination console.
 * Interface logic only; Python delegates all execution to WordBench.
 */
(() => {
  'use strict';
  const TOKEN = new URLSearchParams(location.search).get('token') || '';
  let locale = 'fr';
  try {locale = localStorage.getItem('defluens-lang') === 'en' ? 'en' : 'fr';} catch (_) { /* Restricted browser context. */ }
  let page = 'overview';
  let state = null;
  let selectedCode = 'Fre';
  let languageData = null;
  let noticeTimeout = null;
  let lastState = '';
  const el = (id) => document.getElementById(id);
  const t = (fr,en) => locale === 'fr' ? fr : en;
  const safe = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  async function api(path, opts={}) {
    const response = await fetch('/api/' + path, {
      ...opts,
      headers: {'X-Defluens-Token':TOKEN,...(opts.body?{'Content-Type':'application/json'}:{}),...(opts.headers||{})},
      cache:'no-store'
    });
    let result;
    try {result = await response.json();} catch {throw Error(t('Réponse locale invalide','Invalid local response'));}
    if (!response.ok) throw Error(result.error || `${response.status}`);
    return result;
  }
  function tell(message,error=false) {
    const n=el('notice'); n.textContent=message; n.classList.toggle('error',error);n.hidden=false;
    clearTimeout(noticeTimeout);noticeTimeout=setTimeout(()=>{n.hidden=true;},5800);
  }
  function applyLocale(){
    document.documentElement.lang=locale;
    document.querySelectorAll('[data-fr][data-en]').forEach(n => {
      n.innerHTML=n.dataset[locale];
    });
    el('language-toggle').textContent=locale==='fr'?'EN':'FR';
    el('current-date').textContent=new Intl.DateTimeFormat(locale==='fr'?'fr-CA':'en-CA',{day:'2-digit',month:'long',year:'numeric'}).format(new Date());
    if(state)renderEverything();
    renderV06Catalog();
    // Typed input options are translated by data-fr/data-en; IDs remain stable.
    document.querySelectorAll('.v05-language-chip').forEach(label => {const iso=label.querySelector('input')?.value;const entry=state?.languages.find(l=>saIsoCodes[l.code]===iso);if(entry)label.querySelector('span').textContent=entry[locale];});
  }
  function route(name){
    if(!['overview','campaigns','studio','languages','ecosystem','settings'].includes(name))return;
    page=name;
    document.querySelectorAll('.page').forEach(n=>n.classList.toggle('active',n.id==='page-'+page));
    document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n.dataset.page===page));
    if (location.hash.slice(1)!==page) history.replaceState(null,'','#'+page);
    if(name==='languages') loadLanguage(selectedCode);
    if(name==='settings') renderSettings();
    if(name==='studio') {refreshCandidateStatus();refreshV07Status();renderV06Languages();}
    window.scrollTo({top:0,behavior:'instant'});
  }
  function renderEverything(){
    renderOverview();renderInspector();renderSystems();renderLanguagesList();renderJob();
    if(languageData)renderScenarios();
    if(page==='settings')renderSettings();
    renderStudioLanguages();renderV06Languages();
  }
  function renderOverview(){
    const report=state.latest;
    el('metric-candidates').textContent=report?`${report.totals.candidates}/${report.totals.attempted}`:'—';
    el('metric-errors').textContent=report?String(report.totals.failures+report.totals.timeouts):'—';
    const target=el('latest-overview');
    if(!report){
      target.innerHTML=`<div class="empty-state">${safe(t('Aucun rapport WordBench trouvé dans Downloads. Vérifie les chemins, ou exécute un balayage rapide.','No WordBench report found in Downloads. Check your paths, or run a smoke test.'))}</div>`;
      return;
    }
    const n=report.totals;
    const ratio=n.attempted?Math.min(100,Math.max(0,100*n.candidates/n.attempted)):0;
    const labels=(report.entries||[]).map(x=>`<span class="lang-tag" title="${safe(x.name_fr)}">${safe(x.code)}</span>`).join('');
    target.innerHTML=`<div class="batch-summary-row"><span>${safe(t('Campagne','Campaign'))} <b>${safe(report.mode)}</b></span><strong>${n.candidates} / ${n.attempted}</strong></div>
      <div class="batch-fine">${safe(report.archive_name)}</div>
      <div class="progress-track" role="progressbar" aria-valuenow="${ratio}" aria-valuemin="0" aria-valuemax="100"><span style="width:${ratio}%"></span></div>
      <div class="batch-fine">${safe(t('Générations candidates','Candidate generations'))} · ${n.failures+n.timeouts} ${safe(t('échec(s) et délai(s)','errors and timeouts'))} · ${report.entries.length} ${safe(t('langues','languages'))}</div>
      <div class="tag-row">${labels}</div>`;
  }
  function renderInspector(){
    const h=state.health, names=[['dik','diK lexical'],['gf','GF 3.12'],['rgl','GF RGL'],['wordbench','GF WordBench'],['semantik','SemantiK Architect'],['runtime_orchestrator','Runtime Orchestrator'],['observatory','GF Observatory'],['compendium','AI Compendium']];
    el('health-list').innerHTML=names.map(([code,label])=>`<div class="health-row"><span>${safe(label)}</span><span class="health-state ${h[code]?'':'missing'}">${safe(h[code]?t('Détecté','Found'):t('Non trouvé','Missing'))}</span></div>`).join('');
    if (state.latest){
      const r=state.latest;
      el('inspector-report').innerHTML=`<strong>${r.totals.candidates} / ${r.totals.attempted}</strong><div>${safe(t('phrases candidates','candidate sentences'))}</div>
        <div>${safe(r.entries.length)} ${safe(t('langues','languages'))} · ${r.totals.failures+r.totals.timeouts} ${safe(t('échecs','failures'))}</div><div style="margin-top:9px;color:#a15536">${safe(t('Non certifié linguistiquement','Not linguistically certified'))}</div>`;
    } else el('inspector-report').textContent=t('Aucune campagne trouvée dans les archives locales.','No campaign found in local archives.');
  }
  function renderSystems(){
    const systems=[
      ['dik','diK · Lexical Authority','00',t('Dictionnaires, sens et provenance; aucune grammaire inventée.','Dictionaries, sense records and provenance; no guessed grammar.'),'dik',false],
      ['wordbench','GF WordBench','01',t('Tests GF, scénarios et archives de preuves.','GF tests, scenarios and evidence archives.'),'wordbench',true],
      ['observatory','GF Observatory','02',t('Vue diagnostique et état des langues.','Diagnostic view and language status.'),'observatory',true],
      ['compendium','GF RGL AI Compendium','03',t('Contrats, méthodes de réparation et provenance.','Contracts, repair methods and provenance.'),'compendium',false],
      ['rgl','GF / RGL','04',t('Grammaires et lexiques de référence, en lecture seule ici.','Reference grammar and lexicons, read-only here.'),'rgl',false],
      ['semantik','SemantiK Architect','05',t('Planification sémantique et réalisation via GF.','Semantic planning and GF realization.'),'semantik',false],
      ['runtime_orchestrator','SemantiK Runtime Orchestrator','06',t('Conformité, promotion et retour arrière des RuntimeSets.','RuntimeSet release gates, promotion and rollback.'),'runtime_orchestrator',false]
    ];
    el('systems-list').innerHTML=systems.map(([key,title,no,description,target,launch])=>{
      const ok=!!state.health[key];
      return `<article class="system-card"><span class="system-icon">${no}</span><span class="system-status ${ok?'':'missing'}">${safe(ok?t('Installation détectée','Installation found'):t('Chemin à vérifier','Check path'))}</span><h3>${safe(title)}</h3><p>${safe(description)}</p>
        <div class="system-actions">${launch?`<button class="btn btn-primary" data-action="launch" data-target="${target}" ${ok?'':'disabled'}>${safe(t('Lancer l’application','Launch application'))} ↗</button>`:''}
        <button class="btn btn-outline" data-action="open" data-target="${target}" ${ok?'':'disabled'}>${safe(t('Ouvrir le dossier','Open folder'))}</button></div></article>`;
    }).join('');
  }
  function renderLanguagesList(){
    const latest=state.latest;
    const counts=Object.fromEntries((latest?.entries||[]).map(x=>[x.code,`${x.candidates}/${x.attempted}`]));
    el('language-buttons').innerHTML=state.languages.map(x=>`<button type="button" class="language-item ${x.code===selectedCode?'active':''}" data-language="${safe(x.code)}"><span>${safe(x[locale])}</span><span class="amount">${safe(counts[x.code]||'—')}</span></button>`).join('');
    if(!latest){
      el('selected-language-title').textContent=t('Aucun rapport','No report');
      el('scenario-list').innerHTML=`<div class="empty-state">${safe(t('Exécute une campagne pour afficher les phrases réelles.','Run a campaign to view real sentences.'))}</div>`;
      el('selected-context').textContent=t('Aucune sortie GF disponible.','No GF outputs available.');
    }
  }
  async function loadLanguage(code){
    if (!state?.latest) return;
    selectedCode=code;renderLanguagesList();
    el('scenario-list').innerHTML=`<div class="empty-state">${safe(t('Lecture des preuves…','Reading evidence…'))}</div>`;
    try {
      const data=await api('language?code='+encodeURIComponent(code));
      if(selectedCode!==code)return;
      languageData=data;renderScenarios();
    }catch(e){languageData=null;el('selected-language-title').textContent=code;el('scenario-list').textContent=e.message;}
  }
  function renderScenarios(){
    if(!languageData || !state)return;
    const raw=el('show-raw').checked;
    el('selected-language-title').textContent=languageData['name_'+locale];
    el('selected-context').textContent=t('Sorties produites par GF · candidates non approuvées · provenance et sorties brutes conservées.','GF-generated outputs · unapproved candidates · raw evidence and provenance preserved.');
    el('scenario-list').innerHTML=languageData.scenarios.map((x,i)=>{
      const sentence=(raw?x.raw:x.candidate)||t('Aucune phrase','No sentence');
      const status=x.status==='candidate_for_review';
      return `<article class="scenario-item"><div class="scenario-top"><span class="scenario-id">${String(i+1).padStart(2,'0')} · ${safe(x.id)}</span><span class="status-mark ${status?'':'failure'}">${safe(status?t('Candidate GF','GF candidate'):x.status)}</span></div>
          <p>${safe(sentence)}</p><div class="expected">${safe(t('Intention : ','Intent: '))}${safe(x.meaning_en)}</div></article>`;
    }).join('');
  }
  function renderJob(){
    const j=state.job;
    const running=j.state==='running';
    const stateLabels={idle:t('Aucune tâche en cours','No active job'),running:t('Exécution en cours…','Running…'),completed:t('Terminé (code 0)','Completed (exit 0)'),failed:t('Échec du processus','Process failed'),stopped:t('Arrêt demandé','Stop requested')};
    el('job-state').textContent=`${j.mode||'WordBench'} — ${stateLabels[j.state]||j.state}`;
    el('job-led').classList.toggle('running',running);
    el('stop-run').disabled=!running;
    document.querySelectorAll('.run-btn').forEach(b=>b.disabled=running);
    const log=el('job-output');
    const content=j.lines?.length?j.lines.slice(-190).join('\n') : t('> Ars Magna Defluens\n> Les journaux d’exécution WordBench apparaîtront ici.','> Ars Magna Defluens\n> WordBench execution logs will appear here.');
    if(log.textContent!==content){
      const nearBottom=log.scrollHeight-log.scrollTop-log.clientHeight<75;
      log.textContent=content;
      if(nearBottom)log.scrollTop=log.scrollHeight;
    }
    if(lastState==='running' && !running){
      tell(j.state==='completed'?t('WordBench a terminé. Les derniers rapports ont été actualisés.','WordBench finished. The latest reports were refreshed.'):t('WordBench s’est arrêté : consulte le journal.','WordBench stopped; inspect the log.'),j.state!=='completed');
    }
    lastState=j.state;
  }
  const settingsNames={
    dik:['diK (lexical) · C:\\mycode\\diK','diK lexical source'],
    wordbench:['GF WordBench','GF WordBench'],observatory:['GF Observatory','GF Observatory'],
    compendium:['GF RGL AI Compendium','GF RGL AI Compendium'],rgl:['Sources RGL','RGL source tree'],
    gf:['Compilateur gf.exe','GF compiler (gf.exe)'],reports:['Archives de campagne (Downloads)','Campaign archives (Downloads)'],
    alignment:['Rapports d’alignement','Alignment reports'],
    semantik:['SemantiK Architect (source)','SemantiK Architect (source)'],
    runtime_orchestrator:['Runtime Orchestrator (source)','Runtime Orchestrator (source)']
  };
  function renderSettings(){
    if(!state)return;
    const form=el('settings-fields');
    const active=document.activeElement;
    if(active && form.contains(active))return;
    form.innerHTML=Object.entries(settingsNames).map(([key,names])=>{
      const value=state.paths[key]||'';
      return `<div class="setting-row"><label for="setting-${key}"><span>${safe(names[locale==='fr'?0:1])}</span><span class="path-status ${state.health[key]?'':'missing'}">${safe(state.health[key]?t('Trouvé','Found'):t('À vérifier','Check'))}</span></label><input id="setting-${key}" name="${key}" spellcheck="false" autocomplete="off" value="${safe(value)}"></div>`;
    }).join('');
  }
  async function refresh(){
    try{
      const s=await api('status');
      const changed=JSON.stringify(s.latest)!==JSON.stringify(state?.latest)||JSON.stringify(s.paths)!==JSON.stringify(state?.paths);
      state=s;
      renderOverview();renderInspector();renderSystems();renderJob();renderStudioLanguages();
      if(changed){renderLanguagesList();if(page==='languages')loadLanguage(selectedCode);if(page==='settings')renderSettings();}
    }catch(e){if(!state)tell(t('Connexion au serveur local impossible : ','Unable to connect to local server: ')+e.message,true);}
  }
  async function command(action,data){
    try{
      const result=await api(action,{method:'POST',body:JSON.stringify(data)});
      if(action==='run') {route('campaigns');tell(t('WordBench démarre…','WordBench is starting…'));}
      else if(action==='settings')tell(t('Chemins enregistrés.','Paths saved.'));
      else if(action==='stop')tell(t('Arrêt demandé.','Stop requested.'));
      else if(action==='quit'){tell(t('Console arrêtée. Tu peux fermer cet onglet.','Console stopped. You may close this tab.'));return;}
      else tell(result.message||t('Action effectuée.','Action completed.'));
      await refresh();
    }catch(e){tell(e.message,true);}
  }
  async function studioCall(kind, data) {
    const output=el('semantic-output'), label=el('semantic-output-label');
    label.textContent=t('Commande SA en cours…','SA command running…');
    output.textContent='…';
    try {
      const response=await api(kind==='capabilities'?'semantik/capabilities':kind==='example'?'semantik/example':
        kind==='readiness'?'semantik/readiness':'semantik/request',
        kind==='capabilities'||kind==='example'?{}:{method:'POST',body:JSON.stringify(data)});
      if(kind==='example') {
        el('semantic-request').value=JSON.stringify(response.example,null,2);
        label.textContent=t('Exemple structuré chargé depuis SemantiK Architect','Structured example loaded from SemantiK Architect');
        output.textContent=response.origin;
        return;
      }
      const ok=response.ok !== false && response.result?.status!=='BLOCKED';
      label.textContent=ok?t('Commande exécutée (vérifier le statut de conformité)','Command executed (check conformance status)'):
        t('Non disponible / refus du moteur amont','Not available / upstream engine refused');
      label.classList.toggle('is-error',!ok);
      output.textContent=JSON.stringify(response.result??response,null,2);
    } catch(error) {
      label.textContent=t('Commande refusée','Command rejected');
      label.classList.add('is-error');
      output.textContent=error.message;
    }
  }
  function semanticInput(action){
    let request;
    try {request=JSON.parse(el('semantic-request').value);if(!request||Array.isArray(request)||typeof request!=='object')throw Error('JSON object required');}
    catch(error){tell(t('JSON invalide : ','Invalid JSON: ')+error.message,true);return;}
    studioCall('request',{action,request});
  }


  // v0.6 — single real WordBench GF probe; SA still owns the operation inventory.
  let v06Intents=[];
  let v06Result=null;
  function renderV06Languages(){
    const select=el('v06-language');
    if(!select || !state || select.options.length===state.languages.length)return;
    const current=select.value||'Fre';
    select.innerHTML=state.languages.map(l=>`<option value="${safe(l.code)}">${safe(l[locale])} · ${safe(l.code)}</option>`).join('');
    select.value=state.languages.some(l=>l.code===current)?current:'Fre';
  }
  function renderV06Catalog(){
    const sel=el('v06-intent');if(!sel||!v06Intents.length)return;
    const current=sel.value || 'factual-present';
    sel.innerHTML=v06Intents.map(row=>`<option value="${safe(row.id)}">${safe(row['label_'+locale])} · ${safe(row.id)}</option>`).join('');
    sel.value=v06Intents.some(r=>r.id===current)?current:v06Intents[0].id;
    updateV06Mapping();
  }
  function updateV06Mapping(){
    const row=v06Intents.find(r=>r.id===el('v06-intent').value);
    el('v06-gloss').textContent=row?`${t('Sens attendu','Expected meaning')}: ${row.meaning_en}`:'';
    if(!row){el('v06-bridge-state').textContent=t('Catalogue sémantique indisponible','Semantic catalog unavailable');return;}
    const mapped=!!row.sa_operation_family;
    const label=mapped?t('Famille d’opération SA identifiée','SA operation family identified'):
      t('Extension du contrat SA↔GF nécessaire','SA↔GF contract extension required');
    el('v06-bridge-state').textContent=`${label} : ${row.sa_operation_family||'—'} · ${t('pont non qualifié','bridge not qualified')}`;
    el('v06-bridge-state').classList.toggle('v06-gap',!mapped);
  }
  async function loadV06Catalog(){
    try{
      const data=await api('semantik/practical-intents');
      if(!data.ok || !Array.isArray(data.result?.intents)) throw Error(data.result?.message_safe||data.error||'SA catalog unavailable');
      v06Intents=data.result.intents;
      renderV06Catalog();
    // Typed input options are translated by data-fr/data-en; IDs remain stable.
    }catch(error){el('v06-bridge-state').textContent=error.message;}
  }
  function renderV06Result(payload,origin){
    v06Result={...payload, origin, captured_at:new Date().toISOString()};
    const status=payload.status || 'UNKNOWN';
    const ok=(status==='candidate_for_review' && !!(payload.candidate||payload.raw));
    const raw=String(payload.raw??payload.candidate??'');
    const readable=String(payload.readable??raw.replace(/\s*&\+\s*/g,''));
    el('v06-phrase').hidden=!ok;
    el('v06-phrase').textContent=ok?(el('v06-show-raw').checked?raw:readable):'';
    el('v06-save').disabled=false;
    const source=origin==='archive'?t('Dernière archive WordBench','Latest WordBench archive'):
      t('Nouvelle exécution par WordBench','New WordBench execution');
    const details=ok?`${source} · ${status} · ${t('candidat technique','technical candidate')}`:
      `${source} · ${status} · ${payload.error||payload.reason||t('aucune phrase produite','no sentence generated')}`;
    el('v06-result-meta').textContent=details;
    el('v06-result-meta').classList.toggle('v06-error',!ok);
    el('v06-detail').hidden=false;
    el('v06-detail').textContent=JSON.stringify(v06Result,null,2);
  }
  function resetV06Result(){
    v06Result=null;
    el('v06-phrase').hidden=true;
    el('v06-detail').hidden=true;
    el('v06-save').disabled=true;
    el('v06-result-meta').textContent=t('Choisis une preuve existante ou lance une nouvelle sonde GF.','View previous evidence or run a new GF probe.');
    updateV06Mapping();
  }
  el('v06-language').addEventListener('change',resetV06Result);
  el('v06-intent').addEventListener('change',resetV06Result);
  el('v06-show-raw').addEventListener('change',()=>{if(v06Result)renderV06Result(v06Result,v06Result.origin);});
  el('v06-last').addEventListener('click',async()=>{
    if(studioBusy)return;
    setStudioBusy(true);
    try {
      const lang=el('v06-language').value,cap=el('v06-intent').value;
      const report=await api('language?code='+encodeURIComponent(lang));
      const item=(report.scenarios||[]).find(x=>x.id===cap);
      if(!item)throw Error(t('Cas absent de la dernière campagne','Case missing from latest campaign'));
      renderV06Result({language:lang,capability:cap,status:item.status,
        candidate:item.raw||'',raw:item.raw||'',readable:item.candidate||'',
        source_sha256:item.source_sha256,archive_run:true, gf_executed_now:false,
        sa_semantic_request_executed:false,released:false,linguistically_certified:false},'archive');
    }catch(error){tell(error.message,true);}
    finally{setStudioBusy(false);}
  });
  el('v06-run').addEventListener('click',async()=>{
    if(studioBusy)return;
    const lang=el('v06-language').value,cap=el('v06-intent').value;
    setStudioBusy(true);
    el('v06-result-meta').textContent=t('WordBench exécute la sonde avec GF 3.12…','WordBench is running this probe with GF 3.12…');
    try{
      const out=await api('semantik/practical-preview',{method:'POST',body:JSON.stringify({language:lang,capability:cap})});
      renderV06Result(out,'live');
      tell(out.ok?t('Nouvelle phrase GF produite — candidature technique.','New GF sentence generated — technical candidate.'):
        t('Exécution bloquée; consulter le diagnostic.','Execution blocked; inspect the diagnostic.'),!out.ok);
    }catch(error){el('v06-result-meta').textContent=error.message;tell(error.message,true);}
    finally{setStudioBusy(false);}
  });
  el('v06-save').addEventListener('click',()=>{
    if(!v06Result)return;
    const blob=new Blob([JSON.stringify(v06Result,null,2)],{type:'application/json;charset=utf-8'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=url;
    a.download=`defluens-gf-${v06Result.language||'unknown'}-${v06Result.capability||'unknown'}.json`;
    a.click();URL.revokeObjectURL(url);
  });
  loadV06Catalog();

  // v0.7 — canonical typed input via public SemantiK CLI, never a JS grammar.
  let v07Ready = false;
  async function refreshV07Status(){
    try {
      const status=await api('semantik/attribute-status');
      v07Ready=!!status.ready;
      el('v07-status').textContent=status.ready?
        t('PGF RGL français présent, empreintes vérifiées. Candidat non publié.','French RGL PGF present; hashes verified. Unreleased candidate.'):
        t('Candidat non compilé ou non vérifié : ','Candidate not compiled or unverified: ')+(status.status||'NOT_BUILT');
      el('v07-status').classList.toggle('v05-ready',v07Ready);
    } catch(error){v07Ready=false;el('v07-status').textContent=error.message;}
  }
  async function composeV07(){
    const payload={subject:el('v07-subject').value,attribute:el('v07-attribute').value,
      polarity:el('v07-polarity').value,tense:el('v07-tense').value};
    try {
      const answer=await api('semantik/attribute-request',{method:'POST',body:JSON.stringify(payload)});
      if(!answer.ok || !answer.result || answer.result.capability_profile!=='defluens-attribute-fr-1'){
        throw Error(answer.result?.message_safe || answer.error || 'SemantiK request mapper refused this selection');
      }
      el('v07-json').value=JSON.stringify(answer.result,null,2);
      el('v07-result').textContent='';el('v07-sentence').hidden=true;
      tell(t('Demande canonique préparée par SemantiK.','Canonical request prepared by SemantiK.'));
      return true;
    }catch(error){el('v07-result').textContent=error.message;tell(error.message,true);return false;}
  }
  el('v07-compose').addEventListener('click',composeV07);
  el('v07-build').addEventListener('click',async()=>{
    if(studioBusy)return;
    if(!confirm(t('Compiler un PGF candidat RGL via WordBench ? L’ancien candidat sera sauvegardé.',
      'Compile a real RGL candidate PGF through WordBench? The existing candidate will be backed up.')))return;
    setStudioBusy(true);el('v07-status').textContent=t('Compilation RGL en cours…','Compiling RGL…');
    try {
      const answer=await api('semantik/attribute-build',{method:'POST',body:'{}'});
      el('v07-result').textContent=JSON.stringify(answer.report||answer,null,2);
      tell(answer.ok?t('PGF RGL candidat compilé.','RGL candidate PGF built.'):
        t('Compilation bloquée : consulter la sortie WordBench.','Build blocked: inspect WordBench output.'),!answer.ok);
    }catch(error){el('v07-result').textContent=error.message;tell(error.message,true);}
    finally{setStudioBusy(false);await refreshV07Status();}
  });
  el('v07-preview').addEventListener('click',async()=>{
    if(studioBusy)return;
    let request;
    try {request=JSON.parse(el('v07-json').value);
      if(!request || Array.isArray(request) || typeof request!=='object')throw Error('Expected JSON object');
    }catch(error){tell(t('Compose d’abord la demande JSON.','Compose the JSON request first.')+' '+error.message,true);return;}
    setStudioBusy(true);el('v07-sentence').hidden=true;
    el('v07-result').textContent=t('SemantiK et GF réalisent la demande…','SemantiK and GF are realizing the request…');
    try {
      const answer=await api('semantik/attribute-preview',{method:'POST',body:JSON.stringify({request})});
      const body=answer.result||answer;
      el('v07-result').textContent=JSON.stringify(body,null,2);
      const text=body.communication_result?.plain_text;
      if(answer.ok && body.status==='CANDIDATE_PREVIEW' && text){
        el('v07-sentence').textContent=text;el('v07-sentence').hidden=false;
        tell(t('Réalisation GF candidate obtenue.','GF candidate realization obtained.'));
        studioHistory.unshift({type:'candidate',timestamp:new Date().toISOString(),response:body});
        studioHistory.splice(12);renderStudioHistory();
      } else tell(body.message_safe||body.error||t('Aucune sortie GF.','No GF output.'),true);
    }catch(error){el('v07-result').textContent=error.message;tell(error.message,true);}
    finally{setStudioBusy(false);}
  });

  // v0.5 — public SemantiK operations and WordBench-produced GF candidates.
  const saIsoCodes={Eng:'en',Fre:'fr',Spa:'es',Ger:'de',Dut:'nl',Swe:'sv',Dan:'da',Nor:'nb',Nno:'nn',Fin:'fi',Est:'et',Afr:'af',Ita:'it',Por:'pt'};
  const studioHistory=[];
  let studioLatest=null;
  let pilotCases=[];
  let studioBusy=false;
  function renderStudioLanguages(){
    if(!state)return;
    const container=el('studio-language-picks');
    if(container.children.length)return;
    container.innerHTML=state.languages.map(l=>{
      const iso=saIsoCodes[l.code], checked=['fr','en','de'].includes(iso);
      return `<label class="v05-language-chip"><input type="checkbox" name="studio-language" value="${safe(iso)}" ${checked?'checked':''}><span>${safe(l[locale])}</span><small>${safe(iso)}</small></label>`;
    }).join('');
  }
  function setStudioBusy(busy){
    studioBusy=busy;
    ['candidate-build','candidate-preview','pilot-load','studio-render-many','v06-last','v06-run','v07-compose','v07-build','v07-preview'].forEach(id=>el(id).disabled=busy);
  }
  function showCandidateResult(response){
    const out=el('candidate-result'), sentence=el('candidate-sentence');
    const body=response.result||response;
    const result=body.communication_result;
    const ok=response.ok!==false && body.status==='CANDIDATE_PREVIEW' && result?.plain_text;
    sentence.hidden=!ok;
    sentence.textContent=ok?result.plain_text:'';
    out.textContent=JSON.stringify(body,null,2);
    if(ok){
      tell(t('Phrase réalisée par SemantiK et GF — candidat uniquement.','Sentence realized by SemantiK and GF — candidate only.'));
      studioHistory.unshift({type:'candidate',timestamp:new Date().toISOString(),response:body});
      studioHistory.splice(12);
      renderStudioHistory();
    } else tell(t('Le moteur GF n’a pas encore produit de phrase.','The GF engine has not yet produced a sentence.'),true);
  }
  async function refreshCandidateStatus(){
    try {
      const status=await api('semantik/candidate');
      el('candidate-status').textContent=status.ready?
        t('PGF candidat présent, empreintes vérifiées. Non publié.','Candidate PGF present; hashes verified. Not released.'):
        t('PGF non disponible ou non vérifié : ','PGF missing or unverified: ')+(status.status||'NOT_BUILT');
      el('candidate-status').classList.toggle('v05-ready',status.ready);
      el('candidate-preview').disabled=!status.ready || studioBusy;
    } catch(error){el('candidate-status').textContent=error.message;el('candidate-preview').disabled=true;}
  }
  async function loadPilotCases(){
    try {
      const payload=await api('semantik/pilot');
      pilotCases=payload.cases;
      el('pilot-case').innerHTML=pilotCases.map(c=>`<option value="${safe(c.id)}">${safe(c.id)}</option>`).join('');
    }catch(error){el('pilot-case').innerHTML=`<option>${safe(error.message)}</option>`;}
  }
  el('pilot-load').addEventListener('click',()=>{
    const choice=pilotCases.find(c=>c.id===el('pilot-case').value);
    if(!choice){tell(t('Profil non chargé.','Profile not loaded.'),true);return;}
    el('semantic-request').value=JSON.stringify(choice.request,null,2);
    tell(t('Demande canonique chargée; le texte attendu n’est pas une sortie GF.','Canonical request loaded; expected fixture text is not a GF output.'));
  });
  el('candidate-build').addEventListener('click',async()=>{
    if(studioBusy)return;
    if(!confirm(t('Compiler un vrai candidat GF avec WordBench ? Un ancien candidat sera sauvegardé.','Compile a real GF candidate through WordBench? An older candidate will be backed up.')))return;
    setStudioBusy(true);
    el('candidate-status').textContent=t('Compilateur GF en cours…','GF compiler running…');
    try {
      const res=await api('semantik/build',{method:'POST',body:'{}'});
      el('candidate-result').textContent=JSON.stringify(res.report||res,null,2);
      tell(res.ok?t('PGF compilé en mode candidat.','PGF compiled as candidate.'):t('Échec ou blocage de compilation GF.','GF build failed or blocked.'),!res.ok);
    }catch(error){tell(error.message,true);el('candidate-result').textContent=error.message;}
    finally{setStudioBusy(false);refreshCandidateStatus();}
  });
  el('candidate-preview').addEventListener('click',async()=>{
    if(studioBusy)return;
    let request;
    try{request=JSON.parse(el('semantic-request').value);}catch(error){tell(error.message,true);return;}
    setStudioBusy(true);
    el('candidate-result').textContent=t('Réalisation GF réelle en cours…','Real GF realization running…');
    el('candidate-sentence').hidden=true;
    try{showCandidateResult(await api('semantik/preview',{method:'POST',body:JSON.stringify({request})}));}
    catch(error){tell(error.message,true);el('candidate-result').textContent=error.message;}
    finally{setStudioBusy(false);refreshCandidateStatus();}
  });
  function renderStudioResults(payload){
    const rows=payload.results||[];
    el('studio-compare-summary').textContent=rows.length?
      `${payload.success_count} / ${rows.length} ${t('réalisations disponibles — profils publiés uniquement','successful realizations — released profiles only')}`:
      t('Aucune réalisation.','No realization.');
    el('studio-compare-results').innerHTML=rows.map(r=>{
      const message=r.ok?r.text:(r.detail?.message_safe||r.detail?.message||'SA runtime unavailable');
      return `<article class="v05-result ${r.ok?'v05-success':'v05-failed'}"><div class="v05-result-top"><strong>${safe(r.language)}</strong><span>${safe(r.ok?'SA · RELEASED':t('Indisponible','Unavailable'))}</span></div><p>${safe(message)}</p></article>`;
    }).join('');
  }
  function renderStudioHistory(){
    el('studio-history').innerHTML=studioHistory.map((r,i)=>{
      const info=r.type==='candidate'?r.response.communication_result?.plain_text:
        (r.response.results||[]).filter(x=>x.ok).map(x=>`${x.language}: ${x.text}`).join(' · ');
      return `<div class="v05-history-item"><span>${safe(new Date(r.timestamp).toLocaleTimeString())} · ${safe(r.type)}</span><p>${safe(info||t('Aucune sortie publiée','No published output'))}</p></div>`;
    }).join('')||`<p class="studio-note">${safe(t('Aucune génération dans cette session.','No generations in this session.'))}</p>`;
  }
  el('studio-render-many').addEventListener('click',async()=>{
    if(studioBusy)return;
    let request;
    try{request=JSON.parse(el('semantic-request').value);if(!request||Array.isArray(request)||typeof request!=='object')throw Error('JSON object required');}
    catch(error){tell(error.message,true);return;}
    const languages=[...document.querySelectorAll('[name="studio-language"]:checked')].map(x=>x.value);
    if(!languages.length){tell(t('Choisis au moins une langue.','Choose at least one language.'),true);return;}
    setStudioBusy(true);
    el('studio-compare-summary').textContent=t('Réalisation par Semantic Architect…','Semantic Architect is realizing…');
    try {
      const out=await api('semantik/render-many',{method:'POST',body:JSON.stringify({request,languages})});
      studioLatest={timestamp:new Date().toISOString(),request,languages,response:out};
      ['studio-export-json','studio-export-md','studio-export-text'].forEach(id=>el(id).disabled=false);
      renderStudioResults(out);
      studioHistory.unshift({type:'production',timestamp:studioLatest.timestamp,response:out});
      studioHistory.splice(12);renderStudioHistory();
    } catch(error){el('studio-compare-summary').textContent=error.message;tell(error.message,true);}
    finally{setStudioBusy(false);}
  });
  function exportStudio(format){
    if(!studioLatest)return;
    const {timestamp,languages,response}=studioLatest;
    let textValue, mime, ext;
    if(format==='json'){
      textValue=JSON.stringify(studioLatest,null,2);mime='application/json';ext='json';
    }else{
      const rows=(response.results||[]).map(r=>`${r.language}: ${r.ok?r.text:'[SA ERROR] '+(r.detail?.message_safe||r.detail?.message||'unavailable')}`);
      textValue=format==='md'?
        `# Ars Magna Defluens — ${timestamp}\n\n`+rows.map(x=>`- ${x}`).join('\n')+'\n':
        `Ars Magna Defluens — ${timestamp}\n`+rows.join('\n')+'\n';
      mime='text/plain';ext=format==='md'?'md':'txt';
    }
    const blob=new Blob([textValue],{type:mime+';charset=utf-8'});
    const url=URL.createObjectURL(blob);const a=document.createElement('a');
    a.href=url;a.download='defluens-session-'+timestamp.replace(/[:.]/g,'-')+'.'+ext;
    document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  el('studio-export-json').addEventListener('click',()=>exportStudio('json'));
  el('studio-export-md').addEventListener('click',()=>exportStudio('md'));
  el('studio-export-text').addEventListener('click',()=>exportStudio('text'));
  loadPilotCases();refreshCandidateStatus();refreshV07Status();renderStudioHistory();

  el('semantic-sample').addEventListener('click',()=>studioCall('example'));
  el('semantic-validate').addEventListener('click',()=>semanticInput('validate-request'));
  el('semantic-render').addEventListener('click',()=>semanticInput('render'));
  el('semantic-capabilities').addEventListener('click',()=>studioCall('capabilities'));
  el('semantic-readiness').addEventListener('click',()=>studioCall('readiness',{
    language:el('semantic-lang').value.trim(),profile:el('semantic-profile').value.trim()
  }));
  document.addEventListener('click',(event)=>{
    const target=event.target.closest('button,a');
    if(!target)return;
    if(target.dataset.page) route(target.dataset.page);
    else if(target.dataset.route) route(target.dataset.route);
    else if(target.dataset.language)loadLanguage(target.dataset.language);
    else if(target.dataset.mode){
      const m=target.dataset.mode;
      if(m==='full' && !confirm(t('Lancer les 210 scénarios GF sur les 14 langues ? Cette opération peut durer plusieurs minutes.','Run all 210 GF scenarios in 14 languages? This may take several minutes.')))return;
      command('run',{mode:m});
    }
    else if(target.dataset.action && target.dataset.target)command(target.dataset.action,{target:target.dataset.target});
  });
  el('show-raw').addEventListener('change',renderScenarios);
  el('stop-run').addEventListener('click',()=>{
    if(confirm(t('Arrêter le processus WordBench en cours ?','Stop the active WordBench process?')))command('stop',{});
  });
  el('quit-app').addEventListener('click',()=>{
    if(state?.job.state==='running') {tell(t('Arrête la campagne avant de fermer la console.','Stop the campaign before closing the console.'),true);return;}
    if(confirm(t('Fermer le serveur local Defluens ?','Shut down the local Defluens server?')))command('quit',{});
  });
  el('settings-form').addEventListener('submit',async event=>{
    event.preventDefault();
    const formData=new FormData(event.currentTarget);
    const paths=Object.fromEntries(formData.entries());
    await command('settings',{paths});
  });
  el('language-toggle').addEventListener('click',()=>{
    locale=locale==='fr'?'en':'fr';
    try {localStorage.setItem('defluens-lang',locale);} catch (_) {}
    applyLocale();
  });
  window.addEventListener('hashchange',()=>route(location.hash.slice(1)||'overview'));
  applyLocale();
  route(location.hash.slice(1)||'overview');
  refresh();
  setInterval(refresh,2500);
})();
