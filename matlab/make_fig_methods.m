function make_fig_methods(out)
%MAKE_FIG_METHODS How the three data-driven methods work: Monte Carlo and Sobol (primary) and the Isolation
%   Forest (secondary). Each column shows three steps with a small graphic; the Sobol bars and the hold-out
%   F1 values are the results reported in the paper (matlab_results.json), the scatter and tree are schematic.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures'); end
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
INK = h('#0b0b0b'); INK2 = h('#52514e'); MUTE = h('#a8a6a0'); RULE = h('#e4e2dc'); BLUE = h('#1e78d2');
LBLUE = h('#8dccfc'); GREY = h('#c9c7c1'); PALE = h('#f4f8fb');
R = jsondecode(fileread(fullfile(here, 'matlab_results.json')));
FW = 7.4; FH = 4.8;
f = figure('Units', 'inches', 'Position', [1 1 FW FH], 'Color', 'w', 'Visible', 'off');
A = axes(f, 'Position', [0 0 1 1]); hold(A, 'on'); axis(A, [0 1 0 1]); axis(A, 'off');
    function tx(x, y, s, sz, col, varargin)
        text(A, x, y, s, 'FontName', 'Arial', 'FontSize', sz, 'Color', col, 'Interpreter', 'none', varargin{:});
    end
    function ax = mini(x, y, w, hh)
        ax = axes(f, 'Position', [x y w hh]); hold(ax, 'on');
        set(ax, 'FontName', 'Arial', 'FontSize', 5.2, 'Box', 'off', 'TickDir', 'out', 'LineWidth', 0.5, 'XColor', INK2, 'YColor', INK2, ...
            'Color', 'none', 'TickLabelInterpreter', 'none', 'TickLength', [0.03 0.03]);
    end
    function down(x, y0, y1, col)
        plot(A, [x x], [y0 y1], '-', 'Color', col, 'LineWidth', 1.0);
        patch(A, [x x - 0.007 x + 0.007], [y1 y1 + 0.02 y1 + 0.02], col, 'EdgeColor', 'none');
    end
