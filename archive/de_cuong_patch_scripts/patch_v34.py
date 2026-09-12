# -*- coding: utf-8 -*-
"""Vá dây chuyền v3.3 -> v3.4: thay mọi số Power-MF cũ bằng số sau bản vá P7."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TONG = 0


def sua(path, cap):
    global TONG
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in cap:
        if old not in t:
            print('  !! KHONG THAY trong %s: %r' % (path, old[:70]))
            continue
        t = t.replace(old, new)
        n += 1
    io.open(path, 'w', encoding='utf-8').write(t)
    print('%-20s %d cho' % (path, n))
    TONG += n


# ============================================================ sec_7_12.tex
sua('sec_7_12.tex', [
 # 1. bang diem yeu, dong baseline
 (r"""Chưa cài lại baseline nào &
\tot{Đã xử lý} & Ba baseline cổ điển (\S\ref{sec:baselines}) \textbf{và Power-MF chạy lại thật} qua GNU
Octave, chấm bằng cùng bộ chấm (\S\ref{sec:powermf}). Kết quả: hòa \\""",
  r"""Chưa cài lại baseline nào &
\tot{Đã xử lý} & Ba baseline cổ điển (\S\ref{sec:baselines}), Power-MF \textbf{đa kênh} chạy lại qua GNU
Octave, \textbf{và} Power-MF \textbf{đơn kênh} tự cài (\S\ref{sec:powermf}). Không phân biệt được với bản
đa kênh ($-1{,}27$; KTC $[-3{,}08;\ +0{,}27]$), hơn hẳn bản đơn kênh ($+10{,}85$; 22/22) \\"""),

 # 2. them mot dong diem yeu moi
 (r"""Chưa chạy thí nghiệm tinh chỉnh (E7) & Trung bình & Phase P7 \\""",
  r"""Nhóm đoán nguyên nhân trước khi đo, hai lần trong một ngày &
\xau{Mới phát hiện} & Cả hai lần đều đoán sai, và mỗi lần suýt dẫn tới một baseline bị sửa tham số hoặc
một quy tắc chọn kênh khớp vào tập đánh giá. Nguyên tắc mới: không phát biểu nguyên nhân trước khi đo
được nó (\S\ref{sec:doansai}) \\
Chưa chạy thí nghiệm tinh chỉnh (E7) & Trung bình & Phase P7 \\"""),

 # 3. C1 trong "Danh gia thang than ba dong gop"
 (r"""Gia cố mới: Power-MF \textbf{đã được chạy lại thật} và chấm bằng cùng bộ chấm (\S\ref{sec:powermf}) ---
C1 không còn dựa vào con số trích từ y văn. Kết quả của phép đối chuẩn đó là \textbf{hòa}, và nhóm báo
cáo đúng như vậy.""",
  r"""Gia cố mới của bản 3.4: Power-MF \textbf{đã được chạy lại thật} ở \textbf{cả hai cấu hình} --- bốn đạo
trình như bài gốc, và một đạo trình do nhóm tự cài lại --- rồi chấm bằng cùng bộ chấm
(\S\ref{sec:powermf}). C1 không còn dựa vào con số trích từ y văn, và bản chạy lại tái lập số công bố
của tác giả đến \textbf{0,06 điểm}. Kết quả: \textbf{không phân biệt được} với bản đa kênh ($-1{,}27$
điểm; KTC 95\% $[-3{,}08;\ +0{,}27]$; trung vị $+0{,}23$; thắng 18/22), và \textbf{hơn hẳn} bản đơn kênh
($+10{,}85$ điểm; 22/22). \textit{Ranh giới:} trên trung bình toàn tập nhóm vẫn thua 1,27 điểm, và ba
bản ghi thua nặng là ba bản ghi mà \textit{mọi} phương pháp đơn kênh đều hỏng."""),

 # 4. "Vi sao de tai co cua Q1", y 3
 (r"""\item \textbf{Một đối chuẩn công bằng thật} (C1): Power-MF chạy lại trên cùng máy, cùng bộ chấm, và kết
