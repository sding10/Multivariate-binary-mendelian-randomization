
n_validate <- 1000
a0_validate <- 0
c_x_validate <- 1.5
sigma_u_validate <- 0.5

J_main <- 30

p_z_30 <- c(
  rep(0.1, 10),
  rep(0.2, 10),
  rep(0.3, 10)
)

r_min_validate <- 0.10
r_max_validate <- 0.20

alpha_grid <- c(
  0.100,
  0.150,
  0.200,
  0.250,
  0.300,
  0.350,
  0.400,
  0.450,
  0.500,
  0.600,
  0.700,
  0.800,
  0.900,
  1.000,
  1.200
)

alpha_settings <- data.frame(
  alpha_id = seq_along(alpha_grid),
  alpha_value = alpha_grid,
  stringsAsFactors = FALSE
)

n_sim_per_alpha <- 100

n_jobs_validate <- nrow(alpha_settings) * n_sim_per_alpha