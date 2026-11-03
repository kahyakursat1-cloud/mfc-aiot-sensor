classdef CrossValidationTest < matlab.unittest.TestCase
    % Compares the MATLAB implementation (+ec) with python_reference.json.
    % Deterministic quantities must agree to round-off; Monte Carlo and Sobol
    % statistics within sampling noise (different random streams, same distributions).

    properties
        R
        ref
    end

    methods (TestClassSetup)
        function load(tc)
            root = fileparts(fileparts(mfilename('fullpath')));
            addpath(root);
            tc.ref = jsondecode(fileread(fullfile(root, 'python_reference.json')));
            tc.R = ec.compute_all();
        end
    end

    methods (Test)
        function eventEnergies(tc)
            for p = {'lean', 'lowgas', 'sgp30', 'mq135'}
                tc.verifyEqual(tc.R.e_event_J.(p{1}), tc.ref.e_event_J.(p{1}), 'RelTol', 1e-12);
            end
        end

        function intervalsAndNetPower(tc)
            cs = {'ideal', 'realistic', 'conservative'};
            for i = 1:3
                tc.verifyEqual(tc.R.p_net_150uW_W.(cs{i}), tc.ref.p_net_150uW_W.(cs{i}), 'RelTol', 1e-12);
                tc.verifyEqual(tc.R.deficit_10min_x.(cs{i}), tc.ref.deficit_10min_x.(cs{i}), 'RelTol', 1e-12);
                for p = {'lean', 'lowgas', 'sgp30', 'mq135'}
                    tc.verifyEqual(tc.R.interval_150uW_h.(p{1}).(cs{i}), tc.ref.interval_150uW_h.(p{1}).(cs{i}), 'RelTol', 1e-12);
                end
            end
            tc.verifyEqual(tc.R.zheng_41uW.ideal_h, tc.ref.zheng_41uW.ideal_h, 'RelTol', 1e-12);
            tc.verifyLessThan(tc.R.zheng_41uW.pnet_realistic_W, 0);
        end

        function sizingRelations(tc)
            tc.verifyEqual(tc.R.cells_vs_interval.N(:), tc.ref.cells_vs_interval.N(:));
            tc.verifyEqual(tc.R.cells_150uW_det, tc.ref.cells_150uW_det);
            tc.verifyEqual(tc.R.esr_max_ohm, tc.ref.esr_max_ohm, 'RelTol', 1e-12);
            tc.verifyEqual(tc.R.pareto.total_per_day(:), tc.ref.pareto.total_per_day(:), 'RelTol', 1e-12);
            for c = {'ideal', 'realistic', 'conservative'}
                tc.verifyEqual(tc.R.wake_sweep_min.(c{1})(:), tc.ref.wake_sweep_min.(c{1})(:), 'RelTol', 1e-12);
            end
        end

        function gasStrategy(tc)
            g = tc.R.gas_strategy; q = tc.ref.gas_strategy;
            tc.verifyEqual(g.report_h(:), q.report_h(:), 'RelTol', 1e-12);
            tc.verifyEqual(g.gas_h(:), q.gas_h(:), 'RelTol', 1e-12);
            tc.verifyEqual(g.mq135_cells(:), q.mq135_cells(:));
            tc.verifyEqual(g.sgp30_cells_2p3h, q.sgp30_cells_2p3h);
            tc.verifyEqual(g.sgp30_continuous_W, q.sgp30_continuous_W, 'RelTol', 1e-12);
        end

        function designChecks(tc)
            g = tc.R.design_checks; q = tc.ref.design_checks;
            tc.verifyEqual(g.bank_usable_J, q.bank_usable_J, 'RelTol', 1e-12);
            for p = {'lean', 'sgp30', 'mq135'}
                tc.verifyEqual(g.c_required_F.(p{1}), q.c_required_F.(p{1}), 'RelTol', 1e-12);
            end
            tc.verifyEqual(g.burst.c_burst_min_F, q.burst.c_burst_min_F, 'RelTol', 1e-12);
            tc.verifyEqual(g.bridge.F_per_day, q.bridge.F_per_day, 'RelTol', 1e-12);
            tc.verifyEqual(g.bridge.max_days_leak_scaled, q.bridge.max_days_leak_scaled, 'RelTol', 1e-12);
            tc.verifyEqual(g.lean_h_bank_referenced, q.lean_h_bank_referenced, 'RelTol', 1e-12);
            for b = {'sleep', 'measure', 'transmit', 'anomaly'}
                tc.verifyEqual(g.branch_costs_J.(b{1}), q.branch_costs_J.(b{1}), 'RelTol', 1e-12);
            end
            for k = {'STM32L0', 'MSP430FR', 'nRF52832', 'Apollo3'}
                tc.verifyEqual(g.mcu_22uW.(k{1}).realistic_h, q.mcu_22uW.(k{1}).realistic_h, 'RelTol', 1e-12);
                tc.verifyEqual(g.mcu_22uW.(k{1}).ideal_h, q.mcu_22uW.(k{1}).ideal_h, 'RelTol', 1e-12);
            end
            tc.verifyEmpty(g.mcu_22uW.ESP32.realistic_h);
        end

        function measuredTraceScenario(tc)
            tc.assumeTrue(isfield(tc.ref, 'trace') && isfield(tc.R, 'trace'), 'Yen trace not available');
            for k = 1:numel(tc.ref.trace)
                m = tc.R.trace(k); q = tc.ref.trace(k);
                tc.verifyEqual([m.outages m.tx_total m.n_transmit m.n_measure m.n_sleep], ...
                               [q.outages q.tx_total q.n_transmit q.n_measure q.n_sleep]);
                tc.verifyEqual(m.availability, q.availability, 'AbsTol', 1e-12);
            end
            tc.verifyEqual(tc.R.policy_report_ratio, tc.ref.policy_report_ratio, 'AbsTol', 1e-12);
            tc.verifyEqual(tc.R.policy_availability, tc.ref.policy_availability, 'AbsTol', 1e-12);
        end

        function anomalyLayerTraversal(tc)
            % The node-visit count used for the inference-cost estimate comes from an explicit
            % traversal of every tree; the anomaly score rebuilt from those path lengths must
            % reproduce the score of iforest, otherwise the traversal (and the cost) is wrong.
            a = tc.R.anomaly;
            tc.verifyLessThan(a.score_check_max_abs_diff, 1e-3);
            tc.verifyEqual(a.n_trees, 150);
            tc.verifyGreaterThan(a.holdout_isolation_forest.f1, 0.9);
        end

        function cellCountMonteCarlo(tc)
            tc.verifyEqual(tc.R.cells_150uW_mc.median, tc.ref.cells_150uW_mc.median, 'AbsTol', 1);
            tc.verifyEqual(tc.R.cells_150uW_mc.p5, tc.ref.cells_150uW_mc.p5, 'AbsTol', 1);
            tc.verifyEqual(tc.R.cells_150uW_mc.p95, tc.ref.cells_150uW_mc.p95, 'AbsTol', 1);
        end

        function intervalMonteCarlo(tc)
            m = tc.R.mc_interval; r = tc.ref.mc_interval;
            tc.verifyEqual(m.n_infeasible, r.n_infeasible);
            tc.verifyEqual(m.median_h, r.median_h, 'RelTol', 0.02);
            tc.verifyEqual(m.p5_h, r.p5_h, 'RelTol', 0.03);
            tc.verifyEqual(m.p95_h, r.p95_h, 'RelTol', 0.03);
            tc.verifyEqual(m.frac_sub2h, r.frac_sub2h, 'AbsTol', 0.015);
            tc.verifyGreaterThan(m.min_h, 0.5);
        end

        function inputDistributions(tc)
            rng(7, 'twister');
            X = ec.sample_inputs(400000);
            names = fieldnames(tc.ref.input_moments);
            for j = 1:numel(names)
                q = tc.ref.input_moments.(names{j}); x = X(:, j);
                tc.verifyEqual(mean(x), q.mean, 'RelTol', 0.005, names{j});
                tc.verifyEqual(std(x, 1), q.std, 'RelTol', 0.01, names{j});
                tc.verifyEqual(prctile(x, 5), q.p5, 'RelTol', 0.01, names{j});
                tc.verifyEqual(prctile(x, 95), q.p95, 'RelTol', 0.01, names{j});
            end
        end

        function sobolIndices(tc)
            % Two independent estimates agree when their difference is within the
            % combined bootstrap 95% half-widths (plus 0.005 for near-zero indices).
            for i = 1:numel(tc.ref.sobol)
                m = tc.R.sobol(i); q = tc.ref.sobol(i);
                tol1 = hypot((m.S1_hi - m.S1_lo)/2, (q.S1_hi - q.S1_lo)/2) + 0.005;
                tolT = hypot((m.ST_hi - m.ST_lo)/2, (q.ST_hi - q.ST_lo)/2) + 0.005;
                tc.verifyEqual(m.S1, q.S1, 'AbsTol', tol1, q.name);
                tc.verifyEqual(m.ST, q.ST, 'AbsTol', tolT, q.name);
            end
            [~, iM] = max([tc.R.sobol.S1]); [~, iP] = max([tc.ref.sobol.S1]);
            tc.verifyEqual(iM, iP, 'dominant input differs');
        end

        function dynamicScenarioIsIdentical(tc)
            for k = 1:2
                d = tc.R.dynamic(k); q = tc.ref.dynamic(k);
                tc.verifyEqual([d.n_transmit d.n_measure d.n_sleep d.n_anomaly], ...
                               [q.n_transmit q.n_measure q.n_sleep q.n_anomaly]);
                tc.verifyEqual(d.event_t_h(:), q.event_t_h(:), 'AbsTol', 1e-9);
                tc.verifyEqual(d.event_action(:), q.event_action(:));
                tc.verifyEqual(d.event_v_before(:), q.event_v_before(:), 'AbsTol', 1e-9);
                tc.verifyEqual([d.v_min d.v_max d.soc_min d.soc_max], [q.v_min q.v_max q.soc_min q.soc_max], 'AbsTol', 1e-9);
            end
        end
    end
end
