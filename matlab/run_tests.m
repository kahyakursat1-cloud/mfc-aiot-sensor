% run_tests.m  Runs the MATLAB-vs-Python cross-validation suite.
here = fileparts(mfilename('fullpath'));
addpath(here);
results = runtests(fullfile(here, 'tests'));
disp(table(results));
assert(all([results.Passed]), 'cross-validation failed');
