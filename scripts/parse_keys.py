import re, os, glob, csv, sys

TXT_DIR = sys.argv[1]
OUT_CSV = sys.argv[2]
REPORT = sys.argv[3]

EXPECTED_OLD = {"English": 75, "Math": 60, "Reading": 40, "Science": 40}
EXPECTED_ENH = {"English": 50, "Math": 45, "Reading": 36, "Science": 40}

ODD_LETTERS = set("ABCDE")
EVEN_LETTERS = set("FGHJK")

# section anchor patterns -> section name
ANCHOR_PATTERNS = [
    (re.compile(r"\bPOW\b"), "English"),
    (re.compile(r"\bPHM\b"), "Math"),
    (re.compile(r"\bKID\b"), "Reading"),
    (re.compile(r"\bIOD\b"), "Science"),
    (re.compile(r"(?i)Test\s*1\s*[:\-–—]\s*English"), "English"),
    (re.compile(r"(?i)Test\s*2\s*[:\-–—]\s*Math"), "Math"),
    (re.compile(r"(?i)Test\s*3\s*[:\-–—]\s*Reading"), "Reading"),
    (re.compile(r"(?i)Test\s*4\s*[:\-–—]\s*Science"), "Science"),
    (re.compile(r"(?i)^English\s*Scoring Key", re.M), "English"),
    (re.compile(r"(?i)^Mathematics\s*Scoring Key", re.M), "Math"),
    (re.compile(r"(?i)^Reading\s*Scoring Key", re.M), "Reading"),
    (re.compile(r"(?i)^Science\s*Scoring Key", re.M), "Science"),
    (re.compile(r"\bUM\b"), "English"),
    (re.compile(r"\bEA\b"), "Math"),
    (re.compile(r"\bSS\b"), "Reading"),
]

START_PATTERNS = [
    re.compile(r"(?i)\btest\s*1\s*[:\-–—]?\s*english"),
    re.compile(r"(?i)english\s*scoring\s*key"),
    re.compile(r"(?i)scoring\s*keys?\s*for"),
]

# number then (optional period) then a single valid letter token, same line or next line
PAIR_RE = re.compile(r"(?m)^[ \t]*(\d{1,3})\.?\s+([A-HJK])(?=[\s'\"\.,]|$)")


def find_start(text):
    idxs = []
    for pat in START_PATTERNS:
        m = pat.search(text)
        if m:
            idxs.append(m.start())
    return min(idxs) if idxs else None


def build_anchors(window):
    anchors = []
    for pat, section in ANCHOR_PATTERNS:
        for m in pat.finditer(window):
            anchors.append((m.start(), section))
    anchors.sort()
    return anchors


def section_for_offset(anchors, offset):
    sec = None
    for pos, s in anchors:
        if pos <= offset:
            sec = s
        else:
            break
    return sec


def parse_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    start = find_start(text)
    if start is None:
        return None, "no scoring-key section header found"
    window = text[start:]
    anchors = build_anchors(window)
    if not anchors:
        return None, "no section anchors found"

    pairs_by_section = {"English": {}, "Math": {}, "Reading": {}, "Science": {}}
    for m in PAIR_RE.finditer(window):
        num = int(m.group(1))
        letter = m.group(2)
        sec = section_for_offset(anchors, m.start())
        if sec is None:
            continue
        d = pairs_by_section[sec]
        if num not in d:
            d[num] = letter
        # if conflicting, keep first occurrence (most local/most likely correct)
    return pairs_by_section, None


def sanity_check(section, answers, expected_count):
    """returns (ok, reason)"""
    if not answers:
        return False, "empty"
    n = len(answers)
    nums = sorted(answers)
    if nums != list(range(1, expected_count + 1)):
        missing = set(range(1, expected_count + 1)) - set(nums)
        extra = set(nums) - set(range(1, expected_count + 1))
        return False, f"count={n} expected={expected_count} missing={sorted(missing)[:5]} extra={sorted(extra)[:5]}"
    violations = 0
    for q, letter in answers.items():
        if q % 2 == 1 and letter not in ODD_LETTERS:
            violations += 1
        if q % 2 == 0 and letter not in EVEN_LETTERS:
            violations += 1
    if violations:
        return False, f"odd/even pattern violated in {violations} of {n} answers"
    return True, "ok"


def derive_form_year(basename):
    # basename like "107_ACT 201506 Form 73C.pdf.txt" or "417_ACT 202012 Form D03.pdf.txt"
    # or "2025_25MC1-2025_25MC1-2025.pdf.txt" or "2018_A09-2018_A09-2018.pdf.txt"
    name = basename
    # tests_github style: <year>_<form>-...
    m = re.match(r"^(20\d\d)_([0-9A-Za-z]+)-", name)
    if m:
        return m.group(2), int(m.group(1))
    # tests/ style: contains "Form <code>" and a date token
    mform = re.search(r"Form[\s\-]?([A-Za-z0-9]+)", name)
    form = mform.group(1) if mform else None
    if not form:
        # e.g. 44_2001-56B.pdf -> form 56B
        mform2 = re.search(r"(\d{4})-(\S+?)\.pdf", name)
        if mform2:
            form = mform2.group(2)
    myear = re.search(r"\b(19|20)(\d\d)(\d{2})?\b", name)
    year = None
    if myear:
        yy = myear.group(0)[:4]
        year = int(yy)
    return form, year


def main():
    files = sorted(glob.glob(os.path.join(TXT_DIR, "*.txt")))
    rows = []
    report_lines = []
    section_ok_count = {"English": 0, "Math": 0, "Reading": 0, "Science": 0}
    total_forms_with_any = 0
    fail_lines = []
    skip_lines = []

    for path in files:
        base = os.path.basename(path)
        if base.endswith("SC.pdf.txt"):
            continue  # score chart, not needed
        # AK files replace their sibling main pdf; main "scanned" pdfs get skipped anyway if no key found
        is_enhanced = bool(re.search(r"25MC", base))
        expected = EXPECTED_ENH if is_enhanced else EXPECTED_OLD
        form, year = derive_form_year(base)

        result, err = parse_file(path)
        if result is None:
            skip_lines.append(f"{base}: SKIPPED ({err})")
            continue

        any_ok = False
        file_fail = []
        for section, expected_count in expected.items():
            answers = result[section]
            ok, reason = sanity_check(section, answers, expected_count)
            if ok:
                section_ok_count[section] += 1
                any_ok = True
                for q in range(1, expected_count + 1):
                    rows.append({
                        "form": form,
                        "year": year,
                        "format": "enhanced" if is_enhanced else "old",
                        "section": section,
                        "qnum": q,
                        "answer": answers[q],
                    })
            else:
                file_fail.append(f"{section}: {reason}")
        if any_ok:
            total_forms_with_any += 1
        if file_fail:
            fail_lines.append(f"{base} (form={form}, year={year}): " + "; ".join(file_fail))

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["form", "year", "format", "section", "qnum", "answer"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(f"Total forms with at least one section parsed: {total_forms_with_any}\n\n")
        f.write("Section success counts:\n")
        for s, c in section_ok_count.items():
            f.write(f"  {s}: {c}\n")
        f.write("\nSkipped files (no scoring key section found):\n")
        for l in skip_lines:
            f.write(f"  {l}\n")
        f.write("\nSection failures:\n")
        for l in fail_lines:
            f.write(f"  {l}\n")

    print(f"rows={len(rows)} forms_ok={total_forms_with_any}")
    print(f"section_ok_count={section_ok_count}")
    print(f"skipped={len(skip_lines)} failed_files={len(fail_lines)}")


if __name__ == "__main__":
    main()
