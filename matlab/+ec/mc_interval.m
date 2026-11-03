function [dt, nInfeasible] = mc_interval(n, seed)
%MC_INTERVAL Monte Carlo of the realistic lean interval (h) over physical distributions.
%   Same distributions as energy_chain.mc_interval: lognormal P_MFC, triangular t_active,
%   eta_PMIC = eta_boost*eta_buck with eta_boost = 0.71 + 0.25*Beta(5,2) and eta_buck = 0.86 + 0.07*Beta(4,3)
%   (mean 0.80, at most 0.89, so the boost stage never exceeds unity), lognormal quiescent and leakage,
%   normal sleep floor.
if nargin < 1, n = 20000; end
if nargin < 2, seed = 42; end
P = ec.params();
rng(seed, 'twister');
tri = makedist('Triangular', 'a', 1.5, 'b', 2.0, 'c', 3.0);
p_mfc = clip(lognrnd(log(150e-6), 0.20, n, 1), 80e-6, 400e-6);
t_act = clip(random(tri, n, 1), 1.5, 3.0);
eta   = (0.71 + 0.25*betarnd(5, 2, n, 1)).*(0.86 + 0.07*betarnd(4, 3, n, 1));
pq    = clip(lognrnd(log(1.6e-6), 0.3, n, 1), 0.5e-6, 5e-6);
pleak = clip(lognrnd(log(5e-6), 0.5, n, 1), 1e-6, 25e-6);
floorP = clip(normrnd(33e-6, 3e-6, n, 1), 25e-6, 40e-6);
e_ev = P.V_CC*(P.I_ACT*t_act + P.I_SENS*t_act) + P.E_TX;
pn = eta.*p_mfc - floorP - pq - pleak;
nInfeasible = sum(pn <= 0);
dt = e_ev(pn > 0)./pn(pn > 0)/3600;
end

function y = clip(x, lo, hi)
y = min(max(x, lo), hi);
end
