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


    @app.route("/generate", methods=['POST', 'GET'])
    def generate_preview():
        """ generate image preview
        """
        req = request.get_json(force=True)
        
        is_valid, message = file_is_valid(req.get('file_url', None))

        if is_valid:
            unique_id = str(uuid.uuid4().hex)
            local_filename = 'temp/{0}_{1}'.format(unique_id, req.get('file_name', ''))

            resource = requests.get(req['file_url'], stream=True)
           
            # download image asset locally 
            with open(local_filename, 'wb') as f:

                for chunk in resource.iter_content(chunk_size=1024):

                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()

            if req['file_name'].split('.')[-1].lower() == 'psd':

                # generate preview
                with Image(filename='{0}[0]'.format(local_filename)) as img:
                    img.format = 'png'
                    img.transform(resize='250x')
                    img.save(filename='temp/RESIZED_{0}_{1}.png'.format(unique_id, req.get('file_name', '')))

        else:
            return jsonify(result=message, success=False)

        return jsonify(result=request.get_json(force=True), success=True)


    # initiliaze api error responses
    @app.errorhandler(400)
    def bad_request(error):
        """ Bad Request
        """
        return make_response(jsonify( { 'error': 'request cannot be fulfilled due to bad syntax' } ), 400)


    @app.errorhandler(401)
    def unauthorized(error):
        """ Unauthorized
        """
        return make_response(jsonify( { 'error': 'authentication is possible but has failed' } ), 401)


    @app.errorhandler(403)
    def forbidden(error):
        """ Forbidden
        """
        return make_response(jsonify( { 'error': 'server refuses to respond to request' } ), 403)


    @app.errorhandler(404)
    def not_found(error):
        """ 404 Not Found
        """
        return make_response(jsonify( { 'error': 'requested resource could not be found' } ), 404)


    @app.errorhandler(405)
    def method_not_allowed(error):
        """ Method not Allowed
        """
        return make_response(jsonify( { 'error': 'request method not supported by that resource' } ), 405)


    return app
