import csv, re, glob, os, sys

SC = r"./work/"
SC = os.environ.get("SCRATCH", SC)
TXT_DIR = os.path.join(SC, "txt")
OUT_DIR = os.path.join(SC, "english")
os.makedirs(OUT_DIR, exist_ok=True)

FORM_MAP = {
    "52C": "9_ACT 1996 Form 52C.pdf.txt",
    "59F": "15_ACT 200301 Form 59F.pdf.txt",
    "61C": "19_ACT 200601 Form 61C.pdf.txt",
    "64E": "23_ACT 200704 Form 64E.pdf.txt",
    "67C": "31_ACT 200906 Form 67C.pdf.txt",
    "D03": "417_ACT 202012 Form D03.pdf.txt",
    "D05": "419_ACT 202104 Form D05.pdf.txt",
    "D06": "420_ACT 202106 Form D06.pdf.txt",
    "E23": "421_ACT 202112 Form E23.pdf.txt",
    "E25": "423_ACT-202204-E25.pdf.txt",
    "E26": "424_ACT-202206-E26.pdf.txt",
    "F07": "425_ACT-202212-Form-F07.pdf.txt",
    "F11": "426_ACT-202304-Form-F11.pdf.txt",
    "F12": "542_ACT-202306-Form-F12.pdf.txt",
    "G01": "543_ACT-202309-Form-G01.pdf.txt",
    "G19": "544_ACT-202404-Form-G19.pdf.txt",
    "G20": "545_ACT-202406-Form-G20.pdf.txt",
    "H11": "546_ACT-202409-Form-H11.pdf.txt",
    "H31": "547_ACT-202412-Form-H31.pdf.txt",
    "Z04": "418_ACT 202104 Form Z04.pdf.txt",
    "Z08": "422_ACT-202204-Z08.pdf.txt",
    "Z14": "548_ACT-202502-Form-Z14.pdf.txt",
    "25MC1": "2025_25MC1-2025_25MC1-2025.pdf.txt",
    "25MC5": "2025_25MC5-2025_25MC5-2025.pdf.txt",
}
EXPECTED_N = {"25MC1": 50, "25MC5": 50}  # else 75

ODD_LETTERS = ["A", "B", "C", "D"]
EVEN_LETTERS = ["F", "G", "H", "J"]

QNUM_RE = re.compile(r'^\s*(\d{1,3})\.\s*(.*)$')
CHOICE_RE = re.compile(r'^\s*([A-DFGHJ])\.\s*(.*)$')
# Page-turn boilerplate that shows up between the last choice of a question
# and the next question when they straddle a page break -- if left alone it
# gets swallowed into that choice's text along with the next page's passage
# content (inflating its length hugely). Also matches bare page/box numbers.
PAGE_BREAK_RE = re.compile(
    r'^\s*(GO ON TO THE NEXT PAGE\.?|STOP!.*|END OF TEST \d+|ACT[- ]\S+|www\.\S+|\d{1,3}'
    r'|ENGLISH TEST|DIRECTIONS:.*|\d+ Minutes\W+\d+ Questions'
    r'|PASSAGE [IVX]+.*|Questions? \d+.*ask.* about (the preceding|the passage).*)\s*$'
)

