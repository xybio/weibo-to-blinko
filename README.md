# weibo-to-blinko

[English](README.md) | [中文](README.zh-CN.md)

This repository provides a workflow and tooling to export Weibo content and import it into Blinko.
It is based on the open-source crawler from `dataabc/weibo-crawler` and adds a converter that
generates Blinko-compatible `.bko` archives.

The original `weibo-crawler` documentation is preserved verbatim here:
`README.weibo-crawler.md`.

## What This Adds

- Converts `weibo-crawler` CSV + downloaded media into Blinko notes
- Generates Blinko `attachments` metadata so images/videos render correctly
- Packages output into a `.bko` archive by default

## Quick Start

1) Export Weibo with `weibo-crawler`

Ensure the following exist:

- CSV: `weibo/<nickname>/<uid>.csv`
- Media folders:
  - `weibo/<nickname>/img/原创微博图片`
  - `weibo/<nickname>/video/原创微博视频`
  - `weibo/<nickname>/live_photo/原创微博Live Photo视频` (optional)

2) Convert to Blinko

```bash
python weibo-to-blinko/weibo-crawler/tools/weibo_to_blinko.py \
  --csv weibo-to-blinko/weibo-crawler/weibo/昵称/3046043151.csv \
  --media-root weibo-to-blinko/weibo-crawler/weibo/昵称 \
  --output-dir weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko \
  --export-template weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_export_bk \
  --seq-start 127 \
  --seq-order newest
```

This produces:

- Folder: `weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko`
- Archive: `weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko.bko`

3) Import `.bko` into Blinko

Use Blinko's import function and select the generated `.bko`.

## Converter Docs

Full CLI options and behavior are documented here:

- `weibo-to-blinko/weibo-crawler/tools/README.md`

## Weibo-Crawler Docs

- `README.weibo-crawler.md` (verbatim from `dataabc/weibo-crawler`)

## Credits

- Original crawler: `https://github.com/dataabc/weibo-crawler`
