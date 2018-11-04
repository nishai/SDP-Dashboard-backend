from django.test import Client

c = Client()

response = c.post('/login/', {'username': 'john', 'password': 'smith'})
response.status_code

response = c.post('course_stats/query', {'chain': [{'group': {'by': ['calendar_instance_year']}}]})
response.content

response = c.post('school_info/query', {'chain': [{'group': {'by': ['faculty']}}]})
response.content

#response = c.post('school_info/query', {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact',
#'value': faculties}]}]})
#response.content

#response = c.post('course_info/query', {'chain': [{'filter': [{'field': 'school', 'operator': 'exact',
#'value': schools}]}]})
#response.content

#response = c.post('course_stats/query', {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact',
#'value': faculties}], 'group': {'by': ['groupBy'], 'yield': [{'name': 'count', 'via': 'count', 'from': 'groupBy'}]}}]})
