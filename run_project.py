import subprocess
import time
import socket
import sys
import os

def run_command(command, description):

    print(f"--- {description} ---")
    try:
        subprocess.check_call(command, shell=True)
        print(f"OK: {description} completed.\n")
    except subprocess.CalledProcessError:
        print(f"ERROR: {description} failed.")
        sys.exit(1)

def wait_for_postgres(host, port, timeout=30):
    
    print(f"--- Waiting for Database ({host}:{port}) to be ready ---")
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("OK: Database is ready!\n")
                return
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time > timeout:
                print("ERROR: Database connection timed out. Is Docker running?")
                sys.exit(1)
            time.sleep(1)

def main():
    print("=== STARTING AUTOMATED PIPELINE ===\n")

    run_command("docker-compose up -d", "Starting Docker Containers")

    wait_for_postgres("localhost", 5432)

    run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Dependencies")

    run_command(f"{sys.executable} etl_finance.py", "Running ETL Pipeline (Extract & Load)")

    run_command(f"{sys.executable} create_view.py", "Creating SQL Analytical Views")

    print("--- Launching Dashboard ---")
    print("Press Ctrl+C to stop the dashboard and server.")
    subprocess.run(f"{sys.executable} -m streamlit run dashboard.py", shell=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")