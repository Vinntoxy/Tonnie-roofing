"""
Gunicorn configuration for Tonnie Roofing
Optimized for Render's free tier
"""

import multiprocessing
import os

# Bind to the port Render provides
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker configuration
workers = 1  # Single worker for free tier (prevents session issues)
threads = 4  # Multiple threads per worker
worker_class = "gthread"  # Thread-based workers

# Timeout settings
timeout = 120
graceful_timeout = 30
keepalive = 5

# Maximum requests before worker restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "tonnie-roofing"

# Preload app for faster startup
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# On worker start (for database connections)
def on_starting(server):
    """Log when server starts"""
    server.log.info("🚀 Tonnie Roofing server starting...")

def on_exit(server):
    """Log when server exits"""
    server.log.info("👋 Tonnie Roofing server shutting down...")