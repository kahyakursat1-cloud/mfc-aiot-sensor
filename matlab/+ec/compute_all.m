function R = compute_all()
%COMPUTE_ALL Every headline number of the framework, in the field layout of
%   python_reference.json, so the two implementations can be compared field by field.
P = ec.params();
cs = {'ideal', 'realistic', 'conservative'};
pls = {'lean', 'lowgas', 'sgp30', 'mq135'};
El = ec.e_event('lean'); Ef = ec.e_event('mq135');

for j = 1:numel(pls), R.e_event_J.(pls{j}) = ec.e_event(pls{j}); end
R.e_tx_J = P.E_TX;
R.p_floor_W = P.P_FLOOR;
for i = 1:3, R.p_net_150uW_W.(cs{i}) = ec.p_net(150e-6, cs{i}); end
for j = 1:numel(pls)
    for i = 1:3, R.interval_150uW_h.(pls{j}).(cs{i}) = ec.interval_h(pls{j}, 150e-6, cs{i}); end
end
demand = 144*El;
for i = 1:3, R.deficit_10min_x.(cs{i}) = demand/(ec.p_net(150e-6, cs{i})*86400); end
R.daily_J.harvest = 150e-6*86400;
for i = 1:3, R.daily_J.(['net_' cs{i}]) = ec.p_net(150e-6, cs{i})*86400; end
R.daily_J.demand_10min = demand;
R.zheng_41uW.ideal_h = ec.interval_h('lean', 41e-6, 'ideal');
R.zheng_41uW.pnet_realistic_W = ec.p_net(41e-6, 'realistic');

dts = [12 6 3 1 0.5 1/6];
R.cells_vs_interval.dt_h = dts;
R.cells_vs_interval.N = ceil((P.P_FLOOR + El./(dts*3600) + 1.6e-6 + 5e-6)/(0.80*0.75*22e-6));
R.cells_150uW_det = ceil(150e-6/(22e-6*0.75));
N = ec.mc_cells();
R.cells_150uW_mc = struct('median', median(N), 'p5', prctile(N, 5), 'p95', prctile(N, 95));
R.esr_max_ohm = (5.0 - 3.5)/P.I_TX;

Pr = ec.p_net(150e-6, 'realistic'); Es = ec.e_event('sgp30');
ncell = @(E, h) ceil((P.P_FLOOR + E./(h*3600) + 1.6e-6 + 5e-6)/(0.80*0.75*22e-6));
ks = [1 4 8]; rep = ((ks - 1)*El + Es)./ks/Pr/3600; gh = [72 48 24 12 6];
R.gas_strategy = struct('sgp30_every_k', ks, 'report_h', rep, 'gas_h', rep.*ks, 'mq135_gas_h', gh, ...
    'mq135_cells', ncell(Ef, gh), 'sgp30_cells_2p3h', ncell(Es, 2.3), 'sgp30_continuous_W', P.I_SGP30*P.V_CC);

ta = [0.1 0.25 0.5 1.0 2.0 5.0];
R.wake_sweep_min.t_active_s = ta;
for i = 1:3
    R.wake_sweep_min.(cs{i}) = (P.V_CC*(P.I_ACT + P.I_SENS)*ta + P.E_TX)/ec.p_net(150e-6, cs{i})/60;
end

Pn = ec.p_net(150e-6, 'realistic');
f = [0 0.05 0.10 0.25 1.0];
tot = Pn./((1 - f)*El + f*Ef)*86400;
R.pareto = struct('f', f, 'total_per_day', tot, 'gas_per_day', f.*tot);

[dt, nInf] = ec.mc_interval();
R.mc_interval = struct('n', 20000, 'n_infeasible', nInf, 'median_h', median(dt), ...
    'p5_h', prctile(dt, 5), 'p95_h', prctile(dt, 95), 'frac_sub2h', mean(dt < 2), ...
    'n_sub1h', sum(dt < 1), 'min_h', min(dt));

T = ec.sobol_ci();
R.sobol = table2struct(T);

window = 5.0^2 - 3.5^2; etab = 0.90; Ibmin = 93e-3; esr = 0.5;
D.bank_usable_J = 0.25*window;
D.c_required_F = struct('lean', 2*El/etab/window, 'sgp30', 2*Es/etab/window, 'mq135', 2*Ef/etab/window);
q = (P.I_ACT + P.I_TX - Ibmin)*P.TOA + max(P.I_ACT + P.I_SENS - Ibmin, 0)*2.0;
D.burst = struct('rail_peak_A', P.I_ACT + P.I_TX, 'deficit_charge_C', q, 'esr_ohm', esr, ...
    'c_burst_min_F', q/((P.V_CC - 3.0) - esr*(P.I_ACT + P.I_TX - Ibmin)));
