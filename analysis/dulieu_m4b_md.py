# -*- coding: utf-8 -*-
"""Sinh khoi ket qua M4-mini va cam vao analysis/DULIEU.md tai moc <!-- KET_QUA_M4_MINI -->.
Chay lai duoc nhieu lan (thay the khoi cu). Chay: python analysis/dulieu_m4b_md.py"""
import io, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, 'DULIEU.md')
MARK = '<!-- KET_QUA_M4_MINI -->'
END = '<!-- /KET_QUA_M4_MINI -->'


def f(x, n=2):
    return ('%.*f' % (n, x)).replace('.', ',').replace('-', '−')


def fs(x, n=2):
    return ('%+.*f' % (n, x)).replace('.', ',').replace('-', '−')


def block():
    R = json.load(io.open(os.path.join(HERE, 'dulieu_results.json'), encoding='utf-8'))['thuc_nghiem']
    L = []
    A = R['tang_cuong_vs_khong']
    L.append('**Bảng A — tăng cường (`base`) trừ không tăng cường (`noaug`), F1 mức chủ thể, quy tắc PSD.**\n')
    L.append('| fold | chủ thể | base | noaug | hiệu |')
    L.append('|---|---|---|---|---|')
    for r in A['tung_chu_the']:
        L.append('| %d | %s | %s | %s | **%s** |' % (r['fold'], r['chu_the'], f(r['A']), f(r['B']), fs(r['hieu'])))
    L.append('| | **trung bình (n = %d)** | | | **%s** |' % (A['n_chu_the'], fs(A['hieu_trung_binh'])))
    L.append('')
    L.append('Hiệu trung bình **%s** điểm, KTC95 bootstrap [%s; %s], Wilcoxon p = %s, '
             'thắng %d / hoà %d / thua %d.' % (fs(A['hieu_trung_binh']), fs(A['ci95'][0]), fs(A['ci95'][1]),
                                               ('%.3g' % A['wilcoxon_p']).replace('.', ','),
                                               A['thang'], A['hoa'], A['thua']))
    if A['hieu_trung_binh_khong_o_tran'] is not None:
        L.append('Chỉ tính %d chủ thể **không ở trần** (F1 < 99,5 ở cả hai nhánh): hiệu **%s** điểm.'
                 % (A['n_chu_the_khong_o_tran'], fs(A['hieu_trung_binh_khong_o_tran'])))
    L.append('')
    L.append('> **KẾT LUẬN (báo cáo thất bại).** Ở quy mô đã đo, tăng cường dữ liệu hiện tại '
             '**không làm gì cả**: hiệu số trung bình %s điểm, KTC95 ôm sát 0 ở cả hai phía, '
             'thắng %d / hoà %d / thua %d. Bốn trong tám chủ thể cho hiệu số **đúng bằng 0,00** — '
             'tăng cường không đổi được một nhịp nào. Phát biểu đúng là *"không có bằng chứng '
             'tăng cường giúp"*, **không** phải *"tăng cường có hại"*. Điều này khớp với phân tích '
             'ở mục 3.2: hai trong bốn phép (nhiễu Gauss toàn dải, trôi đường nền 0,1–0,5 Hz) được '
             'cộng **sau** bộ lọc 10–60 Hz nên dạy mạng chống một nhiễu không thể tồn tại lúc suy '
             'luận. Nhóm đang trả ~20 %% thời gian huấn luyện cho bốn phép biến đổi không đo được '
             'tác dụng.' % (fs(A['hieu_trung_binh']), A['thang'], A['hoa'], A['thua']))
    L.append('')
    C = R['can_bang_vs_base']
    if 'tung_chu_the' in C:
        L.append('**Bảng B — cân bằng theo số nhịp (`bal`) trừ `base`.**\n')
        L.append('| fold | chủ thể | bal | base | hiệu |')
        L.append('|---|---|---|---|---|')
        for r in C['tung_chu_the']:
            L.append('| %d | %s | %s | %s | **%s** |' % (r['fold'], r['chu_the'], f(r['A']), f(r['B']), fs(r['hieu'])))
        L.append('| | **trung bình (n = %d)** | | | **%s** |' % (C['n_chu_the'], fs(C['hieu_trung_binh'])))
        L.append('')
        L.append('Hiệu trung bình **%s** điểm, KTC95 [%s; %s], Wilcoxon p = %s, thắng %d / hoà %d / thua %d.'
                 % (fs(C['hieu_trung_binh']), fs(C['ci95'][0]), fs(C['ci95'][1]),
                    ('%.3g' % C['wilcoxon_p']).replace('.', ','), C['thang'], C['hoa'], C['thua']))
        L.append('')
        L.append('> **KẾT LUẬN — đây là kết quả đáng theo đuổi nhất của mục này.** Cân bằng nguồn '
                 '**thắng %d, hoà %d, KHÔNG thua trận nào**, và khoảng tin cậy **không chứa 0**. '
                 'Hiệu ứng tập trung đúng chỗ cần: ba chủ thể khó nhất của dự án đều được lợi nhiều '
                 'nhất (B2_03 **+1,97** — bản ghi duy nhất bị giới hạn thật của bộ dò; B1_06 +1,22; '
                 'B1_07 +0,90), còn ba chủ thể đã ở trần thì đứng yên. Wilcoxon p = %s chỉ vì n quá '
                 'nhỏ: với 4 cặp khác 0, giá trị p nhỏ nhất có thể đạt được là 0,125 — **kiểm định '
                 'không thể có ý nghĩa ở cỡ mẫu này dù hiệu ứng có thật đến đâu**.'
                 % (C['thang'], C['hoa'], ('%.3g' % C['wilcoxon_p']).replace('.', ',')))
    L.append('>')
    L.append('> **CHƯA phải bằng chứng, vì hai lý do phải nói rõ.** (1) Ba fold này được chọn '
                 '**có chủ đích vì chúng chứa các bản ghi khó** — mẫu không đại diện, và hiệu ứng đo '
                 'được ở đây là cận trên lạc quan. (2) n = %d với 2 cặp hoà; KTC95 bootstrap trên 4 giá '
                 'trị khác 0 rất mỏng. **Khuyến nghị: chạy cân bằng đủ 11 fold ở quy mô sản xuất** '
                 '(~2,5 giờ/nhánh) — đây là thí nghiệm tiếp theo đáng chi ngân sách nhất trong nhiệm '
                 'vụ M4. Và dùng **trọng số mất mát** thay vì lấy mẫu lặp (mục 4.2), vì lấy mẫu lặp '
                 'khiến 5 chủ thể PhysioNet bị lặp ~2,3 lần/epoch.' % C['n_chu_the'])
    L.append('')
    L.append('*Nguồn: `analysis/dulieu_exp.json` (từng lần chạy), `analysis/dulieu_results.json → thuc_nghiem` '
             '(tổng hợp), `analysis/dulieu_exp_log.txt` (nhật ký). Tổng hợp bởi `analysis/dulieu_m4b.py`.*')
    return '\n'.join(L)


def main():
    s = io.open(MD, encoding='utf-8').read()
    i = s.index(MARK)
    j = s.index(END) + len(END) if END in s else i + len(MARK)
    s = s[:i] + MARK + '\n\n' + block() + '\n\n' + END + s[j:]
    io.open(MD, 'w', encoding='utf-8').write(s)
    print('-> ' + MD)


if __name__ == '__main__':
    main()
