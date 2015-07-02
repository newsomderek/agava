""" Welcome to Agava
"""

from flask import Flask, make_response, jsonify, request

import os

from DownloadStrategy import DownloadStrategyDefault
from GeneratePreviewTask import generate_preview_task


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

            download_strategy = DownloadStrategyDefault()

            # throw exception if file does not exists or is too large
            download_strategy.validate(req.get('file_url', None))

            generate_preview_task(req.get('file_url', None), req.get('file_name', ''))

            return jsonify(result=request.get_json(force=True), success=True)

        except Exception as ex:
            return jsonify(result=ex.message, success=False)


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

        return make_response(jsonify(error=message), error.code)

    return app
