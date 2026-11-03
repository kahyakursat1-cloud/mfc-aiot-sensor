function make_fig_hoca(out)
%MAKE_FIG_HOCA Figures 13-17, 19 and 20 of the submission version in the look chosen by the co-author
%   (navy title bands, saturated blue), drawn from the model and the measured record, so that the
%   styling cannot move a data point. The aspect ratio of each figure matches its frame in the draft.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures', 'v30'); end
addpath(here);
if ~exist(out, 'dir'), mkdir(out); end
set(groot, 'defaultTextInterpreter', 'none', 'defaultAxesTickLabelInterpreter', 'none', ...
    'defaultLegendInterpreter', 'none', 'defaultAxesFontName', 'Arial', 'defaultTextFontName', 'Arial');
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
C.NAVY = h('#003a84'); C.BLUE = h('#1e78d2'); C.LB = h('#8dccfc'); C.PALE = h('#dbecfc'); C.INK = h('#0b0b0b');
C.INK2 = h('#3c3c3c'); C.GREY = h('#b4b4b4'); C.DG = h('#7a7a7a'); C.RULE = h('#e2e2e2');
C.case.ideal = {C.DG, '--', 1.3}; C.case.realistic = {C.BLUE, '-', 2.0}; C.case.conservative = {C.INK, ':', 1.7};
fig13(out, C); fig14(out, C); fig15(out, C); fig16(out, C); fig17(out, C); fig18(out, C); fig19(out, C); fig20(out, C);
end

% ------------------------------------------------------------------ layout
function [f, A] = canvas(w, ratio)
f = figure('Units', 'inches', 'Position', [1 1 w w/ratio], 'Color', 'w', 'Visible', 'off');
A = axes(f, 'Position', [0 0 1 1]); hold(A, 'on'); axis(A, [0 1 0 1]); axis(A, 'off');
end

