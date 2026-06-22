# Multivariate Binary Mendelian Randomization with Multiple Genetic Instruments

This repository contains the simulation code used for the manuscript:

**The Multivariate Binary Mendelian Randomization Method with Multiple Genetic Instruments**

## Authors

- Sandeep C. Vejandla*
- Mengchen Ding*
- Phillip H. Allman
- Inmaculada Aban
- Dustin Long
- Amit Patki
- Todd MacKenzie
- Marguerite Irvin
- Leslie Lange
- Ethan Lange
- Gary Cutter
- Hemant K. Tiwari

\* Contributed equally to this work.

## Overview

This repository provides the R code used to conduct the simulation studies evaluating instrumental variable methods for Mendelian randomization with binary exposures and binary outcomes.

Methods evaluated include:

- Two-Stage Predictor Substitution (2SPS)
- Two-Stage Residual Inclusion (2SRI)
- Generalized Method of Moments (GMM)
- Instrumental Variable Multivariate Binary (IV-MVB)

The simulation framework investigates estimator performance under varying:

- Instrument strength
- Number of genetic instruments
- Sample size
- Confounding strength
- Causal effect size

## Repository Structure

```text
simulation_code/
├── 01_scenario_definitions.R
├── 02_mrbinary_methods.R
├── 03_run_single_job.R
├── 04_simulation_engine.R
├── 05_combine_simulation_results.R
├── 06_run_iv_number_experiment.R
└── 07_combine_iv_number_results.R
```

### Script Descriptions

| Script | Description |
|----------|----------|
| 01_scenario_definitions.R | Defines simulation scenarios and parameter settings |
| 02_mrbinary_methods.R | Implements 2SPS, 2SRI, GMM, and IV-MVB estimators |
| 03_run_single_job.R | Executes a single simulation job |
| 04_simulation_engine.R | Generates simulated datasets and runs simulation studies |
| 05_combine_simulation_results.R | Combines and summarizes simulation outputs |
| 06_run_iv_number_experiment.R | Runs sensitivity analyses varying the number of instruments |
| 07_combine_iv_number_results.R | Combines results from IV-number sensitivity analyses |

## Software Requirements

R (version 4.0 or higher)

Required packages include:

- dplyr
- tidyr
- purrr
- readr
- MASS
- Matrix
- AER
- stats

## Reproducibility

The scripts in this repository were used to generate the simulation results reported in the manuscript.

Additional scripts used to generate manuscript figures and tables may be added as the manuscript revision process is finalized.

## Contact

For questions regarding the methodology or code, please contact the corresponding author.

Hemant K. Tiwari  
Department of Biostatistics  
University of Alabama at Birmingham
