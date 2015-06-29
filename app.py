""" Setup the flask application and register blueprints
"""

from flask import Flask, send_file, make_response, jsonify, redirect, url_for, session, g, request
from wand.image import Image

import os
import requests
import uuid


def init_app():
    """ Initialize the application entry points
    """
    app = Flask(__name__)

    # set the secret key.  keep this really secret:
    app.secret_key = os.environ['AGAVA_SECRET_KEY']

    # 8GB file size limit
    FILE_SIZE_LIMIT = 8000000000


    def file_is_valid(file_url):
        """ check is file is valid to generate preview
        """
        is_valid = True
        message = ''

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

            if is_valid and (int(resource.headers['content-length']) > FILE_SIZE_LIMIT):
                is_valid = False
                message = 'file size larger than 8GB limit'

        else:
            is_valid = False
            message = 'file not found'

        return is_valid, message


    def download_file(url, name):
        """ Download file and insure a unique file name
        """
        is_valid, message = file_is_valid(url)

        if is_valid:
            unique_id = str(uuid.uuid4().hex)
            local_filename = 'temp/{0}_{1}'.format(unique_id, name)

            resource = requests.get(url, stream=True)

            # download image asset locally
            with open(local_filename, 'wb') as f:

                for chunk in resource.iter_content(chunk_size=1024):

                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()

            return local_filename, message

        return None, message

    @app.route("/generate", methods=['POST', 'GET'])
    def generate_preview():
        """ generate image preview
        """
        req = request.get_json(force=True)

        local_file, message = download_file(req.get('file_url', None), req.get('file_name', ''))

        if local_file:

            if req['file_name'].split('.')[-1].lower() == 'psd':

                # generate preview
                with Image(filename='{0}[0]'.format(local_file)) as img:
                    img.format = 'png'
                    img.transform(resize='250x')
                    img.save(filename='temp/RESIZED_{0}.png'.format(req.get('file_name', '')))

        else:
            return jsonify(result=message, success=False)

        return jsonify(result=request.get_json(force=True), success=True)

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
