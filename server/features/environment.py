'''
Behave environment pre/post hooks.
'''

import os.path
from subprocess import check_call, check_output, PIPE, STDOUT
import sys
from time import sleep, time

APP = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'app.py',
)
PORT = 8080
INTERFACE = '127.0.0.1'
# how long should we wait for the server process to shut down cleanly?
TIMEOUT = 5

def url():
    return 'http://{}:{}'.format(INTERFACE, PORT)

def before_all(context):
    print 'about to start server...'
    context.server_p = check_output(
        [sys.executable, APP, '--interface', INTERFACE, '--port', str(PORT)])
        # stdout=PIPE, stderr=STDOUT)
    print '...done'
    context.url = url

def after_all(context):
    context.server_p.terminate()
    start = time()
    while time() - start < TIMEOUT:
        if context.server_p.poll() != None:
            sleep(0.5)

    if context.server_p.poll() != None:
        print 'server process did not shut down in time; killing it.'
        context.server_p.kill()
