import logging, os

os.makedirs("logs", exist_ok=True)

log = logging.getLogger("main")
log.setLevel(10)
log.propagate = False

handler = logging.FileHandler("./logs/main.log", mode = "a")
handler.setLevel(10)
handler.setFormatter(logging.Formatter("%(module)s, line %(lineno)d | %(asctime)s [%(levelname)s]: %(message)s"))

log.addHandler(handler)

log.debug("log is created")
