from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
bind = "127.0.0.1:9000"                   # Don't use port 80 becaue nginx occupied it already.
# Make sure you have the folder of the log files created beforehand
errorlog = os.path.join(BASE_DIR,'gunicorn/error.log')
accesslog = os.path.join(BASE_DIR,'gunicorn/access.log')
loglevel = 'debug'
workers = 1     # the number of recommended workers is '2 * number of CPUs + 1'
