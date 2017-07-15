import logging

logging.basicConfig(level=logging.DEBUG)
hdlr = logging.FileHandler("log.txt")
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)
