# Bike Rental Demand Prediction: Vanilla vs. Mixup vs. RegMix

Controlled comparison of data augmentation methods for regression on the UCI Bike Sharing dataset (`hour.csv`).
Method reference: Hwang & Whang, "RegMix: Data Mixing Augmentation for Regression", arXiv:2106.03374.

## Contents
- `bike_regmix_experiments.ipynb`: full pipeline (EDA, preprocessing, splits, Vanilla / Mixup / Global kNN / RegMix, statistics, figures, tables).
- `build_paper.py`: builds the IEEE two-column PDF; inserts tables and figures automatically from the notebook outputs.
- `data/`: `hour.csv`, `day.csv` from https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset (CC BY 4.0; Fanaee-T, 2013, doi:10.24432/C5W894).
- `requirements.txt`

## Run
1. Open the notebook in Google Colab with a GPU runtime. Set `PRESET = "QUICK"` for a smoke test, then `"STANDARD"` for the reported experiments.
2. Outputs (tables, figures, `results.jsonl`, `config.json`) are written to the output directory shown at the top of the run.
3. Build the paper: `python build_paper.py <OUTPUT_DIR> paper.pdf`

## Notes
RegMix here is a reduced-budget re-implementation of Algorithm 1 of the paper; deviations are listed at the top of the notebook.
