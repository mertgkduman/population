"""Generate the main README: version overview first, then full model equations."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
versions=json.loads((ROOT/'publication/versions.json').read_text())
text='''# Developmental deference, cultural learning and demographic fitness

Hypothetical computational research. Technical validation does not establish a historical adaptation or genetic separability from cognition.

## Versions at a glance

| Version | Scientific question / change | Data and specification |
|---|---|---|
'''
for v in versions:
 path=v['id'] if v['id']!='future' else 'proposals'
 text+='| '+v['title']+' | '+v['summary']+' | ['+path+'/]('+path+'/) |\n'
text+='''
## View the research

Build and preview the six-tab site:

~~~bash
python scripts/build_pages.py
python -m http.server 8000 --directory docs
~~~

Open http://localhost:8000. The tabs are V1–V5 and Further work. Each has Model, Results, Changes and Shortcomings. The original interactive dashboards retain every plot family. Under each plot, an exact displayed-data ZIP supplies JSON, CSV, available parameters and units, alongside a reference-data package. Data and definitions remain version-specific. Large results load when requested. No new results are claimed for proposals.

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

## Equations and definitions

Each section below belongs to its own scientific version. F is the nonreproductive follower stage and A the reproductive adult stage. Maturation is irreversible at constant hazard m=1/tau. Extra cognitive substates in V4/V5 are not additional biological stages. All time and density units are arbitrary model units.

### V1: behavioral decisions and two-stage demography

The private error has mean0 and variance sigma_I²; adult error has mean b_A, variance sigma_A², and covariance rho sigma_I sigma_A with private error.

$$L_{copy}(d)=(1-d)\\sigma_I^2+d(\\sigma_A^2+b_A^2).$$

$$L_{blend}(d)=(1-d)^2\\sigma_I^2+d^2(\\sigma_A^2+b_A^2)+2\\rho d(1-d)\\sigma_I\\sigma_A.$$

$$\\mu_F=\\mu_{F,base}+k_{error}L,\\quad m=1/\\tau,\\quad N=F+A.$$

$$S(N)=\\frac{S_0}{1+N/K_N},\\quad \\beta(N,\\tau)=\\beta_{max}(\\tau)\\frac{S(N)}{K_S+S(N)}.$$

$$\\dot F=\\beta(N,\\tau)A-(m+\\mu_F)F,\\qquad \\dot A=mF-\\mu_A A.$$

$$B=\\beta A,\\quad D=\\mu_F F+\\mu_A A,\\quad M=mF,\\quad \\dot N=B-D.$$

M0 has constant beta_max=beta_const. M1 separately imposes:

$$\\beta_{max}(\\tau)=\\beta_{min}+\\beta_{gain}\\frac{\\tau}{\\tau+\\tau_{learning}}.$$

At low density beta0=beta_max S0/(KS+S0), with demographic matrix:

$$G_0=\\begin{pmatrix}-(m+\\mu_F)&\\beta_0\\\\m&-\\mu_A\\end{pmatrix}.$$

$$r_0=\\frac{-(m+\\mu_F+\\mu_A)+\\sqrt{(m+\\mu_F-\\mu_A)^2+4m\\beta_0}}{2}.$$

Positive growth requires m beta0 > mu_A(m+mu_F).

$$\\Delta r_0(d,\\tau)=r_0(d,\\tau)-r_0(0,\\tau),\\qquad r_T=\\frac{\\log[N(T)/N(0)]}{T}.$$

For positive persistent equilibrium:

$$\\beta_{required}=\\mu_A(1+\\mu_F\\tau),$$

$$N_*=K_N\\left[\\frac{S_0}{K_S}\\left(\\frac{\\beta_{max}}{\\beta_{required}}-1\\right)-1\\right],$$

$$A_*=\\frac{N_*}{1+\\mu_A\\tau},\\qquad F_*=\\mu_A\\tau A_*.$$

When r0<=0, the nonnegative equilibrium is0. Conditional mutant invasion uses the mutant matrix with beta(N*_resident,tau_mutant) and the same external advice distribution. Its dominant eigenvalue supports initial invasion, not fixation.

Survival to maturation with constant competing mortality is m/(m+mu_F); mean stage-exit time is1/(m+mu_F). Tau is not the mean observed age of surviving adults. With zero births and deaths:

$$F(t)=F(0)e^{-mt},\\qquad A(t)=A(0)+F(0)(1-e^{-mt}).$$

### V2: externally improving or decaying adult advice

$$\\sigma_A(t)=\\operatorname{clamp}[\\sigma_A(0)e^{-gt},\\sigma_{floor},\\sigma_{ceiling}].$$

Positive g improves precision; negative g degrades it. Substitute sigma_A(t) into both V1 losses and mu_F(t). F and A retain the same ODEs. A frozen-time eigenvalue r_inst(t) is a diagnostic; changing advice does not have the single stationary interpretation used for V1.

### V3: declining copying and increasing advice feature

$$d(t)=d_{floor}+(d_0-d_{floor})e^{-\\lambda_d t},$$

$$Q(t)=Q_0+(Q_{max}-Q_0)(1-e^{-\\lambda_Q t}),$$

$$\\sigma_A(t)=\\sigma_{A0}\\frac{1+Q_0}{1+Q(t)}.$$

Substitute d(t) and sigma_A(t) into V1's losses, mortality and two demographic equations. Rates lambda_d,lambda_Q are nonnegative. These are calendar-time functions rather than individual age or learned knowledge.

'''
for title,paths in [('V4: full endogenous-culture model',['v4/mathematical_model.md']),('V5: full private-evidence model and companion benchmarks',['v5/mathematical_model.md','v5/repertoire_model.md','v5/bayesian_benchmark.md'])]:
 text+='\n## '+title+'\n\n'
 for path in paths:
  text+='Source: ['+path+']('+path+')\n\n'+(ROOT/path).read_text()+'\n'
text+='\n## Further work\n\nSee [proposed investigations](proposals/RESEARCH_PROPOSALS.md). They are not executed V6 results.\n'
(ROOT/'README.md').write_text(text)
