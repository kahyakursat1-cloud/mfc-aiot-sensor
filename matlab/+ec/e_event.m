function E = e_event(payload)
%E_EVENT Energy per measure-and-transmit event (J) for 'lean', 'lowgas' or 'mq135'.
P = ec.params();
switch payload
    case 'lean'
        t = 2.0;
        E = P.V_CC*(P.I_ACT*t + P.I_SENS*t) + P.E_TX;
    case 'lowgas'
        t = 2.0;
        e_gas = 48e-3*P.V_CC*0.012;   % sgp30_measure_iaq, 12 ms maximum

        E = P.V_CC*(P.I_ACT*t + P.I_SENS*t) + e_gas + P.E_TX;
    case 'sgp30'
        t = 2.0;
        e_gas = P.I_SGP30*P.V_CC*P.T_SGP30_ON + P.I_LIGHT*P.V_CC*(P.T_SGP30_ON - 1.0);
        E = P.V_CC*(P.I_ACT*t + P.I_SENS*t) + e_gas + P.E_TX;
    case 'mq135'
        t = 5.0;
        e_heater = 150e-3*5.0*30.0;
        E = P.V_CC*(P.I_ACT*t + P.I_SENS*t) + e_heater + P.E_TX;
    otherwise
        error('ec:payload', 'unknown payload %s', payload);
end
end
