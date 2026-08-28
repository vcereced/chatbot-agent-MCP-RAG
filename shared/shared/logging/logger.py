import logging


def configure_logging(service_name: str, level: str = "INFO") -> logging.Logger:

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    return logging.getLogger(service_name)