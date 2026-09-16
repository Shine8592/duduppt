# 多 Batch 合并 + 中文 QA

> 本文件是 SKILL.md 步骤 3.5「最终合并」与中文字体检查的完整展开。
> **何时读**：页面数 > 15 需要分批评生成时；以及**每次含中文的 deck 交付前**。

---

## 一、多 Batch 合并

### 1.1 何时可以分批

| 场景 | 策略 |
|---|---|
| **含 chart 的 PPT** | ❌ **禁止分批** —— 必须用单个 pptxgenjs 实例 |
| 纯文字 & 超 15 页 | ✅ 可分批生成后合并 |
| 含图片 / 复杂布局 | ⚠️ 谨慎：图片关系引用易断，建议单实例 |

### 1.2 为什么含 chart 必须单实例

pptxgenjs 的图表数据存在 `ppt/charts/chartN.xml` 并依赖
`ppt/charts/_rels/chartN.xml.rels` 与 `ppt/embeddings/` 中的工作簿。
多实例合并时这些关系 ID 会冲突 → 表现是"图表消失"或"打开时提示修复"。

**验证方法**（合并后必查）：

```python
import zipfile, re
z = zipfile.ZipFile('merged.pptx')

# 1. 每个 chart 都要有对应的 rels 与 embedding
charts = [n for n in z.namelist() if re.match(r'ppt/charts/chart\d+\.xml$', n)]
for c in charts:
    rels = c.replace('ppt/charts/', 'ppt/charts/_rels/') + '.rels'
    assert rels in z.namelist(), f'{c} 缺 rels（图表会消失）'

# 2. 关系 ID 不得重复
all_rels = [n for n in z.namelist() if n.endswith('.rels')]
ids = []
for r in all_rels:
    ids += re.findall(r'Id="([^"]+)"', z.read(r).decode('utf-8', 'ignore'))
dupes = {i for i in ids if ids.count(i) > 1}
# 注意：不同 .rels 文件内 ID 可以重复，这里只做参考，需按文件维度细查

print(f'charts={len(charts)}, rels={len(all_rels)}')
```

### 1.3 合并脚本要点

```python
import zipfile, shutil
from pathlib import Path

def merge_pptx(parts: list[Path], out: Path):
    """把多个单页 pptx 合并成一个（仅适用于纯文字页，含 chart 请勿使用）。"""
    base = parts[0]
    shutil.copy(base, out)
    with zipfile.ZipFile(out, 'a') as zout:
        slide_idx = len([n for n in zout.namelist()
                        if re.match(r'ppt/slides/slide\d+\.xml$', n)])
        for p in parts[1:]:
            with zipfile.ZipFile(p) as zin:
                # 只搬 slide xml + 其 rels + media（编号重排）
                ...
    # ⚠️ 合并后必须重写 [Content_Types].xml 与 ppt/_rels/presentation.xml.rels
```

> 实操建议：**优先单实例生成**。分批合并的复杂度高于收益，
> 只在"纯文字页 > 15"且单实例超时时才用。

---

## 二、中文字体 QA（最容易出问题的一环）

### 2.1 核心概念：字体有两个槽位

OOXML 里每个 run 的字体分**拉丁槽位**和**中文（东亚）槽位**：

```xml
<a:rPr>
  <a:latin typeface="Arial"/>       <!-- 拉丁/数字走这里 -->
  <a:ea typeface="Microsoft YaHei"/> <!-- 中文走这里（ea = East Asian） -->
</a:rPr>
```

**关键陷阱**：给一个中文 run 设置字体名时，如果只写了拉丁槽位，
**中文根本不会用这个字体** —— 它会走 PowerPoint 的默认东亚字体。

```js
// ❌ 只设了拉丁槽位，中文仍用默认字体（静默失效）
text: { fontFace: 'Microsoft YaHei' }   // 某些 pptxgenjs 调用等价于只设 latin

// ✅ 需要确保同时写入 <a:latin> 与 <a:ea>
```

> 这是**不报错、不警告、只在别人电脑上看起来不对**的一类问题。
> QA 必须显式检查 `<a:ea>` 是否存在。

### 2.2 QA 代码（区分槽位，别只查 `typeface` 出现过）