quả \textbf{hòa} được báo cáo đúng như vậy (\S\ref{sec:powermf}). \textit{Ranh giới:} hòa, không thắng.""",
  r"""\item \textbf{Một đối chuẩn công bằng thật, và một câu hỏi đo được} (C1): Power-MF chạy lại trên cùng
máy, cùng bộ chấm, ở \textbf{cả hai cấu hình đạo trình}. Điều đó cho phép nhóm hỏi một câu mà chưa ai
hỏi bằng số trong fECG: \textit{một mạng đơn kênh lấy lại được bao nhiêu phần lợi ích của tách nguồn đa
kênh?} Đáp số: tách nguồn đa kênh đáng 12,12 điểm F1 cho chính Power-MF, mạng đơn kênh lấy lại 10,85
điểm, tức \textbf{89,5\,\%} (\S\ref{sec:luande}). \textit{Ranh giới:} so với Power-MF đa kênh đầy đủ thì
đây là \textbf{hoà}, không phải thắng --- và tỉ số 89,5\,\% chưa có khoảng tin cậy."""),

 # 5. danh sach phase P2
 (r"""\item \textbf{P2} \textbf{xong hoàn toàn} (12/09): ba baseline cổ điển (\S\ref{sec:baselines})
\textbf{và Power-MF chạy lại thật} qua GNU Octave, chấm bằng cùng bộ chấm (\S\ref{sec:powermf}).""",
  r"""\item \textbf{P2} \textbf{xong hoàn toàn} (12/09): ba baseline cổ điển (\S\ref{sec:baselines}),
Power-MF \textbf{4 đạo trình} chạy lại qua GNU Octave sau bảy bản vá, và Power-MF \textbf{1 đạo trình}
tự cài lại bằng Python --- cả ba chấm bằng cùng bộ chấm (\S\ref{sec:powermf})."""),

 # 6. P2 trong bang 12 giai doan
 (r"""P2 & 5--6 & Cài lại bốn baseline cổ điển; đối chiếu với mã mở Power-MF & Baseline chạy được \\""",
  r"""P2 & 5--6 & Cài lại bốn baseline cổ điển; chạy lại mã mở Power-MF ở cả hai cấu hình đạo trình &
Baseline chạy được \\"""),
])


# ============================================================ sec_baselines.tex
sua('sec_baselines.tex', [
 (r"""\begin{ghichu}[title={Power-MF: bản 3.2 nói không chạy lại được --- bản 3.3 đã chạy}]
Bản 3.2 ghi rằng Power-MF cần MATLAB R2021a và các hàm ICA đa kênh của Varanini 2014 không có trong kho
mã công bố, nên không chạy lại được. \textbf{Phát biểu đó đã bị rút.} Power-MF chạy được trên
\textbf{GNU Octave 11.3.0} sau sáu bản vá, và đã được chấm bằng \textbf{chính bộ chấm của nhóm} trên 18
bản ghi chung. Toàn bộ kết quả ở \S\ref{sec:powermf}. Con số 98,0 giờ không còn là con số trích từ y văn
nữa --- nó là con số nhóm tự đo, và nó tái lập được (98,13 trên Silesia B2).
\end{ghichu}""",
  r"""\begin{ghichu}[title={Power-MF: bản 3.2 nói không chạy lại được --- bản 3.4 đã chạy, ở hai cấu hình}]
Bản 3.2 ghi rằng Power-MF cần MATLAB R2021a và các hàm ICA đa kênh của Varanini 2014 không có trong kho
mã công bố, nên không chạy lại được. \textbf{Phát biểu đó đã bị rút.} Power-MF chạy được trên
\textbf{GNU Octave 11.3.0} sau bảy bản vá, và được chấm bằng \textbf{chính bộ chấm của nhóm} trên
\textbf{cả 22 chủ thể}. Con số công bố cho Silesia B1 là 99,46; nhóm chạy lại được \textbf{99,40} ---
lệch 0,06 điểm.

