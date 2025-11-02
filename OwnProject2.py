import psutil
import time
from datetime import datetime
import os
from plyer import notification

# List of suspicious process keywords
SUSPICIOUS_KEYWORDS = ['keylogger', 'hook', 'spy', 'inputlog', 'logger', 'intercept']

# Keep track of already detected processes
detected_processes = set()

def scan_for_keyloggers():
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            process_name = proc.info.get('name', '')
            pid = proc.info.get('pid', '')
            path = proc.info.get('exe', 'Unknown')

            cmdline_list = proc.info.get('cmdline')
            cmdline = ' '.join(cmdline_list) if isinstance(cmdline_list, list) else ''

            for keyword in SUSPICIOUS_KEYWORDS:
                if (keyword.lower() in process_name.lower()) or (keyword.lower() in cmdline.lower()):
                    if (process_name, pid) not in detected_processes:
                        detected_processes.add((process_name, pid))
                        alert_user(process_name, pid, path)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def alert_user(process_name, pid, path):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] 🔴 Suspicious process: {process_name} | PID: {pid} | Path: {path}"
    
    print(log_entry)

    # Write to log file
    with open("suspicious_log.txt", "a", encoding="utf-8") as file:
        file.write(log_entry + "\n")

    # Show popup notification
    notification.notify(
        title="🔴 Suspicious Process Detected!",
        message=f"{process_name} (PID: {pid})\nPath: {path}",
        timeout=5
    )

# --- Main Program ---
if __name__ == "__main__":
    try:
        duration = int(input("🔧 Enter scan duration in seconds: "))
        print("\n🔍 Scanning for suspicious processes...\n(Press Ctrl+C to stop early)\n")
        end_time = time.time() + duration

        while time.time() < end_time:
            scan_for_keyloggers()
            time.sleep(5)

        print("\n✅ Scan completed.")

    except KeyboardInterrupt:
        print("\n🛑 Scan stopped by user.")
