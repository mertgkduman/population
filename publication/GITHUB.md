# GitHub publication

Repository: https://github.com/mertgkduman/population

Expected Pages address after activation: https://mertgkduman.github.io/population/

## One-time Pages activation

A repository administrator must open https://github.com/mertgkduman/population/settings/pages and set **Build and deployment → Source → GitHub Actions**.

Then open **Actions → Versioned research Pages → Run workflow** (branch main), or push a new main commit. The workflow restores the preserved large files, builds the site, checks source hashes/archives/links and publishes the static artifact.

The normal workflow token can deploy to an existing Pages site; it cannot create the initial Pages configuration. The workspace SSH key can push repository content but does not grant REST administration access. No access token needs to be pasted into a chat or committed.

## Build a clone locally

    python scripts/restore_large_files.py
    python scripts/build_pages.py
    python scripts/verify_pages.py
    python -m http.server 8000 --directory docs

Open http://localhost:8000. Install plotly==7.1.0 if it is not already present. The Markdown build renderer is vendored.

Large originals are restored and verified from version-local chunks and remain ignored by Git. Do not add the restored oversized HTML or gzip files to regular Git history.
