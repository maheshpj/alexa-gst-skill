import json
import os
import subprocess
import sys
import time
import unittest

import flask_ask
import six
from requests import post

import alexa_gst_skill as gst

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


class SmokeTestGSTSkill(unittest.TestCase):
    def test_gst_rates(self):
        """ 
        Test the GST rates for items 
        
        Examples:
            * Given Milk as item test should return 'Milk GST rate should be 0%'
            * Given Coal as item test should return 'Coal GST rate should be 5%'
        """
        gst.init()
        self.assertNotEqual(gst.gst_rates_dict, {})
        rate = gst.gst_rates_dict['milk']
        self.assertEqual('0%', rate, "Milk GST rate should be 0%")
        rate = gst.gst_rates_dict['coal']
        self.assertEqual('5%', rate, "Coal GST rate should be 5%")
        rate = gst.gst_rates_dict['mobile']
        self.assertEqual('12%', rate, "Mobile GST rate should be 12%")
        rate = gst.gst_rates_dict['cars']
        self.assertEqual('28%', rate, "Cars GST rate should be 28%")

    def test_news(self):
        """ 
        Test the GST news 
        
        Provide RSS JSON feed to the test and test should return only GST related news
        """
        expected_news = 'September inflation may hit six- month high on GST and public sector pay rise; ' \
                        'Reduced GST on yarn to help textile sector: Exporter body; ' \
                        'Import of oil-drilling rigs kept out of GST purview'
        rss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rss.json')
        with open(rss_path, 'r') as f:
            rss = json.load(f)
        actual_news = gst.get_gst_news(rss)
        self.assertIsNotNone(actual_news)
        self.assertEqual(actual_news, expected_news, 'Actual news should be same as expected news')

    def test_news_error(self):
        """ 
        Test the GST news error when RSS feed is invalid
        
        Should get 'Failed parsig RSS feed' error if news in invalid
        """
        with self.assertRaises(Exception) as e:
            gst.get_gst_news({})
        self.assertEqual('Failed parsing RSS feed', str(e.exception), "Should get parsing failed error")

    @unittest.skip
    def test_reddit_headline(self):
        """ 
        Test the GST news from Reddit
        This test may fail
        """
        headline = gst.get_reddit_headline()
        self.assertIsNotNone(headline)


@unittest.skipIf(six.PY2, "Not yet supported on Python 2.x")
class SmokeTestGSTSkillPy3(unittest.TestCase):
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
        """ Test the Alexa GST skill service """
        self._launch('alexa_gst_skill.py')
        response = self._post(data=launch)
        self.assertIsNotNone(self._get_text(response))
