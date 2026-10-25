# Higgsfield prompt pack: LLM → Jev → CDM

Use these prompts to generate **faceless, 9:16 B-roll** in Higgsfield, one clip per scene, then layer
`out/cdm_explainer.mp4` on top. The rendered explainer already has every label, number, chart and caption
in sharp vector type. AI video models still garble on-screen text, so keep the Higgsfield clips **text-free**
and let them carry mood, depth and camera motion.

**Compositing tip:** the explainer uses a near-black background. In CapCut, Premiere or DaVinci Resolve, put
the Higgsfield clip on the lower track, put `cdm_explainer.mp4` above it, and set the top layer's blend mode
to **Screen** (or *Lighten*). The B-roll then shows through the dark areas and the graphics stay crisp.
Drop the B-roll opacity to about 40–60% so captions stay readable.

**Global settings for every clip**
- Aspect ratio: **9:16**, 1080×1920 (or the highest available)
- Duration: the scene length below (generate 5–10 s clips and loop or extend as needed)
- Add to every prompt: `no people, no faces, no hands, no text, no letters, no logos, no watermark`
- Look: dark navy-black base `#06070e`, soft volumetric glow, shallow depth of field, clean sci-fi UI aesthetic
- Accent colour per chapter: LLM = amber `#FFB547`, Jev = cyan `#34E4D7`, CDM = violet `#A88BFF`

Camera-motion names differ between Higgsfield's models and presets, so pick the closest preset to the
suggestion given for each scene.

---

### 1 · Hook (0:00–0:08): "First LLMs. Then Jev. Now CDMs."
> Three glowing light pillars rise one after another out of a dark reflective floor: first amber, then cyan,
> then violet. Volumetric fog, particles drifting upward, cinematic, ultra clean, abstract technology mood.
> No people, no faces, no text.

Camera: slow **dolly in** that ends on a fast **crash zoom** at the third pillar.

### 2 · LLM (0:08–0:22): "It predicts one token, feeds it back in…"
> An endless conveyor of small glowing amber cubes, each emerging one at a time from a large dark neural
> machine. Every cube travels along a looping track back into the machine's input, which pulses each time.
> The loop speeds up. Dark industrial sci-fi, amber rim light, smoke. No people, no text.

Camera: slow **orbit** around the loop, slight handheld drift.

### 3 · Insight (0:22–0:30): "Most agent work isn't writing. It's deciding."
> A dark flowing data river splits into four branching glowing cyan channels at a crossroads, each channel
> lighting up in sequence. Top-down abstract network, minimal, cinematic depth. No people, no text.

Camera: **overhead / top-down** shot, slow push in, then a gentle tilt forward.

### 4 · Jev (0:30–0:49): "One pass → a decision"
> A single bright cyan beam of light shoots through a crystalline prism in one clean flash. The prism splits
> it into four rays of very different brightness, and one ray is far brighter than the others. Then a
> neon wireframe runner track rushes toward camera with obstacles, and a glowing cyan cube jumps over a low
> barrier. Synthwave grid, motion blur, high speed. No people, no text.

Camera: **FPV / drone forward** rush along the track (for the second half), with a **bullet-time** pause at
the jump.

### 5 · CDM (0:49–1:26): "Output locked to a schema"
> Hundreds of floating violet glass tiles drift in darkness. Most of them dim and shatter into dust, while a
> few glowing tiles snap precisely into the slots of a clean geometric grid frame, like a form being filled
> in. Then a tall stack of luminous pages compresses into a single thin glowing card. Precise, satisfying,
> minimal, violet volumetric light. No people, no text.

Camera: **dolly in** on the grid, then a **super dolly out** as the pages compress.

### 6 · Compare (1:26–1:31): "LLMs write. Jev decides. CDMs fill in the form."
> Three abstract glowing objects on dark plinths, left to right: an amber flowing ribbon of light (writing),
> a cyan concentric target ring (deciding), a violet grid tablet with slots (structure). Museum spotlighting,
> reflections, slow rotation. No people, no text.

Camera: lateral **truck right** past the three plinths.

### 7 · Caveat (1:31–1:43): "A perfect format isn't a correct answer"
> A flawless glowing glass box that looks perfect from the front. As the camera circles it, it shows a
> hairline red crack inside. Then a central amber orb with four smaller cyan and violet orbs orbiting it,
> linked by pulsing light threads. Moody red and amber accent light. No people, no text.

Camera: **orbit 180°** around the box, then a smooth **crane up** to reveal the orbiting system.

### 8 · Outro (1:43–1:49): "Write. Decide. Structure."
> Amber, cyan and violet light streams braid together into one bright beam that fades into a calm starfield.
> Elegant, cinematic ending. No people, no text.

Camera: slow **pull back / dolly out** into darkness.

---

## If you'd rather have Higgsfield generate the whole thing

Paste the narration from `narration.json` (the `show` lines) as the script, and use the scene prompts above
as per-shot prompts. Expect to re-type all labels and numbers in an editor afterwards, because generated
text in AI video is rarely legible or accurate. The rendered `cdm_explainer.mp4` already covers this.
