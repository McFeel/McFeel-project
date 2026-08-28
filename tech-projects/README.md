# RD19 / RD10 技术规范书 Word 批注

## 当前状态

本仓库、全部可见远端分支、Git 历史、既有 PR、当前工作区和可访问的历史
Cloud Agent 产物中均未找到两份原始 Word 二进制文件。PR #3 的历史任务只收到
了 RD19 的纯文本抽取结果，没有收到或保存 `.docx`；该抽取结果不能用于重建原稿。

因此，本提交严格按任务中的阻塞分支处理：

- 未从抽取文本重新排版或臆造 Word 正文；
- 未生成看似完整、实为重建的“批注稿”；
- 收录完整批注清单和原位注入工具；
- 工具仅接受下列固定路径的真实原稿，缺任一文件即退出，且不产生部分输出。

所需原稿路径：

- `tech-projects/procurement/specs/RD19-技术规范书-用户交来.docx`
- `tech-projects/templates/RD10-技术规范书-用户交来.docx`

计划输出路径：

- `tech-projects/procurement/specs/commented/RD19-技术规范书-批注稿.docx`
- `tech-projects/procurement/specs/commented/RD10-技术规范书-批注稿.docx`

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

原稿补入后，必须提交两份原稿和两份生成的批注稿，并把生成命令输出中的
正文一致性和批注计数写入 PR 说明，方可解除本阻塞状态。
