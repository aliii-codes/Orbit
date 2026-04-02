import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "Backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "Frontend"))

from PyQt6.QtWidgets import QApplication
from GUI import MainWindow
from scheduler import start_scheduler
import threading

def main():
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()