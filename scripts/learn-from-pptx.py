#!/usr/bin/env python3
"""
duduppt — learn-from-pptx.py
从参考 PPTX 中学习视觉风格：配色方案、字体、布局特征。
输出可直接用于 duduppt pptxgenjs 生成的 style config。

Usage:
  python3 scripts/learn-from-pptx.py --input reference.pptx
  python3 scripts/learn-from-pptx.py --input reference.pptx --format json --out style-config.json
  python3 scripts/learn-from-pptx.py --input reference.pptx --compare  # 对比 duduppt 预设风格

Output:
  - 配色方案（主色/强调色/背景色/文字色）
  - 字体方案（标题字体/正文字体/字号范围）
  - 布局特征摘要（页数、每页形状数、图片使用比例）
  - 最接近的 duduppt 预设风格匹配
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile


# ── Namespaces ──
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}

# duduppt 8+1 预设风格（用于匹配）
DUDUPPT_STYLES = {
    "01_经典深红咨询风": {
        "bg": "F3F4EF", "accent": "8B1E1E", "text": "2D3436",
        "desc": "战略/竞品/行业研究"
    },
    "02_冷灰勃艮第红": {
        "bg": "F5F5F2", "accent": "7A1F2B", "text": "2D3436",
        "desc": "财务/投研/风险"
    },
    "03_暖象牙暗酒红": {
        "bg": "F4F1EA", "accent": "8A1538", "text": "2D3436",
        "desc": "品牌/消费品/电商"
    },
    "04_象牙白深蓝": {
        "bg": "F7F6F0", "accent": "12355B", "text": "2D3436",
        "desc": "科技/SaaS/AI"
    },
    "05_浅灰白墨绿": {
        "bg": "F2F3EF", "accent": "1F5B4D", "text": "2D3436",
        "desc": "可持续/增长"
    },
    "06_纸张米色铜棕": {
        "bg": "F4F0E8", "accent": "9A5A2E", "text": "2D3436",
        "desc": "消费/零售/奢侈品"
    },
    "07_纯净浅灰黑金": {
        "bg": "F6F6F4", "accent": "A87932", "text": "2D3436",
        "desc": "高管汇报/融资/董事会"
    },
    "08_冷白灰深紫": {
        "bg": "F4F5F6", "accent": "4B2E83", "text": "2D3436",
        "desc": "AI/技术/创新"
    },
    "09_清新高客风": {
        "bg": "F8F9F7", "accent": "5B9B8A", "text": "2D3436",
        "desc": "高客财富沙龙/传承"
    },
}


def rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex string (no #)."""
    return f"{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(h):
    """Convert hex string to RGB tuple."""
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def color_distance(c1, c2):
    """Simple Euclidean RGB distance."""
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r, g, b):
    """WCAG relative luminance."""
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


def extract_theme_colors(zf: ZipFile) -> dict:
    """提取主题配色方案 (clrScheme)。"""
    theme_files = [n for n in zf.namelist() if n.startswith('ppt/theme/') and n.endswith('.xml')]
    if not theme_files:
        return {}

    theme_xml = zf.read(theme_files[0]).decode('utf-8', 'ignore')
    root = ET.fromstring(theme_xml)

    colors = {}
    # clrScheme 下的每个子标签名 = 颜色角色，内容 = 颜色值
    for scheme in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}clrScheme'):
        for child in scheme:
            tag = child.tag.split('}')[-1]  # 去掉 namespace
            # 颜色可能在 <a:srgbClr val="..."/> 或 <a:sysClr val="..."/> 中
            srgb = child.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            sysclr = child.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}sysClr')
            if srgb is not None:
                colors[tag] = srgb.get('val').upper()
            elif sysclr is not None:
                colors[tag] = sysclr.get('lastClr', sysclr.get('val', '')).upper()
    return colors


