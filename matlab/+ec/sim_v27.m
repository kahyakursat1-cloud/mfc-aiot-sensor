function S = sim_v27()
%SIM_V27 Closed-form and time-stepped checks added after the audit of the draft: LoRa airtime from
%   the datasheet formula, rail transient, MPPT operating point, cold start after outages and the
%   pH settling time. Inputs not read from a datasheet are named as assumptions in the paper.
P = ec.params(); El = ec.e_event('lean'); c = P.cases.realistic;
pn150 = ec.p_net(150e-6, 'realistic');
here = fileparts(fileparts(mfilename('fullpath')));
A = readmatrix(fullfile(fileparts(here), 'external', 'yen_smfc_trace_5min.csv'));
t_s = A(:, 1); p_cell = A(:, 2);
base = @(pc, varargin) ec.trace_scenario(t_s, pc, 10, 0.75, 2.26, 0.5, 5.0, 3.5, 0.05, 5e-6, varargin{:});
rb = base(p_cell);

sf = 7:12; toa = ec.lora_toa(sf); t_crc = ec.lora_toa(7, 13, 125e3, 1, 8, 1);
S.lora = struct('sf', sf, 'toa_ms', toa*1e3, 'e_mJ', toa*P.I_TX*P.V_CC*1e3, ...
    'toa_crc_ms', t_crc*1e3, 'e_crc_mJ', t_crc*P.I_TX*P.V_CC*1e3);

esr = 0.5; vmin = 3.0; i_w = P.I_ACT + P.I_SENS; i_tx = P.I_ACT + P.I_TX;
cb = @(io, ta) (max(i_tx - io, 0)*ta + max(i_w - io, 0)*2.0)/((P.V_CC - vmin) - esr*(i_tx - io));
iout = sort([(60:10:110)'*1e-3; 0.093]); v = zeros(size(iout)); cc = v;
for k = 1:numel(iout)
    cc(k) = cb(iout(k), P.TOA); r = ec.rail_transient(iout(k), cc(k), esr, P.TOA); v(k) = r.v_min;
end
c46 = cb(0.093, P.TOA); r46 = ec.rail_transient(0.093, c46, esr, P.TOA);
csf = arrayfun(@(t) cb(0.093, t), toa);
vsf = arrayfun(@(t) ec.rail_transient(0.093, c46, esr, t).v_min, toa);
S.rail = struct('i_out_A', iout, 'c_F', cc, 'v_min_at_c', v, 'refill_s', r46.t_refill, 'c_sf_F', csf, ...
    'v_min_sf_at_46mF', vsf, 'c_crc_F', cb(0.093, t_crc), 'c_retry_F', cb(0.093, 2*P.TOA), ...
    'q_window_C', (i_w - 0.093)*2.0, 'q_tx_C', (i_tx - 0.093)*P.TOA);

k = [0.5 0.6 0.7 0.8]; samp = 1 - 0.256/16; f = 4*k.*(1 - k);
pm = 150e-6*f*samp; pnk = c.eta*pm - P.P_FLOOR - c.pq - c.pleak;
rat = zeros(size(k)); av = rat;
for i = 1:numel(k), r = base(p_cell*f(i)*samp); rat(i) = r.report_ratio; av(i) = r.availability; end
S.mppt = struct('k', k, 'factor', f*samp, 'p_uW', pm*1e6, 'p_net_uW', pnk*1e6, 'dt_h', El./pnk/3600, ...
    'report_ratio', rat, 'availability', av);

cs0 = struct('v_bank', 1.73 - 0.6, 'v_cs', 0.6, 'p_min', 15e-6, 'eta', 0.10, 'r_int', 6e3, ...
    'r_meas', 2e3, 'v_oc_max', 0.75, 'n_series', 2);
etas = [0.05 0.10 0.20]; vcs = [0.6 0.7]; rints = [2e3 6e3]; n = numel(etas)*numel(vcs)*numel(rints);
cold = repmat(struct('eta', 0, 'v_cs', 0, 'r_int', 0, 'report_ratio', 0, 'availability', 0, 'outages', 0, ...
    'longest_d', 0, 'days_without_tx', 0), n, 1);
m = 0;
for i = 1:numel(etas)
    for j = 1:numel(vcs)
        for h = 1:numel(rints)
            q = cs0; q.eta = etas(i); q.v_cs = vcs(j); q.r_int = rints(h); m = m + 1;
            r = base(p_cell, 'soc', 0, [], q);
            cold(m) = struct('eta', etas(i), 'v_cs', vcs(j), 'r_int', rints(h), 'report_ratio', r.report_ratio, ...
                'availability', r.availability, 'outages', r.outages, 'longest_d', runlen(r.on)*300/86400, ...
                'days_without_tx', daysoff(t_s, r.tx));
        end
    end
end
S.coldstart = struct('runs', cold, 'base_report_ratio', rb.report_ratio, 'base_availability', rb.availability, ...
    'base_longest_d', runlen(rb.on)*300/86400, 'base_days_without_tx', daysoff(t_s, rb.tx), ...
    'e_bank_J', 0.25*cs0.v_bank^2);

ts = [0 10 30 60 120]; e = El + P.V_CC*(10e-3 + P.I_LIGHT)*ts; dt = e/pn150/3600;
cm = 2*e/(P.ETA_BUCK*(5^2 - 3.5^2)); rr = zeros(size(ts)); ra = rr; rres = rr;
for i = 1:numel(ts)
    r = ec.trace_scenario(t_s, p_cell, 10, 0.75, dt(i), 0.5, 5.0, 3.5, 0.05, 5e-6, 'soc', 0, e(i));
    q = ec.trace_scenario(t_s, p_cell, 10, 0.75, dt(i), 0.5, 5.0, 3.5, 0.05, 5e-6, 'reserve', 0, e(i));
    rr(i) = r.report_ratio; ra(i) = r.availability; rres(i) = q.report_ratio;
end
S.ph = struct('t_settle_s', ts, 'E_J', e, 'dt_h', dt, 'c_min_F', cm, 'report_ratio', rr, 'availability', ra, ...
    'report_ratio_greedy', rres, 'ratio_to_lean', e/El);
end

function n = runlen(on)
n = 0; c = 0;
for i = 1:numel(on)
    if on(i), c = 0; else, c = c + 1; n = max(n, c); end
end
end

function n = daysoff(t_s, tx)
d = floor(t_s(:)/86400); n = sum(accumarray(d + 1, tx(:)) == 0);
end
