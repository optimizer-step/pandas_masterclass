"""Synthesise the narration with Piper and write timeline.json + the audio mix.

Usage: python3 build_audio.py <piper-binary> <voice.onnx>

Each sentence is rendered separately so the animation can be keyed to the
exact moment it starts. Word timings inside a sentence are estimated from
character length, which is close enough for karaoke-style captions.
"""
import json
import os
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
SR = 22050


def synth(piper, voice, text, path, length_scale):
    subprocess.run(
        [piper, "-m", voice, "-f", path, "--length_scale", str(length_scale)],
        input=text.encode(), check=True, capture_output=True,
    )
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def trim_silence(path):
    """Piper pads each clip; trim leading/trailing silence so gaps are ours."""
    out = path.replace(".wav", ".trim.wav")
    filt = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
            "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-af", filt, "-ar", str(SR), "-ac", "1", out], check=True)
    with wave.open(out) as w:
        return out, w.getnframes() / w.getframerate()


def word_times(show, t0, t1):
    words = show.split()
    weights = [len(w) + 2 for w in words]
    total = sum(weights)
    out, t = [], t0
    for w, k in zip(words, weights):
        d = (t1 - t0) * k / total
        out.append({"w": w, "t0": round(t, 3), "t1": round(t + d, 3)})
        t += d
    return out


def main():
    piper, voice = sys.argv[1], sys.argv[2]
    os.makedirs(BUILD, exist_ok=True)
    cfg = json.load(open(os.path.join(HERE, "narration.json")))
    gap, tail = cfg["sentence_gap"], cfg["scene_tail"]

    t = 0.35  # small lead-in before the first word
    clips, scenes = [], []
    for si, sc in enumerate(cfg["scenes"]):
        s_start = t if si else 0.0
        sents = []
        for i, s in enumerate(sc["sentences"]):
            raw = os.path.join(BUILD, f"{sc['id']}_{i}.wav")
            synth(piper, voice, s["say"], raw, cfg["length_scale"])
            path, dur = trim_silence(raw)
            clips.append((t, path))
            sents.append({"show": s["show"], "t0": round(t, 3), "t1": round(t + dur, 3),
                          "words": word_times(s["show"], t, t + dur)})
            t += dur + gap + s.get("pause_after", 0)
        t += tail
        scenes.append({"id": sc["id"], "t0": round(s_start, 3), "t1": round(t, 3), "sentences": sents})

    total = round(t + 0.6, 3)
    scenes[-1]["t1"] = total
    json.dump({"duration": total, "fps": 30, "scenes": scenes},
              open(os.path.join(BUILD, "timeline.json"), "w"), indent=1)

    # Voice track: place every clip at its start time.
    inputs, filters = [], []
    for k, (start, path) in enumerate(clips):
        inputs += ["-i", path]
        ms = int(start * 1000)
        filters.append(f"[{k}]adelay={ms}|{ms}[a{k}]")
    mix = "".join(f"[a{k}]" for k in range(len(clips)))
    filters.append(f"{mix}amix=inputs={len(clips)}:normalize=0,apad=whole_dur={total}[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[v]", "-ar", "44100", "-ac", "2", os.path.join(BUILD, "voice.wav")], check=True)

    # Whoosh on every scene change + a quiet ambient pad underneath.
    whooshes = [s["t0"] for s in scenes[1:]]
    w_in, w_f = [], []
    for k, st in enumerate(whooshes):
        w_in += ["-f", "lavfi", "-t", "0.7", "-i", "anoisesrc=color=pink:amplitude=0.5:sample_rate=44100"]
        ms = max(0, int((st - 0.25) * 1000))
        w_f.append(f"[{k}]bandpass=f=1400:width_type=o:w=2,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.4,"
                   f"volume=0.22,adelay={ms}|{ms},aformat=channel_layouts=stereo[w{k}]")
    n = len(whooshes)
    w_in += ["-f", "lavfi", "-t", str(total), "-i",
             "aevalsrc='0.05*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.11*t))+0.035*sin(2*PI*164.8*t)*(0.6+0.4*sin(2*PI*0.07*t+1))"
             "+0.025*sin(2*PI*220.6*t)*(0.5+0.5*sin(2*PI*0.05*t+2))':s=44100"]
    w_f.append(f"[{n}]lowpass=f=900,afade=t=in:d=2,afade=t=out:st={total-2.5}:d=2.5,aformat=channel_layouts=stereo[pad]")
    w_f.append("".join(f"[w{k}]" for k in range(n)) + f"[pad]amix=inputs={n+1}:normalize=0[sfx]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *w_in, "-filter_complex", ";".join(w_f),
                    "-map", "[sfx]", "-t", str(total), os.path.join(BUILD, "sfx.wav")], check=True)

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(BUILD, "voice.wav"),
                    "-i", os.path.join(BUILD, "sfx.wav"), "-filter_complex",
                    "[1]volume=0.9[s];[0][s]amix=inputs=2:normalize=0,alimiter=limit=0.95[m]",
                    "-map", "[m]", os.path.join(BUILD, "mix.wav")], check=True)
    print(f"duration {total:.2f}s, {len(clips)} sentences")


if __name__ == "__main__":
    main()
