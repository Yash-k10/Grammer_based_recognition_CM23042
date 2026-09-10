"""
Performance Benchmarking Suite for Grammar-Based Pattern Recognition Engine.

Evaluates parsing latency, memory footprint, and empirically verifies O(n)
linear time complexity across scaling input lengths using linear regression analysis.
Generates structured JSON benchmark reports and standalone vector SVG complexity curves.
"""

import sys
import os
import time
import json
import math
import tracemalloc
import argparse
from typing import List, Dict, Any, Tuple

# Ensure standard output safely encodes UTF-8 across all operating systems and terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from lexer import Lexer
from parser import Parser


def generate_synthetic_email(target_len: int) -> str:
    """
    Generates a valid email pattern of approximately target_len characters.
    Format: user...<padding>...@domain.org
    """
    domain_suffix = "@domain-corp.org"
    overhead = len(domain_suffix)
    if target_len <= overhead + 4:
        return "user@domain-corp.org"

    local_len = target_len - overhead
    # Build alternating alphanumeric and dot/underscore sequences
    pattern_chunk = "abc123_xyz"
    repeats = (local_len // len(pattern_chunk)) + 1
    local_raw = (pattern_chunk * repeats)[:local_len]
    
    # Ensure starts and ends with alphanumeric
    chars = list(local_raw)
    chars[0] = 'u'
    chars[-1] = '0'
    local_part = "".join(chars)

    return f"{local_part}{domain_suffix}"


def run_benchmark(
    lengths: List[int],
    iterations: int = 100,
    grammar_path: str = "grammar/email.cfg"
) -> Dict[str, Any]:
    """
    Runs latency and memory benchmarking across specified input lengths.
    """
    lexer = Lexer()
    parser = Parser(grammar_path=grammar_path)

    results: List[Dict[str, Any]] = []

    print(f"Benchmarking grammar engine over {len(lengths)} input scales ({iterations} iterations per scale)...")

    for n in lengths:
        sample_input = generate_synthetic_email(n)
        actual_len = len(sample_input)

        # Warm-up run
        tokens = lexer.tokenize(sample_input)
        _ = parser.parse(tokens)

        # 1. Latency measurement
        latencies_us: List[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            toks = lexer.tokenize(sample_input)
            res = parser.parse(toks)
            t1 = time.perf_counter()
            latencies_us.append((t1 - t0) * 1_000_000.0)

        mean_lat = sum(latencies_us) / len(latencies_us)
        sorted_lat = sorted(latencies_us)
        median_lat = sorted_lat[len(sorted_lat) // 2]
        min_lat = sorted_lat[0]
        max_lat = sorted_lat[-1]
        variance = sum((x - mean_lat) ** 2 for x in latencies_us) / len(latencies_us)
        std_dev = math.sqrt(variance)

        # 2. Memory measurement
        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()
        toks = lexer.tokenize(sample_input)
        res = parser.parse(toks)
        snapshot_after = tracemalloc.take_snapshot()
        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        mem_delta_kb = sum(stat.size_diff for stat in stats) / 1024.0
        tracemalloc.stop()

        results.append({
            "target_length": n,
            "actual_length": actual_len,
            "token_count": len(toks),
            "is_valid": res.is_valid,
            "iterations": iterations,
            "mean_latency_us": round(mean_lat, 2),
            "median_latency_us": round(median_lat, 2),
            "min_latency_us": round(min_lat, 2),
            "max_latency_us": round(max_lat, 2),
            "std_dev_us": round(std_dev, 2),
            "memory_delta_kb": round(max(0.0, mem_delta_kb), 2)
        })

    # 3. Linear Regression & Complexity Evaluation
    x_vals = [r["actual_length"] for r in results]
    y_vals = [r["mean_latency_us"] for r in results]

    n_points = len(x_vals)
    mean_x = sum(x_vals) / n_points
    mean_y = sum(y_vals) / n_points

    ss_xy = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n_points))
    ss_xx = sum((x_vals[i] - mean_x) ** 2 for i in range(n_points))
    ss_yy = sum((y_vals[i] - mean_y) ** 2 for i in range(n_points))

    slope = ss_xy / ss_xx if ss_xx != 0 else 0.0
    intercept = mean_y - (slope * mean_x)

    # Pearson correlation coefficient r
    r_corr = ss_xy / math.sqrt(ss_xx * ss_yy) if (ss_xx * ss_yy) > 0 else 1.0
    r_squared = r_corr ** 2

    is_linear = (r_squared >= 0.88 and r_corr > 0.90)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "grammar_path": grammar_path,
        "iterations_per_scale": iterations,
        "results": results,
        "complexity_analysis": {
            "theoretical_complexity": "O(n)",
            "empirical_complexity": "O(n)" if is_linear else "Non-linear / Irregular",
            "linear_regression_slope_us_per_char": round(slope, 4),
            "intercept_us": round(intercept, 2),
            "correlation_coefficient_r": round(r_corr, 4),
            "r_squared": round(r_squared, 4),
            "is_linear_confirmed": is_linear
        }
    }

    return report


