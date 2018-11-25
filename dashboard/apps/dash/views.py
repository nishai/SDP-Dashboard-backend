import jsonschema
from django.http import JsonResponse
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from dashboard.apps.dash.serializers import *
from dashboard.apps.wits.parser.schema import Schema


# REPORT_LAYOUT_SCHEMA = Schema.array(Schema.object({
#     'i': Schema.str,
#     'x': Schema.int,
#     'y': Schema.int,
#     'w': Schema.int,
#     'h': Schema.int,
#     'moved': Schema.any(Schema.null, Schema.bool),
# }, not_required=['moved'], anything=True))
#
# CHART_META_SCHEMA = Schema.object({
#     'chartType': Schema.str,
#     'template': Schema.str,
#     'subsets': Schema.array(Schema.object(anything=True), min_size=0),
# }, anything=True)
#
# # User Data
# # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
#
# USER_DATA_SCHEMA = Schema.object({
#     "defaultReport": Schema.any(Schema.null, Schema.str),
#     "reports": Schema.array(Schema.object({
#         'name': Schema.str,
#         'id': Schema.str,
#         'charts': Schema.object(anything=True),  # TODO: how to define keys and values
#         'layout': REPORT_LAYOUT_SCHEMA
#     }, anything=True), min_size=0),
# }, anything=True)

USER_DATA_SCHEMA = Schema.object({
    "defaultReport": Schema.any(Schema.null, Schema.str),
    "reports": Schema.object(anything=True),
}, anything=True)

# ========================================================================= #
# USER VIEWS                                                                #
# ========================================================================= #


@api_view(['GET', 'PATCH'])
def profile_data_view(request):
    profile = request.user.profile
    if request.method == 'PATCH':
        jsonschema.validate(request.data, USER_DATA_SCHEMA)
        profile.rawData = request.data
        profile.save()
    return JsonResponse(profile.rawData)


@api_view(['GET'])
def profile_view(request):
    return JsonResponse(ProfileSerializer(request.user.profile).data)


@api_view(['GET'])
def user_view(request):
    return JsonResponse(UserSerializer(request.user).data)



# ========================================================================= #
# UTIL VIEWS                                                                #
# ========================================================================= #

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def status_view(request):
    """
    Used to check if the server is alive.
    """
    return JsonResponse({'status': 'active'})
