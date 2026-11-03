function R = trace_scenario(t_s, p_cell, n_cells, eta_stack, wake_h, c_eq, v_max, v_min, restart_soc, pleak, policy, reserve_J, e_event_rail, cs)
%TRACE_SCENARIO Algorithm 2 driven by a measured single-cell power trace (uniform step).
%   Bank-referenced: harvest enters the bank at eta_PMIC/eta_buck, rail loads leave it divided by
%   eta_buck. Below v_min the node is off (no sleep floor) and it restarts once the bank refills to
%   restart_soc of the usable window. Wakes follow a fixed grid of wake_h from the last restart and
%   run at the first step at or after each grid time; a SLEEP wake pays E_CHECK on its own.
%   pleak overrides the case leakage. policy: 'soc' (Algorithm 2 thresholds 0.25 / 0.55),
%   'defer' (transmit at SoC >= 0.55, otherwise sleep without measuring), or 'reserve' (transmit
%   when the usable energy covers one event plus reserve_J, otherwise sleep). e_event_rail overrides the
%   rail-referred event energy (default: the lean event).
%   cs adds the BQ25570 cold start: while the bank is below cs.v_bank the input is clamped to cs.v_cs
%   and charges only through the cold-start circuit, at efficiency cs.eta, if the array can deliver
%   cs.p_min there. The cell open-circuit voltage is inferred from the voltage across the logging
%   resistor cs.r_meas with internal resistance cs.r_int, capped at cs.v_oc_max.
if nargin < 3, n_cells = 10; end
if nargin < 4, eta_stack = 0.75; end
if nargin < 5, wake_h = 2.26; end
if nargin < 6, c_eq = 0.5; end
if nargin < 7, v_max = 5.0; end
if nargin < 8, v_min = 3.5; end
if nargin < 9, restart_soc = 0.05; end
P = ec.params(); c = P.cases.realistic; eb = P.ETA_BUCK;
if nargin < 10 || isempty(pleak), pleak = c.pleak; end
if nargin < 11, policy = 'soc'; end
if nargin < 12, reserve_J = 0; end
e_min = 0.5*c_eq*v_min^2; e_max = 0.5*c_eq*v_max^2; e_on = e_min + restart_soc*(e_max - e_min);
if nargin < 13 || isempty(e_event_rail), e_event_rail = ec.e_event('lean'); end
e_lean = e_event_rail/eb; e_meas = (e_event_rail - P.E_TX)/eb; e_chk = P.E_CHECK/eb;
dt = t_s(2) - t_s(1);
p_in = c.eta/eb*n_cells*eta_stack*p_cell(:);
E = e_on; on = true; nxt = wake_h*3600; n = numel(t_s);
e_cs = -Inf; p_cs = zeros(n, 1);
if nargin >= 14 && ~isempty(cs)
    e_cs = 0.5*c_eq*cs.v_bank^2;
    v_oc = min(sqrt(max(p_cell(:), 0)*cs.r_meas)*(1 + cs.r_int/cs.r_meas), cs.v_oc_max);
    i_cs = max(cs.n_series*v_oc - cs.v_cs, 0)/(cs.n_series*cs.r_int/(n_cells/cs.n_series));
    p_cs = cs.v_cs*i_cs; p_cs(p_cs < cs.p_min) = 0; p_cs = cs.eta*p_cs;
end
on_flag = false(n, 1); tx = zeros(n, 1); cnt = [0 0 0]; outages = 0;
for i = 1:n
    if E < e_cs, p_h = p_cs(i); else, p_h = p_in(i); end
    E = E + (p_h - c.pq - pleak - P.P_FLOOR/eb*on)*dt;
    E = min(max(E, 0), e_max);
    if on && E < e_min
        on = false; outages = outages + 1;
    elseif ~on && E >= e_on
        on = true; nxt = t_s(i);
    end
    if on && t_s(i) >= nxt
        while nxt <= t_s(i), nxt = nxt + wake_h*3600; end
        soc = (E - e_min)/(e_max - e_min);
        switch policy
            case 'soc'
                if soc < 0.25, act = 3; elseif soc < 0.55, act = 2; else, act = 1; end
            case 'defer'
                if soc >= 0.55, act = 1; else, act = 3; end
            otherwise
                if E - e_min >= e_lean + reserve_J, act = 1; else, act = 3; end
        end
        if act == 3
            E = E - e_chk;
        elseif act == 2
            E = E - e_meas;
        else
            E = E - e_lean; tx(i) = 1;
        end
        cnt(act) = cnt(act) + 1;
        if E < e_min
            on = false; outages = outages + 1;
        end
    end
    on_flag(i) = on;
end
R = struct('availability', mean(on_flag), 'outages', outages, 'tx_total', sum(tx), ...
    'n_transmit', cnt(1), 'n_measure', cnt(2), 'n_sleep', cnt(3), ...
    'report_ratio', sum(tx)/(t_s(end)/(wake_h*3600)), 'on', on_flag, 'tx', tx);
end