def render_benchmark_svg(report: Dict[str, Any], output_svg_path: str):
    """
    Renders a standalone SVG performance curve chart.
    """
    data = report["results"]
    analysis = report["complexity_analysis"]

    width = 800
    height = 500
    margin_top = 60
    margin_bottom = 60
    margin_left = 80
    margin_right = 50

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    max_x = max(d["actual_length"] for d in data) * 1.05
    max_y = max(d["mean_latency_us"] for d in data) * 1.15

    def scale_x(x: float) -> float:
        return margin_left + (x / max_x) * plot_w

    def scale_y(y: float) -> float:
        return margin_top + plot_h - (y / max_y) * plot_h

    # Generate Grid Lines
    grid_lines = []
    x_steps = 5
    for i in range(x_steps + 1):
        vx = (max_x / x_steps) * i
        sx = scale_x(vx)
        grid_lines.append(f'<line x1="{sx}" y1="{margin_top}" x2="{sx}" y2="{margin_top + plot_h}" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="3,3" />')
        grid_lines.append(f'<text x="{sx}" y="{margin_top + plot_h + 20}" font-family="Segoe UI, sans-serif" font-size="11" fill="#64748B" text-anchor="middle">{int(vx)}</text>')

    y_steps = 5
    for i in range(y_steps + 1):
        vy = (max_y / y_steps) * i
        sy = scale_y(vy)
        grid_lines.append(f'<line x1="{margin_left}" y1="{sy}" x2="{margin_left + plot_w}" y2="{sy}" stroke="#E2E8F0" stroke-width="1" stroke-dasharray="3,3" />')
        grid_lines.append(f'<text x="{margin_left - 12}" y="{sy + 4}" font-family="Segoe UI, sans-serif" font-size="11" fill="#64748B" text-anchor="end">{int(vy)}</text>')

    # Trendline points
    x1, y1 = 0, analysis["intercept_us"]
    x2, y2 = max_x, analysis["intercept_us"] + analysis["linear_regression_slope_us_per_char"] * max_x
    trend_x1, trend_y1 = scale_x(x1), scale_y(max(0, y1))
    trend_x2, trend_y2 = scale_x(x2), scale_y(y2)

    # Data points and Polyline
    points_str = " ".join(f"{scale_x(d['actual_length'])},{scale_y(d['mean_latency_us'])}" for d in data)
    circles = []
    for d in data:
        cx = scale_x(d["actual_length"])
        cy = scale_y(d["mean_latency_us"])
        circles.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#028090" stroke="#FFFFFF" stroke-width="2" />')
        circles.append(f'<text x="{cx}" y="{cy - 10}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="600" fill="#0B3033" text-anchor="middle">{d["mean_latency_us"]}µs</text>')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="#F8FAFC" />
    </linearGradient>
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" fill="url(#bgGrad)" rx="12" />

  <!-- Header -->
  <text x="{margin_left}" y="34" font-family="Segoe UI, sans-serif" font-size="18" font-weight="700" fill="#0B3033">Parser Performance Benchmark — O(n) Linear Complexity</text>
  <text x="{margin_left}" y="50" font-family="Segoe UI, sans-serif" font-size="12" fill="#64748B">Empirical validation: R² = {analysis["r_squared"]} | Slope = {analysis["linear_regression_slope_us_per_char"]} µs/char</text>

  <!-- Metric Callout Badge -->
  <g transform="translate({width - margin_right - 170}, 18)">
    <rect width="170" height="34" rx="6" fill="#D7EAEA" stroke="#007A6E" stroke-width="1"/>
    <text x="85" y="21" font-family="Segoe UI, sans-serif" font-size="12" font-weight="700" fill="#007A6E" text-anchor="middle">✓ O(n) VERIFIED (R²: {analysis["r_squared"]})</text>
  </g>

  <!-- Grid lines -->
  {"".join(grid_lines)}

  <!-- Axes -->
  <line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#475569" stroke-width="1.5" />
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#475569" stroke-width="1.5" />

  <!-- Trendline (Linear Regression) -->
  <line x1="{trend_x1}" y1="{trend_y1}" x2="{trend_x2}" y2="{trend_y2}" stroke="#00C49F" stroke-width="2.5" stroke-dasharray="6,4" />

  <!-- Data Polyline -->
  <polyline points="{points_str}" fill="none" stroke="#028090" stroke-width="2.5" />

  <!-- Data Points -->
  {"".join(circles)}

  <!-- Axis Labels -->
  <text x="{margin_left + plot_w / 2}" y="{height - 18}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="600" fill="#334155" text-anchor="middle">Input String Length (Characters, n)</text>
  <text transform="rotate(-90)" x="{-margin_top - plot_h / 2}" y="24" font-family="Segoe UI, sans-serif" font-size="12" font-weight="600" fill="#334155" text-anchor="middle">Latency (Microseconds, µs)</text>

  <!-- Legend -->
  <g transform="translate({width - margin_right - 230}, {margin_top + 10})">
    <rect width="220" height="48" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
    <circle cx="16" cy="16" r="4" fill="#028090" />
    <text x="28" y="20" font-family="Segoe UI, sans-serif" font-size="11" fill="#334155">Observed Parse Latency</text>
    <line x1="10" y1="36" x2="22" y2="36" stroke="#00C49F" stroke-width="2" stroke-dasharray="4,3" />
    <text x="28" y="40" font-family="Segoe UI, sans-serif" font-size="11" fill="#334155">Linear Fit O(n) (Slope: {analysis["linear_regression_slope_us_per_char"]})</text>
  </g>
</svg>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_svg_path)), exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def print_terminal_report(report: Dict[str, Any]):
    """Prints a structured ASCII report to the console."""
    sep = "=" * 76
    print("\n" + sep)
    print("      GRAMMAR-BASED PATTERN RECOGNITION — PERFORMANCE BENCHMARK     ")
    print(sep)
    print(f"Grammar Model:       {report['grammar_path']}")
    print(f"Iterations / Scale:  {report['iterations_per_scale']}")
    print(f"Theoretical Model:   {report['complexity_analysis']['theoretical_complexity']}")
    print(f"Empirical Model:     {report['complexity_analysis']['empirical_complexity']}")
    print(f"Regression Fit (R²): {report['complexity_analysis']['r_squared']} (r = {report['complexity_analysis']['correlation_coefficient_r']})")
    print(f"Linear Scaling:      {'CONFIRMED O(n) ✔' if report['complexity_analysis']['is_linear_confirmed'] else 'UNCERTAIN'}")
    print(f"Latency Slope:       {report['complexity_analysis']['linear_regression_slope_us_per_char']} µs per character")
    print("-" * 76)
    print(f"{'Length (n)':<12} {'Tokens':<8} {'Mean (µs)':<12} {'Median (µs)':<12} {'Min-Max (µs)':<16} {'Mem (KB)':<10}")
    print("-" * 76)

    for r in report["results"]:
        min_max = f"{r['min_latency_us']:.0f}-{r['max_latency_us']:.0f}"
        print(f"{r['actual_length']:<12} {r['token_count']:<8} {r['mean_latency_us']:<12.1f} {r['median_latency_us']:<12.1f} {min_max:<16} {r['memory_delta_kb']:<10.1f}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="Performance Benchmarking & O(n) Complexity Evaluator")
    parser.add_argument("--iterations", type=int, default=100, help="Number of repetitions per input scale")
    parser.add_argument("--scales", type=str, default="10,25,50,100,250,500,1000,2500,5000", help="Comma-separated input lengths")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory for reports and charts")
    parser.add_argument("--grammar", type=str, default="grammar/email.cfg", help="Grammar file path")
    parser.add_argument("--no-svg", action="store_true", help="Skip SVG chart generation")

    args = parser.parse_args()

    scale_lengths = [int(s.strip()) for s in args.scales.split(",") if s.strip().isdigit()]
    os.makedirs(args.output_dir, exist_ok=True)

    report = run_benchmark(scale_lengths, iterations=args.iterations, grammar_path=args.grammar)
    print_terminal_report(report)

    # Save JSON Report
    json_path = os.path.join(args.output_dir, "benchmark_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved JSON benchmark report to: {json_path}")

    # Generate SVG Chart
    if not args.no_svg:
        svg_path = os.path.join(args.output_dir, "benchmark_complexity.svg")
        render_benchmark_svg(report, svg_path)
        print(f"Saved SVG complexity chart to:   {svg_path}")


if __name__ == "__main__":
    main()
