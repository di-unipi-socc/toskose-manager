import os
import sys
from pathlib import Path
import unittest
import logging
import logging.handlers as handlers

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt

from app.config import AppConfig
from app.config import configs

from app.core.exceptions import FatalError
from app.core.logging import LoggingFacility
from app.manager import ToskoseManager


bcrypt = Bcrypt()


def create_app():
    """ Flask application factory """

    app = Flask(__name__)

    # dynamically load configuration based on app mode (from env TOSKOSE_APP_MODE)
    app.config.from_object(configs[AppConfig._APP_MODE])

    # init flask extensions/plugins
    bcrypt.init_app(app)

    # API INFO
    from app import __full_name__, __author__,__email__,__version__,__repository__
    def api_info():
        return jsonify({
            "name": __full_name__,
            "version": __version__,
            "maintainer": __author__,
            "contacts": __email__,
            "repository": __repository__,
        })
    
    
    # Add a flask route to expose information
    app.add_url_rule("/api/info", "info", view_func=api_info)

    # register blueprints
    from app.api import bp as bp_tosca_api
    app.register_blueprint(bp_tosca_api)

    if not app.debug and not app.testing:

        # remove default handler and add a custom handler
        from flask.logging import default_handler
        app.logger.removeHandler(default_handler)

        app.logger.addHandler(LoggingFacility.get_instance().get_handler())
        app.logger.setLevel(logging.INFO)
        app.logger.info('- Toskose Manager API started -')

    return app


if __name__ == "__main__":

    try:

        flask_app = create_app()
        flask_app.app_context().push()
        flask_app.run()

    except FatalError as err:
        sys.exit(1)