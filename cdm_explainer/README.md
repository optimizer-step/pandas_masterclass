# LLM → Jev → CDM: faceless motion-graphics explainer

A 1:49, 9:16 (1080×1920, 30 fps) explainer reel. It is all motion graphics with an AI voiceover and
karaoke captions, and it explains how **CDMs (Constrained Decoding Models)** differ from **LLMs** and **Jev**.

**Final video:** [`out/cdm_explainer.mp4`](out/cdm_explainer.mp4)
**Higgsfield B-roll prompts:** [`HIGGSFIELD_PROMPTS.md`](HIGGSFIELD_PROMPTS.md)

## Storyboard

| Time | Scene | What the graphics show |
|---|---|---|
| 0:00 | Hook | "LLMs → Jev → CDMs" slam in; "without ~~writing~~" |
| 0:08 | LLM | Prompt → neural net → tokens stream out one by one and loop back in; pass counter climbs to 53; the single useful word "spam" is circled |
| 0:22 | Insight | "Most work inside an AI agent isn't ~~writing~~. **It's deciding.**" Route → Label → Extract → Score pipeline |
| 0:30 | Jev | Situation + allowed actions → **one pass** → probability bars → `{"action":"JUMP","confidence":0.81}` → real-time runner game making decisions |
| 0:49 | CDM | Vocabulary mask (only schema-legal tokens survive) → always-valid JSON; then Classify (Σ = 1.00), Extract (spans → JSON + confidence), Summarize (1M tokens → ≤1,000); $0.05 / 1M input, $0 output; 200× / 467× claims with a bar race |
| 1:26 | Compare | LLM **writes** · Jev **decides** · CDM **fills the form** |
| 1:31 | Caveat | Valid ≠ true; the speed figures are vendor-reported; hybrid stack with the LLM in the middle and Jev/CDM around it |
| 1:43 | Outro | WRITE. DECIDE. STRUCTURE. |

## Facts used (October 2026)

- **Jev** is TypeSafe AI's "System 1" *decision model* (early access 15 Sep 2026). It takes a situation and a
  list of allowed actions and returns probabilities and confidence in a single non-autoregressive pass. It
  does not write prose. Vendor figures: about 70–500 ms per call, ~$0.042 per 1M input tokens, output free.
- **CDMs** are ScaleDown's *Constrained Decoding Models* (13 Oct 2026): **Classify**, **Extract** and
  **Summarize**. Output is constrained to a schema. Each accepts up to 1M input tokens, costs $0.05 per 1M
  input tokens, and output is free. ScaleDown claims they are "200× faster, 467× cheaper" than frontier
  models on these narrow tasks.
- **Caveats:** constrained decoding guarantees valid *format*, not correct *content*. Summarize still
  generates text. All speed and cost numbers are the vendors' own.

## Rebuild

```bash
# 1. voice + timeline + music/sfx (Piper TTS, offline neural voice)
python3 -m venv tts && tts/bin/pip install piper-tts
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json
python3 build_audio.py tts/bin/piper en_US-ryan-high.onnx

# 2. frame-exact render (Playwright + Chromium + ffmpeg)
node render.js                      # -> out/cdm_explainer.mp4
node render.js --stills 12,40,70    # quick PNG/JPG checks in build/
```

To change the narration, edit `narration.json` and rerun both steps. Every animation is keyed to sentence
and word timings, so it re-syncs automatically. To watch a live preview with audio, serve the folder
(`python3 -m http.server`) and open `explainer.html`.
