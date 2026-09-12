# -*- coding: utf-8 -*-
"""Chèn mục con mới: 'Nhóm đã đoán sai nguyên nhân hai lần trong một ngày'."""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MUC = r"""\subsection{Nhóm đã đoán sai nguyên nhân hai lần trong một ngày}
\label{sec:doansai}

Mục này nhóm đưa vào không phải để tự trách. Nó ở đây vì nó là bằng chứng kiểm tra được rằng những con
số còn lại trong đề cương đã đi qua một quy trình biết tự bắt lỗi. Một đề cương không có mục này thì
người đọc chỉ có thể \textit{tin}; có mục này thì người đọc \textit{kiểm tra} được.

Ngày 12/09/2026, trong khoảng mười hai tiếng, nhóm phát biểu hai nguyên nhân trước khi đo được chúng.
Cả hai lần đều sai, và cả hai lần cái sai đều đi theo hướng \textbf{có lợi cho câu chuyện nhóm muốn kể}.
Đó là điều đáng lo nhất.

\subsubsection{Lần một --- ``Power-MF hỏng vì tham số 340\,ms quá sát''}

\textbf{Quan sát:} Power-MF chạy lại hỏng trên 6 trên 10 bản ghi Silesia B1. Hai bản cho
Se $\approx 50$\,\% với PPV $\approx 99{,}7$\,\%; bốn bản trả về rỗng.

\textbf{Nhóm đoán:} \texttt{ms\_minpeakdistance} $= 340$\,ms quá sát khoảng RR của thai 155 nhịp/phút,
nên bộ dò bỏ mất một nhịp trên hai. Giả thuyết này \textit{nghe rất đúng}: chữ ký Se $\approx 50$\,\%
với PPV gần 100\,\% đúng là chữ ký kinh điển của bắt cách nhịp, và nhịp tim thai thì thật sự nhanh.

\textbf{Đo thật:} nhóm đo phân bố RR từ nhãn tham chiếu của từng bản ghi
(\texttt{baselines/powermf\_rr\_diag.json}). Trên B1\_01, tỉ lệ khoảng RR ngắn hơn 340\,ms là
\xau{0,00\,\%}. Trên cả 27 bản ghi đã kiểm tra, giá trị lớn nhất là 0,15\,\%. Ràng buộc 340\,ms chưa
từng chặn một nhịp thật nào. \textbf{Giả thuyết sai.}

\textbf{Nguyên nhân thật:} \texttt{findpeaks} của gói \texttt{signal} trong Octave cài
\texttt{MinPeakDistance} bằng một ma trận khoảng cách đôi một, $O(k^2)$ bộ nhớ, và tràn trên bản ghi
2.395.600 mẫu. Lỗi bị \texttt{try/catch} nội bộ nuốt. MATLAB dùng thuật toán tham $O(k \log k)$ nên
không bao giờ gặp. Se $\approx 50$\,\% không phải bắt cách nhịp --- đó là \textbf{mất đúng nửa sau của
bản ghi} (\S\ref{sec:powermf}).

\textbf{Nếu nhóm không đo:} nhóm sẽ tăng tham số cho Power-MF chạy được. Power-MF khi đó đạt khoảng 94,87
và mô hình của nhóm ``thắng'' $+2{,}74$ điểm. Một kết quả đẹp, đăng được, và \textbf{sai hoàn toàn}:
baseline đã bị nhóm sửa tham số nên không còn đối chiếu được với bài gốc. Sau khi vá đúng, Power-MF đạt
98,83 và nhóm \textit{thua} 1,27 điểm.

\subsubsection{Lần hai --- ``quy tắc kênh 0 cố định tốt hơn quy tắc PSD''}

\textbf{Quan sát:} trên mẫu 10 bản ghi CinC 2013, quy tắc chọn kênh theo mật độ phổ công suất chỉ cho
69,31, trong khi lấy cố định kênh 0 cho \textbf{90,34}.

\textbf{Nhóm đoán:} quy tắc PSD không hợp với hệ ghi CinC, và kênh 0 của tập này tình cờ là kênh tốt.
Bản 3.2 đưa 90,34 lên làm con số chính.

\textbf{Đo thật:} chạy \textbf{toàn bộ 75 bản ghi} set-a (\texttt{benchmark\_dpss/eval\_cinc75.json}).
Quy tắc kênh 0 rơi xuống \xau{69,33}, trong khi quy tắc PSD mù nhãn đạt \tot{79,40}. Kênh 0 hoá ra là
quy tắc \textbf{tệ nhất trong bốn quy tắc}, kém quy tắc PSD hơn 10 điểm. \textbf{Giả thuyết sai.}

\begin{table}[H]\centering\small
\caption{Bốn quy tắc chọn kênh, mô hình 22 ca, trên mẫu 10 bản ghi so với toàn bộ 75 bản ghi.
Nguồn: \texttt{benchmark\_dpss/eval\_cinc75.json}.}
\label{tab:doansai_kenh}
\begin{tabular}{@{}L{5.0cm} C{3.0cm} C{3.0cm} C{2.6cm}@{}}
\toprule
\textbf{Quy tắc chọn kênh} & \textbf{Mẫu 10 bản ghi} & \textbf{Toàn bộ 75 bản ghi} & \textbf{Lệch} \\
\midrule
PSD mù nhãn (\textbf{số chính}) & 69,31 & \tot{79,40} & $-10{,}09$ \\
Kênh 0 cố định (hậu kiểm) & \xau{90,34} & \xau{69,33} & $+21{,}01$ \\
Trung bình 4 kênh & --- & 74,09 & --- \\
Oracle (kênh tốt nhất, không dùng được) & --- & 86,87 & --- \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Nguyên nhân thật:} ``kênh 0'' được chọn \textit{sau khi} nhóm nhìn thấy quy tắc PSD thất bại
trên đúng 10 bản ghi đó. Đó là một siêu tham số đã khớp vào chính tập đánh giá. Đem ra 65 bản ghi chưa
thấy, nó rơi 21 điểm.

\textbf{Nếu nhóm không đo:} 90,34 sẽ đứng trong bài báo, kèm kết luận ``không còn bản ghi nào dưới 50''.
Trên 75 bản ghi, vẫn còn \textbf{16 bản dưới 50}. Đó sẽ là một tuyên bố sai về chính điểm yếu lớn nhất
của đề tài.

\begin{ghichu}[title={Điểm chung của hai lần đoán sai --- và nguyên tắc nhóm rút ra}]
Cả hai lần, giả thuyết sai đều \textbf{nghe hợp lý}, \textbf{khớp với dữ liệu nhóm đang nhìn}, và
\textbf{có lợi cho nhóm}. Lần một cho nhóm một chiến thắng $+2{,}74$ điểm; lần hai cho nhóm một con số
90,34 đẹp hơn 79,40. Không lần nào nhóm cố ý gian lận --- và đó chính là lý do nó nguy hiểm.

Điểm chung thứ hai: cả hai lần, dữ liệu để bác bỏ đều \textbf{đã nằm sẵn trên đĩa}. RR thật nằm trong
nhãn tham chiếu; 65 bản ghi CinC còn lại nằm trong cùng thư mục. Nhóm không cần thêm dữ liệu, chỉ cần
chịu đo.

\textbf{Ba nguyên tắc nhóm áp dụng từ đây:}
\begin{enumerate}[leftmargin=1.6em,itemsep=3pt]
\item \textbf{Không phát biểu nguyên nhân trước khi đo được nguyên nhân.} Một bản ghi hỏng thì đọc
\textit{log} của chính nó, không suy diễn từ tham số.
\item \textbf{Nghi ngờ mạnh nhất với giả thuyết có lợi cho mình.} Nếu một cách giải thích làm con số của
nhóm đẹp lên, đó là giả thuyết phải đo trước, không phải giả thuyết được tin trước.
\item \textbf{Không bao giờ chốt số trên tập con của một tập có sẵn đầy đủ.} Nếu có 75 bản ghi thì chạy
75. Mẫu 10 bản ghi đã lệch, và lệch theo \textit{hai hướng ngược nhau} tuỳ quy tắc.
\end{enumerate}
\end{ghichu}

Nhóm giữ mục này trong bản nộp hội đồng. Lý do thẳng thắn: một phản biện Q1 sẽ tìm đúng loại lỗi này, và
tốt hơn là họ thấy nhóm đã tự tìm ra, tự đo, và tự rút --- kèm con số đúng và mã chạy lại được --- thay
vì họ tự phát hiện. Mục này làm đề cương \textbf{đáng tin hơn}, không làm nó yếu đi. Nó cũng là lý do
nhóm dám để nguyên ba bản ghi thua nặng trong \S\ref{sec:powermf} thay vì loại chúng ra.

"""

p = 'sec_7_12.tex'
t = io.open(p, encoding='utf-8').read()
anchor = r'\subsection{Kiến trúc nhóm đã cân nhắc và loại}'
assert anchor in t
assert r'\label{sec:doansai}' not in t
t = t.replace(anchor, MUC + anchor, 1)
io.open(p, 'w', encoding='utf-8').write(t)
print('da chen muc sec:doansai vao sec_7_12.tex')
