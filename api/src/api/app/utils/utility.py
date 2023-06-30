import errno
import os
import shutil

def _get_input_directory():
    return os.path.join("/api", "input")

def _create_directory(directory_name):
    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

def _create_empty_directory(directory_name):
    try:
        os.makedirs(directory_name)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise