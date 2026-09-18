import csv,sys,math,collections as C
from itertools import groupby
files=sys.argv[1:]
rows=[]
for f in files:
    rows+=list(csv.DictReader(open(f)))
POS={'A':1,'F':1,'B':2,'G':2,'C':3,'H':3,'D':4,'J':4,'E':5,'K':5}
for r in rows: r['qnum']=int(r['qnum']); r['pos']=POS[r['answer']]
by=C.defaultdict(list)
for r in rows: by[(r['form'],r['section'])].append(r)
for k in by: by[k].sort(key=lambda r:r['qnum'])
forms=sorted({r['form'] for r in rows})
print(f"FORMS ({len(forms)}): {' '.join(forms)}\nrows={len(rows)}\n")
def chi(counts,n,k):
    e=n/k; return sum((c-e)**2/e for c in counts)
def pct(a,b): return f"{100*a/b:5.1f}%" if b else "  n/a"
print("=== 1. Correct-answer POSITION frequency (1=A/F 2=B/G 3=C/H 4=D/J 5=E/K) ===")
for sec in ['English','Math','Reading','Science']:
    for fmt in ['old','enhanced']:
        rs=[r for r in rows if r['section']==sec and r['format']==fmt]
        if not rs: continue
        k=5 if (sec=='Math' and fmt=='old') else 4
        cnt=[sum(1 for r in rs if r['pos']==p) for p in range(1,k+1)]
        n=len(rs); x2=chi(cnt,n,k)
        # chi2 critical (df=k-1): df3 7.81 (p.05) 11.34(p.01); df4 9.49 / 13.28
        crit={3:(7.81,11.34),4:(9.49,13.28)}[k-1]
        sig='**p<.01' if x2>crit[1] else ('*p<.05' if x2>crit[0] else 'ns')
        print(f"{sec:8s} {fmt:8s} n={n:5d} "+" ".join(f"P{p}={pct(c,n)}" for p,c in enumerate(cnt,1))+f"  chi2={x2:5.1f} {sig}")
print("\n=== 2. Same position as previous question (streak tendency) ===")
for sec in ['English','Math','Reading','Science']:
    same=tot=0
    for (f,s),rs in by.items():
        if s!=sec or f=='J08': continue
        for a,b in zip(rs,rs[1:]):
            tot+=1; same+=(a['pos']==b['pos'])
    k=5 if sec=='Math' else 4  # mostly old-format
    print(f"{sec:8s} P(same as prev)={pct(same,tot)}  (random baseline ~{100/k:.0f}% for {k}-choice; enhanced math is 4-choice)")
print("\n=== 3. Runs of identical position (excluding J08) ===")
for sec in ['English','Math','Reading','Science']:
    runs=C.Counter(); nq=0; longest=0
    for (f,s),rs in by.items():
        if s!=sec or f=='J08': continue
        nq+=len(rs)
        for pos,g in groupby(r['pos'] for r in rs):
            L=len(list(g)); runs[L]+=1; longest=max(longest,L)
    print(f"{sec:8s} questions={nq} runs: "+" ".join(f"len{L}:{runs[L]}" for L in sorted(runs))+f"  longest={longest}")
print("\n=== 4. Position frequency by quarter of section (old format) ===")
for sec in ['English','Math','Reading','Science']:
    rs=[r for r in rows if r['section']==sec and r['format']=='old']
    if not rs: continue
    N=max(r['qnum'] for r in rs); k=5 if sec=='Math' else 4
    for q in range(4):
        lo,hi=q*N//4+1,(q+1)*N//4
        sub=[r for r in rs if lo<=r['qnum']<=hi]; n=len(sub)
        cnt=[sum(1 for r in sub if r['pos']==p) for p in range(1,k+1)]
        print(f"{sec:8s} Q{lo:2d}-{hi:2d} n={n:4d} "+" ".join(f"P{p}={pct(c,n)}" for p,c in enumerate(cnt,1)))
print("\n=== 5. Per-form: are all positions used ~evenly? (min/max count of any position per section, old format) ===")
for sec in ['English','Math','Reading','Science']:
    spread=[]
    for (f,s),rs in by.items():
        if s!=sec or rs[0]['format']!='old': continue
        c=C.Counter(r['pos'] for r in rs); spread.append((f,min(c.values()),max(c.values()),len(rs)))
    if spread:
        mn=min(x[1] for x in spread); mx=max(x[2] for x in spread)
        print(f"{sec:8s} across {len(spread)} forms: least-used position count ranges down to {mn}, most-used up to {mx} (of {spread[0][3]} Qs)")
