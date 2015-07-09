""" File Preview Strategy
"""
import uuid
import os

from wand.image import Image


class PreviewStrategy:
    """ Interface for file preview strategy
    """

    # root directory for local file preview storage
    preview_root = os.environ.get('AGAVA_PREVIEW_ROOT', 'temp')

    def __init__(self):
        # compatible file types
        self.compatible_types = []

        self.preview_width = os.environ.get('AGAVA_PREVIEW_WIDTH', None)
        self.preview_height = os.environ.get('AGAVA_PREVIEW_HEIGHT', None)
        self.preview_resize = os.environ.get('AGAVA_PREVIEW_RESIZE', None)

    def generate(self, path):
        """ Generate preview image

            Args:
                path (str): path to local file

            Returns:
                str: local path to preview image
        """
        raise NotImplementedError('PreviewStrategy needs to be implmented!')

    def unique_path(self, name, format):
        """ Get a unique local file path

            Args:
                name   (str): name of the resulting file
                format (str): outbound file format extension

            Returns:
                str: unique local file path
        """
        return '{0}/R_{1}_{2}.{3}'.format(
            self.preview_root,
            str(uuid.uuid4().hex),
            name,
            format.lower()
        )


    def dimensions(self, path, width=None, height=None, resize=None):
        """ Get image preview dimensions

            Args:
                path   (str): local path to original inbound file
                width  (int): width in pixels
                height (int): height in pixels
                resize (int): resize pixel bounding box

            Returns:
                str: preview dimensions in string form
        """

        # resize file to largest preview possible within resize pixel bounds
        if resize:

            with Image(filename=path) as img:

                if img.width >= img.height:
                    return '{0}x'.format(resize)

                else:
                    return 'x{0}'.format(resize)

        # custom width and height. could lead to improper image ratio
        elif width and height:
            return '{0}x{1}'.format(width, height)

        # sized to width with height staying in proper ratio
        elif width:
            return '{0}x'.format(width)

        # sized to height with width staying in proper ratio
        elif height:
            return 'x{0}'.format(height)

        # same resize using environment variable
        elif self.preview_resize:
            with Image(filename=path) as img:

                if img.width >= img.height:
                    return '{0}x'.format(self.preview_resize)

                else:
                    return 'x{0}'.format(self.preview_resize)

        # custom width and height using environment variables
        elif self.preview_width and self.preview_height:
            return '{0}x{1}'.format(self.preview_width, self.preview_height)

        # size to width using environment variables
        elif self.preview_width:
            return '{0}x'.format(self.preview_width)

        # size to height using environment variables
        elif self.preview_height:
            return 'x{1}'.format(self.preview_height)

        # if execution makes it here, you really didn't set things
        # up properly. a default dimension of a 300 width and ratio
        # matching height will be generated
        return '300x'


class PreviewStrategyGeneral(PreviewStrategy):
    """ General image file previews.
    """

    def __init__(self):

        PreviewStrategy.__init__(self)

        # compatible file types
        self.compatible_types = ['psd', 'psb', 'jpg', 'jpeg', 'png']

    def generate(self, path, name, format='png', width=None, height=None, resize=None):
        """ Generate preview image

            Args:
                path (str): path to local file
                name (str): outbound file name

            Returns:
                str: local path to preview image
        """
        try:

            extension = path.split('.')[-1].lower()

            if extension in self.compatible_types:

                # generate preview
                with Image(filename='{0}[0]'.format(path)) as img:

                    img.format = format

                    if width and height:

                        # allow potential image distortion
                        img.resize(width, height)

                    else:
                        # does not allow image distortion
                        img.transform(
                            resize=self.dimensions(path,
                                        width=width,
                                        height=height,
                                        resize=resize
                                    )
                        )

                    img.save(filename=self.unique_path(name, format))

        except Exception as ex:
            raise Exception(ex.message)

        return None
