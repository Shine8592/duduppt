#!/usr/bin/env python3
"""
duduppt — search-image.py
多来源 PPT 图片搜索：Pexels / Unsplash / Pixabay。
自动切换来源，输出可直接用于 PPT 的图片信息。

Usage:
  python3 scripts/search-image.py --query "business meeting"
  python3 scripts/search-image.py --query "technology abstract" --source pexels --count 3 --style bg
  python3 scripts/search-image.py --query "city skyline" --source unsplash --download ./images/

Supported sources (auto-fallback):
  - pexels:  需要 PEXELS_API_KEY (免费，pexels.com/api)
  - unsplash: 需要 UNSPLASH_ACCESS_KEY (免费，unsplash.com/developers)
  - pixabay: 需要 PIXABAY_API_KEY (免费，pixabay.com/api/docs)
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PPT_STYLES = {
    "bg":   {"orientation": "landscape", "min_w": 1920, "min_h": 1080, "desc": "16:9 背景"},
    "hero": {"orientation": "landscape", "min_w": 1024, "min_h": 768, "desc": "4:3 主图"},
    "icon": {"orientation": "square",    "min_w": 512,  "min_h": 512,  "desc": "1:1 图标"},
}


def get_api_key(name: str) -> str:
    """从环境变量或 .hermes/.env 读取 API key。"""
    key = os.environ.get(name, '')
    if not key:
        env_path = Path.home() / '.hermes' / '.env'
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith(f'{name}='):
                    key = line.split('=', 1)[1].strip().strip("'\"")
                    break
    return key


def search_pexels(query: str, count: int = 3) -> list:
    """Pexels API 搜索（推荐，质量最高）。"""
    api_key = get_api_key('PEXELS_API_KEY')
    if not api_key:
        return []

    params = urllib.parse.urlencode({
        "query": query,
        "per_page": count,
        "orientation": "landscape",
    })
    url = f"https://api.pexels.com/v1/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"Authorization": api_key})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = []
        for photo in data.get('photos', []):
            src = photo.get('src', {})
            results.append({
                "id": photo.get('id'),
                "url": src.get('original', ''),
                "medium": src.get('medium', ''),
                "small": src.get('small', ''),
                "photographer": photo.get('photographer', ''),
                "photographer_url": photo.get('photographer_url', ''),
                "alt": photo.get('alt', ''),
                "width": photo.get('width', 0),
                "height": photo.get('height', 0),
                "source": "pexels",
                "license": "Pexels License (free use)",
            })
        return results
    except Exception as e:
        print(f"  ⚠️ Pexels API error: {e}", file=sys.stderr)
        return []


def search_unsplash(query: str, count: int = 3) -> list:
    """Unsplash API 搜索。"""
    api_key = get_api_key('UNSPLASH_ACCESS_KEY')
    if not api_key:
        return []

    params = urllib.parse.urlencode({
        "query": query,
        "per_page": count,
        "orientation": "landscape",
    })
    url = f"https://api.unsplash.com/search/photos?{params}"

    try:
        req = urllib.request.Request(url, headers={
            "Authorization": f"Client-ID {api_key}",
            "User-Agent": "duduppt/1.0",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = []
        for photo in data.get('results', []):
            urls = photo.get('urls', {})
            results.append({
                "id": photo.get('id'),
                "url": urls.get('raw', ''),
                "medium": urls.get('regular', ''),
                "small": urls.get('small', ''),
                "photographer": photo.get('user', {}).get('name', ''),
                "photographer_url": photo.get('user', {}).get('links', {}).get('html', ''),
                "alt": photo.get('alt_description', ''),
                "width": photo.get('width', 0),
                "height": photo.get('height', 0),
                "source": "unsplash",
                "license": "Unsplash License (free use)",
            })
        return results
    except Exception as e:
        print(f"  ⚠️ Unsplash API error: {e}", file=sys.stderr)
        return []


def search_pixabay(query: str, count: int = 3) -> list:
    """Pixabay API 搜索。"""
    api_key = get_api_key('PIXABAY_API_KEY')
    if not api_key:
        return []

    params = urllib.parse.urlencode({
        "key": api_key,
        "q": query,
        "per_page": count,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
    })
    url = f"https://pixabay.com/api/?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "duduppt/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = []
        for photo in data.get('hits', []):
            results.append({
                "id": photo.get('id'),
                "url": photo.get('largeImageURL', ''),
                "medium": photo.get('webformatURL', ''),
                "small": photo.get('previewURL', ''),
                "photographer": photo.get('user', ''),
                "photographer_url": f"https://pixabay.com/users/{photo.get('user', '')}-{photo.get('user_id', '')}/",
                "alt": photo.get('tags', ''),
                "width": photo.get('imageWidth', 0),
                "height": photo.get('imageHeight', 0),
                "source": "pixabay",
                "license": "Pixabay License (free use)",
            })
        return results
    except Exception as e:
        print(f"  ⚠️ Pixabay API error: {e}", file=sys.stderr)
        return []


def download_image(url: str, output_path: str) -> bool:
    """下载图片到本地。"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp = urllib.request.urlopen(req, timeout=30)
        data = resp.read()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(data)
        return True
    except Exception as e:
        print(f"  ⚠️ Download failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="duduppt — 多来源 PPT 图片搜索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--query", "-q", required=True, help="搜索关键词")
    parser.add_argument("--source", choices=["pexels", "unsplash", "pixabay", "auto"],
                        default="auto", help="图片来源 (auto=自动尝试全部)")
    parser.add_argument("--count", "-n", type=int, default=3, help="返回数量")
    parser.add_argument("--style", choices=list(PPT_STYLES.keys()), default="hero",
                        help="PPT 用途 (影响图片尺寸建议)")
    parser.add_argument("--download", "-d", help="下载到指定目录")
    parser.add_argument("--format", choices=["human", "json"], default="human")
    args = parser.parse_args()

    # ── 搜索 ──
    sources_to_try = []
    if args.source == "auto":
        sources_to_try = ["pexels", "unsplash", "pixabay"]
    else:
        sources_to_try = [args.source]

    all_results = []
    for src in sources_to_try:
        if all_results:
            break  # 有结果就不再尝试其他源
        search_fn = {
            "pexels": search_pexels,
            "unsplash": search_unsplash,
            "pixabay": search_pixabay,
        }[src]
        results = search_fn(args.query, args.count)
        if results:
            all_results = results

    if not all_results:
        style = PPT_STYLES[args.style]
        print(f"\n❌ 未找到图片。请配置 API key 或使用 generate-image.js 生成。")
        print(f"\n支持的图片源 API key（免费注册）：")
        print(f"  PEXELS_API_KEY     → https://www.pexels.com/api/")
        print(f"  UNSPLASH_ACCESS_KEY → https://unsplash.com/developers")
        print(f"  PIXABAY_API_KEY    → https://pixabay.com/api/docs/")
        print(f"\n或使用 AI 生成：")
        print(f"  node scripts/generate-image.js --prompt \"{args.query}\" --style {args.style}")
        sys.exit(1 if not any([get_api_key('PEXELS_API_KEY'), get_api_key('UNSPLASH_ACCESS_KEY'), get_api_key('PIXABAY_API_KEY')]) else 0)

    # ── 下载 ──
    if args.download:
        dl_dir = Path(args.download)
        dl_dir.mkdir(parents=True, exist_ok=True)
        for i, img in enumerate(all_results):
            ext = ".jpg"
            fname = f"{args.query.replace(' ', '_')}_{i+1}{ext}"
            fpath = str(dl_dir / fname)
            print(f"  ⬇️  Downloading {i+1}/{len(all_results)}: {fname}")
            if download_image(img['url'], fpath):
                img['local_path'] = fpath
                print(f"     ✅ Saved: {fpath}")

    # ── 输出 ──
    style_info = PPT_STYLES[args.style]

    if args.format == "json":
        output = {
            "query": args.query,
            "style": args.style,
            "style_desc": style_info['desc'],
            "results": all_results,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n🖼️  PPT 图片搜索结果")
        print(f"{'='*50}")
        print(f"  关键词:  {args.query}")
        print(f"  用途:    {style_info['desc']} ({style_info['orientation']})")
        print(f"  来源:    {all_results[0]['source']}")
        print(f"  许可:    {all_results[0]['license']}")
        print(f"{'='*50}\n")

        for i, img in enumerate(all_results, 1):
            print(f"  #{i}: {img.get('alt', '') or '无描述'}")
            print(f"      摄影师: {img['photographer']}")
            print(f"      尺寸:   {img['width']}x{img['height']}")
            print(f"      URL:    {img['url']}")
            if img.get('local_path'):
                print(f"      本地:   {img['local_path']}")
            print()

        print(f"💡 提示：用 --download ./images/ 下载到本地")
        print(f"       或者复制 URL 到 generate-image.js 用 AI 风格重绘")


if __name__ == "__main__":
    main()
