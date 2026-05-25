source("Paper3_methods_noF.R")
source("Paper3_simulation_noF.R")
source("Paper3_scenarios_noF.R")

args <- commandArgs(trailingOnly = TRUE)

sim_id <- as.integer(args[1])

if (is.na(sim_id)) {
  stop("Please provide a simulation ID, e.g., Rscript Paper3_run_cell.R 1")
}

if (sim_id < 1 || sim_id > n_jobs_validate) {
  stop("sim_id must be between 1 and ", n_jobs_validate)
}

seed_use <- 100000 + sim_id

tmp <- sim_once(
  n = n_validate,
  a1 = a1_validate,
  b1 = b1_validate,
  c_x = c_x_validate,
  c_y = c_y_validate,
  p_z = p_z_15,
  sigma_u = sigma_u_validate,
  a0 = a0_validate,
  b0 = b0_validate,
  seed = seed_use,
  alpha = alpha_validate
)

tmp$sim <- sim_id
tmp$scen <- scenario_validate
tmp$n <- n_validate
tmp$b1 <- b1_validate
tmp$c_x <- c_x_validate
tmp$c_y <- c_y_validate
tmp$sigma_u <- sigma_u_validate
tmp$strength_id <- strength_id_validate
tmp$strength_label <- strength_label_validate
tmp$a1_value <- a1_value_validate
tmp$n_iv <- J_main
tmp$p_z_pattern <- "pZ_0.1x5_0.2x5_0.3x5"
tmp$iv_corr <- "independent"
tmp$method_version <- "ScenarioA_validation_all_methods_independent_IVs"

out_file <- sprintf(
  "results/validate_A_allmethods_indepIV_sim%04d.rds",
  sim_id
)

saveRDS(tmp, out_file)

message("Saved: ", out_file)
