/* Defluens lexical-lab UI: orchestration only. diK and WordBench own data. */
(() => {
  'use strict';
  const el = (id) => document.getElementById(id);
  const token = new URLSearchParams(location.search).get('token') || '';
  const bilingual = (fr, en) => document.documentElement.lang === 'en' ? en : fr;
  const output = el('v09-lexical-result');
  const note = el('v09-lexical-status');
  const buttons = ['v09-from-dik','v09-wordbench','v09-inspect','v09-refresh'];
  async function request(path, data) {
    const options = {headers:{'X-Defluens-Token':token},cache:'no-store'};
    if (data !== undefined) {
      options.method='POST';options.body=JSON.stringify(data);
      options.headers['Content-Type']='application/json';
    }
    const reply = await fetch('/api/lexical/'+path, options);
    const parsed=await reply.json();
    if (!reply.ok) throw Error(parsed.error || 'Local integration error');
    return parsed;
  }
  async function work(fn) {
    buttons.forEach(id => {el(id).disabled=true;});
    note.textContent=bilingual('Opération locale en cours…','Local operation in progress…');
    try {
      const data=await fn();
      output.textContent=JSON.stringify(data,null,2);
      note.textContent=data.ok ? bilingual('Candidat enregistré. Aucune publication ni certification.','Candidate recorded. No release or certification.') : bilingual('Commande externe bloquée ou refusée — voir le rapport.','External command blocked or rejected — see report.');
    } catch (err) {
      output.textContent=String(err.message || err);
      note.textContent=bilingual('Échec sans repli — consulte le diagnostic.','No-fallback failure — inspect diagnostic.');
    } finally {buttons.forEach(id => {el(id).disabled=false;});}
  }
  el('v09-from-dik').addEventListener('click', () => work(async () => {
    const d=await request('handoff',{observations:el('v09-observations').value.trim(),locale:el('v09-locale').value});
    if (d.ok) {
      el('v09-knowledge').value=d.knowledge_bundle;
      el('v09-decisions').value=d.decisions_template;
      el('v09-inspect-bundle').value=d.knowledge_bundle;
    }
    return d;
  }));
  el('v09-wordbench').addEventListener('click', () => work(async () => {
    const d=await request('bindings',{knowledge_bundle:el('v09-knowledge').value.trim(),review_file:el('v09-decisions').value.trim()});
    if (d.ok) el('v09-inspect-bundle').value=d.candidate_bundle;
    return d;
  }));
  el('v09-inspect').addEventListener('click', () => work(async () => request('inspect',{bundle:el('v09-inspect-bundle').value.trim()})));
  el('v09-refresh').addEventListener('click', () => work(async () => request('status')));
})();
