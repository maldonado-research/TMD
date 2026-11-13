"use strict";
/* Copyright (c) 2026 Ricardo Maldonado. MIT. */
function runTransportChecks(api,input,saved) {
  let assertions=0;const checks={zero_endpoint_matches:0,scenario_evaluations:0,adjacent_cap_comparisons:0,
    adjacent_interval_comparisons:0,input_refusals:0,hand_examples:0};
  const eq=(x,y)=>{assertions++;if(JSON.stringify(x)!==JSON.stringify(y))throw Error("equality failed");};
  const ok=x=>{assertions++;if(!x)throw Error("assertion failed");};
  const R=s=>{const a=s.split("/");return new api.Rational(BigInt(a[0]),BigInt(a[1]||"1"));};
  const zero=api.analyzeTransport(input,{false_gate:"0",correct_call:"0"});
  if(saved){
    for(let i=0;i<zero.contexts.length;i++){
      for(const a of ["baseline","selected"]){
        const x=zero.contexts[i][a],y=saved.contexts[i][a];
        for(const k of ["lower","upper"]){eq(x.Q[k],y[k].exact);checks.zero_endpoint_matches++;}
        for(const k of ["W","A","M"]){eq(x.caps[k],y.caps[k]);checks.zero_endpoint_matches++;}
        eq(x.eligible_fraction_lower,y.eligibility.eligible_fraction_lower_exact);checks.zero_endpoint_matches++;
      }
      for(const k of ["lower","upper"]){eq(zero.contexts[i].J[k],saved.contexts[i].J[k].exact);checks.zero_endpoint_matches++;}
    }
    for(const k of ["lower","upper"]){eq(zero.common_J[k],saved.common_J[k].exact);checks.zero_endpoint_matches++;}
  }
  const allRows=[];
  for(const path of ["both","false_gate","correct_call"]){
    let previous;
    for(let j=0;j<=256;j++){
      const t=new api.Rational(BigInt(j),256n).str();
      const d={false_gate:path==="correct_call"?"0":t,correct_call:path==="false_gate"?"0":t};
      const x=api.analyzeTransport(input,d);checks.scenario_evaluations++;
      ok(x.common_J.status!=="unevaluable_observation_contract");
      if(previous){
        ok(!x.reject_common_J || previous.reject_common_J);checks.adjacent_interval_comparisons++;
        ok(R(x.common_J.lower).cmp(R(previous.common_J.lower))<=0);checks.adjacent_interval_comparisons++;
        ok(x.common_J.upper===null || (previous.common_J.upper!==null && R(x.common_J.upper).cmp(R(previous.common_J.upper))>=0));checks.adjacent_interval_comparisons++;
        for(let i=0;i<x.contexts.length;i++)for(const a of ["baseline","selected"])for(const k of ["W","A","M"]){
          ok(R(x.contexts[i][a].caps[k]).cmp(R(previous.contexts[i][a].caps[k]))>=0);checks.adjacent_cap_comparisons++;
        }
      }
      previous=x;
    }
    allRows.push(api.bracketFrontier(input,path));
  }
  const probs={F:"1/5",g:"4/5",U:{W:"3/20",A:"3/10",M:"3/20"},L:{W:"4/5",A:"4/5",M:"4/5"}};
  const tiny={schema_version:1,alpha:"1/20",contexts:[{id:"tiny",baseline:probs,selected:probs}]};
  eq(api.analyzeTransport(tiny,{false_gate:"0",correct_call:"0"}).contexts[0].selected.Q.lower,"4");checks.hand_examples++;
  eq(api.analyzeTransport(tiny,{false_gate:"0",correct_call:"1/5"}).contexts[0].selected.Q.lower,"1");checks.hand_examples++;
  ok(R(api.analyzeTransport(tiny,{false_gate:"0",correct_call:"19/100"}).contexts[0].selected.Q.lower).cmp(R("1"))>0);checks.hand_examples++;
  const vac=api.analyzeTransport(input,{false_gate:"1",correct_call:"1"});
  eq(vac.reject_common_J,false);eq(vac.common_J.lower,"0");eq(vac.common_J.upper,null);checks.hand_examples+=3;
  const first=JSON.parse(JSON.stringify(input));first.contexts=first.contexts.slice(0,1);
  eq(api.analyzeTransport(first,{false_gate:"0",correct_call:"0"}).reject_common_J,false);checks.hand_examples++;
  const bads=[0,0.05,-1,null,true,"-1/10","1/0","2","0.05","1e-2","1/02","1/","",{},Array(201).join("9")];
  for(const value of bads){let refused=false;try{api.analyzeTransport(input,{false_gate:value,correct_call:"0"});}catch(e){refused=true;}ok(refused);checks.input_refusals++;}
  let refused=false;try{api.analyzeTransport(input,{false_gate:"0",correct_call:"0",extra:"1"});}catch(e){refused=true;}ok(refused);checks.input_refusals++;
  const f=api.analyzeTransport(input,{false_gate:"0",correct_call:"0"});
  return {status:"pass",runtime_scope:"Pure JavaScript core executed in V8; Python, CP inversion, filesystem CLI and native experiments not executed.",
    assertions,checks,frontiers:allRows,starting_reject_common_J:f.reject_common_J,native_validation:false,
    confidence_endpoint_recomputation:false,source_authentication_performed:false};
}
if(typeof module!=="undefined"&&module.exports)module.exports={runTransportChecks};
