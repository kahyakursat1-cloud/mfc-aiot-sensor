% run_all.m
% =========================================================================
% MATLAB implementation of the loss-aware energy-chain framework (package +ec).
% Computes every headline number, prints it next to the Python value from
% python_reference.json [in brackets], and writes matlab_results.json.
% Requires: Statistics and Machine Learning Toolbox (lognrnd, betarnd, makedist).
% Run:  >> run_all          Tests:  >> run_tests
% =========================================================================
here = fileparts(mfilename('fullpath'));
addpath(here);
ref = jsondecode(fileread(fullfile(here, 'python_reference.json')));
tic; R = ec.compute_all(); elapsed = toc;

cs = {'ideal', 'realistic', 'conservative'};
fprintf('MATLAB %s  (%.1f s)\n\n', version, elapsed);
fprintf('==== per-event energy (J) ====\n');
for p = {'lean', 'lowgas', 'mq135'}
    fprintf('  %-7s %.4f [%.4f]\n', p{1}, R.e_event_J.(p{1}), ref.e_event_J.(p{1}));
end
fprintf('\n==== sustainable interval @150 uW (h), Eq. 7 ====\n');
for p = {'lean', 'lowgas', 'mq135'}
    fprintf('  %-7s', p{1});
    for i = 1:3
        fprintf('  %s %.2f [%.2f]', cs{i}(1:4), R.interval_150uW_h.(p{1}).(cs{i}), ref.interval_150uW_h.(p{1}).(cs{i}));
    end
    fprintf('\n');
end
fprintf('\n==== net power, daily energy, 10-min deficit ====\n');
for i = 1:3
    fprintf('  %-12s P_net %.1f uW [%.1f]   net %.2f J/day [%.2f]   deficit %.1fx [%.1fx]\n', cs{i}, ...
        R.p_net_150uW_W.(cs{i})*1e6, ref.p_net_150uW_W.(cs{i})*1e6, R.daily_J.(['net_' cs{i}]), ...
        ref.daily_J.(['net_' cs{i}]), R.deficit_10min_x.(cs{i}), ref.deficit_10min_x.(cs{i}));
end
fprintf('\n==== cells (Eq. 13) ====\n  N* for dt = %s h: %s [%s]\n', mat2str(round(R.cells_vs_interval.dt_h, 3)), ...
    mat2str(R.cells_vs_interval.N), mat2str(ref.cells_vs_interval.N'));
fprintf('  150 uW: deterministic %d [%d]; MC median %g, 5-95%% [%g, %g]  [%g, %g-%g]\n', R.cells_150uW_det, ...
    ref.cells_150uW_det, R.cells_150uW_mc.median, R.cells_150uW_mc.p5, R.cells_150uW_mc.p95, ...
    ref.cells_150uW_mc.median, ref.cells_150uW_mc.p5, ref.cells_150uW_mc.p95);
fprintf('  R_ESR,max = %.2f ohm [%.2f]\n', R.esr_max_ohm, ref.esr_max_ohm);
m = R.mc_interval; r = ref.mc_interval;
fprintf('\n==== Monte Carlo, realistic lean (N = %d) ====\n', m.n);
fprintf('  median %.2f h [%.2f]   5-95%% [%.2f, %.2f] [%.2f, %.2f]\n', m.median_h, r.median_h, m.p5_h, m.p95_h, r.p5_h, r.p95_h);
fprintf('  P(dt<2 h) %.3f [%.3f]   sub-hour %d [%d]   min %.2f h [%.2f]   infeasible %d [%d]\n', ...
    m.frac_sub2h, r.frac_sub2h, m.n_sub1h, r.n_sub1h, m.min_h, r.min_h, m.n_infeasible, r.n_infeasible);
fprintf('\n==== Sobol (Saltelli N = 32768, bootstrap 95%% CI) ====\n');
for i = 1:numel(R.sobol)
    s = R.sobol(i); q = ref.sobol(i);
    fprintf('  %-17s S1 %.3f [%.2f, %.2f] {%.3f}   ST %.3f [%.2f, %.2f] {%.3f}\n', s.name, s.S1, s.S1_lo, ...
        s.S1_hi, q.S1, s.ST, s.ST_lo, s.ST_hi, q.ST);
end
fprintf('  sum S1 = %.3f {%.3f}   (braces: Python)\n', sum([R.sobol.S1]), sum([ref.sobol.S1]));
fprintf('\n==== dynamic scenario, Algorithm 2 ====\n');
for k = 1:2
    d = R.dynamic(k); q = ref.dynamic(k);
    fprintf('  wake %.2f h: transmit %d [%d], measure %d [%d], sleep %d [%d], anomaly %d [%d]; V %.2f-%.2f [%.2f-%.2f]; SoC %.2f-%.2f\n', ...
        d.wake_h, d.n_transmit, q.n_transmit, d.n_measure, q.n_measure, d.n_sleep, q.n_sleep, ...
        d.n_anomaly, q.n_anomaly, d.v_min, d.v_max, q.v_min, q.v_max, d.soc_min, d.soc_max);
end

R.matlab_version = version;
fid = fopen(fullfile(here, 'matlab_results.json'), 'w');
fprintf(fid, '%s', jsonencode(R, 'PrettyPrint', true));
fclose(fid);
fprintf('\nwrote matlab_results.json\n');
