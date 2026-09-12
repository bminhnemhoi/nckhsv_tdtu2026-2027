# -*- coding: utf-8 -*-
"""Ap cac ban va Octave vao ban sao PowerMF.m trong baselines/octave/.

Chay lai duoc nhieu lan (idempotent): moi ban va kiem tra chuoi dich truoc khi thay.
Ban goc nam o tools/fecg-benchmarking/Code/PowerMF.m (khong sua, khong commit).
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'PowerMF.m')

PATCHES = [
    # (ten, chuoi cu, chuoi moi, bat buoc)
    ('P1 pwelch overlap: Nfft/2 (so mau, MATLAB) -> 0.5 (phan so, Octave)',
     '[Pxx,f] = pwelch(current-mean(current),gausswin(Nfft), Nfft/2, ...\n        Nfft, fs);',
     '[Pxx,f] = pwelch(current-mean(current),gausswin(Nfft), 0.5, ...\n        Nfft, fs);   % OCTAVE-PATCH P1'),

    ('P2a findpeaks tren abs_dev co gia tri am -> dich len khong am',
     "    [~,peaks] = findpeaks(abs_dev(channel,:),'MINPEAKDISTANCE',distance); ",
     "    s_ad = abs_dev(channel,:); s_ad = s_ad - min(s_ad);   % OCTAVE-PATCH P2a\n"
     "    [~,peaks] = findpeaks(s_ad,'MINPEAKDISTANCE',distance); "),

    ('P2b findpeaks tren dau ra matched filter co gia tri am -> dich len khong am',
     "    [~,fPeaks] = findpeaks(r,'MinPeakDistance',distance); % find peaks",
     "    r_shift = r - min(r);                                 % OCTAVE-PATCH P2b\n"
     "    [~,fPeaks] = findpeaks(r_shift,'MinPeakDistance',distance); % find peaks"),

    ('P3 disp voi phep "+" tren chuoi (lop string cua MATLAB) -> printf cua Octave',
     '        disp("channel " + ch + ": " + "freq. " + freq + "/" + freq*60);',
     '        printf("channel %d: freq. %g/%g\\n", ch, freq(1), freq(1)*60);   % OCTAVE-PATCH P3'),

    ('P4 Nfft co the mang kieu uint16 (do nsc=uint16) -> ep ve double',
     '        Nfft = max(256,2^nextpow2(nsc)); ',
     '        Nfft = double(max(256,2^nextpow2(nsc)));   % OCTAVE-PATCH P4\n'),

    # --- P6: loi chan dung that su, tim ra sau khi P1..P5 da chay ---
    # Octave: interpft(x) tra ve MANG PHUC voi phan ao ~1e-16 ngay ca khi x thuc
    #         (da do: iscomplex=1, max|imag|=6.85e-16 tren randn(1000,3)).
    # MATLAB: interpft co dong  "if isreal(x), y = real(y); end"  -> luon thuc.
    # Hau qua: Se phuc -> sig phuc -> template phuc -> r phuc ->
    #          findpeaks cua Octave tra ve 0 dinh (tieu chuan dao ham that bai tren so phuc)
    #          -> PowerMF tra ve rong tren MOI ban ghi.
    # Ban va khoi phuc DUNG ngu nghia MATLAB, khong doi thuat toan.
    ('P6 interpft cua Octave tra ve so phuc -> ep ve thuc (MATLAB tu lam dieu nay)',
     '    [Se,fs]=FecgInterp(Se,fs,4,cName,0);',
     '    [Se,fs]=FecgInterp(Se,fs,4,cName,0);\n'
     '    Se = real(Se);   % OCTAVE-PATCH P6: interpft cua Octave tra ve phuc (~1e-16 ao),\n'
     '                     % MATLAB interpft ep ve thuc khi dau vao thuc. Khong ep -> findpeaks(r)=0 dinh.'),

    ('P5 in them stack khi loi (chi de chan doan, khong doi thuat toan)',
     "    fprintf(1,'There was an error! The message was:\\n%s',e.message);",
     "    fprintf(1,'There was an error! The message was:\\n%s\\n',e.message);\n"
     "    for k=1:numel(e.stack)\n"
     "        fprintf(1,'  at %s line %d\\n', e.stack(k).name, e.stack(k).line);\n"
     "    end"),
]


def main():
    txt = open(SRC, encoding='utf-8', errors='replace').read()
    report = []
    for name, old, new in PATCHES:
        if new.strip() in txt:
            report.append((name, 'DA CO'))
            continue
        if old not in txt:
            report.append((name, 'KHONG TIM THAY CHUOI DICH -- KIEM TRA LAI'))
            continue
        line_no = txt[:txt.index(old)].count('\n') + 1
        txt = txt.replace(old, new, 1)
        report.append((name, 'da ap tai dong %d' % line_no))
    open(SRC, 'w', encoding='utf-8', newline='\n').write(txt)
    for n, s in report:
        print('  %-70s %s' % (n, s))
    bad = [n for n, s in report if 'KHONG' in s]
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
