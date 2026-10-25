"""Voice (Kokoro TTS) + music bed + sound design -> build/timeline.json, build/mix.wav

Usage: python build_audio.py <kokoro-v1.0.onnx> <voices-v1.0.bin>

Each sentence is synthesised on its own so the animation can key off exact
sentence starts. Word timings inside a sentence are estimated from character
length. Animation beats that also make a sound (token ticks, the Jev pass,
the schema lock, ...) are computed here once and written into the timeline,
so picture and sound share one source of truth.
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 44100
rng = np.random.default_rng(7)


def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 200): idx[-1] + 1200] if len(idx) else x


def resample(x, sr_in):
    n = int(len(x) * SR / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def word_times(show, t0, t1):
    words = show.split()
    weights = [len(w) + (4 if w[-1] in ",.:" else 2) for w in words]
    total, t, out = sum(weights), t0, []
    for w, k in zip(words, weights):
        d = (t1 - t0) * k / total
        out.append({"w": w, "t0": round(t, 3), "t1": round(t + d, 3)})
        t += d
    return out


def word_at(sent, pattern):
    for w in sent["words"]:
        if pattern.lower() in w["w"].lower():
            return w["t0"]
    return sent["t0"]


# ---------------------------------------------------------------- synth bits
def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def onepole_lp(x, cut):
    """One-pole low-pass with a per-sample cutoff (Hz) array or scalar."""
    cut = np.broadcast_to(np.asarray(cut, dtype=np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(d=0.9):
    n = int(d * SR)
    k = np.linspace(0, 1, n)
    cut = 300 + 5000 * np.sin(np.pi * k) ** 2
    y = onepole_lp(rng.standard_normal(n), cut)
    return y * np.sin(np.pi * k) ** 1.5 * 0.9


def tick(f=2400, d=0.03, a=0.5):
    n = int(d * SR)
    t = np.arange(n) / SR
    return a * np.sin(2 * np.pi * f * t) * env_exp(n, 0.006)


def impact(d=1.6, a=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 38 + 40 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.45)
    hit = onepole_lp(rng.standard_normal(n), 1800) * env_exp(n, 0.04) * 0.8
    return a * (body + hit)


def riser(d=0.8):
    n = int(d * SR)
    k = np.linspace(0, 1, n)
    y = onepole_lp(rng.standard_normal(n), 400 + 7000 * k ** 2) * k ** 2
    t = np.arange(n) / SR
    y += 0.25 * np.sin(2 * np.pi * np.cumsum(300 + 900 * k ** 2) / SR) * k ** 2
    return y * 0.6


def pad(total):
    """Slow minor-key pad (Am9 – Fmaj7 – C6 – Em7), detuned sines, soft sub."""
    n = int(total * SR)
    t = np.arange(n) / SR
    chords = [[110.0, 164.8, 261.6, 329.6, 493.9], [87.3, 174.6, 261.6, 329.6, 440.0],
              [130.8, 196.0, 261.6, 329.6, 392.0], [82.4, 164.8, 246.9, 293.7, 392.0]]
    seg = 6.0
    out = np.zeros(n)
    for ci in range(int(total // seg) + 2):
        notes = chords[ci % 4]
        s0 = ci * seg - 1.5
        i0, i1 = max(0, int(s0 * SR)), min(n, int((s0 + seg + 3.0) * SR))
        if i0 >= i1:
            continue
        tt = t[i0:i1] - s0
        e = np.clip(tt / 1.8, 0, 1) * np.clip((seg + 3.0 - tt) / 2.2, 0, 1)
        for j, f in enumerate(notes):
            for det in (-0.0015, 0.0, 0.0017):
                out[i0:i1] += e * np.sin(2 * np.pi * f * (1 + det) * tt + j) * (0.5 if j == 0 else 0.22)
        out[i0:i1] += e * 0.35 * np.sin(2 * np.pi * notes[0] / 2 * tt)
    return out * 0.05


def pulse(total, start, end, bpm=96):
    """Quiet 8th-note ticks + soft sub kick: keeps momentum without being music."""
    n = int(total * SR)
    out = np.zeros(n)
    beat = 60 / bpm
    k = 0
    while start + k * beat / 2 < end:
        t0 = start + k * beat / 2
        i = int(t0 * SR)
        h = onepole_lp(rng.standard_normal(1400), 9000)
        h = (h - onepole_lp(h, 4000)) * env_exp(1400, 0.008) * (0.05 if k % 2 else 0.03)
        out[i:i + len(h)] += h[: max(0, n - i)]
        if k % 4 == 0:
            m = int(0.5 * SR)
            tt = np.arange(m) / SR
            kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-tt * 30)) / SR) * env_exp(m, 0.18) * 0.16
            out[i:i + m] += kick[: max(0, n - i)]
        k += 1
    return out


def bell(f=880, d=2.4, a=0.5):
    """Soft glassy chime: inharmonic partials with staggered decays."""
    n = int(d * SR)
    t = np.arange(n) / SR
    y = sum(w * np.sin(2 * np.pi * f * r * t) * env_exp(n, tau)
            for r, w, tau in ((1, 1, .9), (2.0, .45, .5), (3.01, .25, .3), (4.2, .12, .18)))
    return a * y * np.clip(t / .004, 0, 1)


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i < 0:
        clip, i = clip[-i:], 0
    j = min(len(buf), i + len(clip))
    if j > i:
        buf[i:j] += clip[: j - i] * gain


def main():
    model, voices = sys.argv[1], sys.argv[2]
    os.makedirs(BUILD, exist_ok=True)
    cfg = json.load(open(os.path.join(HERE, "narration.json")))
    tts = Kokoro(model, voices)

    t, clips, scenes = 0.45, [], []
    for si, sc in enumerate(cfg["scenes"]):
        s_start = t if si else 0.0
        sents = []
        for s in sc["sentences"]:
            t += s.get("pause_before", 0)
            # espeak spells the plural "Ms" in "L L Ms" / "C D Ms" as "em-ess"; say "ems".
            ph = tts.tokenizer.phonemize(s["say"], "en-us").replace("ˌɛmˈɛs", "ˈɛmz")
            audio, sr = tts.create(ph, voice=cfg["voice"], speed=cfg["speed"], lang="en-us", is_phonemes=True)
            a = resample(trim(audio), sr)
            dur = len(a) / SR
            clips.append((t, a))
            sents.append({"show": s["show"], "t0": round(t, 3), "t1": round(t + dur, 3),
                          "words": word_times(s["show"], t, t + dur)})
            t += dur + cfg["sentence_gap"] + s.get("pause_after", 0)
        t += cfg["scene_tail"]
        scenes.append({"id": sc["id"], "t0": round(s_start, 3), "t1": round(t, 3), "sentences": sents})
    total = round(t + 0.3, 3)
    scenes[-1]["t1"] = total
    S = {s["id"]: s for s in scenes}

    # ---- shared animation/sound beats
    llm = S["llm"]["sentences"]
    n_tok = 28
    g0, g1 = word_at(llm[0], "token"), llm[2]["t0"] + 1.0
    tokens = [round(g0 + (g1 - g0) * ((i + 1) / n_tok) ** 0.7, 3) for i in range(n_tok)]
    jev, cdm, end = S["jev"]["sentences"], S["cdm"]["sentences"], S["end"]["sentences"]
    events = {
        "tokens": tokens,
        "jev_pass": round(word_at(jev[2], "pass"), 3),
        "lock": round(word_at(cdm[1], "locked"), 3),
        "trio": [round(word_at(cdm[2], w), 3) for w in ("Classify", "Extract", "Summarize")],
        "claim": round(word_at(cdm[3], "200"), 3),
        "finale": [round(word_at(end[1], w), 3) for w in ("LLMs", "Jev", "CDMs")],
    }
    # End card: ring forms -> emblem reveal -> ball steps down the loss curve -> land -> wordmark -> CTA tap
    O = S["outro"]["t0"]
    steps = [round(O + 1.75 + i * 0.3, 3) for i in range(5)]
    land = steps[-1]
    events["outro"] = {"ring": round(O + .25, 3), "reveal": round(O + .95, 3), "start": round(O + 1.45, 3),
                       "steps": steps, "land": land, "word": round(land + .05, 3), "divider": round(land + .55, 3),
                       "cta": round(land + .9, 3), "shine": round(land + 1.3, 3), "tap": round(land + 2.4, 3)}
    json.dump({"duration": total, "fps": 30, "scenes": scenes, "events": events},
              open(os.path.join(BUILD, "timeline.json"), "w"), indent=1)

    # ---- voice
    n = int(total * SR)
    voice = np.zeros(n)
    for start, a in clips:
        place(voice, a, start)

    # ---- music bed, ducked under the voice
    music = pad(total) + pulse(total, 0.45, end[1]["t0"] - 0.2)
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.45 * np.clip(env / 0.05, 0, 1)
    fade = np.clip(np.arange(n) / (1.5 * SR), 0, 1) * np.clip((n - np.arange(n)) / (2.5 * SR), 0, 1)
    music *= duck * fade

    # ---- sound design
    sfx = np.zeros(n)
    place(sfx, impact(a=0.7), 0.35)
    for s in scenes[1:]:
        place(sfx, whoosh(), s["t0"] - 0.55, 0.22)
        place(sfx, impact(a=0.45), s["t0"] + 0.05)
    for i, tt in enumerate(tokens):
        place(sfx, tick(2000 + 40 * (i % 5), a=0.16), tt)
    place(sfx, riser(0.7), events["jev_pass"] - 0.7, 0.5)
    place(sfx, impact(a=0.6), events["jev_pass"])
    place(sfx, tick(1300, 0.06, 0.4), events["lock"])
    place(sfx, tick(1700, 0.06, 0.4), events["lock"] + 0.09)
    for tt in events["trio"]:
        place(sfx, tick(1500, 0.05, 0.35), tt)
    place(sfx, riser(0.9), events["claim"] - 0.9, 0.5)
    place(sfx, impact(a=0.9), events["claim"])
    for tt in events["finale"]:
        place(sfx, impact(a=0.35), tt)
    o = events["outro"]
    place(sfx, riser(0.9), o["reveal"] - 0.9, 0.45)
    place(sfx, impact(a=0.7), o["reveal"])
    place(sfx, bell(587.3, a=.35), o["reveal"])
    place(sfx, bell(880, a=.18), o["reveal"] + .02)
    place(sfx, tick(1100, .05, .3), o["start"])
    for i, tt in enumerate(o["steps"]):          # descending steps down the loss curve
        place(sfx, bell(1318.5 / (1.06 ** (i * 2)), 0.6, .16), tt)
        place(sfx, tick(1600 - 120 * i, .04, .25), tt)
    place(sfx, impact(a=1.0), o["land"])
    for f, a in ((440, .32), (659.3, .22), (880, .18), (1108.7, .12)):
        place(sfx, bell(f, 3.2, a), o["land"])
    place(sfx, bell(2637, 1.4, .08), o["shine"])
    place(sfx, tick(1900, .05, .35), o["tap"])
    place(sfx, bell(1760, 0.9, .1), o["tap"] + .03)

    mix = voice * 0.95 + music + sfx * 0.55
    st = np.stack([mix, mix], axis=1)
    sf.write(os.path.join(BUILD, "mix_raw.wav"), st.astype(np.float32), SR)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(BUILD, "mix_raw.wav"),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(SR), os.path.join(BUILD, "mix.wav")], check=True)
    print(f"duration {total:.2f}s")
    for s in scenes:
        print(s["id"], s["t0"], s["t1"], [x["t0"] for x in s["sentences"]])


if __name__ == "__main__":
    main()
