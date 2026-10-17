"""Builds the conference paper PDF.
Usage: python build_paper.py [OUTPUT_DIR_FROM_NOTEBOOK] [out.pdf]
If OUTPUT_DIR contains the notebook's tables/ and figures/, they are inserted automatically.
Anything not yet measured is shown as a highlighted PENDING block. No numbers are invented."""
import os, sys, glob
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, KeepTogether, PageBreak, FrameBreak, NextPageTemplate)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = sys.argv[1] if len(sys.argv) > 1 else ""
PDF = sys.argv[2] if len(sys.argv) > 2 else "bike_demand_augmentation_paper.pdf"
D = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("S", "DejaVuSerifCondensed.ttf"), ("S-B", "DejaVuSerifCondensed-Bold.ttf"), ("S-I", "DejaVuSerifCondensed-Italic.ttf"), ("S-BI", "DejaVuSerifCondensed-BoldItalic.ttf")]:
    pdfmetrics.registerFont(TTFont(n, D + f))
pdfmetrics.registerFontFamily("S", normal="S", bold="S-B", italic="S-I", boldItalic="S-BI")

base = dict(fontName="S", fontSize=8.9, leading=11)
st = dict(
    title=ParagraphStyle("title", fontName="S-B", fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=8),
    auth=ParagraphStyle("auth", fontName="S", fontSize=10.5, leading=13.5, alignment=TA_CENTER),
    aff=ParagraphStyle("aff", fontName="S-I", fontSize=9, leading=12, alignment=TA_CENTER, spaceAfter=10),
    h1=ParagraphStyle("h1", fontName="S", fontSize=9, leading=11, alignment=TA_CENTER, spaceBefore=9, spaceAfter=4),
    h2=ParagraphStyle("h2", fontName="S-I", fontSize=9, leading=11, spaceBefore=5, spaceAfter=2),
    body=ParagraphStyle("body", alignment=TA_JUSTIFY, spaceAfter=5, **base),
    abs=ParagraphStyle("abs", alignment=TA_JUSTIFY, fontName="S-B", fontSize=8.6, leading=10.8, spaceAfter=3),
    cap=ParagraphStyle("cap", fontName="S", fontSize=7.8, leading=9.6, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8),
    tcap=ParagraphStyle("tcap", fontName="S", fontSize=7.8, leading=9.6, alignment=TA_CENTER, spaceAfter=3, spaceBefore=6),
    eq=ParagraphStyle("eq", alignment=TA_CENTER, spaceAfter=4, spaceBefore=2, **base),
    pend=ParagraphStyle("pend", fontName="S-I", fontSize=8, leading=10, backColor=colors.HexColor("#FFF3C4"), borderColor=colors.HexColor("#D9B300"),
                        borderWidth=0.6, borderPadding=4, spaceBefore=4, spaceAfter=8, alignment=TA_LEFT),
    ref=ParagraphStyle("ref", fontName="S", fontSize=7.9, leading=9.6, leftIndent=0.7 * cm, firstLineIndent=-0.7 * cm, alignment=TA_JUSTIFY, spaceAfter=2.5),
    cell=ParagraphStyle("cell", fontName="S", fontSize=7.4, leading=8.8),
    cellb=ParagraphStyle("cellb", fontName="S-B", fontSize=8.2, leading=10),
)
P = lambda t, s="body": Paragraph(t, st[s])
PENDING_USED = []
def pend(t): PENDING_USED.append(t); return P("<b>PENDING (to be completed from experiment output):</b> " + t, "pend")

def table_from_csv(path, caption, col_widths=None, index_label=None):
    df = pd.read_csv(path)
    data = [[Paragraph(f"<b>{c}</b>", st["cell"]) for c in df.columns]] + [[Paragraph(str(v), st["cell"]) for v in r] for r in df.values.tolist()]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black), ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([P(caption, "tcap"), t, Spacer(1, 6)])

