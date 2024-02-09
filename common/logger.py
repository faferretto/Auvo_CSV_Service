import logging.handlers
import logging
import os
import setup


class CustomFormatter(logging.Formatter):
    lavender = '<body bgcolor="#000000"><font color="Lavender">'
    yellow = '<body bgcolor="#000000"><font color="lightgoldenrodyellow">'
    red = '<body bgcolor="#000000"><font color="indianred">'
    orange = '<body bgcolor="#000000"><font color="Orange">'
    reset = '</font><br />'
    format = "%(asctime)s [%(levelname)-3.3s]  %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: lavender + format + reset,
        logging.INFO: yellow + format + reset,
        logging.WARNING: orange + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LOGGER:
    logFormatterFile = logging.Formatter("%(asctime)s [%(levelname)-3.3s]  %(message)s")
    logFormatterConsole = logging.Formatter("%(asctime)s [%(levelname)-3.3s]  %(message)s (%(filename)s:%(lineno)d)")
    logging.basicConfig(level=logging.DEBUG)
    rootLogger = logging.getLogger("App")
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.propagate = setup.debug_enabled
    if setup.log_enabled:
        LogFolder = "Logs"
        LogPath = os.getcwd() + "\\" + LogFolder
        if not os.path.exists(LogPath):
            os.mkdir(LogPath)
        fileHandler = logging.handlers.TimedRotatingFileHandler('Logs/log.txt', when=setup.log_when,
                                                                interval=setup.log_interval,
                                                                backupCount=setup.log_max_files)
        fileHandler.namer = lambda name: name.replace(".txt", "").replace(".", "_") + ".txt"
        fileHandler.setFormatter(logFormatterFile)
        fileHandler.setLevel(logging.INFO)
        if setup.debug_enabled:
            htmlHandler = logging.handlers.RotatingFileHandler('Logs/debug.html', maxBytes=20000000, backupCount=20)
            htmlHandler.namer = lambda name: name.replace(".html", "").replace(".", "_") + ".html"
            htmlHandler.setFormatter(CustomFormatter())
            htmlHandler.setLevel(logging.DEBUG)
            rootLogger.addHandler(htmlHandler)
        errorLogHandler = logging.handlers.RotatingFileHandler('Logs/error.txt', maxBytes=5000, backupCount=0)
        errorLogHandler.namer = lambda name: name.replace(".txt", "").replace(".", "_") + ".txt"
        errorLogHandler.setLevel(logging.ERROR)
        errorLogHandler.setFormatter(logFormatterFile)
        rootLogger.addHandler(fileHandler)
        rootLogger.addHandler(errorLogHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatterConsole)
    rootLogger.addHandler(consoleHandler)
