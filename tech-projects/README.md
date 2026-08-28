# RD19 / RD10 技术规范书 Word 批注

## 当前状态

本仓库、全部可见远端分支、Git 历史、既有 PR、当前工作区和可访问的历史
Cloud Agent 产物中均未找到两份原始 Word 二进制文件。PR #3 的历史任务只收到
了 RD19 的纯文本抽取结果，没有收到或保存 `.docx`；该抽取结果不能用于重建原稿。

因此，PR #49 仅包含：

- 完整批注 JSON；
- 原位注入原始 DOCX 的原生 Word 批注工具；
- 批注清单、正文文字一致性和 OOXML 结构测试。

两份已批注 `.docx` **不在本 PR 中**，因为 Cloud VM 无法取得原稿。严禁添加
占位 DOCX，也严禁根据纯文本抽取结果新打字、重建或臆造 DOCX。

## 已向用户交付的文件

真实、已验证的批注稿已在共享电脑上于 VM 外生成并交付给用户；正文文字不变，
且使用原生 Word 批注。交付记录如下（文件不在本 PR 中）：

- `tech-projects/procurement/specs/commented/RD19-技术规范书-批注稿.docx`
  - 大小：34636 bytes
  - SHA-256：`4c46da8cfba1d5cbbae1475d8c44e3ec3b03522c89d0bd56bef77d3c067d19cc`
  - 原生 Word 批注：34 条
- `tech-projects/procurement/specs/commented/RD10-技术规范书-批注稿.docx`
  - 大小：32359 bytes
  - SHA-256：`f8af90a922ccda66b745a4de3d77c4625e342f21e0f6d0e9a71079a10d4c6ca1`
  - 原生 Word 批注：13 条

以上路径用于标识已交付文件，不表示这些文件存在于当前分支或 PR。

## 批注清单

`tools/comments.json` 收录：

- RD19：34 条（总览 1 条、格式 F01–F16、技术接口 P01–P17）
- RD10：13 条（总览 1 条、D01–D12）

高、中、低优先级意见分别以 `[高]`、`[中]`、`[低]` 开头。Word 批注作者固定为
“科技项目专责”，initials 固定为“科”。

## 生成与验证

安装依赖：

```bash
python3 -m pip install -r tech-projects/requirements.txt
```

把两份未经改写、未经批注的用户原稿放到固定路径后，在仓库根目录运行：

```bash
python3 tech-projects/tools/inject_word_comments.py
```

工具会：

1. 读取原始 DOCX ZIP，不接受已有 Word 批注的文件；
2. 在 `word/document.xml` 的现有 run 外插入
   `commentRangeStart`、`commentRangeEnd` 和 `commentReference`，不拆分或改写
   任何正文文字节点；
3. 新增 `word/comments.xml`，并登记内容类型和关系；
4. 逐项确认所有锚点均存在，否则不落盘；
5. 用 `python-docx` 比较原稿与批注稿的段落和表格文字；
6. 确认 `comments.xml`、开始标记、结束标记、引用标记计数一致；
7. 确认除四个批注所需部件外，其余 DOCX 部件保持原始字节。

只校验清单（不要求原稿存在）：

```bash
python3 tech-projects/tools/inject_word_comments.py --check-config
```

运行测试：

```bash
python3 -m unittest discover -s tech-projects/tests -v
```

除非取得两份真实原稿，不得运行生成流程并向本 PR 添加任何 DOCX。
