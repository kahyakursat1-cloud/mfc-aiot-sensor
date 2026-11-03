function S = sobol_seed_stability(seeds, n)
%SOBOL_SEED_STABILITY Total-effect Sobol index of harvested power over several seeds, computed on
%   the reporting rate r* (Eq. 11) and on the interval dt = 24/r* (h). dt diverges as P_net -> 0,
%   so a few near-infeasible draws dominate its variance and its indices move between seeds.
if nargin < 1, seeds = 1:8; end
if nargin < 2, n = 65536; end
P = ec.params();
st_rate = zeros(numel(seeds), 1); st_dt = st_rate;
for k = 1:numel(seeds)
    rng(seeds(k), 'twister');
    A = ec.sample_inputs(n); B = ec.sample_inputs(n);
    AB = A; AB(:, 1) = B(:, 1);
    r = @(X) (X(:, 3).*X(:, 1) - X(:, 6) - 1.6e-6 - X(:, 4))./(P.V_CC*(P.I_ACT*X(:, 2) + P.I_SENS*X(:, 2).*X(:, 5)) + P.E_TX)*86400;
    rA = r(A); rB = r(B); rAB = r(AB);
    st_rate(k) = 0.5*mean((rA - rAB).^2)/var([rA; rB], 1);
    dA = 24./rA; dB = 24./rB; dAB = 24./rAB;
    st_dt(k) = 0.5*mean((dA - dAB).^2)/var([dA; dB], 1);
end
S = struct('seeds', seeds, 'st_rate', st_rate, 'st_dt', st_dt, ...
    'st_rate_range', [min(st_rate) max(st_rate)], 'st_dt_range', [min(st_dt) max(st_dt)]);
end
