# 复杂结构的处理规则

按论文需要读取相应部分，通用要求见上级 `SKILL.md`。

## 引用还原

- 先收集有效正文、列表、图注、表注、脚注、附录和 `\nocite` 所需的全部文献，再确定参考文献列表及其顺序。参考文献插入点前后的引用属于同一集合；数据库中未被引用且未被 `\nocite` 纳入的条目不自动加入。
- 检查主文件、文档类及样式中的 `natbib` / `biblatex` 选项、`\setcitestyle`、`\bibpunct`、`\bibliographystyle`、`\addbibresource`、`\bibliography` 和局部参考文献环境，用于理解引用语义和文献排序；输出标记遵循 `SKILL.md` 的数字编号规则。
- 优先使用与当前源码和 `.bib` 相符的 `.aux`、`.bbl`、`.bcf`、`.blg`；缺失时结合声明的样式与文献数据还原条目及排序。旧编译产物只能作线索，不能无条件覆盖当前源码。
- 项目有可用编译环境时，可在隔离副本按项目配置生成辅助文件。不要默认安装完整 TeX 发行版，也不要运行源码中的外部命令来试出样式。
- 最终列表确定后，按列表顺序一次性分配连续数字编号，并保存“引用键 → 编号 → 条目锚点”映射。这是 Markdown 输出使用的编号，不应冒称为原论文的数字标签；不要在转换各个段落或中文译文时重新编号。
- `\citep` 及作附带文献标记的 `\cite` 转为 `[n]`。`\citet` 等在句中承担叙述作用时保留作者，例如 `Smith et al. [n]`，避免删除句子的主语。独立的 `\citeauthor`、`\citeyear` 应保留作者或年份本身的语义，并在合适位置关联编号，避免相邻命令造成冗余的重复标记。
- 原作者—年份圆括号或上标引用默认改为行内数字方括号；只有用户明确要求保留另一种样式时才按其要求处理。保留组合引用中的每一篇文献、原有组内次序及前后附注、页码等信息，不要因编号相近而合并或漏掉条目。
- 在 natbib 中，无附注的 `\cite` 在作者—年份模式下等同于 `\citet`，在数字模式下等同于 `\citep`；这一源语义用于判断作者是否参与行文，并不要求输出继续采用作者—年份标记。其他包或自定义重定义按实际语义解析。参见 [natbib 官方手册](https://tug.ctan.org/macros/latex/contrib/natbib/natbib.pdf)。
- 参考文献中的作者、年份及 `2025a` / `2025b` 等后缀应由文献数据、样式规则或有效编译产物支持，不得猜测。机构作者、姓氏前缀、`and` 分隔符、`@string`、字符串连接和 `crossref` 均可能影响结果，不要用简单正则切割整个 BibTeX 文件。
- 保留每条文献的实际字段和有效 DOI/URL，不补造缺失信息。条目不翻译、不重复成双语；标题可沿用 `References` 或源码标题。若源文件先插入参考文献再插入附录，Markdown 同样如此，不用自动脚注将整份文献列表移到末尾。
- 使用显式锚点并核对链接，确保阅读器显示的是单层方括号编号。示例中的 Markdown 正文显示为 `[1], [2]`，文献条目也显式显示 `[1]`、`[2]`：

```markdown
Related work [[1]](#ref-paper-a), [[2]](#ref-paper-b).

<a id="ref-paper-a"></a>

[1] Smith, A. Paper A. Journal, 2025.

<a id="ref-paper-b"></a>

[2] Jones, B. Paper B. Conference, 2024.
```

## 复杂表格

表格的语义单位是逻辑单元格，不是源码的物理行。

- 只有位于当前 `tabular` 顶层、且不在嵌套分组或数学环境时，`&` 才分隔列，`\\` 才可能结束行。保留 `\&`，处理 `\makecell` 的内部换行。
- 按 `\multicolumn` 的跨度映射列，多层表头组合成完整路径。例如 `Solid–Solid` 下的 `SA`、`PC` 输出为 `Solid–Solid / SA<br>固体–固体 / SA` 与 `Solid–Solid / PC<br>固体–固体 / PC`。
- `\multirow` 的分类标签在其覆盖的各行重复，保持数据行次序。分组标题含义保留，纯横线可去除。
- 保留 `--`、`N/A`、有效空单元格、负号、误差、范围、小数位及最优值样式。去除 `\phantom`、纯间距、颜色或缩放时不能改变数值。
- 自定义增益宏如 `\gain{1.2}` 可能显示 `(+1.2)`，不能仅取其参数；先读取宏定义再确定可见内容。
- 普通文字提供双语，代码、模型名称、缩写、单位或纯数学不机械重复。缩写可保留，在相邻完整文字中说明中文含义。
- GFM 表格中的普通文字竖线写成 `\|`。数学中根据含义使用 `\lvert` / `\rvert`、`\lVert` / `\rVert`、`\mid` 等等价命令，避免管道被误当成分列；不要把不同含义一律替换成同一符号。
- 单元格用 `<br>` 接中文，整行仍占一个 Markdown 源码行；公式用行内数学，不在管道表格中放多行 `$$` 块。
- 必须多行展示的公式可紧邻表格作为编号公式块，单元格保留对应编号，并说明表示调整。无法保持数据归属的特殊结构须单独处理，不得静默生成错误网格。

```markdown
| Method<br>方法 | Solid–Solid / PC<br>固体–固体 / PC | Score<br>得分 |
| --- | ---: | ---: |
| Baseline<br>基线 | 32.2 | $s_0$ |
| Model-A | **36.3** | $s_1$ |
```

## 数学与跨阅读器显示

- 把外层 `equation` / `equation*` 转为 Markdown 数学块，保留主体；对齐块采用共同支持的 `aligned` 等环境，保持对齐和换行含义。
- 保留编号和重置规则，不让两个语言版本分别自动编号；未知编号不按当前片段从 1 猜测。
- 只按参数和作用域展开明确已定义的宏；不要靠删除未知命令或反斜杠修复公式。保留原数学片段用于等价性核对，不必交付工作材料。
- 已有可执行代码、内联代码标识符和数学中的文字不进入普通翻译流程。算法伪代码中的自然语言说明与注释按 `SKILL.md` 的“伪代码与算法”规则，在围栏代码块内保留英文并紧接中文注释；数学表达式转为等价的可读纯文本，不依赖代码块内的公式渲染。普通段落的字面 `$` 要转义。
- 图表编号和引用用可读文字即可；添加跳转链接时验证目标阅读器锚点，不把专用锚点规则当作通用标准。

维护时可核对下列官方来源，日常转换不必全部联网读取：

- [VS Code Markdown](https://code.visualstudio.com/Docs/languages/markdown)
- [GitHub Markdown 表格](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables)
- [Typora 数学与行内数学设置](https://support.typora.io/Math/)
- [Obsidian Markdown](https://help.obsidian.md/syntax)
- [PyMuPDF 按 DPI 生成 PNG](https://pymupdf.readthedocs.io/en/latest/recipes-images.html)
