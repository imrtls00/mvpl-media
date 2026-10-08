# Media cleanup

Media here is a temporary host for Buffer, not storage. Nothing stays more than 15 days.

- Every upload is logged in `MANIFEST.tsv` (path, date added) at upload time.
- Run weekly, not per reel: `python3 scripts/cleanup_media.py` (dry run), then `--apply`.
- Before applying, pass `--keep keep.txt` listing any media still used by a scheduled or draft Buffer post.
- `.last_cleanup` holds the date of the last run. If it is older than 7 days, run it.
- Deleting a file does not erase git history. Only publish media you are fine keeping in history, or squash history if needed.
- Original files live with Sameer. Delete here never means lost.