def parse_form(form, fname, expected_n):
    path = os.path.join(TXT_DIR, fname)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    # Scan the WHOLE file (not bounded by "ENGLISH TEST"/"MATHEMATICS TEST"
    # headings) and collect every maximal run of sequential question numbers
    # 1,2,3,... with matching ABCD/FGHJ 4-choice structure. Every ACT test
    # section (English/Math/Reading/Science) restarts numbering at 1, so a
    # "1." (with a plausible choice-letter start) always begins a new run;
    # any number that isn't exactly prev+1 is treated as ordinary passage
    # text, not a question start. We then pick whichever run has exactly
    # expected_n questions with clean 4-choice structure as "the" English
    # section. This sidesteps pymupdf block-reordering quirks where the
    # "ENGLISH TEST" heading/directions text can appear AFTER question 1-5
    # in extraction order.
    runs = []
    cur_run = []
    cur_q = None
    cur_letter = None
    buf = []
    cur_choice_locked = False

    def flush_buf():
        nonlocal buf
        txt = " ".join(s.strip() for s in buf if s.strip() != "")
        txt = re.sub(r'\s+', ' ', txt).strip()
        buf = []
        return txt

    def close_current_target():
        # cur_choice_locked means this target's real content was already
        # saved (a page-break boilerplate line ended it); anything
        # accumulated in buf since then is discarded passage/junk text.
        nonlocal cur_q
        if cur_q is None:
            buf.clear()
            return
        txt = flush_buf()
        if cur_choice_locked:
            return
        if cur_letter is None:
            cur_q["stem"] = txt
        else:
            cur_q["choices"][cur_letter] = txt

    def finish_run():
        nonlocal cur_run, cur_q
        close_current_target()
        if cur_q is not None:
            cur_run.append(cur_q)
        cur_q = None
        if cur_run:
            runs.append(cur_run)
        cur_run = []

    force_next_content = False
    high_water = 0    # highest question number accepted into the current run
    owed = set()      # numbers < high_water skipped by a forward jump, still expected
    owed_since = {}   # qnum -> line index when it was added to owed, for staleness expiry
    MAX_SKIP = 6       # ACT occasionally prints a "whole passage" box question
                        # (or a paragraph-reorder question) ahead of its numeric
                        # position on the page; tolerate a small out-of-order cluster.
    OWED_EXPIRY_LINES = 150  # an owed number must resolve within ~150 lines (same
                              # page/passage) or it's abandoned -- prevents a stray
                              # scoring-key table thousands of lines later (which also
                              # prints bare "74." etc.) from falsely "resolving" it.
    for line_idx, raw in enumerate(lines):
        line = raw.rstrip("\n")
        if owed:
            for stale in [q for q in owed if line_idx - owed_since[q] > OWED_EXPIRY_LINES]:
                owed.discard(stale)
                del owed_since[stale]

        if cur_q is not None and not cur_choice_locked and PAGE_BREAK_RE.match(line):
            # Page-turn boilerplate: end the in-progress target right here
            # (saving whatever real content it already has) and discard
            # everything else -- boilerplate lines and next page's passage
            # text -- until the next real question/choice marker.
            close_current_target()
            cur_choice_locked = True
            force_next_content = False
            continue

        if force_next_content:
            # We just opened a choice letter with no content on its own line
            # (e.g. "D.$"). The very next line is unconditionally that
            # choice's content -- some answer choices are themselves bare
            # numbers like "1." (e.g. "place the new sentence after
            # Sentence: A. 1. B. 2. C. 3. D. 4."), which would otherwise be
            # misread as a new question-number marker.
            force_next_content = False
            buf.append(line)
            continue

        qm = QNUM_RE.match(line)
        if qm:
            n = int(qm.group(1))
            is_new_run = (n == 1 and not owed)
            is_continue = (n == high_water + 1)
            is_owed = (n in owed)
            is_skip_ahead = (not owed and 1 < n - high_water <= MAX_SKIP)
            if is_new_run or is_continue or is_owed or is_skip_ahead:
                close_current_target()
                if cur_q is not None:
                    cur_run.append(cur_q)
                if is_new_run and cur_run:
                    runs.append(cur_run)
                    cur_run = []
                    owed = set()
                    owed_since = {}
                    high_water = 0
                if is_owed:
                    owed.discard(n)
                    owed_since.pop(n, None)
                elif is_skip_ahead:
                    for gap_n in range(high_water + 1, n):
                        owed.add(gap_n)
                        owed_since[gap_n] = line_idx
                if n > high_water:
                    high_water = n
                elif is_new_run:
                    high_water = 1
                qnum = n
                cur_q = {"qnum": qnum, "stem": "", "choices": {}}
                cur_letter = None
                cur_choice_locked = False
                rest = qm.group(2)
                expected_letters = ODD_LETTERS if qnum % 2 == 1 else EVEN_LETTERS
                cm = CHOICE_RE.match(rest)
                if cm and cm.group(1) == expected_letters[0]:
                    cur_letter = expected_letters[0]
                    buf = [cm.group(2)]
                    force_next_content = (cm.group(2).strip() == "")
                else:
                    buf = [rest] if rest.strip() else []
                continue

        if cur_q is not None:
            qnum = cur_q["qnum"]
            expected_letters = ODD_LETTERS if qnum % 2 == 1 else EVEN_LETTERS
            next_letter_idx = 0 if cur_letter is None else expected_letters.index(cur_letter) + 1
            cm = CHOICE_RE.match(line)
            if cm and next_letter_idx < len(expected_letters) and cm.group(1) == expected_letters[next_letter_idx]:
                close_current_target()
                cur_letter = expected_letters[next_letter_idx]
                cur_choice_locked = False
                buf = [cm.group(2)]
                force_next_content = (cm.group(2).strip() == "")
                continue

        buf.append(line)

    finish_run()

    candidates = [r for r in runs if len(r) == expected_n]
    if not candidates:
        lens = [len(r) for r in runs]
        return None, f"no run of length {expected_n} found; run lengths seen: {lens}"
    # validate letter structure for each candidate; take first clean one
    for run in candidates:
        errs = []
        for q in run:
            expected_letters = ODD_LETTERS if q["qnum"] % 2 == 1 else EVEN_LETTERS
            got = list(q["choices"].keys())
            if got != expected_letters:
                errs.append(f"q{q['qnum']}: expected choices {expected_letters}, got {got}")
        if not errs:
            return run, None
    return None, "; ".join(errs[:5]) + (f" (+{len(errs)-5} more)" if len(errs) > 5 else "")

