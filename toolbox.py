""" usefull methods """
import json
import logging
import sys

from flask import Response

import settings


class ApiResponseHandle:
    """
    api response in unified form
    """

    def __init__(self, message, status=200, mimetype='application/json'):
        self.message = message
        self.status = status
        self.mimetype = mimetype

    def emit(self):
        """
        fire
        :return:
        """
        return Response(json.dumps(self.message), status=self.status, mimetype=self.mimetype)


class ToolBox:
    """
    tools
    """

    @staticmethod
    def get_logger(channel, level=logging.DEBUG):
        """
        get logger instance
        :param channel: text
        :param level:
        :return:
        """
        logger = logging.getLogger(channel)
        logger.setLevel(level)
        file_handler = logging.FileHandler(f'logs\\{channel}.log')

        formatter = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(formatter)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if settings.LOGGING_TO_STDOUT:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger
