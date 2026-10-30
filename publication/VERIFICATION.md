# Versioned publication verification

**Technical verdict: VALIDATED.** This verdict concerns publication packaging, navigation, plots, downloads and GitHub readiness. No new scientific model or numerical research was run.

- 46 browser checks pass across V1–V5 and Further work: four nested sections, keyboard selection, deep links, original interactive plots, links beneath every rendered plot, exact displayed-data ZIPs and mobile layout. Zero console errors and zero external requests were recorded; HTTPS was blocked.
- 24 static checks pass: local relative links, all reference archive CRCs and source-byte hashes, separate-version catalogues, payload chunk sizes and Pages/file-size limits.
- Five captured displayed-plot ZIPs independently pass Python ZIP CRC/JSON/CSV checks. Each includes the actual trace values, parameters and available axis units. Packages stay below10MiB in these tests; the adapter excludes the full application dataset from selection metadata.
- The generated site is approximately681MB, below the1GB Pages ceiling. Its largest published file is approximately37MB, below GitHub's100MiB regular-file limit.
- Scientific files in v1–v5 are unchanged from af171fe. Their prior numerical verification records remain intact.
- A separate clean Git repository on main was created and audited: no oversized blobs anywhere in its history. Three original V5 files are preserved in version-local24MiB chunks, deduplicating identical content. Restoration verifies every original SHA-256. The exported checkout was restored, built and verified successfully using the same source commands as the Pages workflow.

## Investigation trail

Only five scientific versions were present. The user clarified that the sixth tab should contain proposals. Existing self-contained dashboards were too large for regular GitHub history; original research history was retained and a clean publication snapshot prepared instead. Hosted dashboards share a local Plotly asset and extract unchanged embedded datasets into small local binary chunks. All original graph families and model logic are retained.

A browser test exposed that V4's application-state object includes its entire dataset. The first download adapter serialized too much state. The final adapter records only selection fields and configuration; all five plot ZIPs now pass independent checks. Reference links also distinguish context trajectories, evolution, volatility, repertoire, tutor and Bayesian datasets. Metadata and raw source archives are version-specific.

## Scope of testing

The browser test used Chrome for Testing154 with a project-style /docs/ URL prefix over local HTTP. The production GitHub Actions workflow was not run remotely because no GitHub remote or Pages site is configured. Setup/deploy action versions and limits were checked against official GitHub documentation. Existing offline standalone dashboards remain preserved; the lightweight publication adapters use HTTP as GitHub Pages does.

The source research repository intentionally retains its old oversized history. Push the clean snapshot in dist/github-repository, not that original history. No force push, destructive history rewrite, remote write or public deployment occurred.
