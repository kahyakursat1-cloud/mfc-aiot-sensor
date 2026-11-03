function make_figures(out)
%MAKE_FIGURES Data figures of the paper (600 dpi PNG) from the MATLAB implementation (+ec).
%   Writes fig4_lora, fig10_relations, fig2_energy_budget, fig7_supercap, fig3_interval,
%   fig9_sensitivity, fig8_harvest_consume, fig_dynamic, fig_trace, fig6_anchor, fig_optim and
%   fig_wake to paper/figures (or to OUT). Run:  >> make_figures
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures'); end
addpath(here);
set(groot, 'defaultTextInterpreter', 'none', 'defaultAxesTickLabelInterpreter', 'none', ...
    'defaultLegendInterpreter', 'none', 'defaultAxesFontName', 'Arial', 'defaultTextFontName', 'Arial', ...
    'defaultAxesFontSize', 8, 'defaultTextFontSize', 8);
C = colors();
fig_lora(out, C); fig_relations(out, C); fig_budget(out, C); fig_supercap(out, C); fig_interval(out, C);
fig_sensitivity(out, C); fig_harvest(out, C); fig_dynamic(out, C); fig_trace(out, C); fig_anchor(out, C);
fig_optim(out, C); fig_wake(out, C);
end

% ------------------------------------------------------------------ style
function C = colors()
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
C.INK = h('#0b0b0b'); C.INK2 = h('#52514e'); C.MUTE = h('#a8a6a0'); C.RULE = h('#e4e2dc');
C.BLUE = h('#1e78d2'); C.LBLUE = h('#8dccfc'); C.GREY = h('#c9c7c1'); C.DGREY = h('#7d7b75');
C.case.ideal = {C.DGREY, '--', 1.2}; C.case.realistic = {C.BLUE, '-', 2.0}; C.case.conservative = {C.INK, ':', 1.6};
end

function f = newfig(w, h)
f = figure('Units', 'inches', 'Position', [1 1 w h], 'Color', 'w', 'Visible', 'off');
end

function ax = sty(ax, C, gridax)
if nargin < 3, gridax = 'y'; end
set(ax, 'Box', 'off', 'TickDir', 'out', 'LineWidth', 0.6, 'XColor', C.INK2, 'YColor', C.INK2, 'FontSize', 7.5, ...
    'GridColor', C.RULE, 'GridAlpha', 1, 'Layer', 'bottom');
ax.XLabel.Color = C.INK; ax.YLabel.Color = C.INK; ax.XLabel.FontSize = 8; ax.YLabel.FontSize = 8;
if contains(gridax, 'y'), ax.YGrid = 'on'; end
if contains(gridax, 'x'), ax.XGrid = 'on'; end
ax.XMinorGrid = 'off'; ax.YMinorGrid = 'off';
end

function ttl(ax, s)
title(ax, s, 'FontSize', 8, 'FontWeight', 'bold', 'HorizontalAlignment', 'left', 'Units', 'normalized', 'Position', [0 1.02 0]);
end

function save(f, out, name)
exportgraphics(f, fullfile(out, name), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, strrep(name, '.png', '.pdf')), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
end

function txt(ax, x, y, s, C, varargin)
text(ax, x, y, s, 'FontSize', 6.6, 'Color', C.INK2, varargin{:});
end

