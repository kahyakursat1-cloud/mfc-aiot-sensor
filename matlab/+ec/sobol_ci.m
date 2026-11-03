function T = sobol_ci(n, nBoot, seed)
%SOBOL_CI Saltelli first-order (S1) and total-effect (ST) indices of the realistic lean
%   reporting rate r* = P_net/E_event (reports/day, Eq. 11) over six loss-aware inputs,
%   with bootstrap 95% confidence intervals. The interval 1/r* is singular as P_net -> 0,
%   which makes its variance-based indices seed-dependent; the rate is not.
%   Estimators as in energy_chain.sobol_ci: S1 = mean(yB.*(yAB-yA))/V, ST = mean((yA-yAB).^2)/(2V).
if nargin < 1, n = 65536; end
if nargin < 2, nBoot = 400; end
if nargin < 3, seed = 1; end
rng(seed, 'twister');
A = ec.sample_inputs(n); B = ec.sample_inputs(n);
yA = model(A); yB = model(B);
names = {'Harvested power'; 'Active duration'; 'PMIC efficiency'; ...
         'Supercap leakage'; 'Sensor current'; 'Sleep floor'};
k = numel(names);
S1 = zeros(k, 1); S1lo = S1; S1hi = S1; ST = S1; STlo = S1; SThi = S1;
for i = 1:k
    AB = A; AB(:, i) = B(:, i);
    yAB = model(AB);
    [S1(i), ST(i)] = indices(yA, yB, yAB);
    b1 = zeros(nBoot, 1); b2 = b1;
    for r = 1:nBoot
        idx = randi(n, n, 1);
        [b1(r), b2(r)] = indices(yA(idx), yB(idx), yAB(idx));
    end
    S1lo(i) = prctile(b1, 2.5); S1hi(i) = prctile(b1, 97.5);
    STlo(i) = prctile(b2, 2.5); SThi(i) = prctile(b2, 97.5);
end
T = table(names, S1, S1lo, S1hi, ST, STlo, SThi, 'VariableNames', ...
          {'name', 'S1', 'S1_lo', 'S1_hi', 'ST', 'ST_lo', 'ST_hi'});
end

function y = model(X)
P = ec.params();
e = P.V_CC*(P.I_ACT*X(:, 2) + P.I_SENS*X(:, 2).*X(:, 5)) + P.E_TX;
y = (X(:, 3).*X(:, 1) - X(:, 6) - 1.6e-6 - X(:, 4))./e*86400;
end

function [s1, st] = indices(a, b, ab)
vy = var([a; b], 1);
s1 = max(mean(b.*(ab - a))/vy, 0);
st = 0.5*mean((a - ab).^2)/vy;
end
