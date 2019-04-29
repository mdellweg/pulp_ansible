from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import detail_route

from pulpcore.plugin.serializers import (
    AsyncOperationResponseSerializer,
    RepositorySyncURLSerializer,
)
from pulpcore.plugin.tasking import enqueue_with_reservation
from pulpcore.plugin.viewsets import (
    ContentFilter,
    ContentViewSet,
    OperationPostponedResponse,
    PublicationViewSet,
    RemoteViewSet
)

from . import tasks
from .models import AnsiblePublication, AnsibleRemote, AnsibleRole
from .serializers import (
    AnsiblePublicationSerializer,
    AnsibleRemoteSerializer,
    AnsibleRoleSerializer
)


class AnsibleRoleFilter(ContentFilter):
    """
    FilterSet for Ansible Role Versions.
    """

    class Meta:
        model = AnsibleRole
        fields = [
            'name',
            'namespace',
            'version',
        ]


class AnsibleRoleViewSet(ContentViewSet):
    """
    ViewSet for Ansible Role versions.
    """

    endpoint_name = 'roles'
    queryset = AnsibleRole.objects.all()
    serializer_class = AnsibleRoleSerializer
    filterset_class = AnsibleRoleFilter


class AnsibleRemoteViewSet(RemoteViewSet):
    """
    ViewSet for Ansible Remotes.
    """

    endpoint_name = 'ansible'
    queryset = AnsibleRemote.objects.all()
    serializer_class = AnsibleRemoteSerializer

    @swagger_auto_schema(
        operation_description="Trigger an asynchronous task to sync Ansible content.",
        responses={202: AsyncOperationResponseSerializer}
    )
    @detail_route(methods=('post',), serializer_class=RepositorySyncURLSerializer)
    def sync(self, request, pk):
        """
        Dispatches a sync task.
        """
        remote = self.get_object()
        serializer = RepositorySyncURLSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        repository = serializer.validated_data.get('repository')
        mirror = serializer.validated_data.get('mirror', False)
        result = enqueue_with_reservation(
            tasks.synchronize,
            [repository, remote],
            kwargs={
                'remote_pk': remote.pk,
                'repository_pk': repository.pk,
                'mirror': mirror,
            }
        )
        return OperationPostponedResponse(result, request)


class AnsiblePublicationsViewSet(PublicationViewSet):
    """
    ViewSet for Ansible Publications.
    """

    endpoint_name = 'ansible'
    queryset = AnsiblePublication.objects.all()
    serializer_class = AnsiblePublicationSerializer

    @swagger_auto_schema(
        operation_description="Trigger an asynchronous task to create a new Ansible "
                              "content publication.",
        responses={202: AsyncOperationResponseSerializer}
    )
    def create(self, request):
        """
        Queues a task that publishes a new Ansible Publication.

        Either the ``repository`` or the ``repository_version`` fields can
        be provided but not both at the same time.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repository_version = serializer.validated_data.get('repository_version')

        result = enqueue_with_reservation(
            tasks.publish, [repository_version.repository],
            kwargs={
                'repository_version_pk': str(repository_version.pk)
            }
        )
        return OperationPostponedResponse(result, request)
