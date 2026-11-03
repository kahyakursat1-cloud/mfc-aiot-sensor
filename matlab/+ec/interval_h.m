function dt = interval_h(payload, p_mfc, caseName)
%INTERVAL_H Sustainable reporting interval in hours (Eq. 7); Inf when P_net <= 0.
pn = ec.p_net(p_mfc, caseName);
if pn <= 0
    dt = Inf;
else
    dt = ec.e_event(payload)/pn/3600;
end
end
