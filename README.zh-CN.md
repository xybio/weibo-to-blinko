# weibo-to-blinko

[English](README.md) | [中文](README.zh-CN.md)

本仓库提供一套“微博导出 → Blinko 导入”的流程与工具。
基于 `dataabc/weibo-crawler` 进行功能增强，新增转换脚本，
可生成 Blinko 可直接导入的 `.bko` 包。

原始 `weibo-crawler` 文档已原样保留在：
`README.weibo-crawler.md`。

## 增强内容

- 将 `weibo-crawler` 的 CSV + 媒体文件转换为 Blinko 笔记
- 生成 `attachments` 元数据，确保图片/视频可显示
- 默认打包生成 `.bko`

## 快速开始

1) 使用 `weibo-crawler` 导出微博

确保存在以下内容：

- CSV：`weibo/<昵称>/<uid>.csv`
- 媒体目录：
  - `weibo/<昵称>/img/原创微博图片`
  - `weibo/<昵称>/video/原创微博视频`
  - `weibo/<昵称>/live_photo/原创微博Live Photo视频`（可选）

2) 转换为 Blinko

```bash
python weibo-to-blinko/weibo-crawler/tools/weibo_to_blinko.py \
  --csv weibo-to-blinko/weibo-crawler/weibo/昵称/3046043151.csv \
  --media-root weibo-to-blinko/weibo-crawler/weibo/昵称 \
  --output-dir weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko \
  --export-template weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_export_bk \
  --seq-start 127 \
  --seq-order newest \
  --keep-meta tool \
  --no-embed-media
```

输出结果：

- 目录：`weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko`
- 归档：`weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko.bko`

3) 在 Blinko 中导入 `.bko`

使用 Blinko 的导入功能选择生成的 `.bko` 文件。

## 转换脚本文档

完整参数与说明见：

- `weibo-to-blinko/weibo-crawler/tools/README.zh-CN.md`

## Weibo-Crawler 原始文档

- `README.weibo-crawler.md`（来自 `dataabc/weibo-crawler`）

## 致谢

- 原始爬虫：`https://github.com/dataabc/weibo-crawler`
