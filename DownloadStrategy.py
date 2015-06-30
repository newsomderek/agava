""" File Download Strategy
"""
import uuid
import requests

from util import file_is_valid


class DownloadStrategyDefault(object):
    """ Default download Strategy
    """

    def download(self, url, name):
        """ Download the inbound file locally
        """
        is_valid = file_is_valid(url)

        if is_valid:

            try:

                local_file_path = 'temp/{0}_{1}'.format(str(uuid.uuid4().hex), name)

                resource = requests.get(url, stream=True)

                # download image asset locally
                with open(local_file_path, 'wb') as f:

                    for chunk in resource.iter_content(chunk_size=1024):

                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                            f.flush()

                return local_file_path

            except:
                raise Exception('Unable to download the inbound file!')

        return None


class DownloadStrategy(object):
    """ Interface for file download Strategy
    """

    def __init__(self, strategy=DownloadStrategyDefault):
        """
        """
        self.action = strategy()

    def download(self, url, name):
        """ Download method for inbound file persistance

            Args:
                url  (str): downloadable url to inbound file
                name (str): name of outbound file

            Returns:
                str: local file path of downloaded inbound file
        """
        if(self.action):
            return self.action.download(url, name)

        else:
            raise NotImplementedError('DownloadStrategy is an abstract class!')
