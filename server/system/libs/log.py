import logging

log = logging.getLogger("main")
log.setLevel(10)
log.propagate = True

handler = logging.FileHandler("./logs/main_log", mode = "w")
handler.setLevel(10)
handler.setFormatter(logging.Formatter("%(module)s | %(asctime)s [%(levelname)s]: %(message)s"))

log.addHandler(handler)

log.debug("log is created")
