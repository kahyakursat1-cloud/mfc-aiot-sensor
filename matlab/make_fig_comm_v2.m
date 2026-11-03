function make_fig_comm_v2(out)
%MAKE_FIG_COMM_V2 Communication chain (a) and the cost of one packet at SF7 and SF12 (b), in the
%   layout proposed by the co-author for Figure 6. Every number is computed from ec.lora_toa and ec.params.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'suscom', 'src'); end
P = ec.params();
[t7, n7] = ec.lora_toa(7); t12 = ec.lora_toa(12);
n_pre = 8 + 4.25; ts7 = 2^7/125e3;
e7 = t7*P.I_TX*P.V_CC*1e3; e12 = t12*P.I_TX*P.V_CC*1e3;
tp = n_pre*ts7*1e3; T = t7*1e3;
assert(abs(n_pre + n7 - T/(ts7*1e3)) < 1e-9);
DOT = char(183); APPROX = char(8776); TIMES = char(215);

h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
NAVY = h('#0d3b66'); TEAL = h('#1b6e78'); BLUE = h('#1e78d2'); LBLUE = h('#9fd0f5'); PALE = h('#eef5fb');
INK = h('#0b0b0b'); INK2 = h('#4a4a48'); MUTE = h('#9a9893'); AMBER = h('#e3a21a'); DAMBER = h('#a8650a'); PAMBER = h('#fdf6e6');
GREEN = h('#1f8a5b'); GREY = h('#c9ccd1'); DGREY = h('#2e3440');

