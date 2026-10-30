# Developmental deference, cultural learning and demographic fitness

Repository: https://github.com/mertgkduman/population · Interactive research: https://mertgkduman.github.io/population/

Hypothetical computational research. Technical validation does not establish a historical adaptation or genetic separability from cognition.

## Versions at a glance

VERSION_TABLE_PLACEHOLDER

## View the research

Build and preview the seven-tab site:

~~~bash
python scripts/restore_large_files.py
python scripts/build_pages.py
python -m http.server 8000 --directory docs
~~~

Open http://localhost:8000. The tabs are V1–V5, Further work and V6, in that order. Each has Model, Results, Changes and Shortcomings. The original interactive dashboards retain every plot family. Under each plot, an exact displayed-data ZIP supplies JSON, CSV, available parameters and units, alongside a reference-data package. Data and definitions remain version-specific. Large results load when requested. No new results are claimed for proposals.

## Prepare GitHub Pages

The research history contains files above GitHub's [100 MiB regular-Git limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Preserve that history locally and create a clean publishable snapshot:

~~~bash
python scripts/prepare_github.py --output dist/github-repository
~~~

The output is a Git repository on **main**, containing every version's source, specification and data. Large originals are losslessly chunked inside their version folder. Run the following in the exported repository to restore original paths and verify their SHA-256 hashes:

~~~bash
python scripts/restore_large_files.py
~~~

The existing research history is not rewritten. Per-version records retain their contemporaneous branch names and verification context; the current main branch unifies every version. To publish, add your GitHub remote to the prepared repository, push main, and select **Settings → Pages → Source: GitHub Actions**. No remote or public deployment is performed by these preparation scripts. Do not push the original research history directly: it still contains historical oversized blobs.

The included workflow restores large files, builds and verifies the static site, then publishes the generated output. The builder enforces the [1 GB Pages site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). URLs are relative for project-site prefixes. Runtime assets are local; no API key or backend is required. Original standalone dashboards remain available offline after restoration. The portal's shared-data adapters use ordinary HTTP, as on GitHub Pages.


Select **GitHub Actions**, not **Deploy from a branch**. Publishing the source root runs Jekyll on the README and omits the generated Results pages. Equations are rendered with bundled KaTeX, including fonts; no runtime CDN is used.
