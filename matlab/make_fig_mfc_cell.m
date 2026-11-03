function make_fig_mfc_cell(out)
%MAKE_FIG_MFC_CELL Labelled cross-section of one single-chamber soil MFC: anode in the anaerobic layer,
%   air cathode at the soil surface, proton path through the soil, electron path through the external load.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures'); end
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
INK = h('#0b0b0b'); INK2 = h('#52514e'); BLUE = h('#1e78d2'); SOIL1 = h('#e3d5bb'); SOIL2 = h('#c9b48f');
ELEC = h('#3a3a38'); AIR = h('#f2f6fa'); BUG = h('#6b8e23');
f = figure('Units', 'inches', 'Position', [1 1 6.4 3.9], 'Color', 'w', 'Visible', 'off');
ax = axes(f, 'Position', [0 0 1 1]); hold(ax, 'on'); axis(ax, [0 100 0 61]); axis(ax, 'off');
    function tx(x, y, s, sz, col, varargin)
        text(ax, x, y, s, 'FontName', 'Arial', 'FontSize', sz, 'Color', col, 'Interpreter', 'tex', varargin{:});
    end
    function arrow(x0, y0, x1, y1, col, lw)
        plot(ax, [x0 x1], [y0 y1], '-', 'Color', col, 'LineWidth', lw);
        d = [x1 - x0, y1 - y0]; d = d/norm(d); n = [-d(2) d(1)]; L = 1.6; Wd = 0.8;
        patch(ax, [x1, x1 - L*d(1) + Wd*n(1), x1 - L*d(1) - Wd*n(1)], [y1, y1 - L*d(2) + Wd*n(2), y1 - L*d(2) - Wd*n(2)], col, 'EdgeColor', 'none');
    end
% ---------------- container, air, two soil layers
rectangle(ax, 'Position', [14 4 42 46], 'FaceColor', AIR, 'EdgeColor', 'none');
rectangle(ax, 'Position', [14 4 42 24], 'FaceColor', SOIL2, 'EdgeColor', 'none');
rectangle(ax, 'Position', [14 28 42 14], 'FaceColor', SOIL1, 'EdgeColor', 'none');
plot(ax, [14 14 56 56], [50 4 4 50], '-', 'Color', INK, 'LineWidth', 1.4);
tx(15.2, 46.5, 'air (O_2)', 6.6, INK2);
tx(15.2, 38.8, 'aerobic layer', 6.6, INK2);
tx(15.2, 25.6, 'anaerobic layer', 6.6, INK2);
% ---------------- electrodes
rectangle(ax, 'Position', [19 41.6 32 1.8], 'FaceColor', ELEC, 'EdgeColor', 'none');
rectangle(ax, 'Position', [21 10 28 2.2], 'FaceColor', ELEC, 'EdgeColor', 'none');
rng(3); bx = 22 + 26*rand(1, 18); by = 12.6 + 2.2*rand(1, 18);
for k = 1:numel(bx)
    rectangle(ax, 'Position', [bx(k) by(k) 1.1 0.55], 'Curvature', [1 1], 'FaceColor', BUG, 'EdgeColor', 'none');
end
% ---------------- proton path through the soil
for xa = [27 35 43]
    arrow(xa, 16.5, xa, 39.8, BLUE, 1.0);
end
tx(44.2, 28, 'H^+', 8, BLUE, 'FontWeight', 'bold');
% ---------------- external circuit and electron path
plot(ax, [21 8 8 30], [11.1 11.1 56 56], '-', 'Color', INK, 'LineWidth', 1.1);
plot(ax, [44 62 62 51], [56 56 42.5 42.5], '-', 'Color', INK, 'LineWidth', 1.1);
rectangle(ax, 'Position', [30 53 14 6], 'FaceColor', 'w', 'EdgeColor', INK, 'LineWidth', 1.1);
tx(37, 56, 'load', 7.2, INK, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
arrow(8, 26, 8, 40, INK, 1.1); tx(6.8, 33, 'e^-', 8, INK, 'HorizontalAlignment', 'right', 'FontWeight', 'bold');
arrow(62, 51, 62, 46, INK, 1.1); tx(63.2, 48.5, 'e^-', 8, INK, 'FontWeight', 'bold');
tx(37, 60.6, 'PMIC input (array of ~10 cells)', 6.2, INK2, 'HorizontalAlignment', 'center');
% ---------------- labels
tx(65.5, 42.5, '\bfAir cathode\rm at the soil surface', 7.0, INK, 'VerticalAlignment', 'middle');
tx(65.5, 39.0, 'O_2 + 4H^+ + 4e^- \rightarrow 2H_2O', 6.8, INK2, 'VerticalAlignment', 'middle');
tx(65.5, 14.5, '\bfAnode\rm in the anaerobic layer', 7.0, INK, 'VerticalAlignment', 'middle');
tx(65.5, 11.0, 'electrogenic biofilm oxidises organic', 6.6, INK2, 'VerticalAlignment', 'middle');
tx(65.5, 8.2, 'matter, e.g. CH_3COO^- + 2H_2O \rightarrow', 6.6, INK2, 'VerticalAlignment', 'middle');
tx(65.5, 5.4, '2CO_2 + 7H^+ + 8e^-', 6.6, INK2, 'VerticalAlignment', 'middle');
plot(ax, [51.5 64.5], [42.5 42.5], ':', 'Color', INK2, 'LineWidth', 0.7);
plot(ax, [49.5 64.5], [11.1 14.5], ':', 'Color', INK2, 'LineWidth', 0.7);
tx(65.5, 28, {'\bfOne cell\rm', 'matched-load power, Eq. (1)', 'sustained 15–30 µW'}, 6.6, INK2, 'VerticalAlignment', 'middle');
exportgraphics(f, fullfile(out, 'fig_mfc_cell.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'fig_mfc_cell.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
end
