function make_fig_schematic(out)
%MAKE_FIG_SCHEMATIC Reference circuit of the node around the BQ25570: pin names and numbers, external
%   parts and divider equations follow the datasheet (SLUSBH2G, Sections 7.3 and 8.2). The thresholds
%   drawn on the figure are computed from the resistor values below.
here = fileparts(mfilename('fullpath'));
if nargin < 1, out = fullfile(fileparts(here), 'paper', 'figures'); end
VBIAS = 1.21; ROV = [4.75 8.25]; ROK = [4.22 8.06 0.698]; ROUT = [4.75 8.25];
V_ov = 1.5*VBIAS*(1 + ROV(2)/ROV(1));
V_ok = VBIAS*(1 + ROK(2)/ROK(1));
V_hy = VBIAS*(1 + (ROK(2) + ROK(3))/ROK(1));
V_out = VBIAS*(1 + ROUT(2)/ROUT(1));
assert(abs(V_ov - 5.0) < 0.05 && abs(V_ok - 3.5) < 0.03 && V_hy > V_ok && V_hy < V_ov && abs(V_out - 3.3) < 0.02);
assert(all([sum(ROV) sum(ROK) sum(ROUT)] >= 11 & [sum(ROV) sum(ROK) sum(ROUT)] <= 15));

