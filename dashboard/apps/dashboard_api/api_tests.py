from django.test import Client
from django.test import TestCase
import json


class APIQueryTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_query(self):
        response = self.client.post('/auth/token/obtain', {'username': 'user', 'password': 'pass'})
        self.assertEqual(response.status_code,400)

        # Actual LDAP Login
        # response = self.client.post('/auth/token/obtain', {'username': 'user', 'password': 'pass'})
        # self.assertEqual(response.status_code, 200)

        python_dict = {
            "chain": [
                {
                    "group": {
                        "by": [
                            'calendar_instance_year'
                        ]
                    }
                }
            ]
        }
        response = self.client.post(
            '/course_stats/query',json.dumps(python_dict),content_type="application/json")
        self.assertEqual(response.status_code,200)

        response = self.client.post(
            '/school_info/query',
            {'chain': [{'group': {'by': ['faculty'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]})
        self.assertEqual(response.status_code,415)

        response = self.client.post(
            '/school_info/query',
            {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact', 'value': 'Science'}],
                        'group': {'by': ['school'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]})
        self.assertEqual(response.status_code,415)

        response = self.client.post(
            '/course_info/query',
            {'chain': [{'filter': [{'field': 'school', 'operator': 'exact',
                                    'value': 'Computer Science and Applied Mathematics'}],
                        'group': {'by': ['course_name'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]})
        self.assertEqual(response.status_code,415)

        response = self.client.post(
            '/course_stats/query',
            {'chain': [{'filter': [{'field': 'calendar_instance_year', 'operator': 'exact', 'value': '2015'},
                                   {'field': 'faculty', 'operator': 'exact', 'value': 'Science'},
                                   {'field': 'school', 'operator': 'exact',
                                    'value': 'Computer Science and Applied Mathematics'},
                                   {'field': 'course_code', 'operator': 'exact', 'value': 'COMS1018'}],
                        'group': {'by': ['gender'], 'yield': [{'name': 'count', 'via': 'count', 'from': 'gender'}],
                                  'distinctGrouping': 'false', 'removeDuplicateCountings': 'duplicate'}}]})
        self.assertEqual(response.status_code,415)
