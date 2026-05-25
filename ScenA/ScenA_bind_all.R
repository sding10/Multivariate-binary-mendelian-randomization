library(dplyr)
library(purrr)
library(readr)
library(tibble)

all_files <- list.files(
  path = "results",
  pattern = "^validate_A_allmethods_indepIV_sim[0-9]+\\.rds$",
  full.names = TRUE
)

cat("Total validation result files found:", length(all_files), "\n")

if (length(all_files) != 8000) {
  stop("Expected 8000 validation result files, but found ", length(all_files))
}

sim_res_all <- map_dfr(all_files, readRDS)

sim_res_all <- sim_res_all %>%
  mutate(
    bias = est - b1,
    cover = ifelse(
      conv == 1 & is.finite(lcl) & is.finite(ucl),
      as.numeric(lcl <= b1 & ucl >= b1),
      NA_real_
    ),
    reject = ifelse(
      conv == 1 & is.finite(p),
      as.numeric(p < 0.05),
      NA_real_
    ),
    method = factor(
      as.character(method),
      levels = c("2SPS", "2SRI", "GMM", "IV-MVB")
    )
  )

cat("\nRows by method and convergence:\n")
print(sim_res_all %>% count(method, conv, name = "n_rows"))

cat("\nRows by method:\n")
print(sim_res_all %>% count(method, name = "n_rows"))

cat("\nSimulation count check:\n")
print(sim_res_all %>% summarise(n_sims = n_distinct(sim)))

analysis_dat <- sim_res_all %>%
  filter(conv == 1, is.finite(bias))

summary_validate <- analysis_dat %>%
  group_by(method) %>%
  summarise(
    n_total = sum(sim_res_all$method == first(method), na.rm = TRUE),
    n_converged = n(),
    median_bias = median(bias, na.rm = TRUE),
    q1_bias = quantile(bias, 0.25, na.rm = TRUE),
    q3_bias = quantile(bias, 0.75, na.rm = TRUE),
    bias_text = sprintf("%.2f (%.2f, %.2f)", median_bias, q1_bias, q3_bias),
    coverage = mean(cover, na.rm = TRUE),
    type1_error = mean(reject, na.rm = TRUE),
    coverage_text = sprintf("%.1f%%", 100 * coverage),
    type1_text = sprintf("%.1f%%", 100 * type1_error),
    .groups = "drop"
  )

cat("\nValidation summary: Scenario A, Very Weak IVs, All Methods, Independent IVs\n")
print(summary_validate)

write_csv(sim_res_all, "validate_A_veryweak_allmethods_indepIV_8000_raw.csv")
write_csv(summary_validate, "validate_A_veryweak_allmethods_indepIV_8000_summary.csv")
saveRDS(sim_res_all, "validate_A_veryweak_allmethods_indepIV_8000_raw.rds")

cat("\nSaved:\n")
cat("validate_A_veryweak_allmethods_indepIV_8000_raw.csv\n")
cat("validate_A_veryweak_allmethods_indepIV_8000_summary.csv\n")
cat("validate_A_veryweak_allmethods_indepIV_8000_raw.rds\n")