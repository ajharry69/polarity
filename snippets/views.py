from rest_framework import renderers, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from snippets.serializers import *
from .permissions import *


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all().order_by('first_name', 'last_name', 'username')
    serializer_class = UserSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        """
        Allow for the modification of how an instance save is managed, and handle any information
        that is implicit in the incoming request or requested URL e.g. in this scenario, owner(user)
        won't be part of the serialized representation but is instead a property of the incoming
        request
        """
        # The create() method of our serializer will now be passed an additional 'owner' field,
        # along with the validated data from the request
        serializer.save(owner=self.request.user)


@api_view(['GET'])
def api_root(request, format=None):
    """
    Not necessary if `ViewSet`(s) are being used! `ViewSet` registration by `Router` does it's work
    """
    from rest_framework.reverse import reverse
    return Response(
        {
            'users': reverse('user-list', request=request, format=format),
            'snippets': reverse('snippet-list', request=request, format=format),
        }
    )
