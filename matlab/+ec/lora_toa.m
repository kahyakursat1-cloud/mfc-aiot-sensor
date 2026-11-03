function [t, n_sym] = lora_toa(sf, pl, bw, cr, n_pre, crc)
%LORA_TOA Time-on-air (s) of an explicit-header LoRa packet (SX127x datasheet formula).
%   The low data rate optimisation is on when the symbol lasts more than 16 ms, as the
%   datasheet requires, which at 125 kHz means SF11 and SF12.
if nargin < 2, pl = 13; end
if nargin < 3, bw = 125e3; end
if nargin < 4, cr = 1; end
if nargin < 5, n_pre = 8; end
if nargin < 6, crc = 0; end
ts = 2.^sf/bw;
de = ts > 16e-3;
n_sym = 8 + max(ceil((8*pl - 4*sf + 28 + 16*crc)./(4*(sf - 2*de))).*(cr + 4), 0);
t = (n_pre + 4.25 + n_sym).*ts;
end
