import re,glob
f=glob.glob('txt/549*')[0]; L=[l.strip() for l in open(f,encoding='utf-8')]
heads={'English':'English Scoring Key','Math':'Mathematics Scoring Key','Reading':'Reading Scoring Key','Science':'Science Scoring Key'}
idx={s:next(i for i,l in enumerate(L) if l.startswith(h)) for s,h in heads.items()}
order=sorted(idx,key=idx.get); rows=[]
for k,s in enumerate(order):
    a=idx[s]; b=idx[order[k+1]] if k+1<len(order) else a+400
    seg=L[a:b]; i=0; got=[]
    while i<len(seg)-1:
        if re.fullmatch(r'\d{1,2}',seg[i]) and re.fullmatch(r'[A-K]',seg[i+1]):
            got.append((int(seg[i]),seg[i+1])); i+=2
        else: i+=1
    nums=[q for q,_ in got]
    bad=[(q,a) for q,a in got if (q%2==1 and a not in 'ABCDE') or (q%2==0 and a not in 'FGHJK')]
    print(s,'count',len(got),'range',min(nums),max(nums),'dupes',len(nums)-len(set(nums)),'oddeven_viol',len(bad))
    rows+=[f'J08,2025,enhanced,{s},{q},{a}' for q,a in got]
open('j08_keys.csv','w').write('form,year,format,section,qnum,answer\n'+'\n'.join(rows)+'\n')
