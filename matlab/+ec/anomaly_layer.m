function A = anomaly_layer()
%ANOMALY_LAYER Isolation Forest of Section 4.8 on synthetic soil data: size, inference cost, and
%   hold-out comparison with a 3-sigma threshold rule. Training set: 1200 normal and 4 x 50 anomaly
%   samples (seed 0); independent hold-out: 200 normal and 4 x 50 anomaly samples (seed 99).
P = ec.params();
[Xa, ya] = gen_data(1200, 50, 0); [Xb, yb] = gen_data(200, 50, 99);
mu = mean(Xa); sd = std(Xa, 1);
Za = (Xa - mu)./sd; Zb = (Xb - mu)./sd;
rng(42, 'twister');
f = iforest(Za, 'NumLearners', 150, 'NumObservationsPerLearner', 256, 'ContaminationFraction', mean(ya));
[tfb, sb] = isanomaly(f, Zb);
w = warning('off', 'all'); T = struct(f).Trees; warning(w);
nTrees = numel(T); nInt = 0; nLeaf = 0; depthMax = 0; visits = zeros(size(Zb, 1), 1); hsum = zeros(size(Zb, 1), 1);
for k = 1:nTrees
    w = warning('off', 'all'); t = struct(T(k)); warning(w);
    [ni, nl, dm] = tree_size(t); nInt = nInt + ni; nLeaf = nLeaf + nl; depthMax = max(depthMax, dm);
    for i = 1:size(Zb, 1)
        [nv, h] = path_of(t, Zb(i, :)); visits(i) = visits(i) + nv; hsum(i) = hsum(i) + h;
    end
end
psi = 256; cpsi = 2*(log(psi - 1) + 0.5772156649) - 2*(psi - 1)/psi;
score_from_paths = 2.^(-(hsum/nTrees)/cpsi);
A.n_trees = nTrees; A.total_nodes = nInt + nLeaf; A.internal_nodes = nInt; A.leaves = nLeaf; A.max_depth = depthMax;
A.score_check_max_abs_diff = max(abs(score_from_paths - sb));
A.mean_node_visits_per_inference = mean(visits);
A.model_bytes_estimate = nInt*(1 + 4 + 2 + 2) + nLeaf*4;
A.cycles_per_node_assumed = 20;
A.inference_time_s = A.mean_node_visits_per_inference*20/240e6;
A.inference_energy_J = P.V_CC*P.I_ACT*A.inference_time_s;
A.holdout_isolation_forest = prf(yb, tfb);
A.holdout_threshold_z3 = prf(yb, any(abs(Zb) > 3, 2));
rng(42, 'twister');
cv = cvpartition(ya, 'KFold', 5, 'Stratify', true); f1 = zeros(5, 1);
for k = 1:5
    tr = training(cv, k); va = test(cv, k);
    m = iforest(Za(tr, :), 'NumLearners', 150, 'NumObservationsPerLearner', 256, 'ContaminationFraction', mean(ya(tr)));
    r = prf(ya(va), isanomaly(m, Za(va, :))); f1(k) = r.f1;
end
A.cv5_f1_mean = mean(f1); A.cv5_f1_std = std(f1, 1);
end

function [X, y] = gen_data(nNormal, nPer, seed)
rng(seed, 'twister');
c = @(x, lo, hi) min(max(x, lo), hi);
N = [c(normrnd(45, 10, nNormal, 1), 5, 95), c(normrnd(22, 5, nNormal, 1), -5, 50), ...
     c(normrnd(6.8, 0.5, nNormal, 1), 4, 10), c(exprnd(55, nNormal, 1), 0, 600)];
D = [c(normrnd(4, 1.5, nPer, 1), 0, 9), c(normrnd(40, 3, nPer, 1), 35, 55), ...
     c(normrnd(6.8, 0.5, nPer, 1), 4, 10), c(exprnd(55, nPer, 1), 0, 600)];
H = [c(normrnd(45, 10, nPer, 1), 5, 95), c(normrnd(22, 5, nPer, 1), -5, 50), ...
     c(normrnd(3.2, 0.3, nPer, 1), 0, 4.5), c(exprnd(55, nPer, 1), 0, 600)];
G = [c(normrnd(45, 10, nPer, 1), 5, 95), c(normrnd(22, 5, nPer, 1), -5, 50), ...
     c(normrnd(6.8, 0.5, nPer, 1), 4, 10), c(normrnd(900, 100, nPer, 1), 600, 3000)];
F = [c(normrnd(97, 2, nPer, 1), 92, 100), c(normrnd(22, 5, nPer, 1), -5, 50), ...
     c(normrnd(6.8, 0.5, nPer, 1), 4, 10), c(exprnd(55, nPer, 1), 0, 600)];
X = [N; D; H; G; F]; y = [false(nNormal, 1); true(4*nPer, 1)];
end

function [nInt, nLeaf, depthMax] = tree_size(t)
stack = [1 0]; nInt = 0; nLeaf = 0; depthMax = 0;
while ~isempty(stack)
    node = stack(end, 1); d = stack(end, 2); stack(end, :) = [];
    if t.Children(node, 1) > 0
        nInt = nInt + 1; stack = [stack; t.Children(node, 1) d + 1; t.Children(node, 2) d + 1]; %#ok<AGROW>
    else
        nLeaf = nLeaf + 1; depthMax = max(depthMax, d);
    end
end
end

function [nVisited, h] = path_of(t, x)
node = 1; nVisited = 1; d = 0;
while t.Children(node, 1) > 0
    if x(t.SplitVariable(node)) < t.Split{node}, node = t.Children(node, 1); else, node = t.Children(node, 2); end
    nVisited = nVisited + 1; d = d + 1;
end
n = t.NumObservations(node);
if n > 1, d = d + 2*(log(n - 1) + 0.5772156649) - 2*(n - 1)/n; end
h = d;
end

function r = prf(y, p)
y = logical(y(:)); p = logical(p(:));
tp = sum(p & y); fp = sum(p & ~y); fn = sum(~p & y);
r.precision = tp/max(1, tp + fp); r.recall = tp/max(1, tp + fn);
r.f1 = 2*r.precision*r.recall/max(1e-12, r.precision + r.recall);
end
