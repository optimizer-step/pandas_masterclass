"""Generate cinematic 9:16 B-roll for each section with the Higgsfield API.

Usage (needs HF_KEY="<api-key-id>:<api-key-secret>" in the environment):
    node render.js --plates                       # text-free seed frames -> build/plate_<id>.jpg
    python higgsfield_broll.py                    # -> broll/<id>.mp4
    python compose.py                             # -> out/cdm_explainer_higgsfield.mp4

Text-to-video on Higgsfield has no aspect-ratio option, so each clip is made
with image-to-video from a 9:16 seed frame of our own animation. That keeps
the vertical format and the visual language consistent with the graphics.
"""
import os
import sys
import urllib.request

import higgsfield_client

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("HF_VIDEO_MODEL", "kling-video/v2.5-turbo/pro/image-to-video")

NEG = "text, letters, words, numbers, logo, watermark, people, faces, hands, low quality, blurry, flicker"
PROMPTS = {
    "llm": "Slow cinematic push-in on a glowing orange particle sphere floating in a dark void. Waves of warm light "
           "ripple across its surface again and again, tiny embers stream out of it one by one. Volumetric haze, "
           "shallow depth of field, premium tech commercial look, smooth camera motion.",
    "jev": "A single clean sweep of teal light passes through the scene once, then the particles settle into calm, "
           "precise horizontal streaks. Dark studio, soft volumetric fog, subtle parallax, elegant and minimal, "
           "slow dolly forward.",
    "cdm": "Violet light particles drift in darkness and snap precisely into a glowing geometric grid frame, like "
           "pieces locking into place. Crisp, satisfying, minimal, soft bloom, slow orbiting camera, premium "
           "motion design aesthetic.",
    "end": "Orange, teal and violet particles orbit and braid together into one luminous sphere, slowly rotating, "
           "then the camera gently pulls back into a calm dark starfield. Cinematic, elegant ending, soft glow.",
}


def find_video_url(result):
    if isinstance(result, dict):
        v = result.get("video")
        if isinstance(v, dict) and v.get("url"):
            return v["url"]
        for x in result.values():
            u = find_video_url(x)
            if u:
                return u
    if isinstance(result, list):
        for x in result:
            u = find_video_url(x)
            if u:
                return u
    if isinstance(result, str) and result.split("?")[0].endswith(".mp4"):
        return result
    return None


def main():
    if not (os.environ.get("HF_KEY") or (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET"))):
        sys.exit("HF_KEY is not set. Add your Higgsfield API key to the environment first.")
    os.makedirs(os.path.join(HERE, "broll"), exist_ok=True)
    only = sys.argv[1:] or list(PROMPTS)
    for sid in only:
        out = os.path.join(HERE, "broll", f"{sid}.mp4")
        if os.path.exists(out):
            print(f"{sid}: exists, skipping")
            continue
        plate = os.path.join(HERE, "build", f"plate_{sid}.jpg")
        image_url = higgsfield_client.upload_file(plate)
        print(f"{sid}: submitted to {MODEL}")
        result = higgsfield_client.subscribe(MODEL, arguments={
            "prompt": PROMPTS[sid], "image_url": image_url, "duration": 10, "negative_prompt": NEG,
        })
        url = find_video_url(result)
        if not url:
            sys.exit(f"{sid}: no video in result: {result}")
        urllib.request.urlretrieve(url, out)
        print(f"{sid}: saved {out}")


if __name__ == "__main__":
    main()
