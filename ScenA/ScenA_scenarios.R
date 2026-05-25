n_sim_final <- 1

scenario_validate <- "A"
methods_validate <- c("2SPS", "2SRI", "GMM", "IV-MVB")

n_validate <- 1000
b1_validate <- 0

a0_validate <- 0
b0_validate <- 0

c_x_validate <- 1.5
c_y_validate <- 1.5
sigma_u_validate <- 0.5

alpha_validate <- 0.05

J_main <- 15

p_z_15 <- c(
  rep(0.1, 5),
  rep(0.2, 5),
  rep(0.3, 5)
)

a1_validate <- rep(0.001, J_main)

strength_id_validate <- "very_weak_validation"
strength_label_validate <- "Very Weak IVs"
a1_value_validate <- 0.001

n_jobs_validate <- 8000