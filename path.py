import os


def check_and_create_directories():
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