CX = [0.025 0.355 0.685]; CW = 0.3; SY = [0.655 0.415 0.175]; SH = 0.2;
heads = {'Monte Carlo', 'Sobol indices', 'Isolation Forest'};
subs = {'distribution of Δt', 'which input drives r*', 'secondary AI layer'};
for c = 1:3
    col = BLUE; if c == 3, col = MUTE; end
    tx(CX(c) + CW/2, 0.955, heads{c}, 8.6, col, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
    tx(CX(c) + CW/2, 0.905, subs{c}, 6.4, INK2, 'HorizontalAlignment', 'center');
    for s = 1:3
        ls = '-'; if c == 3, ls = '--'; end
        fc = 'w'; if s == 3 && c < 3, fc = PALE; end
        rectangle(A, 'Position', [CX(c) SY(s) CW SH], 'FaceColor', fc, 'EdgeColor', col, 'LineWidth', 0.8, 'LineStyle', ls, 'Curvature', 0.04);
        tx(CX(c) + 0.012, SY(s) + SH - 0.022, sprintf('%d', s), 8, col, 'FontWeight', 'bold', 'VerticalAlignment', 'top');
        if s < 3, down(CX(c) + CW/2, SY(s), SY(s + 1) + SH, col); end
    end
end
plot(A, [0.67 0.67], [0.08 0.93], '-', 'Color', RULE, 'LineWidth', 0.8);
% ---------------- Monte Carlo
rng(7); ax = mini(CX(1) + 0.035, SY(1) + 0.035, 0.11, SH - 0.06);
scatter(ax, lognrnd(0, 0.2, 90, 1), (0.71 + 0.25*betarnd(5, 2, 90, 1)).*(0.86 + 0.07*betarnd(4, 3, 90, 1)), 5, BLUE, 'filled', 'MarkerFaceAlpha', 0.7);
xlabel(ax, 'P_MFC', 'Interpreter', 'none'); ylabel(ax, 'η'); set(ax, 'XTick', [], 'YTick', []);
tx(CX(1) + 0.16, SY(1) + SH/2, {'draw the six inputs', 'x_k ~ f(x), k = 1…N', 'N = 20,000'}, 6.2, INK, 'VerticalAlignment', 'middle');
text(A, CX(1) + CW/2, SY(2) + SH/2 + 0.02, '$\Delta t_k=\frac{E_{\mathrm{event}}(x_k)}{P_{\mathrm{net}}(x_k)}$', 'Interpreter', 'latex', 'FontSize', 9.6, 'HorizontalAlignment', 'center');
tx(CX(1) + CW/2, SY(2) + 0.035, 'closed-form model, Eqs. (3), (7), (8)', 6.0, INK2, 'HorizontalAlignment', 'center');
dt = ec.mc_interval(); q = prctile(dt, [5 50 95]);
ax = mini(CX(1) + 0.035, SY(3) + 0.05, CW - 0.06, SH - 0.08);
hc = histcounts(dt, linspace(0.5, 6, 45)); yl = [0 max(hc)*1.2];
patch(ax, [q(1) q(3) q(3) q(1)], [0 0 yl(2) yl(2)], LBLUE, 'EdgeColor', 'none', 'FaceAlpha', 0.45);
histogram(ax, dt, linspace(0.5, 6, 45), 'FaceColor', BLUE, 'EdgeColor', 'none', 'FaceAlpha', 1);
plot(ax, [q(2) q(2)], yl, '-', 'Color', INK, 'LineWidth', 0.9); ylim(ax, yl); xlim(ax, [0.5 6]); set(ax, 'YTick', []);
xlabel(ax, 'Δt (h)'); text(ax, q(2) + 0.1, yl(2)*0.9, sprintf('median %.2f h', q(2)), 'FontName', 'Arial', 'FontSize', 5.6, 'Color', INK);
text(ax, 5.9, yl(2)*0.62, '5–95% band', 'FontName', 'Arial', 'FontSize', 5.6, 'Color', INK2, 'HorizontalAlignment', 'right');
% ---------------- Sobol
for m = 1:3
    x0 = CX(2) + 0.03 + (m - 1)*0.068; y0 = SY(1) + 0.04;
    for i = 1:6
        for j = 1:5
            fcol = GREY; if m == 2, fcol = LBLUE; end
            if m == 3, fcol = GREY; if i == 3, fcol = LBLUE; end, end
            rectangle(A, 'Position', [x0 + (i - 1)*0.0085, y0 + (j - 1)*0.022, 0.0078, 0.02], 'FaceColor', fcol, 'EdgeColor', 'none');
        end
    end
end
tx(CX(2) + 0.055, SY(1) + 0.022, 'A', 6.6, INK, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
tx(CX(2) + 0.123, SY(1) + 0.022, 'B', 6.6, INK, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
text(A, CX(2) + 0.191, SY(1) + 0.022, '$A_B^{(i)}$', 'Interpreter', 'latex', 'FontSize', 7.6, 'HorizontalAlignment', 'center');
tx(CX(2) + 0.232, SY(1) + SH/2, {'N × k', 'matrices,', 'column i', 'from B'}, 5.8, INK2, 'VerticalAlignment', 'middle');
text(A, CX(2) + CW/2, SY(2) + SH/2 + 0.025, '$S_i=\frac{V\left(E(Y\mid X_i)\right)}{V(Y)}$', 'Interpreter', 'latex', 'FontSize', 9.0, 'HorizontalAlignment', 'center');
tx(CX(2) + CW/2, SY(2) + 0.035, 'N(k + 2) = 524,288 runs of r*, Eq. (9)', 6.0, INK2, 'HorizontalAlignment', 'center');
S = R.sobol; nm = {S.name}; s1 = [S.S1]; stt = [S.ST];
short = containers.Map({'Harvested power', 'Active duration', 'PMIC efficiency', 'Supercap leakage', 'Sensor current', 'Sleep floor'}, ...
    {'P_MFC', 't_active', 'η_PMIC', 'P_leak', 'I_sens', 'P_floor'});
lab = cellfun(@(x) short(x), nm, 'UniformOutput', false);
ax = mini(CX(2) + 0.085, SY(3) + 0.03, CW - 0.11, SH - 0.05);
bh = barh(ax, 1:6, [s1; stt]', 1.0, 'grouped', 'EdgeColor', 'none'); bh(1).FaceColor = LBLUE; bh(2).FaceColor = BLUE;
set(ax, 'YDir', 'reverse', 'YTick', 1:6, 'YTickLabel', lab, 'XLim', [0 0.8], 'XTick', [0 0.4 0.8]);
legend(ax, {'S_1', 'S_T'}, 'Box', 'off', 'FontSize', 5.4, 'Location', 'southeast', 'Interpreter', 'none');
% ---------------- Isolation Forest
rng(3); ax = mini(CX(3) + 0.03, SY(1) + 0.03, 0.12, SH - 0.05);
pts = randn(70, 2)*0.6; scatter(ax, pts(:, 1), pts(:, 2), 4, GREY, 'filled');
scatter(ax, 2.3, 1.9, 14, INK, 'filled');
plot(ax, [1.6 1.6], [-2.2 2.6], '--', 'Color', MUTE, 'LineWidth', 0.7); plot(ax, [1.6 3], [1.2 1.2], '--', 'Color', MUTE, 'LineWidth', 0.7);
xlim(ax, [-2 3]); ylim(ax, [-2.2 2.6]); set(ax, 'XTick', [], 'YTick', []);
tx(CX(3) + 0.165, SY(1) + SH/2, {'random axis-', 'parallel splits;', 'the outlier is', 'isolated in 2'}, 5.8, INK2, 'VerticalAlignment', 'middle');
ax = mini(CX(3) + 0.03, SY(2) + 0.025, 0.15, SH - 0.05); axis(ax, 'off'); axis(ax, [0 1 0 1]);
nodes = [0.5 0.92; 0.25 0.7; 0.75 0.7; 0.12 0.48; 0.38 0.48; 0.3 0.26; 0.46 0.26; 0.4 0.05];
edges = [1 2; 1 3; 2 4; 2 5; 5 6; 5 7; 7 8];
for e = 1:size(edges, 1), plot(ax, nodes(edges(e, :), 1), nodes(edges(e, :), 2), '-', 'Color', GREY, 'LineWidth', 0.8); end
plot(ax, nodes(:, 1), nodes(:, 2), 'o', 'MarkerSize', 3, 'MarkerFaceColor', GREY, 'MarkerEdgeColor', 'none');
plot(ax, nodes([1 3], 1), nodes([1 3], 2), '-', 'Color', INK, 'LineWidth', 1.4); plot(ax, nodes(3, 1), nodes(3, 2), 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', INK, 'MarkerEdgeColor', 'none');
text(ax, 0.82, 0.62, 'h = 1', 'FontName', 'Arial', 'FontSize', 5.6, 'Color', INK);
text(ax, 0.5, 0.0, 'h = 4', 'FontName', 'Arial', 'FontSize', 5.6, 'Color', INK2);
text(A, CX(3) + 0.235, SY(2) + SH/2 + 0.02, '$s=2^{-\frac{E[h(x)]}{c(\psi)}}$', 'Interpreter', 'latex', 'FontSize', 8.6, 'HorizontalAlignment', 'center');
tx(CX(3) + 0.235, SY(2) + 0.035, 'Liu et al.', 6.0, INK2, 'HorizontalAlignment', 'center');
ax = mini(CX(3) + 0.09, SY(3) + 0.06, CW - 0.12, SH - 0.085);
F = [R.anomaly.holdout_isolation_forest.f1, R.anomaly.holdout_threshold_z3.f1];
bb = barh(ax, 1:2, F, 0.55, 'FaceColor', 'flat', 'EdgeColor', 'none'); bb.CData = [MUTE; GREY];
set(ax, 'YDir', 'reverse', 'YTick', 1:2, 'YTickLabel', {'forest', '3σ rule'}, 'XLim', [0.8 1], 'XTick', [0.8 0.9 1]);
for i = 1:2, text(ax, F(i) + 0.004, i, sprintf('%.3f', F(i)), 'FontName', 'Arial', 'FontSize', 5.6, 'Color', INK2, 'VerticalAlignment', 'middle'); end
xlabel(ax, 'hold-out F1 (synthetic)');
tx(0.5, 0.06, 'Steps 3 of Monte Carlo and Sobol and the F1 values are results of this study; the Isolation Forest scatter and tree are schematic.', 5.8, INK2, 'HorizontalAlignment', 'center');
exportgraphics(f, fullfile(out, 'fig_methods_no_rf.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'fig_methods_no_rf.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
end
