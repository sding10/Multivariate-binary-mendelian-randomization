library(dplyr)
library(purrr)
library(readr)
library(tibble)

source("Paper3_Fdiag_scenarios.R")

all_files <- list.files(
  path = "results",
  pattern = "^Fdiag_alpha[0-9]+_sim[0-9]+\\.rds$",
  full.names = TRUE
)

cat("Total F-diagnostic result files found:", length(all_files), "\n")

if (length(all_files) != n_jobs_validate) {
  stop("Expected ", n_jobs_validate, " F-diagnostic result files, but found ", length(all_files))
}

f_res_all <- map_dfr(all_files, readRDS)

cat("\nRows by alpha value:\n")
print(
  f_res_all %>%
    count(alpha_id, alpha_value, name = "n_rows") %>%
    arrange(alpha_id)
)

bad_counts <- f_res_all %>%
  count(alpha_id, alpha_value, name = "n_rows") %>%
  filter(n_rows != n_sim_per_alpha)

if (nrow(bad_counts) > 0) {
  warning("Some alpha settings do not have the expected number of simulations:")
  print(bad_counts)
}

f_summary <- f_res_all %>%
  group_by(alpha_id, alpha_value, n, n_iv, c_x, sigma_u) %>%
  summarise(
    n_sim = n(),
    
    n_finite_R2 = sum(is.finite(R2)),
    median_R2 = median(R2, na.rm = TRUE),
    q1_R2 = quantile(R2, 0.25, na.rm = TRUE),
    q3_R2 = quantile(R2, 0.75, na.rm = TRUE),
    
    n_finite_F_Lee_Burgess = sum(is.finite(F_Lee_Burgess)),
    median_F_Lee_Burgess = median(F_Lee_Burgess, na.rm = TRUE),
    q1_F_Lee_Burgess = quantile(F_Lee_Burgess, 0.25, na.rm = TRUE),
    q3_F_Lee_Burgess = quantile(F_Lee_Burgess, 0.75, na.rm = TRUE),
    min_F_Lee_Burgess = min(F_Lee_Burgess, na.rm = TRUE),
    max_F_Lee_Burgess = max(F_Lee_Burgess, na.rm = TRUE),
    
    n_finite_F_anova = sum(is.finite(F_anova)),
    median_F_anova = median(F_anova, na.rm = TRUE),
    q1_F_anova = quantile(F_anova, 0.25, na.rm = TRUE),
    q3_F_anova = quantile(F_anova, 0.75, na.rm = TRUE),
    
    mean_X = mean(mean_X, na.rm = TRUE),
    sd_X = mean(sd_X, na.rm = TRUE),
    
    F_Lee_Burgess_text = sprintf(
      "%.2f (%.2f, %.2f)",
      median_F_Lee_Burgess,
      q1_F_Lee_Burgess,
      q3_F_Lee_Burgess
    ),
    
    F_anova_text = sprintf(
      "%.2f (%.2f, %.2f)",
      median_F_anova,
      q1_F_anova,
      q3_F_anova
    ),
    
    R2_text = sprintf(
      "%.4f (%.4f, %.4f)",
      median_R2,
      q1_R2,
      q3_R2
    ),
    
    F_category = case_when(
      median_F_Lee_Burgess < 10 ~ "Weak",
      median_F_Lee_Burgess >= 10 & median_F_Lee_Burgess <= 30 ~ "Moderate",
      median_F_Lee_Burgess > 30 & median_F_Lee_Burgess <= 100 ~ "Strong",
      median_F_Lee_Burgess > 100 ~ "Very strong",
      TRUE ~ NA_character_
    ),
    
    .groups = "drop"
  ) %>%
  arrange(alpha_id)

cat("\nF-statistic summary using Lee/Burgess R2-based formula:\n")
print(f_summary)

write_csv(f_res_all, "Fdiag_LeeBurgess_30IV_raw.csv")
write_csv(f_summary, "Fdiag_LeeBurgess_30IV_summary.csv")
saveRDS(f_res_all, "Fdiag_LeeBurgess_30IV_raw.rds")