def static_table(rows, caption, widths, bold_first_col=False):
    data = [[Paragraph(f"<b>{c}</b>", st["cell"]) for c in rows[0]]] + [[Paragraph(str(c), st["cell"]) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black), ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([P(caption, "tcap"), t, Spacer(1, 6)])

def pending_table(cols, rowlabels, caption, widths):
    rows = [cols] + [[r] + ["pending"] * (len(cols) - 1) for r in rowlabels]
    PENDING_USED.append(caption); return static_table(rows, caption, widths)

def fig(name, caption, width=None):
    width = width or CW
    p = os.path.join(OUT, "figures", name + ".png") if OUT else ""
    if p and os.path.exists(p):
        from PIL import Image as PI
        w, h = PI.open(p).size; return KeepTogether([Image(p, width=width, height=width * h / w), P(caption, "cap")])
    PENDING_USED.append(caption); return pend(caption + " [figure is produced by the notebook and inserted automatically on rebuild]")

def have(rel): return OUT and os.path.exists(os.path.join(OUT, rel))
MARG = 1.5 * cm; GAP = 0.6 * cm; CW = (A4[0] - 2 * MARG - GAP) / 2; W = CW
S = []

# ---------------- Title block ----------------
S += [P("Improving Bike Rental Demand Prediction Through Data Augmentation: Vanilla Training, Mixup and RegMix Compared", "title"),
      P("Amit, <font backColor='#FFF3C4'>[add full names of all group members]</font>", "auth"), P("Department of Computer Engineering, Pimpri Chinchwad College of Engineering (PCCOE), Pune, India", "aff")]

# ---------------- Abstract / Keywords ----------------
S.append(P("<i>Abstract</i>— Accurate short-term forecasts of bike rental demand support fleet allocation and operational planning in bike-sharing systems, yet prediction models are often trained on limited labelled observations. "
           "Data augmentation can regularise such models, but Mixup, designed for classification, interpolates labels linearly and can create misleading targets when the mixed examples are far apart in a continuous label space. "
           "RegMix (Hwang and Whang) addresses this by learning, for each training example, how many nearest neighbours it should be mixed with. "
           "This study compares Vanilla training, Mixup, a global nearest-neighbour mixing baseline and a reduced-budget re-implementation of RegMix on the UCI Bike Sharing hourly data. "
           "All methods share one multilayer perceptron and are evaluated under a reproduction-style random-subset protocol and a chronological protocol, at four training-set sizes and over repeated random seeds, using RMSE, MAE and R². "
           "<font backColor='#FFF3C4'>[PENDING: principal measured results and the main conclusion will be inserted once the experiments are complete.]</font>", "abs"))
S.append(P("<i>Index Terms</i>— bike-sharing demand prediction; data augmentation for regression; Mixup; RegMix; multilayer perceptron; chronological evaluation.", "abs"))

S.append(FrameBreak())
# ---------------- 1. Introduction ----------------
S.append(P("I. INTRODUCTION", "h1"))
S.append(P("Bike-sharing systems depend on having bikes available where and when riders want them, so operators need demand forecasts for fleet allocation and rebalancing. A systematic review of 35 papers published between 2015 and 2019 found that machine-learning work on bike sharing falls into classification and prediction tasks [1]. "
           "Demand prediction models, however, are frequently fitted to a modest number of labelled observations, and weather and calendar effects on demand are nonlinear. Under these conditions regularisation matters, and data augmentation is a way to improve generalisation without collecting more data."))
S.append(P("Mixup creates synthetic examples by linearly interpolating two training inputs and their labels, with the mixing weight drawn from a Beta distribution [2]. It was introduced for classification, and its regularising effect has been analysed theoretically [3], [4]. "
           "In regression the label space is continuous, so interpolating examples that are far apart can yield a label that does not correspond to the interpolated input, a failure related to manifold intrusion [5]. "
           "RegMix [6] responds to this by limiting the distance over which examples are mixed: a controller trained with reinforcement learning chooses, for every training example, the number of nearest neighbours it is mixed with, using validation loss as the reward. "
           "C-Mixup [7] pursues the same concern differently, sampling mixing partners according to label similarity."))
S.append(P("RegMix is the strongest available answer to this problem for tabular regression, but its evidence base for bike demand is narrow. In [6] the Bike experiment is one of four datasets, uses a random subset of 300 training and 200 validation examples, and reports no chronological evaluation. "
           "The authors also report that RegMix takes hours to converge, which makes its cost relevant to any practical use. "
           "It therefore remains unclear how the method behaves when the test period lies in the future, how its benefit changes with training-set size, and whether a simpler global nearest-neighbour restriction captures most of the gain."))
S.append(P("This paper addresses these points with a controlled comparison on the UCI Bike Sharing dataset [8]. It asks: (RQ1) does augmentation improve prediction over training without it; (RQ2) does selective nearest-neighbour mixing outperform unrestricted Mixup; (RQ3) how does the answer change with training-set size; "
           "(RQ4) are differences consistent across random seeds and under chronological rather than random evaluation; and (RQ5) what computational cost does the learned policy add. "
           "The contribution is an evaluation under a consistent protocol, not a new algorithm. Findings apply to this dataset, a single system and a two-year period, and are not claimed to hold for other cities."))

# ---------------- 2. Methods ----------------
S.append(P("II. METHODS", "h1"))
S.append(P("A. Data", "h2"))
S.append(P("The study uses only the Bike Sharing dataset from the UCI Machine Learning Repository [8], which contains hourly and daily rental counts for the Capital Bikeshare system in 2011 and 2012 together with weather and seasonal information. "
           "The hourly file, <i>hour.csv</i>, is used. Its documentation lists the calendar variables season, year, month, hour, holiday, weekday and working day; a weather-situation category; and normalised temperature, apparent temperature, humidity and wind speed. "
           "Temperature is scaled as (t − t<sub>min</sub>)/(t<sub>max</sub> − t<sub>min</sub>) with t<sub>min</sub> = −8 and t<sub>max</sub> = 39 °C, humidity is divided by 100 and wind speed by 67 [8]. "
           "The target is <i>cnt</i>, the total number of rentals, which equals the sum of the casual and registered counts. Both components are therefore excluded as inputs to avoid target leakage, and the record index and date string are dropped. "
           "The documentation reports no missing values; this, the duplicate check and an outlier screen are verified on the downloaded file and tabulated in Table 1. Outliers are retained because high-demand hours are genuine observations."))
if have("tables/table1_dataset_summary.csv"): S.append(table_from_csv(os.path.join(OUT, "tables/table1_dataset_summary.csv"), "Table 1. Dataset summary (measured on the downloaded file).", [3.0 * cm, W - 3.0 * cm]))
else: S.append(pending_table(["Item", "Value"], ["Rows in hour.csv", "Model inputs after encoding", "Missing values", "Duplicate rows", "Target mean / std / max"], "Table 1. Dataset summary (measured on the downloaded file).", [4.2 * cm, W - 4.2 * cm]))
S.append(P("B. Preprocessing", "h2"))
S.append(P("Hour, month and weekday are encoded cyclically with sine and cosine terms; season and weather situation are one-hot encoded; year, holiday and working day stay binary; the four weather quantities are used as supplied. All inputs are then standardised. "
           "The scaler is fitted on the training pool only, and the target is standardised with statistics of the labelled training subset; all reported errors are converted back to bike counts. The same preprocessing is applied to every method."))
S.append(P("C. Evaluation protocols", "h2"))
S.append(P("Two protocols are used, and they answer different questions. The <i>reproduction-style</i> protocol follows the Bike setting of [6]: a random draw of 300 training and 200 validation examples, with all remaining rows as the test set (the composition of the original test set is not specified in [6], so this is an assumption). "
           "The <i>chronological</i> protocol assigns the first 60% of the time-ordered records to training, the next 20% to validation and the last 20% to testing, so the test period follows the training period. "
           "For each protocol, subsets of 10%, 25%, 50% and 100% of the training pool are drawn from the training pool only; validation and test rows are never used as mixing inputs. "
           "Validation data are used for the learning-rate choice, Mixup and global-neighbour hyperparameters, early stopping and RegMix policy learning. The test set is used once, for final evaluation. "
           "Each configuration is repeated over several random seeds, with all methods sharing the same split within a seed."))
S.append(P("D. Regression model", "h2"))
S.append(P("Every method uses the same multilayer perceptron with hidden layers of 512 and 256 units, ReLU activations, mean-squared-error loss, the Adam optimiser [9] and mini-batches of 64, matching the architecture used for Bike in [6]. "
           "The learning rate is selected from {1×10<super>−4</super>, 3×10<super>−4</super>, 1×10<super>−3</super>} on validation data using Vanilla training only, so that the choice does not favour augmentation, and is then fixed. "
           "Training stops early when validation error has not improved for a fixed number of evaluations, and the best-validation weights are restored."))
S.append(P("E. Compared methods", "h2"))
S.append(P("<b>Vanilla.</b> Training on the original examples only. "
           "<b>Mixup.</b> For examples (x<sub>i</sub>, y<sub>i</sub>) and (x<sub>j</sub>, y<sub>j</sub>) with j drawn uniformly from the other training examples, the synthetic example is "
           "x̃ = λx<sub>i</sub> + (1 − λ)x<sub>j</sub> and ỹ = λy<sub>i</sub> + (1 − λ)y<sub>j</sub>, with λ ~ Beta(α, α) and the same λ for inputs and target [2]. The concentration α is chosen from {0.2, 1, 10, 100} on validation data. "
           "<b>Global kNN mixing.</b> The partner is drawn uniformly from the k nearest training neighbours (Euclidean distance, standardised features), with one k shared by all examples and chosen on validation data, as a simplified baseline from [6]. "
           "<b>RegMix.</b> Following [6], a controller assigns each training example a neighbour count from {0, 1, 4, 16, 64, 256} (0 meaning no mixing) with λ ~ Beta(100, 100). "
           "The controller is a multilayer perceptron with four hidden layers of 100 units whose input is a vector of ones and whose output is one softmax per example. "
           "At each iteration twenty policies are sampled, a regression model is trained under each, and the reward is the inverse of its validation loss minus an exponential moving average baseline (weight 0.95). The controller is updated with Proximal Policy Optimization [10] with an entropy bonus of 0.01."))
S.append(P("Because the search budget of [6], which reports hours of computation, is not available here, the method is described as a <i>reduced-budget re-implementation</i> and not as a replication. The main departures are: mixed examples are sampled on the fly each step from an example's policy-selected neighbour set instead of materialising all pairs; "
           "candidate models in the search use a fixed step budget without early stopping; PPO details not given in [6] (per-example probability ratio, four epochs per iteration, clipping 0.2, advantage scaling) are the author's choices; and the final policy is the controller's most probable option for each example."))
S.append(P("F. Metrics and statistical analysis", "h2"))
S.append(P("With test targets y<sub>i</sub>, predictions ŷ<sub>i</sub>, mean ȳ and n test observations, errors are reported in bikes per hour:"))
S.append(P("RMSE = √( (1/n) Σ<sub>i</sub> (y<sub>i</sub> − ŷ<sub>i</sub>)² )", "eq"))
S.append(P("MAE = (1/n) Σ<sub>i</sub> |y<sub>i</sub> − ŷ<sub>i</sub>|", "eq"))
S.append(P("R² = 1 − Σ<sub>i</sub> (y<sub>i</sub> − ŷ<sub>i</sub>)² / Σ<sub>i</sub> (y<sub>i</sub> − ȳ)²", "eq"))
S.append(P("Results are summarised as mean and standard deviation over seeds. Methods are compared with paired tests across seeds on identical splits, using a paired t-test, a Wilcoxon signed-rank test and a bootstrap 95% confidence interval for the mean RMSE difference, with Holm correction across comparisons. "
           "A two-sided Wilcoxon test cannot reach p &lt; 0.05 with fewer than six pairs, so p-values are treated as descriptive when few seeds are available, and statistical significance is distinguished from practical importance. "
           "Training time is measured in wall-clock seconds and, for RegMix, includes policy search. Code is written in Python with PyTorch and runs in Google Colab; seeds, configuration and software versions are saved with the results."))

# ---------------- 3. Results and Discussion ----------------
S.append(P("III. RESULTS AND DISCUSSION", "h1"))
S.append(P("A. Data characteristics", "h2"))
S.append(fig("fig2_demand_by_hour_season", "Fig. 1. Mean hourly rentals by hour of day and season (bikes per hour)."))
S.append(fig("fig3_correlation_heatmap", "Fig. 2. Pearson correlation between inputs and rentals. Correlation does not imply causation.", CW))
if not (have("figures/fig2_demand_by_hour_season.png")): S.append(pend("Description of the daily and seasonal demand pattern and of the strongest weather associations, written from the measured figures; confounding between temperature and hour of day to be noted."))
S.append(P("B. Results reported in the original RegMix study", "h2"))
S.append(P("For context, Table 2 reproduces the Bike results reported by the RegMix authors [6]. These numbers come from their setting (a random subset of 300 training and 200 validation examples, five repetitions) and are <b>not</b> results of the present study. "
           "Their RMSE values of roughly 369 to 393 are in bikes, and they cannot be compared directly with the values obtained here unless the target, file and test set coincide; this is checked against the target's standard deviation in Table 1."))
S.append(static_table([["Method (as reported in [6])", "RMSE (mean ± sd)"], ["Vanilla", "393.45 ± 0.90"], ["Mixup", "393.36 ± 1.84"], ["Global kNN (k = 68)", "388.81 ± 1.41"], ["RegMix", "368.86 ± 3.07"]],
                      "Table 2. Bike results published by Hwang and Whang [6] (not obtained in this study).", [5.2 * cm, 3.4 * cm]))
S.append(P("C. Main comparison", "h2"))
for pr, label in [("paper", "reproduction-style protocol"), ("chrono", "chronological protocol")]:
    f = f"tables/table3_main_{pr}.csv"; cap = f"Table {3 if pr=='paper' else 4}. Test performance, {label} (full training pool; mean ± sd over seeds; RMSE and MAE in bikes per hour)."
    S.append(table_from_csv(os.path.join(OUT, f), cap) if have(f) else pending_table(["Method", "RMSE", "MAE", "R²", "Time (s)"], ["Vanilla", "Mixup", "Global kNN", "RegMix"], cap, [2.6 * cm] + [(W - 2.6 * cm) / 4] * 4))
S.append(fig("fig6_rmse_comparison", "Fig. 3. Test RMSE by method under each protocol (error bars: standard deviation over seeds)."))
S.append(P("D. Effect of training-set size", "h2"))
for pr, label in [("paper", "reproduction-style"), ("chrono", "chronological")]:
    f = f"tables/table4_size_{pr}.csv"; cap = f"Table {5 if pr=='paper' else 6}. Test RMSE by training-set size, {label} protocol (bikes per hour)."
    S.append(table_from_csv(os.path.join(OUT, f), cap) if have(f) else pending_table(["Size", "Vanilla", "Mixup", "Global kNN", "RegMix"], ["10%", "25%", "50%", "100%"], cap, [2.6 * cm] + [(W - 2.6 * cm) / 4] * 4))
S.append(fig("fig7_performance_vs_size", "Fig. 4. Test RMSE versus training-set size (log scale) for each protocol."))
S.append(P("E. Consistency across seeds and statistical analysis", "h2"))
if have("tables/paired_stats.csv"):
    df = pd.read_csv(os.path.join(OUT, "tables/paired_stats.csv"))
    df = df[df.frac == 1.0][["protocol", "A", "B", "n_pairs", "mean_rmse_gain_of_B", "ci95_low", "ci95_high", "cohen_dz", "p_ttest_holm"]].round(3)
    df.to_csv("/tmp/_stats.csv", index=False); S.append(table_from_csv("/tmp/_stats.csv", "Table 7. Paired comparisons at the full training size (positive gain: method B has lower RMSE than method A)."))
else: S.append(pending_table(["Comparison", "Mean RMSE gain", "95% CI", "Effect size", "Holm-adjusted p"], ["Mixup vs Vanilla", "RegMix vs Vanilla", "RegMix vs Mixup", "RegMix vs Global kNN"], "Table 7. Paired comparisons at the full training size.", [2.6 * cm] + [(W - 2.6 * cm) / 4] * 4))
S.append(fig("fig8_seed_variability", "Fig. 5. Variability of test RMSE across random seeds at the full training size."))
S.append(P("F. Discussion", "h2"))
S.append(pend("Interpretation of Tables 3–7: which method is best under each protocol, the size of the differences in bikes per hour, whether they are consistent across seeds, whether augmentation helps small training subsets, "
              "and whether any gain justifies the extra training time. Unexpected or negative results are reported and explained only as far as the measurements support."))
S.append(P("The discussion will compare the measured results with Table 2 only after accounting for differences in setting. Three differences are already known. First, the original study draws a small random subset, whereas the chronological protocol here evaluates on a later period, "
           "so any distribution shift in demand between the training and test periods affects the two protocols differently. Second, RegMix here runs with a much smaller search budget than reported in [6], so a smaller gain than theirs would not by itself contradict their findings. "
           "Third, the exact test set and input encoding in [6] are not specified in full, and the input representation here differs from a raw 12-feature encoding. "
           "Reported improvements are therefore not presented as a reproduction of the published numbers."))
S.append(P("Limitations. The data cover a single bike-sharing system over two years, so findings are not generalised to other cities. Interpolated examples can be unrealistic even between near neighbours, particularly across hours and weather categories that were encoded with one-hot or cyclical features. "
           "Results depend on the chosen network and on hyperparameters selected on validation data; the learned policy is expensive relative to Mixup; the RegMix budget is reduced; and a limited number of seeds restricts the strength of any significance claim."))

# ---------------- 4. Conclusion ----------------
S.append(P("IV. CONCLUSION", "h1"))
S.append(pend("Conclusion stating, from the measured evidence, whether selective nearest-neighbour mixing improved bike-demand prediction over Vanilla and Mixup, in which protocol and training sizes, and at what computational cost."))
S.append(P("If augmentation proves useful, the practical implication is that operators with small labelled histories could improve forecasts without new data collection; if it does not, the result still indicates where Mixup-style interpolation is unsuited to this kind of demand data. "
           "Future work includes testing further time periods and other bike-sharing systems, comparing with label-similarity mixing such as C-Mixup [7], using forecasting architectures that model temporal dependence directly, "
           "and replacing the repeated model training in policy search by more efficient augmentation-policy methods, a direction also suggested in [6]."))

# ---------------- Acknowledgements ----------------
S.append(P("ACKNOWLEDGEMENT", "h1"))
S.append(P("The author thanks the Department of Computer Engineering, PCCOE, for academic support, and the organisers of the INNOVATE Young Researchers' Conference. The Bike Sharing dataset was provided by H. Fanaee-T through the UCI Machine Learning Repository under a CC BY 4.0 licence."))

# ---------------- References ----------------
S.append(P("REFERENCES", "h1"))
refs = [
 "V. Albuquerque, M. S. Dias, and F. Bação, “Machine learning approaches to bike-sharing systems: A systematic literature review,” <i>ISPRS Int. J. Geo-Inf.</i>, vol. 10, no. 2, 2021, doi: 10.3390/ijgi10020062.",
 "H. Zhang, M. Cisse, Y. N. Dauphin, and D. Lopez-Paz, “mixup: Beyond empirical risk minimization,” in <i>Proc. Int. Conf. Learn. Represent. (ICLR)</i>, 2018.",
 "L. Carratino, M. Cissé, R. Jenatton, and J.-P. Vert, “On mixup regularization,” arXiv:2006.06049, 2020.",
 "L. Zhang, Z. Deng, K. Kawaguchi, A. Ghorbani, and J. Zou, “How does mixup help with robustness and generalization?,” in <i>Proc. ICLR</i>, 2021.",
 "H. Guo, Y. Mao, and R. Zhang, “MixUp as locally linear out-of-manifold regularization,” in <i>Proc. AAAI Conf. Artif. Intell.</i>, 2019, pp. 3714–3722.",
 "S.-H. Hwang and S. E. Whang, “RegMix: Data mixing augmentation for regression,” arXiv:2106.03374v4, 2022.",
 "H. Yao, Y. Wang, L. Zhang, J. Zou, and C. Finn, “C-Mixup: Improving generalization in regression,” in <i>Adv. Neural Inf. Process. Syst. (NeurIPS)</i>, 2022, arXiv:2210.05775.",
 "H. Fanaee-T, “Bike Sharing [Dataset],” UCI Machine Learning Repository, 2013, doi: 10.24432/C5W894. [Online]. Available: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset",
 "D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,” in <i>Proc. ICLR</i>, 2015, arXiv:1412.6980.",
 "J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Proximal policy optimization algorithms,” arXiv:1707.06347, 2017.",
]
for i, r in enumerate(refs, 1): S.append(Paragraph(f"[{i}]&nbsp;&nbsp;{r}", st["ref"]))

# ---------------- build ----------------
def deco(c, d):
    c.saveState(); c.setFont("S", 8); c.setFillColor(colors.grey)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, f"{d.page}")
    if PENDING_USED: c.drawString(2 * cm, A4[1] - 1.1 * cm, "DRAFT: highlighted PENDING items require measured experiment output")
    c.restoreState()
TOP = A4[1] - 1.9 * cm; BOT = 1.9 * cm; HEAD = 9.0 * cm
doc = BaseDocTemplate(PDF, pagesize=A4, title="Improving Bike Rental Demand Prediction Through Data Augmentation", author="Amit")
colx = [MARG, MARG + CW + GAP]
first = PageTemplate(id="first", onPage=deco, frames=[Frame(MARG, TOP - HEAD, A4[0] - 2 * MARG, HEAD, id="head", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)] +
        [Frame(x, BOT, CW, TOP - HEAD - BOT - 0.3 * cm, id=f"c{i}", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0) for i, x in enumerate(colx)])
later = PageTemplate(id="later", onPage=deco, frames=[Frame(x, BOT, CW, TOP - BOT, id=f"l{i}", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0) for i, x in enumerate(colx)])
doc.addPageTemplates([first, later])
S.insert(0, NextPageTemplate("later"))
doc.build(S)
print("built", PDF, "| pending items:", len(PENDING_USED))
