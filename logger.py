import logging


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s : %(name)s::%(lineno)s : %(levelname)s : %(message)s'
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename="logs.log")
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.debug("logger was initialized")
