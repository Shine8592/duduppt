#!/usr/bin/env python3
"""
duduppt — research-topic.py
Deep Research 阶段 0：自动搜索目标主题的多源信息，为证据表打基础。

Usage:
  python3 scripts/research-topic.py --topic "中国财富管理市场规模 2026"
  python3 scripts/research-topic.py --topic "家族信托发展趋势" --depth deep --sources 8
  python3 scripts/research-topic.py --topic "AI Agent 行业格局" --format markdown

Output:
  - 结构化 research report（可直接喂入 Phase 1 证据表）
  - 每个来源附 URL/置信度/时效性标记
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path


def search_tavily(query: str, max_results: int = 5) -> list:
    """通过 Tavily API 搜索（结构化搜索，适合事实性查询）。"""
    try:
        import os
        api_key = os.environ.get('TAVILY_API_KEY', '')
        if not api_key:
            env_path = Path(os.path.expanduser('~/.hermes/.env'))
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith('TAVILY_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        break

        if api_key:
            import urllib.request
            data = json.dumps({
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            }).encode()
            req = urllib.request.Request(
                "https://api.tavily.com/search",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=15)
            result = json.loads(resp.read())
            results = []
            for r in result.get('results', []):
                results.append({
                    "title": r.get('title', ''),
                    "url": r.get('url', ''),
                    "content": r.get('content', '')[:500],
                    "score": r.get('score', 0),
                    "engine": "tavily",
                })
            return results
    except Exception as e:
        print(f"  ⚠️ Tavily search failed: {e}", file=sys.stderr)

    return []


def search_exa(query: str, max_results: int = 5) -> list:
    """通过 Exa API 搜索（语义/神经搜索，适合找相似内容、深度内容）。"""
    try:
        import os
        api_key = os.environ.get('EXA_API_KEY', '')
        if not api_key:
            env_path = Path(os.path.expanduser('~/.hermes/.env'))
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith('EXA_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        break

        if api_key:
            import urllib.request
            data = json.dumps({
                "query": query,
                "num": max_results,
                "type": "keyword",  # keyword | neural | auto
                "contents": {"highlights": True},
            }).encode()
            req = urllib.request.Request(
                "https://api.exa.ai/search",
                data=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=15)
            result = json.loads(resp.read())
            results = []
            for r in result.get('results', []):
                highlights = r.get('highlights', [])
                results.append({
                    "title": r.get('title', ''),
                    "url": r.get('url', ''),
                    "content": (highlights[0] if highlights else r.get('text', ''))[:500],
                    "score": r.get('score', 0.5),
                    "engine": "exa",
                })
            return results
    except Exception as e:
        print(f"  ⚠️ Exa search failed: {e}", file=sys.stderr)

    return []


def search_querit(query: str, max_results: int = 5) -> list:
    """通过 Querit API 搜索（通用网页搜索，适合兜底）。"""
    try:
        import os
        api_key = os.environ.get('QUERIT_API_KEY', '')
        if not api_key:
            env_path = Path(os.path.expanduser('~/.hermes/.env'))
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith('QUERIT_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        break

        if api_key:
            import urllib.request
            data = json.dumps({
                "query": query,
                "count": max_results,
            }).encode()
            req = urllib.request.Request(
                "https://api.querit.ai/v1/search",
                data=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=15)
            result = json.loads(resp.read())
            results = []
            for r in result.get('results', {}).get('result', result.get('data', [])):
                results.append({
                    "title": r.get('title', ''),
                    "url": r.get('url', ''),
                    "content": r.get('snippet', r.get('content', ''))[:500],
                    "score": r.get('score', 0.5),
                    "engine": "querit",
                })
            return results
    except Exception as e:
        print(f"  ⚠️ Querit search failed: {e}", file=sys.stderr)

    return []


def search_serpapi(query: str, max_results: int = 5) -> list:
    """通过 SerpAPI (Google) 搜索"""
    try:
        import os
        api_key = os.environ.get('SERPAPI_API_KEY', '')
        if not api_key:
            env_path = Path(os.path.expanduser('~/.hermes/.env'))
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith('SERPAPI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        break

        if api_key:
            import urllib.request
            params = urllib.parse.urlencode({
                "api_key": api_key,
                "q": query,
                "num": max_results,
                "engine": "google",
            })
            req = urllib.request.Request(
                f"https://serpapi.com/search?{params}",
                headers={"User-Agent": "duduppt/1.0"}
            )
            resp = urllib.request.urlopen(req, timeout=15)
            result = json.loads(resp.read())
            results = []
            for r in result.get('organic_results', []):
                results.append({
                    "title": r.get('title', ''),
                    "url": r.get('link', ''),
                    "content": r.get('snippet', '')[:500],
                    "score": 0.5,
                })
            return results
    except Exception as e:
        print(f"  ⚠️ SerpAPI search failed: {e}", file=sys.stderr)

    return []


def search_fallback(query: str, max_results: int = 3) -> list:
    """兜底：用 curl + duckduckgo lite 搜索（无需 API key）"""
    results = []
    try:
        import urllib.request
        encoded = urllib.parse.quote(query)
        url = f"https://lite.duckduckgo.com/lite/?q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', 'ignore')

        # 从 HTML 中提取结果（DuckDuckGo Lite 的简易解析）
        import re
        # 查找结果链接和文本
        links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)</a>', html)
        seen = set()
        for url, title in links:
            if url not in seen and len(results) < max_results:
                seen.add(url)
                results.append({
                    "title": title.strip(),
                    "url": url,
                    "content": "",
                    "score": 0.3,
                })
    except Exception as e:
        print(f"  ⚠️ Fallback search failed: {e}", file=sys.stderr)

    return results


def extract_page_content(url: str, max_chars: int = 1000) -> str:
    """尝试提取网页正文（简化版）"""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8)
        html = resp.read().decode('utf-8', 'ignore')
        # 简单提取文本
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except:
        return ""


def estimate_timeliness(url: str, content: str) -> str:
    """粗估信息时效性"""
    import re
    # 检查 URL 中的年份
    years = re.findall(r'(20\d{2})', url)
    if years:
        y = int(years[-1])
        if y >= 2026: return "最新"
        if y >= 2025: return "较新"
        return "可能过时"
    # 检查内容中的日期
    dates = re.findall(r'(20\d{2})', content)
    if dates:
        y = int(dates[-1])
        if y >= 2026: return "最新"
        if y >= 2025: return "较新"
    return "未知"


def format_report(topic: str, results: list, depth: str) -> str:
    """格式化为结构化报告。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# 🔍 Deep Research: {topic}")
    lines.append(f"> 生成时间: {now} | 搜索深度: {depth} | 来源数: {len(results)}")
    lines.append("")

    if not results:
        lines.append("⚠️ 未搜索到相关结果。请检查主题词或手动提供材料。")
        lines.append("")
        return "\n".join(lines)

    lines.append("## 搜索结果摘要")
    lines.append("")
    lines.append(f"| # | 标题 | 来源 | 时效性 | 置信度 |")
    lines.append(f"|---|------|------|--------|--------|")
    for i, r in enumerate(results, 1):
        domain = urllib.parse.urlparse(r['url']).netloc if r['url'] else "N/A"
        timeliness = estimate_timeliness(r['url'], r['content'])
        confidence = "高" if r.get('score', 0) > 0.8 else ("中" if r.get('score', 0) > 0.5 else "低")
        lines.append(f"| {i} | {r['title'][:50]} | {domain} | {timeliness} | {confidence} |")

    lines.append("")
    lines.append("## 关键发现")
    lines.append("")
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r['title']}")
        lines.append(f"- **来源**: {r['url']}")
        if r['content']:
            # 取前 3 句
            sentences = [s.strip() for s in r['content'].replace('\n', ' ').split('。') if s.strip()]
            for s in sentences[:3]:
                lines.append(f"  - {s}。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 📋 证据表输入建议")
    lines.append("")
    lines.append("以下数据/论点可纳入 Phase 1 证据表：")
    lines.append("")
    lines.append("| ID | 论点/数据 | 数值 | 来源 | 置信度 | 建议视觉 |")
    lines.append("|----|-----------|------|------|--------|---------|")
    for i, r in enumerate(results, 1):
        lines.append(f"| R{i} | {r['title'][:40]} | — | [{i}] | {'高' if r.get('score', 0) > 0.8 else '中'} | 待定 |")

    lines.append("")
    lines.append("> 💡 **使用方式**: 以上内容已格式化，可直接复制到 Phase 1 证据表。")
    lines.append("> 缺失的数据项标记为「需人工验证」，不编造。")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="duduppt Deep Research 阶段 0：自动搜索目标主题的多源信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--topic", "-t", required=True, help="搜索主题")
    parser.add_argument("--depth", choices=["basic", "deep"], default="deep",
                        help="搜索深度: basic=5条, deep=10条")
    parser.add_argument("--sources", type=int, default=5,
                        help="最大来源数 (默认 5)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="输出格式")
    parser.add_argument("--out", "-o", help="输出文件路径")
    args = parser.parse_args()

    max_results = args.sources

    print(f"\n🔍 duduppt Deep Research")
    print(f"{'='*50}")
    print(f"  主题:     {args.topic}")
    print(f"  深度:     {args.depth}")
    print(f"  最大来源: {max_results}")
    print(f"{'='*50}\n")

    # ── 三引擎搜索 ──
    all_results = []

    search_plan = [
        ("Tavily", search_tavily),
        ("Exa", search_exa),
        ("Querit", search_querit),
        ("SerpAPI", search_serpapi),
        ("DuckDuckGo 兜底", search_fallback),
    ]

    for name, fn in search_plan:
        if len(all_results) >= max_results:
            break
        remain = max_results - len(all_results)
        if remain <= 0:
            break
        print(f"  {name} 搜索中...")
        try:
            results = fn(args.topic, remain)
            if results:
                print(f"     → {len(results)} 条结果")
                all_results.extend(results)
            else:
                print(f"     → 无结果")
        except Exception as e:
            print(f"     → 出错: {e}")

    # 去重
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r['url'] and r['url'] not in seen_urls:
            seen_urls.add(r['url'])
            unique_results.append(r)

    print(f"\n  去重后: {len(unique_results)} 条唯一结果\n")

    # ── 输出 ──
    if args.format == "json":
        output = {
            "topic": args.topic,
            "timestamp": datetime.now().isoformat(),
            "depth": args.depth,
            "total_sources": len(unique_results),
            "results": unique_results,
        }
        json_str = json.dumps(output, indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(json_str, encoding='utf-8')
            print(f"✅ Report saved: {args.out}")
        else:
            print(json_str)
    else:
        report = format_report(args.topic, unique_results, args.depth)
        if args.out:
            Path(args.out).write_text(report, encoding='utf-8')
            print(f"✅ Report saved: {args.out}")
        else:
            print(report)


if __name__ == "__main__":
    main()
