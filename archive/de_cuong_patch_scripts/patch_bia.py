# -*- coding: utf-8 -*-
"""Trang bìa v3.3 -> v3.4 và hộp 'các phát biểu bị rút'."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = 'de_cuong.tex'
t = io.open(p, encoding='utf-8').read()
n = 0

cap = [
 (r"""\date{09/09/2026}""", r"""\date{12/09/2026}"""),
 (r"""\textbf{Phiên bản}         & 3.3 --- 12/09/2026 \\[3pt]""",
  r"""\textbf{Phiên bản}         & 3.4 --- 12/09/2026 \\[3pt]"""),
 (r"""\smallskip
\textbf{Bản 3.3 rút lại bốn phát biểu của bản 3.2} và ghi rõ con số đúng: (i) con số CinC 2013 đo trên
\textbf{toàn bộ 75 bản ghi} chứ không phải mẫu 10 bản ghi (\S\ref{sec:cinc75}); (ii) Power-MF
\textbf{đã chạy lại được} và kết quả là \textbf{hòa}, không phải ``không đối chiếu được''
(\S\ref{sec:powermf}); (iii) mọi trị số $p$ trên 5 sản phụ là giả lập và đã bị gỡ, tuyên bố ``8 kiến trúc
không phân biệt được'' đổi thành ``không đủ lực để phân biệt'' (\S\ref{sec:thongke}); (iv) hệ thống
\textbf{chưa} dùng được làm máy đo biến thiên ngắn hạn (\S\ref{sec:clinical}).""",
  r"""\smallskip
\textbf{Năm phát biểu đã bị rút công khai.} Bốn của bản 3.2: (i) con số CinC 2013 đo trên \textbf{mẫu 10
bản ghi} của một tập có 75 --- số đúng là 79,40 trên toàn bộ 75 (\S\ref{sec:cinc75}); (ii) ``Power-MF
không chạy lại được'' --- sai, đã chạy (\S\ref{sec:powermf}); (iii) mọi trị số $p$ trên 5 sản phụ là giả
lập và đã bị gỡ, ``8 kiến trúc không phân biệt được'' đổi thành ``không đủ lực để phân biệt''
(\S\ref{sec:thongke}); (iv) hệ thống \textbf{chưa} dùng được làm máy đo biến thiên ngắn hạn
(\S\ref{sec:clinical}).

\smallskip
\textbf{Và một của chính bản 3.3, rút chiều 12/09:} con số Power-MF 94,87 cùng kết luận ``loại hai bản
ghi bắt cách nhịp thì còn 98,38 so với 97,33'' \textbf{đều sai}. Cả hai đứng trên một bản Octave hỏng vì
\textit{lỗi cổng chuyển của chính nhóm} ($\texttt{findpeaks}$ tốn $O(k^2)$ bộ nhớ), không phải vì tham số
340\,ms như nhóm đã đoán --- giả thuyết đó bị bác bỏ bằng số đo: 0,00\,\% khoảng RR dưới 340\,ms. Sau khi
vá, Power-MF đa kênh đạt \textbf{98,83} và tái lập số công bố của tác giả đến 0,06 điểm
(\S\ref{sec:powermf}). Hai lần đoán sai nguyên nhân trong cùng một ngày được phân tích ở
\S\ref{sec:doansai}."""),
]

for old, new in cap:
    if old not in t:
        print('  !! KHONG THAY:', old[:60]); continue
    t = t.replace(old, new); n += 1

io.open(p, 'w', encoding='utf-8').write(t)
print('de_cuong.tex: %d cho' % n)
