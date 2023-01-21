import json
import logging

from flask import Response


class ApiResponseHandle:
    def __init__(self, message, status=200, mimetype='application/json'):
        self.message = message
        self.status = status
        self.mimetype = mimetype

    def emit(self):
        return Response(json.dumps(self.message), status=self.status, mimetype=self.mimetype)


class ToolBox:
    @staticmethod
    def get_logger(channel, level=logging.DEBUG):
        logger = logging.getLogger(channel)
        logging.basicConfig(filename='logs\\' + channel + '.log', filemode='w',
                            format='%(name)s - %(levelname)s - %(message)s')

        logger.setLevel(level)

        fh = logging.FileHandler("main.log")
        fmt = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        return logger
