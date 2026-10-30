---
spike: 012
idea: versioned-research-publication
name: versioned-pages
type: integration
validates: "Given preserved V1–V5 research artifacts, when a static viewer is built and packaged for GitHub Pages, then version navigation, equations, interactive results and raw-data downloads work within hosting limits"
verdict: VALIDATED
related: [001, 002, 003, 004, 009, 011]
tags: [publication, github-pages, data, verification]
---

# Spike012: versioned research publication

## What This Validates

A six-tab publication (V1–V5 plus Further work), with Model, Results, Changes and Shortcomings sections; a main README with version summaries followed by all equations; and a non-destructive GitHub-ready snapshot preserving scientific data and specifications.

## Research

Read the installed Codex gsd-spike adapter, spike/spike-wrap-up workflows and conventions. Continued quick-mode execution without a project lifecycle. Official sources: [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [regular-Git file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Compared whole standalone HTML publication (oversized historical blobs), LFS migration (unneeded tooling/history changes), and shared local assets plus lossless chunks and a clean snapshot (selected). No original scientific files or research history were rewritten.

## How to Run

From repository root:

    python scripts/build_pages.py
    python scripts/verify_pages.py
    python -m http.server 8765 --directory .
    node publication/browser_verify.js
    python scripts/prepare_github.py --output dist/github-repository

Open docs/index.html over HTTP. Full instructions and equations are in README.md.

## What to Expect

Five scientific versions and one proposals tab, readable saved model definitions/parameters, all existing interactive graph families, and actual displayed-data ZIP plus reference package links beneath each Plotly figure. The clean export is a Git repository on main with version-local raw data and restorable large files.

## Observability

publication/build_report.json, verification.json, browser_verification.json, download_verification.json, github_export_report.json and verification_summary.json; screenshots and independently captured plot ZIPs.

## Investigation Trail

2026-10-30: inspected branches/artifacts and actual installed GSD Core1.14.0 interface; confirmed no remote configured. User clarified the sixth tab as Further work. Built static tabs and documentation, shared Plotly and local chunked payloads, packaged raw source data, rewrote local document links, and checked project-prefix paths. A download-state serialization defect was caught and corrected. All five displayed-data archives pass independent parsing. Restored and rebuilt the clean GitHub export, preserving originals and source hashes. Prepared a main-branch Pages workflow without deployment.

## Results

**VALIDATED:**46 browser,24 static and five archive checks pass. No console errors or external browser requests. Site approximately681MB; largest published file approximately37MB. Three oversized originals restore from lossless chunks. No oversized blobs in clean export history. Scientific files remain unchanged. Main integration is authorized by the user; live GitHub deployment remains outside this preparation.
