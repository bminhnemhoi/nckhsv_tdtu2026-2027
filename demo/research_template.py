# -*- coding: utf-8 -*-
"""
research_template.py -- Template HTML5/CSS/JS thuần cho Trang Chủ Nghiên Cứu RelyFetal (/)
Tái tạo chính xác 100% giao diện và nội dung nguyên bản (Gradio Soft theme),
nhưng chạy thuần FastAPI + Vanilla JS + Plotly.js mà KHÔNG dùng thư viện Gradio.
"""

RESEARCH_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RelyFetal — demo dò nhịp tim thai đơn kênh</title>
  
  <!-- Font Source Sans 3 chuẩn y tế -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  
  <!-- Plotly.js CDN chính thức -->
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

  <style>
    /* =========================================================================
       1. CSS GỐC NGUYÊN BẢN CỦA TÁC GIẢ ĐỀ TÀI (demo/app.py)
       ========================================================================= */
    :root {
      --font-main: 'Source Sans 3', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --primary-color: #f97316; /* Màu cam Gradio đặc trưng */
      --primary-hover: #ea580c;
      --border-color: #e5e7eb;
      --bg-page: #f9fafb;
      --bg-card: #ffffff;
      --text-main: #111827;
      --text-sub: #4b5563;
      --text-muted: #6b7280;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-main);
      background-color: var(--bg-page);
      color: var(--text-main);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      padding: 16px 20px 40px;
    }

    .app-container {
      max-width: 1280px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* Tiêu đề gốc của đề tài */
    .rf-title h1 {
      margin: 0 0 4px;
      font-size: 26px;
      font-weight: 800;
      color: #111827;
      letter-spacing: -0.01em;
    }
    .rf-title p {
      margin: 0;
      color: #6b7280;
      font-size: 14px;
      line-height: 1.5;
    }

    /* Thanh điều khiển trên cùng */
    .controls-wrapper {
      background: var(--bg-card);
      border: 1.5px solid var(--border-color);
      border-radius: 12px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }

    .controls-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: flex-end;
    }

    .ctrl-col {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .ctrl-label {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-sub);
    }

    /* Radio Group */
    .radio-group {
      display: flex;
      align-items: center;
      gap: 6px;
      background: #f3f4f6;
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }
    .radio-btn {
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      color: var(--text-sub);
      transition: all 0.15s ease;
      user-select: none;
    }
    .radio-btn.active {
      background: #ffffff;
      color: #111827;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
      font-weight: 700;
    }

    /* Dropdown selects */
    .form-select, .form-input {
      font-family: var(--font-main);
      font-size: 13.5px;
      padding: 7px 12px;
      border-radius: 8px;
      border: 1px solid #d1d5db;
      background-color: #ffffff;
      color: #111827;
      outline: none;
      transition: border-color 0.15s ease;
      min-height: 38px;
    }
    .form-select:focus, .form-input:focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.15);
    }

    /* Nút bấm Phân tích chính */
    .btn-analyze {
      background: linear-gradient(to bottom right, #f97316, #ea580c);
      color: #ffffff;
      font-family: var(--font-main);
      font-size: 14px;
      font-weight: 700;
      padding: 8px 22px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      box-shadow: 0 2px 4px rgba(234, 88, 12, 0.25);
      transition: all 0.15s ease;
    }
    .btn-analyze:hover {
      background: linear-gradient(to bottom right, #ea580c, #c2410c);
      box-shadow: 0 3px 6px rgba(234, 88, 12, 0.35);
    }
    .btn-analyze:active {
      transform: translateY(1px);
    }

    .btn-monitor-nav {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #1d4ed8;
      font-size: 12.5px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 6px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
    }
    .btn-monitor-nav:hover {
      background: #dbeafe;
      color: #1e40af;
    }

    /* Dòng trạng thái Markdown gốc */
    .rf-status {
      font-size: 13.5px;
      color: #374151;
      padding: 2px 0;
      line-height: 1.5;
    }

    /* =========================================================================
       4 THẺ HUD METRICS GỐC (.rf-cards, .rf-card)
       ========================================================================= */
    .rf-cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 4px 0 2px;
    }
    @media (max-width: 900px) {
      .rf-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    .rf-card {
      border: 1.5px solid #e5e7eb;
      border-radius: 12px;
      padding: 12px 14px;
      background: #ffffff;
      min-height: 110px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .rf-k {
      font-size: 12px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #6b7280;
      font-weight: 600;
    }
    .rf-v {
      font-size: 30px;
      font-weight: 700;
      line-height: 1.25;
      margin: 4px 0 2px;
      color: #111827;
      font-variant-numeric: tabular-nums;
    }
    .rf-u {
      font-size: 15px;
      font-weight: 500;
      color: #6b7280;
    }
    .rf-s {
      font-size: 12px;
      color: #6b7280;
      line-height: 1.4;
    }
    .rf-r {
      margin: 8px 0 0;
      padding-left: 18px;
      font-size: 12.5px;
      color: #374151;
      line-height: 1.45;
    }
    .rf-note {
      margin-top: 8px;
      font-size: 11.5px;
      color: #92400e;
      background: #fffbeb;
      border: 1px solid #fcd34d;
      border-radius: 8px;
      padding: 6px 8px;
      line-height: 1.4;
    }
    .rf-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin: 6px 0 4px;
    }
    .rf-chip {
      font-size: 11.5px;
      border: 1px solid #d1d5db;
      border-radius: 999px;
      padding: 2px 8px;
      color: #374151;
      background: #f9fafb;
      font-weight: 500;
    }
    .rf-chip-sel {
      border-color: #2563eb;
      background: #dbeafe;
      color: #1e3a8a;
      font-weight: 700;
    }
    .rf-conf .rf-v {
      font-size: 22px;
    }

    /* =========================================================================
       THANH TAB GRADIO SOFT
       ========================================================================= */
    .tab-nav-container {
      display: flex;
      flex-wrap: wrap;
      border-bottom: 2px solid #e5e7eb;
      gap: 2px;
      margin-top: 6px;
    }
    .tab-nav-btn {
      background: transparent;
      border: none;
      font-family: var(--font-main);
      font-size: 13.5px;
      font-weight: 600;
      color: #6b7280;
      padding: 8px 14px;
      cursor: pointer;
      border-radius: 8px 8px 0 0;
      transition: all 0.15s ease;
      position: relative;
      bottom: -2px;
    }
    .tab-nav-btn:hover {
      color: #111827;
      background: #f3f4f6;
    }
    .tab-nav-btn.active {
      color: #ea580c;
      font-weight: 700;
      background: #ffffff;
      border: 1.5px solid #e5e7eb;
      border-bottom-color: #ffffff;
      box-shadow: 0 -2px 4px rgba(0,0,0,0.02);
    }

    /* Tab Content Box */
    .tab-pane {
      display: none;
      background: #ffffff;
      border: 1.5px solid #e5e7eb;
      border-top: none;
      border-radius: 0 0 12px 12px;
      padding: 18px 20px;
      min-height: 520px;
    }
    .tab-pane.active {
      display: block;
    }

    /* Plotly container */
    .plot-container {
      width: 100%;
      min-height: 420px;
    }

    /* Markdown Styling trong Tab */
    .md-content {
      font-size: 14px;
      line-height: 1.6;
      color: #374151;
    }
    .md-content h3 {
      font-size: 18px;
      font-weight: 800;
      color: #111827;
      margin: 16px 0 8px;
    }
    .md-content h4 {
      font-size: 15px;
      font-weight: 700;
      color: #1f2937;
      margin: 12px 0 6px;
    }
    .md-content table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 18px;
      font-size: 13px;
    }
    .md-content th, .md-content td {
      border: 1px solid #e5e7eb;
      padding: 8px 12px;
      text-align: left;
    }
    .md-content th {
      background-color: #f9fafb;
      font-weight: 700;
      color: #111827;
    }
    .md-content tr:nth-child(even) td {
      background-color: #fdfdfd;
    }
    .md-content code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 12px;
      color: #c026d3;
    }
    .md-content pre {
      background: #1e293b;
      color: #f8fafc;
      padding: 12px 16px;
      border-radius: 8px;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 12.5px;
      margin: 10px 0;
    }
    .md-content blockquote {
      border-left: 4px solid #f59e0b;
      background: #fffbeb;
      padding: 8px 12px;
      border-radius: 0 8px 8px 0;
      margin: 10px 0;
      color: #92400e;
    }

    /* Cảnh báo gốc của đề tài */
    .rf-warn {
      border: 1.5px solid #fcd34d;
      background: #fffbeb;
      color: #78350f;
      border-radius: 10px;
      padding: 10px 12px;
      margin: 8px 0;
      font-size: 13.5px;
      line-height: 1.55;
    }
    .rf-warn-red {
      border-color: #fca5a5;
      background: #fef2f2;
      color: #7f1d1d;
    }
    .rf-warn code {
      background: #fff;
      padding: 1px 4px;
      border-radius: 4px;
    }

    /* Footer gốc */
    .rf-foot {
      border-top: 1px solid #e5e7eb;
      margin-top: 14px;
      padding: 12px 4px;
      font-weight: 700;
      color: #991b1b;
      text-align: center;
      font-size: 13.5px;
    }

    /* JSON Box */
    .json-pre-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px;
      font-family: var(--font-mono);
      font-size: 12px;
      color: #0f172a;
      max-height: 520px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    /* Loading spinner */
    .loading-spinner {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>

  <div class="app-container">

    <!-- Header Tiêu đề gốc -->
    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
      <div class="rf-title">
        <h1>RelyFetal — dò phức bộ QRS thai nhi từ điện tim ổ bụng <em>đơn kênh</em>, có cổng từ chối</h1>
        <p>FetalQRS-TCN (113 481 tham số, CPU, huấn luyện 22 chủ thể) · khử QRS mẹ bằng mẫu trung vị · chọn kênh mù nhãn <b>peakprob</b> (mặc định, hậu kiểm) hoặc PSD · đèn tin cậy theo đoạn 4 s. <b style="color:#991b1b">Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.</b></p>
      </div>
      <div>
        <a href="/monitor" class="btn-monitor-nav" title="Mở trang giám sát thời gian thực">
          🏥 Live Monitor ↗
        </a>
      </div>
    </div>

    <!-- Thanh Điều Khiển Controls Row Y chang Gradio -->
    <div class="controls-wrapper">
      <div class="controls-row">
        
        <!-- 1. Nguồn dữ liệu -->
        <div class="ctrl-col" style="flex: 1; min-width: 180px;">
          <label class="ctrl-label">Nguồn dữ liệu</label>
          <div class="radio-group" id="sourceRadioGroup">
            <div class="radio-btn active" data-src="showcase" onclick="setSource('showcase')">Minh hoạ (5 bản)</div>
            <div class="radio-btn" data-src="sample" onclick="setSource('sample')">Bản ghi mẫu</div>
            <div class="radio-btn" data-src="upload" onclick="setSource('upload')">Tải lên file</div>
          </div>
        </div>

        <!-- 2. Dropdown Bản ghi -->
        <div class="ctrl-col" id="recSelectCol" style="flex: 4; min-width: 260px;">
          <label class="ctrl-label" id="recSelectLabel">Bản ghi minh hoạ cho buổi demo (thứ tự gợi ý: từ trên xuống)</label>
          <select class="form-select" id="recSelect" style="width: 100%;">
            <!-- Render động bằng JS -->
          </select>
        </div>

        <!-- 2b. Form Upload file (hiện khi chọn Tải lên) -->
        <div class="ctrl-col" id="uploadCol" style="flex: 4; min-width: 260px; display: none;">
          <label class="ctrl-label">Tải lên: .edf · .hea+.dat(+.fqrs) · .csv · .npy · .txt</label>
          <input type="file" id="fileUploadInput" class="form-input" multiple />
        </div>

        <div class="ctrl-col" id="fsCol" style="flex: 1; min-width: 100px; display: none;">
          <label class="ctrl-label">fs (Hz)</label>
          <input type="number" id="fsInput" class="form-input" value="1000" />
        </div>

        <!-- 3. Kênh bụng -->
        <div class="ctrl-col" style="flex: 2; min-width: 160px;">
          <label class="ctrl-label">Kênh bụng</label>
          <select class="form-select" id="leadSelect">
            <option value="peakprob" selected>Tự động — peakprob (mặc định)</option>
            <option value="psd">Tự động — PSD (Power-MF)</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
          </select>
        </div>

        <!-- 4. Đèn tin cậy -->
        <div class="ctrl-col" style="flex: 2; min-width: 160px;">
          <label class="ctrl-label">Đèn tin cậy</label>
          <select class="form-select" id="confSelect">
            <option value="hoc" selected>Học (GBM, 12 chỉ số / đoạn 4 s)</option>
            <option value="luat">Luật cứng (4 thành phần)</option>
          </select>
        </div>

        <!-- 5. Nút Phân tích -->
        <div class="ctrl-col" style="flex: 0 0 auto;">
          <button class="btn-analyze" id="btnRun" onclick="runAnalysis()">
            <span id="btnSpinner" style="display: none;" class="loading-spinner"></span>
            <span id="btnLabel">Phân tích</span>
          </button>
        </div>

      </div>
    </div>

    <!-- Dòng Trạng Thái status -->
    <div class="rf-status" id="statusLine">
      Chọn bản ghi rồi bấm <b>Phân tích</b>.
    </div>

    <!-- 4 Thẻ HUD Cards (Render đúng HTML từ cards_html) -->
    <div id="cardsContainer">
      <!-- Sinh động từ backend -->
    </div>

    <!-- Thanh Tabs Y chang Gradio -->
    <div class="tab-nav-container">
      <button class="tab-nav-btn active" onclick="openTab('tabSig', this)">📊 Tín hiệu (5 tầng)</button>
      <button class="tab-nav-btn" onclick="openTab('tabLeads', this)">🔀 Chọn kênh — cả 4 kênh</button>
      <button class="tab-nav-btn" onclick="openTab('tabFhr', this)">📈 Nhịp tim thai + đèn đoạn</button>
      <button class="tab-nav-btn" onclick="openTab('tabCmp', this)">🎯 So sánh với nhãn</button>
      <button class="tab-nav-btn" onclick="openTab('tabSummary', this)">📑 Kết quả tổng hợp (60 bản sạch)</button>
      <button class="tab-nav-btn" onclick="openTab('tabDataset', this)">🗂 Dữ liệu của nhóm</button>
      <button class="tab-nav-btn" onclick="openTab('tabUpload', this)">📤 Tải dữ liệu mới</button>
      <button class="tab-nav-btn" onclick="openTab('tabJson', this)">📋 Nhật ký (JSON)</button>
    </div>

    <!-- NỘI DUNG CÁC TAB -->
    
    <!-- Tab 1: Tín hiệu 5 tầng -->
    <div id="tabSig" class="tab-pane active">
      <div id="plotSig" class="plot-container"></div>
    </div>

    <!-- Tab 2: Chọn kênh -->
    <div id="tabLeads" class="tab-pane">
      <div id="leadsMdBox" class="md-content" style="margin-bottom: 14px;"></div>
      <div id="plotLeads" class="plot-container"></div>
    </div>

    <!-- Tab 3: fHR + đèn đoạn -->
    <div id="tabFhr" class="tab-pane">
      <div id="plotFhr" class="plot-container"></div>
    </div>

    <!-- Tab 4: So sánh với nhãn -->
    <div id="tabCmp" class="tab-pane">
      <div id="cmpMdBox" class="md-content" style="margin-bottom: 14px;"></div>
      <div id="cmpTableBox" class="md-content"></div>
    </div>

    <!-- Tab 5: Kết quả tổng hợp (60 bản sạch) -->
    <div id="tabSummary" class="tab-pane">
      <div id="summaryMdBox" class="md-content"></div>
    </div>

    <!-- Tab 6: Dữ liệu của nhóm -->
    <div id="tabDataset" class="tab-pane">
      <div class="controls-wrapper" style="margin-bottom: 14px;">
        <div class="controls-row">
          <div class="ctrl-col" style="flex: 2;">
            <label class="ctrl-label">Bộ dữ liệu</label>
            <select class="form-select" id="dsSelect" onchange="loadDatasetTable(this.value)">
              <option value="adfecgdb" selected>ADFECGDB (5 bản)</option>
              <option value="silesia_b1">Silesia B1 (10 bản)</option>
              <option value="silesia_b2">Silesia B2 (12 bản)</option>
              <option value="cinc_sach">CinC 2013 set-a sạch (60 bản)</option>
              <option value="cinc_nhiem">CinC 2013 set-a nhiễm (15 bản)</option>
            </select>
          </div>
          <div class="ctrl-col" style="flex: 2;">
            <label class="ctrl-label">Chọn bản ghi để xem 10s thô</label>
            <select class="form-select" id="dsRecSelect"></select>
          </div>
          <div class="ctrl-col" style="flex: 0 0 auto;">
            <button class="btn-analyze" style="background:#2563eb;" onclick="loadDatasetRawPlot()">
              Xem tín hiệu thô
            </button>
          </div>
        </div>
      </div>
      <div id="dsTableBox" class="md-content"></div>
      <div id="plotDsRaw" class="plot-container" style="display: none; margin-top: 16px;"></div>
      <div id="dsCapBox" class="md-content" style="margin-top: 8px;"></div>
    </div>

    <!-- Tab 7: Tải dữ liệu mới -->
    <div id="tabUpload" class="tab-pane">
      <div class="md-content">
        <h3>Thử mô hình trên dữ liệu <b>chưa có trong đề tài</b></h3>
        <p>Chọn các định dạng chấp nhận (.edf, WFDB .dat/.hea, .csv, .npy) ở khung Tải lên trên thanh điều khiển.</p>
        <div class="rf-warn"><b>Không có nhãn tham chiếu</b> → chỉ xem được <b>vị trí nhịp</b> và <b>điểm tin cậy</b>. <b>KHÔNG tính được F1 / Se / PPV.</b></div>
        <div class="rf-warn rf-warn-red"><b>Cảnh báo về miền dữ liệu:</b> Mô hình được huấn luyện trên <b>22 sản phụ</b> (ADFECGDB + Silesia). Trên thiết bị khác hoặc dân số khác, đèn tin cậy là thứ cần nhìn đầu tiên.</div>
      </div>
    </div>

    <!-- Tab 8: Nhật ký JSON -->
    <div id="tabJson" class="tab-pane">
      <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
        <button class="btn-analyze" style="background: #4b5563; font-size: 12px; padding: 4px 12px; min-height: 28px;" onclick="copyJson()">
          Sao chép JSON
        </button>
      </div>
      <pre class="json-pre-box" id="jsonBox">{}</pre>
    </div>

    <!-- Footer đỏ nguyên bản -->
    <div class="rf-foot">
      Bản mẫu nghiên cứu. Không phải thiết bị y tế. Không dùng cho chẩn đoán.
    </div>

  </div>

  <!-- JAVASCRIPT ĐIỀU KHIỂN LOGIC (Thuần Vanilla JS, Siêu nhẹ) -->
  <script>
    let currentSource = 'showcase';
    let allSampleRecords = [];

    const SHOWCASE_LIST = [
      { name: 'r01', label: 'r01 — ADFECGDB, dễ — fold 22 ca chưa thấy r01; mọi quy tắc chọn kênh đều cho F1 ≈ 100' },
      { name: 'a09', label: 'a09 — CinC sạch, zero-shot — PSD chọn kênh sai (F1 ≈ 19); peakprob chọn kênh khác (F1 ≈ 94)' },
      { name: 'B2_03', label: 'B2_03 — Silesia chuyển dạ, khó — mô hình thất bại một phần; cổng tin cậy phải báo ĐỎ/VÀNG' },
      { name: 'a02', label: 'a02 — CinC sạch — mô hình bám nhịp MẸ; cổng bám nhịp mẹ phải báo ĐỎ' },
      { name: 'a27', label: 'a27 — CinC sạch, gần như không có tín hiệu thai — hệ thống phải nói tôi không chắc' }
    ];

    function setSource(src) {
      currentSource = src;
      document.querySelectorAll('#sourceRadioGroup .radio-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.src === src);
      });

      const recCol = document.getElementById('recSelectCol');
      const uploadCol = document.getElementById('uploadCol');
      const fsCol = document.getElementById('fsCol');
      const recSelect = document.getElementById('recSelect');
      const recLabel = document.getElementById('recSelectLabel');

      if (src === 'showcase') {
        recCol.style.display = 'flex';
        uploadCol.style.display = 'none';
        fsCol.style.display = 'none';
        recLabel.innerText = 'Bản ghi minh hoạ cho buổi demo (thứ tự gợi ý: từ trên xuống)';
        recSelect.innerHTML = SHOWCASE_LIST.map(r => `<option value="${r.name}">${r.label}</option>`).join('');
      } else if (src === 'sample') {
        recCol.style.display = 'flex';
        uploadCol.style.display = 'none';
        fsCol.style.display = 'none';
        recLabel.innerText = 'Mọi bản ghi mẫu trên đĩa (ADFECGDB · CinC 2013 · Silesia)';
        populateSampleDropdown();
      } else {
        recCol.style.display = 'none';
        uploadCol.style.display = 'flex';
        fsCol.style.display = 'flex';
      }
    }

    async function populateSampleDropdown() {
      const recSelect = document.getElementById('recSelect');
      if (allSampleRecords.length === 0) {
        try {
          const res = await fetch('/api/list_samples');
          const d = await res.json();
          allSampleRecords = d.records || [];
        } catch (e) {
          console.error(e);
        }
      }
      recSelect.innerHTML = allSampleRecords.map(r => `<option value="${r.name}">${r.label}</option>`).join('');
    }

    function openTab(tabId, btn) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-nav-btn').forEach(el => el.classList.remove('active'));

      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');

      // Tự động resize Plotly theo kích thước tab
      if (tabId === 'tabSig') Plotly.Plots.resize('plotSig');
      else if (tabId === 'tabLeads') Plotly.Plots.resize('plotLeads');
      else if (tabId === 'tabFhr') Plotly.Plots.resize('plotFhr');
    }

    async function runAnalysis() {
      const btn = document.getElementById('btnRun');
      const spinner = document.getElementById('btnSpinner');
      const btnLabel = document.getElementById('btnLabel');
      const statusLine = document.getElementById('statusLine');

      const recName = document.getElementById('recSelect').value;
      const leadMode = document.getElementById('leadSelect').value;
      const confMode = document.getElementById('confSelect').value;

      spinner.style.display = 'inline-block';
      btnLabel.innerText = 'Đang chạy...';
      btn.disabled = true;
      statusLine.innerHTML = `Đang phân tích bản ghi <b>${recName}</b>...`;

      try {
        const res = await fetch('/api/run_analysis', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source: currentSource,
            rec_name: recName,
            lead_mode: leadMode,
            conf_mode: confMode
          })
        });

        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();

        // 1. Cập nhật Status
        statusLine.innerHTML = data.status_html || `Đã phân tích <b>${data.record}</b>.`;

        // 2. Cập nhật 4 Cards HTML nguyên bản
        document.getElementById('cardsContainer').innerHTML = data.cards_html || '';

        // 3. Render Plotly Plots (Nền trắng nguyên bản của đề tài)
        if (data.fig_sig) {
          const fig = JSON.parse(data.fig_sig);
          Plotly.newPlot('plotSig', fig.data, fig.layout, { responsive: true, displaylogo: false });
        }
        if (data.fig_leads) {
          const fig = JSON.parse(data.fig_leads);
          Plotly.newPlot('plotLeads', fig.data, fig.layout, { responsive: true, displaylogo: false });
        }
        if (data.fig_fhr) {
          const fig = JSON.parse(data.fig_fhr);
          Plotly.newPlot('plotFhr', fig.data, fig.layout, { responsive: true, displaylogo: false });
        }

        // 4. Markdown Tabs
        document.getElementById('leadsMdBox').innerHTML = data.leads_html || '';
        document.getElementById('cmpMdBox').innerHTML = data.cmp_html || '';
        document.getElementById('cmpTableBox').innerHTML = data.cmp_table_html || '';

        // 5. JSON Box
        document.getElementById('jsonBox').innerText = JSON.stringify(data.summary_json || data, null, 2);

      } catch (err) {
        console.error(err);
        statusLine.innerHTML = `<span style="color:#dc2626">Lỗi phân tích: ${err.message}</span>`;
      } finally {
        spinner.style.display = 'none';
        btnLabel.innerText = 'Phân tích';
        btn.disabled = false;
      }
    }

    function copyJson() {
      const txt = document.getElementById('jsonBox').innerText;
      navigator.clipboard.writeText(txt).then(() => {
        alert('Đã sao chép nhật ký JSON vào bộ nhớ đệm!');
      });
    }

    async function loadSummaryInfo() {
      try {
        const res = await fetch('/api/summary_info');
        const d = await res.json();
        document.getElementById('summaryMdBox').innerHTML = d.html || '';
      } catch (e) {
        console.error(e);
      }
    }

    async function loadDatasetTable(dsName) {
      try {
        const res = await fetch('/api/dataset_table?ds=' + encodeURIComponent(dsName));
        const d = await res.json();
        document.getElementById('dsTableBox').innerHTML = d.table_html || '';
        const picker = document.getElementById('dsRecSelect');
        picker.innerHTML = (d.records || []).map(r => `<option value="${r}">${r}</option>`).join('');
      } catch (e) {
        console.error(e);
      }
    }

    async function loadDatasetRawPlot() {
      const ds = document.getElementById('dsSelect').value;
      const rec = document.getElementById('dsRecSelect').value;
      if (!rec) return;

      try {
        const res = await fetch('/api/dataset_raw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ds, rec })
        });
        const d = await res.json();
        if (d.fig) {
          const plotBox = document.getElementById('plotDsRaw');
          plotBox.style.display = 'block';
          const fig = JSON.parse(d.fig);
          Plotly.newPlot('plotDsRaw', fig.data, fig.layout, { responsive: true, displaylogo: false });
          document.getElementById('dsCapBox').innerHTML = d.cap || '';
        }
      } catch (e) {
        console.error(e);
      }
    }

    // Tự động khởi động khi tải trang
    window.addEventListener('DOMContentLoaded', () => {
      setSource('showcase');
      loadSummaryInfo();
      loadDatasetTable('adfecgdb');
      runAnalysis(); // Tự động chạy bản ghi đầu tiên r01
    });
  </script>
</body>
</html>
"""
