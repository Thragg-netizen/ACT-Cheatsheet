import csv,math,collections as C,sys,random
rows=[r for f in sys.argv[1:] for r in csv.DictReader(open(f))]
POS={'A':1,'F':1,'B':2,'G':2,'C':3,'H':3,'D':4,'J':4,'E':5,'K':5}
for r in rows: r['qnum']=int(r['qnum']); r['pos']=POS[r['answer']]
by=C.defaultdict(list)
for r in rows:
    if r['form']!='J08': by[(r['form'],r['section'],r['format'])].append(r)
def z(p,n,base): return (p-base)/math.sqrt(base*(1-base)/n)
print("=== A. Streak avoidance significance (same position as previous Q) ===")
for sec in ['English','Math','Reading','Science']:
    for fmt in ['old','enhanced']:
        same=tot=0
        for (f,s,fm),rs in by.items():
            if s!=sec or fm!=fmt: continue
            rs.sort(key=lambda r:r['qnum'])
            for a,b in zip(rs,rs[1:]): tot+=1; same+=(a['pos']==b['pos'])
        if not tot: continue
        k=5 if (sec=='Math' and fmt=='old') else 4
        p=same/tot; print(f"{sec:8s} {fmt:8s} pairs={tot:5d} same={p*100:5.1f}%  chance={100/k:.0f}%  z={z(p,tot,1/k):+.1f}")
print("\n=== B. Per-form letter balance: observed SD of per-position counts vs binomial SD if random ===")
for sec in ['English','Math','Reading','Science']:
    cnts=[]; N=None; k=None
    for (f,s,fm),rs in by.items():
        if s!=sec or fm!='old': continue
        N=len(rs); k=5 if sec=='Math' else 4
        c=C.Counter(r['pos'] for r in rs); cnts+= [c[p] for p in range(1,k+1)]
    if not cnts: continue
    mean=sum(cnts)/len(cnts); sd=math.sqrt(sum((x-mean)**2 for x in cnts)/len(cnts))
    bsd=math.sqrt(N*(1/k)*(1-1/k))
    print(f"{sec:8s} N={N} choices={k} forms={len(cnts)//k}: per-position count mean={mean:.1f} observed SD={sd:.2f}  random SD would be={bsd:.2f}  min={min(cnts)} max={max(cnts)}")
print("\n=== C. Within-block balance (old format): Reading per passage (10Q), English per passage (15Q), Science per 10Q, Math per 15Q ===")
blk={'English':15,'Math':15,'Reading':10,'Science':10}
for sec,B in blk.items():
    k=5 if sec=='Math' else 4; mins=C.Counter(); maxs=C.Counter(); nb=0
    for (f,s,fm),rs in by.items():
        if s!=sec or fm!='old': continue
        rs.sort(key=lambda r:r['qnum'])
        for i in range(0,len(rs),B):
            c=C.Counter(r['pos'] for r in rs[i:i+B]); nb+=1
            mins[min(c[p] for p in range(1,k+1))]+=1; maxs[max(c.values())]+=1
    print(f"{sec:8s} block={B}Q blocks={nb} | min-count-of-any-letter distribution: {dict(sorted(mins.items()))} | max-count distribution: {dict(sorted(maxs.items()))}")
print("\n=== D. Enhanced-format forms only (25MC1, 25MC5): per-position counts by section ===")
for (f,s,fm),rs in sorted(by.items()):
    if fm!='enhanced': continue
    c=C.Counter(r['pos'] for r in rs); print(f"{f} {s:8s} n={len(rs)} "+" ".join(f"P{p}={c[p]}" for p in sorted(c)))
