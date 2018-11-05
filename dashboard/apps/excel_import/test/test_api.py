from django.test import Client
from django.test import TestCase


class APIQueryTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_query(self):

        response = self.client.post(
            '/query/course_stats',
            {'chain': [{'group': {'by': ['calendar_instance_year'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]}
        )
        self.assertEqual(response.status_code, 415)

        response = self.client.post(
            '/query/school_info',
            {'chain': [{'group': {'by': ['faculty'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]}
        )
        self.assertEqual(response.status_code, 415)

        response = self.client.post(
            '/query/school_info',
            {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact', 'value': 'Science'}],
                        'group': {'by': ['school'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]}
        )
        self.assertEqual(response.status_code, 415)

        response = self.client.post(
            '/query/course_info',
            {'chain': [{'filter': [{'field': 'school', 'operator': 'exact',
                                    'value': 'Computer Science and Applied Mathematics'}],
                        'group': {'by': ['course_name'], 'distinctGrouping': 'true',
                                  'removeDuplicateCountings': 'false'}}]}
        )
        self.assertEqual(response.status_code, 415)

        response = self.client.post(
            '/query/course_stats',
            {'chain': [{'filter': [{'field': 'calendar_instance_year', 'operator': 'exact', 'value': '2015'},
                                   {'field': 'faculty', 'operator': 'exact', 'value': 'Science'},
                                   {'field': 'school', 'operator': 'exact',
                                    'value': 'Computer Science and Applied Mathematics'},
                                   {'field': 'course_code', 'operator': 'exact', 'value': 'COMS1018'}],
                        'group': {'by': ['gender'], 'yield': [{'name': 'count', 'via': 'count', 'from': 'gender'}],
                                  'distinctGrouping': 'false', 'removeDuplicateCountings': 'duplicate'}}]}
        )
        self.assertEqual(response.status_code, 415)
