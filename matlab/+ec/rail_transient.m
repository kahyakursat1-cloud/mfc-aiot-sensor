function R = rail_transient(i_out, c_b, esr, t_air, t_window)
%RAIL_TRANSIENT Time-stepped rail during one event: the sensing window, then the radio burst.
%   The buck stage is a 3.3 V source limited to i_out; a rail-side capacitor c_b with series
%   resistance esr supplies the excess and is refilled by whatever the limit leaves over.
%   Returns the minimum rail voltage, the time it occurs and the refill time after the event.
if nargin < 5, t_window = 2.0; end
P = ec.params();
i_w = P.I_ACT + P.I_SENS; i_tx = P.I_ACT + P.I_TX;
dt = 1e-4; n = ceil((t_window + t_air)/dt) + ceil(30/dt);
vc = P.V_CC; v_min = vc; t_min = 0; t_full = NaN; i_idle = P.I_SLEEP;
for k = 1:n
    t = (k - 1)*dt;
    if t < t_window, i_l = i_w; elseif t < t_window + t_air, i_l = i_tx; else, i_l = i_idle; end
    if i_l > i_out
        i_c = i_l - i_out;
    else
        i_c = -min(i_out - i_l, (P.V_CC - vc)/esr);
    end
    vc = min(vc - i_c*dt/c_b, P.V_CC);
    v_rail = vc - esr*max(i_c, 0);
    if v_rail < v_min, v_min = v_rail; t_min = t; end
    if t > t_window + t_air && isnan(t_full) && vc >= P.V_CC - 1e-3, t_full = t - t_window - t_air; end
end
R = struct('v_min', v_min, 't_min', t_min, 't_refill', t_full);
end
