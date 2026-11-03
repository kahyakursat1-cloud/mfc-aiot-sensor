function P = params()
%PARAMS Fixed electrical parameters and power-path cases (paper Table 2).
%   MATLAB port of simulation/energy_chain.py.
P.V_CC    = 3.3;
P.I_ACT   = 80e-3;
P.I_SENS  = (5 + 1.5 + 10)*1e-3;
P.I_SLEEP = 10e-6;
P.I_TX    = 120e-3;
P.TOA     = 0.0412;
P.E_TX    = P.I_TX*P.V_CC*P.TOA;
P.P_FLOOR = P.I_SLEEP*P.V_CC;
P.I_SGP30 = 48.8e-3;      % SGP30 measurement mode (datasheet v1.0, 2020)
P.T_SGP30_ON = 16.0;      % 15 s initialisation + first valid reading
P.I_LIGHT = 0.8e-3;       % ESP32 light sleep during the warm-up
P.T_CHECK = 0.25;         % wake that only reads the state of charge
P.E_CHECK = P.V_CC*P.I_ACT*P.T_CHECK;
P.ETA_BUCK = 0.90;        % buck efficiency: rail loads leave the bank divided by it
P.LEAK_PER_F = 10e-6;     % bank leakage scaled with capacitance (5 uW for 0.5 F)
P.cases.ideal        = struct('eta', 1.00, 'pq', 0,      'pleak', 0);
P.cases.realistic    = struct('eta', 0.80, 'pq', 1.6e-6, 'pleak', 5e-6);
P.cases.conservative = struct('eta', 0.70, 'pq', 1.6e-6, 'pleak', 15e-6);
end
