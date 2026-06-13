from rest_framework.views import APIView, Response


class GetNotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "This is a placeholder for the GetNotificationsView."})