import subprocess
import time

while True:
    print("🔄 啟動 app.py")
    process = subprocess.Popen([
        "python",
        "SQL_final_project/final_project/app.py"
    ])

    try:
        time.sleep(4800)
    except KeyboardInterrupt:
        print("⛔ Manual Abort")
        process.terminate()
        break

    print("🛑 app.py end, restart app.py")
    process.terminate()
    process.wait()
