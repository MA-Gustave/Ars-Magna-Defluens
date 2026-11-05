/* Ars Magna Defluens v0.8 — semantic recipe UI only.
 * Actual communication planning and grammatical realization belong to SemantiK Architect / GF.
 * No client-side phrase templates or implicit production fallback.
 */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const tr = (fr, en) => document.documentElement.lang === 'en' ? en : fr;
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const token = new URLSearchParams(location.search).get('token') || '';
  let catalog = null, items = [], canonical = null, busy = false, last = null;
  const names = {
    attribute: ['Attribut', 'Attribute'], classification: ['Classification', 'Classification'],
    event: ['Événement', 'Event'], transitive: ['Action transitive', 'Transitive action'],
    location: ['Lieu', 'Location'], directive: ['Instruction', 'Directive']
  };
  const options = {
    attribute:['attribut','attribute'],classification:['classification','classification'],event:['événement','event'],transitive:['transitif','transitive'],location:['lieu','location'],directive:['instruction','directive'],
    mira:['Mira','Mira'], lea:['Léa','Lea'], noa:['Noa','Noa'],
    ready:['prêt·e','ready'], calm:['calme','calm'], absent:['absent·e','absent'], available:['disponible','available'],
    guide:['guide','guide'],artist:['artiste','artist'],scientist:['scientifique','scientist'],
    work:['travailler','work'],walk:['marcher','walk'],speak:['parler','speak'],
    carry:['porter','carry'],watch:['regarder','watch'],visit:['visiter','visit'],
    here:['ici','here'],there:['là','there'],in_paris:['à Paris','in Paris'],
    wait:['patienter','wait'], book:['livre','book'],document:['document','document'],flower:['fleur','flower'],
    positive:['positive','positive'],negative:['négative','negative'],present:['présent','present'],past:['passé','past'],future:['futur','future']
  };
  const getLabel = value => (options[value] || [value, value])[document.documentElement.lang === 'en' ? 1 : 0];
  async function api(path, data) {
    const res = await fetch('/api/' + path, {
      method: data === undefined ? 'GET' : 'POST',
      headers: {'X-Defluens-Token':token, ...(data === undefined ? {} : {'Content-Type':'application/json'})},
      ...(data === undefined ? {} : {body:JSON.stringify(data)}),cache:'no-store'
    });
    const result = await res.json();
    if (!res.ok) throw Error(result.error || `HTTP ${res.status}`);
    return result;
  }
  function status(text, error=false) {
    const x=$('v08-status');x.textContent=text;
    x.classList.toggle('v05-ready',!error && /(?:ready|réussi|prêt|produit|généré|generated|composed)/i.test(text));
    x.style.borderLeftColor=error?'#D95B38':undefined;
  }
  function start() {
    if (busy) return false;
    busy=true;
    document.querySelectorAll('#v08-core-lab button').forEach(b => b.disabled=true);
    return true;
  }
  function finish() {
    busy=false;
    document.querySelectorAll('#v08-core-lab button').forEach(b => b.disabled=false);
    $('v08-add').disabled=items.length>=8;
    $('v08-export').disabled=!canonical;
  }
  function field(index, fieldName, label, values, current) {
    return `<div class="v08-field"><label for="v08-${fieldName}-${index}">${esc(label)}</label>`+
      `<select id="v08-${fieldName}-${index}" data-index="${index}" data-field="${esc(fieldName)}">`+
      values.map(x=>`<option value="${esc(x)}" ${x===current?'selected':''}>${esc(getLabel(x))}</option>`).join('')+
      `</select></div>`;
  }
  function fresh(intent) {
    const def = catalog.intents[intent];
    const row = {intent,concept:def.options[0],polarity:'positive'};
    if (def.requires_subject!==false)row.subject='mira';
    if (def.requires_object)row.object='book';
    if (def.supports_tense!==false)row.tense='present';
    return row;
  }
  function sanitizeItem(item) {
    const spec=catalog.intents[item.intent];if(!spec)return fresh('attribute');
    const next={intent:item.intent,concept:spec.options.includes(item.concept)?item.concept:spec.options[0],
                polarity:catalog.polarities.includes(item.polarity)?item.polarity:'positive'};
    if (spec.requires_subject!==false)next.subject=catalog.subjects.includes(item.subject)?item.subject:'mira';
    if (spec.requires_object)next.object=catalog.objects.includes(item.object)?item.object:catalog.objects[0];
    if (spec.supports_tense!==false)next.tense=catalog.tenses.includes(item.tense)?item.tense:'present';
    return next;
  }
  function renderItems() {
    if(!catalog) return;
    $('v08-item-count').textContent=`${items.length} / 8`;
    $('v08-add').disabled=items.length>=8||busy;
    $('v08-items').innerHTML=items.map((row,i) => {
      const spec=catalog.intents[row.intent];
      let controls=field(i,'intent',tr('Opération SA','SA operation'),Object.keys(catalog.intents),row.intent);
      if(spec.requires_subject!==false)controls+=field(i,'subject',tr('Sujet','Subject'),catalog.subjects,row.subject);
      controls+=field(i,'concept',tr(spec.label_fr,spec.label_en),spec.options,row.concept);
      if(spec.requires_object)controls+=field(i,'object',tr('Objet','Object'),catalog.objects,row.object);
      controls+=field(i,'polarity',tr('Polarité','Polarity'),catalog.polarities,row.polarity);
      if(spec.supports_tense!==false)controls+=field(i,'tense',tr('Temps','Tense'),catalog.tenses,row.tense);
      return `<div class="v08-item"><div class="v08-item-head"><span class="v08-item-title">${esc(tr('ÉNONCÉ','STATEMENT'))} ${i+1} · ${esc(spec.operation)}</span>`+
             `<button type="button" class="v08-remove" data-remove="${i}" ${items.length<2?'disabled':''}>${esc(tr('Retirer','Remove'))}</button></div>`+
             `<div class="v08-grid">${controls}</div></div>`;
    }).join('');
  }
  function recipeFromItems() {return {language:$('v08-language').value,items:items.map(x=>({...x}))};}
  function syncRecipe() {$('v08-recipe').value=JSON.stringify(recipeFromItems(),null,2);canonical=null;$('v08-canonical').textContent='';$('v08-export').disabled=true;}
  function currentRecipe() {
    const raw=JSON.parse($('v08-recipe').value);
    if(!raw||Array.isArray(raw)||typeof raw!=='object')throw Error(tr('Objet JSON attendu','Expected a JSON object'));
    return raw;
  }
  async function loadCatalog() {
    try {
      const result=await api('semantik/core-catalog');
      if(result.ok!==true||!result.result?.intents)throw Error(JSON.stringify(result.result||result));
      catalog=result.result;
      items=[fresh('attribute')];
      renderItems();syncRecipe();
      $('v08-catalog-note').textContent=tr('Catalogue officiel SemantiK chargé · non publié', 'Canonical SemantiK catalog loaded · not released');
      await refreshStatus();
    } catch(e) {
      status(tr('Catalogue SemantiK indisponible : ','SemantiK catalog unavailable: ')+e.message,true);
      $('v08-catalog-note').textContent=tr('Catalogue indisponible','Catalog unavailable');
      document.querySelectorAll('#v08-core-lab button').forEach(b => b.disabled=true);
    }
  }
  async function refreshStatus() {
    try {
      const d=await api('semantik/core-status');
      $('v08-runtime-cards').innerHTML=['fr','en'].map(lang=>{
        const item=d.languages?.[lang]||{};
        return `<div class="v08-runtime ${item.ready?'ready':''}"><strong>${lang.toUpperCase()} · ${esc(lang==='fr'?'DefluensCoreFre':'DefluensCoreEng')}</strong>`+
          `${esc(item.ready?tr('PGF compilé et empreintes vérifiées','PGF built and hashes verified'):tr('PGF candidat non disponible','Candidate PGF unavailable'))}<div>${esc(item.status||'NOT_BUILT')} · ${esc(tr('non publié','unreleased'))}</div></div>`;
      }).join('');
    } catch(e) {$('v08-runtime-cards').textContent=e.message;}
  }
  function showResult(label, payload) {
    last=payload;
    const rows=payload.results||[{
      language:payload.language||$('v08-language').value,
      ok:payload.ok===true,
      text:payload.ok?payload.result?.result?.communication_result?.plain_text:null,
      detail:payload
    }];
    $('v08-result-cards').innerHTML=rows.map(row=>{
      const message=row.ok?row.text:(row.detail?.result?.error||row.detail?.result?.result?.message_safe||row.detail?.result?.result?.error||row.detail?.error||tr('PGF non disponible ou réalisation refusée','PGF unavailable or realization refused'));
      return `<article class="v05-result ${row.ok?'v05-success':'v05-failed'}"><div class="v05-result-top"><strong>${esc(row.language||'—')}</strong><span>${esc(row.ok?tr('GF CANDIDAT','GF CANDIDATE'):tr('BLOQUÉ','BLOCKED'))}</span></div><p>${esc(message||tr('Aucune phrase','No sentence'))}</p></article>`;
    }).join('');
    $('v08-details').textContent=JSON.stringify({label,payload},null,2);
    status(`${label}: ${rows.filter(r=>r.ok).length}/${rows.length} ${tr('réalisations candidates','candidate realizations')}`, rows.some(r=>!r.ok));
  }
  async function compose() {
    if(!start())return;
    try {
      const result=await api('semantik/core-request',{recipe:currentRecipe()});
      if(!result.ok)throw Error(result.result?.message_safe||'Semantic request refused');
      canonical=result.result;
      $('v08-canonical').textContent=JSON.stringify(canonical,null,2);
      $('v08-canonical-details').open=true;
      status(tr('CommunicationRequest canonique produit par Semantic Architect.','Canonical CommunicationRequest generated by Semantic Architect.'));
    }catch(e){status(e.message,true);}
    finally{finish();}
  }
  async function build(lang) {
    if(!confirm(tr('Compiler le PGF candidat avec WordBench / GF 3.12 ? Le candidat précédent sera sauvegardé.','Build the candidate PGF using WordBench / GF 3.12? The previous candidate will be backed up.')))return;
    if(!start())return;
    status(tr('Compilation GF en cours pour ', 'GF compilation in progress for ')+lang.toUpperCase());
    try {
      const result=await api('semantik/core-build',{language:lang});
      $('v08-details').textContent=JSON.stringify(result,null,2);
      status(result.ok?tr('PGF candidat construit; non publié.','Candidate PGF built; unreleased.'):
        (result.report?.error||result.error||tr('Compilation bloquée.','Compilation blocked.')),!result.ok);
    }catch(e){status(e.message,true);}finally{finish();await refreshStatus();}
  }
  async function preview(compare) {
    if(!start())return;
    status(tr('Demande transmise au pipeline SemantiK + GF…','Request submitted to SemantiK + GF pipeline…'));
    try {
      const recipe=currentRecipe();
      const answer=await api(compare?'semantik/core-preview-many':'semantik/core-preview',
        compare?{recipe,languages:['fr','en']}:{recipe});
      showResult(compare?'FR + EN':'SA + GF',answer);
    }catch(e){status(e.message,true);}
    finally{finish();await refreshStatus();}
  }
  function exportCanonical() {
    if(!canonical)return;
    const blob=new Blob([JSON.stringify({status:'CANDIDATE_REQUEST_ONLY', released:false, request:canonical},null,2)],{type:'application/json;charset=utf-8'});
    const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='defluens-semantic-request-v08.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  document.addEventListener('DOMContentLoaded',() => {
    $('v08-items').addEventListener('change',e=>{
      const select=e.target.closest('select[data-index]');if(!select||!catalog)return;
      const idx=Number(select.dataset.index),field=select.dataset.field;
      if(field==='intent')items[idx]=fresh(select.value);
      else items[idx]={...items[idx],[field]:select.value};
      items[idx]=sanitizeItem(items[idx]);renderItems();syncRecipe();
    });
    $('v08-items').addEventListener('click',e=>{
      const button=e.target.closest('button[data-remove]');if(!button||items.length<2)return;
      items.splice(Number(button.dataset.remove),1);renderItems();syncRecipe();
    });
    $('v08-add').addEventListener('click',()=>{if(!catalog||items.length>=8)return;items.push(fresh('event'));renderItems();syncRecipe();});
    $('v08-example').addEventListener('click',()=>{
      if(!catalog)return;
      items=[{intent:'attribute',subject:'mira',concept:'ready',polarity:'negative',tense:'present'},
             {intent:'transitive',subject:'lea',concept:'carry',object:'book',polarity:'positive',tense:'past'},
             {intent:'directive',concept:'wait',polarity:'negative'}];
      renderItems();syncRecipe();
    });
    $('v08-language').addEventListener('change',syncRecipe);
    $('v08-compose').addEventListener('click',compose);
    $('v08-export').addEventListener('click',exportCanonical);
    $('v08-build-fr').addEventListener('click',()=>build('fr'));
    $('v08-build-en').addEventListener('click',()=>build('en'));
    $('v08-preview').addEventListener('click',()=>preview(false));
    $('v08-compare').addEventListener('click',()=>preview(true));
    $('v010-audit').addEventListener('click',async()=>{
      const button=$('v010-audit'), note=$('v010-audit-status');
      if(button.disabled)return;
      button.disabled=true;
      note.textContent=tr('Vérification par le CLI public SemantiK…','Verifying through SemantiK public CLI…');
      try {
        const result=await api('semantik/core-acceptance',{mode:'structural'});
        $('v010-audit-result').textContent=JSON.stringify(result,null,2);
        note.textContent=result.structural_passed
          ?tr(`Structure validée : ${result.totals.structurally_validated} demandes + ${result.totals.expected_rejections} rejets. Aucune réalisation GF exécutée.`,
              `Structural pass: ${result.totals.structurally_validated} requests + ${result.totals.expected_rejections} rejections. No GF execution.`)
          :tr('Échec des contrôles structurels : consulter le rapport.','Structural checks failed: inspect the report.');
      }catch(e){note.textContent=tr('Audit bloqué : ','Audit blocked: ')+e.message;}
      finally{button.disabled=false;}
    });

    $('v011-audit').addEventListener('click',async()=>{
      const button=$('v011-audit'), note=$('v011-audit-status');
      if(button.disabled)return;
      button.disabled=true;
      note.textContent=tr('Contrôle canonique et parité SA en cours…', 'Checking canonical SA parity…');
      try {
        const result=await api('semantik/core-qualification',{mode:'structural'});
        $('v011-audit-result').textContent=JSON.stringify(result,null,2);
        note.textContent=result.structural_passed && result.cross_language_parity_passed
          ?tr(`${result.totals.structurally_validated} demandes et ${result.totals.parity_pairs} paires équivalentes. PGF non exécuté.`,
              `${result.totals.structurally_validated} requests and ${result.totals.parity_pairs} equivalent pairs. GF not executed.`)
          :tr('Qualification structurelle en échec : voir le rapport JSON.','Structural qualification failed: see JSON report.');
      }catch(e){note.textContent=tr('Qualification bloquée : ','Qualification blocked: ')+e.message;}
      finally{button.disabled=false;}
    });

    $('language-toggle').addEventListener('click',()=>setTimeout(()=>{if(catalog)renderItems();},0));
    loadCatalog();
  });
})();
