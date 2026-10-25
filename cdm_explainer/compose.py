"""Blend Higgsfield B-roll underneath the rendered graphics.

Each broll/<scene>.mp4 is retimed to its section's length, darkened and laid
under out/cdm_explainer.mp4 with a screen blend, so the footage glows through
the dark background while type and data stay crisp.
    python compose.py  ->  out/cdm_explainer_higgsfield.mp4
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def main():
    tl = json.load(open(os.path.join(HERE, "build", "timeline.json")))
    graphics = os.path.join(HERE, "out", "cdm_explainer.mp4")
    out = os.path.join(HERE, "out", "cdm_explainer_higgsfield.mp4")
    inputs, chains = ["-i", graphics], []
    for k, s in enumerate(tl["scenes"], start=1):
        clip = os.path.join(HERE, "broll", f"{s['id']}.mp4")
        need = s["t1"] - s["t0"]
        inputs += ["-i", clip]
        speed = need / duration(clip)
        chains.append(
            f"[{k}]setpts={speed:.4f}*PTS,fps=30,scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,trim=duration={need:.3f},setpts=PTS-STARTPTS,"
            f"eq=brightness=-0.06:saturation=0.85,lutrgb=r=val*0.5:g=val*0.5:b=val*0.5,format=yuv420p[b{k}]")
    n = len(tl["scenes"])
    graph = ";".join(chains) + ";" + "".join(f"[b{k}]" for k in range(1, n + 1)) + \
        f"concat=n={n}:v=1:a=0[bg];[0:v]format=yuv420p[fg];[fg][bg]blend=all_mode=screen,format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "copy", "-movflags", "+faststart", out],
                   check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
