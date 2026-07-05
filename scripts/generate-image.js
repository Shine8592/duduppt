#!/usr/bin/env node
/**
 * duduppt — generate-image.js
 * Generate PPT-ready images via Agnes AI API.
 *
 * Usage:
 *   export AGNES_API_KEY="sk-..."
 *   node scripts/generate-image.js --prompt "abstract tech blue" --style bg --out ./output.png
 *
 * Options:
 *   --prompt    Required. Image description.
 *   --style     "bg" (16:9 background), "hero" (4:3 hero image), "icon" (1:1 icon)
 *   --size      Custom size, e.g. "1280x720". Overrides --style.
 *   --out       Output path (default: ./duduppt-image-{timestamp}.png)
 *   --seed      Optional seed for reproducible results
 *   --model     Model (default: agnes-image-2.1-flash)
 */

const STYLES = {
  bg:   { size: '1280x720',  desc: '16:9 full-slide background' },
  hero: { size: '1024x768',  desc: '4:3 hero/feature image' },
  icon: { size: '512x512',   desc: '1:1 square icon/illustration' },
};

async function main() {
  const args = parseArgs();
  const prompt = args.prompt || args._[0];
  if (!prompt) { console.error('❌ Usage: --prompt "description"'); process.exit(1); }

  const style = STYLES[args.style] || STYLES.bg;
  const sizeStr = args.size || style.size;
  const outPath = args.out || `./duduppt-image-${Date.now()}.png`;
  const model = args.model || 'agnes-image-2.1-flash';

  const apiKey = process.env.AGNES_API_KEY;
  if (!apiKey) { console.error('❌ Set AGNES_API_KEY env var'); process.exit(1); }

  // Build a richer prompt for PPT use
  const fullPrompt = args.style === 'bg'
    ? `${prompt}, presentation background, clean composition, suitable for text overlay, professional, minimalist, high quality, 16:9`
    : `${prompt}, professional quality, clean, suitable for business presentation`;

  console.log(`🎨 Generating: "${prompt}"`);
  console.log(`   Style: ${args.style || 'bg'} (${style.desc})`);
  console.log(`   Size: ${sizeStr}`);
  console.log(`   Model: ${model}`);

  const payload = {
    model,
    prompt: fullPrompt,
    n: 1,
    size: sizeStr,
  };
  if (args.seed) payload.seed = parseInt(args.seed);

  const resp = await fetch('https://apihub.agnes-ai.com/v1/images/generations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const err = await resp.text();
    console.error(`❌ API error (${resp.status}): ${err}`);
    process.exit(1);
  }

  const data = await resp.json();
  const imgUrl = data.data?.[0]?.url;
  if (!imgUrl) {
    console.error('❌ No image URL in response');
    console.error(JSON.stringify(data, null, 2));
    process.exit(1);
  }

  // Download
  const imgResp = await fetch(imgUrl);
  const buffer = Buffer.from(await imgResp.arrayBuffer());
  require('fs').writeFileSync(outPath, buffer);

  console.log(`✅ Saved: ${outPath} (${(buffer.length / 1024).toFixed(0)} KB)`);
  console.log(`   URL: ${imgUrl}`);
}

function parseArgs() {
  const args = { _: [] };
  const raw = process.argv.slice(2);
  for (let i = 0; i < raw.length; i++) {
    if (raw[i].startsWith('--')) {
      const key = raw[i].slice(2);
      if (raw[i + 1] && !raw[i + 1].startsWith('--')) {
        args[key] = raw[i + 1];
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(raw[i]);
    }
  }
  return args;
}

main().catch(e => { console.error('❌', e); process.exit(1); });
