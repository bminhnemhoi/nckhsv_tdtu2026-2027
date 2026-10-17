"""
Phân tích mô phỏng phần cứng vi điều khiển (MCU Hardware Profiler)
theo chuẩn STM32Cube.AI & ARM CMSIS-NN cho mô hình FetalQRS-TCN.

Tính toán chi tiết:
- MACs (Multiply-Accumulate Operations) từng lớp
- Dung lượng bộ nhớ Flash (Trọng số INT8 vs FP32)
- Dung lượng bộ nhớ RAM đệm (Activation Arena với kỹ thuật Ping-Pong Buffer)
- Số chu kỳ xung nhịp (CPU Clock Cycles) trên ARM Cortex-M7 (STM32H7) và Xtensa LX7 (ESP32-S3)
- Thời gian suy luận ước tính chính xác (Latency ms) và Hệ số thời gian thực (RTF)
"""
import os, json
import numpy as np

def profile_fetalqrs_tcn():
    # Cấu hình kiến trúc FetalQRS-TCN
    cin = 2
    cout_stem = 40
    kernel = 7
    dilations = [1, 2, 4, 8, 16]
    seq_len = 1000  # 4 giây @ 250 Hz
    
    layers = []
    
    # 1. Stem: Conv1D(2 -> 40, k=7, d=1)
    mac_stem = seq_len * cin * cout_stem * kernel
    param_stem = cin * cout_stem * kernel + cout_stem  # weights + bias
    layers.append({
        "name": "Stem (Conv1D + GELU)",
        "in_shape": [1, cin, seq_len],
        "out_shape": [1, cout_stem, seq_len],
        "kernel": kernel,
        "dilation": 1,
        "params": param_stem,
        "macs": mac_stem,
        "cycles_per_mac_m7": 0.85, # CMSIS-NN arm_convolve_s8 SIMD
        "cycles_per_mac_esp": 1.20
    })
    
    # 2. Năm khối Residual Dilated TCN
    for i, d in enumerate(dilations):
        # Nhánh a: Conv1D(40 -> 40, k=7, dilation=d)
        mac_a = seq_len * cout_stem * cout_stem * kernel
        param_a = cout_stem * cout_stem * kernel + cout_stem
        # Nhánh b: Conv1D(40 -> 40, k=7, dilation=d)
        mac_b = seq_len * cout_stem * cout_stem * kernel
        param_b = cout_stem * cout_stem * kernel + cout_stem
        
        # Với d > 1, strided access nạp dữ liệu tăng chu kỳ nhẹ
        c_m7 = 1.15 if d <= 4 else 1.25
        c_esp = 1.35 if d <= 4 else 1.45
        
        layers.append({
            "name": f"Block_{i+1}_ConvA (d={d})",
            "in_shape": [1, cout_stem, seq_len],
            "out_shape": [1, cout_stem, seq_len],
            "kernel": kernel,
            "dilation": d,
            "params": param_a,
            "macs": mac_a,
            "cycles_per_mac_m7": c_m7,
            "cycles_per_mac_esp": c_esp
        })
        layers.append({
            "name": f"Block_{i+1}_ConvB (d={d})",
            "in_shape": [1, cout_stem, seq_len],
            "out_shape": [1, cout_stem, seq_len],
            "kernel": kernel,
            "dilation": d,
            "params": param_b,
            "macs": mac_b,
            "cycles_per_mac_m7": c_m7,
            "cycles_per_mac_esp": c_esp
        })
    
    # 3. Head: Conv1D(40 -> 1, k=1, d=1)
    mac_head = seq_len * cout_stem * 1 * 1
    param_head = cout_stem * 1 * 1 + 1
    layers.append({
        "name": "Head (Conv1D 1x1 + Sigmoid)",
        "in_shape": [1, cout_stem, seq_len],
        "out_shape": [1, 1, seq_len],
        "kernel": 1,
        "dilation": 1,
        "params": param_head,
        "macs": mac_head,
        "cycles_per_mac_m7": 0.50, # 1x1 conv tối ưu cực cao
        "cycles_per_mac_esp": 0.80
    })
    
    # Tổng hợp
    total_macs = sum(l["macs"] for l in layers)
    total_params = sum(l["params"] for l in layers)
    
    # Chu kỳ xung nhịp Cortex-M7 (STM32H7 @ 480 MHz)
    conv_cycles_m7 = sum(l["macs"] * l["cycles_per_mac_m7"] for l in layers)
    # Thêm chi phí cho GELU LUT (2 cycles/element) và Residual Add (__SADD8: 0.25 cycles/element)
    gelu_elements = seq_len * cout_stem * (1 + len(dilations) * 2)
    res_elements = seq_len * cout_stem * len(dilations)
    misc_cycles_m7 = (gelu_elements * 2.0) + (res_elements * 0.25)
    total_cycles_m7 = conv_cycles_m7 + misc_cycles_m7
    
    # Chu kỳ xung nhịp ESP32-S3 (Xtensa LX7 @ 240 MHz, ESP-NN)
    conv_cycles_esp = sum(l["macs"] * l["cycles_per_mac_esp"] for l in layers)
    misc_cycles_esp = (gelu_elements * 2.5) + (res_elements * 0.5)
    total_cycles_esp = conv_cycles_esp + misc_cycles_esp
    
    # Bộ nhớ Flash tĩnh
    flash_fp32_kb = (total_params * 4) / 1024.0
    flash_int8_kb = (total_params * 1 + len(layers) * 4 * 4) / 1024.0 # weights + bias/scale
    
    # Bộ nhớ RAM động (Activation Arena - Ping Pong buffer + 1 Skip buffer)
    # Max activation: 40 channels * 1000 samples
    max_act = cout_stem * seq_len
    # FP32: 2 ping-pong buffers (40k * 4 bytes = 160KB each) + 1 skip buffer (160KB) = 480 KB
    ram_fp32_kb = (max_act * 4 * 3) / 1024.0
    # INT8: 2 ping-pong buffers (40k * 1 byte = 40KB each) + 1 skip buffer (40KB) = 120 KB
    ram_int8_kb = (max_act * 1 * 3) / 1024.0
    
    # Thời gian suy luận
    # STM32H7 @ 480 MHz
    freq_h7 = 480e6
    latency_h7_ms = (total_cycles_m7 / freq_h7) * 1000.0
    rtf_h7 = 4000.0 / latency_h7_ms
    duty_cycle_h7 = (latency_h7_ms / 4000.0) * 100.0
    sleep_h7 = 100.0 - duty_cycle_h7
    
    # ESP32-S3 @ 240 MHz (1 core)
    freq_esp = 240e6
    latency_esp_1core_ms = (total_cycles_esp / freq_esp) * 1000.0
    rtf_esp_1core = 4000.0 / latency_esp_1core_ms
    duty_cycle_esp = (latency_esp_1core_ms / 4000.0) * 100.0
    sleep_esp = 100.0 - duty_cycle_esp
    
    # ESP32-S3 Dual-Core (hệ số tăng tốc đa nhân ~1.8x)
    latency_esp_2core_ms = latency_esp_1core_ms / 1.8
    rtf_esp_2core = 4000.0 / latency_esp_2core_ms
    
    results = {
        "model": "FetalQRS-TCN",
        "input_window_s": 4.0,
        "input_samples": seq_len,
        "total_parameters": total_params,
        "total_macs": total_macs,
        "total_macs_m": total_macs / 1e6,
        "gflops": (total_macs * 2) / 1e9,
        "memory": {
            "flash_fp32_kb": round(flash_fp32_kb, 1),
            "flash_int8_kb": round(flash_int8_kb, 1),
            "flash_savings_pct": round((1 - flash_int8_kb / flash_fp32_kb) * 100, 1),
            "ram_arena_fp32_kb": round(ram_fp32_kb, 1),
            "ram_arena_int8_kb": round(ram_int8_kb, 1),
            "ram_savings_pct": round((1 - ram_int8_kb / ram_fp32_kb) * 100, 1)
        },
        "stm32h7": {
            "mcu": "STM32H743ZI / STM32H753VI",
            "core": "ARM Cortex-M7 @ 480 MHz",
            "flash_available_kb": 2048,
            "ram_available_kb": 1024,
            "flash_usage_pct": round((flash_int8_kb / 2048.0) * 100, 2),
            "ram_usage_pct": round((ram_int8_kb / 1024.0) * 100, 2),
            "clock_cycles": int(total_cycles_m7),
            "latency_ms": round(latency_h7_ms, 2),
            "rtf": round(rtf_h7, 1),
            "duty_cycle_pct": round(duty_cycle_h7, 2),
            "deep_sleep_pct": round(sleep_h7, 2)
        },
        "esp32s3": {
            "mcu": "ESP32-S3 (WROOM-1 / DevKit)",
            "core": "Xtensa Dual-Core LX7 @ 240 MHz",
            "flash_available_kb": 8192,
            "ram_available_kb": 512,
            "flash_usage_pct": round((flash_int8_kb / 8192.0) * 100, 2),
            "ram_usage_pct": round((ram_int8_kb / 512.0) * 100, 2),
            "clock_cycles_1core": int(total_cycles_esp),
            "latency_1core_ms": round(latency_esp_1core_ms, 2),
            "rtf_1core": round(rtf_esp_1core, 1),
            "latency_2core_ms": round(latency_esp_2core_ms, 2),
            "rtf_2core": round(rtf_esp_2core, 1),
            "duty_cycle_2core_pct": round((latency_esp_2core_ms / 4000.0) * 100, 2),
            "deep_sleep_2core_pct": round(100.0 - (latency_esp_2core_ms / 4000.0) * 100, 2)
        },
        "layers": layers
    }
    
    os.makedirs("analysis", exist_ok=True)
    with open("analysis/mcu_hardware_profile.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"=== BÁO CÁO MÔ PHỎNG PHẦN CỨNG THEO CHUẨN STM32Cube.AI & CMSIS-NN ===")
    print(f"Mô hình: {results['model']} | Tham số: {total_params:,} | Tính toán: {results['total_macs_m']:.2f} MMACs ({results['gflops']:.3f} GFLOPs)")
    print(f"\n[1] BỘ NHỚ NHÚNG:")
    print(f"  - Flash ROM (INT8): {results['memory']['flash_int8_kb']} KB (Tiết kiệm {results['memory']['flash_savings_pct']}%)")
    print(f"  - RAM đệm Arena (INT8): {results['memory']['ram_arena_int8_kb']} KB (Tiết kiệm {results['memory']['ram_savings_pct']}%)")
    print(f"\n[2] VI ĐIỀU KHIỂN STM32H7 (ARM Cortex-M7 @ 480 MHz):")
    print(f"  - Chiếm Flash: {results['stm32h7']['flash_usage_pct']}% / 2MB Flash")
    print(f"  - Chiếm RAM:   {results['stm32h7']['ram_usage_pct']}% / 1MB RAM")
    print(f"  - Chu kỳ CPU:  {results['stm32h7']['clock_cycles']:,} cycles")
    print(f"  - Thời gian:   {results['stm32h7']['latency_ms']} ms (cho 4s tín hiệu)")
    print(f"  - Tốc độ RTF:  {results['stm32h7']['rtf']}x nhanh hơn thời gian thực")
    print(f"  - Ngủ sâu:     {results['stm32h7']['deep_sleep_pct']}% thời gian (Duty cycle: {results['stm32h7']['duty_cycle_pct']}%)")
    print(f"\n[3] VI ĐIỀU KHIỂN ESP32-S3 (Xtensa Dual-Core LX7 @ 240 MHz):")
    print(f"  - Chiếm Flash: {results['esp32s3']['flash_usage_pct']}% / 8MB Flash")
    print(f"  - Chiếm RAM:   {results['esp32s3']['ram_usage_pct']}% / 512KB SRAM")
    print(f"  - Thời gian (Dual-Core): {results['esp32s3']['latency_2core_ms']} ms (cho 4s tín hiệu)")
    print(f"  - Tốc độ RTF:  {results['esp32s3']['rtf_2core']}x nhanh hơn thời gian thực")
    print(f"  - Ngủ sâu:     {results['esp32s3']['deep_sleep_2core_pct']}% thời gian (Duty cycle: {results['esp32s3']['duty_cycle_2core_pct']}%)")
    
    return results

if __name__ == "__main__":
    profile_fetalqrs_tcn()
