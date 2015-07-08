""" Generate Preview Task
"""
from DownloadStrategy import DownloadStrategyDefault
from PreviewStrategy import PreviewStrategyGeneral

from rq import get_current_job
from redis import Redis


def generate_preview_task(url, name, width, height, resize):
    """ Generate preview from inbound file

        Args:
            url  (str): inbound file download url
            name (str): outbound file name

        Returns:
            None
    """
    try:

        download_strategy = DownloadStrategyDefault()

        # download inbound file
        local_file_path = download_strategy.download(url, name)

        general_preview_strategy = PreviewStrategyGeneral()

        extension = url.split('.')[-1].lower()

        # general image previews
        if extension in general_preview_strategy.compatible_types:

            general_preview_strategy.generate(local_file_path, name, width=width, height=height, resize=resize)

        # remove original inbound file
        download_strategy.remove(local_file_path)

    except Exception as ex:

        # get current running queue job
        job = get_current_job(connection=Redis())

        if job:

            job.meta['error'] = ex.message;

            job.save()

        # re-raise exception so RQ job is flagged properly as failed
        raise ex
