# Lab 01 — The Price of One Request

**Course:** LLMs, Agentic AI and Reinforcement Learning · Narxoz University
**Student:** Inria Kalalo

---

## 1. Part 1 Prediction vs. Measured Value

**Prediction (before Part 2), based on bytes/char from Part 1:**
- RU / EN ≈ 1.92x
- KK / EN ≈ 2.13x

**Basis for prediction:** Bytes, not characters or words. Bytes are the closest physical proxy for text size in UTF-8. Characters were rejected because a Cyrillic character is not equivalent in "weight" to a Latin one (bytes/char: EN=1.00, RU=1.83, KK=1.86). Words were rejected because they move in the opposite direction of cost — English has the most words (54) yet is the cheapest.

**Measured (Part 0, COMPLAINT item):**

| Tokenizer | RU / EN | KK / EN |
|---|---|---|
| o200k_base | 1.36x | 2.00x |
| cl100k_base | 2.47x | 4.49x |

**Reflection:** The byte-based prediction significantly underestimated the real cost, especially on `cl100k_base`. This confirms that tokenizer cost is not a physical property of text length — it is a property of the tokenizer's training data. `cl100k_base` was trained predominantly on English/Latin text, so it has efficient merge patterns for English but is forced to split Kazakh into smaller, more expensive pieces. No single offline measure (chars, bytes, or words) has any principled reason to match tokenizer behavior, since a BPE tokenizer's cost is determined by learned merge tables, not by the physical size of the input.

---

## 2. Annual Cost Table

**Volume:** 2,000 requests/day — representative of a mid-sized national support queue (e.g., a bank or telecom in Kazakhstan handling roughly one complaint every 45 seconds during business hours).

| Model | EN | RU | KK |
|---|---|---|---|
| haiku-4.5 | $3,592 | $4,627 | $5,111 |
| sonnet-5 | $7,183 | $9,255 | $10,223 |
| opus-5 | $17,958 | $23,137 | $25,557 |
| fable-5.1 | $35,916 | $46,275 | $51,115 |

**The two ratios that are not the same number:**

| | EN | RU | KK |
|---|---|---|---|
| Input-only ratio | 1.00x | 1.44x | 2.19x |
| Total bill ratio | 1.00x | 1.29x | 1.42x |

The input-only ratio is a pure property of the tokenizer. The total bill ratio is what is actually paid, and it is dampened here because output tokens (priced 5x input) dominate the bill, and the relative gap in answer length between languages is smaller than the gap in input tokens.

---

## 3. Model Recommendation for a Kazakh-Language Support Queue

**Recommendation: haiku-4.5**, provisionally.

**Cost argument:** haiku-4.5's list price is exactly 1/5th of opus-5's on both input and output. At 2,000 requests/day, that is a difference of over $20,000/year on Kazakh alone ($5,111 vs. $25,557).

**Quality argument:** Cost alone cannot settle this. The corpus contains a deliberate trap: the complaint claims a contract and statement are attached, but nothing is attached, and the system prompt requires answering only from provided documents — a compliant answer must decline to explain the rate change rather than fabricate a plausible-sounding cause. Without running Task 7's paired haiku-4.5 vs. opus-5 comparison (which requires the API key) and scoring both against a pre-registered checklist, I cannot confirm haiku-4.5 holds this line as reliably as opus-5. The recommendation is therefore provisional: haiku-4.5 for its decisive cost advantage, pending a manual pass/fail review of its Kazakh-language answers against the checklist (declines to fabricate a cause; invents no unstated numbers; answers entirely in Kazakh; names a concrete next step).

---

## 4. A Cost Lever Not Used in This Lab

Prompt caching (`CACHE_READ_FRACTION` in `prices.py`) is defined but never applied by `cost_usd`; since `system_prompt` makes up roughly 38–40% of every request's input tokens, caching it across repeated calls is one of the largest unused input-side savings available.

---

## Extension Tasks (Core)

### Task 1 — Add a corpus item (NOTICE)

Added a fourth parallel corpus item, `NOTICE` (a National Bank rate-update notice), to `texts.py`.

| Tokenizer | RU / EN | KK / EN |
|---|---|---|
| o200k_base | 1.33x | 1.50x |
| cl100k_base | 2.40x | 4.30x |

These fall within the expected band for a semantically parallel item (o200k_base ≈1.4–2.0×, cl100k_base ≈2.5–4.5×), confirming the translation is faithful rather than a paraphrase of different length.

*Note:* as documented in the lab, this new item is counted by Part 0 and Part 1 but cannot appear in Part 3's cost tables, since `part2_measure.py` hardcodes only `system_prompt` and `complaint` for the priced request.

### Task 2 — Locate the Kazakh premium

Two similar-length Kazakh sentences were written outside the main `CORPUS` structure (since this task needs Kazakh-only content, not three parallel languages) and measured with a small standalone script rather than the two main lab scripts, since `part0_tokenizers.py`/`part1_offline.py` iterate over `CORPUS` assuming all three languages are present.

| | chars | bytes | bytes/char | o200k tokens | cl100k tokens |
|---|---|---|---|---|---|
| Shared letters only | 45 | 82 | 1.82 | 16 | 32 |
| Dense in ә ғ қ ң ө ұ ү һ і | 61 | 112 | 1.84 | 22 | 53 |

**Finding:** bytes/char is nearly identical (1.82 vs. 1.84) — expected, since both are Cyrillic at 2 bytes/letter regardless of which specific letters appear. But normalizing token count by character length shows `cl100k_base` is far more expensive per character for the Kazakh-specific-letter sentence (0.869 tokens/char vs. 0.711), while `o200k_base` shows almost no difference (0.361 vs. 0.356). This confirms the premium lives in the tokenizer's merge table, not in the alphabet or byte count.

### Task 3 — Prose vs. JSON

Re-expressed COMPLAINT as a JSON object (`COMPLAINT_JSON`) in all three languages, preserving the full prose content inside JSON string values (an initial draft that paraphrased/shortened the content was discarded, since it produced a misleadingly *lower* token count than the prose version — exactly the "division artifact" trap the lab warns about).

**Predicted direction (before finalizing the corrected version):** JSON would cost more tokens in every language due to punctuation and field-name overhead.

**Measured (o200k_base), absolute token increase over prose:**

| | EN | RU | KK |
|---|---|---|---|
| Prose tokens | 59 | 80 | 118 |
| JSON tokens | 81 | 109 | 152 |
| Absolute increase | +22 | +29 | +34 |
| Relative increase | +37% | +36% | +29% |

**Finding:** JSON costs more in every language, confirming the predicted direction. However, the relative increase does not show the pattern the lab describes for its own reference corpus (where EN's smaller base inflates its percentage most) — here KK shows the smallest percentage increase despite Kazakh field names carrying real linguistic content rather than staying ASCII. This is itself an instance of the lab's stated trap: field names translated into Kazakh add token overhead that is not language-neutral, so the "roughly constant absolute overhead across languages" assumption only holds when field names stay in ASCII/English regardless of the values' language.

---

*Prices sourced from `prices.py`, checked 2026-09-12. Token counts from `part0_tokenizers.py` (tiktoken o200k_base / cl100k_base) and `part3_cost.py` (claude-opus-5, `measurements.example.json` reference run).*
