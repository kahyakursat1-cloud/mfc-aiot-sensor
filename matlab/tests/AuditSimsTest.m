classdef AuditSimsTest < matlab.unittest.TestCase
    % Checks of the airtime formula, the rail transient and the cold-start gate.

    properties
        S
    end

    methods (TestClassSetup)
        function load(tc)
            addpath(fileparts(fileparts(mfilename('fullpath'))));
            tc.S = ec.sim_v27();
        end
    end

    methods (Test)
        function airtimeMatchesDatasheetFormula(tc)
            [t, n] = ec.lora_toa([7 8 9 10 11 12]);
            tc.verifyEqual(n, [28 28 23 23 23 23]);
            tc.verifyEqual(t*1e3, [41.216 82.432 144.384 288.768 577.536 1155.072], 'AbsTol', 0.01);
        end

        function transientReproducesClosedForm(tc)
            v = tc.S.rail.v_min_at_c;
            tc.verifyEqual(v, 3.0*ones(size(v)), 'AbsTol', 2e-3);
        end

        function transientIsBelowLimitWhenCapacitorIsSmaller(tc)
            r = ec.rail_transient(0.093, 0.02, 0.5, 0.0412);
            tc.verifyLessThan(r.v_min, 3.0);
        end

        function mpptPeakIsAtHalfOpenCircuit(tc)
            tc.verifyEqual(tc.S.mppt.factor(1), 1 - 0.256/16, 'RelTol', 1e-12);
            tc.verifyLessThan(tc.S.mppt.factor(4), tc.S.mppt.factor(3));
        end

        function coldStartNeverHelps(tc)
            r = [tc.S.coldstart.runs.report_ratio];
            tc.verifyLessThanOrEqual(max(r), tc.S.coldstart.base_report_ratio + 1e-3);
        end

        function settlingAddsEnergyMonotonically(tc)
            tc.verifyTrue(all(diff(tc.S.ph.E_J) > 0));
            tc.verifyEqual(tc.S.ph.E_J(1), ec.e_event('lean'), 'RelTol', 1e-12);
        end
    end
end
