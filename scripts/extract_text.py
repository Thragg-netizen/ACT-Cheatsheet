import pymupdf, os, sys, glob

SCRATCH = sys.argv[1]
outdir = os.path.join(SCRATCH, "txt")
os.makedirs(outdir, exist_ok=True)

dirs = [r"C:\Coding\ACT\tests", r"C:\Coding\ACT\tests_github"]
report = []
for d in dirs:
    for path in sorted(glob.glob(os.path.join(d, "*.pdf"))):
        base = os.path.basename(path)
        outpath = os.path.join(outdir, base + ".txt")
        try:
            doc = pymupdf.open(path)
            text = "\n".join(page.get_text() for page in doc)
        except Exception as e:
            report.append(f"{base}: ERROR {e}")
            continue
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(text)
        nchars = len(text.strip())
        report.append(f"{base}: {nchars} chars, {len(doc)} pages")
        if nchars < 500:
            report.append(f"  ** LOW TEXT WARNING: {base}")

with open(os.path.join(SCRATCH, "extract_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("done", len(report))
