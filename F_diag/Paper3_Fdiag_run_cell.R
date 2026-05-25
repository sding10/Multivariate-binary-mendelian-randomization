source("Paper3_Fdiag_simulation.R")
source("Paper3_Fdiag_scenarios.R")

args <- commandArgs(trailingOnly = TRUE)

job_id <- as.integer(args[1])

if (is.na(job_id)) {
  stop("Please provide a job ID, e.g., Rscript Paper3_Fdiag_run_cell.R 1")
}

if (job_id < 1 || job_id > n_jobs_validate) {
  stop("job_id must be between 1 and ", n_jobs_validate)
}

alpha_id <- ceiling(job_id / n_sim_per_alpha)

sim_within_alpha <- ((job_id - 1) %% n_sim_per_alpha) + 1

alpha_row <- alpha_settings[alpha_id, ]

seed_use <- 200000 + job_id

tmp <- sim_once(
  n = n_validate,
  alpha_value = alpha_row$alpha_value,
  c_x = c_x_validate,
  p_z = p_z_30,
  sigma_u = sigma_u_validate,
  a0 = a0_validate,
  r_min = r_min_validate,
  r_max = r_max_validate,
  seed = seed_use
)

tmp$job_id <- job_id
tmp$alpha_id <- alpha_row$alpha_id
tmp$alpha_value <- alpha_row$alpha_value
tmp$sim_within_alpha <- sim_within_alpha

tmp$n <- n_validate
tmp$c_x <- c_x_validate
tmp$sigma_u <- sigma_u_validate

tmp$n_iv <- J_main

tmp$p_z_pattern <- "pZ_0.1x10_0.2x10_0.3x10"

tmp$iv_corr <- "random_r_0.10_to_0.20"

tmp$analysis_type <- "Lee_Burgess_F_diagnostic"

out_file <- sprintf(
  "results/Fdiag_alpha%02d_sim%04d.rds",
  alpha_row$alpha_id,
  sim_within_alpha
)

saveRDS(tmp, out_file)

message("Saved: ", out_file)
