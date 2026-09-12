function [pks, idx] = findpeaks_mpd(x, distance)
% findpeaks_mpd -- thay the findpeaks(x,'MinPeakDistance',d) cua Octave.
%
% VI SAO CAN: findpeaks cua Octave (signal 1.4.x) cai dat rang buoc MinPeakDistance
% bang mot ma tran khoang cach doi mot giua CAC UNG VIEN DINH (line ~203),
% tuc O(k^2) bo nho. Tren ban ghi Silesia B1 (598900 mau x noi suy 4 = 2395600 mau)
% so ung vien dinh len toi hang tram nghin -> ma tran ~1e10 phan tu ->
% "out of memory or dimension too large for Octave's index type".
% MATLAB lam viec nay bang thuat toan tham O(k log k) nen khong bao gio loi.
%
% Ham nay tai lap DUNG NGU NGHIA cua MATLAB findpeaks:
%   1. tim moi cuc dai dia phuong (co xu ly vung bang phang -> lay diem giua)
%   2. sap xep theo bien do giam dan
%   3. tham lam: nhan dinh cao nhat, loai moi dinh cach no < distance, lap lai
% Buoc 3 dung danh sach lien ket doi nen moi ung vien bi go DUNG MOT LAN -> O(k).
%
% Vao : x        vector (hang hoac cot)
%       distance MinPeakDistance tinh bang MAU
% Ra  : pks      bien do cac dinh (theo thu tu vi tri tang dan)
%       idx      chi so mau cua cac dinh (1-based, thu tu tang dan)

  x = x(:).';
  n = numel(x);
  if n < 3
    pks = []; idx = []; return;
  end

  d = diff(x);
  s = sign(d);
  % vung bang phang: dien dau khong khong bang dau khac khong gan nhat ve BEN TRAI
  % (vector hoa, O(n) -- khong dung vong lap vi s co the dai hang trieu phan tu)
  nz = find(s ~= 0);
  if isempty(nz)
    pks = []; idx = []; return;
  end
  mark = zeros(1, numel(s));
  mark(nz) = 1;
  cs = cumsum(mark);
  ok = cs >= 1;
  s2 = zeros(1, numel(s));
  s2(ok) = s(nz(cs(ok)));
  s = s2;
  cand = find(s(1:end-1) > 0 & s(2:end) < 0) + 1;
  if isempty(cand)
    pks = []; idx = []; return;
  end

  k = numel(cand);
  if ~(distance > 0) || k == 1
    idx = cand; pks = x(idx); return;
  end

  h = x(cand);                  % bien do ung vien, theo thu tu vi tri tang dan
  prevA = (0:k-1);              % danh sach lien ket doi tren thu tu VI TRI
  nextA = (2:k+1);              % 0 = het trai, k+1 = het phai
  alive = true(1, k);

  [~, ord] = sort(h, 'descend');
  keep = false(1, k);

  for t = 1:k
    j = ord(t);
    if ~alive(j)
      continue;
    end
    keep(j) = true;
    % go moi ung vien con song cach cand(j) < distance (hai phia)
    p = prevA(j);
    while p >= 1 && (cand(j) - cand(p)) < distance
      alive(p) = false;
      pp = prevA(p);
      p = pp;
    end
    prevA(j) = p;
    if p >= 1
      nextA(p) = j;
    end
    q = nextA(j);
    while q <= k && (cand(q) - cand(j)) < distance
      alive(q) = false;
      qq = nextA(q);
      q = qq;
    end
    nextA(j) = q;
    if q <= k
      prevA(q) = j;
    end
    alive(j) = false;           % da xu ly xong, khong xet lai
  end

  idx = cand(keep);
  pks = x(idx);
end
