# Surgical-TSplineGS / ZT-GS default config
# Based on paper: ZT_GS.pdf Sec IV-A Implementation Details

# Dataset
dataset_type = "surgical"
depth_type = "depth"

# Model - ZSTF (Zernike Spectral Trajectory Field), paper Sec. III-A / IV-A
zernike_N = 6                          # max radial order N (paper: N=6, M=(N+1)^2=49 modes)
zernike_omega = 4.0                    # temporal winding number omega (paper: omega=4)
zernike_beta = 0.5                     # exponential decay beta (paper: beta=0.5)
control_num = 6                        # legacy alias, interpreted as N by GaussianModel
deform_spatial_scale = 1e-2
prune_error_threshold = 0.5
sh_degree = 3

# Pose network (same as base Surgical-TSplineGS)
timebase_pe = 10
timenet_width = 256
timenet_output = 6
pixel_base_pe = 5

# Training
iterations = 30000
coarse_iterations = 2000               # warm-up: 2k iterations
static_iterations = 2000
position_lr_init = 0.00016
position_lr_final = 0.000016
position_lr_max_steps = 30000
pose_lr_init = 0.0005
pose_lr_final = 0.00005
feature_lr = 0.0025
opacity_lr = 0.05
scaling_lr = 0.005
rotation_lr = 0.001
omega_lr = 0.0001
rgb_lr = 0.0001

# Loss weights (paper Eq. 8)
lambda_dssim = 0.2                    # lambda_ssim
w_depth = 0.5                         # part of lambda_depth
w_mask = 1.0
w_track = 1.0
w_normal = 0

# ZT-GS hyperparameters
tass_epsilon = 0.15                   # epsilon_entropy: spectral-entropy rupture threshold (Sec. IV-A)
tass_gamma = 2.0                      # gamma: MG-TPC gradient scaling (Eq. 4)
tass_nlow = 2                         # N_low: low/high frequency boundary for bifurcation (Eq. 7)
mgtpc_tau0 = 0.01                     # tau_0: spectral-order gradient gate base (Eq. 4)
mgmas_enabled = True                  # enable MG-TPC (legacy alias name kept)
tass_enabled = True
lambda_depth_consistency = 0.5        # lambda_depth (Eq. 11)
lambda_traj_smoothness = 0.01         # lambda_sparse: spectral sparsity (Eq. 8)
lambda_masked_rgb = 1.0               # lambda_rgb (Eq. 9)

# Cyclic Spatio-Temporal Evolution Paradigm (Eq. 12)
cyclic_st_enabled = True              # forward+backward traversal, bidirectional grad accumulation
cyclic_accum_steps = 2                # # of grads (forward+backward) accumulated per update

# Densification
densify_from_iter = 500
densify_until_iter = 15000
densification_interval = 100
densify_grad_threshold = 0.0008
densify_grad_threshold_dynamic = 0.00008
opacity_reset_interval = 3000
densify = 1
desicnt = 6
opthr = 0.005

# Initial points (reduced for memory-constrained GPU)
stat_npts = 10000
dyn_npts = 10000
