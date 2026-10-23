# Improving Bike Rental Demand Prediction Through Data Augmentation: Vanilla Training, Mixup and RegMix Compared

Group 5 · Department of Computer Engineering (Regional Language), Pimpri Chinchwad College of Engineering (PCCOE), Pune

| Member | PRN |
|---|---|
| Amit Jadhav | 124B1D028 |
| Atharva Jamathkar | 124B1D007 |
| Yashvardhan Agwan | 124B1D056 |

## What this project does
We compare four ways of training the same multilayer perceptron (512-256 hidden units) to predict hourly bike rentals on the UCI Bike Sharing dataset (`hour.csv`, 17,379 rows):

1. **Vanilla**: no augmentation
2. **Mixup**: linear interpolation of inputs and labels (alpha chosen on validation)
3. **Global kNN mixing**: partner drawn from the k nearest neighbours (one k for all examples)
4. **RegMix** (Hwang and Whang, arXiv:2106.03374): a reduced-budget re-implementation in which an RL controller (PPO) learns a neighbour count per example. We run 40 search iterations with 20 policies each.

Two evaluation protocols are used: a **reproduction-style** protocol (300 train / 200 validation / remaining rows test, random) and a **chronological** protocol (60/20/20 split in time order). Each is run at 10%, 25%, 50% and 100% of the training pool over 5 seeds (0-4). Metrics: RMSE, MAE, R², training time, with paired t-tests, bootstrap confidence intervals and Holm correction.

## Main findings (see the paper for details)
- Augmentation helped little. With 30 random training examples RegMix lowered mean RMSE from 153.6 to 144.4 bikes/h (5 of 5 seeds), but this was not significant after Holm correction.
- With 300 examples Vanilla was best (RMSE 105.0) and RegMix worst (115.7).
- Under the chronological protocol Vanilla was best at every size; RegMix (run at all four sizes) was worse than Vanilla at each.
- RegMix took about 8x (300 examples) to 14x (averaged over sizes) the training time of Vanilla; its learned policy stayed close to uniform at this reduced budget.

## Repository contents
```
.
├── bike_regmix_experiments.ipynb   # full experiment notebook (Google Colab)
├── requirements.txt
├── data/
│   ├── hour.csv                    # UCI Bike Sharing, hourly (CC BY 4.0)
│   └── day.csv
├── outputs/
│   ├── config.json                 # settings, software versions, data SHA-256
│   ├── results.jsonl               # one line per (protocol, size, seed, method)
│   ├── lr_paper_hour.csv.json      # learning-rate selection, reproduction-style
│   ├── lr_chrono_hour.csv.json     # learning-rate selection, chronological
│   ├── tables/                     # CSV tables used in the paper
│   ├── figures/                    # figures used in the paper
│   └── preds/                      # saved test predictions (seed 0, full size)
├── paper/bike_demand_paper_IEEE.pdf
└── presentation/bike_demand_presentation.pptx
```

## How to run
1. Open `bike_regmix_experiments.ipynb` in Google Colab and select a GPU runtime (the reported runs used a Tesla T4).
2. Put `hour.csv` in the data folder the notebook expects (it is included in `data/`), or download it from the UCI repository: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
3. Run all cells. Results are appended to `results.jsonl`; the runner skips any (protocol, size, seed) already in the file, so an interrupted run can be resumed.
4. Tables, statistics and figures are regenerated from `results.jsonl` by the later cells.

Locally: `pip install -r requirements.txt`, then `jupyter notebook`.

## Settings used (also in `outputs/config.json`)
Batch 64, Adam, learning rate chosen from {1e-4, 3e-4, 1e-3} on validation with Vanilla only; early stopping (evaluate every 100 steps, patience 30, max 20,000 steps); Mixup alpha in {0.2, 1, 10, 100}; global kNN k in {1, 4, 16, 64, 256}; RegMix options {0, 1, 4, 16, 64, 256}, Beta(100, 100), controller MLP 4x100, controller learning rate 0.002, PPO 4 epochs, clip 0.2, entropy 0.01, EMA baseline 0.95, 40 iterations x 20 policies, 1,500 training steps per candidate.

## Data and licence
The Bike Sharing dataset is by H. Fanaee-T (UCI Machine Learning Repository, doi:10.24432/C5W894), licensed CC BY 4.0. Check the repository licence you choose for the code.

## References
- S.-H. Hwang and S. E. Whang, "RegMix: Data mixing augmentation for regression," arXiv:2106.03374v4, 2022.
- H. Zhang et al., "mixup: Beyond empirical risk minimization," ICLR, 2018.
- H. Fanaee-T, "Bike Sharing [Dataset]," UCI Machine Learning Repository, 2013.
