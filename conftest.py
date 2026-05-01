import csv
from pathlib import Path
from datetime import datetime

test_results = []


def _short_error(report):
    if report.passed:
        return ""

    if hasattr(report.longrepr, "reprcrash"):
        return str(report.longrepr.reprcrash.message)

    if report.longrepr:
        lines = str(report.longrepr).splitlines()
        return lines[-1] if lines else ""

    return ""


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    test_file = Path(report.location[0]).name
    test_name = report.nodeid.split("::")[-1]

    test_results.append({
        "test_file": test_file,
        "test_name": test_name,
        "status": report.outcome.upper(),
        "duration_seconds": f"{report.duration:.4f}",
        "message": _short_error(report),
    })


def pytest_sessionfinish(session, exitstatus):
    output_dir = Path("test_reports")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "pytest_results.csv"

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "test_file",
                "test_name",
                "status",
                "duration_seconds",
                "message",
            ],
        )
        writer.writeheader()
        writer.writerows(test_results)

    print(f"\nCSV test report saved to: {output_file}")