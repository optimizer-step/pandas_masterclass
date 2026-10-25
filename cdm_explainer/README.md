# LLM → Jev → CDM: motion-graphics explainer (v2)

A 46-second, 9:16 (1080×1920, 30 fps) faceless explainer. It uses motion graphics, a natural AI voiceover,
captions and a sound design built to match the picture.

**Video:** [`out/cdm_explainer.mp4`](out/cdm_explainer.mp4)
**With Higgsfield B-roll** (once an API key is set): `out/cdm_explainer_higgsfield.mp4`

## The idea, in one continuous shot

A single 3D point cloud, standing in for "the model", morphs to carry each idea:

| Time | Section | The point cloud becomes | On screen |
|---|---|---|---|
| 0:00 | 01 · LLM | a rotating sphere that pulses on every forward pass | the answer is typed out token by token, `PASS 28`, then "28 tokens billed, 1 word needed" |
| 0:12 | 02 · Jev | one scan line passes through it, then it collapses into probability bars | situation + options → APPROVE 0.82 / ESCALATE 0.15 / REJECT 0.03 |
| 0:21 | 03 · CDM | the outline of a schema card | free-form words (“Sure!”, “I think”) get struck out; only schema-legal values snap into the slots; Classify / Extract / Summarize; then a ring around **200×** |
| 0:36 | 04 · The catch | the card again, with the wrong slot turning red | FORMAT ✓, ANSWER ✗ → "Valid ≠ correct." |
| 0:40 | Finale | a tri-colour sphere | LLMs write. Jev decides. CDMs structure. |

## Facts used (October 2026)

- **Jev** (TypeSafe AI, Sep 2026) is a "System 1" decision model. It takes a situation and the allowed
  options, and in one non-autoregressive pass returns a probability for each. It does not write text.
- **CDMs** (ScaleDown, 13 Oct 2026) are Constrained Decoding Models: Classify, Extract and Summarize. Output
  is locked to a schema. Pricing is $0.05 per 1M input tokens with free output. ScaleDown claims "200×
  faster" than frontier models on these narrow tasks.
- **Caveat:** a schema guarantees valid format, not correct content, and the speed and cost figures are the
  vendors' own.

## Build

```bash
# voice (Kokoro TTS) + music + sound design + timeline
pip install kokoro-onnx soundfile numpy
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python build_audio.py kokoro-v1.0.onnx voices-v1.0.bin

# graphics (Playwright + Chromium + ffmpeg)
node render.js                       # -> out/cdm_explainer.mp4
node render.js --stills 5,15,30      # review frames in build/
```

### Higgsfield B-roll

```bash
pip install higgsfield-client
export HF_KEY="<api-key-id>:<api-key-secret>"    # from console.higgsfield.ai
node render.js --plates              # text-free 9:16 seed frames, one per section
python higgsfield_broll.py           # Kling 2.5 Turbo image-to-video -> broll/<section>.mp4
python compose.py                    # screen-blends the B-roll under the graphics
```

Higgsfield's text-to-video endpoints have no aspect-ratio setting, so each clip is made with
**image-to-video** from a 9:16 frame of the animation itself. That keeps the format vertical and the look
consistent. Set `HF_VIDEO_MODEL` to switch models, for example `minimax/hailuo-2.3/standard/image-to-video`.
