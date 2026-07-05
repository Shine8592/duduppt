#!/usr/bin/env python3
"""
duduppt — extract-palette.py
Extract dominant colors from a reference image and generate a PPT color palette.

Usage:
  python3 scripts/extract-palette.py --input brand-logo.png --colors 5
  python3 scripts/extract-palette.py --input photo.jpg --format hex

Output:
  - Color palette (hex codes)
  - Color names for CSS/PPT reference
  - Suggested PPT style mapping (background, text, accent, etc.)
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Requires Pillow: pip install Pillow")
    sys.exit(1)


def extract_colors(image_path: Path, num_colors: int = 5) -> list[tuple[int, int, int]]:
    """Extract dominant colors using simple quantization."""
    img = Image.open(image_path).convert("RGB")
    # Resize for speed
    img = img.resize((150, 150))
    pixels = list(img.getdata())

    # Simple k-means-like approach: bucket by rounded values
    buckets: dict[tuple[int, int, int], int] = {}
    for r, g, b in pixels:
        # Round to nearest 16 for bucketing
        key = ((r // 16) * 16, (g // 16) * 16, (b // 16) * 16)
        buckets[key] = buckets.get(key, 0) + 1

    # Sort by frequency, return top N
    sorted_colors = sorted(buckets.items(), key=lambda x: -x[1])
    return [color for color, _ in sorted_colors[:num_colors]]


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def luminance(r: int, g: int, b: int) -> float:
    """Relative luminance for WCAG contrast."""
    def linearize(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def suggest_style_palette(colors: list[tuple[int, int, int]]) -> dict:
    """Map extracted colors to PPT style roles."""
    if not colors:
        return {}

    # Sort by luminance
    sorted_by_lum = sorted(colors, key=lambda c: luminance(*c))

    darkest = sorted_by_lum[0]
    lightest = sorted_by_lum[-1]
    # Pick the most saturated color as accent
    def saturation(c):
        r, g, b = [x / 255.0 for x in c]
        return max(r, g, b) - min(r, g, b)
    accent = max(colors, key=saturation)
    # Pick mid-tone as secondary
    mid = sorted_by_lum[len(sorted_by_lum) // 2] if len(sorted_by_lum) > 2 else colors[1]

    bg_lum = luminance(*lightest)
    use_light_bg = bg_lum > 0.5

    return {
        "background": rgb_to_hex(*lightest) if use_light_bg else rgb_to_hex(*darkest),
        "title_text": rgb_to_hex(*darkest) if use_light_bg else rgb_to_hex(*lightest),
        "body_text": rgb_to_hex(*mid) if use_light_bg else rgb_to_hex(*mid),
        "accent": rgb_to_hex(*accent),
        "secondary_accent": rgb_to_hex(*mid),
        "style_type": "light_background" if use_light_bg else "dark_background",
    }


def main():
    parser = argparse.ArgumentParser(description="Extract PPT color palette from an image")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--colors", "-n", type=int, default=5, help="Number of colors to extract")
    parser.add_argument("--format", choices=["hex", "json", "css"], default="hex",
                        help="Output format")
    args = parser.parse_args()

    img_path = Path(args.input)
    if not img_path.exists():
        print(f"❌ File not found: {img_path}")
        sys.exit(1)

    colors = extract_colors(img_path, args.colors)
    style = suggest_style_palette(colors)

    if args.format == "json":
        print(json.dumps({
            "source": str(img_path),
            "extracted_colors": [rgb_to_hex(*c) for c in colors],
            "style_palette": style,
        }, indent=2))
    elif args.format == "css":
        print("/* duduppt extracted palette */")
        print(f":root {{")
        for role, hex_val in style.items():
            if role == "style_type": continue
            print(f"  --ppt-{role}: {hex_val};")
        print(f"}}")
    else:
        print(f"\n🎨 Palette from: {img_path.name}\n")
        print("Extracted colors:")
        for c in colors:
            hex_c = rgb_to_hex(*c)
            # Simple ANSI color block
            block = f"\033[48;2;{c[0]};{c[1]};{c[2]}m    \033[0m"
            print(f"  {block}  {hex_c}  RGB({c[0]},{c[1]},{c[2]})")

        print("\nSuggested PPT style palette:")
        print(f"  Background:      {style['background']}")
        print(f"  Title text:      {style['title_text']}")
        print(f"  Body text:       {style['body_text']}")
        print(f"  Accent:          {style['accent']}")
        print(f"  Secondary:       {style['secondary_accent']}")
        print(f"  Type:            {style['style_type']}")


if __name__ == "__main__":
    main()
