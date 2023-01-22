""" make sure we have all folders we need """
import os


def create_folders_if_not_exist():
    """
    create if not exists
    :return:
    """
    # sound
    if not os.path.exists('models'):
        os.makedirs('models')

    # camera
    if not os.path.exists('upload'):
        os.makedirs('upload')
        os.makedirs('upload/trained')

    if not os.path.exists('database'):
        os.makedirs('database')

    if not os.path.exists('logs'):
        os.makedirs('logs')
