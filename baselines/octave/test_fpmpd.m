% Kiem chung findpeaks_mpd == findpeaks(...,'MinPeakDistance',...) tren du lieu ngan
pkg load signal;
addpath(fileparts(mfilename('fullpath')));
rand('seed', 7); randn('seed', 7);
nfail = 0; ncase = 0;
for trial = 1:12
  n = 20000;
  fs = 4000;
  rr = 0.38 + 0.02*randn(1,60);
  t = (0:n-1)/fs;
  x = zeros(1,n);
  pos = 200;
  k = 1;
  while pos < n-200
    x(round(pos)) = 1 + 0.3*randn();
    pos = pos + rr(min(k,numel(rr)))*fs;
    k = k + 1;
  end
  x = filter(gausswin(41)/sum(gausswin(41)), 1, x);
  x = x + 0.05*randn(1,n);
  x = x - min(x);
  for dist = [400 1000 1360 2000]
    ncase = ncase + 1;
    [~, i1] = findpeaks(x, 'MinPeakDistance', dist);
    [~, i2] = findpeaks_mpd(x, dist);
    i1 = i1(:)'; i2 = i2(:)';
    if numel(i1) == numel(i2) && all(i1 == i2)
      ;
    else
      nfail = nfail + 1;
      printf('LECH trial=%d dist=%d: octave=%d dinh, mpd=%d dinh, giao=%d\n', ...
             trial, dist, numel(i1), numel(i2), numel(intersect(i1,i2)));
    end
  end
end
printf('KET QUA: %d/%d truong hop KHOP tuyet doi\n', ncase-nfail, ncase);

% do toc do tren vector dai (findpeaks goc se OOM -> chi do mpd)
xl = cumsum(randn(1, 2395600)); xl = xl - min(xl);
t0 = tic(); [~, ii] = findpeaks_mpd(xl, 1360); e = toc(t0);
printf('mpd tren 2395600 mau: %d dinh, %.1f s\n', numel(ii), e);