def extract_theme_fonts(zf: ZipFile) -> dict:
    """提取主题字体方案 (fontScheme)。"""
    theme_files = [n for n in zf.namelist() if n.startswith('ppt/theme/') and n.endswith('.xml')]
    if not theme_files:
        return {}

    theme_xml = zf.read(theme_files[0]).decode('utf-8', 'ignore')
    fonts = {}

    # 匹配 majorFont (标题) 和 minorFont (正文) 的 latin typeface
    for font_type in ['majorFont', 'minorFont']:
        m = re.search(
            rf'<a:{font_type}[^>]*>.*?<a:latin[^>]*typeface="([^"]+)"',
            theme_xml, re.DOTALL
        )
        if m:
            fonts[font_type] = m.group(1)

    return fonts


def extract_used_fonts(zf: ZipFile) -> dict:
    """从所有 slide XML 中提取实际使用的字体及其频率。"""
    slides = [n for n in zf.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]
    font_counter = Counter()

    for s in slides:
        xml = zf.read(s).decode('utf-8', 'ignore')
        for m in re.finditer(r'typeface="([^"]+)"', xml):
            font_counter[m.group(1)] += 1

    # 区分标题字体和正文字体（粗略：按使用频率分）
    if not font_counter:
        return {}

    most_common = font_counter.most_common()
    # 取使用最多的字体为正文，第二多的可能为标题（如果差异大）
    body_font = most_common[0][0]
    title_font = most_common[1][0] if len(most_common) > 1 and most_common[1][1] > 2 else body_font

    return {
        "title_font": title_font,
        "body_font": body_font,
        "all_fonts": dict(font_counter.most_common(10)),
    }


def extract_fill_colors(zf: ZipFile) -> list:
    """从所有 slide 中提取形状填充色（用于推断色板）。"""
    slides = [n for n in zf.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]
    colors = []

    for s in slides:
        xml = zf.read(s).decode('utf-8', 'ignore')
        # solidFill 中的 srgbClr
        for m in re.finditer(r'<a:solidFill>.*?<a:srgbClr val="([^"]+)"', xml, re.DOTALL):
            colors.append(m.group(1).upper())
        # gradient fill 中的 stop color
        for m in re.finditer(r'<a:gsStop>.*?<a:srgbClr val="([^"]+)"', xml, re.DOTALL):
            colors.append(m.group(1).upper())

    return colors


