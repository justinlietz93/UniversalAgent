"""
Test runner script for the Universal Agent project.

This script discovers and runs all unit tests within the 'tests' directory
using the 'coverage' tool to measure code coverage.
"""
import os
import sys
import subprocess

# Add the project root directory to the Python path to allow imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Determine the path to the virtual environment's Python executable
# Adjust 'Scripts' for Windows, 'bin' for Linux/macOS if needed, but assuming Windows based on OS info
VENV_PYTHON_PATH = os.path.join(project_root, '.venv', 'Scripts', 'python.exe')
# Use the venv python if it exists, otherwise fall back to sys.executable (though this might fail)
python_exe = VENV_PYTHON_PATH if os.path.exists(VENV_PYTHON_PATH) else sys.executable


def run_all_tests_with_coverage():
    """Discovers and runs all tests using coverage."""
    print("Running tests with coverage...")
    test_dir = os.path.join(project_root, 'tests')
    source_dir = os.path.join(project_root, 'src')

    # Command to run tests under coverage
    # Includes source specification for accurate reporting
    coverage_run_cmd = [
        python_exe, '-m', 'coverage', 'run',
        f'--source={source_dir}',
        # Run discover from the project root (cwd in subprocess.run)
        '-m', 'unittest', 'discover',
        # Removed '-s test_dir'
        '-p', 'test_*.py'
    ]

    # Command to generate text report
    coverage_report_cmd = [python_exe, '-m', 'coverage', 'report', '-m']

    # Command to generate HTML report
    coverage_html_cmd = [python_exe, '-m', 'coverage', 'html']

    # Execute coverage run
    print(f"Executing: {' '.join(coverage_run_cmd)}")
    # Create a copy of the current environment and add the project root to PYTHONPATH
    env = os.environ.copy()
    # Ensure project_root itself is on the path for the subprocess
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    run_result = subprocess.run(coverage_run_cmd, capture_output=True, text=True, cwd=project_root, env=env)

    print("\n--- Coverage Run Output ---")
    print(run_result.stdout)
    if run_result.stderr:
        print("--- Coverage Run Errors ---")
        print(run_result.stderr)
        print("-------------------------")

    if run_result.returncode != 0:
        print("\nCoverage run command failed.")
        # Optionally, could try to run report anyway or just exit
        # sys.exit(run_result.returncode) # Exit if run fails

    # Execute coverage report (text)
    print(f"\nExecuting: {' '.join(coverage_report_cmd)}")
    report_result = subprocess.run(coverage_report_cmd, capture_output=True, text=True, cwd=project_root)
    print("\n--- Coverage Text Report ---")
    print(report_result.stdout)
    if report_result.stderr:
        print("--- Coverage Report Errors ---")
        print(report_result.stderr)
        print("----------------------------")

    # Execute coverage html report
    print(f"\nExecuting: {' '.join(coverage_html_cmd)}")
    html_result = subprocess.run(coverage_html_cmd, capture_output=True, text=True, cwd=project_root)
    print("\n--- Coverage HTML Report ---")
    print(html_result.stdout) # Usually prints output directory
    if html_result.stderr:
        print("--- Coverage HTML Errors ---")
        print(html_result.stderr)
        print("--------------------------")

    # Note: Determining overall test success (pass/fail) from coverage output
    # can be complex. This script focuses on running coverage and generating reports.
    # The user should inspect the 'Coverage Run Output' and reports for failures.
    # A more robust script might parse the output or use pytest-cov.

    # For simplicity, exit 0 if commands ran, user inspects results.
    # A non-zero exit from 'coverage run' might indicate test failures.
    if run_result.returncode != 0:
         print("\nTest execution via coverage encountered errors or failures.")
         sys.exit(run_result.returncode)
    else:
         print("\nTests executed via coverage. Please review reports.")
         sys.exit(0)


if __name__ == '__main__':
    run_all_tests_with_coverage()
