function R = yen_rule(t_s, p_cell, n_cells, eta_stack, wake_h, c_eq, v_max, pleak, empty_store)
%YEN_RULE The accounting of the trace simulator of Yen et al. (Runtime_Simulation/models.py) applied to
%   this node on the same trace and wake grid: the harvest enters the store through the converter
%   efficiency and the store leaks, but there is no sleep floor, no PMIC quiescent draw and no storage
%   window (the store starts empty and the node never browns out); a wake transmits when the stored
%   energy covers one event and then empties the store, as in their simulator. Rail-referred, Eq. (6).
%   empty_store = false keeps the remainder after a transmission (only the energy terms differ from the
%   full model's transmit-when-one-event-is-stored policy).
if nargin < 9, empty_store = true; end
P = ec.params(); c = P.cases.realistic;
El = ec.e_event('lean');
dt = t_s(2) - t_s(1); n = numel(t_s);
p_in = c.eta*n_cells*eta_stack*p_cell(:);
e_max = 0.5*c_eq*v_max^2; E = 0; nxt = wake_h*3600; tx = zeros(n, 1);
for i = 1:n
    E = min(max(E + (p_in(i) - pleak)*dt, 0), e_max);
    if t_s(i) >= nxt
        if E >= El
            tx(i) = 1;
            if empty_store, E = 0; else, E = E - El; end
        end
        nxt = nxt + wake_h*3600;
    end
end
day = floor(t_s(:)/86400);
per_day = accumarray(day + 1, tx);
R = struct('report_ratio', sum(tx)/(t_s(end)/(wake_h*3600)), 'tx_total', sum(tx), ...
    'days_without_tx', sum(per_day == 0), 'tx', tx);
end
