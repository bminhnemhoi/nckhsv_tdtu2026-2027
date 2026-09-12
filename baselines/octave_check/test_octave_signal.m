% Smoke test: can this Octave run the Power-MF critical path?
printf('octave version: %s\n', version());
try
  pkg load signal;
  printf('pkg load signal: OK\n');
catch e
  printf('pkg load signal: FAIL -- %s\n', e.message);
end

fs = 4000;                       % PowerMF runs at 4x1000 Hz after FecgInterp
t  = (0:1/fs:20-1/fs)';
x  = sin(2*pi*2.2*t) + 0.3*randn(size(t));   % ~132 bpm

% --- the 7 signal-package functions PowerMF's chain needs ---
ok = {};
try, [b,a]=butter(1,[0.7 8]/(fs/2)); ok{end+1}='butter'; catch, printf('butter FAIL\n'); end
try, y=filtfilt(b,a,x);              ok{end+1}='filtfilt'; catch, printf('filtfilt FAIL\n'); end
try, w=gausswin(256);                ok{end+1}='gausswin'; catch, printf('gausswin FAIL\n'); end
try, m=medfilt1(x,5);                ok{end+1}='medfilt1'; catch, printf('medfilt1 FAIL\n'); end
try, [h,f]=freqz(b,a,64,fs);         ok{end+1}='freqz'; catch, printf('freqz FAIL\n'); end
try, xi=interpft(x(1:1000),4000);    ok{end+1}='interpft'; catch, printf('interpft FAIL\n'); end

% pwelch: MATLAB signature pwelch(x, window, noverlap, nfft, fs)
try
  Nfft = 256;
  [Pxx,f2] = pwelch(x-mean(x), gausswin(Nfft), Nfft/2, Nfft, fs);
  printf('pwelch: OK  (Pxx len %d, f range %.2f..%.2f Hz)\n', numel(Pxx), f2(1), f2(end));
  ok{end+1}='pwelch';
catch e
  printf('pwelch: FAIL -- %s\n', e.message);
end

% findpeaks with MinPeakDistance -- the highest-risk API difference
try
  [pks, locs] = findpeaks(y, 'MINPEAKDISTANCE', round(0.34*fs));
  printf('findpeaks MINPEAKDISTANCE: OK  (%d peaks, median RR %.1f ms)\n', ...
         numel(locs), median(diff(locs))/fs*1000);
  ok{end+1}='findpeaks';
catch e
  printf('findpeaks: FAIL -- %s\n', e.message);
end

printf('\nPASSED %d/8: %s\n', numel(ok), strjoin(ok, ', '));
