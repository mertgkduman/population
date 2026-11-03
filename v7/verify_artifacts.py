#!/usr/bin/env python3
"""Verify the V7 source package, isolated offline rebuild, and external manifests.

This never runs or modifies the scientific experiments. Hash-bearing reports are
kept outside the archive to avoid a self-referential package checksum.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict:
    return {'path': str(path.relative_to(REPO)), 'bytes': path.stat().st_size,
            'sha256': sha(path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-package', action='store_true')
    args = parser.parse_args()
    page = ROOT / 'research_dashboard.html'
    archive = ROOT / 'full_v7_research_project.zip'
    if args.refresh_package:
        subprocess.run([sys.executable, str(ROOT / 'build_dashboard.py'),
                        '--output', str(page), '--source-zip', str(archive)],
                       cwd=REPO, check=True, capture_output=True, text=True)
    assert (ROOT / 'index.html').read_bytes() == page.read_bytes(), 'index alias differs'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None, 'ZIP CRC failure'
        names = z.namelist()
        for name in names:
            path = REPO / name
            assert path.is_file() and z.read(name) == path.read_bytes(), f'stale ZIP entry: {name}'
        assert 'docs/assets/plotly.min.js' in names
        with tempfile.TemporaryDirectory(prefix='v7-isolated-rebuild-') as td:
            temp = Path(td)
            z.extractall(temp)
            rebuilt = temp / 'rebuilt.html'
            run = subprocess.run([sys.executable, str(temp / 'v7/build_dashboard.py'),
                                  '--output', str(rebuilt), '--source-zip', str(temp / 'rebuilt.zip')],
                                 cwd=temp, check=True, capture_output=True, text=True)
            info = json.loads(run.stdout)
            assert sha(rebuilt) == sha(page), 'isolated rebuild HTML differs'
    browser = json.loads((ROOT / 'browser_verification.json').read_text())
    portal = json.loads((REPO / 'publication/verification.json').read_text())
    assert browser['pass'] and portal['pass'], 'artifact acceptance failed'
    report = {'pass': True, 'checks': {'zip_crc': True, 'all_source_entries_match_live_bytes': True,
              'index_equals_dashboard': True, 'isolated_rebuild_dashboard_sha256': sha(page),
              'plotly_locally_bundled': True}, 'archive': artifact(archive) | {'entries': len(names)},
              'html': artifact(page), 'scope': 'V7 project; no older scientific version is needed for this rebuild'}
    (ROOT / 'export_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    handoff_path = ROOT / 'evidence/handoffs/08-dashboard.json'
    handoff = json.loads(handoff_path.read_text())
    handoff['artifacts']['offline_dashboard'] = artifact(page) | {
        'plotly': 'plotly.js v4.1.1', 'scientific_gzip_bytes': info['data_gzip_bytes']}
    handoff['artifacts']['full_local_project_zip'] = artifact(archive) | {
        'crc': 'verified', 'isolated_rebuild_dashboard_sha256': sha(page)}
    handoff['artifacts']['portal_v7'] = artifact(REPO / 'docs/apps/v7.html')
    handoff['artifacts']['corrected_public_data_zip'] = artifact(REPO / 'docs/downloads/v7/corrected-simulation-data.zip')
    size = sum(p.stat().st_size for p in (REPO / 'docs').rglob('*') if p.is_file())
    handoff['verification']['browser'] = f"v7/browser_verify.js: {len(browser['checks'])} passed; HTTP(S) blocked, actual stages/flux and all rendered exact-trace ZIPs checked; desktop/mobile screenshots saved"
    handoff['verification']['portal'] = f"scripts/verify_pages.py: {len(portal['checks'])} passed; {size} bytes below 1GB"
    handoff['verification']['source_checks'] = 'v7/verify_artifacts.py: ZIP CRC, every archive source byte, index alias, isolated rebuild SHA, and local Plotly verified'
    handoff['dashboard_contract']['exports'] = 'ZIP with exact embedded records, Plotly traces/layouts, complete selected parameters, freeze revision, units, metric, seed, transmission rule, and source hashes; separate PNG download'
    handoff_path.write_text(json.dumps(handoff, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