function band(A, C, x, y, w, hg, bh, s, fs)
rectangle(A, 'Position', [x y w hg], 'EdgeColor', C.NAVY, 'LineWidth', 1.1, 'FaceColor', 'w', 'Curvature', [0.012 0.02]);
rectangle(A, 'Position', [x y + hg - bh w bh], 'EdgeColor', C.NAVY, 'FaceColor', C.NAVY, 'Curvature', [0.012 0.08]);
text(A, x + w/2, y + hg - bh/2, s, 'FontSize', fs, 'FontWeight', 'bold', 'Color', 'w', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
end

function sty(ax, C, g)
if nargin < 3, g = 'y'; end
set(ax, 'Box', 'off', 'TickDir', 'out', 'LineWidth', 0.7, 'XColor', C.INK, 'YColor', C.INK, 'FontSize', 7.4, 'GridColor', C.RULE, 'GridAlpha', 1, 'Layer', 'bottom');
ax.XLabel.Color = C.INK; ax.YLabel.Color = C.INK; ax.XLabel.FontSize = 7.8; ax.YLabel.FontSize = 7.8;
ax.YGrid = matlab.lang.OnOffSwitchState(contains(g, 'y')); ax.XGrid = matlab.lang.OnOffSwitchState(contains(g, 'x'));
ax.XMinorGrid = 'off'; ax.YMinorGrid = 'off';
end

function callout(ax, C, x, y, s, varargin)
text(ax, x, y, s, 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'BackgroundColor', C.PALE, 'EdgeColor', C.BLUE, ...
    'Margin', 2.5, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', varargin{:});
end

function save(f, out, name)
exportgraphics(f, fullfile(out, name), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, strrep(name, '.png', '.pdf')), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
end

% ------------------------------------------------------------------ Figure 13
function fig13(out, C)
[f, ~] = canvas(5.6, 1.809);
ax = axes(f, 'Position', [0.09 0.125 0.895 0.855]); hold(ax, 'on');
Pw = linspace(35, 500, 300);
patch(ax, [15 30 30 15], [0.1 0.1 100 100], C.GREY, 'FaceAlpha', 0.45, 'EdgeColor', 'none', 'HandleVisibility', 'off');
cs = {'ideal', 'realistic', 'conservative'};
for k = 1:3
    d = arrayfun(@(p) ec.interval_h('lean', p*1e-6, cs{k}), Pw); d(~isfinite(d)) = NaN; s = C.case.(cs{k});
    plot(ax, Pw, d, 'Color', s{1}, 'LineStyle', s{2}, 'LineWidth', s{3}, 'DisplayName', cs{k});
end
xline(ax, 33, '--', 'Color', C.DG, 'LineWidth', 0.8, 'HandleVisibility', 'off');
xline(ax, 49.5, ':', 'Color', C.BLUE, 'LineWidth', 1.0, 'HandleVisibility', 'off');
xline(ax, 150, ':', 'Color', C.DG, 'LineWidth', 0.8, 'HandleVisibility', 'off');
yline(ax, 1/6, '--', 'Color', C.INK, 'LineWidth', 0.8, 'HandleVisibility', 'off');
text(ax, 495, 0.185, '10-min target', 'FontSize', 7, 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(ax, 22.5, 0.24, 'single cell 15–30 µW', 'FontSize', 6.2, 'Color', C.INK, 'Rotation', 90);
text(ax, 35, 0.24, 'ideal floor 33 µW', 'FontSize', 6.2, 'Color', C.INK, 'Rotation', 90, 'VerticalAlignment', 'top');
text(ax, 52, 0.24, 'realistic floor ~50 µW', 'FontSize', 6.2, 'Color', C.NAVY, 'Rotation', 90, 'VerticalAlignment', 'top');
y150 = ec.interval_h('lean', 150e-6, 'realistic');
plot(ax, [150 205], [y150 9], '-', 'Color', C.INK, 'LineWidth', 0.7, 'HandleVisibility', 'off');
text(ax, 207, 9, '150 µW multi-cell target', 'FontSize', 7, 'Color', C.INK);
callout(ax, C, 165, 30, sprintf('Realistic floor ~50 µW,\nTarget 150 µW'));
set(ax, 'YScale', 'log'); ylim(ax, [0.1 100]); xlim(ax, [10 520]);
xlabel(ax, 'Mean MFC power at PMIC input (µW)'); ylabel(ax, 'Min. sustainable lean interval (h)');
lg = legend(ax, 'Location', 'northeast', 'Box', 'off', 'FontSize', 7); title(lg, 'power path'); sty(ax, C);
save(f, out, 'fig13.png');
end

% ------------------------------------------------------------------ Figure 14
function fig14(out, C)
[f, ~] = canvas(5.8, 2.098);
ax = axes(f, 'Position', [0.08 0.14 0.905 0.84]); hold(ax, 'on');
P = ec.params(); c = P.cases.realistic; eb = P.ETA_BUCK; Cb = 0.5; Vmax = 5; Vmin = 3.5; dt = 30;
n = round(6*3600/dt) + 1; t = (0:n - 1)*dt/3600;
Pb = c.eta/eb*150e-6 - P.P_FLOOR/eb - c.pq - c.pleak; Ee = ec.e_event('lean')/eb;
E = 0.5*Cb*3.6^2; V = zeros(1, n); nxt = 2.26*3600; ev = []; vtop = [];
for i = 1:n
    if (i - 1)*dt >= nxt && E >= Ee
        vtop(end + 1) = sqrt(2*E/Cb); E = E - Ee; ev(end + 1) = (i - 1)*dt/3600; nxt = nxt + 2.26*3600; %#ok<AGROW>
    end
    E = min(E + Pb*dt, 0.5*Cb*Vmax^2);
    V(i) = sqrt(2*E/Cb);
end
usable = 0.5*Cb*(Vmax^2 - Vmin^2);
patch(ax, [0 6 6 0], [Vmin Vmin Vmax Vmax], C.PALE, 'FaceAlpha', 0.55, 'EdgeColor', 'none');
patch(ax, [t fliplr(t)], [V Vmin*ones(1, n)], C.LB, 'FaceAlpha', 0.55, 'EdgeColor', 'none');
for k = 1:numel(ev), plot(ax, [ev(k) ev(k)], [3.3 5.2], ':', 'Color', C.DG, 'LineWidth', 0.8); end
yline(ax, Vmax, '--', 'Color', C.NAVY, 'LineWidth', 1.0); yline(ax, Vmin, '--', 'Color', C.NAVY, 'LineWidth', 1.0);
plot(ax, t, V, 'Color', C.BLUE, 'LineWidth', 2.2);
plot(ax, ev, vtop, 'o', 'MarkerSize', 5.5, 'MarkerFaceColor', C.NAVY, 'MarkerEdgeColor', 'w', 'LineWidth', 0.7);
text(ax, 0.06, Vmax + 0.03, 'V_max 5.0 V', 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'VerticalAlignment', 'bottom');
text(ax, 0.06, Vmin - 0.03, 'buck-dropout floor 3.5 V', 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'VerticalAlignment', 'top');
text(ax, 5.94, 4.87, sprintf('Usable window 3.5–5.0 V, ≈%.1f J', usable), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
ya = 4.66;
plot(ax, ev(1:2), [ya ya], '-', 'Color', C.NAVY, 'LineWidth', 1.0);
plot(ax, ev(1) + 0.03, ya, '<', 'MarkerSize', 4, 'MarkerFaceColor', C.NAVY, 'MarkerEdgeColor', C.NAVY);
plot(ax, ev(2) - 0.03, ya, '>', 'MarkerSize', 4, 'MarkerFaceColor', C.NAVY, 'MarkerEdgeColor', C.NAVY);
text(ax, mean(ev(1:2)), ya + 0.02, sprintf('Δt = %.2f h', ev(2) - ev(1)), 'FontSize', 7.2, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
callout(ax, C, 1.18, 4.42, sprintf('Lean event discharge\n%.2f J drawn from the bank', Ee));
plot(ax, [1.72 ev(1) - 0.09], [4.28 vtop(1) + 0.03], '-', 'Color', C.BLUE, 'LineWidth', 0.9);
callout(ax, C, 3.4, 4.32, sprintf('Continuous MFC charging\n≈%.0f µW into the bank', Pb*1e6));
plot(ax, [3.4 3.4], [4.18 3.79], '-', 'Color', C.BLUE, 'LineWidth', 0.9);
xlabel(ax, 'Time (h)'); ylabel(ax, 'Storage-bank voltage (V)'); ylim(ax, [3.3 5.2]); xlim(ax, [0 6]); sty(ax, C, '');
save(f, out, 'fig14.png');
end

% ------------------------------------------------------------------ Figure 15
function fig15(out, C)
[f, A] = canvas(7.4, 2.076);
bx = [0.006 0.505]; by = [0.51 0.01]; bw = 0.489; bh = 0.48; tb = 0.085;
band(A, C, bx(1), by(1), bw, bh, tb, '(a) Tornado: Δt sensitivity', 9);
band(A, C, bx(2), by(1), bw, bh, tb, '(b) Monte Carlo (N = 20000)', 9);
band(A, C, bx(1), by(2), bw, bh, tb, '(c) Payload cost (realistic)', 9);
band(A, C, bx(2), by(2), bw, bh, tb, '(d) LoRa-burst voltage sag', 9);
P = ec.params(); El = ec.e_event('lean'); base = ec.interval_h('lean', 150e-6, 'realistic');
dtf = @(pm, es, eta, pl) El*es/(eta*pm - P.P_FLOOR - 1.6e-6 - pl)/3600;
rows = {'Harvested P ±20%', dtf(180e-6, 1, .8, 5e-6), dtf(120e-6, 1, .8, 5e-6);
        'Active-wake ±30%', dtf(150e-6, .76, .8, 5e-6), dtf(150e-6, 1.24, .8, 5e-6);
        'PMIC eff. 0.72–0.88', dtf(150e-6, 1, .88, 5e-6), dtf(150e-6, 1, .72, 5e-6);
        'Leakage 1–15 µW', dtf(150e-6, 1, .8, 1e-6), dtf(150e-6, 1, .8, 15e-6)};
[~, o] = sort(abs(cell2mat(rows(:, 3)) - cell2mat(rows(:, 2)))); rows = rows(o, :);
ax = axes(f, 'Position', [bx(1) + 0.135, by(1) + 0.095, bw - 0.155, bh - tb - 0.125]); hold(ax, 'on');
for k = 1:4
    lo = min(rows{k, 2}, rows{k, 3}); hi = max(rows{k, 2}, rows{k, 3});
    patch(ax, [lo hi hi lo], k - 1 + [-0.3 -0.3 0.3 0.3], C.BLUE, 'EdgeColor', 'none');
end
xline(ax, base, '--', 'Color', C.NAVY, 'LineWidth', 1.1);
text(ax, base, 3.62, sprintf('baseline %.2f h', base), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
v = cell2mat(rows(:, 2:3)); set(ax, 'YTick', 0:3, 'YTickLabel', rows(:, 1), 'TickLength', [0 0]);
ylim(ax, [-0.6 4.1]); xlim(ax, [min(v(:)) - 0.12, max(v(:)) + 0.12]); xlabel(ax, 'Realistic lean interval Δt (h)'); sty(ax, C, 'x');
ax = axes(f, 'Position', [bx(2) + 0.05, by(1) + 0.095, bw - 0.07, bh - tb - 0.125]); hold(ax, 'on');
rng(42, 'twister'); dt = ec.mc_interval(); lo = prctile(dt, 5); hi = prctile(dt, 95); med = median(dt);
histogram(ax, dt, 'BinEdges', linspace(0, 6, 51), 'Normalization', 'pdf', 'FaceColor', C.LB, 'EdgeColor', 'w', 'LineWidth', 0.3);
yl = [0 0.6]; patch(ax, [lo hi hi lo], [0 0 yl(2) yl(2)], C.PALE, 'EdgeColor', 'none'); uistack(findobj(ax, 'Type', 'histogram'), 'top');
xs = linspace(0, 6, 250); plot(ax, xs, ksdensity(dt, xs), 'Color', C.BLUE, 'LineWidth', 1.6);
xline(ax, med, 'Color', C.INK, 'LineWidth', 1.0);
text(ax, med + 0.08, yl(2)*0.95, sprintf('median %.2f h', med), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.INK, 'VerticalAlignment', 'top');
text(ax, 5.1, yl(2)*0.6, sprintf('5–95%%\n[%.2f, %.2f] h', lo, hi), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center');
xlim(ax, [0 6]); ylim(ax, yl); xlabel(ax, 'Realistic lean interval Δt (h)'); ylabel(ax, 'Probability density'); sty(ax, C);
ax = axes(f, 'Position', [bx(1) + 0.05, by(2) + 0.095, bw - 0.07, bh - tb - 0.125]); hold(ax, 'on');
pls = {'lean', 'lowgas', 'sgp30', 'mq135'}; iv = cellfun(@(p) ec.interval_h(p, 150e-6, 'realistic'), pls);
cols = [C.BLUE; C.LB; C.GREY; C.NAVY];
for k = 1:4
    patch(ax, k + [-0.3 0.3 0.3 -0.3], [1 1 iv(k) iv(k)], cols(k, :), 'EdgeColor', 'none');
    text(ax, k, iv(k)*1.12, sprintf('%.1f h', iv(k)), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
end
set(ax, 'YScale', 'log', 'XTick', 1:4, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Lean', 'SGP30\newline(12 ms)', 'SGP30 +\newlinewarm-up', 'MQ-135\newlinestress'}, 'TickLength', [0 0], 'XTickLabelRotation', 0);
ylim(ax, [1 300]); xlim(ax, [0.4 4.6]); ylabel(ax, 'Realistic interval (h)'); sty(ax, C);
ax = axes(f, 'Position', [bx(2) + 0.05, by(2) + 0.095, bw - 0.07, bh - tb - 0.125]); hold(ax, 'on');
esr = linspace(0, 20, 120); plot(ax, esr, 5 - P.I_TX*esr, 'Color', C.BLUE, 'LineWidth', 1.9);
yline(ax, 3.5, '--', 'Color', C.INK, 'LineWidth', 0.8); xline(ax, 12.5, ':', 'Color', C.DG, 'LineWidth', 1.0);
text(ax, 0.3, 3.55, '3.5 V buck-dropout floor', 'FontSize', 7, 'Color', C.INK, 'VerticalAlignment', 'bottom');
text(ax, 13, 4.45, 'R_ESR,max ≈ 12.5 Ω', 'FontSize', 7, 'Color', C.INK);
text(ax, 2.6, 4.82, 'terminal V from 5.0 V', 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY);
ylim(ax, [2.8 5.1]); xlabel(ax, 'Series ESR (Ω)'); ylabel(ax, 'Terminal voltage (V)'); sty(ax, C);
save(f, out, 'fig15.png');
end

% ------------------------------------------------------------------ Figure 16
function fig16(out, C)
[f, ~] = canvas(5.6, 1.481);
root = fileparts(fileparts(mfilename('fullpath')));
tr = readtable(fullfile(root, 'external', 'yen_smfc_trace_5min.csv'));
day = floor(tr.t_s/86400); nd = max(day) + 1;
dm = accumarray(day + 1, tr.p_cell_W*1e6, [nd 1], @mean); d = (0:nd-1)';
a1 = axes(f, 'Position', [0.115 0.575 0.865 0.405]); hold(a1, 'on');
patch(a1, [-5 170 170 -5], [15 15 30 30], C.GREY, 'FaceAlpha', 0.45, 'EdgeColor', 'none');
plot(a1, d, max(dm, 0.01), 'Color', C.BLUE, 'LineWidth', 1.4);
text(a1, 1, 33, '15–30 µW assumed in this work', 'FontSize', 6.6, 'Color', C.INK, 'VerticalAlignment', 'bottom');
set(a1, 'YScale', 'log', 'YTick', [0.01 0.1 1 10 100], 'YTickLabel', {'≤0.01', '0.1', '1', '10', '100'});
ylim(a1, [0.01 400]); xlim(a1, [-5 165]); ylabel(a1, sprintf('Single-cell power,\ndaily mean (µW)')); sty(a1, C);
plot(a1, [122 118], [1.2 13], '-', 'Color', C.BLUE, 'LineWidth', 0.8); callout(a1, C, 135, 0.9, 'Power < 30 µW');
text(a1, -0.115, 1.0, '(a)', 'Units', 'normalized', 'FontSize', 8, 'FontWeight', 'bold');
a2 = axes(f, 'Position', [0.115 0.09 0.865 0.365]); hold(a2, 'on'); P = ec.params();
cfg = {0.5, [], C.BLUE, '-', 1.4, '0.5 F bank'; 5.0, [], C.INK, '--', 1.0, '5 F, leakage 5 µW'; 5.0, 5*P.LEAK_PER_F, C.DG, ':', 1.1, '5 F, leakage 50 µW (scaled with C)'};
for k = 1:3
    r = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, cfg{k, 1}, 5.0, 3.5, 0.05, cfg{k, 2});
    on = accumarray(day + 1, double(r.on), [nd 1], @mean);
    plot(a2, d, on, 'Color', cfg{k, 3}, 'LineStyle', cfg{k, 4}, 'LineWidth', cfg{k, 5}, 'DisplayName', cfg{k, 6});
end
ylim(a2, [-0.05 1.05]); xlim(a2, [-5 165]); ylabel(a2, sprintf('Fraction of day\nthe node is on')); xlabel(a2, 'Day of the 161-day record');
legend(a2, 'Location', 'northoutside', 'Orientation', 'horizontal', 'Box', 'off', 'FontSize', 7); sty(a2, C);
text(a2, -0.115, 1.0, '(b)', 'Units', 'normalized', 'FontSize', 8, 'FontWeight', 'bold');
save(f, out, 'fig16.png');
end

% ------------------------------------------------------------------ Figure 17
function fig17(out, C)
[f, ~] = canvas(6.2, 2.036);
S = ec.dynamic_scenario(1.9); th = S.t/3600;
a1 = axes(f, 'Position', [0.105 0.72 0.87 0.26]); hold(a1, 'on');
plot(a1, th, S.p*1e6, 'Color', C.INK, 'LineWidth', 1.3); yline(a1, 150, ':', 'Color', C.DG, 'LineWidth', 0.9);
text(a1, 71.5, 152, 'daily mean 150 µW', 'FontSize', 6.6, 'FontWeight', 'bold', 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
ylim(a1, [100 200]); xlim(a1, [0 72]); ylabel(a1, sprintf('Harvested\npower (µW)')); set(a1, 'XTickLabel', []); sty(a1, C);
a2 = axes(f, 'Position', [0.105 0.125 0.87 0.565]); hold(a2, 'on');
plot(a2, th, S.v, 'Color', C.DG, 'LineWidth', 0.8, 'HandleVisibility', 'off');
yline(a2, 5, '--', 'Color', C.INK, 'LineWidth', 0.8, 'HandleVisibility', 'off'); yline(a2, 3.5, '--', 'Color', C.INK, 'LineWidth', 0.8, 'HandleVisibility', 'off');
text(a2, 71.5, 5.02, 'V_max 5.0 V', 'FontSize', 6.4, 'FontWeight', 'bold', 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(a2, 71.5, 3.52, 'buck-dropout floor 3.5 V', 'FontSize', 6.4, 'FontWeight', 'bold', 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
fr = [0.25 0.55]; lb = {'SoC 0.25 (sleep below)', 'SoC 0.55 (measure below)'};
for k = 1:2
    vth = sqrt(2*(S.e_min + fr(k)*(S.e_max - S.e_min))/0.5); yline(a2, vth, ':', 'Color', C.DG, 'LineWidth', 0.8, 'HandleVisibility', 'off');
    text(a2, 0.5, vth + 0.01, lb{k}, 'FontSize', 5.8, 'Color', C.INK, 'VerticalAlignment', 'bottom');
end
E = S.events; key = {'transmit', 'measure', 'sleep', 'anomaly'}; lab = {'transmit', 'measure (store)', 'sleep (recharge)', 'anomaly override'};
for k = 1:4
    m = strcmp(E.action, key{k}); if ~any(m), continue; end
    switch k
        case 1, scatter(a2, E.t_h(m), E.v_before(m), 16, C.BLUE, 'filled', 'DisplayName', lab{k});
        case 2, scatter(a2, E.t_h(m), E.v_before(m), 16, C.INK, 'MarkerFaceColor', 'w', 'LineWidth', 0.7, 'DisplayName', lab{k});
        case 3, scatter(a2, E.t_h(m), E.v_before(m), 20, C.INK, 'x', 'LineWidth', 0.9, 'DisplayName', lab{k});
        case 4, scatter(a2, E.t_h(m), E.v_before(m), 55, C.INK, 'p', 'filled', 'DisplayName', lab{k});
    end
end
legend(a2, 'Location', 'north', 'Orientation', 'horizontal', 'Box', 'off', 'FontSize', 6.4);
ylim(a2, [3.3 5.55]); xlim(a2, [0 72]); xlabel(a2, 'Time (h)'); ylabel(a2, sprintf('Storage-bank\nvoltage (V)')); sty(a2, C);
save(f, out, 'fig17.png');
end

% ------------------------------------------------------------------ Figure 18
function fig18(out, C)
[f, A] = canvas(6.8, 2.1);
band(A, C, 0.006, 0.015, 0.489, 0.97, 0.11, '(a) Reported open-circuit voltage', 9);
band(A, C, 0.505, 0.015, 0.489, 0.97, 0.11, '(b) Power density at load', 9);
ax = axes(f, 'Position', [0.07 0.15 0.41 0.69]); hold(ax, 'on'); ocv = [0.733 0.75]; ol = {'0.73', '0.75'};
b = bar(ax, 1:2, ocv, 0.5, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = repmat(C.GREY, 2, 1);
for k = 1:2, text(ax, k, ocv(k) + 0.02, ol{k}, 'FontSize', 8, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom'); end
set(ax, 'XTick', 1:2, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Zheng\newlineet al.', 'Zhang\newlineet al.'}, 'TickLength', [0 0], 'XTickLabelRotation', 0);
ylim(ax, [0 1]); xlim(ax, [0.4 2.6]); ylabel(ax, 'Open-circuit voltage (V)'); sty(ax, C);
ax = axes(f, 'Position', [0.57 0.15 0.41 0.69]); hold(ax, 'on'); pd = [3.0 4.3 17.4 2.1 1.8];
b = bar(ax, 1:5, pd, 0.6, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = [C.GREY; C.GREY; C.GREY; C.GREY; C.BLUE];
errorbar(ax, 5, 1.8, 0.6, 0.6, 'LineStyle', 'none', 'Color', C.INK, 'LineWidth', 0.8, 'CapSize', 4);
lab = {'3', '4.3', '17.4', '2.1', '1.2–2.4'}; top = [3.0 4.3 17.4 2.1 2.4];
for k = 1:5, text(ax, k, top(k) + 0.3, lab{k}, 'FontSize', 8, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom'); end
set(ax, 'XTick', 1:5, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Zhang\newlinepeak', 'Yang\newlinepeak', 'Yen bench.\newlinepeak', 'Yen v3\newlinemean', 'This\newlinework'}, 'TickLength', [0 0], 'XTickLabelRotation', 0);
ylim(ax, [0 20]); xlim(ax, [0.4 5.6]); ylabel(ax, 'Power density (mW/m²)'); sty(ax, C);
save(f, out, 'fig18.png');
end

% ------------------------------------------------------------------ Figure 19
function fig19(out, C)
[f, A] = canvas(6.8, 2.915);
band(A, C, 0.006, 0.015, 0.489, 0.97, 0.13, '(a) Pareto: resolution vs gas coverage', 9);
band(A, C, 0.505, 0.015, 0.489, 0.97, 0.13, '(b) Min. cells (loss-aware)', 9);
P = ec.params(); Pn = ec.p_net(150e-6, 'realistic'); El = ec.e_event('lean'); Ef = ec.e_event('mq135');
ax = axes(f, 'Position', [0.095 0.2 0.385 0.6]); hold(ax, 'on');
fr = linspace(0, 1, 200); tot = Pn./((1 - fr)*El + fr*Ef)*86400;
plot(ax, tot, fr.*tot, 'Color', C.BLUE, 'LineWidth', 1.9);
for fv = [0 0.05 0.10 0.25 1.0]
    t1 = Pn/((1 - fv)*El + fv*Ef)*86400; plot(ax, t1, fv*t1, 'o', 'Color', C.NAVY, 'MarkerFaceColor', C.NAVY, 'MarkerSize', 4);
    text(ax, t1 + 0.25, fv*t1 + 0.018, sprintf('f = %.2f', fv), 'FontSize', 6.6, 'FontWeight', 'bold', 'Color', C.NAVY);
end
xlim(ax, [0 12]); ylim(ax, [0 0.35]); xlabel(ax, 'Total reports / day'); ylabel(ax, sprintf('MQ-135 stress\nreadings / day')); sty(ax, C);
ax = axes(f, 'Position', [0.565 0.2 0.415 0.6]); hold(ax, 'on');
dts = [12 6 3 1 0.5 1/6]; N = ceil((P.P_FLOOR + El./(dts*3600) + 1.6e-6 + 5e-6)/(0.80*0.75*22e-6));
plot(ax, dts, N, '-', 'Color', C.BLUE, 'LineWidth', 1.7); plot(ax, dts, N, 's', 'Color', C.NAVY, 'MarkerFaceColor', C.NAVY, 'MarkerSize', 4);
for k = 1:numel(dts), text(ax, dts(k)*1.05, N(k) + 4, num2str(N(k)), 'FontSize', 7, 'FontWeight', 'bold', 'Color', C.NAVY, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom'); end
set(ax, 'XScale', 'log', 'XDir', 'reverse'); ylim(ax, [0 105]); xlabel(ax, 'Target reporting interval (h)'); ylabel(ax, 'Cells required N*'); sty(ax, C);
save(f, out, 'fig19.png');
end

% ------------------------------------------------------------------ Figure 20
function fig20(out, C)
[f, ~] = canvas(6.2, 3.176);
P = ec.params(); t = [0.1 0.25 0.5 1 2 5];
ax = axes(f, 'Position', [0.09 0.2 0.89 0.775]); hold(ax, 'on');
patch(ax, [0.05 0.3 0.3 0.05], [5 5 1000 1000], C.PALE, 'EdgeColor', 'none', 'HandleVisibility', 'off');
cs = {'ideal', 'realistic', 'conservative'};
for k = 1:3
    s = C.case.(cs{k}); d = (P.V_CC*(P.I_ACT + P.I_SENS)*t + P.E_TX)/ec.p_net(150e-6, cs{k})/60;
    plot(ax, t, d, 'Color', s{1}, 'LineStyle', s{2}, 'LineWidth', s{3}, 'Marker', 'o', 'MarkerSize', 3.5, 'MarkerFaceColor', s{1}, 'DisplayName', cs{k});
end
yline(ax, 10, '--', 'Color', C.INK, 'LineWidth', 0.8, 'HandleVisibility', 'off');
text(ax, 6.6, 10.8, '10-min target', 'FontSize', 7, 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(ax, 0.124, 170, sprintf('impractical\n(ESP32 boot +\nsensor settling)'), 'FontSize', 6.4, 'Color', C.INK, 'HorizontalAlignment', 'center');
xline(ax, 2, ':', 'Color', C.DG, 'LineWidth', 0.9, 'HandleVisibility', 'off');
text(ax, 2.15, 30, 'baseline 2 s', 'FontSize', 6.4, 'Color', C.INK);
Ed = P.V_CC*(P.I_ACT*(P.T_CHECK + 0.10) + P.I_LIGHT*0.75 + P.I_SENS*1.0) + P.E_TX; te = (Ed - P.E_TX)/(P.V_CC*(P.I_ACT + P.I_SENS));
de = Ed/ec.p_net(150e-6, 'realistic')/60;
plot(ax, te, de, 'd', 'MarkerSize', 6.5, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', C.NAVY, 'LineWidth', 1.3, 'HandleVisibility', 'off');
plot(ax, [te*1.03 0.62], [de*0.9 21], '-', 'Color', C.BLUE, 'LineWidth', 0.8, 'HandleVisibility', 'off');
callout(ax, C, 0.95, 16, sprintf('Decomposed event: %.0f min\n(0.35 s active, 0.75 s DS18B20)', de), 'FontSize', 6.2);
set(ax, 'XScale', 'log', 'YScale', 'log'); xlim(ax, [0.05 7]); ylim(ax, [5 1000]);
xlabel(ax, 'ESP32 active-wake duration t_active (s)'); ylabel(ax, 'Sustainable lean interval (min)');
lg = legend(ax, 'Location', 'northwest', 'Box', 'off', 'FontSize', 7); title(lg, 'power path'); lg.Position(1) = lg.Position(1) + 0.2; sty(ax, C);
save(f, out, 'fig20.png');
end
