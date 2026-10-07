"""Independent exact finite synthetic oracle for paired-aliquot implementations.

Enumerate per-cell assignments and count-of-positive-jump partitions. Neither
oracle uses the implementation's Euler recurrence or polynomial convolution.
No biological observation, fit, significance test or statistical certificate.
"""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from math import factorial
from pathlib import Path


def assignments(law, p1, p2, frame):
    if frame == 'disjoint':
        categories = [((0,0),1-p1-p2),((1,0),p1),((0,1),p2)]
    else:
        categories = [((0,0),(1-p1)*(1-p2)),((1,0),p1*(1-p2)),
                      ((0,1),(1-p1)*p2),((1,1),p1*p2)]
    out={}; enumerated=0
    for k,w in law.items():
        for choices in itertools.product(range(len(categories)),repeat=k):
            a=b=0;weight=w
            for choice in choices:
                (da,db),q=categories[choice]
                a+=da;b+=db;weight*=q
            out[a,b]=out.get((a,b),F())+weight;enumerated+=1
    return out,enumerated


def partition_coefficient(intensities,a,b):
    jumps=[(i,j,v) for (i,j),v in sorted(intensities.items())
           if i+j>0 and v and i<=a and j<=b]
    total=F()
    def visit(index,left_a,left_b,product):
        nonlocal total
        if index==len(jumps):
            if left_a==0 and left_b==0:total+=product
            return
        i,j,v=jumps[index]
        limits=[]
        if i:limits.append(left_a//i)
        if j:limits.append(left_b//j)
        for count in range(min(limits)+1):
            visit(index+1,left_a-i*count,left_b-j*count,
                  product*v**count/factorial(count))
    visit(0,a,b,F(1))
    return total


def moments(marked,m):
    mean_a=m*sum((a*w for (a,b),w in marked.items()),F())
    mean_b=m*sum((b*w for (a,b),w in marked.items()),F())
    var_a=m*sum((a*a*w for (a,b),w in marked.items()),F())
    var_b=m*sum((b*b*w for (a,b),w in marked.items()),F())
    cov=m*sum((a*b*w for (a,b),w in marked.items()),F())
    return [mean_a,mean_b],[var_a,var_b],cov


def run(implementation):
    spec=importlib.util.spec_from_file_location('reviewed_paired_aliquot',implementation)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    laws=[{0:F(1)},{1:F(1)},{2:F(1)},{1:F(3,4),3:F(1,4)},
          {0:F(1,3),3:F(2,3)},{2:F(1,2),4:F(1,2)}]
    pairs=[(F(0),F(0)),(F(0),F(1)),(F(1),F(0)),(F(1,4),F(1,4)),
           (F(1,6),F(1,3)),(F(1,2),F(1,2)),(F(3,4),F(3,4)),(F(1),F(1))]
    counts={'cell_assignment_tables':0,'cell_assignments_enumerated':0,
            'marked_probability_entries_compared':0,'compound_coefficients_vs_jump_partitions':0,
            'finite_moment_and_void_fields':0,'independent_culture_coefficients':0,
            'exact_counterexample_assertions':0,'extreme_32bit_input_assertions':0}
    for law in laws:
        for p1,p2 in pairs:
            frames=['overlapping']+(['disjoint'] if p1+p2<=1 else [])
            for frame in frames:
                marked,enumerated=assignments(law,p1,p2,frame)
                actual=module.joint_clone_law(law,p1,p2,frame)
                assert sum(marked.values(),F())==1
                for key in set(marked)|set(actual):
                    assert marked.get(key,F())==actual.get(key,F())
                    counts['marked_probability_entries_compared']+=1
                counts['cell_assignment_tables']+=1
                counts['cell_assignments_enumerated']+=enumerated
                for m in [F(0),F(2,3),F(3,2)]:
                    result=module.paired_model(law,m,p1,p2,frame,4)
                    means,variances,cov=moments(marked,m)
                    assert result['means']==means
                    assert result['variances']==variances
                    assert result['covariance']==cov
                    assert result['negative_log_P00']==m*(1-marked.get((0,0),F()))
                    counts['finite_moment_and_void_fields']+=4
                    intensities={key:m*w for key,w in marked.items()}
                    for (a,b),q in result['relative_coefficients'].items():
                        assert q==partition_coefficient(intensities,a,b)
                        counts['compound_coefficients_vs_jump_partitions']+=1
            # Separate independent-culture histories: axis-only jump intensities.
            for m in [F(0),F(2,3),F(3,2)]:
                first,_=assignments(law,p1,F(0),'disjoint')
                second,_=assignments(law,F(0),p2,'disjoint')
                intensities={key:m*w for key,w in first.items() if key!=(0,0)}
                for key,w in second.items():
                    if key!=(0,0):intensities[key]=intensities.get(key,F())+m*w
                result=module.paired_model(law,m,p1,p2,'independent_cultures',4)
                assert result['negative_log_P00']==m*(2-first.get((0,0),F())-second.get((0,0),F()))
                assert result['covariance']==0
                counts['finite_moment_and_void_fields']+=2
                for (a,b),q in result['relative_coefficients'].items():
                    assert q==partition_coefficient(intensities,a,b)
                    counts['independent_culture_coefficients']+=1
    examples={}
    for frame,intensity,cov in [('disjoint',F(3,4),F(1,8)),
                              ('overlapping',F(175,256),F(1,4)),
                              ('independent_cultures',F(7,8),F(0))]:
        x=module.paired_model({2:1},1,F(1,4),F(1,4),frame,4)
        assert x['negative_log_P00']==intensity
        assert x['covariance']==cov
        assert x['means']==[F(1,2)]*2 and x['variances']==[F(5,8)]*2
        assert x['negative_log_P0_marginals']==[F(7,16)]*2
        counts['exact_counterexample_assertions']+=4
        examples[frame]={'negative_log_P00':str(intensity),'covariance':str(cov)}
    split={}
    for frame,expected in [('disjoint',F(1,2)),('overlapping',F(25,34))]:
        q=module.paired_model({1:1},1,F(1,4),F(1,4),frame,2)['relative_coefficients']
        value=q[1,1]/(q[0,2]+q[1,1]+q[2,0])
        assert value==expected;counts['exact_counterexample_assertions']+=1
        split[frame]=str(value)
    # All positive compound-Poisson jump intensities agree, hence the complete
    # generating functions agree, not merely the compared low-order coefficients.
    histories=[(F(1),{2:F(1)}),(F(2),{0:F(1,2),2:F(1,2)})]
    measures=[{k:m*w for k,w in law.items() if k>0 and w} for m,law in histories]
    assert measures[0]==measures[1]=={2:F(1)}
    counts['exact_counterexample_assertions']+=1
    # Mixed-Poisson R|Lambda, Lambda in{0,3}: exact moments and an exact support
    # distinction; no Decimal exponential is needed to establish nonidentity.
    mean_l=F(1,3)*0+F(2,3)*3
    second_l=F(1,3)*0+F(2,3)*9
    mean_r=mean_l;var_r=mean_l+second_l-mean_l**2
    assert mean_r==2 and var_r==4
    assert F(1,4)**2*(var_r-mean_r)==F(1,8)
    assert -F(2)*F(1,4)**2==-F(1,8)
    counts['exact_counterexample_assertions']+=3
    den=2**32-1;other_den=2**32-5
    extreme_law={0:F(1,den),8:F(den-1,den)}
    extreme_cases=[(extreme_law,F(20),F(1,den),1-F(1,other_den),'disjoint'),
                   (extreme_law,F(1,den),F(1,den),1-F(1,other_den),'overlapping'),
                   ({2:F(1)},F(den-1,den),1-F(1,other_den),F(1,den),'disjoint'),
                   ({0:F(1)},F(20),F(1),F(1),'overlapping')]
    for law,m,p1,p2,frame in extreme_cases:
        result=module.paired_model(law,m,p1,p2,frame,2)
        ek=sum((k*w for k,w in law.items()),F())
        factorial_second=sum((k*(k-1)*w for k,w in law.items()),F())
        r=1-p1-p2 if frame=='disjoint' else (1-p1)*(1-p2)
        assert result['negative_log_P00']==m*(1-sum((w*r**k for k,w in law.items()),F()))
        assert result['means']==[m*p1*ek,m*p2*ek]
        assert result['variances']==[m*(p1*ek+p1*p1*factorial_second),m*(p2*ek+p2*p2*factorial_second)]
        assert result['covariance']==m*p1*p2*(factorial_second if frame=='disjoint' else factorial_second+ek)
        if frame=='disjoint':
            first=sum((w*k*p1*r**(k-1) for k,w in law.items() if k),F())
            second=sum((w*k*p2*r**(k-1) for k,w in law.items() if k),F())
        else:
            first=sum((w*k*p1*(1-p1)**(k-1)*(1-p2)**k for k,w in law.items() if k),F())
            second=sum((w*k*p2*(1-p2)**(k-1)*(1-p1)**k for k,w in law.items() if k),F())
        assert result['relative_coefficients'][1,0]==m*first
        assert result['relative_coefficients'][0,1]==m*second
        counts['extreme_32bit_input_assertions']+=6
    return {'status':'passed','scope':'independent exact finite synthetic assignment and positive-jump-partition oracles',
            'checks':counts,'implementation_sha256':hashlib.sha256(Path(implementation).read_bytes()).hexdigest(),
            'three_frame_counterexample':examples,'K1_conditional_middle_given_total2':split,
            'zero_mark_full_PGF_identity':'1*(u^2-1)=2*((1+u^2)/2-1)',
            'mixed_Poisson_counterexample':{'Lambda_values':['0','3'],'weights':['1/3','2/3'],'E_R':str(mean_r),'Var_R':str(var_r),'paired_covariance_p_quarter':'1/8','full_PGF_equal_to_K2_CP':False,'proof_of_inequality':'CP K2 has probability(R=1)=0; mixture has probability(R=1)=2 exp(-3)>0.'},
            'new_source_acquisitions':0,'biological_observations_or_fit':False,
            'statistical_tests_or_confidence_intervals':False,'new_theorem_or_priority_claim':False,
            'actual_study_fields_resolved':0}


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Independent verification requires assertions enabled; run without -O/-OO.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    result=run(args.implementation)
    result['reviewer_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
