from django.test import Client


def test_api_queries(self):
    c = Client()
    response = c.post('/login/', {'username': 'john', 'password': 'smith'})
    response.status_code
    self.assertEqual(response.status_code,400)

    response = c.post('/login/', {'username': 'user', 'password': 'pass'})
    response.status_code
    self.assertEqual(response.status_code, 200)

    # response = c.post(
    #     'course_stats/query',
    #     {'chain': [{'group': {'by': ['calendar_instance_year'], 'distinctGrouping': 'true',
    #                           'removeDuplicateCountings': 'false'}}]})
    # response.content
    # self.assertEqual(response.status_code,200)
    #
    # response = c.post(
    #     'school_info/query',
    #     {'chain': [{'group': {'by': ['faculty'], 'distinctGrouping': 'true',
    #                           'removeDuplicateCountings': 'false'}}]})
    # response.content
    # self.assertEqual(response.status_code,200)
    #
    # response = c.post(
    #     'school_info/query',
    #     {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact', 'value': 'Science'}],
    #                 'group': {'by': ['school'], 'distinctGrouping': 'true',
    #                           'removeDuplicateCountings': 'false'}}]})
    # response.content
    # self.assertEqual(response.status_code,200)
    #
    # response = c.post(
    #     'course_info/query',
    #     {'chain': [{'filter': [{'field': 'school', 'operator': 'exact',
    #                             'value': 'Computer Science and Applied Mathematics'}],
    #                 'group': {'by': ['course_name'], 'distinctGrouping': 'true',
    #                           'removeDuplicateCountings': 'false'}}]})
    # response.content
    # self.assertEqual(response.status_code,200)
    #
    # response = c.post(
    #     'course_stats/query',
    #     {'chain': [{'filter': [{'field': 'calendar_instance_year', 'operator': 'exact', 'value': '2015'},
    #                            {'field': 'faculty', 'operator': 'exact', 'value': 'Science'},
    #                            {'field': 'school', 'operator': 'exact',
    #                             'value': 'Computer Science and Applied Mathematics'},
    #                            {'field': 'course_code', 'operator': 'exact', 'value': 'COMS1018'}],
    #                 'group': {'by': ['gender'], 'yield': [{'name': 'count', 'via': 'count', 'from': 'gender['}],
    #                           'distinctGrouping': 'false', 'removeDuplicateCountings': 'duplicate'}}]})
    # response.content
    # self.assertEqual(response.status_code,200)
