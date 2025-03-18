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
            "class": "logging.FileHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
        "storage_handler": {
            "class": "logging.FileHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
        "catalog_handler": {
            "class": "logging.FileHandler",
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
        "storage_logger": {
            "handlers": ["storage_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
        "catalog_logger": {
            "handlers": ["catalog_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

logging.config.dictConfig(logging_config)

api_logger = logging.getLogger("api_logger")
storage_logger = logging.getLogger("storage_logger")
catalog_logger = logging.getLogger("catalog_logger")
