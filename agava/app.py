""" Welcome to Agava
"""

from flask import Flask, make_response, jsonify, request

import os

from agava.DownloadStrategy import DownloadStrategyDefault
from agava.GeneratePreviewTask import generate_preview_task
from redis import Redis
from rq import Queue
from rq.job import Job


def init_app():
    """ Initialize
    """
    app = Flask(__name__)

    # set the secret key.  keep this really secret
    app.secret_key = os.environ['AGAVA_SECRET_KEY']

    @app.route("/generate", methods=['POST'])
    def generate_preview():
        """ Generate image preview
        """
        try:
            req = request.get_json(force=True)

            # process request arguments
            url = req.get('url', None)
            name = req.get('name', '')
            width = req.get('width', None)
            height = req.get('height', None)
            resize = req.get('resize', None)

            download_strategy = DownloadStrategyDefault()

            # throw exception if file does not exists or is too large
            download_strategy.validate(url)

            q = Queue(connection=Redis())

            # 30 minutes default before job times out
            job_timeout = os.environ.get('AGAVA_TIMEOUT', 60 * 30)

            # 1 day default before job results expire
            job_result_ttl = os.environ.get('AGAVA_RESULT_TTL', 60 * 60 * 24)

             # 1 hour maximum for job to sit in queue before cancelled
            job_ttl = os.environ.get('AGAVA_TTL', 60 * 60)

            # add preview job to task queue
            job = q.enqueue_call(
                func=generate_preview_task,
                args=(url, name, width, height, resize),
                timeout=job_timeout,
                result_ttl=job_result_ttl,
                ttl=job_ttl
            )

            result = {
                'job_id': job.id,
                'images': []
            }

            return jsonify(result=result)

        except Exception as ex:

            result = {
                'error': ex.message
            }

            return jsonify(result=result), 500



    @app.route("/job/<string:job_id>", methods=['GET'])
    def get_job(job_id):
        """ Get preview job details
        """
        try:

            job = Job.fetch(job_id, connection=Redis())

            if job:

                result = {
                    'id': job.id,
                    'status': job._status,
                    'meta': job.meta
                }

                return jsonify(result=result)

            raise Exception('unable to find job')

        except Exception as ex:

            result = {
                'error': ex.message
            }

            return jsonify(result=result), 404


    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    def bad_request(error):
        """ HTTP error handling
        """
        messages = {
            400: 'request cannot be fulfilled due to bad syntax',
            401: 'authentication is possible but has failed',
            403: 'server refuses to respond to request',
            404: 'requested resource could not be found',
            405: 'request method not supported by that resource',
            'error': 'server error!'
        }

        message = messages[error.code] if error.code in messages else messages['error']

        return jsonify(error=message), error.code

    return app
