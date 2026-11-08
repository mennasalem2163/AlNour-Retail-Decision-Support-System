#!/usr/bin/env python3
"""
run.py — Quick-start entry point for the DSS project.
Usage:  python run.py
"""
import os, sys, subprocess

BASE = os.path.dirname(__file__)

def banner():
    print("\n" + "═"*60)
    print("  DSS B-01 · Shop Operating Hours Compliance System")
    print("  Al-Nour Fashion Boutique · Cairo, Egypt")
    print("═"*60 + "\n")

def check_data():
    files = ["pos_transactions.csv", "foot_traffic.csv",
             "staffing.csv", "competitor_activity.csv"]
    missing = [f for f in files if not os.path.exists(os.path.join(BASE, "data", f))]
    if missing:
        print("📦 Generating synthetic datasets...")
        subprocess.run([sys.executable, os.path.join(BASE, "data", "generate_data.py")], check=True)
    else:
        print(f"✅ All {len(files)} data files found.")

def run_tests():
    print("\n🧪 Running unit tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=BASE
    )
    if result.returncode != 0:
        print("⚠️  Some tests failed. Check output above.")
    else:
        print("✅ All tests passed.\n")

def generate_reports():
    print("📄 Generating report and architecture diagram...")
    subprocess.run([sys.executable, os.path.join(BASE, "utils", "generate_report.py")], check=True)
    subprocess.run([sys.executable, os.path.join(BASE, "utils", "generate_architecture_diagram.py")], check=True)
    print("✅ Reports saved to reports/\n")

def launch_dashboard():
    print("🚀 Launching Streamlit dashboard at http://localhost:8501")
    print("   Press Ctrl+C to stop.\n")
    subprocess.run(
        ["streamlit", "run", os.path.join(BASE, "views", "app.py"),
         "--server.headless", "false"],
        cwd=BASE
    )

if __name__ == "__main__":
    banner()
    check_data()
    run_tests()
    generate_reports()
    launch_dashboard()
