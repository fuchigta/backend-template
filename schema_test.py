#!/usr/bin/env python3
"""
Schema-driven contract testing using schemathesis CLI.
Validates API endpoints against OpenAPI specification.
"""

import subprocess
import sys
import time

import requests


def log(message: str) -> None:
    """Log message to stdout (replaces print for linting compliance)."""
    sys.stdout.write(f"{message}\n")
    sys.stdout.flush()


def start_server():
    """Start the FastAPI server."""
    return subprocess.Popen(
        ["uv", "run", "python", "main.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(max_wait=10):
    """Wait for server to be ready."""
    for _ in range(max_wait * 2):  # Check every 0.5 seconds
        try:
            response = requests.get("http://localhost:8000/tasks", timeout=1)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


def run_schema_tests():
    """Run schema-driven tests using schemathesis CLI."""
    log("🧪 Running schema-driven tests with schemathesis...")

    # Run schemathesis against the OpenAPI spec
    result = subprocess.run(
        [
            "uv",
            "run",
            "schemathesis",
            "run",
            "openapi.yaml",
            "--url",
            "http://localhost:8000",
            "--max-examples",
            "5",
            "--checks",
            "all",
        ],
        capture_output=True,
        text=True,
    )

    log(result.stdout)
    if result.stderr:
        log(f"Errors: {result.stderr}")

    return result.returncode == 0


def main():
    """Main function to run schema-driven contract tests."""
    log("🚀 Starting schema-driven contract tests...")

    # Start server
    log("📡 Starting server...")
    server = start_server()

    try:
        # Wait for server to be ready
        if not wait_for_server():
            log("❌ Server failed to start within timeout")
            return 1

        log("✅ Server is ready")

        # Run schema tests
        if run_schema_tests():
            log("✅ All schema tests passed!")
            return 0
        else:
            log("❌ Some schema tests failed!")
            return 1

    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return 1

    finally:
        # Stop server
        log("🛑 Stopping server...")
        server.terminate()
        server.wait()


if __name__ == "__main__":
    sys.exit(main())
