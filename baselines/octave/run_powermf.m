% run_powermf.m -- driver Octave cho Power-MF (Jaeger 2024) tren mot ban ghi.
%
% Goi:  octave-cli --no-gui --quiet run_powermf.m <in.mat> <out.mat> <varanini_dir> <ms>
% Vao:  in.mat  chua  signal [4 x N], Fs, fqrs, rec   (do baselines/powermf_export.py tao)
% Ra:   out.mat chua  fPeaks (chi so mau @Fs, 1-based), elapsed_s, ok, err
%
% Tuan thu benchmark_algorithms.m cua repo goc:
%   - chi lay 4 kenh dau  (signal(1:4,:))
%   - ban ghi dai > 500000 mau bi cat doi va ghep lai:  [r1, r2 + bis + 1]
% PowerMF.m dung o day la BAN DA VA cho Octave (xem apply_patches.py).

pkg load signal;

args = argv();
in_mat   = args{1};
out_mat  = args{2};
var_dir  = args{3};
if numel(args) >= 4
    ms = str2double(args{4});
else
    ms = 340;
end

here = fileparts(mfilename('fullpath'));
addpath(here);                 % PowerMF.m (da va) + matched_filter.m
addpath(genpath(var_dir));     % 30 ham xCinC cua Varanini 2014

S = load(in_mat);
signal = double(S.signal);
Fs = double(S.Fs);
rec = S.rec;

if size(signal,1) > 4
    signal = signal(1:4,:);
end

printf('[octave] rec=%s  kenh=%d  N=%d  Fs=%g  ms=%g\n', rec, size(signal,1), size(signal,2), Fs, ms);
fflush(stdout);

t0 = tic();
ok = 1; err = '';
try
    if size(signal,2) > 500000
        bis = floor(size(signal,2)/2);
        printf('[octave] ban ghi dai -> cat doi tai mau %d (nhu benchmark_algorithms.m)\n', bis);
        fflush(stdout);
        r1 = PowerMF(signal(:,1:bis), Fs, ms);
        r2 = PowerMF(signal(:,bis+1:end), Fs, ms);
        fPeaks = [r1(:)', r2(:)' + bis + 1];
    else
        fPeaks = PowerMF(signal, Fs, ms);
        fPeaks = fPeaks(:)';
    end
catch e
    ok = 0;
    err = e.message;
    fPeaks = [];
    printf('[octave] LOI: %s\n', err);
end
elapsed_s = toc(t0);

if isempty(fPeaks)
    ok = 0;
    if isempty(err)
        err = 'PowerMF tra ve rong (try/catch noi bo cua PowerMF.m da nuot loi)';
    end
end

printf('[octave] xong rec=%s  n_peaks=%d  %.1f s  ok=%d\n', rec, numel(fPeaks), elapsed_s, ok);
fflush(stdout);

save('-v7', out_mat, 'fPeaks', 'elapsed_s', 'ok', 'err', 'rec');
