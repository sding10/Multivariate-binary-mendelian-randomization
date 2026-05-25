library(MASS)
library(Matrix)
library(dplyr)

sim_binary_iv <- function(n, p_z) {
  k <- length(p_z)
  
  Z_mat <- sapply(seq_len(k), function(j) {
    rbinom(n, size = 1, prob = p_z[j])
  })
  
  Z_mat <- matrix(Z_mat, nrow = n, ncol = k)
  colnames(Z_mat) <- paste0("Z", seq_len(k))
  
  Z_mat
}

make_fail_row <- function(method) {
  data.frame(
    method = method,
    est = NA_real_,
    se = NA_real_,
    lcl = NA_real_,
    ucl = NA_real_,
    z = NA_real_,
    p = NA_real_,
    conv = 0,
    stringsAsFactors = FALSE
  )
}

clean_fit_row <- function(fit, method) {
  if (is.null(fit)) {
    return(make_fail_row(method))
  }
  
  out <- as.data.frame(as.list(fit), stringsAsFactors = FALSE)
  
  if (!("method" %in% names(out))) {
    out$method <- method
  }
  
  keep_cols <- c("method", "est", "se", "lcl", "ucl", "z", "p", "conv")
  
  for (v in setdiff(keep_cols, names(out))) {
    out[[v]] <- if (v == "method") method else NA_real_
  }
  
  out <- out[, keep_cols, drop = FALSE]
  
  num_cols <- c("est", "se", "lcl", "ucl", "z", "p", "conv")
  for (v in num_cols) {
    out[[v]] <- as.numeric(out[[v]])
  }
  
  out$method <- as.character(out$method)
  out
}

sim_once <- function(n,
                     a1,
                     b1,
                     c_x,
                     c_y,
                     p_z,
                     sigma_u = 0.5,
                     a0 = 0,
                     b0 = 0,
                     seed = NULL,
                     alpha = 0.05) {
  
  if (!is.null(seed)) set.seed(seed)
  
  k <- length(a1)
  
  if (length(p_z) == 1) {
    p_z <- rep(p_z, k)
  }
  
  if (length(p_z) != k) {
    stop("Length of p_z must be 1 or equal to length(a1).")
  }
  
  Z_mat <- sim_binary_iv(
    n = n,
    p_z = p_z
  )
  
  U <- rnorm(n, mean = 0, sd = sigma_u)
  
  lin_x <- a0 + as.numeric(Z_mat %*% a1) + c_x * U
  p_x <- trim_prob(expit(lin_x))
  X <- rbinom(n, size = 1, prob = p_x)
  
  lin_y <- b0 + b1 * X + c_y * U
  p_y <- trim_prob(expit(lin_y))
  Y <- rbinom(n, size = 1, prob = p_y)
  
  dat <- data.frame(
    X = X,
    Y = Y,
    U = U,
    Z_mat,
    check.names = FALSE
  )
  
  z_names <- colnames(Z_mat)
  mr_dat <- dat[, c(z_names, "X", "Y"), drop = FALSE]
  
  fit_2sps <- tryCatch(
    est_2sps(
      dat = mr_dat,
      z = z_names,
      x = "X",
      y = "Y",
      alpha = alpha
    ),
    error = function(e) NULL
  )
  
  fit_2sri <- tryCatch(
    est_2sri(
      dat = mr_dat,
      z = z_names,
      x = "X",
      y = "Y",
      alpha = alpha
    ),
    error = function(e) NULL
  )
  
  fit_gmm <- tryCatch(
    est_gmm(
      dat = mr_dat,
      z = z_names,
      x = "X",
      y = "Y",
      alpha = alpha
    ),
    error = function(e) NULL
  )
  
  fit_ivmvb <- tryCatch(
    est_ivmvb(
      dat = mr_dat,
      z = z_names,
      x = "X",
      y = "Y",
      alpha = alpha
    ),
    error = function(e) NULL
  )
  
  bind_rows(
    clean_fit_row(fit_2sps, "2SPS"),
    clean_fit_row(fit_2sri, "2SRI"),
    clean_fit_row(fit_gmm, "GMM"),
    clean_fit_row(fit_ivmvb, "IV-MVB")
  )
}