library(dplyr)

library(purrr)

library(readr)


dir.create("results_ivmvb_combined", showWarnings = FALSE)



files <- list.files(

  "results_ivnum_weak",

  pattern = "\\.rds$",

  full.names = TRUE

)

print(basename(files))



if (length(files) != 7) {

  stop("Expected 7 weak-IV NumIV result files, but found ", length(files))

}



numiv_weak_raw <- purrr::map_dfr(files, readRDS)

print(dim(numiv_weak_raw))


print(numiv_weak_raw %>% count(n_iv, method))


print(numiv_weak_raw %>% summarise(

  n_unique_b1 = n_distinct(b1),

  b1 = unique(b1)[1],

  n_unique_n = n_distinct(n),

  n = unique(n)[1],

  n_unique_cx = n_distinct(c_x),

  c_x = unique(c_x)[1],

  n_unique_cy = n_distinct(c_y),

  c_y = unique(c_y)[1],

  iv_strength = unique(iv_strength)[1]

))



numiv_weak_summary <- numiv_weak_raw %>%

  filter(conv == 1, is.finite(bias)) %>%

  group_by(n_iv, method) %>%

  summarise(

    n_sim = n(),

    min_bias = min(bias, na.rm = TRUE),

    q1_bias = quantile(bias, 0.25, na.rm = TRUE),

    median_bias = median(bias, na.rm = TRUE),

    q3_bias = quantile(bias, 0.75, na.rm = TRUE),

    max_bias = max(bias, na.rm = TRUE),

    mean_bias = mean(bias, na.rm = TRUE),

    mean_abs_bias = mean(abs(bias), na.rm = TRUE),

    sd_bias = sd(bias, na.rm = TRUE),

    coverage = mean(cover, na.rm = TRUE),

    power = mean(reject, na.rm = TRUE),

    .groups = "drop"

  ) %>%

  arrange(n_iv, factor(method, levels = c("2SPS", "2SRI", "GMM", "IV-MVB")))



saveRDS(

  numiv_weak_raw,

  "results_ivnum_weak_combined/NumIV_Weak_raw.rds"

)



saveRDS(

  numiv_weak_summary,

  "results_combined/NumIV_Weak_summary.rds"

)



write_csv(

  numiv_weak_raw,

  "results__combined/NumIV_Weak_raw.csv"

)



write_csv(

  numiv_weak_summary,

  "results_ivnum_weak_combined/NumIV_Weak_summary.csv"

)