% ------------------------------------------------------------------ Figure 3: LoRa
function fig_lora(out, C)
sf = {'SF7', 'SF8', 'SF9', 'SF10', 'SF11', 'SF12'};
P = ec.params(); toa = ec.lora_toa(7:12); e = toa*P.I_TX*P.V_CC*1e3; toa = toa*1e3;
f = newfig(7.2, 3.0); tl = tiledlayout(f, 1, 2, 'TileSpacing', 'loose', 'Padding', 'loose');
vals = {toa, e}; yl = {'Time-on-air (ms)', 'TX energy per packet (mJ)'};
tt = {'(a) Time-on-air, 13-byte payload', '(b) Transmit energy per packet'}; fm = {'%.0f', '%.1f'};
for k = 1:2
    ax = nexttile(tl); v = vals{k};
    b = bar(ax, 1:6, v, 0.66, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = repmat(C.GREY, 6, 1); b.CData(1, :) = C.BLUE;
    for i = 1:6, txt(ax, i, v(i) + max(v)*0.02, sprintf(fm{k}, v(i)), C, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom'); end
    set(ax, 'XTick', 1:6, 'XTickLabel', sf, 'TickLength', [0 0]); ylim(ax, [0 max(v)*1.12]); ylabel(ax, yl{k});
    sty(ax, C); ttl(ax, tt{k});
end
save(f, out, 'fig4_lora.png');
end

% ------------------------------------------------------------------ Figure 5: closed-form relations
function fig_relations(out, C)
f = newfig(7.4, 5.4); tl = tiledlayout(f, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
ax = nexttile(tl); k = linspace(0, 1, 200);
plot(ax, k, 4*k.*(1 - k), 'Color', C.BLUE, 'LineWidth', 1.8); hold(ax, 'on');
plot(ax, [0.5 0.8], [1 0.64], 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', C.BLUE, 'MarkerEdgeColor', 'w');
txt(ax, 0.5, 1.03, 'matched load, 50% of V_oc', C, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
txt(ax, 0.82, 0.66, '80% of V_oc: 0.64', C, 'VerticalAlignment', 'bottom');
ylim(ax, [0 1.2]); xlabel(ax, 'Operating voltage / open-circuit voltage'); ylabel(ax, 'Power / matched-load power'); sty(ax, C); ttl(ax, '(a) Operating point, Eq. (1)');
ax = nexttile(tl); R = linspace(1, 20, 200); Pm = 0.73^2./(4*R*1e3)*1e6;
patch(ax, [1 20 20 1], [15 15 30 30], C.RULE, 'EdgeColor', 'none'); hold(ax, 'on');
plot(ax, R, Pm, 'Color', C.BLUE, 'LineWidth', 1.8);
plot(ax, 6.06, 22, 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', C.BLUE, 'MarkerEdgeColor', 'w');
txt(ax, 6.6, 24, 'R_int ≈ 6 kΩ, 22 µW', C, 'VerticalAlignment', 'bottom');
txt(ax, 19.8, 31, '15–30 µW band', C, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
ylim(ax, [0 140]); xlim(ax, [1 20]); xlabel(ax, 'Internal resistance R_int (kΩ), V_oc = 0.73 V'); ylabel(ax, 'Matched-load power (µW)'); sty(ax, C); ttl(ax, '(b) Cell power, Eq. (1)');
ax = nexttile(tl); El = ec.e_event('lean'); dt = linspace(0.5, 12, 200)*3600; hold(ax, 'on');
cs = {'ideal', 'realistic', 'conservative'};
for k = 1:3, s = C.case.(cs{k}); plot(ax, dt/3600, ec.p_net(150e-6, cs{k})*dt/El, 'Color', s{1}, 'LineStyle', s{2}, 'LineWidth', s{3}, 'DisplayName', cs{k}); end
yline(ax, 1, '--', 'Color', C.INK2, 'LineWidth', 0.8, 'HandleVisibility', 'off'); txt(ax, 11.8, 1.15, 'M = 1', C, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
lg = legend(ax, 'Location', 'northwest', 'Box', 'off', 'FontSize', 6.6); title(lg, 'power path @150 µW');
xlabel(ax, 'Reporting interval Δt (h)'); ylabel(ax, 'Energy-positive margin M'); sty(ax, C); ttl(ax, '(c) Margin, Eq. (12)');
ax = nexttile(tl); E = logspace(-1, log10(30), 200); Cmin = 2*E/(0.90*(5^2 - 3.5^2));
semilogx(ax, E, Cmin, 'Color', C.BLUE, 'LineWidth', 1.8); hold(ax, 'on');
xline(ax, 0.653, '--', 'Color', C.INK2, 'LineWidth', 0.8); xline(ax, 24.1, '--', 'Color', C.INK2, 'LineWidth', 0.8);
txt(ax, 0.653*1.12, 4.4, 'lean 0.65 J', C, 'VerticalAlignment', 'top'); txt(ax, 24.1/1.12, 4.4, 'MQ-135 stress 24 J', C, 'VerticalAlignment', 'top', 'HorizontalAlignment', 'right');
ylim(ax, [0 4.6]); xlabel(ax, 'Event energy E_event (J)'); ylabel(ax, 'Min. capacitance C (F)'); sty(ax, C); ttl(ax, '(d) Supercap sizing, Eq. (10)');
save(f, out, 'fig10_relations.png');
end

% ------------------------------------------------------------------ Figure 8: per-event energy
function fig_budget(out, C)
P = ec.params();
items = {'SGP30, measurement only (12 ms)', 'LoRa TX SF7 (41 ms)', 'Deep sleep (per cycle)', 'Base sensors (2 s)', ...
         'ESP32 active (2 s)', 'SGP30 incl. 15 s warm-up', 'MQ-135 stress (30 s heater)'};
e = [48e-3*P.V_CC*0.012, P.E_TX, P.P_FLOOR*600, P.V_CC*P.I_SENS*2, P.V_CC*P.I_ACT*2, ...
     P.I_SGP30*P.V_CC*P.T_SGP30_ON + P.I_LIGHT*P.V_CC*(P.T_SGP30_ON - 1), 22.5]*1e3;
f = newfig(7.2, 3.2); ax = axes(f); y = 0:6;
b = barh(ax, y, e, 0.62, 'FaceColor', 'flat', 'EdgeColor', 'none', 'BaseValue', 0.5); b.CData = repmat(C.GREY, 7, 1); b.CData(5, :) = C.BLUE;
set(ax, 'XScale', 'log'); hold(ax, 'on'); xline(ax, 90, '--', 'Color', C.INK, 'LineWidth', 0.9);
text(ax, 90*1.1, 6.62, 'harvested per 10-min cycle at 150 µW (90 mJ)', 'FontSize', 6.8, 'Color', C.INK);
for i = 1:7
    if e(i) >= 1000, s = sprintf('%.1f J', e(i)/1000); else, s = sprintf('%.0f mJ', e(i)); end
    if e(i) < 10, s = sprintf('%.1f mJ', e(i)); end
    text(ax, e(i)*1.15, y(i), s, 'FontSize', 7, 'Color', C.INK2, 'VerticalAlignment', 'middle');
end
set(ax, 'YTick', y, 'YTickLabel', items, 'TickLength', [0 0]); xlim(ax, [0.5 9e4]); ylim(ax, [-0.6 7]);
xlabel(ax, 'Energy per event (mJ, log scale)'); sty(ax, C, 'x');
save(f, out, 'fig2_energy_budget.png');
end

% ------------------------------------------------------------------ Figure 9: bank over successive cycles
function fig_supercap(out, C)
P = ec.params(); c = P.cases.realistic; eb = P.ETA_BUCK;
Cb = 0.5; Vmax = 5; Vmin = 3.5; dt = 5; n = 6*3600/dt; t = (0:n-1)*dt/3600;
Pb = c.eta/eb*150e-6 - P.P_FLOOR/eb - c.pq - c.pleak; Ee = ec.e_event('lean')/eb;
E = 0.5*Cb*3.6^2; V = zeros(1, n); nxt = 2.26*3600; ev = [];
for i = 1:n
    E = min(E + Pb*dt, 0.5*Cb*Vmax^2);
    if (i - 1)*dt >= nxt && E >= Ee, E = E - Ee; ev(end+1) = (i - 1)*dt/3600; nxt = nxt + 2.26*3600; end %#ok<AGROW>
    V(i) = sqrt(2*E/Cb);
end
f = newfig(6.8, 2.8); ax = axes(f); hold(ax, 'on');
for k = 1:numel(ev), xline(ax, ev(k), 'Color', C.RULE, 'LineWidth', 0.9); end
plot(ax, t, V, 'Color', C.BLUE, 'LineWidth', 1.4);
yline(ax, Vmax, '--', 'Color', C.INK2, 'LineWidth', 0.8); yline(ax, Vmin, '--', 'Color', C.INK, 'LineWidth', 0.8);
txt(ax, 0.05, Vmax + 0.03, 'V_max 5.0 V', C, 'VerticalAlignment', 'bottom');
text(ax, 0.05, Vmin + 0.03, 'buck-dropout floor 3.5 V', 'FontSize', 6.6, 'Color', C.INK, 'VerticalAlignment', 'bottom');
if ~isempty(ev), txt(ax, ev(1) + 0.06, 5.12, 'lean event', C); end
xlabel(ax, 'Time (h)'); ylabel(ax, 'Storage-bank voltage (V)'); ylim(ax, [3.3 5.2]); xlim(ax, [0 6]); sty(ax, C, '');
save(f, out, 'fig7_supercap.png');
end

% ------------------------------------------------------------------ Figure 10: interval vs harvested power
function fig_interval(out, C)
Pw = linspace(35, 500, 300); f = newfig(6.6, 3.3); ax = axes(f); hold(ax, 'on');
patch(ax, [15 30 30 15], [0.1 0.1 100 100], C.GREY, 'FaceAlpha', 0.55, 'EdgeColor', 'none', 'HandleVisibility', 'off');
cs = {'ideal', 'realistic', 'conservative'};
for k = 1:3
    d = arrayfun(@(p) ec.interval_h('lean', p*1e-6, cs{k}), Pw); d(~isfinite(d)) = NaN; s = C.case.(cs{k});
    plot(ax, Pw, d, 'Color', s{1}, 'LineStyle', s{2}, 'LineWidth', s{3}, 'DisplayName', cs{k});
end
xline(ax, 33, '--', 'Color', C.DGREY, 'LineWidth', 0.8, 'HandleVisibility', 'off');
xline(ax, 49.5, ':', 'Color', C.BLUE, 'LineWidth', 1.0, 'HandleVisibility', 'off');
xline(ax, 150, ':', 'Color', C.MUTE, 'LineWidth', 0.9, 'HandleVisibility', 'off');
yline(ax, 1/6, '--', 'Color', C.INK2, 'LineWidth', 0.8, 'HandleVisibility', 'off');
txt(ax, 515, 0.183, '10-min target', C, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(ax, 22.5, 0.24, 'single cell 15–30 µW', 'FontSize', 6.2, 'Color', C.INK2, 'Rotation', 90);
text(ax, 35, 0.24, 'ideal floor 33 µW', 'FontSize', 6.2, 'Color', C.DGREY, 'Rotation', 90, 'VerticalAlignment', 'top');
text(ax, 52, 0.24, 'realistic floor ~50 µW', 'FontSize', 6.2, 'Color', C.BLUE, 'Rotation', 90, 'VerticalAlignment', 'top');
y150 = ec.interval_h('lean', 150e-6, 'realistic');
plot(ax, [150 205], [y150 9], '-', 'Color', C.INK2, 'LineWidth', 0.7, 'HandleVisibility', 'off');
text(ax, 207, 9, '150 µW multi-cell target', 'FontSize', 7, 'Color', C.INK);
set(ax, 'YScale', 'log'); ylim(ax, [0.1 100]); xlim(ax, [10 520]);
xlabel(ax, 'Mean MFC power at PMIC input (µW)'); ylabel(ax, 'Min. sustainable lean interval (h)');
lg = legend(ax, 'Location', 'northeast', 'Box', 'off', 'FontSize', 7); title(lg, 'power path'); sty(ax, C);
save(f, out, 'fig3_interval.png');
end

% ------------------------------------------------------------------ Figure 11: sensitivity and uncertainty
function fig_sensitivity(out, C)
P = ec.params(); El = ec.e_event('lean'); base = ec.interval_h('lean', 150e-6, 'realistic');
dtf = @(pm, es, eta, pl) El*es/(eta*pm - P.P_FLOOR - 1.6e-6 - pl)/3600;
rows = {'Harvested P ±20%', dtf(180e-6, 1, .8, 5e-6), dtf(120e-6, 1, .8, 5e-6);
        'Active-wake ±30%', dtf(150e-6, .76, .8, 5e-6), dtf(150e-6, 1.24, .8, 5e-6);
        'PMIC eff. 0.72–0.88', dtf(150e-6, 1, .88, 5e-6), dtf(150e-6, 1, .72, 5e-6);
        'Leakage 1–15 µW', dtf(150e-6, 1, .8, 1e-6), dtf(150e-6, 1, .8, 15e-6)};
[~, o] = sort(abs(cell2mat(rows(:, 3)) - cell2mat(rows(:, 2)))); rows = rows(o, :);
f = newfig(7.4, 5.4); tl = tiledlayout(f, 2, 2, 'TileSpacing', 'loose', 'Padding', 'compact');
ax = nexttile(tl); hold(ax, 'on');
for k = 1:4
    lo = min(rows{k, 2}, rows{k, 3}); hi = max(rows{k, 2}, rows{k, 3});
    patch(ax, [lo hi hi lo], k - 1 + [-0.3 -0.3 0.3 0.3], C.GREY, 'EdgeColor', 'none');
end
xline(ax, base, '--', 'Color', C.BLUE, 'LineWidth', 1.0);
text(ax, base + 0.04, 3.55, sprintf('baseline %.2f h', base), 'FontSize', 6.6, 'Color', C.BLUE, 'VerticalAlignment', 'bottom');
v = cell2mat(rows(:, 2:3)); set(ax, 'YTick', 0:3, 'YTickLabel', rows(:, 1), 'TickLength', [0 0]);
ylim(ax, [-0.6 3.9]); xlim(ax, [min(v(:)) - 0.12, max(v(:)) + 0.12]);
xlabel(ax, 'Realistic lean interval Δt (h)'); sty(ax, C, 'x'); ttl(ax, '(a) Tornado: Δt sensitivity');
ax = nexttile(tl); hold(ax, 'on'); rng(42, 'twister'); dt = ec.mc_interval();
lo = prctile(dt, 5); hi = prctile(dt, 95); med = median(dt);
histogram(ax, dt, 'BinEdges', linspace(0, 6, 51), 'Normalization', 'pdf', 'FaceColor', C.LBLUE, 'EdgeColor', 'w', 'LineWidth', 0.3);
yl = ylim(ax); patch(ax, [lo hi hi lo], [0 0 yl(2) yl(2)], C.RULE, 'EdgeColor', 'none'); uistack(findobj(ax, 'Type', 'histogram'), 'top');
xs = linspace(0, 6, 250); plot(ax, xs, ksdensity(dt, xs), 'Color', C.BLUE, 'LineWidth', 1.5);
xline(ax, med, 'Color', C.INK, 'LineWidth', 1.0); xline(ax, 2, ':', 'Color', C.MUTE, 'LineWidth', 0.9);
text(ax, med + 0.08, yl(2)*0.93, sprintf('median %.2f h', med), 'FontSize', 6.6, 'Color', C.INK, 'VerticalAlignment', 'top');
txt(ax, hi - 0.06, yl(2)*0.70, sprintf('5–95%%\n[%.2f, %.2f] h', lo, hi), C, 'VerticalAlignment', 'top', 'HorizontalAlignment', 'right');
xlim(ax, [0 6]); ylim(ax, yl); xlabel(ax, 'Realistic lean interval Δt (h)'); ylabel(ax, 'Probability density'); sty(ax, C); ttl(ax, '(b) Monte Carlo (N = 20000)');
ax = nexttile(tl); hold(ax, 'on'); pls = {'lean', 'lowgas', 'sgp30', 'mq135'};
iv = cellfun(@(p) ec.interval_h(p, 150e-6, 'realistic'), pls);
b = bar(ax, 1:4, iv, 0.6, 'FaceColor', 'flat', 'EdgeColor', 'none', 'BaseValue', 1); b.CData = [C.BLUE; C.GREY; C.GREY; C.DGREY];
for k = 1:4, text(ax, k, iv(k)*1.2, sprintf('%.1f h', iv(k)), 'FontSize', 6.8, 'Color', C.INK2, 'HorizontalAlignment', 'center'); end
set(ax, 'YScale', 'log', 'XTick', 1:4, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Lean', 'SGP30\newline(12 ms)', 'SGP30 +\newlinewarm-up', 'MQ-135\newlinestress'}, 'TickLength', [0 0], 'XTickLabelRotation', 0, 'FontSize', 6.8);
ylim(ax, [1 300]); ylabel(ax, 'Realistic interval (h)'); sty(ax, C); ttl(ax, '(c) Payload cost (realistic)');
ax = nexttile(tl); hold(ax, 'on'); esr = linspace(0, 20, 120);
plot(ax, esr, 5 - P.I_TX*esr, 'Color', C.BLUE, 'LineWidth', 1.8);
yline(ax, 3.5, '--', 'Color', C.INK, 'LineWidth', 0.8); xline(ax, 12.5, ':', 'Color', C.MUTE, 'LineWidth', 1.0);
text(ax, 0.3, 3.53, '3.5 V buck-dropout floor', 'FontSize', 6.6, 'Color', C.INK, 'VerticalAlignment', 'bottom');
text(ax, 12.9, 4.55, 'R_ESR,max ≈ 12.5 Ω', 'FontSize', 6.4, 'Color', C.INK2, 'Rotation', 90, 'HorizontalAlignment', 'center');
text(ax, 3.0, 4.72, 'terminal V from 5.0 V', 'FontSize', 6.6, 'Color', C.BLUE, 'Rotation', -14, 'VerticalAlignment', 'bottom');
ylim(ax, [2.8 5.1]); xlabel(ax, 'Series ESR (Ω)'); ylabel(ax, 'Storage terminal voltage (V)'); sty(ax, C); ttl(ax, '(d) LoRa-burst voltage sag');
save(f, out, 'fig9_sensitivity.png');
end

% ------------------------------------------------------------------ Figure 13: daily energy vs demand
function fig_harvest(out, C)
cs = {'ideal', 'realistic', 'conservative'}; net = cellfun(@(c) ec.p_net(150e-6, c)*86400, cs);
dem = 144*ec.e_event('lean'); v = [net dem]; y = 3:-1:0;
f = newfig(6.6, 2.3); ax = axes(f); hold(ax, 'on');
cols = [C.GREY; C.BLUE; C.DGREY; C.INK];
for k = 1:4, barh(ax, y(k), v(k), 0.6, 'FaceColor', cols(k, :), 'EdgeColor', 'none'); end
for k = 1:3, text(ax, v(k) + 1.2, y(k), sprintf('%.1f J  (%.1f× short of demand)', v(k), dem/v(k)), 'FontSize', 7, 'Color', C.INK2); end
text(ax, dem - 1.2, y(4), sprintf('%.0f J/day', dem), 'FontSize', 7, 'Color', 'w', 'FontWeight', 'bold', 'HorizontalAlignment', 'right');
set(ax, 'YTick', fliplr(y), 'YTickLabel', fliplr({'Ideal net', 'Realistic net', 'Conservative net', '10-min lean demand'}), 'TickLength', [0 0]);
xlim(ax, [0 dem*1.03]); xlabel(ax, 'Energy per day at 150 µW, lean payload (J/day)'); sty(ax, C, 'x');
save(f, out, 'fig8_harvest_consume.png');
end

% ------------------------------------------------------------------ Figure 14: three-day dynamic run
function fig_dynamic(out, C)
S = ec.dynamic_scenario(1.9); th = S.t/3600;
f = newfig(6.6, 4.4); tl = tiledlayout(f, 5, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
a1 = nexttile(tl, [2 1]); plot(a1, th, S.p*1e6, 'Color', C.INK2, 'LineWidth', 1.3); hold(a1, 'on');
yline(a1, 150, ':', 'Color', C.MUTE, 'LineWidth', 0.9); txt(a1, 71.5, 152, 'daily mean 150 µW', C, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
ylim(a1, [100 200]); xlim(a1, [0 72]); ylabel(a1, 'Harvested power (µW)'); set(a1, 'XTickLabel', []); sty(a1, C);
a2 = nexttile(tl, [3 1]); hold(a2, 'on'); plot(a2, th, S.v, 'Color', C.DGREY, 'LineWidth', 0.9, 'HandleVisibility', 'off');
yline(a2, 5, '--', 'Color', C.INK2, 'LineWidth', 0.8, 'HandleVisibility', 'off'); yline(a2, 3.5, '--', 'Color', C.INK, 'LineWidth', 0.8, 'HandleVisibility', 'off');
text(a2, 71.5, 5.02, 'V_max 5.0 V', 'FontSize', 6.4, 'Color', C.INK2, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(a2, 71.5, 3.52, 'buck-dropout floor 3.5 V', 'FontSize', 6.4, 'Color', C.INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
fr = [0.25 0.55]; lb = {'SoC 0.25 (sleep below)', 'SoC 0.55 (measure below)'};
for k = 1:2
    vth = sqrt(2*(S.e_min + fr(k)*(S.e_max - S.e_min))/0.5); yline(a2, vth, ':', 'Color', C.MUTE, 'LineWidth', 0.8, 'HandleVisibility', 'off');
    text(a2, 0.5, vth + 0.01, lb{k}, 'FontSize', 5.8, 'Color', C.INK2, 'VerticalAlignment', 'bottom');
end
E = S.events; key = {'transmit', 'measure', 'sleep', 'anomaly'}; lab = {'transmit', 'measure (store)', 'sleep (recharge)', 'anomaly override'};
for k = 1:4
    m = strcmp(E.action, key{k}); if ~any(m), continue; end
    switch k
        case 1, scatter(a2, E.t_h(m), E.v_before(m), 20, C.BLUE, 'filled', 'DisplayName', lab{k});
        case 2, scatter(a2, E.t_h(m), E.v_before(m), 20, C.INK, 'MarkerFaceColor', 'w', 'LineWidth', 0.8, 'DisplayName', lab{k});
        case 3, scatter(a2, E.t_h(m), E.v_before(m), 24, C.INK, 'x', 'LineWidth', 1.0, 'DisplayName', lab{k});
        case 4, scatter(a2, E.t_h(m), E.v_before(m), 70, C.INK, 'p', 'filled', 'DisplayName', lab{k});
    end
end
legend(a2, 'Location', 'north', 'Orientation', 'horizontal', 'Box', 'off', 'FontSize', 6.6);
ylim(a2, [3.3 5.55]); xlim(a2, [0 72]); xlabel(a2, 'Time (h)'); ylabel(a2, 'Storage-bank voltage (V)'); sty(a2, C);
save(f, out, 'fig_dynamic.png');
end

% ------------------------------------------------------------------ Figure 15: measured trace
function fig_trace(out, C)
root = fileparts(fileparts(mfilename('fullpath')));
tr = readtable(fullfile(root, 'external', 'yen_smfc_trace_5min.csv'));
day = floor(tr.t_s/86400); nd = max(day) + 1;
dm = accumarray(day + 1, tr.p_cell_W*1e6, [nd 1], @mean); d = (0:nd-1)';
f = newfig(6.8, 4.4); tl = tiledlayout(f, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
a1 = nexttile(tl); hold(a1, 'on');
patch(a1, [-5 170 170 -5], [15 15 30 30], C.GREY, 'FaceAlpha', 0.55, 'EdgeColor', 'none');
plot(a1, d, max(dm, 0.01), 'Color', C.BLUE, 'LineWidth', 1.2);
text(a1, 1, 33, '15–30 µW assumed in this work', 'FontSize', 6.4, 'Color', C.INK2, 'VerticalAlignment', 'bottom');
set(a1, 'YScale', 'log', 'YTick', [0.01 0.1 1 10 100], 'YTickLabel', {'≤0.01', '0.1', '1', '10', '100'}, 'XTickLabel', []);
ylim(a1, [0.01 400]); xlim(a1, [-5 165]); ylabel(a1, sprintf('Single-cell power,\ndaily mean (µW)')); sty(a1, C);
text(a1, -0.1, 1.02, '(a)', 'Units', 'normalized', 'FontSize', 8, 'FontWeight', 'bold', 'VerticalAlignment', 'bottom');
a2 = nexttile(tl); hold(a2, 'on'); P = ec.params();
cfg = {0.5, [], C.BLUE, '-', 1.3, '0.5 F bank'; 5.0, [], C.INK, '--', 1.0, '5 F, leakage 5 µW'; 5.0, 5*P.LEAK_PER_F, C.MUTE, ':', 1.0, '5 F, leakage 50 µW (scaled with C)'};
for k = 1:3
    r = ec.trace_scenario(tr.t_s, tr.p_cell_W, 10, 0.75, 2.26, cfg{k, 1}, 5.0, 3.5, 0.05, cfg{k, 2});
    on = accumarray(day + 1, double(r.on), [nd 1], @mean);
    plot(a2, d, on, 'Color', cfg{k, 3}, 'LineStyle', cfg{k, 4}, 'LineWidth', cfg{k, 5}, 'DisplayName', cfg{k, 6});
end
ylim(a2, [-0.05 1.05]); xlim(a2, [-5 165]); ylabel(a2, sprintf('Fraction of day\nthe node is on')); xlabel(a2, 'Day of the 161-day record');
legend(a2, 'Location', 'northoutside', 'Orientation', 'horizontal', 'Box', 'off', 'FontSize', 7); sty(a2, C);
text(a2, -0.1, 1.02, '(b)', 'Units', 'normalized', 'FontSize', 8, 'FontWeight', 'bold', 'VerticalAlignment', 'bottom');
save(f, out, 'fig_trace.png');
end

% ------------------------------------------------------------------ Figure 16: published measurements
function fig_anchor(out, C)
f = newfig(7.0, 3.1); tl = tiledlayout(f, 1, 2, 'TileSpacing', 'loose', 'Padding', 'loose');
ax = nexttile(tl); hold(ax, 'on'); ocv = [0.733 0.75]; ol = {'0.73', '0.75'};
b = bar(ax, 1:2, ocv, 0.5, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = repmat(C.GREY, 2, 1);
for k = 1:2, text(ax, k, ocv(k) + 0.02, ol{k}, 'FontSize', 6.8, 'Color', C.INK2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom'); end
set(ax, 'XTick', 1:2, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Zheng\newlineet al.', 'Zhang\newlineet al.'}, 'TickLength', [0 0], 'XTickLabelRotation', 0);
ylim(ax, [0 1]); xlim(ax, [0.4 2.6]); ylabel(ax, 'Open-circuit voltage (V)'); sty(ax, C, ''); ttl(ax, '(a) Reported open-circuit voltage');
ax = nexttile(tl); hold(ax, 'on'); pd = [3.0 4.3 17.4 2.1 1.8];
b = bar(ax, 1:5, pd, 0.6, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = [C.GREY; C.GREY; C.GREY; C.GREY; C.BLUE];
errorbar(ax, 5, 1.8, 0.6, 0.6, 'LineStyle', 'none', 'Color', C.INK, 'LineWidth', 0.8, 'CapSize', 4);
lab = {'3', '4.3', '17.4', '2.1', '1.2–2.4'}; top = [3.0 4.3 17.4 2.1 2.4];
for k = 1:5, text(ax, k, top(k) + 0.3, lab{k}, 'FontSize', 6.8, 'Color', C.INK2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom'); end
set(ax, 'XTick', 1:5, 'TickLabelInterpreter', 'tex', 'XTickLabel', {'Zhang\newlinepeak', 'Yang\newlinepeak', 'Yen\newlinepeak', 'Yen\newlinemean', 'This\newlinework'}, 'TickLength', [0 0], 'XTickLabelRotation', 0);
ylim(ax, [0 19]); xlim(ax, [0.4 5.6]); ylabel(ax, 'Power density (mW/m²)'); sty(ax, C, ''); ttl(ax, '(b) Power density at load');
save(f, out, 'fig6_anchor.png');
end

% ------------------------------------------------------------------ Figure 17: optimisation
function fig_optim(out, C)
P = ec.params(); Pn = ec.p_net(150e-6, 'realistic'); El = ec.e_event('lean'); Ef = ec.e_event('mq135');
f = newfig(7.2, 3.2); tl = tiledlayout(f, 1, 2, 'TileSpacing', 'loose', 'Padding', 'loose');
ax = nexttile(tl); hold(ax, 'on'); fr = linspace(0, 1, 200); tot = Pn./((1 - fr)*El + fr*Ef)*86400;
plot(ax, tot, fr.*tot, 'Color', C.BLUE, 'LineWidth', 1.8);
for fv = [0 0.05 0.10 0.25 1.0]
    t1 = Pn/((1 - fv)*El + fv*Ef)*86400; plot(ax, t1, fv*t1, 'o', 'Color', C.INK, 'MarkerFaceColor', C.INK, 'MarkerSize', 4);
    text(ax, t1 + 0.15, fv*t1 + 0.012, sprintf('f = %.2f', fv), 'FontSize', 6.4, 'Color', C.INK2);
end
xlabel(ax, 'Total reports / day'); ylabel(ax, 'MQ-135 stress readings / day'); sty(ax, C); ttl(ax, '(a) Pareto: resolution vs gas coverage');
ax = nexttile(tl); hold(ax, 'on'); dts = [12 6 3 1 0.5 1/6];
N = ceil((P.P_FLOOR + El./(dts*3600) + 1.6e-6 + 5e-6)/(0.80*0.75*22e-6));
plot(ax, dts, N, '-', 'Color', C.BLUE, 'LineWidth', 1.6); plot(ax, dts, N, 's', 'Color', C.INK, 'MarkerFaceColor', C.INK, 'MarkerSize', 4);
for k = 1:numel(dts), text(ax, dts(k)*1.08, N(k) + 3, num2str(N(k)), 'FontSize', 6.6, 'Color', C.INK2, 'HorizontalAlignment', 'right'); end
set(ax, 'XScale', 'log', 'XDir', 'reverse'); xlabel(ax, 'Target reporting interval (h)'); ylabel(ax, 'Cells required N*');
sty(ax, C); ttl(ax, '(b) Min. cells (loss-aware)');
save(f, out, 'fig_optim.png');
end

% ------------------------------------------------------------------ Figure 18: active-wake duration
function fig_wake(out, C)
P = ec.params(); t = [0.1 0.25 0.5 1 2 5];
f = newfig(6.6, 3.2); ax = axes(f); hold(ax, 'on');
patch(ax, [0.05 0.3 0.3 0.05], [1 1 1e4 1e4], C.GREY, 'FaceAlpha', 0.55, 'EdgeColor', 'none', 'HandleVisibility', 'off');
cs = {'ideal', 'realistic', 'conservative'};
for k = 1:3
    s = C.case.(cs{k}); d = (P.V_CC*(P.I_ACT + P.I_SENS)*t + P.E_TX)/ec.p_net(150e-6, cs{k})/60;
    plot(ax, t, d, 'Color', s{1}, 'LineStyle', s{2}, 'LineWidth', s{3}, 'Marker', 'o', 'MarkerSize', 3.5, 'DisplayName', cs{k});
end
yline(ax, 10, '--', 'Color', C.INK2, 'LineWidth', 0.8, 'HandleVisibility', 'off');
txt(ax, 6.6, 10.8, '10-min target', C, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
text(ax, 0.124, 150, sprintf('impractical\n(ESP32 boot +\nsensor settling)'), 'FontSize', 6.2, 'Color', C.INK2, 'HorizontalAlignment', 'center');
xline(ax, 2, ':', 'Color', C.MUTE, 'LineWidth', 0.9, 'HandleVisibility', 'off');
text(ax, 2.12, 12, 'baseline 2 s', 'FontSize', 6.4, 'Color', C.INK2, 'Rotation', 90);
Ed = P.V_CC*(P.I_ACT*(P.T_CHECK + 0.10) + P.I_LIGHT*0.75 + P.I_SENS*1.0) + P.E_TX; te = (Ed - P.E_TX)/(P.V_CC*(P.I_ACT + P.I_SENS));
de = Ed/ec.p_net(150e-6, 'realistic')/60;
plot(ax, te, de, 'd', 'MarkerSize', 6.5, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', C.BLUE, 'LineWidth', 1.4, 'HandleVisibility', 'off');
text(ax, te*1.12, de*0.80, sprintf('decomposed window: %.0f min\n(0.35 s active, 0.75 s DS18B20\nconversion in light sleep)', de), ...
    'FontSize', 6.2, 'Color', C.BLUE, 'VerticalAlignment', 'top', 'Interpreter', 'none');
set(ax, 'XScale', 'log', 'YScale', 'log'); xlim(ax, [0.05 7]); ylim(ax, [5 1000]);
xlabel(ax, 'ESP32 active-wake duration t_active (s)'); ylabel(ax, 'Sustainable lean interval (min)');
lg = legend(ax, 'Location', 'northwest', 'Box', 'off', 'FontSize', 7); title(lg, 'power path'); lg.Position(1) = lg.Position(1) + 0.15; sty(ax, C);
save(f, out, 'fig_wake.png');
end
