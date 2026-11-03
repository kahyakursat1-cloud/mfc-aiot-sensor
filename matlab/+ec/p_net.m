function pn = p_net(p_mfc, caseName)
%P_NET Loss-aware net power (Eq. 6): eta*P_MFC - P_floor - P_PMIC,q - P_leak.
P = ec.params();
c = P.cases.(caseName);
pn = c.eta*p_mfc - P.P_FLOOR - c.pq - c.pleak;
end
