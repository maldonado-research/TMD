#!/usr/bin/env node
// Independent exact-rational diagnostic of the stored synthetic fixture.
// Read-only input; no CP endpoint generation and no Python execution.
// Usage: node transport_sensitivity_exact.mjs example_strict_separation_result.json
// Pin the fixture to maldonado-research/TMD commit f425bf4e1ae99db42d1b5c88bec1992be75ace50.
// Q, J and common-intersection formulas reproduce the existing cap projection.
// Every decision uses BigInt fractions; Number conversion is display-only.
// The monotone rejection checks require this fixture's evaluable starting cap sets.
// No native validation, scientific-power, or novel-theorem claim is made.
import { readFileSync } from "node:fs";

function makeCalc(fixture) {
 function gcd(a,b){a=a<0n?-a:a;b=b<0n?-b:b;while(b){[a,b]=[b,a%b]}return a}
 class R {
  constructor(n,d=1n){n=BigInt(n);d=BigInt(d);if(!d)throw Error("zero denominator");if(d<0n){n=-n;d=-d}let g=gcd(n,d);this.n=n/g;this.d=d/g}
  static of(v){if(v instanceof R)return v;let t=String(v);if(t.includes(".")){let [a,b]=t.split(".");return new R(BigInt(a+b),10n**BigInt(b.length))}let [a,b]=t.split("/");return new R(a,b===undefined?1n:b)}
  add(v){v=R.of(v);return new R(this.n*v.d+v.n*this.d,this.d*v.d)}
  sub(v){v=R.of(v);return new R(this.n*v.d-v.n*this.d,this.d*v.d)}
  mul(v){v=R.of(v);return new R(this.n*v.n,this.d*v.d)}
  div(v){v=R.of(v);return new R(this.n*v.d,this.d*v.n)}
  cmp(v){v=R.of(v);let z=this.n*v.d-v.n*this.d;return z>0n?1:z<0n?-1:0}
  sq(){return this.mul(this)}
  str(){return this.d===1n?String(this.n):this.n+"/"+this.d}
  num(){return Number(this.n)/Number(this.d)}
 }
 const q=R.of,zero=q(0),one=q(1),routes=["W","A","M"];
 const min=(...vs)=>vs.map(q).reduce((a,b)=>a.cmp(b)<=0?a:b);
 const max=(...vs)=>vs.map(q).reduce((a,b)=>a.cmp(b)>=0?a:b);
 const sum=vs=>vs.reduce((a,b)=>a.add(b),zero);
 const point=vs=>Object.fromEntries(routes.map((r,i)=>[r,vs[i].str()]));
 const endpoint=(v,attained=v!==null&&v.cmp(0)>0)=>({exact:v===null?null:v.str(),infinity:v===null?"positive":null,attained_in_positive_domain:attained});
 function capsProjection(caps) {
  const u=routes.map(r=>q(caps[r])),[w,a,m]=u,total=sum(u);
  const result={caps:point(u),sum_caps_exact:total.str()};
  if(total.cmp(1)<0)return {...result,status:"empty_observation_contract_set"};
  if(u.some(v=>v.cmp(0)===0))return {...result,status:"no_strictly_positive_latent_law"};
  const aLow=max(0,one.sub(w).sub(m)),nonA=one.sub(aLow);
  const wLow=min(max(nonA.div(2),max(0,nonA.sub(m))),min(w,nonA)),mLow=nonA.sub(wLow);
  const low=aLow.sq().div(wLow.mul(mLow));
  const rem=one.sub(a);
  let wHigh=zero,upper=null;
  if(rem.cmp(0)>0){const ends=[max(0,rem.sub(m)),min(w,rem)]; wHigh=ends[0].mul(rem.sub(ends[0])).cmp(ends[1].mul(rem.sub(ends[1])))<=0?ends[0]:ends[1]; const den=wHigh.mul(rem.sub(wHigh));if(den.cmp(0)>0)upper=a.sq().div(den)}
  return {...result,status:"ok",lower:endpoint(low),upper:endpoint(upper,upper!==null),
   lower_closure_witness:point([wLow,aLow,mLow]),upper_closure_witness:point([wHigh,a,rem.sub(wHigh)]),
   positive_feasible_witness:point(u.map(v=>v.div(total)))};
 }
 function ratio(b,s){
  if(b.status!=="ok"||s.status!=="ok")return {status:"unevaluable_observation_contract"};
  const lo=s.lower.exact==="0"||b.upper.exact===null?zero:q(s.lower.exact).div(b.upper.exact);
  const hi=b.lower.exact==="0"||s.upper.exact===null?null:q(s.upper.exact).div(b.lower.exact);
  return {status:"ok",lower:endpoint(lo),upper:endpoint(hi,hi!==null)};
 }
 function common(js){
  if(!js.length||js.some(j=>j.status!=="ok"))return {status:"unevaluable_observation_contract",separated:false};
  const lo=max(...js.map(j=>j.lower.exact)),fs=js.filter(j=>j.upper.exact!==null);
  const hi=fs.length?min(...fs.map(j=>j.upper.exact)):null;
  const separated=hi!==null&&(lo.cmp(hi)>0||(lo.cmp(hi)===0&&lo.cmp(0)===0));
  return {status:separated?"separated":"compatible",separated,lower:endpoint(lo),upper:endpoint(hi,hi!==null)};
 }
 function arm(a,df,dd){
  const F=min(1,q(a.calibration.control_false_gate_upper_exact).add(df));
  const g=q(a.gate_positive_lower.exact);
  const beta=F.cmp(1)===0?zero:max(0,g.sub(F).div(one.sub(F)));
  const lower=Object.fromEntries(routes.map(r=>[r,max(0,q(a.marginal_limits[r].correct_call_lower.exact).sub(dd))]));
  const caps=Object.fromEntries(routes.map(r=>{const den=beta.mul(lower[r]); return [r,(den.cmp(0)===0?one:min(1,q(a.marginal_limits[r].observed_upper.exact).div(den))).str()]}));
  return {...capsProjection(caps),nativeF:F.str(),beta:beta.str(),nativeCorrect:Object.fromEntries(routes.map(r=>[r,lower[r].str()]))};
 }
 function evaluate(df,dd){
  df=q(df);dd=q(dd);
  const contexts=fixture.contexts.map(c=>{const b=arm(c.baseline,df,dd),s=arm(c.selected,df,dd);return {id:c.id,baseline:b,selected:s,J:ratio(b,s)}});
  const joint=common(contexts.map(c=>c.J));
  return {deltaF:df.str(),deltaD:dd.str(),contexts,common_J:joint,reject:joint.separated};
 }
 function summary(r){
  return {deltaF:r.deltaF,deltaD:r.deltaD,reject:r.reject,status:r.common_J.status,
  common:[q(r.common_J.lower.exact).num(),r.common_J.upper.exact===null?"infinity":q(r.common_J.upper.exact).num()],
  arms:r.contexts.flatMap(c=>["baseline","selected"].map(a=>({id:c.id+"."+a,nativeF:q(c[a].nativeF).num(),beta:q(c[a].beta).num(),nativeCorrect:q(c[a].nativeCorrect.W).num(),caps:Object.fromEntries(routes.map(x=>[x,q(c[a].caps[x]).num()])),Q:[q(c[a].lower.exact).num(),c[a].upper.exact===null?"infinity":q(c[a].upper.exact).num()]})))};
 }
 function bracket(path,bits=24){
  const D=1n<<BigInt(bits);let lo=0n,hi=D,calls=0;
  const at=n=>{calls++;const t=new R(n,D);return path==="both"?evaluate(t,t):path==="falsepass"?evaluate(t,0):evaluate(0,t)};
  const start=at(lo),end=at(hi);
  if(start.common_J.status==="unevaluable_observation_contract")throw Error("requires evaluable start");
  if(!start.reject)return {case:"not_rejected_at_zero",calls};
  if(end.reject)return {case:"rejected_through_one",calls};
  let steps=0;
  while(hi-lo>1n){const m=(lo+hi)/2n,r=at(m);if(r.common_J.status==="unevaluable_observation_contract")throw Error("unexpected unevaluable");if(r.reject)lo=m;else hi=m;steps++}
  const left=at(lo),right=at(hi);
  return {path,denominator:String(D),leftNumerator:String(lo),rightNumerator:String(hi),left:(new R(lo,D)).str(),right:(new R(hi,D)).str(),leftDecimal:(new R(lo,D)).num(),rightDecimal:(new R(hi,D)).num(),width:(new R(1n,D)).str(),steps,calls,leftResult:left,rightResult:right};
 }
 return {R,q,min,max,sum,point,endpoint,capsProjection,ratio,common,evaluate,summary,bracket,routes};
}

