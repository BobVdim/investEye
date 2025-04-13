import logging
import colorlog

logger = logging.getLogger("investEye_bot")
logger.setLevel(logging.DEBUG)

formatter = colorlog.ColoredFormatter(
    fmt=(
        "%(log_color)s[%(asctime)s] [%(levelname)s] "
        "[%(name)s] %(filename)s:%(lineno)d - %(funcName)s(): "
        "%(message)s"
    ),
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
    datefmt='%H:%M:%S'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
