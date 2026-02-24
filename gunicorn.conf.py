# gunicorn.conf.py
# Force single worker to avoid session conflicts
workers = 1
threads = 4
worker_class = 'gthread'
timeout = 120
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = 'info'