function runChecks(fixture) {
 const c=makeCalc(fixture),{q,sum,routes}=c;
 const zeroCounts={},zeroFailures=[],at0=c.evaluate(0,0);
 function same(kind,a,b,label){zeroCounts[kind]=(zeroCounts[kind]||0)+1;if(JSON.stringify(a)!==JSON.stringify(b))zeroFailures.push({kind,label,a,b})}
 for(let i=0;i<fixture.contexts.length;i++)for(const arm of ["baseline","selected"]){
  const old=fixture.contexts[i][arm],now=at0.contexts[i][arm],id=fixture.contexts[i].id+"."+arm;
  same("eligibility",now.beta,old.eligibility.eligible_fraction_lower_exact,id);
  for(const route of routes)same("caps",now.caps[route],old.caps[route],id+"."+route);
  for(const end of ["lower","upper"])for(const key of ["exact","infinity","attained_in_positive_domain"])same("QEndpointFields",now[end][key],old[end][key],id+"."+end+"."+key);
  for(const key of ["lower_closure_witness","upper_closure_witness","positive_feasible_witness"])for(const route of routes)same("witnessCoordinates",now[key][route],old[key][route],id+"."+key+"."+route);
  same("sumCaps",now.sum_caps_exact,old.sum_caps_exact,id);same("armStatus",now.status,old.status,id);
 }
 for(let i=0;i<fixture.contexts.length;i++){
  const a=at0.contexts[i].J,b=fixture.contexts[i].J;
  for(const end of ["lower","upper"])for(const key of ["exact","infinity","attained_in_positive_domain"])same("JEndpointFields",a[end][key],b[end][key],fixture.contexts[i].id+"."+end+"."+key);
  same("JStatus",a.status,b.status,fixture.contexts[i].id);
 }
 for(const end of ["lower","upper"])for(const key of ["exact","infinity","attained_in_positive_domain"])same("commonEndpointFields",at0.common_J[end][key],fixture.common_J[end][key],end+"."+key);
 same("commonStatus",at0.common_J.status,fixture.common_J.status,"common");
 same("rejection",at0.reject,fixture.reject_common_J,"rejection");
 const counts={},failures=[];
 function check(kind,ok,detail){counts[kind]=(counts[kind]||0)+1;if(!ok)failures.push({kind,detail})}
 function validateProjection(p,label){
  if(p.status!=="ok")return;
  const cp=routes.map(r=>q(p.caps[r]));
  for(const key of ["lower_closure_witness","upper_closure_witness","positive_feasible_witness"]){
   const v=routes.map(r=>q(p[key][r]));check("witnessSimplex",sum(v).cmp(1)===0,label+"."+key);
   for(let i=0;i<3;i++)check("witnessCap",v[i].cmp(0)>=0&&v[i].cmp(cp[i])<=0,label+"."+key+"."+routes[i]);
   if(key==="positive_feasible_witness")check("positiveWitness",v.every(x=>x.cmp(0)>0),label);
   else {
    const den=v[0].mul(v[2]),ep=key==="lower_closure_witness"?p.lower:p.upper;
    if(ep.exact===null)check("infiniteEndpointDenominator",den.cmp(0)===0,label+"."+key);
    else check("finiteEndpointValue",den.cmp(0)>0&&v[1].sq().div(den).cmp(ep.exact)===0,label+"."+key);
   }
  }
 }
 for(const path of ["both","falsepass","correctcall"]){
  let prev=null;
  for(let k=0;k<=256;k++){
   const t=q(k).div(256),r=c.evaluate(path==="correctcall"?0:t,path==="falsepass"?0:t);
   check("pathEvaluable",r.common_J.status!=="unevaluable_observation_contract",path+k);
   if(prev){
    check("rejectNeverReappears",prev.reject||!r.reject,path+k);
    check("commonLowerNonincreasing",q(r.common_J.lower.exact).cmp(prev.common_J.lower.exact)<=0,path+k);
    check("commonUpperNondecreasing",r.common_J.upper.exact===null||prev.common_J.upper.exact!==null&&q(r.common_J.upper.exact).cmp(prev.common_J.upper.exact)>=0,path+k);
   }
   for(let i=0;i<2;i++)for(const arm of ["baseline","selected"]){
    const p=r.contexts[i][arm];validateProjection(p,path+k+i+arm);
    if(prev){
     const prior=prev.contexts[i][arm];
     for(const route of routes)check("capsNondecreasing",q(p.caps[route]).cmp(prior.caps[route])>=0,path+k+i+arm+route);
     check("QLowerNonincreasing",q(p.lower.exact).cmp(prior.lower.exact)<=0,path+k+i+arm);
     check("QUpperNondecreasing",p.upper.exact===null||prior.upper.exact!==null&&q(p.upper.exact).cmp(prior.upper.exact)>=0,path+k+i+arm);
    }
   }
   prev=r;
  }
 }
 for(let w=0;w<=4;w++)for(let a=0;a<=4;a++)for(let m=0;m<=4;m++){
  const caps={W:q(w).div(4).str(),A:q(a).div(4).str(),M:q(m).div(4).str()},p=c.capsProjection(caps),label=JSON.stringify(caps);
  validateProjection(p,label);
  if(p.status!=="ok"){check("emptyClassification",w+a+m<4?p.status==="empty_observation_contract_set":(w*a*m===0&&p.status==="no_strictly_positive_latent_law"),label);continue}
  for(let i=1;i<16;i++)for(let j=1;j<16-i;j++){
   const k=16-i-j;if(i>4*w||j>4*a||k>4*m)continue;const value=q(j*j).div(i*k);
   check("latticeQBounds",value.cmp(p.lower.exact)>=0&&(p.upper.exact===null||value.cmp(p.upper.exact)<=0),label+":"+i+","+j+","+k);
  }
 }
 const F=q(fixture.contexts[0].baseline.calibration.control_false_gate_upper_exact),g=q(fixture.contexts[0].baseline.gate_positive_lower.exact),d=q(fixture.contexts[0].baseline.marginal_limits.W.correct_call_lower.exact),saturated=[];
 for(const [label,df,dd] of [["F_equals_g",g.sub(F),0],["F_equals_one",q(1).sub(F),0],["d_equals_zero",0,d],["both_saturated",1,1]]){
  const r=c.evaluate(df,dd);saturated.push({label,deltaF:r.deltaF,deltaD:r.deltaD,common:r.common_J});
  check("saturatedCompatible",r.common_J.status==="compatible"&&!r.reject,label);
  for(const ctx of r.contexts)for(const arm of ["baseline","selected"]){
   const a=ctx[arm];check("saturatedCaps",routes.every(x=>a.caps[x]==="1"),label+ctx.id+arm);
   check("saturatedQ",a.lower.exact==="0"&&!a.lower.attained_in_positive_domain&&a.upper.exact===null&&!a.upper.attained_in_positive_domain,label+ctx.id+arm);
  }
 }
 const singleton=c.capsProjection({W:"1/3",A:"1/3",M:"1/3"});
 check("singletonExact",singleton.lower.exact==="1"&&singleton.upper.exact==="1"&&singleton.lower.attained_in_positive_domain&&singleton.upper.attained_in_positive_domain,"singleton");
 const brackets=["both","falsepass","correctcall"].map(path=>c.bracket(path));
 const u=q(fixture.contexts[0].baseline.marginal_limits.W.observed_upper.exact),v=q(fixture.contexts[0].selected.marginal_limits.W.observed_upper.exact),z=q(fixture.contexts[1].selected.marginal_limits.W.observed_upper.exact);
 const polynomial=brackets.flatMap(b=>["leftResult","rightResult"].map(side=>{
  const r=b[side],p=r.contexts[0].baseline,h=q(p.beta).mul(p.nativeCorrect.W);
  const L=h.sub(v.mul(2)).sq().div(v.sq()).mul(h.sub(u.mul(2))).div(u);
  const U=v.sq().div(z.mul(h.sub(v).sub(z))).mul(u.sq()).div(h.sub(u.mul(2)).sq());
  const lhs=h.sub(v.mul(2)).sq().mul(h.sub(u.mul(2))).mul(h.sub(u.mul(2))).mul(h.sub(u.mul(2))).mul(z).mul(h.sub(v).sub(z)),rhs=v.sq().sq().mul(u.sq()).mul(u);
  return {path:b.path,side,h:h.str(),LMatches:L.cmp(r.common_J.lower.exact)===0,UMatches:U.cmp(r.common_J.upper.exact)===0,polynomialSign:lhs.cmp(rhs),matchesDecision:(lhs.cmp(rhs)>0)===r.reject};
 }));
 const rows=["both","falsepass","correctcall"].flatMap(path=>["0","1/20","1/10","3/20","1/5"].map(t=>({path,result:c.evaluate(path==="correctcall"?0:t,path==="falsepass"?0:t)})));
 const receipt={zero:{counts:zeroCounts,total:Object.values(zeroCounts).reduce((a,b)=>a+b,0),failures:zeroFailures},invariants:{counts,total:Object.values(counts).reduce((a,b)=>a+b,0),failures},polynomial,saturated,brackets,rows};
 if(zeroFailures.length||failures.length||polynomial.some(x=>!x.LMatches||!x.UMatches||!x.matchesDecision))throw Error("Check failure: "+JSON.stringify(receipt));
 return receipt;
}

if (!process.argv[2]) throw Error("Provide the pinned fixture JSON path");
const fixture = JSON.parse(readFileSync(process.argv[2], "utf8"));
const result = runChecks(fixture);
console.log(JSON.stringify(result, null, 2));