D.bank_current_max_A = P.V_CC*110e-3/(etab*3.5);
mcus = {'ESP32', 10e-6, 80e-3; 'STM32L0', 0.9e-6, 5e-3; 'MSP430FR', 0.5e-6, 1e-3; 'nRF52832', 1.5e-6, 3.7e-3; 'Apollo3', 1e-6, 0.5e-3};
for k = 1:size(mcus, 1)
    e = P.V_CC*(mcus{k, 3}*2 + P.I_SENS*2) + P.E_TX; fl = mcus{k, 2}*P.V_CC;
    id = 22e-6 - fl; re = 0.8*22e-6 - fl - 1.6e-6 - 5e-6;
    m = struct('E_event_J', e, 'ideal_h', [], 'realistic_h', []);
    if id > 0, m.ideal_h = e/id/3600; end
    if re > 0, m.realistic_h = e/re/3600; end
    D.mcu_22uW.(mcus{k, 1}) = m;
end
D.power_density_mW_m2 = struct('per_cell_22uW', 2.2, 'cell_15uW', 1.5, 'cell_30uW', 3.0);
p_off_rail = P.P_FLOOR + P.E_CHECK/(2.26*3600);
p_off = p_off_rail/etab + 1.6e-6 + 5e-6;
D.bridge = struct('p_off_bank_W', p_off, 'F_per_day', 2*p_off*86400/window, ...
    'max_days_leak_scaled', window/2/(P.LEAK_PER_F*86400));
D.lean_h_bank_referenced = El/etab/(0.80/etab*150e-6 - P.P_FLOOR/etab - 1.6e-6 - 5e-6)/3600;
D.branch_costs_J = struct('sleep', P.E_CHECK, 'measure', El - P.E_TX, 'transmit', El, 'anomaly', El);
iout = (60:10:110)'*1e-3; cb = zeros(size(iout));
for k = 1:numel(iout)
    qk = (P.I_ACT + P.I_TX - iout(k))*P.TOA + max(P.I_ACT + P.I_SENS - iout(k), 0)*2.0;
    cb(k) = qk/((P.V_CC - 3.0) - esr*(P.I_ACT + P.I_TX - iout(k)));
end
D.burst_vs_iout = struct('i_out_A', iout, 'c_burst_F', cb);
t_boot = P.T_CHECK; t_proc = 0.10; t_conv = 0.75; t_sens = 1.0;
Ed = P.V_CC*(P.I_ACT*(t_boot + t_proc) + P.I_LIGHT*t_conv + P.I_SENS*t_sens) + P.E_TX;
D.window_decomposed = struct('t_boot_s', t_boot, 't_proc_s', t_proc, 't_conv_light_sleep_s', t_conv, 't_sensors_on_s', t_sens, ...
    'E_event_J', Ed, 'interval_min', Ed/ec.p_net(150e-6, 'realistic')/60, ...
    't_active_equivalent_s', (Ed - P.E_TX)/(P.V_CC*(P.I_ACT + P.I_SENS)));
R.design_checks = D;