def analyze(q):
    qnum = q["qnum"]
    letters = ODD_LETTERS if qnum % 2 == 1 else EVEN_LETTERS
    choices = q["choices"]
    has_nochange = 1 if choices[letters[0]].strip().upper() == "NO CHANGE" else 0
    has_delete = 0
    delete_letter = ""
    for L in letters:
        t = choices[L].strip().lower()
        if "delete the underlined portion" in t or "omit the underlined portion" in t:
            has_delete = 1
            delete_letter = L
            break
    lens = {L: len(choices[L]) for L in letters}
    minlen = min(lens.values())
    maxlen = max(lens.values())
    min_letters = [L for L in letters if lens[L] == minlen]
    max_letters = [L for L in letters if lens[L] == maxlen]
    shortest_letter = min_letters[0] if len(min_letters) == 1 else ""
    longest_letter = max_letters[0] if len(max_letters) == 1 else ""
    is_rhetorical = 1 if q["stem"].strip() != "" else 0
    return {
        "qnum": qnum,
        "has_nochange": has_nochange,
        "has_delete": has_delete,
        "delete_letter": delete_letter,
        "len_A": lens[letters[0]],
        "len_B": lens[letters[1]],
        "len_C": lens[letters[2]],
        "len_D": lens[letters[3]],
        "shortest_letter": shortest_letter,
        "longest_letter": longest_letter,
        "is_rhetorical": is_rhetorical,
    }

def main():
    out_rows = []
    dropped = []
    used_forms = []
    for form, fname in FORM_MAP.items():
        expected_n = EXPECTED_N.get(form, 75)
        questions, err = parse_form(form, fname, expected_n)
        if err:
            dropped.append((form, err))
            print(f"DROP {form}: {err}", file=sys.stderr)
            continue
        used_forms.append(form)
        for q in questions:
            r = analyze(q)
            r["form"] = form
            out_rows.append(r)

    out_path = os.path.join(OUT_DIR, "english_choices.csv")
    cols = ["form","qnum","has_nochange","has_delete","delete_letter","len_A","len_B","len_C","len_D","shortest_letter","longest_letter","is_rhetorical"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow({c: r[c] for c in cols})

    print(f"Wrote {len(out_rows)} rows for {len(used_forms)} forms to {out_path}")
    print(f"Used forms: {used_forms}")
    print(f"Dropped forms: {dropped}")

if __name__ == "__main__":
    main()