h = @(s) sscanf(s(2:end), '%2x%2x%2x', [1 3])/255;
RES = h('#c2188b'); CAP = h('#1ea0d6'); IND = h('#0f7f8c'); INK = h('#0b0b0b'); INK2 = h('#3c3c3c'); MUTE = h('#a8a6a0'); BLUE = h('#1e78d2'); LBLUE = h('#e8f1f8');
f = figure('Units', 'inches', 'Position', [1 1 7.4 5.33], 'Color', 'w', 'Visible', 'off');
ax = axes(f, 'Position', [0 0 1 1]); hold(ax, 'on'); axis(ax, [0 100 0 72]); axis(ax, 'off');

    function tx(x, y, s, sz, col, varargin)
        text(ax, x, y, s, 'FontName', 'Arial', 'FontSize', sz, 'Color', col, 'Interpreter', 'none', varargin{:});
    end
    function ln(x, y, col, lw)
        if nargin < 3, col = INK; end
        if nargin < 4, lw = 0.8; end
        plot(ax, x, y, '-', 'Color', col, 'LineWidth', lw);
    end
    function dot(x, y, col)
        if nargin < 3, col = INK; end
        plot(ax, x, y, 'o', 'MarkerSize', 2.6, 'MarkerFaceColor', col, 'MarkerEdgeColor', col);
    end
    function region(x0, y0, w, hgt, s)
        rectangle(ax, 'Position', [x0 y0 w hgt], 'EdgeColor', MUTE, 'LineWidth', 0.7, 'LineStyle', '--');
        tx(x0 + 0.7, y0 + hgt - 1.1, s, 5.8, INK, 'FontWeight', 'bold');
    end
    function gnd(x, y)
        ln([x x], [y y - 1.0]);
        ln([x - 1.3 x + 1.3], [y - 1.0 y - 1.0], INK, 0.9);
        ln([x - 0.8 x + 0.8], [y - 1.5 y - 1.5], INK, 0.8);
        ln([x - 0.3 x + 0.3], [y - 2.0 y - 2.0], INK, 0.7);
    end
    function capv(x, y)
        ln([x - 1.4 x + 1.4], [y + 0.4 y + 0.4], CAP, 1.5);
        ln([x - 1.4 x + 1.4], [y - 0.4 y - 0.4], CAP, 1.5);
    end
    function caph(x, y)
        ln([x - 0.35 x - 0.35], [y - 1.0 y + 1.0], CAP, 1.5);
        ln([x + 0.35 x + 0.35], [y - 1.0 y + 1.0], CAP, 1.5);
    end
    function resv(x, y1, y0)
        n = 6; ym = linspace(y1 - 0.7, y0 + 0.7, 2*n + 1); xs = x + 0.7*[0 repmat([1 -1], 1, n - 1) 1 0];
        ln([x x], [y1 y1 - 0.7]); ln(xs(1:numel(ym)), ym, RES, 1.1); ln([x x], [y0 + 0.7 y0]);
    end
    function indh(x0, x1, y, col)
        th = linspace(pi, 0, 24); n = 4; w = (x1 - x0)/n;
        for k = 1:n
            ln(x0 + (k - 0.5)*w + w/2*cos(th), y + 0.9*sin(th), col, 1.2);
        end
    end
    function cell(x, y)
        ln([x - 1.8 x + 1.8], [y + 0.45 y + 0.45], INK, 1.1);
        ln([x - 0.9 x + 0.9], [y - 0.45 y - 0.45], INK, 1.6);
    end
    function pinl(y, name, num)
        ln([33 34], [y y]); tx(34.6, y, name, 5.6, INK, 'VerticalAlignment', 'middle');
        tx(33.5, y + 0.25, num, 4.6, INK2, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
    end
    function pinr(y, name, num)
        ln([60 61], [y y]); tx(59.4, y, name, 5.6, INK, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
        tx(60.5, y + 0.25, num, 4.6, INK2, 'VerticalAlignment', 'bottom');
    end
    function pint(x, name, num)
        ln([x x], [52 53]); tx(x, 51.4, name, 5.6, INK, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
        tx(x + 0.3, 52.5, num, 4.6, INK2, 'VerticalAlignment', 'bottom');
    end
    function pinb(x, name, num)
        ln([x x], [25 26]); tx(x, 26.6, name, 5.4, INK, 'Rotation', 90, 'VerticalAlignment', 'middle');
        tx(x + 0.3, 25.5, num, 4.6, INK2, 'VerticalAlignment', 'top');
    end
    function loadbox(x0, y0, w, hgt, t, s1, s2)
        rectangle(ax, 'Position', [x0 y0 w hgt], 'EdgeColor', INK, 'LineWidth', 0.9, 'FaceColor', 'w');
        tx(x0 + w/2, y0 + hgt - 1.7, t, 6.2, INK, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        tx(x0 + w/2, y0 + hgt - 4.3, s1, 5.4, INK2, 'HorizontalAlignment', 'center');
        tx(x0 + w/2, y0 + hgt - 6.5, s2, 5.4, INK2, 'HorizontalAlignment', 'center');
    end
    function sw(xc, yc)
        rectangle(ax, 'Position', [xc - 1.7 yc - 1.2 3.4 2.4], 'EdgeColor', INK, 'LineWidth', 0.8, 'FaceColor', 'w');
        tx(xc, yc, 'SW', 5.0, INK, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', 'FontWeight', 'bold');
    end

% ---------------- U1
rectangle(ax, 'Position', [34 26 26 26], 'EdgeColor', INK, 'LineWidth', 1.3, 'FaceColor', LBLUE);
tx(48, 46, 'U1: BQ25570', 7.2, INK, 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
tx(48, 42.2, 'boost charger + buck', 5.6, INK2, 'HorizontalAlignment', 'center');
pinl(48, 'VIN_DC', '2'); pinl(44, 'LBOOST', '20'); pinl(40, 'VOC_SAMP', '3'); pinl(37.8, 'VREF_SAMP', '4');
pinl(35.6, 'EN', '5'); pinl(33.4, 'VSS', '1');
pinr(48, 'LBUCK', '16'); pinr(44, 'VOUT', '14'); pinr(40, 'VOUT_EN', '6'); pinr(36.5, 'VBAT_OK', '13'); pinr(33.4, 'VSS', '15');
pint(41, 'VSTOR', '19'); pint(54, 'VBAT', '18');
pinb(36, 'VRDIV', '8'); pinb(39.5, 'VBAT_OV', '7'); pinb(45, 'OK_PROG', '11'); pinb(50, 'OK_HYST', '10'); pinb(56, 'VOUT_SET', '12');

% ---------------- source
region(1, 36, 26.5, 18, 'SOIL-MFC ARRAY (2s5p)');
ln([8 33], [48 48]); dot(8, 48);
ln([8 8], [48 46.4]); cell(8, 46); ln([8 8], [45.5 43.4]); cell(8, 43); ln([8 8], [42.5 40.5]); gnd(8, 40.5);
tx(10.5, 44.6, {'10 cells', '15–30 µW each', '5 strings of 2'}, 5.0, INK2, 'VerticalAlignment', 'middle');
tx(9, 49, '≈150 µW', 5.8, BLUE, 'FontWeight', 'bold', 'VerticalAlignment', 'bottom');
ln([21 21], [48 44.4]); dot(21, 48); capv(21, 44); ln([21 21], [43.6 41.5]); gnd(21, 41.5);
tx(22.8, 44, {'C_IN', '4.7 µF'}, 5.0, INK2, 'VerticalAlignment', 'middle');
ln([28 28], [48 44]); dot(28, 48); indh(28, 32.2, 44, IND); ln([32.2 33], [44 44]);
tx(30.1, 45.2, 'L1 22 µH', 5.0, INK2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');

% ---------------- MPPT and enable
region(1, 24.8, 27, 10.4, 'MPPT AND ENABLE');
ln([31 33], [40 40]); ln([31 33], [35.6 35.6]); ln([31 33], [33.4 33.4]); ln([31 31], [40 32.4]);
dot(31, 35.6); dot(31, 33.4); ln([33 32.3], [37.8 37.8]); caph(31.95, 37.8); ln([31.6 31], [37.8 37.8]); dot(31, 37.8);
gnd(31, 32.4);
tx(1.7, 31.2, 'VOC_SAMP to VSS: MPPT at 50% of V_oc', 5.2, INK2, 'VerticalAlignment', 'middle');
tx(1.7, 29.0, 'C_REF 10 nF on VREF_SAMP', 5.2, INK2, 'VerticalAlignment', 'middle');
tx(1.7, 26.8, 'EN to VSS: device enabled', 5.2, INK2, 'VerticalAlignment', 'middle');

% ---------------- storage
region(36, 54.5, 38, 16.5, 'MAIN ENERGY STORAGE');
ln([41 41], [53 67]); ln([41 46], [67 67]);
ln([46 46], [67 62.4]); capv(46, 62); ln([46 46], [61.6 60]); gnd(46, 60);
tx(47.8, 62, {'C_STOR', '4.7 + 0.1 µF'}, 4.6, INK2, 'VerticalAlignment', 'middle');
ln([54 54], [53 66]); ln([54 58], [66 66]); dot(58, 66);
ln([58 58], [66 64.9]); capv(58, 64.5); ln([58 58], [64.1 61.4]); capv(58, 61); ln([58 58], [60.6 59.4]); gnd(58, 59.4);
tx(60.2, 63.6, {'2 × 2.7 V, 1 F in series', '0.5 F, ≈3.2 J usable'}, 5.0, INK2, 'VerticalAlignment', 'middle');
ln([58 58], [66 68.4]); ln([58 65], [68.4 68.4]); patch(ax, [65 63.8 63.8], [68.4 68.9 67.9], INK, 'EdgeColor', 'none');
tx(65.3, 68.4, {'to ESP32 ADC', 'gated divider'}, 4.6, INK2, 'VerticalAlignment', 'middle');

% ---------------- buck, enable and rail
ln([61 62], [48 48]); indh(62, 66, 48, IND); ln([66 67], [48 48]); ln([61 67], [44 44]); ln([67 67], [44 48]); dot(67, 48);
tx(64, 49.3, 'L2 10 µH', 5.0, INK2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
ln([61 65], [40 40]); ln([61 65], [36.5 36.5]); ln([65 65], [36.5 40]);
tx(61.4, 38.2, 'buck on', 4.8, INK2, 'VerticalAlignment', 'middle');
ln([61 63], [33.4 33.4]); gnd(63, 33.4);

region(69.5, 1.5, 30, 53, 'AIoT SENSOR NODE (3.3 V RAIL)');
ln([67 98], [48 48], BLUE, 1.5); ln([72 72], [48 8.2], BLUE, 1.5); dot(72, 48, BLUE);
tx(73, 48.6, 'V_OUT = 3.3 V', 5.8, BLUE, 'FontWeight', 'bold', 'VerticalAlignment', 'bottom');
ln([80 80], [48 45.4]); dot(80, 48); capv(80, 45); ln([80 80], [44.6 43.4]); gnd(80, 43.4);
tx(81.8, 45, {'C_OUT', '22 µF'}, 5.0, INK2, 'VerticalAlignment', 'middle');
ln([90 90], [48 45.4]); dot(90, 48); capv(90, 45); ln([90 90], [44.6 43.4]); gnd(90, 43.4);
tx(91.8, 45, {'C_burst', '≥ 46 mF'}, 5.0, INK2, 'VerticalAlignment', 'middle');
rectangle(ax, 'Position', [84 49 14 2.5], 'EdgeColor', BLUE, 'LineWidth', 1.0, 'FaceColor', 'w');
tx(91, 50.25, 'P_net ≈ 80 µW', 6.0, BLUE, 'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
loadbox(78, 29, 20, 9.5, 'Soil sensors', '3 probes, 16.5 mA in total', '2 s window');
loadbox(78, 16.5, 20, 9.5, 'ESP32', 'deep sleep 10 µA', 'active 80 mA');
loadbox(78, 3.5, 20, 9.5, 'SX1278 LoRa', 'SF7, 120 mA', '16.3 mJ per packet');
ln([72 73.3], [33.7 33.7], BLUE, 1.5); sw(75, 33.7); ln([76.7 78], [33.7 33.7], BLUE, 1.5); dot(72, 33.7, BLUE);
ln([72 78], [21.2 21.2], BLUE, 1.5); dot(72, 21.2, BLUE);
ln([72 73.3], [8.2 8.2], BLUE, 1.5); sw(75, 8.2); ln([76.7 78], [8.2 8.2], BLUE, 1.5);
ln([88 88], [26 29]); ln([88 88], [13 16.5]);
tx(88.6, 27.5, 'ADC, 1-Wire', 4.8, INK2, 'VerticalAlignment', 'middle');
tx(88.6, 14.8, 'SPI', 4.8, INK2, 'VerticalAlignment', 'middle');

% ---------------- threshold dividers
region(29, 1.2, 39, 23.4, '');
tx(29.7, 2.6, 'THRESHOLD DIVIDERS', 5.8, INK, 'FontWeight', 'bold');
ln([36 36], [25 23]); ln([36 59], [23 23]); dot(37.5, 23); dot(47.5, 23); tx(36.4, 23.2, '', 4, INK);
ln([37.5 37.5], [23 22.6]); resv(37.5, 22.6, 14); dot(37.5, 14); resv(37.5, 14, 6.5); gnd(37.5, 6.5);
ln([39.5 39.5], [25 14]); ln([39.5 37.5], [14 14]);
tx(36.5, 18.5, {'R_OV2', sprintf('%.2f MΩ', ROV(2))}, 4.8, INK2, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
tx(36.5, 10.5, {'R_OV1', sprintf('%.2f MΩ', ROV(1))}, 4.8, INK2, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
ln([47.5 47.5], [23 22.6]); resv(47.5, 22.6, 16.6); dot(47.5, 16.6); resv(47.5, 16.6, 10.6); dot(47.5, 10.6); resv(47.5, 10.6, 5.6); gnd(47.5, 5.6);
ln([50 50], [25 16.6]); ln([50 47.5], [16.6 16.6]); ln([45 45], [25 10.6]); ln([45 47.5], [10.6 10.6]);
tx(50.8, 20.0, {'R_OK3', sprintf('%.3f MΩ', ROK(3))}, 4.8, INK2, 'VerticalAlignment', 'middle');
tx(50.8, 13.6, {'R_OK2', sprintf('%.2f MΩ', ROK(2))}, 4.8, INK2, 'VerticalAlignment', 'middle');
tx(50.8, 8.0, {'R_OK1', sprintf('%.2f MΩ', ROK(1))}, 4.8, INK2, 'VerticalAlignment', 'middle');
dot(59, 23); resv(59, 23, 14); dot(59, 14); resv(59, 14, 6.5); gnd(59, 6.5);
ln([56 56], [25 14]); ln([56 59], [14 14]);
tx(60.5, 18.5, {'R_OUT2', sprintf('%.2f MΩ', ROUT(2))}, 4.8, INK2, 'VerticalAlignment', 'middle');
tx(60.5, 10.5, {'R_OUT1', sprintf('%.2f MΩ', ROUT(1))}, 4.8, INK2, 'VerticalAlignment', 'middle');

% ---------------- programmed values
region(1, 1.2, 27, 22, 'PROGRAMMED THRESHOLDS');
tx(1.8, 18.2, sprintf('Bank ceiling V_BAT_OV = %.2f V', V_ov), 5.4, INK, 'VerticalAlignment', 'middle');
tx(1.8, 15.6, sprintf('Bank floor V_BAT_OK = %.2f V', V_ok), 5.4, INK, 'VerticalAlignment', 'middle');
tx(1.8, 13.0, sprintf('Buck restart at %.2f V (rising)', V_hy), 5.4, INK, 'VerticalAlignment', 'middle');
tx(1.8, 10.4, sprintf('Rail V_OUT = %.2f V', V_out), 5.4, INK, 'VerticalAlignment', 'middle');
tx(1.8, 7.0, sprintf('V_BIAS = %.2f V; each divider ≈ 13 MΩ,', VBIAS), 5.0, INK2, 'VerticalAlignment', 'middle');
tx(1.8, 5.0, 'biased from VRDIV only while sampling', 5.0, INK2, 'VerticalAlignment', 'middle');
exportgraphics(f, fullfile(out, 'fig_schematic.png'), 'Resolution', 600, 'BackgroundColor', 'white');
exportgraphics(f, fullfile(out, 'fig_schematic.pdf'), 'ContentType', 'vector', 'BackgroundColor', 'white');
close(f);
fprintf('V_ov %.3f V_ok %.3f V_hy %.3f V_out %.3f\n', V_ov, V_ok, V_hy, V_out);
end
