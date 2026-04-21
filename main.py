import logging
import os
import sys
import threading

from dotenv import load_dotenv

load_dotenv()


def _check_env_keys() -> bool:
    """Check if required .env keys are present. Returns True if all set."""
    required = ["GITHUB_TOKEN", "GROQ_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD"]
    return all(os.getenv(k) for k in required)


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("orbit")
    logger.info("Starting Orbit...")

    from PyQt6.QtWidgets import QApplication

    from Backend.scheduler import start_scheduler
    from Frontend.GUI import FirstRunWizard, MainWindow

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    # Show first-run wizard if .env keys are missing
    if not _check_env_keys():
        logger.info("Missing .env keys — showing setup wizard")
        wizard = FirstRunWizard()
        if wizard.exec() != 1:  # Rejected
            sys.exit(0)
        # Re-load env after wizard saves
        load_dotenv(override=True)

    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()