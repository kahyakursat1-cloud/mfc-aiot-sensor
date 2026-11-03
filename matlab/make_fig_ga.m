function make_fig_ga(out)
%MAKE_FIG_GA Graphical abstract: from the harvested power through the loss-aware power path to the
%   sustainable interval, the burst capacitor and the delivered share on the measured record.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'suscom'); end
addpath(here);
P = ec.params(); pn = ec.p_net(150e-6, 'realistic'); dt = ec.interval_h('lean', 150e-6, 'realistic');
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
NAVY = h('#003a84'); BLUE = h('#1e78d2'); PALE = h('#dbecfc'); INK = h('#0b0b0b'); GREY = h('#6b6b6b');
f = figure('Units', 'inches', 'Position', [1 1 7.4 3.2], 'Color', 'w', 'Visible', 'off');
A = axes(f, 'Position', [0 0 1 1]); hold(A, 'on'); axis(A, [0 100 0 43]); axis(A, 'off');
    function box(x, y, w, hg, t, s, fc, tc)
        rectangle(A, 'Position', [x y w hg], 'FaceColor', fc, 'EdgeColor', NAVY, 'LineWidth', 1.2, 'Curvature', 0.06);
        text(A, x + w/2, y + hg*0.66, t, 'FontName', 'Arial', 'FontSize', 10, 'FontWeight', 'bold', 'Color', tc, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
        text(A, x + w/2, y + hg*0.27, s, 'FontName', 'Arial', 'FontSize', 8, 'Color', tc, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
    end
    function arr(x0, y0, x1, y1)
        plot(A, [x0 x1], [y0 y1], '-', 'Color', NAVY, 'LineWidth', 1.8);
        d = [x1 - x0, y1 - y0]; d = d/norm(d); n = [-d(2) d(1)];
        patch(A, [x1, x1 - 1.7*d(1) + 0.9*n(1), x1 - 1.7*d(1) - 0.9*n(1)], [y1, y1 - 1.7*d(2) + 0.9*n(2), y1 - 1.7*d(2) - 0.9*n(2)], NAVY, 'EdgeColor', 'none');
    end
box(2, 14, 21, 15, 'Soil-MFC array', sprintf('ten cells, 150 µW'), PALE, NAVY);
box(32, 14, 25, 15, sprintf('%.0f µW net', pn*1e6), 'after losses and sleep floor', NAVY, [1 1 1]);
box(70, 30, 28, 11, sprintf('%.2f h', dt), 'sustainable lean interval', PALE, NAVY);
box(70, 16, 28, 11, sprintf('%.0f mF', 46), 'burst capacitor for 200 mA', PALE, NAVY);
box(70, 2, 28, 11, '71% to 56%', 'reports on a 161-day record', PALE, NAVY);
arr(23.5, 21.5, 31.3, 21.5); arr(57.5, 21.5, 69.3, 35.5); arr(57.5, 21.5, 69.3, 21.5); arr(57.5, 21.5, 69.3, 7.5);
text(A, 12.5, 9.5, 'single cell: 15–30 µW', 'FontName', 'Arial', 'FontSize', 8, 'Color', INK, 'HorizontalAlignment', 'center');
text(A, 12.5, 6.3, 'below the 50 µW break-even', 'FontName', 'Arial', 'FontSize', 8, 'Color', GREY, 'HorizontalAlignment', 'center');
exportgraphics(f, fullfile(out, 'graphical_abstract.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'graphical_abstract.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
fprintf('pn %.1f dt %.2f tx %g\n', pn*1e6, dt, P.I_ACT + P.I_TX);
end
