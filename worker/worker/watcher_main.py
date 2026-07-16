import time

from worker.config import get_settings
from worker.logging import configure_logging, get_logger
from worker.watcher import start_watching

logger = get_logger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    observer = start_watching(settings.uploads_dir)
    logger.info("watcher.started", uploads_dir=settings.uploads_dir)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
