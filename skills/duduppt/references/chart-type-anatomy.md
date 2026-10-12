# Chart 类型剖析与 pptxgenjs 坑清单

> 本文件是 SKILL.md 步骤 3.2「Chart Type 大坑」的完整展开。
> **何时读**：Phase 3 生成任何含图表的页面**之前**必读。

---

## 一、最致命的一个坑：`addChart('column')` 产出空白页

### 现象

```js
// ❌ 不报错，但这一页是空白的（最难排查的一类问题）
slide.addChart('column', data, { x: 1, y: 1, w: 8, h: 4 });
```

pptxgenjs **不会抛异常**，生成的 PPTX 能正常打开，但图表区域是空白。

### 原因

pptxgenjs 的图表类型枚举里，柱状图统一用 `'bar'`，**方向由 `barDir` 决定**：

- `barDir: 'bar'`（默认）→ **水平**条形图
- `barDir: 'col'` → **垂直**柱状图

`'column'` 不是合法类型名，被静默忽略。

### 正确写法

```js
// ✅ 垂直柱状图（最常见的"柱状图"）
slide.addChart('bar', data, { x: 1, y: 1, w: 8, h: 4, barDir: 'col' });

// ✅ 水平条形图（长类别名时更好读）
slide.addChart('bar', data, { x: 1, y: 1, w: 8, h: 4, barDir: 'bar' });
```

### 自检（见 SKILL.md 的 zipfile 检查）

```python
cx = z.read(chart_path).decode('utf-8')
assert 'barDir' in cx, 'chart 缺 barDir，可能是空白柱状图'
assert 'val="col"' in cx or 'val="bar"' in cx, f'barDir 未正确设置: {cx[:200]}'
```

---

## 二、其他已验证的坑

### 2.1 图表类型名对照表

| 想要的图 | pptxgenjs 类型 | 必要参数 |
|---|---|---|
| 垂直柱状图 | `'bar'` | `barDir: 'col'` |
| 水平条形图 | `'bar'` | `barDir: 'bar'`（或省略） |
| 折线图 | `'line'` | — |
| 面积图 | `'area'` | — |
| 饼图 | `'pie'` | — |
| 环形图 | `'doughnut'` | `holeSize: 50` |
| 散点图 | `'scatter'` | — |
| 雷达图 | `'radar'` | — |

### 2.2 中文标签乱码

图表内的类别名/系列名若是中文，**必须**同时确保：

1. 全局字体已绑定中文字体（见 `merge-and-qa.md` 的 EA 槽位检查）
2. 图表的 `catAxisLabelFontFace` / `valAxisLabelFontFace` 显式指定

```js
slide.addChart('bar', data, {
  barDir: 'col',
  catAxisLabelFontFace: 'Microsoft YaHei',
  valAxisLabelFontFace: 'Microsoft YaHei',
  dataLabelFontFace: 'Microsoft YaHei',
});
```

> 不指定时，LibreOffice 渲染可能用默认字体 → 中文变方框；
> PowerPoint 打开时又可能正常 → **QA 结果与实际投递不一致**。

### 2.3 数据必须原生传数组，不能传图片

```js
// ✅ 原生：PowerPoint 里可右键"编辑数据"
slide.addChart('bar', [{ name: '2026', labels: ['Q1','Q2'], values: [100,120] }], {...});

// ❌ 禁止：截图贴图 → 不可编辑，违反"双硬门槛"
slide.addImage({ path: 'chart-screenshot.png', ... });
```

**例外**：PowerPoint 无原生形式的图表类型（桑基图 / 网络图 / 和弦图）才允许用图片，
且必须在页脚注明"示意图"。

### 2.4 渐变填充不支持

pptxgenjs 对图表系列的渐变支持不完整。需要渐变效果时：

- 用**纯色** + 深浅变化来模拟层次
- 或把渐变做成**背景图片**垫在图表下方（图表本身仍为原生）

### 2.5 图表与文字重叠

pptxgenjs 的 `x/y/w/h` 是 inch 单位，且**不会自动避让**其他元素。
常见错误：图表区高度过大压住下方 SO WHAT 条。

```
自查：图表底边 y + h 必须 < SO WHAT 条的 y
推荐留白：图表与下方元素间距 ≥ 0.2 inch
```

---

## 三、QA 检查项（机械可判，秒级）

生成后立即用 zipfile 扫一遍（无需 LibreOffice）：

```python
import zipfile, re

z = zipfile.ZipFile('deck.pptx')
charts = [n for n in z.namelist() if 'charts/chart' in n and n.endswith('.xml')]

for c in charts:
    cx = z.read(c).decode('utf-8', 'ignore')
    n = c.split('/')[-1]

    # 1. 柱状图必须有 barDir，且值合法
    if '<c:barChart>' in cx:
        m = re.search(r'<c:barDir val="(\w+)"/>', cx)
        assert m, f'{n}: barChart 缺 barDir（会渲染成空白）'
        assert m.group(1) in ('col', 'bar'), f'{n}: barDir 非法值 {m.group(1)}'

    # 2. 系列必须有数据点
    pts = re.findall(r'<c:pt ', cx)
    assert len(pts) > 0, f'{n}: 图表无数据点（可能是空的）'

    # 3. 中文轴标签需指定字体
    has_cjk_label = bool(re.search(r'<a:t>[^<]*[\u4e00-\u9fff]', cx))
    has_cjk_font = 'YaHei' in cx or 'Noto Sans CJK' in cx or 'Source Han' in cx
    if has_cjk_label:
        assert has_cjk_font, f'{n}: 中文轴标签未指定中文字体（可能乱码）'

    print(f'{n}: OK  barDir={m.group(1) if m else "-"}  points={len(pts)}')
```

---

## 四、排查顺序（当图表页看起来不对时）

1. **先看是否空白** → 检查 `barDir`（本文件第一节）
2. **中文变方框** → 检查轴标签字体（2.2）
3. **图表压住文字** → 检查坐标（2.5）
4. **数据不对** → 检查是否误用了图片（2.3）
5. **渲染图与 PowerPoint 不一致** → 字体替换问题（见 `merge-and-qa.md`）

---

## 五、相关文件

- 主流程：`SKILL.md` 步骤 3.2 / 3.4
- 中文字体与合并：`merge-and-qa.md`
- 布局与坐标换算：`references/layouts/layout-library.md`
