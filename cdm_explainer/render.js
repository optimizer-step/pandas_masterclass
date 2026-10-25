// Frame-exact capture of explainer.html → MP4 (or a few PNG stills for review).
//   node render.js                 full video  -> out/cdm_explainer.mp4
//   node render.js --stills 3,12   PNG stills  -> build/still_<t>.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const BUILD = path.join(HERE, 'build');
const OUT = path.join(HERE, 'out', 'cdm_explainer.mp4');

(async () => {
  const tl = JSON.parse(fs.readFileSync(path.join(BUILD, 'timeline.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(HERE, 'explainer.html') + '?capture');
  // pass the logo as a data URL: a file:// image would taint the canvas and block capture
  const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(HERE, 'assets', 'optimizer_step_logo.png')).toString('base64');
  await page.evaluate(([t, l]) => window.init(t, l), [tl, logo]);
  const grab = async t => {
    const url = await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.94); }, t);
    return Buffer.from(url.split(',')[1], 'base64');
  };

  // Text-free seed frames (one per section) for Higgsfield image-to-video.
  if (process.argv.includes('--plates')) {
    await page.evaluate(() => { window.PLATE = true; });
    for (const s of tl.scenes) {
      fs.writeFileSync(path.join(BUILD, `plate_${s.id}.jpg`), await grab((s.t0 + s.t1) / 2));
    }
    await browser.close();
    return;
  }

  const si = process.argv.indexOf('--stills');
  if (si > 0) {
    for (const t of process.argv[si + 1].split(',').map(Number)) {
      fs.writeFileSync(path.join(BUILD, `still_${t}.jpg`), await grab(t));
    }
    await browser.close();
    return;
  }

  const fps = tl.fps, n = Math.ceil(tl.duration * fps);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', path.join(BUILD, 'mix.wav'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const buf = await grab(i / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote', OUT);
})();
