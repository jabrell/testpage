import logging.config
import sys

# Logger-Konfiguration
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(name)s - %(asctime)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "api_handler": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
    },
    "loggers": {
        "api_logger": {
            "handlers": ["api_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

logging.config.dictConfig(logging_config)

api_logger = logging.getLogger("api_logger")
