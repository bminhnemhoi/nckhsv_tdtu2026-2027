pkg load signal;
fs = 4000;
t  = (0:1/fs:20-1/fs)';
x  = sin(2*pi*2.2*t) + 0.3*randn(size(t));
[b,a] = butter(1,[0.7 8]/(fs/2));
y = filtfilt(b,a,abs(x));
Nfft = 256;

printf('--- FIX 1: pwelch overlap as FRACTION not samples ---\n');
try
  [Pxx,f2] = pwelch(x-mean(x), gausswin(Nfft), 0.5, Nfft, fs);
  printf('  pwelch(...,0.5,...) OK: %d bins, 0..%.1f Hz\n', numel(Pxx), f2(end));
  lo = find(f2>1.8)(1); hi = find(f2<3)(end);
  pk = max(findpeaks(Pxx(lo:hi)));
  if isempty(pk), printf('  no peak in 1.8-3.0 Hz\n'); else
    printf('  peak in fetal band = %.4g\n', pk); end
catch e
  printf('  FAIL: %s\n', e.message);
end

printf('--- FIX 2: findpeaks on data with negatives ---\n');
d = round(0.34*fs);
printf('  y has negatives? %d (min %.3f)\n', any(y<0), min(y));
try
  [p1,l1] = findpeaks(y,'MINPEAKDISTANCE',d);
  printf('  plain call OK: %d peaks\n', numel(l1));
catch e
  printf('  plain call FAIL: %s\n', e.message);
end
try
  [p2,l2] = findpeaks(y,'MINPEAKDISTANCE',d,'DoubleSided');
  printf('  DoubleSided OK: %d peaks (includes troughs -- WRONG for PowerMF)\n', numel(l2));
catch e
  printf('  DoubleSided FAIL: %s\n', e.message);
end
% correct fix: shift so signal is non-negative, matching MATLAB semantics
try
  ys = y - min(y);
  [p3,l3] = findpeaks(ys,'MINPEAKDISTANCE',d);
  printf('  shifted y-min(y) OK: %d peaks, median RR %.1f ms\n', ...
         numel(l3), median(diff(l3))/fs*1000);
catch e
  printf('  shifted FAIL: %s\n', e.message);
end
