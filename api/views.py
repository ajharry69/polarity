from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root(request, format=None):
    from rest_framework.reverse import reverse
    from rest_framework.response import Response
    return Response(
        {
            'quickstart': reverse('quickstart:index', request=request, format=format),
            'snippets': reverse('snippets:index', request=request, format=format),
        }
    )
