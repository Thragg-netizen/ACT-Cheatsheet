# ACT 
Built 2026-09-18 from 33 real ACT forms with validated answer keys (6,239 answers; 30 old-format forms 1996–2023 from text extraction plus OCR, and three 2025 Enhanced forms 25MC1, 25MC5, J08), plus choice-text parses of 1,600 English and 510 Math questions. Every number below has its sample size. Baseline = what random would give.

## Coverage
| Source | Forms (any section) | Answers |
|---|---|---|
| text | 25 | 5114 |
| text | 25 | 5114 |
| tir-manual | 1 | 215 |
| ocr-tir | 4 | 400 |
| ocr-tess | 5 | 365 |
| ocr-tess | 5 | 365 |
| ocr-tess | 5 | 365 |
| ocr-tess | 5 | 365 |
| ocr-early | 7 | 910 |
| **total** | **39** (29 with all four sections) | **7004** |

Of the 85 distinct full forms in the collection, 39 contribute at least one validated section. Every key passed two checks: exact question count per section, and the odd/even letter rule (odd questions A–E, even F–K). OCR-sourced keys were cross-checked where two independent engines read the same page (73C Math and Science: 100 of 100 letters agreed).

## 1. The test you are taking (Enhanced ACT, mandatory on paper since Sept 2025)
| Section | Questions | Minutes | Pace | Scored items |
|---|---|---|---|---|
| English | 50 | 35 | 42 sec/question | 40 (10 unscored field items, position varies) |
| Math | 45 | 50 | 67 sec/question | 41 |
| Reading | 36 | 40 | 10 min per passage (4 passages, 9 Q each) | 27 |
| Science (optional) | 40 | 40 | ~5.7 min per passage (7 passages) | 34 |
- Composite = average of English, Math, Reading ONLY. Science does not count toward it.
- Math now has 4 choices, not 5. Odd questions A–D, even F–J (still alternates on the 2025 paper forms).
- No guessing penalty. Never leave a bubble blank.
- Break comes after Math. Calculator only on Math; no CAS (TI-89, Nspire CAS, HP Prime, ClassPad).
- Bring: printed admission ticket, photo ID, calculator, #2 pencils, watch without alarm. Report by 8:00.

## 2. What a 34 costs you (from the 2025 official conversion tables)
| Section | raw needed for 30 | 32 | 34 | 36 |
|---|---|---|---|---|
| English (of 40 scored) | 35–36 | 36–37 | 37–38 | 40 |
| Math (of 41) | 33–35 | 35–37 | 37–38 | 40 |
| Reading (of 27) | 23 | 24 | 25 | 27 |
| Science (of 34) | 28–30 | 30–31 | 32 | 34 |
Reading is brutal: about 27 scored questions, so every miss is roughly one scale point. Two misses in Reading is still a 34; five misses is a 30. Precision matters more than speed there, and you have 10 minutes per passage, which is generous.

## 3. Patterns that are real (tested on this corpus)

### A. ACT balances the answer letters inside every section — use it to guess
Across 25 old-format forms every English letter is correct 17–21 times out of 75, and across 30 forms every Reading letter is correct 7–12 times out of 40 (29 of 30 forms sit in 8–12). Random keys would spread about twice as wide (observed SD 1.5 vs random 3.75 in English; 1.3 vs 2.7 in Reading). It holds per passage too: in 97% of Reading passages all four letters appear at least once in the 10 questions, and no letter appears 5+ times in 99% of them.
How to use it: when you must guess, glance at your bubbles for that passage/section and pick the letter you have used least. On the two 2025 forms the balance looked looser (English 10–17 per letter of 50), so treat this as a tiebreaker, not a law.

