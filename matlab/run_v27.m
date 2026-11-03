% run_v27.m  Writes v27_results.json. Run:  >> run_v27
here = fileparts(mfilename('fullpath'));
addpath(here);
S = ec.sim_v27();
fid = fopen(fullfile(here, 'v27_results.json'), 'w');
fwrite(fid, jsonencode(S, 'PrettyPrint', true), 'char');
fclose(fid);
