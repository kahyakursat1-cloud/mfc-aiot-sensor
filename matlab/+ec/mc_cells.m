function N = mc_cells(p_target, n, seed)
%MC_CELLS Cells needed for p_target with uncertain single-cell output and stack efficiency.
if nargin < 1, p_target = 150e-6; end
if nargin < 2, n = 20000; end
if nargin < 3, seed = 1; end
rng(seed, 'twister');
p_single = min(max(lognrnd(log(22e-6), 0.20, n, 1), 10e-6), 40e-6);
eta_stack = 0.65 + 0.25*rand(n, 1);
N = ceil(p_target./(p_single.*eta_stack));
end
