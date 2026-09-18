Scripts expect a `./work/` folder containing pymupdf text dumps of ACT booklets (`work/txt/*.txt`) and produce `answer_keys.csv`. The booklets themselves are ACT's copyrighted material and are not included.
- extract_text.py  -> work/txt/*.txt
- parse_keys.py    -> answer_keys.csv (scoring-key tables)
- parse_j08.py     -> keys for the Oct 2025 J08 layout
- parse_english.py -> english_choices.csv (NO CHANGE / DELETE / choice lengths)
- parse_math.py    -> math_choices.csv (cannot-be-determined, numeric rank)
- stats.py, balance.py -> results/*.txt
