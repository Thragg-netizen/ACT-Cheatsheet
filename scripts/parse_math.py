import csv, re, sys
from pathlib import Path

SCRATCH = Path(r"./work/")
TXT = SCRATCH / "txt"
OUT = SCRATCH / "math"
OUT.mkdir(exist_ok=True)

FORM_FILE = {
    "25MC1": "2025_25MC1-2025_25MC1-2025.pdf.txt",
    "25MC5": "2025_25MC5-2025_25MC5-2025.pdf.txt",
    "52C":   "9_ACT 1996 Form 52C.pdf.txt",
    "59F":   "15_ACT 200301 Form 59F.pdf.txt",
    "61C":   "19_ACT 200601 Form 61C.pdf.txt",
    "64E":   "23_ACT 200704 Form 64E.pdf.txt",
    "67C":   "31_ACT 200906 Form 67C.pdf.txt",
    "D03":   "417_ACT 202012 Form D03.pdf.txt",
    "D05":   "419_ACT 202104 Form D05.pdf.txt",
    "D06":   "420_ACT 202106 Form D06.pdf.txt",
    "E23":   "421_ACT 202112 Form E23.pdf.txt",
    "E25":   "423_ACT-202204-E25.pdf.txt",
    "E26":   "424_ACT-202206-E26.pdf.txt",
    "F07":   "425_ACT-202212-Form-F07.pdf.txt",
    "F11":   "426_ACT-202304-Form-F11.pdf.txt",
    "F12":   "542_ACT-202306-Form-F12.pdf.txt",
    "G01":   "543_ACT-202309-Form-G01.pdf.txt",
    "G19":   "544_ACT-202404-Form-G19.pdf.txt",
    "G20":   "545_ACT-202406-Form-G20.pdf.txt",
    "H11":   "546_ACT-202409-Form-H11.pdf.txt",
    "H31":   "547_ACT-202412-Form-H31.pdf.txt",
    "Z04":   "418_ACT 202104 Form Z04.pdf.txt",
    "Z08":   "422_ACT-202204-Z08.pdf.txt",
    "Z14":   "548_ACT-202502-Form-Z14.pdf.txt",
}

# (?!\d) avoids matching decimal choice values like "2.30" or "5.75" as if
# they were question-start lines ("N. text") -- real question numbers are
# always followed by a space/letter, never another digit.
QSTART_RE = re.compile(r'^\s*(\d{1,3})\.(?!\d)\s*(.*)$')
LABEL_RE = re.compile(r'^\s*([A-K])\.\s*(.*)$')
CND_RE = re.compile(r'cannot be determined', re.IGNORECASE)


def choice_letters(fmt, qnum):
    odd = qnum % 2 == 1
    if fmt == "old":
        return ['A', 'B', 'C', 'D', 'E'] if odd else ['F', 'G', 'H', 'J', 'K']
    else:
        return ['A', 'B', 'C', 'D'] if odd else ['F', 'G', 'H', 'J']


def normalize_num(s):
    if not s:
        return None
    t = s.strip()
    if not t:
        return None
    t = t.replace('\u2212', '-').replace('\u2013', '-').replace('\u2014', '-')
    allowed = set('0123456789,.-/+ ')
    if not all(c in allowed for c in t):
        return None
    t2 = t.replace(',', '').replace(' ', '')
    if not t2:
        return None
    try:
        if re.fullmatch(r'[+-]?\d+', t2):
            return float(t2)
        if re.fullmatch(r'[+-]?\d+\.\d+', t2):
            return float(t2)
        if re.fullmatch(r'[+-]?\d+/\d+', t2):
            n, d = t2.split('/')
            d = float(d)
            if d == 0:
                return None
            return float(n) / d
    except ValueError:
        return None
    return None


def try_parse_choices(math_lines, i, qnum, fmt, expected_n):
    """Attempt to find all expected choice labels starting search at index i.
    Returns (choice_vals, next_i) on success, None on failure (bails out if a
    line matching the NEXT question number is hit before all choices found)."""
    n = len(math_lines)
    letters = choice_letters(fmt, qnum)
    choice_vals = {}
    for letter in letters:
        label_idx = None
        j = i
        while j < n:
            line = math_lines[j]
            mq = QSTART_RE.match(line)
            if mq and int(mq.group(1)) == qnum + 1 and qnum + 1 <= expected_n:
                return None
            ml = LABEL_RE.match(line)
            if ml and ml.group(1) == letter:
                label_idx = j
                break
            j += 1
        if label_idx is None:
            return None
        same_line = LABEL_RE.match(math_lines[label_idx]).group(2).strip()
        i = label_idx + 1
        if same_line:
            value = same_line
        else:
            value = None
            if i < n:
                nxt = math_lines[i].strip()
                if nxt and not QSTART_RE.match(nxt) and not LABEL_RE.match(nxt):
                    value = nxt
                    i += 1
        choice_vals[letter] = value
    return choice_vals, i


