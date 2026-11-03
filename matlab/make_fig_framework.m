function make_fig_framework(out)
%MAKE_FIG_FRAMEWORK Framework pipeline: one card per stage with its governing equation and a small plot
%   computed from the model (+ec), source-specific stages separated from reusable ones.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures'); end
h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
INK = h('#0b0b0b'); INK2 = h('#52514e'); MUTE = h('#a8a6a0'); RULE = h('#e4e2dc'); BLUE = h('#1e78d2');
LBLUE = h('#8dccfc'); GREY = h('#c9c7c1'); DGREY = h('#7d7b75'); PALE = h('#f4f8fb');
FW = 7.4; FH = 4.9;
f = figure('Units', 'inches', 'Position', [1 1 FW FH], 'Color', 'w', 'Visible', 'off');
A = axes(f, 'Position', [0 0 1 1]); hold(A, 'on'); axis(A, [0 1 0 1]); axis(A, 'off');
W = 0.222; H = 0.385; X = 0.018 + (0:3)*0.248; Y = [0.505 0.045];
S = struct('t', {}, 'eq', {}, 'n', {}, 'kind', {}, 'r', {}, 'c', {});
S(1) = struct('t', 'Source cell', 'eq', '$P_{\max}=\frac{V_{\mathrm{oc}}^{2}}{4R_{\mathrm{int}}}$', 'n', 'Eq. (1)', 'kind', 'src', 'r', 1, 'c', 1);
S(2) = struct('t', 'Cell array', 'eq', '$N^{*}=\frac{E_{\mathrm{event}}/\Delta t+P_{\mathrm{loss}}}{\eta\,\eta_{\mathrm{stack}}P_{\mathrm{cell}}}$', 'n', 'Eq. (16)', 'kind', 'src', 'r', 1, 'c', 2);
S(3) = struct('t', 'Loss-aware PMIC', 'eq', '$P_{\mathrm{net}}=\eta P_{\mathrm{MFC}}-P_{\mathrm{floor}}-P_{q}-P_{\mathrm{leak}}$', 'n', 'Eq. (7)', 'kind', 'key', 'r', 1, 'c', 3);
S(4) = struct('t', 'Event energy', 'eq', '$E_{\mathrm{event}}=V_{cc}\big(I_a t_a+\sum_k I_k t_k+I_{tx}\mathrm{ToA}\big)$', 'n', 'Eq. (3)', 'kind', 'reuse', 'r', 1, 'c', 4);
S(5) = struct('t', 'Storage bank', 'eq', '$C\geq\frac{2E_{\mathrm{event}}}{\eta_{\mathrm{buck}}(V_{\max}^{2}-V_{\min}^{2})}$', 'n', 'Eqs. (10), (11)', 'kind', 'reuse', 'r', 2, 'c', 4);
S(6) = struct('t', 'Duty-cycle core', 'eq', '$\Delta t=\frac{E_{\mathrm{event}}}{P_{\mathrm{net}}},\;M=\frac{P_{\mathrm{net}}\Delta t_{\mathrm{target}}}{E_{\mathrm{event}}}$', 'n', 'Eqs. (8), (12)', 'kind', 'reuse', 'r', 2, 'c', 3);
S(7) = struct('t', 'AI decision layer', 'eq', '$s(x,\psi)=2^{-E[h(x)]/c(\psi)}$', 'n', '', 'kind', 'ai', 'r', 2, 'c', 2);
S(8) = struct('t', 'LoRa uplink', 'eq', '$\mathrm{ToA}=(n_{\mathrm{pre}}+4.25)\frac{2^{SF}}{BW}+T_{\mathrm{pl}}$', 'n', 'Eq. (5)', 'kind', 'reuse', 'r', 2, 'c', 1);
for k = 1:8
    x0 = X(S(k).c); y0 = Y(S(k).r);
    switch S(k).kind
        case 'src',   hc = DGREY; ec_ = INK2; lw = 0.8; ls = '-'; fc = 'w';
        case 'key',   hc = DGREY;  ec_ = BLUE; lw = 1.8; ls = '-'; fc = PALE;
        case 'reuse', hc = BLUE;  ec_ = INK2; lw = 0.8; ls = '-'; fc = 'w';
        case 'ai',    hc = MUTE;  ec_ = MUTE; lw = 0.9; ls = '--'; fc = 'w';
    end
    rectangle(A, 'Position', [x0 y0 W H], 'FaceColor', fc, 'EdgeColor', ec_, 'LineWidth', lw, 'LineStyle', ls);
    rectangle(A, 'Position', [x0 y0 + H - 0.058 W 0.058], 'FaceColor', hc, 'EdgeColor', 'none');
    text(A, x0 + 0.01, y0 + H - 0.029, sprintf('%d  %s', k, S(k).t), 'FontName', 'Arial', 'FontSize', 7.6, 'FontWeight', 'bold', ...
        'Color', 'w', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
    fs = 8.4; if any(k == [3 8]), fs = 6.9; elseif k == 4, fs = 6.3; end
    text(A, x0 + W/2, y0 + H - 0.105, S(k).eq, 'Interpreter', 'latex', 'FontSize', fs, 'Color', INK, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    text(A, x0 + W - 0.008, y0 + H - 0.158, S(k).n, 'FontName', 'Arial', 'FontSize', 5.8, 'Color', INK2, 'HorizontalAlignment', 'right', 'Interpreter', 'none');
    ax = axes(f, 'Position', [x0 + 0.05, y0 + 0.048, W - 0.065, 0.14]); hold(ax, 'on');
    inset(ax, k);
    set(ax, 'FontName', 'Arial', 'FontSize', 5.4, 'Box', 'off', 'TickDir', 'out', 'TickLength', [0.02 0.02], 'LineWidth', 0.5, ...
        'XColor', INK2, 'YColor', INK2, 'Color', 'none', 'Layer', 'top');
end
text(A, X(3) + W/2, Y(1) + H + 0.022, 'principal addition of this work', 'FontName', 'Arial', 'FontSize', 6.8, 'FontAngle', 'italic', 'Color', BLUE, 'HorizontalAlignment', 'center');
% ---------------- flow arrows
    function arr(x0, y0, x1, y1)
        plot(A, [x0 x1], [y0 y1], '-', 'Color', INK, 'LineWidth', 1.1);
        d = [x1 - x0, (y1 - y0)*FH/FW]; d = d/norm(d); n = [-d(2) d(1)]; L = 0.012; Wd = 0.006;
        px = [x1, x1 - L*d(1) + Wd*n(1), x1 - L*d(1) - Wd*n(1)];
        py = [y1, y1 - (L*d(2) - Wd*n(2))*FW/FH, y1 - (L*d(2) + Wd*n(2))*FW/FH];
        patch(A, px, py, INK, 'EdgeColor', 'none');
    end
ym1 = Y(1) + H/2 + 0.06; ym2 = Y(2) + H/2 + 0.06;
for c = 1:3, arr(X(c) + W, ym1, X(c + 1), ym1); end
arr(X(4) + W/2, Y(1), X(4) + W/2, Y(2) + H);
for c = 4:-1:2, arr(X(c), ym2, X(c - 1) + W, ym2); end
% ---------------- legend
ly = 0.985;
rectangle(A, 'Position', [0.018 ly - 0.022 0.022 0.018], 'FaceColor', DGREY, 'EdgeColor', 'none');
text(A, 0.046, ly - 0.013, 'source-specific (re-specified for another harvester)', 'FontName', 'Arial', 'FontSize', 6.4, 'Color', INK2, 'VerticalAlignment', 'middle');
rectangle(A, 'Position', [0.40 ly - 0.022 0.022 0.018], 'FaceColor', BLUE, 'EdgeColor', 'none');
text(A, 0.428, ly - 0.013, 'reused unchanged', 'FontName', 'Arial', 'FontSize', 6.4, 'Color', INK2, 'VerticalAlignment', 'middle');
rectangle(A, 'Position', [0.56 ly - 0.022 0.022 0.018], 'FaceColor', MUTE, 'EdgeColor', 'none');
text(A, 0.588, ly - 0.013, 'secondary layer', 'FontName', 'Arial', 'FontSize', 6.4, 'Color', INK2, 'VerticalAlignment', 'middle');
exportgraphics(f, fullfile(out, 'fig_pipeline.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'fig_pipeline.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);

    function inset(ax, k)
        switch k
            case 1
                r = linspace(1, 20, 200); plot(ax, r, 0.73^2./(4*r*1e3)*1e6, 'Color', BLUE, 'LineWidth', 1.3);
                plot(ax, 6.06, 22, 'o', 'MarkerSize', 3.5, 'MarkerFaceColor', BLUE, 'MarkerEdgeColor', 'w');
                xlabel(ax, 'R_int (kΩ)', 'Interpreter', 'none'); ylabel(ax, 'P (µW)'); xlim(ax, [0 20]); ylim(ax, [0 140]);
            case 2
                d = logspace(log10(1/6), log10(12), 200); El = ec.e_event('lean');
                n = (El./(d*3600) + 39.6e-6)/(0.8*0.75*22e-6); ax.XScale = 'log'; ax.YScale = 'log';
                plot(ax, d, n, 'Color', BLUE, 'LineWidth', 1.3);
                plot(ax, 2.26, (El/(2.26*3600) + 39.6e-6)/(0.8*0.75*22e-6), 'o', 'MarkerSize', 3.5, 'MarkerFaceColor', BLUE, 'MarkerEdgeColor', 'w');
                xlabel(ax, 'Δt (h)'); ylabel(ax, 'N*'); xlim(ax, [1/6 12]); ylim(ax, [3 100]);
            case 3
                v = [150, -30, -33, -1.6, -5]; top = [150 150 120 87 85.4]; bot = top + [0 v(2:end)];
                for i = 1:5
                    if i == 1, y = [0 150]; col = GREY; else, y = sort([bot(i) top(i)]); col = LBLUE; end
                    patch(ax, [i - 0.35 i + 0.35 i + 0.35 i - 0.35], [y(1) y(1) y(2) y(2)], col, 'EdgeColor', 'none');
                end
                patch(ax, [5.65 6.35 6.35 5.65], [0 0 80.4 80.4], BLUE, 'EdgeColor', 'none');
                text(ax, 1, 154, '150', 'FontSize', 5.4, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'Color', INK2);
                text(ax, 6, 84, '80.4', 'FontSize', 5.4, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'Color', BLUE, 'FontWeight', 'bold');
                set(ax, 'XTick', 1:6, 'XTickLabel', {'in', 'η', 'floor', 'q', 'leak', 'net'}, 'TickLabelInterpreter', 'none', 'XTickLabelRotation', 0);
                xlim(ax, [0.4 6.6]); ylim(ax, [0 175]); ylabel(ax, 'µW');
            case 4
                e = [0.528 0.109 0.0163]; c0 = 0; cols = {BLUE, LBLUE, INK};
                labs = {'ESP32 active', 'sensors', 'LoRa'};
                for i = 1:3
                    patch(ax, [c0 c0 + e(i) c0 + e(i) c0], [0.3 0.3 0.7 0.7], cols{i}, 'EdgeColor', 'w', 'LineWidth', 0.6);
                    c0 = c0 + e(i);
                end
                text(ax, 0.264, 0.86, 'ESP32 0.53 J', 'FontSize', 5.4, 'HorizontalAlignment', 'center', 'Color', INK2);
                text(ax, 0.58, 0.14, 'sensors 0.11 J', 'FontSize', 5.4, 'HorizontalAlignment', 'center', 'Color', INK2);
                text(ax, 0.66, 0.86, 'LoRa 16 mJ', 'FontSize', 5.4, 'HorizontalAlignment', 'right', 'Color', INK2);
                xlim(ax, [0 0.68]); ylim(ax, [0 1]); set(ax, 'YTick', []); xlabel(ax, 'lean event energy (J), total 0.65 J');
            case 5
                E = logspace(-1, log10(30), 200); ax.XScale = 'log'; plot(ax, E, 2*E/(0.90*(5^2 - 3.5^2)), 'Color', BLUE, 'LineWidth', 1.3);
                yline(ax, 0.5, ':', 'Color', INK2, 'LineWidth', 0.8);
                plot(ax, 0.653, 2*0.653/(0.9*12.75), 'o', 'MarkerSize', 3.5, 'MarkerFaceColor', BLUE, 'MarkerEdgeColor', 'w');
                text(ax, 0.13, 0.62, '0.5 F bank', 'FontSize', 5.4, 'Color', INK2, 'VerticalAlignment', 'bottom');
                xlabel(ax, 'E_event (J)', 'Interpreter', 'none'); ylabel(ax, 'C_min (F)', 'Interpreter', 'none'); ylim(ax, [0 4.6]); xlim(ax, [0.1 30]);
            case 6
                p = linspace(60, 400, 300)*1e-6; El = ec.e_event('lean');
                pn = ec.p_net(p, 'realistic'); dt = El./pn/3600; dt(pn <= 0) = NaN;
                ax.YScale = 'log'; plot(ax, p*1e6, dt, 'Color', BLUE, 'LineWidth', 1.3);
                plot(ax, 150, El/ec.p_net(150e-6, 'realistic')/3600, 'o', 'MarkerSize', 3.5, 'MarkerFaceColor', BLUE, 'MarkerEdgeColor', 'w');
                text(ax, 165, El/ec.p_net(150e-6, 'realistic')/3600*1.5, '2.26 h', 'FontSize', 5.6, 'Color', BLUE, 'FontWeight', 'bold');
                xlabel(ax, 'P_MFC (µW)', 'Interpreter', 'none'); ylabel(ax, 'Δt (h)'); xlim(ax, [60 400]); ylim(ax, [0.5 100]);
            case 7
                x = linspace(0, 2.5, 200); plot(ax, x, 2.^(-x), 'Color', MUTE, 'LineWidth', 1.3);
                yline(ax, 0.5, ':', 'Color', INK2, 'LineWidth', 0.7);
                text(ax, 0.08, 0.92, 'short path: anomaly', 'FontSize', 5.4, 'Color', INK2, 'VerticalAlignment', 'top');
                xlabel(ax, 'E[h]/c(ψ)'); ylabel(ax, 's'); ylim(ax, [0 1.05]);
            case 8
                P = ec.params(); e = ec.lora_toa(7:12)*P.I_TX*P.V_CC*1e3;
                b = bar(ax, 1:6, e, 0.62, 'FaceColor', 'flat', 'EdgeColor', 'none'); b.CData = repmat(GREY, 6, 1); b.CData(1, :) = BLUE;
                text(ax, 1, 40, '16.3', 'FontSize', 5.4, 'HorizontalAlignment', 'center', 'Color', BLUE, 'FontWeight', 'bold');
                set(ax, 'XTick', 1:6, 'XTickLabel', {'7', '8', '9', '10', '11', '12'}); xlabel(ax, 'SF'); ylabel(ax, 'mJ/packet'); ylim(ax, [0 500]);
        end
        ax.XLabel.FontSize = 5.6; ax.YLabel.FontSize = 5.6; ax.XLabel.Color = INK2; ax.YLabel.Color = INK2;
        ax.XLabel.Interpreter = 'none'; ax.YLabel.Interpreter = 'none'; ax.TickLabelInterpreter = 'none';
        grid(ax, 'off'); ax.YGrid = 'on'; ax.GridColor = RULE; ax.GridAlpha = 1;
    end
end
