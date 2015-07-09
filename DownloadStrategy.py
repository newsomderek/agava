""" File Download Strategy
"""
import uuid
import requests
import os
import hashlib

from wand.image import Image


class DownloadStrategy:
    """ Interface for file download strategy
    """

    # 8GB file size limit by default
    file_size_limit = os.environ.get('AGAVA_FILE_SIZE_LIMIT', 8000000000)

    # root directory for local file storage
    local_file_root = os.environ.get('AGAVA_LOCAL_FILE_ROOT', 'temp')

    def download(self, url, name):
        """ Download the inbound file. Needs to be implmented!

            Args:
                url  (str): inbound file download url
                name (str): outbound file name

            Returns:
                str: local path to original inbound file
        """
        raise NotImplementedError('DownloadStrategy needs to be implmented!')

    def remove(self, path):
        """ Remove local file

            Args:
                path (str): path to local file

            Returns:
                None: returns nothing or exception if error is raised
        """
        os.remove(path)

    def validate(self, url):
        """ Check if file exists and is not too large

            Args:
                url (str): file download url

            Returns:
                bool: True if file exists or otherwise throws an Exception
        """

        # check if file url is provided
        if not url:
            raise Exception('Inbound file not provided!')

        resource = requests.head(url, headers={'Accept-Encoding': 'identity'})

        # in the case of multiple url redirects, confirm the last redirect to the
        # file was successful
        redirect_history = [resp for resp in resource.history]

        if redirect_history and (redirect_history[-1].status_code != 200):
            raise Exception('Last redirect of inbound file did not yield a 200 http status code!')

        # check for a http status success code
        if (not redirect_history) and (resource.status_code != 200):
            raise Exception('Inbound file not found!')

        # check if file is too large
        if int(resource.headers['content-length']) > self.file_size_limit:
            raise Exception('File size larger than {0} byte limit!'.format(self.file_size_limit))

        return True

    def unique_path(self, name):
        """ Get a unique local file path

            Args:
                name (str): name of the resulting file

            Returns:
                str: unique local file path
        """
        return '{0}/{1}_{2}'.format(self.local_file_root, str(uuid.uuid4().hex), name)

    def get_md5(self, path):
        """ Generate file md5 hash

            Args:
                path (str): path to local file

            Returns:
                str: md5 hash of the file
        """

        # find an efficient block size for reading the file
        blocksize = (2**20) if os.path.getsize(path) > (2**20) else 128

        file_hash = hashlib.md5()

        with open(path, "rb" ) as f:

            while True:

                buf = f.read(blocksize)

                if not buf:
                    break

                file_hash.update(buf)

        return file_hash.hexdigest()

    def get_metadata(self, path):
        """ Get file metadata

            Args:
                img (wand.image.Image): Wand Image object

            Returns:
                dict: file metadata
        """
        meta = {}

        with Image(filename=path) as img:

            # extract all basic metadata
            image_metadata = {k: v for k, v in img.metadata.items()}

            meta = {
                'width': img.width,
                'height': img.height,
                'md5': self.get_md5(path),
                # extract all exif metadata
                'exif': {k[len('exif:'):]: image_metadata[k] for k in image_metadata.keys() if k.startswith('exif:')},
                # extract all xmp metadata
                'xmp': {k[len('xmp:'):]: image_metadata[k] for k in image_metadata.keys() if k.startswith('xmp:')},
            }

            if 'date:create' in image_metadata:
                meta['created'] = image_metadata['date:create']

            if 'date:modify' in image_metadata:
                meta['modified'] = image_metadata['date:modify']

        return meta


class DownloadStrategyDefault(DownloadStrategy):
    """ Default download strategy
    """

    def download(self, url, name):
        """ Download the inbound file locally

            Args:
                url  (str): inbound file download url
                name (str): outbound file name

            Returns:
                str: local path to original inbound file
        """

        # throw exception if file does not exists or is too large
        self.validate(url)

        try:

            local_file_path = self.unique_path(name)

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
