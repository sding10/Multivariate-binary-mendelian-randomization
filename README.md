# Multivariate Binary Mendelian Randomization with Multiple Genetic Instruments

This repository contains the R code used for the simulation studies and real-data analysis described in the manuscript:

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

This repository provides the code used to evaluate instrumental variable methods for Mendelian randomization with binary exposures and binary outcomes.

The methods considered include:

* Two-Stage Predictor Substitution (2SPS)
* Two-Stage Residual Inclusion (2SRI)
* Generalized Method of Moments (GMM)
* Instrumental Variable Multivariate Binary (IV-MVB)

Performance was evaluated through extensive Monte Carlo simulation studies under varying:

* Instrument strength
* Number of genetic instruments
* Sample size
* Confounding strength
* Causal effect size

In addition to the simulation studies, this repository contains code used for the real-data analysis based on the REGARDS study dataset.

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

real_data_analysis/
└── 01_regards_real_data_analysis.R
```

## Script Descriptions

### Simulation Code

| Script                          | Description                                                                |
| ------------------------------- | -------------------------------------------------------------------------- |
| 01_scenario_definitions.R       | Defines simulation scenarios and parameter settings                        |
| 02_mrbinary_methods.R           | Implements the 2SPS, 2SRI, GMM, and IV-MVB estimators                      |
| 03_run_single_job.R             | Executes a single simulation replicate/job                                 |
| 04_simulation_engine.R          | Generates simulated datasets and runs simulation studies                   |
| 05_combine_simulation_results.R | Combines and summarizes simulation outputs                                 |
| 06_run_iv_number_experiment.R   | Performs sensitivity analyses varying the number of instrumental variables |
| 07_combine_iv_number_results.R  | Combines outputs from the IV-number sensitivity analyses                   |

### Real Data Analysis

| Script                          | Description                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------- |
| 01_regards_real_data_analysis.R | Performs the real-data Mendelian randomization analysis using the REGARDS dataset |

## Software Requirements

R version 4.0 or later.

Required packages include:

* dplyr
* tidyr
* purrr
* readr
* MASS
* Matrix

Additional packages may be required depending on the computing environment.

## Data Availability

The simulation code is fully available in this repository.

The REGARDS individual-level dataset is not included due to data-use restrictions and participant privacy protections. Authorized users with access to the REGARDS data should place the required dataset in a local data directory before running the real-data analysis script.

## Reproducibility

The scripts in this repository reproduce the simulation studies and real-data analyses described in the manuscript.

## Correspondence

For questions regarding the methodology or code, please contact:

Hemant K. Tiwari<br>
Email: htiwari@uab.edu<br>
Department of Biostatistics<br>
School of Public Health<br>
The University of Alabama at Birmingham
