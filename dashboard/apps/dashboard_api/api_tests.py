from django.test import Client


def test_api_queries(self):
    c = Client()

    response = c.post('/login/', {'username': 'john', 'password': 'smith'})
    response.status_code

    response = c.post('/login/', {'username': 'user', 'password': 'pass'})
    response.status_code

    #response = c.post('course_stats/query', {'chain': [{'group': {'by': ['calendar_instance_year'], 'distinctGrouping': 'true', 'removeDuplicateCountings': 'false'}}]})
    #response.content


    #response = c.post('school_info/query', {'chain': [{'group': {'by': ['faculty'], 'distinctGrouping': 'true', 'removeDuplicateCountings': 'false'}}]})
    #response.content

    #response = c.post('school_info/query', {'chain': [{'filter': [{'field': 'faculty', 'operator': 'exact', 'value': faculties}], 'group': {'by': ['school'], 'distinctGrouping': 'true','removeDuplicateCountings': 'false'}}]})
    #response.content

    #response = c.post('course_info/query', {'chain': [{'filter': [{'field': 'school', 'operator': 'exact', 'value': schools}], 'group': {'by': ['course_name'], 'distinctGrouping': 'true','removeDuplicateCountings': 'false'}}]})
    #response.content

    #response = c.post('course_stats/query', {'chain': [{'filter': [{'field': 'calendar_instance_year', 'operator': 'exact', 'value': years}, {'field': 'faculty', 'operator': 'exact', 'value': faculties},
    #{'field': 'school', 'operator': 'exact', 'value': schools}, {'field': 'course_code', 'operator': 'exact', 'value': courses}],
    #'group': {'by': ['groupBy'], 'yield': [{'name': 'count', 'via': 'count', 'from': 'groupBy'}], 'distinctGrouping': 'false', 'removeDuplicateCountings': 'duplicate'}}]})
    #response.content