tf = fullfile(fileparts(fileparts(fileparts(mfilename('fullpath')))), 'external', 'yen_smfc_trace_5min.csv');
if exist(tf, 'file')
    tr = readtable(tf); cfg = [10 0.5 5e-6; 20 0.5 5e-6; 40 5.0 5e-6; 10 5.0 5.0*P.LEAK_PER_F];
    for k = 1:size(cfg, 1)
        r = ec.trace_scenario(tr.t_s, tr.p_cell_W, cfg(k, 1), 0.75, 2.26, cfg(k, 2), 5.0, 3.5, 0.05, cfg(k, 3));
        R.trace(k) = struct('n_cells', cfg(k, 1), 'c_eq', cfg(k, 2), 'availability', r.availability, ...
            'outages', r.outages, 'tx_total', r.tx_total, 'n_transmit', r.n_transmit, 'n_measure', r.n_measure, 'n_sleep', r.n_sleep);
    end
    banks = [0.5 5e-6; 5.0 5e-6; 5.0 5.0*P.LEAK_PER_F];
    pols = {'soc', 0; 'defer', 0; 'reserve', 1.0; 'reserve', 0};
    R.policy_report_ratio = zeros(4, 3); R.policy_availability = zeros(4, 3);
    for a = 1:4
        for b = 1:3
            r = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, banks(b, 1), 5.0, 3.5, 0.05, banks(b, 2), pols{a, 1}, pols{a, 2});
            R.policy_report_ratio(a, b) = r.report_ratio; R.policy_availability(a, b) = r.availability;
        end
    end
    T = tr.t_s(end); sched = T/(2.26*3600); Pm = 10*0.75*mean(tr.p_cell_W);
    R.ablation = struct('A_mean_harvest_event_energy', min(1, Pm*T/El/sched), ...
        'B_plus_floor_and_losses', min(1, max(ec.p_net(Pm, 'realistic'), 0)*T/El/sched), ...
        'C_plus_finite_storage_greedy', R.policy_report_ratio(4, 1), 'D_plus_algorithm2', R.policy_report_ratio(1, 1));
    rb = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 3.5, 0.05, 5e-6);
    dayb = accumarray(floor(tr.t_s/86400) + 1, rb.tx);
    yr = ec.yen_rule(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 5e-6);
    R.yen_rule = struct('report_ratio', yr.report_ratio, 'tx_total', yr.tx_total, 'days_without_tx', yr.days_without_tx, ...
        'ours_report_ratio', rb.report_ratio, 'ours_days_without_tx', sum(dayb == 0));
    yk = ec.yen_rule(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 5e-6, false);
    R.yen_rule.keep_remainder_report_ratio = yk.report_ratio; R.yen_rule.keep_remainder_days_without_tx = yk.days_without_tx;
    R.yen_rule.ours_greedy_report_ratio = R.policy_report_ratio(4, 1);
    Ed = D.window_decomposed.E_event_J; wdec = D.window_decomposed.interval_min/60;
    rd1 = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, wdec, 0.5, 5.0, 3.5, 0.05, 5e-6, 'soc', 0, Ed);
    rd2 = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, wdec, 0.5, 5.0, 3.5, 0.05, 5e-6, 'reserve', 1.0, Ed);
    rd3 = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 3.5, 0.05, 5e-6, 'soc', 0, Ed);
    dd = accumarray(floor(tr.t_s/86400) + 1, rd1.tx); d3 = accumarray(floor(tr.t_s/86400) + 1, rd3.tx);
    runlen = @(on) max(accumarray(cumsum([1; diff(double(~on(:))) ~= 0]), double(~on(:))));
    dtt = tr.t_s(2) - tr.t_s(1); T = tr.t_s(end);
    R.trace_decomposed = struct('E_event_J', Ed, 'wake_h', wdec, 'report_ratio', rd1.report_ratio, 'availability', rd1.availability, ...
        'outages', rd1.outages, 'days_without_tx', sum(dd == 0), 'reserve_report_ratio', rd2.report_ratio, ...
        'grid226_report_ratio', rd3.report_ratio, 'grid226_availability', rd3.availability, 'tx_total', rd1.tx_total, ...
        'ideal_reports', T/(wdec*3600), 'longest_outage_days', runlen(rd1.on)*dtt/86400, ...
        'grid226_tx_total', rd3.tx_total, 'grid226_days_without_tx', sum(d3 == 0), 'grid226_outages', rd3.outages, ...
        'grid226_longest_outage_days', runlen(rd3.on)*dtt/86400, ...
        'base_tx_total', rb.tx_total, 'base_ideal_reports', T/(2.26*3600), 'base_longest_outage_days', runlen(rb.on)*dtt/86400, 'base_outages', rb.outages);
    rs = [0.02 0.05 0.10 0.25]; R.restart_soc = struct('restart_soc', rs, 'report_ratio', zeros(size(rs)), 'availability', zeros(size(rs)));
    for k = 1:numel(rs)
        r = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 3.5, rs(k), 5e-6);
        R.restart_soc.report_ratio(k) = r.report_ratio; R.restart_soc.availability(k) = r.availability;
    end
    tf1 = strrep(tf, '5min', '1min');
    if exist(tf1, 'file')
        t1 = readtable(tf1);
        a1 = ec.trace_scenario(t1.t_s, t1.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 3.5, 0.05, 5e-6);
        b1 = ec.trace_scenario(t1.t_s, t1.p_cell_W, 10, 0.75, 2.26, 0.5, 5.0, 3.5, 0.05, 5e-6, 'reserve', 1.0);
        R.trace_step = struct('step_s', [300 60], 'report_ratio', [rb.report_ratio a1.report_ratio], ...
            'availability', [rb.availability a1.availability], 'reserve_report_ratio', [R.policy_report_ratio(3, 1) b1.report_ratio], ...
            'mean_cell_uW', [mean(tr.p_cell_W) mean(t1.p_cell_W)]*1e6);
    end
end
R.anomaly = ec.anomaly_layer();
R.sobol_seed = ec.sobol_seed_stability();

w = [1.9 2.26];
for k = 1:2
    S = ec.dynamic_scenario(w(k));
    R.dynamic(k) = struct('wake_h', w(k), 'n_transmit', S.n_transmit, 'n_measure', S.n_measure, ...
        'n_sleep', S.n_sleep, 'n_anomaly', S.n_anomaly, 'v_min', S.v_min, 'v_max', S.v_max, ...
        'soc_min', S.soc_min, 'soc_max', S.soc_max, 'event_t_h', S.events.t_h, ...
        'event_action', {S.events.action}, 'event_v_before', S.events.v_before);
end
end
