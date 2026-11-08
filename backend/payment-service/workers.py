import logging
import threading

import saga
from db import SessionLocal

logger = logging.getLogger("worker")

INTERVAL_SECONDS = 15
_stop = threading.Event()


def _loop() -> None:
    while not _stop.wait(INTERVAL_SECONDS):
        db = SessionLocal()
        try:
            expired = saga.expire_stale(db)
            recovered = saga.recover_stuck(db)
            if expired or recovered:
                logger.info("Worker: %d giao dịch hết hạn, %d giao dịch kẹt được xử lý lại", expired, recovered)
        except Exception:
            logger.exception("Worker gặp lỗi")
        finally:
            db.close()


def start() -> None:
    threading.Thread(target=_loop, name="payment-worker", daemon=True).start()


def stop() -> None:
    _stop.set()
    