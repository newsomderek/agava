""" Agava Dev Server
"""

from agava.app import init_app

app = init_app()
app.debug = True
app.run(host='0.0.0.0', port=8080)
