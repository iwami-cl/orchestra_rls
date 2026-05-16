from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from schedule.models import Attendance, Schedule, ScheduleLog
from .serializer import AttendanceForScheduleSerializer, ScheduleLogSerializer, ScheduleSerializer
import datetime
from django.core.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializer import AttendanceCreateUpdateSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from schedule.models import Schedule
from music.models import Music



class ScheduleListView(ListAPIView):
    queryset = Schedule.objects.all().order_by("date", "start")
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self, **kwargs):
        month = self.request.GET.get("m", None)
        year = int(self.request.GET.get("y", datetime.datetime.now().year))
        query = super().get_queryset()

        if month is None:
            filtered = query.filter(date__year=year)
        else:
            filtered = query.filter(date__year=year, date__month=int(month))
        return filtered


class AttendanceCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AttendanceCreateUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # If the serializer did not include a user, set it to the authenticated user.
        if "user" not in serializer.validated_data:
            attendance = serializer.save(user=request.user)
        else:
            # Prevent creating attendance for another user
            if serializer.validated_data.get("user") != request.user:
                raise ValidationError("You cannot create attendance for another user.")
            attendance = serializer.save()

        return Response(AttendanceCreateUpdateSerializer(attendance, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class GetAttencanceForScheduleAPIView(RetrieveAPIView):
    serializer_class = AttendanceForScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        music_id = self.request.GET.get("music_id", None)
        schedule_id = self.kwargs.get("pk", None)
        return {
            "schedule_id": schedule_id,
            "music_id": music_id
        }


class ScheduleLogListView(ListAPIView):
    queryset = ScheduleLog.objects.all().order_by("date", "start")
    serializer_class = ScheduleLogSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self, **kwargs):
        month = self.request.GET.get("m", None)
        year = int(self.request.GET.get("y", datetime.datetime.now().year))
        query = super().get_queryset()

        if month is None:
            filtered = query.filter(date__year=year)
        else:
            filtered = query.filter(date__year=year, date__month=int(month))
        return filtered
