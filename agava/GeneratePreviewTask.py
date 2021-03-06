""" Generate Preview Task
"""
from agava.DownloadStrategy import DownloadStrategyDefault
from agava.UploadStrategy import UploadStrategyPostback
from agava.PreviewStrategy import PreviewStrategyGeneral

from rq import get_current_job
from redis import Redis


def generate_preview_task(url, name, width, height, resize, postback):
    """ Generate preview from inbound file

        Args:
            url  (str): inbound file download url
            name (str): outbound file name

        Returns:
            None
    """
    job = None

    try:

        # get current running queue job
        job = get_current_job(connection=Redis())

        download_strategy = DownloadStrategyDefault()

        # download inbound file
        local_file_path = download_strategy.download(url, name)

        general_preview_strategy = PreviewStrategyGeneral()

        extension = url.split('.')[-1].lower()

        # general image previews
        if extension in general_preview_strategy.compatible_types:

            preview_path = general_preview_strategy.generate(
                local_file_path,
                name,
                width=width,
                height=height,
                resize=resize
            )

            upload_strategy = UploadStrategyPostback()

            # update job with file metadata
            job.meta.update(download_strategy.get_metadata(local_file_path))
            job.meta.update({'path': preview_path})

            # public facing download url
            job.meta.update({'download': '{0}/job/{1}/preview'.format(upload_strategy.host, job.id)})

            job.save()

            # send outbound image preview on its way
            if postback:
                upload_strategy.upload(postback, job.meta)

        # remove original inbound file
        download_strategy.remove(local_file_path)

    except Exception as ex:

        if job:

            job.meta['error'] = ex.message;

            job.save()

        # re-raise exception so RQ job is flagged properly as failed
        raise ex
