function S = dynamic_scenario(wake_h, soc0, anomalies_h, T_h, dt)
%DYNAMIC_SCENARIO Algorithm 2 under a diurnal harvest P(t) = P0(1 + 0.2 sin 2*pi*t/24 h).
%   The 0.5 F bank (3.5-5.0 V window) is bank-referenced: harvest enters at eta_PMIC/eta_buck,
%   rail loads leave divided by eta_buck. SoC is the usable-energy fraction of the window.
%   An anomaly forces a transmission only when SoC > 0.35; otherwise it stays pending.
if nargin < 1, wake_h = 1.9; end
if nargin < 2, soc0 = 0.8; end
if nargin < 3, anomalies_h = [28 52]; end
if nargin < 4, T_h = 72; end
if nargin < 5, dt = 60; end
P = ec.params(); c = P.cases.realistic; eb = P.ETA_BUCK;
c_eq = 0.5; v_max = 5.0; v_min = 3.5; p0 = 150e-6; amp = 0.2;
e_min = 0.5*c_eq*v_min^2; e_max = 0.5*c_eq*v_max^2;
e_lean = ec.e_event('lean')/eb; e_meas = (ec.e_event('lean') - P.E_TX)/eb; e_chk = P.E_CHECK/eb;
t = (0:dt:T_h*3600 - dt)';
p = p0*(1 + amp*sin(2*pi*t/86400));
pnet = c.eta/eb*p - P.P_FLOOR/eb - c.pq - c.pleak;
E = e_min + soc0*(e_max - e_min);
nxt = wake_h*3600;
pending = sort(anomalies_h(:)'*3600);
v = zeros(numel(t), 1);
ev_t = []; ev_a = {}; ev_vb = []; ev_va = [];
for i = 1:numel(t)
    ti = t(i);
    E = min(E + pnet(i)*dt, e_max);
    if ti >= nxt
        nxt = nxt + wake_h*3600;
        soc = (E - e_min)/(e_max - e_min);
        v_before = sqrt(2*E/c_eq);
        if ~isempty(pending) && pending(1) <= ti && soc > 0.35
            E = E - e_lean; action = 'anomaly'; pending(1) = [];
        elseif soc < 0.25
            E = E - e_chk; action = 'sleep';
        elseif soc < 0.55
            E = E - e_meas; action = 'measure';
        else
            E = E - e_lean; action = 'transmit';
        end
        ev_t(end+1, 1) = ti; ev_a{end+1, 1} = action; %#ok<AGROW>
        ev_vb(end+1, 1) = v_before; ev_va(end+1, 1) = sqrt(2*E/c_eq); %#ok<AGROW>
    end
    v(i) = sqrt(2*E/c_eq);
end
soc = (0.5*c_eq*v.^2 - e_min)/(e_max - e_min);
S.t = t; S.p = p; S.v = v; S.e_min = e_min; S.e_max = e_max;
S.events = table(ev_t/3600, ev_a, ev_vb, ev_va, 'VariableNames', {'t_h', 'action', 'v_before', 'v_after'});
S.n_transmit = sum(strcmp(ev_a, 'transmit'));
S.n_measure  = sum(strcmp(ev_a, 'measure'));
S.n_sleep    = sum(strcmp(ev_a, 'sleep'));
S.n_anomaly  = sum(strcmp(ev_a, 'anomaly'));
S.v_min = min(v); S.v_max = max(v); S.soc_min = min(soc); S.soc_max = max(soc);
end
