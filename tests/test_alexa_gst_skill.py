import os
import subprocess
import sys
import time
import unittest

import flask_ask
import six
from requests import post

launch = {
    "version": "1.0",
    "session": {
        "new": True,
        "sessionId": "amzn1.echo-api.session.0000000-0000-0000-0000-00000000000",
        "application": {
            "applicationId": "fake-application-id"
        },
        "attributes": {},
        "user": {
            "userId": "amzn1.account.AM3B00000000000000000000000"
        }
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "fake-application-id"
            },
            "user": {
                "userId": "amzn1.account.AM3B00000000000000000000000"
            },
            "device": {
                "supportedInterfaces": {
                    "AudioPlayer": {}
                }
            }
        },
        "AudioPlayer": {
            "offsetInMilliseconds": 0,
            "playerActivity": "IDLE"
        }
    },
    "request": {
        "type": "LaunchRequest",
        "requestId": "string",
        "timestamp": "string",
        "locale": "string",
        "intent": {
            "name": "TestPlay",
            "slots": {
            }
        }
    }
}

project_root = os.path.abspath(os.path.join(flask_ask.__file__, '../..'))


@unittest.skipIf(six.PY2, "Not yet supported on Python 2.x")
class SmokeTestGSTSkill(unittest.TestCase):
    def setUp(self):
        self.python = sys.executable
        self.env = {'PYTHONPATH': project_root,
                    'ASK_VERIFY_REQUESTS': 'false'}
        if os.name == 'nt':
            self.env['SYSTEMROOT'] = os.getenv('SYSTEMROOT')
            self.env['PATH'] = os.getenv('PATH')

    def _launch(self, sample):
        prefix = os.path.join(project_root, '/')
        path = prefix + sample
        process = subprocess.Popen([self.python, path], env=self.env)
        time.sleep(1)
        self.assertIsNone(process.poll(),
                          msg='Poll should work,'
                              'otherwise we failed to launch')
        self.process = process

    def _post(self, route='/', data={}):
        url = 'http://127.0.0.1:5000' + str(route)
        print('POSTing to %s' % url)
        response = post(url, json=data)
        self.assertEqual(200, response.status_code)
        return response

    def tearDown(self):
        try:
            self.process.terminate()
            self.process.communicate(timeout=1)
        except Exception as e:
            try:
                print('[%s]...trying to kill.' % str(e))
                self.process.kill()
                self.process.communicate(timeout=1)
            except Exception as e:
                print('Error killing test python process: %s' % str(e))
                print('*** it is recommended you manually kill with PID %s',
                      self.process.pid)

    def test_gst_skill(self):
        """ Test the GST skill service """
        self._launch('alexa_gst_skill.py')
        response = self._post(data=launch)
        self.assertTrue('hello' in self._get_text(response))
