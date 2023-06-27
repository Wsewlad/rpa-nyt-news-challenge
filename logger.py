import logging

logger = logging.getLogger('nyt')
logger.setLevel(logging.DEBUG)
logger.propagate = False

formatter = logging.Formatter(
    r"%(levelname)-7s [%(filename)s:%(lineno)s] - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