f = figure('Units', 'inches', 'Position', [1 1 7.4 3.7], 'Color', 'w', 'Visible', 'off');
A = axes(f, 'Position', [0 0 1 1]); hold(A, 'on'); axis(A, [0 100 0 50]); axis(A, 'off');
    function tx(x, y, s, sz, col, varargin)
        text(A, x, y, s, 'FontName', 'Arial', 'FontSize', sz, 'Color', col, 'Interpreter', 'none', varargin{:});
    end
    function tt(x, y, s, sz, col, varargin)
        text(A, x, y, s, 'FontName', 'Arial', 'FontSize', sz, 'Color', col, 'Interpreter', 'tex', varargin{:});
    end
    function box(x0, y0, w, hh, fc, ec_, lw, cv)
        rectangle(A, 'Position', [x0 y0 w hh], 'FaceColor', fc, 'EdgeColor', ec_, 'LineWidth', lw, 'Curvature', cv);
    end
    function card(x0, w, ttl, lines, hc)
        box(x0, 25.2, w, 8.2, 'w', hc, 1.0, 0.05);
        box(x0, 29.6, w, 3.8, hc, hc, 1.0, 0.05);
        tx(x0 + w/2, 31.5, ttl, 7.4, 'w', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        for k = 1:numel(lines)
            tx(x0 + w/2, 28.2 - 2.0*(k - 1) - (numel(lines) == 1)*0.9, lines{k}, 6.6, INK, 'HorizontalAlignment', 'center');
        end
    end
    function arr(x0, x1, y, col, lab)
        plot(A, [x0 x1 - 1.2], [y y], '-', 'Color', col, 'LineWidth', 1.3);
        patch(A, [x1, x1 - 1.5, x1 - 1.5], [y, y + 0.8, y - 0.8], col, 'EdgeColor', 'none');
        if nargin > 4, tx((x0 + x1)/2, y + 1.0, lab, 6.8, NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontWeight', 'bold'); end
    end
    function waves(x, y, col)
        for r = [1.2 2.2 3.2]
            t = linspace(-0.75, 0.75, 30);
            plot(A, x + r*cos(t), y + 1.6*r*sin(t), '-', 'Color', col, 'LineWidth', 1.0);
        end
    end
    function dimarrow(x0, x1, y, lab)
        plot(A, [x0 x1], [y y], '-', 'Color', NAVY, 'LineWidth', 0.8);
        patch(A, [x0, x0 + 1.0, x0 + 1.0], [y, y + 0.5, y - 0.5], NAVY, 'EdgeColor', 'none');
        patch(A, [x1, x1 - 1.0, x1 - 1.0], [y, y + 0.5, y - 0.5], NAVY, 'EdgeColor', 'none');
        plot(A, [x0 x0], [y - 0.8 y + 0.8], '-', 'Color', NAVY, 'LineWidth', 0.8);
        plot(A, [x1 x1], [y - 0.8 y + 0.8], '-', 'Color', NAVY, 'LineWidth', 0.8);
        tx((x0 + x1)/2, y, lab, 7.4, NAVY, 'HorizontalAlignment', 'center', 'FontWeight', 'bold', 'BackgroundColor', 'w', 'Margin', 0.5);
    end

% ======================= (a) communication chain
tx(1, 48.3, '(a)', 9.5, NAVY, 'FontWeight', 'bold');
tx(5.5, 48.3, 'From soil sensor to cloud', 9.5, NAVY, 'FontWeight', 'bold');
box(1, 23.8, 45.5, 22.2, PALE, BLUE, 0.8, 0.02);
set(findobj(A, 'Type', 'rectangle', '-and', 'EdgeColor', BLUE, '-and', 'FaceColor', PALE), 'LineStyle', '--');
tx(3, 44.4, ['Battery-free node ' DOT ' included in the energy budget'], 7.0, BLUE, 'FontWeight', 'bold');

% sensor node icon: board with MCU and two soil probes
box(6, 36.0, 13, 5.6, DGREY, DGREY, 0.6, 0.08);
box(10.5, 37.2, 4.4, 3.2, GREY, GREY, 0.5, 0.05);
tx(12.7, 38.8, 'MCU', 5.2, DGREY, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
for xp = [7.4 9.4]
    patch(A, [xp xp + 0.9 xp + 0.45], [36.0 36.0 33.6], MUTE, 'EdgeColor', DGREY, 'LineWidth', 0.4);
end
card(3, 16, 'Sensor node', {'ESP32 + sensors', '13-byte packet'}, NAVY);
arr(19, 26, 38.8, NAVY, 'SPI');

% LoRa module icon with antenna
box(26.5, 36.0, 12, 5.6, BLUE, NAVY, 0.6, 0.08);
box(29.6, 37.1, 5.8, 3.4, NAVY, NAVY, 0.5, 0.05);
tx(32.5, 38.8, 'SX1278', 5.2, 'w', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
plot(A, [38.5 40.2], [41.6 41.6], '-', 'Color', DGREY, 'LineWidth', 1.0);
plot(A, [40.2 40.2], [41.6 43.6], '-', 'Color', DGREY, 'LineWidth', 1.8);
card(24.5, 16, 'LoRa transmitter', {['SX1278 ' DOT ' 433 MHz'], ['SF7 ' DOT ' 125 kHz']}, NAVY);
waves(41.6, 40.0, BLUE);

% LoRa uplink
arr(46.8, 53.2, 38.8, NAVY);
tx(50, 41.2, {'LoRa', 'uplink'}, 6.8, NAVY, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontWeight', 'bold');

% gateway icon
box(55.5, 35.6, 10, 3.2, GREY, DGREY, 0.6, 0.4);
for xl = 57.2:1.6:60.4, plot(A, xl, 37.2, 'o', 'MarkerSize', 2.2, 'MarkerFaceColor', GREEN, 'MarkerEdgeColor', 'none'); end
plot(A, [57 57], [38.8 43.6], '-', 'Color', DGREY, 'LineWidth', 1.8);
for r = [0.9 1.7 2.5]
    t = linspace(pi/4, 3*pi/4, 20);
    plot(A, 62.2 + r*cos(t), 40.0 + 1.5*r*sin(t), '-', 'Color', BLUE, 'LineWidth', 1.0);
end
card(53.5, 14, 'Gateway', {['LoRa Rx + Wi-Fi']}, TEAL);
arr(67.5, 72.5, 38.8, NAVY, 'MQTT');

% broker icon: stacked servers
for k = 0:2
    box(75.0, 35.4 + 2.0*k, 8.5, 1.7, DGREY, DGREY, 0.5, 0.15);
    plot(A, 81.6, 36.25 + 2.0*k, 's', 'MarkerSize', 2.0, 'MarkerFaceColor', LBLUE, 'MarkerEdgeColor', 'none');
end
card(72.5, 14, 'MQTT broker', {'Mosquitto'}, TEAL);
arr(86.5, 89.5, 38.8, NAVY);

% cloud icon with dashboard trace
cx = [92.0 94.6 97.2 95.6 93.0]; cy = [39.2 41.4 39.4 38.0 38.0]; cr = [1.9 2.4 1.8 1.9 1.8];
for i = 1:5
    rectangle(A, 'Position', [cx(i) - cr(i), cy(i) - cr(i)*0.85, 2*cr(i), 1.7*cr(i)], 'Curvature', [1 1], 'FaceColor', LBLUE, 'EdgeColor', 'none');
end
xs_ = linspace(91.6, 97.6, 7); ys_ = [38.2 39.4 38.8 40.2 39.6 40.8 40.4];
plot(A, xs_, ys_, '-', 'Color', NAVY, 'LineWidth', 1.0);
card(89.5, 10.5, 'Cloud', {'Dashboard'}, TEAL);

% bracket under the infrastructure
plot(A, [53.5 53.5 99.5 99.5], [24.4 23.6 23.6 24.4], '-', 'Color', TEAL, 'LineWidth', 0.9);
plot(A, [76.5 76.5], [23.6 22.9], '-', 'Color', TEAL, 'LineWidth', 0.9);
tx(76.5, 22.0, ['Externally powered ' DOT ' excluded from the node budget'], 7.0, TEAL, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
plot(A, [1 99.5], [19.6 19.6], '-', 'Color', NAVY, 'LineWidth', 0.8);

% ======================= (b) one packet at SF7 and SF12
tx(1, 17.6, '(b)', 9.5, NAVY, 'FontWeight', 'bold');
tx(5.5, 17.6, 'One packet, two energy costs', 9.5, NAVY, 'FontWeight', 'bold');
box(1, 8.6, 7.4, 3.8, BLUE, BLUE, 0.6, 0.15);
tx(4.7, 10.5, {'SF7', 'packet'}, 6.8, 'w', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
waves(8.6, 10.5, BLUE);
x0 = 13.5; x1 = 62; xs = @(t) x0 + (x1 - x0)*t/T;
box(xs(0), 8.3, xs(tp) - xs(0), 4.4, LBLUE, NAVY, 0.6, 0);
box(xs(tp), 8.3, xs(T) - xs(tp), 4.4, TEAL, NAVY, 0.6, 0);
tx((xs(0) + xs(tp))/2, 10.5, {'Preamble', sprintf('%.2f symbols', n_pre)}, 6.6, NAVY, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
tx((xs(tp) + xs(T))/2, 10.5, {sprintf('Header + %d-byte payload', 13), sprintf('%d symbols', n7)}, 6.6, 'w', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
dimarrow(xs(0), xs(tp), 14.4, sprintf('%.1f%%', 100*tp/T));
dimarrow(xs(tp), xs(T), 14.4, sprintf('%.1f%%', 100*(T - tp)/T));
plot(A, [x0 x1], [7.4 7.4], '-', 'Color', NAVY, 'LineWidth', 1.0);
for t = [0 tp T]
    plot(A, xs(t), 7.4, 'o', 'MarkerSize', 3, 'MarkerFaceColor', NAVY, 'MarkerEdgeColor', 'none');
    tx(xs(t), 6.4, sprintf('%.1f ms', t), 6.6, INK, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
end
set(findobj(A, 'Type', 'text', 'String', '0.0 ms'), 'String', '0 ms');
box(1, 0.6, 62, 3.6, PALE, PALE, 0.5, 0.25);
tx(2.2, 2.4, ['SF7 ' DOT ' BW 125 kHz ' DOT ' CR 4/5 ' DOT ' explicit header ' DOT ' CRC off'], 6.4, INK);
tt(40.5, 2.4, sprintf('T_{sym} = %.3f ms', ts7*1e3), 6.4, INK);
tx(51.5, 2.4, sprintf('TX %.0f mA at %.1f V', P.I_TX*1e3, P.V_CC), 6.4, INK);

box(66, 14.2, 33.5, 3.9, PALE, PALE, 0.5, 0.2);
tx(82.75, 16.8, 'Radio transmission energy', 7.6, NAVY, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
tx(82.75, 14.9, 'one packet, radio only', 6.2, INK2, 'HorizontalAlignment', 'center');
    function ecard(x0_, sf, tms, emj, ec_, tc, fc)
        box(x0_, 0.6, 12.5, 12.4, fc, ec_, 1.2, 0.08);
        tx(x0_ + 6.25, 11.3, sprintf('SF%d', sf), 8.4, tc, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        tx(x0_ + 6.25, 8.4, sprintf('%.*f ms', double(tms < 100), tms), 7.6, tc, 'HorizontalAlignment', 'center');
        plot(A, [x0_ + 2.5 x0_ + 10], [6.9 6.9], '-', 'Color', ec_, 'LineWidth', 0.6);
        tx(x0_ + 6.25, 4.9, sprintf('%s mJ', num2str(emj, '%.3g')), 10, tc, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        tx(x0_ + 6.25, 2.2, {'radio', 'energy'}, 5.6, tc, 'HorizontalAlignment', 'center');
    end
ecard(66, 7, t7*1e3, e7, BLUE, NAVY, 'w');
ecard(87, 12, t12*1e3, e12, AMBER, DAMBER, PAMBER);
tx(82.75, 7.6, sprintf('%s%.0f%s', APPROX, e12/e7, TIMES), 12, NAVY, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
tx(82.75, 4.0, {'energy', 'at SF12'}, 6.2, INK2, 'HorizontalAlignment', 'center');

exportgraphics(f, fullfile(out, 'fig_comm_v2.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'fig_comm_v2.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
fprintf('toa7 %.2f ms, toa12 %.1f ms, e7 %.2f mJ, e12 %.1f mJ, ratio %.2f, preamble %.1f%%\n', t7*1e3, t12*1e3, e7, e12, e12/e7, 100*tp/T);
end
