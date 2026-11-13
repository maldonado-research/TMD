"use strict";
/* Copyright (c) 2026 Ricardo Maldonado. MIT; see repository LICENSE.
 * Exact sensitivity projection of already-certified endpoints.
 * This module does not compute confidence limits or authenticate inputs.
 */
class Rational {
  constructor(n,d=1n) {
    n=BigInt(n); d=BigInt(d); if(d===0n) throw Error("zero denominator");
    if(d<0n){n=-n;d=-d;} let a=n<0n?-n:n,b=d;
    while(b){const t=a%b;a=b;b=t;} this.n=n/a;this.d=d/a;
  }
  add(x){return new Rational(this.n*x.d+x.n*this.d,this.d*x.d);}
  sub(x){return new Rational(this.n*x.d-x.n*this.d,this.d*x.d);}
  mul(x){return new Rational(this.n*x.n,this.d*x.d);}
  div(x){if(x.n===0n)throw Error("division by zero");return new Rational(this.n*x.d,this.d*x.n);}
  cmp(x){const v=this.n*x.d-x.n*this.d;return v<0n?-1:v>0n?1:0;}
  sq(){return this.mul(this);}
  str(){return this.d===1n?String(this.n):String(this.n)+"/"+String(this.d);}
  approx(){return Number(this.n)/Number(this.d);}
}
const ZERO=new Rational(0n),ONE=new Rational(1n),TWO=new Rational(2n);
const ROUTES=["W","A","M"];
function minimum(...xs){return xs.reduce((a,b)=>a.cmp(b)<=0?a:b);}
function maximum(...xs){return xs.reduce((a,b)=>a.cmp(b)>=0?a:b);}
function probability(s) {
  if(typeof s!=="string" || s.length>200 || !/^\d+(\/[1-9]\d*)?$/.test(s))throw Error("probability must be an exact nonnegative integer/fraction string");
  const p=s.split("/"); const n=BigInt(p[0]),d=BigInt(p[1]||"1");
  if(n.toString(2).length>256 || d.toString(2).length>256)throw Error("rational token too large");
  const x=new Rational(n,d);if(x.cmp(ONE)>0)throw Error("probability exceeds one");return x;
}
function exactKeys(x,keys,label){
  if(!x || typeof x!=="object" || Array.isArray(x) || Object.keys(x).sort().join("|")!==keys.slice().sort().join("|"))throw Error("invalid keys: "+label);
}
function projectCaps(caps) {
  const [w,a,m]=ROUTES.map(k=>caps[k]),sum=w.add(a).add(m);
  if(sum.cmp(ONE)<0)return {status:"empty_observation_contract_set"};
  if([w,a,m].some(x=>x.n===0n))return {status:"no_strictly_positive_latent_law"};
  const amin=maximum(ZERO,ONE.sub(w).sub(m)),smin=ONE.sub(amin);
  const loW=maximum(ZERO,smin.sub(m)),hiW=minimum(w,smin);
  const W=minimum(maximum(smin.div(TWO),loW),hiW);
  const lower=amin.sq().div(W.mul(smin.sub(W)));
  const smax=ONE.sub(a);
  let upper=null;
  if(smax.n!==0n){
    const left=maximum(ZERO,smax.sub(m)),right=minimum(w,smax);
    const leftDen=left.mul(smax.sub(left)),rightDen=right.mul(smax.sub(right));
    const den=minimum(leftDen,rightDen);
    if(den.n!==0n)upper=a.sq().div(den);
  }
  return {status:"ok",lower:lower.str(),upper:upper===null?null:upper.str()};
}
function ratioBounds(base,sel) {
  if(base.status!=="ok" || sel.status!=="ok")return {status:"unevaluable_observation_contract"};
  const b=probabilityFree(base.lower),s=probabilityFree(sel.lower);
  const lower=s.n===0n || base.upper===null?ZERO:s.div(probabilityFree(base.upper));
  const upper=b.n===0n || sel.upper===null?null:probabilityFree(sel.upper).div(b);
  return {status:"ok",lower:lower.str(),upper:upper===null?null:upper.str()};
}
function probabilityFree(s){const [n,d="1"]=s.split("/");return new Rational(BigInt(n),BigInt(d));}
function intersect(intervals) {
  if(!intervals.length || intervals.some(x=>x.status!=="ok"))return {status:"unevaluable_observation_contract",separated:false};
  const lo=maximum(...intervals.map(x=>probabilityFree(x.lower)));
  const finite=intervals.filter(x=>x.upper!==null).map(x=>probabilityFree(x.upper));
  const hi=finite.length?minimum(...finite):null;
  const separated=hi!==null && (lo.cmp(hi)>0 || (lo.cmp(hi)===0 && lo.n===0n));
  return {status:separated?"separated":"compatible",separated,lower:lo.str(),upper:hi===null?null:hi.str()};
}
function analyzeTransport(input,deficits) {
  exactKeys(deficits,["false_gate","correct_call"],"deficits");
  const df=probability(deficits.false_gate),dd=probability(deficits.correct_call);
  if(!input || input.schema_version!==1 || !Array.isArray(input.contexts) || input.contexts.length<1 || input.contexts.length>64)throw Error("invalid endpoint bundle");
  const alpha=probability(input.alpha);
  if(alpha.n===0n || alpha.cmp(ONE)===0)throw Error("alpha must be strictly between zero and one");
  const ids=new Set();
  const contexts=input.contexts.map(c=>{
    exactKeys(c,["id","baseline","selected"],"context");
    if(typeof c.id!=="string" || !c.id || ids.has(c.id))throw Error("invalid context id"); ids.add(c.id);
    const out={id:c.id};
    for(const arm of ["baseline","selected"]){
      const x=c[arm];exactKeys(x,["F","g","U","L"],"arm");exactKeys(x.U,ROUTES,"U");exactKeys(x.L,ROUTES,"L");
      const F=minimum(ONE,probability(x.F).add(df)),g=probability(x.g);
      const beta=F.cmp(ONE)===0?ZERO:maximum(ZERO,g.sub(F).div(ONE.sub(F)));
      const L=Object.fromEntries(ROUTES.map(k=>[k,maximum(ZERO,probability(x.L[k]).sub(dd))]));
      const caps=Object.fromEntries(ROUTES.map(k=>{
        const den=beta.mul(L[k]),u=probability(x.U[k]);
        return [k,den.n===0n?ONE:minimum(ONE,u.div(den))];
      }));
      out[arm]={native_false_gate_upper:F.str(),eligible_fraction_lower:beta.str(),
        native_correct_lower:Object.fromEntries(ROUTES.map(k=>[k,L[k].str()])),
        caps:Object.fromEntries(ROUTES.map(k=>[k,caps[k].str()])),Q:projectCaps(caps)};
    }
    out.J=ratioBounds(out.baseline.Q,out.selected.Q);return out;
  });
  const common=intersect(contexts.map(x=>x.J));
  return {schema_version:1,deficits,contexts,common_J:common,
    reject_common_J:contexts.length>=2 && common.separated,
    confidence_recomputed:false,scope:"Conditional outer projection of supplied endpoints; no native authentication or power calculation."};
}
function pathDeficits(path,t) {
  if(!["both","false_gate","correct_call"].includes(path))throw Error("invalid path");
  return {false_gate:path==="correct_call"?"0":t,correct_call:path==="false_gate"?"0":t};
}
function bracketFrontier(input,path,bits=24) {
  if(!Number.isInteger(bits)||bits<1||bits>32)throw Error("bits must be 1..32");
  const start=analyzeTransport(input,pathDeficits(path,"0"));
  if(start.common_J.status==="unevaluable_observation_contract")throw Error("frontier requires evaluable starting caps");
  if(!start.reject_common_J)return {status:"starting_point_not_rejecting",path};
  const end=analyzeTransport(input,pathDeficits(path,"1"));
  if(end.reject_common_J)throw Error("endpoint unexpectedly rejects");
  const denominator=1n<<BigInt(bits);let lo=0n,hi=denominator;
  while(hi-lo>1n){const mid=(lo+hi)/2n,t=new Rational(mid,denominator).str();
    const result=analyzeTransport(input,pathDeficits(path,t));
    if(result.common_J.status==="unevaluable_observation_contract")throw Error("evaluable nesting failed");
    if(result.reject_common_J)lo=mid;else hi=mid;
  }
  const a=new Rational(lo,denominator),b=new Rational(hi,denominator);
  return {status:"certified_dyadic_bracket",path,bits,still_rejecting:a.str(),no_longer_rejecting:b.str(),
    width:new Rational(1n,denominator).str(),lower_approximation:a.approx(),upper_approximation:b.approx(),
    boundary_scope:"Bracket for first loss along this common path, from evaluable starting caps; no claim of exact boundary equality or native mismatch estimate."};
}
if(typeof module!=="undefined" && module.exports)module.exports={analyzeTransport,bracketFrontier,projectCaps,Rational};
