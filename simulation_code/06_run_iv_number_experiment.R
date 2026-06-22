source("simulation_code/02_mrbinary_methods.R")
source("simulation_code/04_simulation_engine.R")
source("simulation_code/01_scenario_definitions.R")

args <- commandArgs(trailingOnly = TRUE)

cell_id <- as.integer(args[1])

ivnum_grid <- c(1, 5, 10, 15, 20, 25, 30)
n_iv_cell <- ivnum_grid[cell_id]

if (is.na(n_iv_cell)) {
  stop("cell_id must be 1, 2, 3, 4, 5, 6, or 7.")
}

dir.create("results_ivnum_weak", showWarnings = FALSE)

res_ivnum <- run_sim(
  n_sim = n_sim_final,
  n = 1000,
  b1 = 1,
  iv_strength = "weak",
  c_x = 1.5,
  c_y = 1.5,
  n_iv = n_iv_cell,
  pz = rep(0.3, n_iv_cell),
  sigma_u = sigma_u,
  alpha0 = alpha0,
  beta0 = beta0,
  r_min = r_min,
  r_max = r_max,
  scenario = "NumIV",
  setting_id = cell_id,
  seed_base = 9100 + 100000 * cell_id,
  ci_alpha = ci_alpha
)

res_ivnum <- res_ivnum %>%
  dplyr::mutate(
    pz_pattern = "pz_0.3_all",
    method_version = "constant_theta_ivmvb_F_inside_2SPS",
    figure2_setting = "Scenario B, weak IVs, b1=1, n=1000, c_x=c_y=1.5"
  )

out_file <- sprintf(
  "results_ivnum_weak/NumIV_Weak_%02dIV_%dsim.rds",
  n_iv_cell,
  n_sim_final
)

saveRDS(res_ivnum, out_file)