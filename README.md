# latex2md

将英文论文的 LaTeX 源码转换为按原文顺序排列的中英双语 Markdown。

A Codex skill for converting English LaTeX papers into paragraph-aligned English–Chinese Markdown, with numbered citations, equations, tables, pseudocode, and PDF figures.

由 Codex 按 [SKILL.md](SKILL.md) 读取源码、转换结构并翻译；附带的 Python 脚本负责将论文使用的 PDF 图片渲染为 PNG。

## 转换规则

- **逐段双语**：英文后紧接简体中文，保留章节、列表、图表、参考文献和附录在源码中的逻辑顺序。
- **参考文献编号**：参考文献连续编号为 `[1]`、`[2]`、`[3]`……；正文与译文共用同一套编号，引用可跳转到对应条目，重复引用不增号。
- **伪代码代码块**：算法使用 `text` 围栏代码块，保留原有行号、缩进、循环、分支、输入输出和双语注释；代码块内使用可读的数学记法。
- **公式与交叉引用**：保留数学含义及可确定的原编号，展开必要的已知宏，还原章节、公式和图表引用。
- **双语表格**：使用 GFM 表格，在同一文字单元格内以 `<br>` 分隔原文和译文，保留数值、分组和表头含义。
- **PDF 图片**：默认 300 DPI，输出到原 PDF 同目录的同名 PNG，保留源文件；相同像素的已有 PNG 可复用。

详细行为见 [skill 指令](SKILL.md) 与 [复杂结构处理规则](references/conversion-rules.md)。

## 输入与输出

提供包含主 `.tex`、被引入文件、文献数据库和所用图片的论文源码目录，并指定主文件和输出路径（如有要求）。只有整篇论文 PDF 时不适用本工作流。

默认输出为源码目录中的 `<主文件名>.en-zh.md`；未明确要求更新时，已有输出不会被覆盖。图片采用相对路径，Markdown 可以随论文文件夹一起移动。

源码缺失、无法解析的宏、无法可靠确定的文献或编号会被具体标记。复杂数学、HTML 锚点与表格的显示取决于阅读器，应在实际使用的阅读器中核对。

## 安装

运行图片脚本需要 Python 3.10 或更高版本。依赖版本记录在 [requirements.txt](requirements.txt)，建议使用独立虚拟环境。

将仓库克隆到你的 skill 目录。以下示例使用 `$CODEX_HOME/skills`，未设置 `CODEX_HOME` 时使用 `~/.codex/skills`，并假设 `latex2md` 安装目录尚不存在。

### Windows PowerShell

```powershell
$skillBase = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$skillDir = Join-Path $skillBase 'skills\latex2md'
git clone https://github.com/CanyonChen/latex2md.git $skillDir
py -3 -m venv (Join-Path $skillDir '.venv')
& (Join-Path $skillDir '.venv\Scripts\python.exe') -m pip install -r (Join-Path $skillDir 'requirements.txt')
```

### macOS / Linux

```bash
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/latex2md"
git clone https://github.com/CanyonChen/latex2md.git "$skill_dir"
python3 -m venv "$skill_dir/.venv"
"$skill_dir/.venv/bin/python" -m pip install -r "$skill_dir/requirements.txt"
```

如果你的环境使用其他 skill 目录，调整安装路径即可。无需将本机虚拟环境加入仓库。

## 使用

在加载了该 skill 的 Codex 会话中，可以这样请求：

```text
使用 $latex2md，将 ./paper_latex 中的论文 LaTeX 源码转换为逐段中英双语 Markdown。
主文件为 ./paper_latex/main.tex，输出到 ./paper_latex/paper.md。
```

也可以明确要求更新已有文档：

```text
使用 $latex2md，更新 ./paper_latex/paper.md。
参考文献和正文引用统一为数字编号，所有算法伪代码保留为代码块。
```

### 单独转换 PDF 图片

在已安装依赖的 Python 环境中，从仓库根目录运行：

```bash
python scripts/pdf_to_png.py path/to/figure.pdf
python scripts/pdf_to_png.py path/to/figure.pdf --page 2 --dpi 300
python scripts/pdf_to_png.py path/to/figure-a.pdf path/to/figure-b.pdf
```

`--page` 从 1 开始，默认第 1 页，作用于本次调用的所有输入。脚本渲染完整页面，源码要求的额外裁剪、旋转或子图组合需要按转换规则处理。

已有 PNG 与目标渲染像素相同时输出 `REUSED`；内容、页码、分辨率或透明度不符时报告冲突并保留原文件。确认需要替换后可显式使用：

```bash
python scripts/pdf_to_png.py path/to/figure.pdf --overwrite
```

转换成功的退出码为 `0`，输入或转换失败为 `1`，缺少依赖或命令行参数无效为 `2`。

## 文件结构

```text
latex2md/
├── SKILL.md                       # 主工作流与质量核对规则
├── agents/openai.yaml             # skill 展示信息
├── references/conversion-rules.md # 引用、表格与数学的详细规则
├── scripts/pdf_to_png.py           # PDF 图片渲染工具
├── requirements.txt               # Python 依赖
├── README.md
└── LICENSE
```

修改规则时同步检查示例与正文要求；修改图片脚本时核对新建、复用、冲突保留、覆盖和选页行为。

## 许可证

本仓库原创内容采用 [MIT License](LICENSE)。

第三方依赖及输入论文遵循各自的许可证。PyMuPDF 采用 AGPL 或商业许可，具体条款见 [PyMuPDF 官方许可说明](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)。本仓库不随附依赖包或论文内容。
