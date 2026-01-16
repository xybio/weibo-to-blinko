# Weibo to Blinko Exporter

This tool converts data from `weibo-crawler` into a Blinko-importable `.bko` archive.
It reads the exported CSV, gathers downloaded media (images/videos), builds Blinko
metadata, and packages everything into a `.bko` file by default.

## Requirements

- Python 3.8+
- A completed `weibo-crawler` export:
  - CSV: `weibo/<nickname>/<uid>.csv`
  - Media folders:
    - `weibo/<nickname>/img/原创微博图片`
    - `weibo/<nickname>/video/原创微博视频`
    - `weibo/<nickname>/live_photo/原创微博Live Photo视频` (optional)

## Quick Start

```bash
python weibo-to-blinko/weibo-crawler/tools/weibo_to_blinko.py \
  --csv weibo-to-blinko/weibo-crawler/weibo/昵称/3046043151.csv \
  --media-root weibo-to-blinko/weibo-crawler/weibo/昵称 \
  --output-dir weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko \
  --export-template weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_export_bk \
  --seq-start 127 \
  --seq-order newest
```

This command outputs:

- Folder: `weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko`
- Archive: `weibo-to-blinko/weibo-crawler/weibo/昵称/blinko_bko.bko`

## What the Tool Generates

The output directory follows Blinko export structure:

- `files/`  
  - All attachments (images/videos) copied here with Blinko-style names.
  - `markdown_extract_<timestamp>/` contains the generated `note-*.md` files.
- `pgdump/bak.json`  
  - Notes metadata, including `createdAt` and `attachments`.
- `plugins/` and `vector/`  
  - Created as empty directories to match Blinko structure (no content copied).

## Notes and Behavior

- Each note is named: `note-<sequence>-<epoch_ms>.md`
- `createdAt/updatedAt` uses the timestamp from the filename (milliseconds).
- Attachments are detected by matching the weibo media naming:
  - Prefix: `<YYYYMMDD>T_<weibo_id>`
- All attachments are referenced in markdown as:
  - `/api/file/<filename>`
- No extra tags are added to the content.

## CLI Options

- `--csv`  
  Weibo CSV path (required).

- `--media-root`  
  Weibo user folder that contains `img/`, `video/`, `live_photo/` (required).

- `--output-dir`  
  Output folder to build the Blinko structure (required).

- `--export-template`  
  Path to an existing Blinko export folder. Used to copy the account template
  and version from `pgdump/bak.json`. If omitted, a minimal account template
  is created.

- `--seq-start`  
  Sequence number for the first note (default: `1`).

- `--seq-order`  
  `newest` or `oldest`. Controls how note IDs are assigned.

- `--no-zip`  
  Skip creating the `.bko` archive.

## Common Patterns

- Latest post should be the highest ID:
  - Use `--seq-order newest` and set `--seq-start` accordingly.

- Skip packaging:
  - Add `--no-zip` and manually zip later if needed.

## Troubleshooting

- Missing attachments:
  - Ensure you have downloaded images/videos in the expected media folders.
  - Check that `weibo_id` and date exist in the CSV.

- Wrong timestamps:
  - The tool uses the CSV time fields as local time.
  - Blinko will display based on its own timezone settings.
