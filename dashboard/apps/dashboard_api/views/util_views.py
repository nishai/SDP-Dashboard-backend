from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny


# ========================================================================= #
# UTIL VIEWS                                                                #
# ========================================================================= #


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def status_view(request):
    """
    Used to check if the server is alive.
    """
    return JsonResponse({'status': 'active'})
