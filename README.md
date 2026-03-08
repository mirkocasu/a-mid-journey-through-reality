# A (Mid)journey Through Reality: Assessing Accuracy, Impostor Bias, and Automation Bias in Human Detection of AI-Generated Images

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

This repository contains the dataset, stimulus images, analysis scripts, and figures for the paper **"A (Mid)journey Through Reality"** ([DOI: 10.1155/hbe2/9977058](https://doi.org/10.1155/hbe2/9977058)), published in *Human Behavior and Emerging Technologies* (2025).

## Overview

This dataset supports the study investigating whether people are able to distinguish real photographs from AI-generated images, and whether they are subject to *automation bias* when an algorithmic suggestion is provided, or *impostor bias* (systematic over-skepticism).

Through a mixed-methods study with 746 participants across 5 distinct experimental variants, we collected 11,170 individual judgments. See the paper for a full discussion of the results.

---

## ⚠️ Mandatory Citation 

**Unless otherwise noted, the stimulus images and CSV data in this repository are licensed under CC BY 4.0. Reuse, redistribution, and modification are permitted, provided that appropriate attribution is given, changes are indicated, and the following paper is cited:**

```bibtex
@article{https://doi.org/10.1155/hbe2/9977058,
author = {Casu, Mirko and Guarnera, Luca and Zangara, Ignazio and Caponnetto, Pasquale and Battiato, Sebastiano},
title = {A (Mid)journey Through Reality: Assessing Accuracy, Impostor Bias, and Automation Bias in Human Detection of AI-Generated Images},
journal = {Human Behavior and Emerging Technologies},
volume = {2025},
number = {1},
pages = {9977058},
keywords = {cognitive biases, cognitive psychology, deepfake detection, generative AI, impostor bias},
doi = {https://doi.org/10.1155/hbe2/9977058},
url = {https://onlinelibrary.wiley.com/doi/abs/10.1155/hbe2/9977058},
eprint = {https://onlinelibrary.wiley.com/doi/pdf/10.1155/hbe2/9977058},
year = {2025}
}
```

---

## Repository Structure

```
.
├── data/
│   ├── responses_task.csv           ← Processed data: one row per participant × image (11,170 rows)
│   ├── participants_demographics.csv← Demographics: one row per participant (746 rows)
│   ├── stimuli_manifest.csv         ← Metadata for every stimulus image
│   ├── statistical_analysis_results_with_effect_sizes.csv
│   ├── resnet/                      ← ResNet-50 predictions used in the study
│   └── raw/                         ← Original unprocessed questionnaire CSVs (Italian & English)
├── stimuli/                         ← The 75 stimulus images divided into 5 variants (alpha-epsilon)
├── gradcam/                         ← Grad-CAM visualizations comparing human vs model focus
├── code/                            ← Python scripts to reproduce the data processing pipeline
└── figures/                         ← Summary plots, boxplots, and demographic distributions
```

## Data Dictionary

### `data/responses_task.csv`
One row per *(participant × image)* observation — **11,170 rows** total (746 participants × 15 images each).

| Column                    | Description |
|---------------------------|-------------|
| `participant_id`          | Anonymous identifier `P0001`–`P0746` |
| `variant`                 | Questionnaire variant (`alpha`–`epsilon`) |
| `image_id`                | Foreign key to `stimuli_manifest.csv` |
| `ground_truth`            | `real` · `AI_midjourney` · `AI_magnific` |
| `initial_response`        | First judgment before algorithm: `real` or `AI` |
| `had_doubt`               | Self-reported uncertainty: `yes` / `no` |
| `ai_confidence_score`     | Simulated algorithm confidence (0–100 %) displayed to the participant |
| `post_suggestion_action`  | `confirm` (kept initial choice) or `change` (switched) |
| `effective_final_response`| Final answer after the suggestion: `real` or `AI` |

### `data/stimuli_manifest.csv`
One row per stimulus (75 total). Every variant contains exactly **5 real**, **5 AI_midjourney**, and **5 AI_magnific** images, fully counterbalanced across positions.

| Column               | Description |
|----------------------|-------------|
| `image_id`           | Unique identifier, format `{variant}_{order:02d}` (e.g. `alpha_01`) |
| `variant`            | Questionnaire variant: `alpha`, `beta`, `gamma`, `delta`, `epsilon` |
| `presentation_order` | Position in the questionnaire (1–15) |
| `filename`           | Original filename (e.g. `1_real.jpg`) |
| `ground_truth`       | `real` · `AI_midjourney` · `AI_magnific` |

### Participant Counts by Variant

| Variant | Name    | N participants |
|---------|---------|---------------|
| 1       | alpha   | 256 |
| 2       | beta    | 150 |
| 3       | gamma   | 142 |
| 4       | delta   | 106 |
| 5       | epsilon |  92 |
| **Total** |       | **746** |

---

## Stimulus Images (`stimuli/`)

Each subfolder (`alpha` through `epsilon`) contains exactly 15 JPEG files named `{presentation_order}_{type}.jpg`, where `{type}` encodes the ground truth:

| Suffix   | Meaning                                      | Tool / Source |
|----------|----------------------------------------------|---------------|
| `_real`  | Authentic photograph                         | Publicly licensed stock images |
| `_m`     | Synthetic image                              | Midjourney v6 |
| `_mm`    | Synthetic image (upscaled/enhanced)          | Midjourney v6 + Magnific AI |

All images depict human figures (portraits, groups, or scenes with people) so as to make the detection task ecologically plausible.

---

## Anonymisation Notes

- No names, email addresses, IP addresses, or precise timestamps are included in ANY dataset file.
- Free-text observation fields have been completely removed from all files.
- Age was collected as a categorical range.
- `academic_affiliation` is a normalised broad label.
- *Note: the files in `data/raw/` contain the original data exports, but have been fully stripped of personal data (timestamps, emails, and observations).*

---

## Contact

For questions about the dataset or code, please contact the corresponding authors (contact information available in the manuscript).