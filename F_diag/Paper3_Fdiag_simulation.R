library(MASS)
library(Matrix)

expit <- function(x) {
  1 / (1 + exp(-x))
}

trim_prob <- function(p, eps = 1e-8) {
  pmin(pmax(p, eps), 1 - eps)
}

sim_binary_iv <- function(n, p_z, r_min = 0.10, r_max = 0.20) {
  k <- length(p_z)
  
  R <- diag(1, k)
  if (k > 1) {
    idx <- upper.tri(R)
    R[idx] <- runif(sum(idx), min = r_min, max = r_max)
    R[lower.tri(R)] <- t(R)[lower.tri(R)]
  }
  
  R <- as.matrix(Matrix::nearPD(R, corr = TRUE)$mat)
  
  Z_latent <- MASS::mvrnorm(
    n = n,
    mu = rep(0, k),
    Sigma = R
  )
  
  cuts <- qnorm(1 - p_z)
  
  Z_mat <- sweep(Z_latent, 2, cuts, FUN = ">") * 1
  Z_mat <- matrix(Z_mat, nrow = n, ncol = k)
  colnames(Z_mat) <- paste0("Z", seq_len(k))
  
  Z_mat
}

get_first_stage_stats <- function(X, Z_mat) {
  dat <- data.frame(
    X = X,
    Z_mat,
    check.names = FALSE
  )
  
  k <- ncol(Z_mat)
  n <- nrow(dat)
  
  fit_full <- tryCatch(
    lm(
      as.formula(
        paste("X ~", paste(colnames(Z_mat), collapse = " + "))
      ),
      data = dat
    ),
    error = function(e) NULL
  )
  
  if (is.null(fit_full)) {
    return(data.frame(
      R2 = NA_real_,
      F_Lee_Burgess = NA_real_,
      F_anova = NA_real_
    ))
  }
  
  R2 <- tryCatch(
    summary(fit_full)$r.squared,
    error = function(e) NA_real_
  )
  
  F_Lee_Burgess <- ifelse(
    is.finite(R2) && R2 < 1,
    ((n - k - 1) / k) * (R2 / (1 - R2)),
    NA_real_
  )
  
  fit_null <- tryCatch(
    lm(X ~ 1, data = dat),
    error = function(e) NULL
  )
  
  F_anova <- tryCatch(
    if (!is.null(fit_null)) anova(fit_null, fit_full)$F[2] else NA_real_,
    error = function(e) NA_real_
  )
  
  data.frame(
    R2 = as.numeric(R2),
    F_Lee_Burgess = as.numeric(F_Lee_Burgess),
    F_anova = as.numeric(F_anova)
  )
}

sim_once <- function(n,
                     alpha_value,
                     c_x,
                     p_z,
                     sigma_u = 0.5,
                     a0 = 0,
                     r_min = 0.10,
                     r_max = 0.20,
                     seed = NULL) {
  
  if (!is.null(seed)) set.seed(seed)
  
  k <- length(p_z)
  a1 <- rep(alpha_value, k)
  
  Z_mat <- sim_binary_iv(
    n = n,
    p_z = p_z,
    r_min = r_min,
    r_max = r_max
  )
  
  U <- rnorm(n, mean = 0, sd = sigma_u)
  
  lin_x <- a0 + as.numeric(Z_mat %*% a1) + c_x * U
  p_x <- trim_prob(expit(lin_x))
  X <- rbinom(n, size = 1, prob = p_x)
  
  first_stage <- get_first_stage_stats(X = X, Z_mat = Z_mat)
  
  data.frame(
    first_stage,
    mean_X = mean(X),
    sd_X = sd(X),
    stringsAsFactors = FALSE
  )
}