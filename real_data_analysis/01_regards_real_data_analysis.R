library(dplyr)
library(readr)

source("simulation_code/02_mrbinary_methods.R")

# Note: REGARDS individual-level data are not included in this repository.
# Place the complete-case REGARDS analysis file in the data/ folder before running.
mr_data_cc <- read_csv("data/REGARDS_black_HT_anyStroke_final15IV_completecase.csv")

final_snps <- setdiff(
  names(mr_data_cc),
  c("FID", "HTmeds", "anystroke")
)

table(mr_data_cc$HTmeds, useNA = "ifany")
table(mr_data_cc$anystroke, useNA = "ifany")

lapply(mr_data_cc[, final_snps], function(x) sort(unique(x)))

regards_res <- MRbinary(
  dat = mr_data_cc,
  z = final_snps,
  x = "HTmeds",
  y = "anystroke",
  alpha = 0.05,
  maxit = 1000
)

print(regards_res$summary)

dir.create("real_data_results", showWarnings = FALSE)

write_csv(
  regards_res$summary,
  "real_data_results/REGARDS_realdata_results.csv"
)