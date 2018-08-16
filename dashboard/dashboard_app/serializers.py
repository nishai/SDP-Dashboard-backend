from .models import Enrolment
from rest_framework import serializers

class EnrolmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Enrolment
        fields = ('program_code', 'registration_status', 'course_attempt_status', 'student_number',
        'last_name', 'first_name', 'calendar_instance_year', 'course_code', 'course_title', 'nqf_credit',
        'supp_mark', 'final_mark', 'final_grade')
