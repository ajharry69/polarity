from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root(request, format=None):
    from rest_framework.reverse import reverse
    from rest_framework.response import Response
    return Response(
        {
            'quickstart': reverse('quickstart:', request=request, format=format),
            'snippets': reverse('snippets', request=request, format=format),
        }
    )
