from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from crypto.security_utils import cleanup_temp_files, ensure_directories
from gui.dashboard import SecureEncryptorApp


BASE_DIR = Path(__file__).resolve().parent
IST = ZoneInfo("Asia/Kolkata")


class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        timestamp = datetime.fromtimestamp(record.created, IST)
        if datefmt:
            return timestamp.strftime(datefmt)
        return timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def configure_logging() -> None:
    ensure_directories(BASE_DIR)
    handler = logging.FileHandler(BASE_DIR / "logs" / "app.log", encoding="utf-8")
    handler.setFormatter(ISTFormatter("%(asctime)s [%(levelname)s] %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


def main() -> None:
    configure_logging()
    cleanup_temp_files(BASE_DIR)
    app = SecureEncryptorApp(BASE_DIR)
    app.mainloop()


if __name__ == "__main__":
    main()