### B. Consecutive answers avoid repeating the same letter (English, Reading)
| Section | repeat rate | chance | pairs | significance |
|---|---|---|---|---|
| English (old) | 18.0% | 25% | 1,850 | z = -7.0 |
| Reading (old) | 15.6% | 25% | 1,170 | z = -7.4 |
| Reading (2025) | 14.3% | 25% | 70 | z = -2.1 |
| Science | 22.4% | 25% | 1,092 | weak |
| Math | 21.1% | 20% | 1,534 | none |
Runs of 4 identical letters in a row occurred 3 times in 1,975 English answers and 0 times in 1,272 Reading answers. If you are guessing on a Reading or English question and you are confident about the neighbors, pick a letter different from both neighbors. Measured on this corpus, that lifts a blind guess from 25% to 29% in English and 33% in Reading (27% in Science; nothing in Math).

### C. English: DELETE is correct half the time; NO CHANGE is not special
- "DELETE the underlined portion" / "OMIT" offered 90 times: correct 45 times (50%, chance 25%, z = 5.5). When DELETE is offered, seriously consider it. It is always the last choice (D/J).
- NO CHANGE correct 353 of 1,298 times (27.2%; 2025 forms 23.7%). It is at chance. Do not favor it or fear it.
- On bare underline-fix questions (no question stem), the shortest choice is correct 37% (340/919) and the longest only 16% (132/833). Cross out the longest, lean toward the shortest.
- On questions with a written stem ("Which choice best...", "The writer is considering..."), that edge disappears (shortest 27%, longest 20%). Read those for meaning; length tells you nothing.
- Every question on the 2025 forms has an explicit stem; pure underline-only items are gone. Read the stem first, it tells you what is being tested.

### D. Math
- "Cannot be determined from the given information": offered 10 times, correct 0 times. Never pick it. (It did not appear at all on the two 2025 forms.)
- When all choices are plain numbers (n = 183), the smallest value was correct only 13% of the time (chance 20–25%). The largest was at chance. If guessing between numbers, don't pick the smallest.
- Old-format hard questions (Q46–60, n = 315): the correct answer was an outer letter (A/F, D/J, E/K) 74% of the time vs. 60% expected, and B/G or C/H only 26%. Suggestive for late questions, unverified on the 4-choice 2025 format.
- Questions run easy to hard. With 67 seconds each, budget 40 seconds for Q1–25 and bank the rest for Q35–45. The 2025 forms' hard tail included complex numbers, trig graphs, and one matrix question (early, not late).
- 4 choices now means each elimination is worth more: knocking out two leaves a coin flip.

### E. Reading
- No letter edge beyond A and B above. Passage labels on 2025 forms are just LITERARY NARRATIVE and INFORMATIONAL; the paired Passage A/B set can be any slot (it was passage III on one form and passage I on the other).
- 9 questions per passage, 10 minutes. Read the passage (3–4 min), then answer; do not skim-and-hunt, the line references are sparse on the new form.

### F. Science (if you're taking it)
- 7 passages on both 2025 forms: 2–3 Data Representation, 3–4 Research Summaries, 1–2 Conflicting Viewpoints. Do Conflicting Viewpoints last; it is the only one that requires actually reading.
- About 9–13 of 40 questions did not point at a figure (mostly in Conflicting Viewpoints and outside-knowledge items). Everything else is find-the-number-in-the-table.
- It does not affect your Composite, so treat it as low-stakes and keep your energy for the three sections that do.

## 4. Folklore that did NOT survive the data
- "NO CHANGE is right more than chance" — no (27%).
- "There's a best letter to guess" — no; all letters within 2 points of each other in every section.
- "The answer is never the same letter three times in a row" — happens (38 runs of 3 in English), just less than random.
- "Shortest answer always" — only on underline-fix items, and it's 37% not 90%.

## 5. Tomorrow, in order
1. Tonight: set out ID, ticket, calculator (fresh batteries), pencils. Sleep. Cramming content tonight is worth less than being sharp.
2. English: read the stem, cross out the longest choice, consider DELETE when offered, keep to 42 s/question. Guess with the least-used letter that differs from neighbors.
3. Math: never "cannot be determined"; never blank; on numeric guesses avoid the smallest value; save 10+ minutes for the last 10.
4. Reading: 10 min/passage, aim for zero careless misses (each one is a point). Guess against the neighbors' letters.
5. Science: figure-lookup speed, Conflicting Viewpoints last.
