# Weibo 导出到 Blinko

本工具用于将 `weibo-crawler` 导出的数据转换为 Blinko 可导入的 `.bko` 格式。
它会读取 CSV、收集下载的媒体（图片/视频）、生成 Blinko 元数据，并默认打包成 `.bko`。

## 依赖

- Python 3.8+
- 已完成 `weibo-crawler` 导出：
  - CSV：`weibo/<昵称>/<uid>.csv`
  - 媒体目录：
    - `weibo/<昵称>/img/原创微博图片`
    - `weibo/<昵称>/video/原创微博视频`
    - `weibo/<昵称>/live_photo/原创微博Live Photo视频`（可选）

## 快速开始

```bash
python weibo-to-blinko/weibo-crawler/tools/weibo_to_blinko.py \
  --csv weibo-to-blinko/weibo-crawler/weibo/昵称/3046043151.csv \
  --media-root weibo-to-blinko/weibo-crawler/weibo/昵称 \
  --output-dir weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko \
  --export-template weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_export_bk \
  --seq-start 127 \
  --seq-order newest
```

执行后输出：

- 目录：`weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko`
- 归档：`weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko.bko`

## 输出结构

生成的目录符合 Blinko 导出结构：

- `files/`  
  - 所有附件（图片/视频）会被复制到这里，并按 Blinko 规则命名。
  - `markdown_extract_<timestamp>/` 下为生成的 `note-*.md`。
- `pgdump/bak.json`  
  - 笔记元数据，包含 `createdAt` 与 `attachments`。
- `plugins/` 与 `vector/`  
  - 仅创建空目录以匹配结构，不写入内容。

## 规则说明

- 笔记命名：`note-<序号>-<毫秒时间戳>.md`
- `createdAt/updatedAt` 使用文件名中的毫秒时间戳
- 附件通过微博媒体命名规则匹配：
  - 前缀：`<YYYYMMDD>T_<weibo_id>`
- Markdown 中附件引用形式为：
  - `/api/file/<文件名>`
- 不会额外插入标签或内容

## 参数说明

- `--csv`  
  微博 CSV 路径（必填）。

- `--media-root`  
  微博用户目录（包含 `img/`、`video/`、`live_photo/`）（必填）。

- `--output-dir`  
  输出目录（必填）。

- `--export-template`  
  指向已有 Blinko 导出目录，用于复用账号模板与版本号（来自 `pgdump/bak.json`）。
  不填则使用最小账户模板。

- `--seq-start`  
  笔记起始序号（默认：`1`）。

- `--seq-order`  
  序号排序方式：`newest` 或 `oldest`。

- `--no-zip`  
  不打包 `.bko`。

## 常见场景

- 最新微博编号最大：
  - 使用 `--seq-order newest`，并设置合适的 `--seq-start`。

- 仅生成目录，不打包：
  - 添加 `--no-zip`，稍后自行打包。

## 排查建议

- 图片/视频不显示：
  - 确认媒体已下载并位于正确目录。
  - 确认 CSV 中存在有效 `weibo_id` 与日期。

- 时间显示偏移：
  - 时间戳使用本地时间生成，Blinko 显示受其时区设置影响。
