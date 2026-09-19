# BioSynthetix: In-Silico ADMET Screening & Mutation Platform

An enterprise bio-computational screening console for accelerating drug candidate optimization. Evaluates small molecules via topological fingerprints, predicts ADMET pharmacokinetics, and automates bioisosteric side-chain mutations to mitigate mutagenic toxicophores.

## Key Features
- **Topological Skeletal Canvas**: Live 2D skeletal rendering of drug candidates and highlighted toxicophores.
- **5-Axis ADMET Profiling**: Multi-property pharmacokinetic evaluation (Absorption, BBB, CYP3A4, Clearance, Toxicity).
- **Bioisosteric Mutator**: Automated replacement of mutagenic motifs (e.g., `-NO2` to `-CF3`) with verified safety increases.

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
