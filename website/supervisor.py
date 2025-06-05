import subprocess
import time

while True:
    print("🔄 啟動 app.py")
    process = subprocess.Popen([
        "pythonˇ3.10",
        "app.py"
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
