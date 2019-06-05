gunicorn \
--bind 0.0.0.0:${TOSKOSE_MANAGER_PORT} \
--chdir /toskose/source \
'app.run:create_app()'
