""" Utility functions
"""
import requests
import os

# 8GB file size limit
FILE_SIZE_LIMIT = 8000000000


def file_is_valid(file_url):
    """ check is file is valid to generate preview
    """
    is_valid = True
    message = ''
    file_size_limit = os.environ.get('AGAVA_FILE_SIZE_LIMIT', FILE_SIZE_LIMIT)

    if file_url:

        resource = requests.head(file_url, headers={'Accept-Encoding': 'identity'})

        for resp in resource.history:

            if resp.status_code != 200:
                is_valid = False
                message = 'file not found'

            else:
                is_valid = True
                message = ''
                break

        if is_valid and (int(resource.headers['content-length']) > file_size_limit):
            is_valid = False
            message = 'file size larger than 8GB limit'

    else:
        is_valid = False
        message = 'file not found'

    return is_valid, message
