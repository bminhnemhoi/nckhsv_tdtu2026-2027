# -*- coding: utf-8 -*-
"""
HTML/CSS/JS standalone template cho route /monitor (Apple Watch ECG Monitor).
Được nhúng trực tiếp hoặc mở toàn màn hình độc lập, nạp dữ liệu từ /api/monitor_data.
"""

MONITOR_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RelyFetal — Live Clinical ECG Monitor</title>
  <style>
    :root {
      --bg-deep: #000000;
      --bg-card: #0c0d14;
      --border-line: #1c202e;
      --apple-red: #ff3b30;
      --apple-red-dim: rgba(255, 59, 48, 0.22);
      --apple-red-glow: rgba(255, 59, 48, 0.45);
      --apple-green: #30d158;
      --apple-orange: #ff9f0a;
      --apple-cyan: #64d2ff;
      --text-main: #ffffff;
      --text-muted: #8e8e93;
      --text-sub: #a1a1a6;
      --font-ui: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
      --font-mono: "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-deep);
      color: var(--text-main);
      font-family: var(--font-ui);
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    /* Top Bar Header */
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 24px;
      background: #08090f;
      border-bottom: 1px solid var(--border-line);
      flex-wrap: wrap;
      gap: 12px;
    }
    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-pulse-dot {
      width: 10px;
      height: 10px;
      background: var(--apple-red);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--apple-red);
      animation: pulse-red 1.8s infinite ease-in-out;
    }
    @keyframes pulse-red {
      0% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 6px var(--apple-red); }
      50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 14px var(--apple-red); }
      100% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 6px var(--apple-red); }
    }
    .brand-title {
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.3px;
      color: #fff;
    }
    .brand-tag {
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--apple-red-dim);
      color: var(--apple-red);
      border: 1px solid rgba(255, 59, 48, 0.4);
    }
    .header-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 12px;
    }
    .live-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: rgba(48, 209, 88, 0.12);
      border: 1px solid rgba(48, 209, 88, 0.35);
      border-radius: 20px;
      color: var(--apple-green);
      font-weight: 700;
    }
    .live-dot {
      width: 7px;
      height: 7px;
      background: var(--apple-green);
      border-radius: 50%;
      box-shadow: 0 0 6px var(--apple-green);
    }
    .clock-tag {
      font-family: var(--font-mono);
      color: var(--text-sub);
      background: #12141e;
      border: 1px solid var(--border-line);
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 600;
    }

    /* Main Container */
    .monitor-main {
      display: flex;
      flex-direction: column;
      flex: 1;
      padding: 16px 24px;
      gap: 14px;
      max-width: 1540px;
      width: 100%;
      margin: 0 auto;
    }

    /* HUD Top Grid */
    .hud-grid {
      display: grid;
      grid-template-columns: 1.8fr 1fr 1fr 1fr;
      gap: 12px;
    }
    @media (max-width: 1024px) {
      .hud-grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 600px) {
      .hud-grid { grid-template-columns: 1fr; }
    }

    .hud-card {
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      border-radius: 14px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
    }
    .hud-primary {
      border-color: rgba(255, 59, 48, 0.35);
      background: linear-gradient(135deg, rgba(255, 59, 48, 0.08) 0%, rgba(12, 13, 20, 0.95) 70%);
    }
    .hud-label {
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .hud-val-row {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin: 8px 0 4px;
    }
    .hud-bpm-big {
      font-size: 58px;
      font-weight: 900;
      letter-spacing: -1.5px;
      line-height: 1;
      color: var(--apple-green);
      font-variant-numeric: tabular-nums;
      transition: color 0.3s ease;
    }
    .hud-unit {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-muted);
    }
    .hud-status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      width: fit-content;
      background: rgba(48, 209, 88, 0.12);
      color: var(--apple-green);
      border: 1px solid rgba(48, 209, 88, 0.3);
    }
    .heart-icon {
      display: inline-block;
      width: 14px;
      height: 14px;
      color: #ffffff;
      transform-origin: center;
      transition: transform 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .heart-icon.beating {
      transform: scale(1.45);
      filter: drop-shadow(0 0 6px #ffffff);
    }

    .hud-val-medium {
      font-size: 34px;
      font-weight: 800;
      color: #ffffff;
      line-height: 1.1;
      margin: 8px 0 4px;
      font-variant-numeric: tabular-nums;
    }
    .hud-subtext {
      font-size: 11.5px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* Checkbox đánh dấu nhịp góc trên bên phải mỗi card */
    .hud-marker-toggle {
      position: absolute;
      top: 13px;
      right: 14px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      user-select: none;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      transition: all 0.2s ease;
      z-index: 5;
    }
    .hud-marker-toggle:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
    }
    .hud-marker-toggle input[type="checkbox"] {
      appearance: none;
      -webkit-appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 4px;
      border: 1.5px solid #4a4f66;
      background: rgba(0, 0, 0, 0.4);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      position: relative;
      outline: none;
      transition: all 0.2s ease;
      margin: 0;
    }
    .toggle-fetal input[type="checkbox"]:checked {
      background: var(--apple-cyan);
      border-color: var(--apple-cyan);
      box-shadow: 0 0 8px rgba(100, 210, 255, 0.6);
    }
    .toggle-fetal input[type="checkbox"]:checked::after {
      content: '';
      width: 3.5px;
      height: 7px;
      border: solid #000;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg) translate(-0.5px, -1px);
      display: block;
    }
    .toggle-maternal input[type="checkbox"]:checked {
      background: var(--apple-green);
      border-color: var(--apple-green);
      box-shadow: 0 0 8px rgba(48, 209, 88, 0.6);
    }
    .toggle-maternal input[type="checkbox"]:checked::after {
      content: '';
      width: 3.5px;
      height: 7px;
      border: solid #000;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg) translate(-0.5px, -1px);
      display: block;
    }
    .hud-marker-toggle:has(input:checked) {
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.18);
    }

    /* Oscilloscope Canvas Card */
    .canvas-container-card {
      background: #040508;
      border: 1px solid var(--border-line);
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      height: 260px;
      min-height: 220px;
      max-height: 290px;
      position: relative;
      overflow: hidden;
    }
    .canvas-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 18px;
      background: #090a12;
      border-bottom: 1px solid var(--border-line);
      z-index: 2;
    }
    .canvas-title {
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: 0.4px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .canvas-pill {
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 4px;
      background: var(--apple-red-dim);
      color: var(--apple-red);
      border: 1px solid rgba(255, 59, 48, 0.3);
    }
    .canvas-metrics {
      display: flex;
      align-items: center;
      gap: 14px;
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-sub);
    }
    .ecg-canvas {
      width: 100%;
      height: 100%;
      flex: 1;
      display: block;
    }

    /* Bottom Control Bar */
    .controls-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--bg-card);
      border: 1px solid var(--border-line);
      border-radius: 14px;
      padding: 10px 20px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .ctrl-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .ctrl-btn {
      background: #181b28;
      border: 1px solid #282e44;
      color: #fff;
      font-size: 13px;
      font-weight: 700;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.18s ease;
      font-family: var(--font-ui);
    }
    .ctrl-btn:hover {
      background: #242a40;
      border-color: #3b4566;
    }
    .ctrl-btn.active {
      background: var(--apple-red-dim);
      border-color: var(--apple-red);
      color: #ffffff;
      box-shadow: 0 0 10px rgba(255, 59, 48, 0.3);
    }
    .ctrl-btn.paused-highlight {
      background: rgba(48, 209, 88, 0.16);
      border-color: var(--apple-green);
      color: var(--apple-green);
      box-shadow: 0 0 10px rgba(48, 209, 88, 0.3);
    }
    .ctrl-select {
      background: #181b28;
      border: 1px solid #282e44;
      color: #fff;
      font-size: 12.5px;
      font-weight: 600;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      outline: none;
      font-family: var(--font-ui);
    }
    .ctrl-select:focus {
      border-color: var(--apple-cyan);
    }
    .time-tracker {
      font-family: var(--font-mono);
      font-size: 13px;
      color: var(--text-sub);
      font-weight: 700;
    }

    /* Disclaimer Footer */
    .disclaimer-foot {
      text-align: center;
      font-size: 11px;
      color: #ff453a;
      font-weight: 700;
      padding: 6px;
      letter-spacing: 0.3px;
    }
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <header class="header-bar">
    <div class="brand-section">
      <div class="brand-pulse-dot"></div>
      <div class="brand-title">RelyFetal · ECG Live Monitor</div>
      <span class="brand-tag">Thiết bị Theo dõi Tim thai Cá nhân</span>
    </div>

    <div class="header-meta">
      <div class="live-badge">
        <span class="live-dot"></span>
        <span id="liveStatusText">REAL-TIME</span>
      </div>
      <div class="clock-tag" id="wallClock">--:--:--</div>
    </div>
  </header>

  <!-- Main Dashboard -->
  <main class="monitor-main">
    <!-- Top HUD Cards -->
    <div class="hud-grid">
      <!-- 1. Primary Fetal Heart Rate (BPM) -->
      <div class="hud-card hud-primary">
        <label class="hud-marker-toggle toggle-fetal" title="Bật/Tắt đánh dấu nhịp tim thai (chấm trắng + tim trắng)">
          <input type="checkbox" id="toggleFetalBeat" checked />
        </label>
        <div class="hud-label">
          <span>NHỊP TIM THAI (FETAL HR)</span>
          <svg class="heart-icon" id="heartIcon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
        </div>
        <div class="hud-val-row">
          <span class="hud-bpm-big" id="bpmVal">--</span>
          <span class="hud-unit">BPM</span>
        </div>
        <div>
          <span class="hud-status-badge" id="statusBadge">NORMAL RHYTHM</span>
        </div>
      </div>

      <!-- 2. Maternal Resting HR -->
      <div class="hud-card">
        <label class="hud-marker-toggle toggle-maternal" title="Bật/Tắt đánh dấu nhịp tim mẹ (chấm xanh lá + tim xanh)">
          <input type="checkbox" id="toggleMaternalBeat" />
        </label>
        <div class="hud-label">NHỊP TIM MẸ (MATERNAL HR)</div>
        <div class="hud-val-row">
          <span class="hud-val-medium" id="matBpmVal">74</span>
          <span class="hud-unit">BPM</span>
        </div>
        <div class="hud-subtext" style="color: var(--apple-green); font-weight: 700;">
          ỔN ĐỊNH · KHỬ TÁCH MẪU
        </div>
      </div>

      <!-- 3. AI Model Accuracy -->
      <div class="hud-card">
        <div class="hud-label">ĐỘ CHÍNH XÁC (AAMI F1)</div>
        <div class="hud-val-row">
          <span class="hud-val-medium" style="color: var(--apple-cyan);" id="f1Val">99.9%</span>
        </div>
        <div class="hud-subtext">
          FetalQRS-TCN · Zero-shot
        </div>
      </div>

      <!-- 4. Latency & Beats -->
      <div class="hud-card">
        <div class="hud-label">ĐỘ TRỄ SUY LUẬN AI</div>
        <div class="hud-val-row">
          <span class="hud-val-medium" style="color: var(--apple-green);" id="latVal">12</span>
          <span class="hud-unit">ms</span>
        </div>
        <div class="hud-subtext" id="beatsVal">
          Phát hiện: 70 nhịp / 30s
        </div>
      </div>
    </div>

    <!-- Oscilloscope ECG Canvas Card -->
    <div class="canvas-container-card" id="canvasCard">
      <div class="canvas-toolbar">
        <div class="canvas-title">
          <span>Đường điện tâm đồ thai nhi (Isolated Fetal ECG Lead)</span>
        </div>
        <div class="canvas-metrics">
          <span id="sweepSec">00:00.0 / 00:30.0</span>
        </div>
      </div>
      <canvas class="ecg-canvas" id="ecgCanvas"></canvas>
    </div>

    <!-- Control Bar -->
    <div class="controls-bar">
      <div class="ctrl-left">
        <!-- Play / Pause -->
        <button class="ctrl-btn" id="playBtn">
          <span id="playIcon">⏸</span>
          <span id="playText">Tạm dừng</span>
        </button>

        <!-- Speed Toggle -->
        <button class="ctrl-btn" id="speedBtn">
          <span>⚡ Tốc độ: <b id="speedText">1.0x</b></span>
        </button>

        <!-- Sound Toggle -->
        <button class="ctrl-btn" id="soundBtn">
          <span id="soundIcon">🔇</span>
          <span id="soundText">Âm nhịp tim: TẮT</span>
        </button>

        <!-- Lead Toggle -->
        <button class="ctrl-btn" id="leadToggleBtn">
          <span>〰 Sóng: <b id="leadTypeText" style="color: var(--apple-red);">Thai cô lập</b></span>
        </button>
      </div>

      <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Ca minh hoạ:</span>
        <select class="ctrl-select" id="caseSelect">
          <option value="r01">r01 — ADFECGDB (F1: 99.9%, Chuẩn mẫu)</option>
          <option value="a09">a09 — CinC 2013 (Zero-shot, F1: 94%)</option>
          <option value="B2_03">B2_03 — Silesia (Chuyển dạ khó)</option>
          <option value="a02">a02 — CinC 2013 (Cảnh báo nhịp mẹ)</option>
          <option value="a27">a27 — CinC 2013 (Tín hiệu yếu)</option>
        </select>
        <span class="time-tracker" id="trackerTimer">00:00 / 00:30</span>
      </div>
    </div>
  </main>

  <footer class="disclaimer-foot">
    Bản mẫu nghiên cứu RelyFetal. Không phải thiết bị y tế chẩn đoán chính thức.
  </footer>

  <script>
    // =========================================================================
    // 1. STATE & TELEMETRY
    // =========================================================================
    let ecgData = null;
    let isPlaying = true;
    let playbackSpeed = 1.0;
    let isMuted = true;
    let showResidual = true; // true: residual_250 (fetal), false: raw
    let showFetalBeat = true; // Bật/Tắt đánh dấu nhịp tim thai
    let showMaternalBeat = false; // Bật/Tắt đánh dấu nhịp tim mẹ
    let currentTimeSec = 0.0;
    let lastAnimTime = null;
    let lastTriggeredBeatIdx = -1;
    let hasCompletedFirstSweep = false; // Đánh dấu đã hoàn thành ít nhất 1 vòng quét hay chưa

    const canvas = document.getElementById('ecgCanvas');
    const ctx = canvas.getContext('2d');
    const canvasCard = document.getElementById('canvasCard');

    // Web Audio Synthesizer Context
    let audioCtx = null;
    function initAudio() {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    }

    function playBeep() {
      if (isMuted) return;
      initAudio();
      if (!audioCtx) return;

      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(680, now); // Warm medical chime

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.18, now + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.055);

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start(now);
      osc.stop(now + 0.06);
    }

    // =========================================================================
    // 2. DATA FETCHER
    // =========================================================================
    async function loadRecordData(recName, autoPlay = true) {
      document.getElementById('liveStatusText').innerText = 'ĐANG NẠP MÔ HÌNH...';
      try {
        const resp = await fetch('/api/monitor_data?rec=' + encodeURIComponent(recName));
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        ecgData = await resp.json();
        currentTimeSec = 0.0;
        lastTriggeredBeatIdx = -1;
        hasCompletedFirstSweep = false; // Khi chuyển sang data mới: reset sạch sẽ, không vẽ sóng cũ tồn đọng

        if (!autoPlay) {
          isPlaying = false;
          playText.innerText = 'Tiếp tục';
          playIcon.innerText = '▶';
          playBtn.classList.add('paused-highlight');
          document.getElementById('liveStatusText').innerText = 'TẠM DỪNG (CHỜ PHÁT)';
        } else {
          isPlaying = true;
          playText.innerText = 'Tạm dừng';
          playIcon.innerText = '⏸';
          playBtn.classList.remove('paused-highlight');
          document.getElementById('liveStatusText').innerText = 'REAL-TIME';
        }

        updateHUDStatic();
        resizeCanvas();
      } catch (err) {
        console.error('Lỗi nạp dữ liệu:', err);
        document.getElementById('liveStatusText').innerText = 'LỖI NẠP: ' + err.message;
      }
    }

    function updateHUDStatic() {
      if (!ecgData) return;
      document.getElementById('matBpmVal').innerText = Math.round(ecgData.maternal_bpm || 74);
      document.getElementById('f1Val').innerText = ecgData.f1_score ? (ecgData.f1_score + '%') : '99.9%';
      document.getElementById('latVal').innerText = Math.round(ecgData.latency_ms || 12);
      document.getElementById('beatsVal').innerText = 'Phát hiện: ' + (ecgData.peaks ? ecgData.peaks.length : 0) + ' nhịp / ' + Math.round(ecgData.duration) + 's';
    }

    // =========================================================================
    // 3. RETINA CANVAS RESIZING
    // =========================================================================
    let dpr = window.devicePixelRatio || 1;
    let cssWidth = 800;
    let cssHeight = 400;

    function resizeCanvas() {
      dpr = window.devicePixelRatio || 1;
      const rect = canvasCard.getBoundingClientRect();
      const measuredW = (rect.width > 0) ? rect.width : (canvasCard.clientWidth || window.innerWidth - 48);
      const measuredH = (rect.height > 0) ? rect.height : (canvasCard.clientHeight || 260);

      cssWidth = Math.max(320, Math.floor(measuredW));
      cssHeight = Math.max(180, Math.floor(measuredH - 42)); // Trừ thanh toolbar

      canvas.width = Math.floor(cssWidth * dpr);
      canvas.height = Math.floor(cssHeight * dpr);
      canvas.style.width = cssWidth + 'px';
      canvas.style.height = cssHeight + 'px';
    }

    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('load', resizeCanvas);
    document.addEventListener('DOMContentLoaded', resizeCanvas);

    // Tự động nhận diện khi container hoàn tất layout (không cần chuyển tab)
    if (window.ResizeObserver) {
      const ro = new ResizeObserver((entries) => {
        for (const entry of entries) {
          if (entry.contentRect && entry.contentRect.width > 0) {
            resizeCanvas();
          }
        }
      });
      ro.observe(canvasCard);
    }

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        lastAnimTime = null;
        resizeCanvas();
      }
    });
    window.addEventListener('focus', () => {
      lastAnimTime = null;
      resizeCanvas();
    });

    // =========================================================================
    // 4. ANIMATION LOOP (60 FPS SWEEP-BEAM OSCILLOSCOPE)
    // =========================================================================
    function render(timestamp) {
      if (!lastAnimTime) lastAnimTime = timestamp;
      let deltaSec = (timestamp - lastAnimTime) / 1000.0;
      lastAnimTime = timestamp;

      // Bảo vệ chống đơ giật khi máy vừa Sleep hoặc Tab bị ẩn rồi bật lại
      if (deltaSec > 0.2 || deltaSec < 0) {
        deltaSec = 0.016; // Tương đương 1 frame 60fps chuẩn
      }

      if (isPlaying && ecgData && ecgData.duration > 0) {
        currentTimeSec += deltaSec * playbackSpeed;
        if (currentTimeSec >= ecgData.duration) {
          currentTimeSec = 0.0;
          lastTriggeredBeatIdx = -1;
        }
      }

      try {
        drawOscilloscope();
      } catch (err) {
        console.error('Lỗi drawOscilloscope:', err);
      }

      try {
        updateDynamicHUD();
      } catch (err) {
        console.error('Lỗi updateDynamicHUD:', err);
      }

      requestAnimationFrame(render);
    }

    function drawOscilloscope() {
      if (!ctx || cssWidth <= 0 || cssHeight <= 0) return;

      ctx.save();
      ctx.scale(dpr, dpr);

      // A. Deep Black OLED Background
      ctx.fillStyle = '#020306';
      ctx.fillRect(0, 0, cssWidth, cssHeight);

      // B. Medical Grid (Chuẩn thời gian cho khung nhìn 2.8s ~ tối đa 6 đỉnh)
      const VIEW_DURATION = 2.8; // Khung nhìn 2.8 giây chứa chính xác 5 - 6 nhịp tim thai
      // Trần an toàn: Đỉnh sóng và chấm tròn không bao giờ vượt qua TOP_SAFE_Y (đảm bảo không chạm icon tim ở y=15)
      const TOP_SAFE_Y = 38;
      const midY = Math.max(TOP_SAFE_Y + 55, cssHeight * 0.56);
      const pxPerSec = cssWidth / VIEW_DURATION;

      // Vertical time grid lines (vạch phụ 0.5s, vạch chính 1.0s)
      for (let s = 0; s <= VIEW_DURATION + 0.1; s += 0.5) {
        const x = s * pxPerSec;
        const isMajor = Math.abs(s % 1.0) < 0.05 || Math.abs(s % 1.0 - 1.0) < 0.05;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, cssHeight);
        ctx.strokeStyle = isMajor ? 'rgba(255, 59, 48, 0.18)' : 'rgba(255, 255, 255, 0.035)';
        ctx.lineWidth = isMajor ? 1.0 : 0.5;
        ctx.stroke();
      }

      // Horizontal baseline and amplitude scale lines
      ctx.beginPath();
      ctx.moveTo(0, midY);
      ctx.lineTo(cssWidth, midY);
      ctx.strokeStyle = 'rgba(255, 59, 48, 0.22)';
      ctx.lineWidth = 1;
      ctx.stroke();

      for (const frac of [0.20, 0.36, 0.72, 0.88]) {
        ctx.beginPath();
        ctx.moveTo(0, cssHeight * frac);
        ctx.lineTo(cssWidth, cssHeight * frac);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // C. Sóng tín hiệu ECG & Markers
      const signal = (ecgData && ecgData.signals)
        ? (showResidual ? (ecgData.signals.residual || []) : (ecgData.signals.raw || []))
        : (showResidual ? (ecgData.res || []) : (ecgData.raw || []));
      const sigLen = signal.length;
      if (sigLen === 0) {
        ctx.restore();
        return;
      }

      const fs = ecgData.fs || 250;
      const totalDur = ecgData.duration || 30.0;

      // Amplitude Scale: Tự động điều chỉnh để đỉnh sóng cao nhất không bị kích trần và luôn cách xa icon trái tim
      const ampScale = Math.min(cssHeight * 0.28, (midY - TOP_SAFE_Y) * 0.82);

      // Tính chu kỳ quét hiện tại & vị trí con trỏ trên màn hình
      const cycleIndex = Math.floor(currentTimeSec / VIEW_DURATION);
      const timeInCycle = currentTimeSec - cycleIndex * VIEW_DURATION;
      const cursorX = (timeInCycle / VIEW_DURATION) * cssWidth;

      // Khoảng cách xóa rộng hơn (90px - 110px) giúp phân tách rõ rệt sóng mới và cũ
      const ERASE_GAP_PX = Math.max(90, Math.floor(cssWidth * 0.09));
      const ERASE_GAP_SEC = (ERASE_GAP_PX / cssWidth) * VIEW_DURATION;
      // Vùng mờ dần của sóng cũ (120px)
      const FADE_ZONE_PX = Math.max(120, Math.floor(cssWidth * 0.12));

      const traceColor = showResidual ? '#ff3b30' : '#64d2ff';
      const glowColor = showResidual ? 'rgba(255, 59, 48, 0.45)' : 'rgba(100, 210, 255, 0.45)';

      // Cập nhật trạng thái đã hoàn thành ít nhất 1 vòng quét hay chưa
      if (currentTimeSec >= VIEW_DURATION) {
        hasCompletedFirstSweep = true;
      }

      // -----------------------------------------------------------------------
      // 1. VẼ SÓNG CŨ (Old Wave - Mờ dần mềm mại khi tiến về khoảng xóa)
      //    CHỈ VẼ KHI ĐÃ HOÀN THÀNH ÍT NHẤT 1 VÒNG QUÉT (Tránh sóng mờ khi vừa nạp data mới)
      // -----------------------------------------------------------------------
      const oldStartSecInCycle = timeInCycle + ERASE_GAP_SEC;
      const fadeStartX = cursorX + ERASE_GAP_PX;
      const fadeEndX = Math.min(cssWidth, fadeStartX + FADE_ZONE_PX);

      if (hasCompletedFirstSweep && oldStartSecInCycle < VIEW_DURATION) {
        let prevCycle = cycleIndex - 1;
        const totalCycles = Math.ceil(totalDur / VIEW_DURATION);
        if (prevCycle < 0) {
          prevCycle = Math.max(0, totalCycles - 1);
        }

        const oldStartRecordTime = prevCycle * VIEW_DURATION + oldStartSecInCycle;
        const oldEndRecordTime = (prevCycle + 1) * VIEW_DURATION;

        const oldStartIdx = Math.max(0, Math.min(sigLen - 1, Math.floor(oldStartRecordTime * fs)));
        const oldEndIdx = Math.max(0, Math.min(sigLen - 1, Math.floor(oldEndRecordTime * fs)));

        if (oldEndIdx > oldStartIdx) {
          // Tạo Gradient mờ dần từ 0.0 (tan biến sát khoảng xóa) lên 1.0 (sáng rõ đầy đủ, không giảm opacity)
          let oldStrokeStyle;
          if (fadeEndX > fadeStartX) {
            const oldGrad = ctx.createLinearGradient(fadeStartX, 0, fadeEndX, 0);
            if (showResidual) {
              oldGrad.addColorStop(0.0, 'rgba(255, 59, 48, 0.0)');
              oldGrad.addColorStop(0.35, 'rgba(255, 59, 48, 0.30)');
              oldGrad.addColorStop(0.70, 'rgba(255, 59, 48, 0.75)');
              oldGrad.addColorStop(1.0, 'rgba(255, 59, 48, 1.0)');
            } else {
              oldGrad.addColorStop(0.0, 'rgba(100, 210, 255, 0.0)');
              oldGrad.addColorStop(0.35, 'rgba(100, 210, 255, 0.30)');
              oldGrad.addColorStop(0.70, 'rgba(100, 210, 255, 0.75)');
              oldGrad.addColorStop(1.0, 'rgba(100, 210, 255, 1.0)');
            }
            oldStrokeStyle = oldGrad;
          } else {
            oldStrokeStyle = showResidual ? '#ff3b30' : '#64d2ff';
          }

          ctx.beginPath();
          let first = true;
          for (let i = oldStartIdx; i <= oldEndIdx; i++) {
            const tRec = i / fs;
            const tCycle = tRec - prevCycle * VIEW_DURATION;
            const x = (tCycle / VIEW_DURATION) * cssWidth;
            const rawY = midY - signal[i] * ampScale;
            const y = Math.max(TOP_SAFE_Y, Math.min(cssHeight - 8, rawY));
            if (first) { ctx.moveTo(x, y); first = false; }
            else { ctx.lineTo(x, y); }
          }
          ctx.strokeStyle = oldStrokeStyle;
          ctx.lineWidth = 2.0;
          ctx.shadowBlur = 0;
          ctx.stroke();
        }
      }

      // -----------------------------------------------------------------------
      // 2. VẼ SÓNG MỚI (New Wave - Từ x = 0 đến con trỏ cursorX)
      // -----------------------------------------------------------------------
      const newStartRecordTime = cycleIndex * VIEW_DURATION;
      const newEndRecordTime = cycleIndex * VIEW_DURATION + timeInCycle;

      const newStartIdx = Math.max(0, Math.min(sigLen - 1, Math.floor(newStartRecordTime * fs)));
      const newEndIdx = Math.max(0, Math.min(sigLen - 1, Math.floor(newEndRecordTime * fs)));

      if (newEndIdx > newStartIdx) {
        ctx.beginPath();
        let first = true;
        for (let i = newStartIdx; i <= newEndIdx; i++) {
          const tRec = i / fs;
          const tCycle = tRec - newStartRecordTime;
          const x = (tCycle / VIEW_DURATION) * cssWidth;
          const rawY = midY - signal[i] * ampScale;
          const y = Math.max(TOP_SAFE_Y, Math.min(cssHeight - 8, rawY));
          if (first) { ctx.moveTo(x, y); first = false; }
          else { ctx.lineTo(x, y); }
        }
        ctx.strokeStyle = traceColor;
        ctx.lineWidth = 2.4; // Nét dày rực rỡ
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 8;
        ctx.stroke();
      }
      // -----------------------------------------------------------------------
      // 3. VẼ KÍ HIỆU ĐÁNH DẤU NHỊP TIM (Fetal & Maternal Heartbeat Markers)
      //    - Tim thai: Chấm xanh cyan trên đường sóng + Trái tim đỏ trên đỉnh
      //    - Tim mẹ: Chấm xanh lá trên đường sóng + Trái tim xanh lá trên đỉnh
      //    - KHÔNG CÓ đường thẳng nào nối giữa trái tim và chấm
      // -----------------------------------------------------------------------
      function drawBeatMarker(px, py, isFresh, ageSec, fadeFactor = 1.0, beatType = 'fetal') {
        ctx.save();
        const baseAlpha = isFresh ? 1.0 : (1.0 * fadeFactor);
        const isMaternal = (beatType === 'maternal');

        // Dấu chấm của tim mẹ thì màu xanh lá, tim thai (con) thì màu trắng
        const markerColor = isMaternal
          ? (isFresh ? '#30d158' : `rgba(48, 209, 88, ${baseAlpha.toFixed(3)})`)
          : (isFresh ? '#ffffff' : `rgba(255, 255, 255, ${baseAlpha.toFixed(3)})`);

        // Biểu tượng trái tim: mẹ = xanh lá (#30d158), thai (con) = trắng (#ffffff)
        const heartColor = isMaternal
          ? (isFresh ? '#30d158' : `rgba(48, 209, 88, ${baseAlpha.toFixed(3)})`)
          : (isFresh ? '#ffffff' : `rgba(255, 255, 255, ${baseAlpha.toFixed(3)})`);

        // A. Điểm tròn trên đường điện tâm đồ (mẹ: xanh lá 4.2px, thai: trắng 4.0px)
        ctx.beginPath();
        ctx.arc(px, py, isMaternal ? 4.2 : 4.0, 0, Math.PI * 2);
        ctx.fillStyle = markerColor;
        ctx.shadowColor = markerColor;
        ctx.shadowBlur = isFresh ? (isMaternal ? 12 : 10) : 0;
        ctx.fill();

        // B. Biểu tượng trái tim ♥ nằm chung 1 hàng ở trên cùng biểu đồ (y = 15px)
        const heartRowY = 15;
        const heartFontSize = (isFresh && ageSec >= 0 && ageSec <= 0.22) ? 'bold 15px' : 'bold 13px';
        ctx.font = `${heartFontSize} -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = heartColor;
        ctx.shadowColor = heartColor;
        ctx.shadowBlur = isFresh ? 8 : 0;
        ctx.fillText('♥', px, heartRowY);

        // C. Hiệu ứng sóng siêu âm lan tỏa mỏng nhẹ (Ripple Pulse) quanh chấm khi vừa đập
        if (isFresh && ageSec >= 0 && ageSec <= 0.25) {
          const progress = ageSec / 0.25;
          const rippleR = 5 + progress * 20;
          const rippleAlpha = (1 - progress) * 0.85;
          ctx.beginPath();
          ctx.arc(px, py, rippleR, 0, Math.PI * 2);
          ctx.strokeStyle = isMaternal ? `rgba(48, 209, 88, ${rippleAlpha})` : `rgba(255, 255, 255, ${rippleAlpha})`;
          ctx.lineWidth = 1.6;
          ctx.stroke();
        }
        ctx.restore();
      }

      // Helper vẽ danh sách peaks (sóng cũ & sóng mới)
      function renderPeakList(peakArray, beatType) {
        if (!peakArray || peakArray.length === 0) return;

        // Vùng sóng cũ (CHỈ VẼ KHI ĐÃ HOÀN THÀNH ÍT NHẤT 1 VÒNG QUÉT TRƯỚC ĐÓ)
        if (hasCompletedFirstSweep && oldStartSecInCycle < VIEW_DURATION) {
          let prevCycle = cycleIndex - 1;
          const totalCycles = Math.ceil(totalDur / VIEW_DURATION);
          if (prevCycle < 0) prevCycle = Math.max(0, totalCycles - 1);
          const oldStartRecordTime = prevCycle * VIEW_DURATION + oldStartSecInCycle;
          const oldEndRecordTime = (prevCycle + 1) * VIEW_DURATION;

          for (let k = 0; k < peakArray.length; k++) {
            const pt = peakArray[k];
            if (pt >= oldStartRecordTime && pt <= oldEndRecordTime) {
              const tCycle = pt - prevCycle * VIEW_DURATION;
              const px = (tCycle / VIEW_DURATION) * cssWidth;
              if (px < fadeStartX) continue;

              const fadeFactor = Math.min(1.0, Math.max(0.0, (px - fadeStartX) / FADE_ZONE_PX));
              if (fadeFactor < 0.12) continue;

              const pIdx = Math.max(0, Math.min(sigLen - 1, Math.round(pt * fs)));
              const rawY = midY - signal[pIdx] * ampScale;
              const py = Math.max(TOP_SAFE_Y, Math.min(cssHeight - 8, rawY));
              drawBeatMarker(px, py, false, 999, fadeFactor, beatType);
            }
          }
        }

        // Vùng sóng mới
        for (let k = 0; k < peakArray.length; k++) {
          const pt = peakArray[k];
          if (pt >= newStartRecordTime && pt <= newEndRecordTime) {
            const tCycle = pt - newStartRecordTime;
            const px = (tCycle / VIEW_DURATION) * cssWidth;
            const pIdx = Math.max(0, Math.min(sigLen - 1, Math.round(pt * fs)));
            const rawY = midY - signal[pIdx] * ampScale;
            const py = Math.max(TOP_SAFE_Y, Math.min(cssHeight - 8, rawY));
            const ageSec = currentTimeSec - pt;
            drawBeatMarker(px, py, true, ageSec, 1.0, beatType);
          }
        }
      }

      // Vẽ nhịp tim thai nếu tickbox Tim Thai được bật
      if (showFetalBeat && ecgData.peaks) {
        renderPeakList(ecgData.peaks, 'fetal');
      }

      // Vẽ nhịp tim mẹ nếu tickbox Tim Mẹ được bật
      if (showMaternalBeat && ecgData.maternal_peaks) {
        renderPeakList(ecgData.maternal_peaks, 'maternal');
      }

      // -----------------------------------------------------------------------
      // 4. ĐẦU QUÉT PHÁT SÁNG (Leading Spark Dot — Đã bỏ thanh dọc trắng)
      // -----------------------------------------------------------------------
      const currVal = signal[newEndIdx] || 0;
      const headY = Math.max(TOP_SAFE_Y, Math.min(cssHeight - 8, midY - currVal * ampScale));

      ctx.beginPath();
      ctx.arc(cursorX, headY, 5.0, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 14;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cursorX, headY, 9.5, 0, Math.PI * 2);
      ctx.strokeStyle = traceColor;
      ctx.lineWidth = 2.0;
      ctx.shadowColor = traceColor;
      ctx.shadowBlur = 8;
      ctx.stroke();

      ctx.restore();
    }

    // =========================================================================
    // 5. DYNAMIC HUD UPDATES (BPM, HEARTBEAT SYNC, TIMERS)
    // =========================================================================
    const bpmValEl = document.getElementById('bpmVal');
    const statusBadgeEl = document.getElementById('statusBadge');
    const heartIconEl = document.getElementById('heartIcon');
    const sweepSecEl = document.getElementById('sweepSec');
    const trackerTimerEl = document.getElementById('trackerTimer');

    function formatTime(s) {
      const min = Math.floor(s / 60);
      const sec = Math.floor(s % 60);
      return String(min).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
    }

    function formatTimePrecise(s) {
      const min = Math.floor(s / 60);
      const sec = Math.floor(s % 60);
      const dec = Math.floor((s % 1) * 10);
      return String(min).padStart(2, '0') + ':' + String(sec).padStart(2, '0') + '.' + dec;
    }

    function updateDynamicHUD() {
      if (!ecgData) return;

      const dur = ecgData.duration || 30.0;
      sweepSecEl.innerText = formatTimePrecise(currentTimeSec) + ' / ' + formatTimePrecise(dur);
      trackerTimerEl.innerText = formatTime(currentTimeSec) + ' / ' + formatTime(dur);

      // Find instantaneous BPM from tachogram
      let curBpm = ecgData.median_fhr || 140;
      if (ecgData.tachogram && ecgData.tachogram.length > 0) {
        for (let i = 0; i < ecgData.tachogram.length; i++) {
          if (ecgData.tachogram[i].t <= currentTimeSec) {
            curBpm = ecgData.tachogram[i].bpm;
          } else {
            break;
          }
        }
      }

      const roundedBpm = Math.round(curBpm);
      bpmValEl.innerText = roundedBpm;

      // Clinical FIGO Threshold Styling
      if (roundedBpm < 110) {
        bpmValEl.style.color = 'var(--apple-red)';
        statusBadgeEl.innerText = 'NHỊP CHẬM (BRADYCARDIA < 110)';
        statusBadgeEl.style.color = 'var(--apple-red)';
        statusBadgeEl.style.borderColor = 'rgba(255, 59, 48, 0.4)';
        statusBadgeEl.style.background = 'rgba(255, 59, 48, 0.12)';
      } else if (roundedBpm > 160) {
        bpmValEl.style.color = 'var(--apple-orange)';
        statusBadgeEl.innerText = 'NHỊP NHANH (TACHYCARDIA > 160)';
        statusBadgeEl.style.color = 'var(--apple-orange)';
        statusBadgeEl.style.borderColor = 'rgba(255, 159, 10, 0.4)';
        statusBadgeEl.style.background = 'rgba(255, 159, 10, 0.12)';
      } else {
        bpmValEl.style.color = 'var(--apple-green)';
        statusBadgeEl.innerText = 'NHỊP TIM THAI BÌNH THƯỜNG (110 - 160)';
        statusBadgeEl.style.color = 'var(--apple-green)';
        statusBadgeEl.style.borderColor = 'rgba(48, 209, 88, 0.4)';
        statusBadgeEl.style.background = 'rgba(48, 209, 88, 0.12)';
      }

      // Check for heartbeat pulse (peaks)
      if (ecgData.peaks && ecgData.peaks.length > 0) {
        for (let i = 0; i < ecgData.peaks.length; i++) {
          const pt = ecgData.peaks[i];
          const diff = currentTimeSec - pt;
          if (diff >= 0 && diff <= 0.16) {
            if (lastTriggeredBeatIdx !== i) {
              lastTriggeredBeatIdx = i;
              heartIconEl.classList.add('beating');
              playBeep();
              setTimeout(() => heartIconEl.classList.remove('beating'), 140);
            }
            break;
          }
        }
      }
    }

    // =========================================================================
    // 6. EVENT LISTENERS & INTERACTIVITY
    // =========================================================================
    const playBtn = document.getElementById('playBtn');
    const playText = document.getElementById('playText');
    const playIcon = document.getElementById('playIcon');

    function togglePlay() {
      isPlaying = !isPlaying;
      playText.innerText = isPlaying ? 'Tạm dừng' : 'Tiếp tục';
      playIcon.innerText = isPlaying ? '⏸' : '▶';
      playBtn.classList.toggle('paused-highlight', !isPlaying);
      document.getElementById('liveStatusText').innerText = isPlaying ? 'REAL-TIME' : 'TẠM DỪNG';
    }
    playBtn.addEventListener('click', togglePlay);

    // Spacebar shortcut
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'SELECT' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        togglePlay();
      }
    });

    // Speed toggle (1.0x -> 0.5x -> 0.25x -> 1.0x)
    const speedBtn = document.getElementById('speedBtn');
    const speedText = document.getElementById('speedText');
    speedBtn.addEventListener('click', () => {
      if (playbackSpeed === 1.0) {
        playbackSpeed = 0.5;
      } else if (playbackSpeed === 0.5) {
        playbackSpeed = 0.25;
      } else {
        playbackSpeed = 1.0;
      }
      speedText.innerText = (playbackSpeed === 0.25 ? '0.25' : playbackSpeed.toFixed(1)) + 'x';
    });

    // Sound toggle
    const soundBtn = document.getElementById('soundBtn');
    const soundText = document.getElementById('soundText');
    const soundIcon = document.getElementById('soundIcon');
    soundBtn.addEventListener('click', () => {
      initAudio();
      isMuted = !isMuted;
      soundBtn.classList.toggle('active', !isMuted);
      soundText.innerText = isMuted ? 'Âm nhịp tim: TẮT' : 'Âm nhịp tim: BẬT';
      soundIcon.innerText = isMuted ? '🔇' : '🔊';
    });

    // Lead type toggle (residual vs raw)
    const leadToggleBtn = document.getElementById('leadToggleBtn');
    const leadTypeText = document.getElementById('leadTypeText');
    leadToggleBtn.addEventListener('click', () => {
      showResidual = !showResidual;
      leadTypeText.innerText = showResidual ? 'Thai cô lập' : 'Điện tim thô';
      leadTypeText.style.color = showResidual ? 'var(--apple-red)' : 'var(--apple-cyan)';
    });

    // Case selection
    const caseSelect = document.getElementById('caseSelect');
    caseSelect.addEventListener('change', (e) => {
      loadRecordData(e.target.value, false); // Tạm dừng biểu đồ khi chuyển ca, chờ bấm tiếp tục
    });

    // Checkbox đánh dấu nhịp tim thai và tim mẹ
    const toggleFetalBeatEl = document.getElementById('toggleFetalBeat');
    const toggleMaternalBeatEl = document.getElementById('toggleMaternalBeat');
    if (toggleFetalBeatEl) {
      toggleFetalBeatEl.addEventListener('change', (e) => {
        showFetalBeat = e.target.checked;
      });
    }
    if (toggleMaternalBeatEl) {
      toggleMaternalBeatEl.addEventListener('change', (e) => {
        showMaternalBeat = e.target.checked;
      });
    }

    // Real-time Clock
    function updateWallClock() {
      const now = new Date();
      document.getElementById('wallClock').innerText = now.toLocaleTimeString('vi-VN', { hour12: false });
    }
    setInterval(updateWallClock, 1000);
    updateWallClock();

    // Init
    resizeCanvas();
    setTimeout(resizeCanvas, 60);
    setTimeout(resizeCanvas, 250);
    loadRecordData('r01');
    requestAnimationFrame(render);
  </script>
</body>
</html>
"""