def parse_form(form, fmt, expected_n):
    """Returns (questions_dict, fail_reason). questions_dict: qnum -> {letter: text_or_None}

    Boilerplate "Note: ... 1. Illustrative figures ... 4. The word average ..."
    reappears at every page break and its numbered items 1-4 can look like a
    fake question start. We handle this by retrying: if a candidate "N." start
    line doesn't yield a full set of choice labels before the next question
    number appears, we treat it as a false match and search further ahead for
    another candidate with the same number.
    """
    fname = FORM_FILE[form]
    path = TXT / fname
    lines = path.read_text(encoding='utf-8', errors='replace').split('\n')

    idx1 = idx2 = None
    for i, l in enumerate(lines):
        if idx1 is None and 'END OF TEST 1' in l:
            idx1 = i
        elif idx1 is not None and idx2 is None and 'END OF TEST 2' in l:
            idx2 = i
            break
    if idx1 is None or idx2 is None:
        return None, "END OF TEST 1/2 markers not found"

    math_lines = lines[idx1 + 1: idx2]
    n = len(math_lines)

    i = 0
    qnum = 1
    questions = {}
    while qnum <= expected_n:
        search_from = i
        result = None
        while True:
            start_idx = None
            k = search_from
            while k < n:
                m = QSTART_RE.match(math_lines[k])
                if m and int(m.group(1)) == qnum:
                    start_idx = k
                    break
                k += 1
            if start_idx is None:
                break
            result = try_parse_choices(math_lines, start_idx + 1, qnum, fmt, expected_n)
            if result is not None:
                break
            search_from = start_idx + 1
        if result is None:
            return questions, f"question {qnum} start/choices not found"
        choice_vals, next_i = result
        questions[qnum] = choice_vals
        i = next_i
        qnum += 1

    return questions, None


def main():
    keys_path = SCRATCH / "answer_keys.csv"
    answers = {}  # (form, qnum) -> letter
    forms_seen = {}  # form -> (format, max_qnum)
    with open(keys_path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            if row['section'] != 'Math':
                continue
            form = row['form']
            qn = int(row['qnum'])
            answers[(form, qn)] = row['answer']
            fmt = row['format']
            prev = forms_seen.get(form)
            if prev is None or qn > prev[1]:
                forms_seen[form] = (fmt, qn)

    all_forms = sorted(set(r['form'] for r in csv.DictReader(open(keys_path, encoding='utf-8'))))

    kept = []
    dropped = []

    out_rows = []
    for form in all_forms:
        if form not in forms_seen:
            dropped.append((form, "no Math rows in answer_keys.csv"))
            continue
        fmt, expected_n = forms_seen[form]
        if form not in FORM_FILE:
            dropped.append((form, "no txt file mapped"))
            continue
        questions, fail = parse_form(form, fmt, expected_n)
        if fail:
            dropped.append((form, fail))
            continue
        # validate every qnum has an answer key entry, and choice counts correct
        ok = True
        reason = None
        for qn in range(1, expected_n + 1):
            if (form, qn) not in answers:
                ok = False
                reason = f"no answer key for q{qn}"
                break
            expected_letters = choice_letters(fmt, qn)
            if set(questions[qn].keys()) != set(expected_letters):
                ok = False
                reason = f"q{qn} choice set mismatch"
                break
        if not ok:
            dropped.append((form, reason))
            continue

        kept.append((form, fmt, expected_n))
        for qn in range(1, expected_n + 1):
            choices = questions[qn]
            letters = choice_letters(fmt, qn)
            nchoices = len(letters)
            has_cnd = 0
            cnd_letter = ''
            for L in letters:
                v = choices[L]
                if v and CND_RE.search(v):
                    has_cnd = 1
                    cnd_letter = L
                    break

            nums = {}
            all_numeric = 1
            for L in letters:
                v = normalize_num(choices[L])
                if v is None:
                    all_numeric = 0
                nums[L] = v

            key_letter = answers[(form, qn)]
            key_rank = key_is_min = key_is_max = key_is_median = ''
            if all_numeric:
                sorted_letters = sorted(letters, key=lambda L: nums[L])
                rank = sorted_letters.index(key_letter) + 1
                key_rank = rank
                key_is_min = 1 if rank == 1 else 0
                key_is_max = 1 if rank == nchoices else 0
                if nchoices == 5:
                    key_is_median = 1 if rank == 3 else 0
                elif nchoices == 4:
                    key_is_median = 1 if rank in (2, 3) else 0
                else:
                    key_is_median = 0

            out_rows.append({
                'form': form, 'qnum': qn, 'nchoices': nchoices,
                'has_cnd': has_cnd, 'cnd_letter': cnd_letter,
                'all_numeric': all_numeric, 'key_rank': key_rank,
                'key_is_min': key_is_min, 'key_is_max': key_is_max,
                'key_is_median': key_is_median,
            })

    out_csv = OUT / "math_choices.csv"
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['form', 'qnum', 'nchoices', 'has_cnd', 'cnd_letter',
                                           'all_numeric', 'key_rank', 'key_is_min', 'key_is_max', 'key_is_median'])
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    print(f"Kept {len(kept)} forms, dropped {len(dropped)} forms.")
    for form, fmt, n in kept:
        print(f"  KEPT {form} ({fmt}, {n}q)")
    for form, reason in dropped:
        print(f"  DROPPED {form}: {reason}")
    print(f"Total rows: {len(out_rows)}")
    print(f"CSV: {out_csv}")


if __name__ == '__main__':
    main()