```python
import zipfile, re

z = zipfile.ZipFile('deck.pptx')
slides = [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]

CJK_FONTS = {
    '微软雅黑', 'Microsoft YaHei',          # Windows（最通用）
    'Noto Sans CJK SC', 'Source Han Sans SC', # 跨平台开源
    '思源黑体', 'Hiragino Sans GB',           # macOS
    'PingFang SC', '宋体', 'SimSun', '黑体',
}

ea_fonts, latin_fonts, problems = set(), set(), []

for n in slides:
    xml = z.read(n).decode('utf-8', 'ignore')

    ea_fonts.update(re.findall(r'<a:ea typeface="([^"]+)"', xml))
    latin_fonts.update(re.findall(r'<a:latin typeface="([^"]+)"', xml))

    # 检查：有中文但没设 ea 槽位
    has_cjk_text = bool(re.search(r'<a:t>[^<]*[\u4e00-\u9fff]', xml))
    has_ea = '<a:ea ' in xml
    if has_cjk_text and not has_ea:
        problems.append(f'{n}: CJK_NO_EA — 有中文但未设 <a:ea> 槽位（中文将用默认字体）')

    # 检查：中文字体写进了拉丁槽位（无效）
    latin_cjk = {f for f in re.findall(r'<a:latin typeface="([^"]+)"', xml)} & CJK_FONTS
    ea_any = set(re.findall(r'<a:ea typeface="([^"]+)"', xml))
    if latin_cjk and not ea_any:
        problems.append(f'{n}: CJK_FACE_UNREACHED — 中文字体写在 <a:latin>，中文不生效')

if problems:
    print('中文字体问题:')
    for p in problems:
        print('  -', p)
else:
    print(f'中文字体 OK  ea={ea_fonts}')

# 投递提示：告知用户 deck 依赖哪个字体
if ea_fonts:
    print(f'\n⚠️ 本 deck 依赖中文字体: {", ".join(sorted(ea_fonts))}')
    print('   收件人机器若未安装，PowerPoint 会替换字体（可能改变排版）')
```

### 2.3 字体选择建议（跨平台）

| 场景 | 推荐 | 说明 |
|---|---|---|
| **通用（优先）** | `微软雅黑` / `Microsoft YaHei` | Windows 自带，覆盖最广 |
| 跨平台开源 | `Noto Sans CJK SC` | 需收件人安装 |
| macOS | `Hiragino Sans GB` / `PingFang SC` | — |
| 正式文档 | `宋体` / `SimSun` | 打印友好 |

> ⚠️ **不要用 Linux 发行版字体**（如 `WenQuanYi Micro Hei`）作为投递字体 ——
> 开发机上有，但 Windows/macOS 收件人**没有**，等于没绑定。

### 2.4 一个必须知道的限制

**PowerPoint 支持嵌入字体，但 pptxgenjs / python-pptx 都不支持嵌入。**

后果：deck 在**未安装该中文字体**的机器上打开时，会回退到系统默认字体，
可能导致**文字溢出或换行位置变化**（虽然通常不会变方框）。

应对：
1. 优先用 `微软雅黑`（Windows 原生，覆盖最广）
2. 在交付说明里明确写出依赖字体
3. 关键页面留足文字空间（不要把文本框塞满）

### 2.5 中文排版细节

| 项 | 建议 |
|---|---|
| 字号 | 中文同字号视觉比拉丁大，层级可适当下调 1–2pt |
| 行距 | 中文需要更大行距（1.3–1.45 倍字号），否则显得拥挤 |
| 全角标点 | 中文全角标点后**不加**拉丁空格 |
| 中英混排 | 中英文之间可加空格（可选，需全篇统一） |
| 斜体 | 中文没有真斜体，不要用 italic，改用字重/颜色/字号区分 |

---

## 三、完整交付前 QA 顺序

```
1. 结构检查（zipfile，秒级）
   ├─ ZIP 完整、slide 数量正确
   ├─ 无占位符残留（Lorem / xxxx / 单击此处）
   ├─ chart：barDir 正确 + 有数据点（见 chart-type-anatomy.md）
   └─ 中文字体：ea/latin 槽位检查（本文件 2.2）

2. 渲染检查（LibreOffice，需环境支持）
   └─ 导出 PNG → 逐页看（优先查文字溢出）

3. 内容检查（人工/模型）
   ├─ 数字与证据表一致
   ├─ 每页有 SO WHAT
   └─ 标题是结论句而非主题词
```

---

## 四、相关文件

- 主流程：`SKILL.md` 步骤 3.5 / 3.4
- 图表坑：`chart-type-anatomy.md`
- 字体层级：`typography-scale.md`
- 配色：`palettes.md`
