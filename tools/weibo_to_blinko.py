#!/usr/bin/env python3
import argparse
import csv
import json
import mimetypes
import os
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert weibo-crawler CSV + media into a Blinko .bko folder structure."
    )
    parser.add_argument("--csv", required=True, help="Path to weibo CSV, e.g. weibo/昵称/3046....csv")
    parser.add_argument(
        "--media-root",
        required=True,
        help="Weibo user root folder, e.g. weibo/昵称",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output folder to build .bko structure, e.g. weibo/昵称/blinko_bko",
    )
    parser.add_argument(
        "--export-template",
        default="",
        help="Optional path to a Blinko export folder containing pgdump/bak.json for account template.",
    )
    parser.add_argument(
        "--seq-start",
        type=int,
        default=1,
        help="Starting sequence number for note IDs.",
    )
    parser.add_argument(
        "--seq-order",
        choices=["newest", "oldest"],
        default="newest",
        help="Sort order for assigning note IDs.",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Do not package output_dir into a .bko archive.",
    )
    return parser.parse_args()


def parse_date(row):
    date_str = (row.get("完整日期") or row.get("日期") or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def account_template_from_export(export_dir):
    if not export_dir:
        return None, "1.7.0"
    bak_path = Path(export_dir) / "pgdump" / "bak.json"
    if not bak_path.exists():
        return None, "1.7.0"
    data = json.loads(bak_path.read_text(encoding="utf-8"))
    version = data.get("version", "1.7.0")
    notes_list = data.get("notes") or []
    if notes_list:
        return notes_list[0].get("account"), version
    return None, version


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def collect_media(media_root, dt, weibo_id):
    prefix = f"{dt:%Y%m%d}T_{weibo_id}"
    img_dir = Path(media_root) / "img" / "原创微博图片"
    video_dir = Path(media_root) / "video" / "原创微博视频"
    live_dir = Path(media_root) / "live_photo" / "原创微博Live Photo视频"
    candidates = []
    for base in (img_dir, video_dir, live_dir):
        if not base.exists():
            continue
        candidates.extend(sorted(base.glob(f"{prefix}*")))
    return [p for p in candidates if p.is_file()]


def to_epoch_ms(dt):
    # Use local time to match weibo-crawler timestamp naming.
    return int(time.mktime(dt.timetuple()) * 1000)


def build_note_content(dt, row, attachments):
    lines = []
    lines.append(f"# {dt:%Y-%m-%d %H:%M:%S}")

    text = (row.get("正文") or "").strip()
    if text:
        lines.append("")
        lines.append(text)

    lines.append("")
    lines.append("---")
    weibo_id = (row.get("id") or "").strip()
    if weibo_id:
        lines.append(f"- 微博ID: {weibo_id}")

    topic = (row.get("话题") or "").strip()
    if topic:
        lines.append(f"- 话题: {topic}")

    mentions = (row.get("@用户") or "").strip()
    if mentions:
        lines.append(f"- @用户: {mentions}")

    location = (row.get("位置") or "").strip()
    if location:
        lines.append(f"- 位置: {location}")

    tool = (row.get("工具") or "").strip()
    if tool:
        lines.append(f"- 工具: {tool}")

    likes = (row.get("点赞数") or "").strip()
    comments = (row.get("评论数") or "").strip()
    reposts = (row.get("转发数") or "").strip()
    if likes or comments or reposts:
        lines.append(f"- 互动: 赞 {likes} | 评论 {comments} | 转发 {reposts}")

    if attachments:
        lines.append("")
        for att in attachments:
            if att["type"].startswith("image/"):
                lines.append(f"![]({att['path']})")
            else:
                lines.append(f"[视频]({att['path']})")

    return "\n".join(lines) + "\n"


def main():
    args = parse_args()

    csv_path = Path(args.csv)
    media_root = Path(args.media_root)
    output_dir = Path(args.output_dir)

    if output_dir.exists():
        shutil.rmtree(output_dir)

    files_dir = output_dir / "files"
    pgdump_dir = output_dir / "pgdump"
    plugins_dir = output_dir / "plugins"
    vector_dir = output_dir / "vector"
    for d in (files_dir, pgdump_dir, plugins_dir, vector_dir):
        ensure_dir(d)

    account_template, version = account_template_from_export(args.export_template)
    if not account_template:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        account_template = {
            "id": 1,
            "name": "user",
            "nickname": "user",
            "password": "",
            "image": "",
            "apiToken": "",
            "description": "",
            "note": 0,
            "role": "user",
            "loginType": "",
            "linkAccountId": None,
            "createdAt": now,
            "updatedAt": now,
        }

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            dt = parse_date(row)
            if not dt:
                continue
            rows.append((dt, row))

    rows.sort(key=lambda x: x[0], reverse=(args.seq_order == "newest"))

    extract_ts = int(time.time() * 1000)
    md_extract_dir = files_dir / f"markdown_extract_{extract_ts}"
    ensure_dir(md_extract_dir)

    notes_entries = []
    attachment_id = 1

    for i, (dt, row) in enumerate(rows):
        seq = args.seq_start + i
        base_ms = to_epoch_ms(dt)
        weibo_id = (row.get("id") or "").strip()

        media_paths = collect_media(media_root, dt, weibo_id)
        attachments = []

        for idx, media_path in enumerate(media_paths):
            ext = media_path.suffix.lower()
            attach_ms = base_ms + (idx * 1000)
            filename = f"{dt:%Y%m%d_%H%M%S}_{attach_ms}{ext}"
            dest = files_dir / filename
            if not dest.exists():
                shutil.copy2(media_path, dest)

            size = str(dest.stat().st_size)
            mime, _ = mimetypes.guess_type(filename)
            if not mime:
                mime = "application/octet-stream"

            created = datetime.fromtimestamp(attach_ms / 1000, tz=timezone.utc)
            created_iso = created.isoformat().replace("+00:00", "Z")

            attachments.append(
                {
                    "id": attachment_id,
                    "isShare": False,
                    "sharePassword": "",
                    "name": filename,
                    "path": f"/api/file/{filename}",
                    "size": size,
                    "type": mime,
                    "noteId": seq,
                    "accountId": account_template.get("id", 1),
                    "sortOrder": idx,
                    "createdAt": created_iso,
                    "updatedAt": created_iso,
                    "perfixPath": "",
                    "depth": 0,
                    "metadata": None,
                }
            )
            attachment_id += 1

        content = build_note_content(dt, row, attachments)
        md_name = f"note-{seq}-{base_ms}.md"
        (md_extract_dir / md_name).write_text(content, encoding="utf-8")

        created_iso = datetime.fromtimestamp(base_ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        notes_entries.append(
            {
                "id": seq,
                "account": account_template,
                "content": content,
                "isArchived": False,
                "isShare": False,
                "isTop": False,
                "createdAt": created_iso,
                "updatedAt": created_iso,
                "type": 0,
                "attachments": attachments,
                "tags": [],
                "references": [],
                "referencedBy": [],
            }
        )

    bak_out = {
        "notes": notes_entries,
        "exportTime": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": version,
    }
    (pgdump_dir / "bak.json").write_text(json.dumps(bak_out, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.no_zip:
        archive_path = output_dir.parent / f"{output_dir.name}.bko"
        if archive_path.exists():
            archive_path.unlink()
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(output_dir):
                for name in files:
                    full_path = Path(root) / name
                    rel_path = full_path.relative_to(output_dir)
                    zf.write(full_path, output_dir.name + "/" + rel_path.as_posix())


if __name__ == "__main__":
    main()