def extract_slide_stats(zf: ZipFile) -> dict:
    """提取布局统计信息。"""
    slides = sorted(
        [n for n in zf.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
        key=lambda x: int(re.search(r'(\d+)', x).group(1))
    )

    total_shapes = 0
    total_pics = 0
    total_texts = 0
    slide_details = []

    for s in slides:
        xml = zf.read(s).decode('utf-8', 'ignore')
        shapes = len(re.findall(r'<p:sp\b', xml))  # shape
        pics = len(re.findall(r'<p:pic\b', xml))    # picture
        texts = len(re.findall(r'<a:t>', xml))      # text runs
        total_shapes += shapes
        total_pics += pics
        total_texts += texts
        slide_details.append({
            "name": s.split('/')[-1],
            "shapes": shapes,
            "pictures": pics,
            "text_runs": texts,
        })

    image_ratio = total_pics / max(total_shapes, 1)
    avg_shapes = total_shapes / max(len(slides), 1)

    return {
        "slide_count": len(slides),
        "total_shapes": total_shapes,
        "total_pictures": total_pics,
        "total_text_runs": total_texts,
        "avg_shapes_per_slide": round(avg_shapes, 1),
        "image_ratio": round(image_ratio, 3),
        "image_heavy": image_ratio > 0.3,
        "text_heavy": avg_shapes > 15,
        "slide_details": slide_details,
    }


def match_duduppt_style(theme_colors: dict) -> list:
    """将提取的配色与 duduppt 预设风格匹配，返回最接近的 top 3。"""
    if not theme_colors:
        return []

    # 从主题色中提取代表性颜色
    # 取 dk1 (深色1=文字), lt1 (浅色1=背景), accent1-6 中的第一个强调色
    bg_guess = theme_colors.get('lt1') or theme_colors.get('lt2') or 'F4F4F4'
    text_guess = theme_colors.get('dk1') or '2D3436'
    accent_guess = (
        theme_colors.get('accent1')
        or theme_colors.get('accent2')
        or theme_colors.get('accent3')
        or '8B1E1E'
    )

    ref_bg_rgb = hex_to_rgb(bg_guess)
    ref_accent_rgb = hex_to_rgb(accent_guess)

    scored = []
    for name, style in DUDUPPT_STYLES.items():
        s_bg = hex_to_rgb(style['bg'])
        s_accent = hex_to_rgb(style['accent'])
        # 加权：背景色距离权重 0.4，强调色距离权重 0.6
        score = 0.4 * color_distance(ref_bg_rgb, s_bg) + 0.6 * color_distance(ref_accent_rgb, s_accent)
        scored.append((score, name, style))

    scored.sort(key=lambda x: x[0])
    return [
        {"style": name, "score": round(s, 0), "description": style['desc'], "palette": style}
        for s, name, style in scored[:3]
    ]


def build_style_config(theme_colors: dict, fonts: dict, slide_stats: dict) -> dict:
    """构建可直接用于 pptxgenjs 的 style config。"""
    config = {}

    # 调色板
    if theme_colors:
        config["palette"] = {
            "bg": theme_colors.get('lt1', 'F4F4F4'),
            "card": theme_colors.get('lt2', 'FFFFFF'),
            "accent": (
                theme_colors.get('accent1')
                or theme_colors.get('accent2')
                or theme_colors.get('accent3')
                or '5B9B8A'
            ),
            "accentDark": theme_colors.get('dk2', '3D7A68'),
            "gold": theme_colors.get('accent4', 'C4A265'),
            "text": theme_colors.get('dk1', '2D3436'),
            "muted": theme_colors.get('dk2', '8B9B90'),
            "divider": theme_colors.get('lt2', 'E2E8E4'),
            "light": theme_colors.get('lt2', 'E8F0EC'),
        }

    # 字体
    if fonts:
        config["fonts"] = {
            "title": fonts.get('majorFont', 'Arial'),
            "body": fonts.get('minorFont', 'Arial'),
            "chinese_fallback": "WenQuanYi Micro Hei",
        }

    # 布局参考
    if slide_stats:
        config["layout"] = {
            "avg_shapes_per_slide": slide_stats.get("avg_shapes_per_slide", 8),
            "image_density": "high" if slide_stats.get("image_heavy") else "low",
            "style_type": "image_heavy" if slide_stats.get("image_heavy") else "text_focused",
        }

    return config


def main():
    parser = argparse.ArgumentParser(
        description="从参考 PPTX 中学习视觉风格，输出 duduppt style config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/learn-from-pptx.py --input brand-deck.pptx
  python3 scripts/learn-from-pptx.py --input brand-deck.pptx --format json --out style.json
  python3 scripts/learn-from-pptx.py --input brand-deck.pptx --compare
        """
    )
    parser.add_argument("--input", "-i", required=True, help="参考 PPTX 文件路径")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="输出格式")
    parser.add_argument("--out", "-o", help="输出文件路径（仅 json 格式）")
    parser.add_argument("--compare", "-c", action="store_true",
                        help="与 duduppt 预设风格对比匹配")
    args = parser.parse_args()

    pptx_path = Path(args.input)
    if not pptx_path.exists():
        print(f"❌ 文件不存在: {pptx_path}")
        sys.exit(1)

    if pptx_path.suffix.lower() != '.pptx':
        print(f"❌ 不是 PPTX 文件: {pptx_path}")
        sys.exit(1)

    try:
        zf = ZipFile(pptx_path)
    except Exception as e:
        print(f"❌ 无法打开 PPTX: {e}")
        sys.exit(1)

    # ── 提取 ──
    theme_colors = extract_theme_colors(zf)
    theme_fonts = extract_theme_fonts(zf)
    used_fonts = extract_used_fonts(zf)
    fill_colors = extract_fill_colors(zf)
    slide_stats = extract_slide_stats(zf)

    # ── 分析 ──
    style_config = build_style_config(theme_colors, theme_fonts, slide_stats)

    # 匹配预设
    matches = []
    if args.compare and theme_colors:
        matches = match_duduppt_style(theme_colors)

    # ── 输出 ──
    if args.format == "json":
        output = {
            "source": str(pptx_path.name),
            "style_config": style_config,
            "theme_colors": theme_colors,
            "theme_fonts": theme_fonts,
            "used_fonts": used_fonts,
            "slide_stats": slide_stats,
            "duduppt_style_match": matches if args.compare else None,
        }
        json_str = json.dumps(output, indent=2, ensure_ascii=False)

        if args.out:
            Path(args.out).write_text(json_str, encoding='utf-8')
            print(f"✅ Style config saved: {args.out}")
        else:
            print(json_str)
    else:
        # Human-readable
        print(f"\n{'='*60}")
        print(f"📖 分析报告: {pptx_path.name}")
        print(f"{'='*60}")

        print(f"\n📐 基本统计:")
        print(f"  总页数:     {slide_stats['slide_count']}")
        print(f"  总形状数:   {slide_stats['total_shapes']}")
        print(f"  图片数量:   {slide_stats['total_pictures']}")
        print(f"  平均形状/页: {slide_stats['avg_shapes_per_slide']}")
        print(f"  图片密度:   {'🖼️ 高（图片密集型）' if slide_stats.get('image_heavy') else '📝 低（文字密集型）'}")

        if theme_colors:
            print(f"\n🎨 主题色:")
            accent_color = theme_colors.get('accent1', 'N/A')
            bg_color = theme_colors.get('lt1', 'N/A')
            text_color = theme_colors.get('dk1', 'N/A')
            # 简单色块展示
            def color_block(hex_c):
                try:
                    r, g, b = hex_to_rgb(hex_c)
                    return f"\033[48;2;{r};{g};{b}m    \033[0m"
                except:
                    return "    "
            print(f"  背景色:  {color_block(bg_color)} #{bg_color}")
            print(f"  强调色:  {color_block(accent_color)} #{accent_color}")
            print(f"  文字色:  {color_block(text_color)} #{text_color}")
            print(f"  完整色板: {len(theme_colors)} 种主题色定义")

        if theme_fonts:
            print(f"\n🔤 主题字体:")
            print(f"  标题字体: {theme_fonts.get('majorFont', 'N/A')}")
            print(f"  正文字体: {theme_fonts.get('minorFont', 'N/A')}")

        if used_fonts:
            print(f"\n🔤 实际使用字体 (top 5):")
            for font, count in list(used_fonts.get('all_fonts', {}).items())[:5]:
                bar = "█" * min(count, 20)
                print(f"  {font:30s} {bar} {count}次")

        if style_config.get("palette"):
            print(f"\n🔄 生成的 style config (用于 pptxgenjs):")
            print(f"  const C = {json.dumps(style_config['palette'], indent=2)}")

        if matches:
            print(f"\n🔗 最接近的 duduppt 预设风格:")
            for i, m in enumerate(matches, 1):
                match_str = "✅" if i == 1 else "  "
                print(f"  {match_str} #{i}: {m['style']}")
                print(f"       距离分值: {m['score']} (越低越接近)")
                print(f"       适用场景: {m['description']}")
                print(f"       色板: bg=#{m['palette']['bg']}, accent=#{m['palette']['accent']}")

        print(f"\n💡 建议:")
        if slide_stats.get('image_heavy'):
            print("  • 此 PPT 图片密度高 → 注意保留图片占位区域")
        if slide_stats.get('text_heavy'):
            print("  • 此 PPT 文字密度高 → 注意字体层级和可读性")
        if theme_fonts:
            print(f"  • 考虑安装缺失字体: {theme_fonts.get('majorFont', '')} / {theme_fonts.get('minorFont', '')}")
        print(f"  • 使用输出 style_config 中的 palette 做 pptxgenjs 配色")
        print()

    zf.close()


if __name__ == "__main__":
    main()
