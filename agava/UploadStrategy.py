""" File Download Strategy
"""
import requests
import os


class UploadStrategy:
    """ Interface for file upload strategy
    """

    host = os.environ.get('AGAVA_HOST', 'http://localhost:8080')

    # root directory for local file storage
    local_file_root = os.environ.get('AGAVA_LOCAL_FILE_ROOT', 'temp')

    def upload(self, path):
        """ Upload the preview file to outbound destination. Needs to be implmented!

            Args:
                path (str): path to local file

            Returns:
                None
        """
        raise NotImplementedError('UploadStrategy needs to be implemented!')


class UploadStrategyPostback(UploadStrategy):
    """ Default upload postback strategy
    """

    def upload(self, postback_url, postback_data):
        """ Postback the preview image with metadata from the original inbound file

            Args:
                postback_url   (str): url to send postback data
                postback_data (dict): postback image data

            Returns:
                None
        """

        try:
            requests.post(postback_url, data=postback_data)

        except Exception as ex:

            raise Exception('Unable to access to postback url')
