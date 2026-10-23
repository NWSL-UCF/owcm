# OWCM Paper Reproduction Scripts

This directory contains standalone scripts used to reproduce selected results reported in the accompanying OWCM survey paper.

## Figure 12

Run:

```bash
python reproduce/figure12.py
```

The script generates:

- `reproduction_outputs/figure12_owcm_validation.png`
- `reproduction_outputs/figure12_owcm_validation.pdf`
- `reproduction_outputs/table17_figure12_parameters.csv`

Figure 12 contains the six OWCM validation panels for atmospheric, indoor, underwater, underground, and space optical channels.

## Table 17

Run:

```bash
python reproduce/table17.py
```

The script generates:

- `reproduction_outputs/table17_parameters.csv`

The table records the representative simulation parameters associated with the Figure 12 scenarios.

## Reproducibility environment

Use the dependency versions specified in `requirements-reproducibility.txt`. The scripts are intended to be run from the repository root after installing OWCM with:

```bash
pip install -e .
```

All parameters required to reproduce the selected outputs are explicitly specified in the scripts rather than relying on undocumented runtime state.
