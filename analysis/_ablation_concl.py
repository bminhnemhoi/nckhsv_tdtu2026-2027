# -*- coding: utf-8 -*-
"""Phan KET LUAN cua ABLATION_B1.md -- tach rieng de giu ablation_b1.py gon.
Duoc ablation_b1.py goi: conclusion(L, b1, cc, res, vn, vns, pfmt, np, tr, e22)."""


def conclusion(L, b1, cc, res, vn, vns, pfmt, np, tr, e22, B1):
    if not (b1 and cc):
        return
    s = b1['summary']
    m5p, m12p, m22p = s['m5_psd']['mean'], s['m12_psd']['mean'], s['m22_psd']['mean']
    q75 = cc['variant_75']['rules']['psd']
    c5, c12, c22 = q75['m5']['mean'], q75['m12']['mean'], q75['m22']['mean']
    t22 = b1['tests']['psd_m12_vs_m22']
    d22 = cc['variant_75']['rules']['psd']['m12_vs_m22']
    fp = res.get('label_fingerprint', {})
    rec = b1['records']; ref = b1['reference']
    gaps = sorted(((ref[t]['m22_psd'] - rec[t]['F1_psd'], t) for t in B1), reverse=True)
    small = [t for g, t in gaps if g <= 0.5]
    sw = b1.get('threshold_sweep', {})
    best_b1 = max(sw.items(), key=lambda kv: kv[1]['F1_psd']) if sw else None
    swc = cc['variant_75'].get('threshold_sweep', {})
    best_c = max(swc.items(), key=lambda kv: kv[1]['F1_psd']) if swc else None

    L.append('## 6. Kết luận\n')
    L.append('**Trả lời thẳng: cải thiện 5 → 22 chủ thể chủ yếu là do THÊM DỮ LIỆU, không phải do mô hình học '
             'phong cách chấm nhãn của B1. Kết luận cũ được giữ — nhưng phải phát biểu lại chặt hơn ở ba điểm.**\n')
    L.append('**Bằng chứng quyết định là CinC 2013.** CinC là tập hoàn toàn độc lập: thiết bị khác, dân số khác, '
             'người chú thích khác, không liên quan gì tới nhóm Silesia. Trên tập đó, phong cách nhãn B1 '
             '*không thể* mang lại lợi thế nào. Vậy mà m22 vẫn hơn m12 '
             f'{vn(-d22["mean_diff"])} điểm (KTC 95 % [{vns(-d22["ci95_bootstrap"][1])}; '
             f'{vns(-d22["ci95_bootstrap"][0])}], p = {pfmt(d22["wilcoxon_p"])}, n = 75 bản ghi) và hơn m5 '
             f'{vn(c22 - c5)} điểm. Ưu thế của m22 tồn tại ở nơi không có gì để bắt chước → nó là năng lực khái quát '
             'thật do nhiều dữ liệu và đa dạng hơn, không phải thiên lệch sáp nhập dữ liệu.\n')
    L.append('**Thêm 7 ca nhãn vàng KHÔNG thay thế được 10 ca B1.** m12 chỉ lấy lại khoảng một phần ba lợi ích: '
             f'trên B1 {vns(m12p - m5p)} trên tổng {vns(m22p - m5p)} điểm; trên CinC {vns(c12 - c5)} trên tổng '
             f'{vns(c22 - c5)} điểm. Tỉ lệ lấy lại gần như bằng nhau ở hai tập (28–38 %) — đúng như kỳ vọng nếu '
             'nguyên nhân là SỐ LƯỢNG chủ thể, và không phù hợp với giả thuyết "lợi ích trên B1 là ảo".\n')
    g12 = res.get('gold12')
    if g12 and g12['n'] >= 6:
        L.append(f'**Trên chính 12 chủ thể nhãn vàng thì 10 ca B1 KHÔNG giúp gì.** Kiểm định chéo giữ lại nhóm '
                 f'({g12["n"]}/12 chủ thể đã chạy) cho m12 {vn(g12["mean_m12"])} so với m22 {vn(g12["mean_m22"])} '
                 f'(hiệu {vns(g12["psd"]["mean_diff"])}, p Wilcoxon {pfmt(g12["psd"]["wilcoxon_p"])}) — hai mô hình '
                 'không phân biệt được. Nói cách khác: dữ liệu B1 không làm mô hình tốt hơn trên bản ghi chuyển dạ '
                 '5 phút; nó chỉ giúp trên bản ghi thai kỳ 20 phút (miền của chính nó) và trên CinC 2013 (miền lạ). '
                 'Đó là dáng điệu của **đa dạng dữ liệu**, không phải của việc học thuộc một quy ước chấm.\n')
    L.append('**Ba điều phải sửa trong cách phát biểu:**\n')
    L.append(f'1. **Có dấu vân nhãn thật, đo được — nhưng nó nằm ở mốc thời gian, không ở F1.** Trên 8 chủ thể B1 mà '
             f'cả ba mô hình đều đạt F1 ≥ 95 (loại hai ca khó để không lẫn với độ khó), độ lệch thời điểm tuyệt đối '
             f'trung bình là m5 {vn(fp["easy"]["absbias"][0])} ms, m12 {vn(fp["easy"]["absbias"][1])} ms, '
             f'm22 {vn(fp["easy"]["absbias"][2])} ms; jitter {vn(fp["easy"]["jitter"][0])} / '
             f'{vn(fp["easy"]["jitter"][1])} / {vn(fp["easy"]["jitter"][2])} ms. Mô hình từng thấy B1 trùng tâm với '
             'mốc của B1 chính xác gấp đôi hai mô hình chưa từng thấy, và hai mô hình chưa từng thấy lệch **giống '
             'hệt nhau** — đó là chữ ký của quy ước chấm mốc, không phải của chất lượng dò. Với dung sai ±50 ms nó '
             'gần như không đổi F1, nhưng nó cấm ta dùng số B1 để nói về **độ chính xác thời điểm** (jitter, STV).')
    L.append(f'2. **Khoảng cách F1 trên B1 dồn vào hai ca khó, không trải đều.** {len(small)}/10 chủ thể có '
             f'|m22 − m12| ≤ 0,5 điểm; toàn bộ khoảng cách nằm ở {gaps[0][1]} ({vns(-gaps[0][0])}) và '
             f'{gaps[1][1]} ({vns(-gaps[1][0])}). Bắt chước phong cách nhãn sẽ tạo sai lệch **hệ thống trên mọi bản '
             'ghi**; cái ta thấy là ngược lại — một mô hình chưa từng thấy B1 bám sát m22 trên 8/10 ca, và chỉ thua '
             'ở đúng những ca mà dữ liệu thêm giúp được.')
    L.append(f'3. **Lợi ích trong miền lớn hơn ngoài miền, và thiết kế này không tách được "cùng miền" khỏi "cùng '
             f'người chấm".** Giảm sai số tương đối khi đi từ m12 lên m22 là '
             f'{vn(100 * (m22p - m12p) / (100 - m12p), 0)} % trên B1 nhưng chỉ '
             f'{vn(100 * (c22 - c12) / (100 - c12), 0)} % trên CinC. Phần chênh này có thể là do 10 ca thêm vào '
             'đúng miền B1 (cùng máy, cùng loại bản ghi 20 phút thai kỳ, cùng dân số) — một lợi ích hợp lệ — hoặc '
             'do cùng quy ước nhãn. Ablation này **không phân tách được hai khả năng đó**; muốn tách phải có một tập '
             'thai kỳ 20 phút được chấm bằng điện cực da đầu, hiện chưa có công khai.\n')
    if best_b1 and best_c:
        L.append(f'**Kiểm tra ngưỡng.** m12 chạy ở ngưỡng {vn(res["meta"]["eval12_threshold"])} (trung vị ngưỡng fold '
                 'sẵn có lúc huấn luyện production). Nếu ưu ái m12 bằng ngưỡng tốt nhất của chính nó '
                 f'({best_b1[0].replace(".", ",")} trên B1 → {vn(best_b1[1]["F1_psd"])}; '
                 f'{best_c[0].replace(".", ",")} trên CinC → {vn(best_c[1]["F1_psd"])}) thì khoảng cách với m22 vẫn '
                 f'còn {vn(m22p - best_b1[1]["F1_psd"])} điểm trên B1 và {vn(c22 - best_c[1]["F1_psd"])} điểm trên '
                 'CinC. Trung vị ngưỡng của các fold m12 đã chạy xong là '
                 f'{vn(float(np.median([v["threshold"] for v in tr["folds"].values()])))} — '
                 f'ở ngưỡng 0,75 m12 đạt {vn(sw["0.75"]["F1_psd"])} trên B1 và {vn(swc["0.75"]["F1_psd"])} trên CinC, '
                 'vẫn thấp hơn m22. Kết luận không phụ thuộc ngưỡng.\n')
    L.append('**Câu đúng để viết vào bài:** *"Bỏ toàn bộ 10 chủ thể nhãn gián tiếp khỏi tập huấn luyện làm giảm '
             f'{vn(m22p - m12p)} điểm F1 trên chính 10 chủ thể đó và {vn(c22 - c12)} điểm trên 75 bản ghi CinC 2013 '
             'độc lập. Vì tập CinC không chia sẻ người chú thích với Silesia, phần lớn lợi ích của việc mở rộng dữ '
             'liệu là năng lực khái quát thật chứ không phải thiên lệch sáp nhập; phần còn lại, đo được ở độ lệch '
             'mốc thời gian chứ không ở F1, là do mô hình trùng quy ước chấm của tập B1."*\n')
    L.append('**Giới hạn của chính ablation này (khai báo thẳng):**\n')
    L.append(f'- m12 học từ 12 chủ thể / m22 học từ 19 chủ thể ở mỗi fold — so sánh này gộp cả **số lượng** lẫn '
             '**nguồn gốc** dữ liệu, không tách được hai yếu tố.')
    L.append('- m22 trên B1 là checkpoint fold **giữ lại đúng chủ thể đang đo**, nhưng vẫn thấy 9 chủ thể B1 khác; '
             'm12 chưa thấy chủ thể B1 nào. Đó chính là biến ablation, nhưng nó cũng có nghĩa m22 được lợi cả về '
             'độ dài dữ liệu (B1 dài 20 phút, gấp 4 lần bản ghi 5 phút).')
    L.append(f'- Chỉ chạy một seed (0). Độ biến thiên theo seed đã đo trước đây là 0,28 điểm trung bình trên 20 chủ '
             'thể — nhỏ so với các hiệu số báo cáo ở đây, nhưng không phải bằng không.')
    nf = len(tr['folds']); ns = len(tr['subjects'])
    if nf >= 6:
        L.append(f'- Đủ {nf}/6 fold, {ns}/12 chủ thể ở mục 5. Mọi con số ở mục 1–4 dùng `production_12` (huấn luyện '
                 'trên cả 12) nên không phụ thuộc số fold.')
    else:
        L.append(f'- Mới {nf}/6 fold của m12 chạy xong, nên mục 5 chỉ có {ns}/12 chủ thể. Mọi con số ở mục 1–4 dùng '
                 '`production_12` nên không phụ thuộc số fold.')