Nhóm cài thêm \textbf{Power-MF-1ch}: cùng thuật toán, cùng front-end và bộ khử mẹ của nhóm, nhưng chỉ
\textbf{một đạo trình}. Đây là đối chứng công bằng nhất trong cả đề cương, vì mọi thứ trừ thuật toán lõi
đều giống hệt nhau. Nó đạt 86,71 --- kém \hethong{} 10,85 điểm, thua 22/22 chủ thể.

\xau{Cảnh báo:} mọi con số Power-MF của bản 3.3 (94,87 / 98,38 / 97,33 / hiệu số $+2{,}74$ và $-1{,}06$)
đứng trên một bản Octave hỏng vì lỗi cổng chuyển của nhóm, và \textbf{đã bị rút toàn bộ}. Xem hộp đầu
\S\ref{sec:powermf}.
\end{ghichu}"""),
])


# ============================================================ sec_4_6.tex
sua('sec_4_6.tex', [
 (r"""\textbf{Cập nhật bản 3.3:} Power-MF \textbf{đã được chạy lại thật} qua GNU Octave và đặt cạnh mô hình của
nhóm trên 18 bản ghi chung với cùng bộ chấm --- xem \S\ref{sec:powermf}. Đoạn ``không đối chiếu trực tiếp
được'' ở trên chỉ còn đúng với \textbf{con số đã công bố}, không còn đúng với thuật toán.""",
  r"""\textbf{Cập nhật bản 3.4:} Power-MF \textbf{đã được chạy lại thật} qua GNU Octave và đặt cạnh mô hình của
nhóm trên \textbf{cả 22 chủ thể} với cùng bộ chấm --- xem \S\ref{sec:powermf}. Hơn nữa, nhóm tự cài lại
Power-MF ở chế độ \textbf{đơn kênh}, để lần đầu có một so sánh trong đó \textit{chỉ} thuật toán lõi khác
nhau. Đoạn ``không đối chiếu trực tiếp được'' ở trên chỉ còn đúng với \textbf{con số đã công bố}, không
còn đúng với thuật toán."""),
])


# ============================================================ sec_1_3.tex
sua('sec_1_3.tex', [
 (r"""\item \textbf{Power-MF:} bản 3.2 ghi ``không chạy lại được''. Sai --- đã chạy qua GNU Octave. Kết quả là
\textbf{hòa}, không phải thắng (\S\ref{sec:powermf}).""",
  r"""\item \textbf{Power-MF:} bản 3.2 ghi ``không chạy lại được''. Sai --- đã chạy qua GNU Octave.
\textbf{Và bản 3.3 cũng sai}: mọi con số Power-MF của nó (94,87 / 98,38) đứng trên một bản Octave hỏng vì
lỗi cổng chuyển của nhóm, đã rút hết. Số đúng: Power-MF đa kênh 98,83, \hethong{} 97,56 --- không phân
biệt được; Power-MF \textbf{cùng một đạo trình} chỉ đạt 86,71 (\S\ref{sec:powermf})."""),

 (r"""(Power-MF, \S\ref{sec:powermf}) thay vì trích con số đã công bố. Không phải ``đối chuẩn đầu tiên'';
kho \texttt{mad-lab-fau/fecg-benchmarking} đã tồn tại.""",
  r"""(Power-MF, \S\ref{sec:powermf}) thay vì trích con số đã công bố --- chạy ở \textbf{cả hai cấu hình đạo
trình}, để đo được tách nguồn đa kênh đáng bao nhiêu điểm F1. Không phải ``đối chuẩn đầu tiên'';
kho \texttt{mad-lab-fau/fecg-benchmarking} đã tồn tại."""),
])

print('TONG CONG: %d cho da sua' % TONG)
