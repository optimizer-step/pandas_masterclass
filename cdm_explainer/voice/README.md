# Your voice takes

Record **one file per line** and save it here, named exactly as below with any extension
(`.m4a` from a phone voice memo is fine; `.wav` is best). For example: `voice/llm_1.m4a`.

| File | Line |
|---|---|
| `llm_1` | An LLM answers by writing, one token at a time. |
| `llm_2` | Every token is another full pass through the model. |
| `llm_3` | Ask if an email is spam, and you pay for a paragraph just to get one word. |
| `jev_1` | Jev, from TypeSafe AI, doesn't write. It decides. |
| `jev_2` | Give it the situation and the options. |
| `jev_3` | In one pass, it returns a probability for each. |
| `cdm_1` | CDMs, Constrained Decoding Models from ScaleDown, take it further. |
| `cdm_2` | The output is locked to a schema, so it always comes back in the right shape. |
| `cdm_3` | Classify. Extract. Summarize. |
| `cdm_4` | ScaleDown claims up to 200× faster than frontier models. |
| `end_1` | Just remember: a valid format isn't a correct answer. |
| `end_2` | LLMs write. Jev decides. CDMs structure. |
| `outro_1` | Follow Optimizer Step for more AI, decoded. |

Tips:
- Use a quiet, soft-furnished room (a closet full of clothes is great). Keep the phone or mic about a hand's width from your mouth, slightly off to the side.
- Leave about a second of silence before and after each line. Silence is trimmed automatically.
- Say it the way you'd explain it to a friend, with energy. Do 2–3 takes and keep the best.
- Missing lines fall back to the AI voice, so you can test with just one or two files.

Then run `python build_audio.py ...` and `node render.js`. The animation re-times itself to your takes.
