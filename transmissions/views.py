# TransmissionPy/api/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import Frequency, Transmission, EncryptionKey
from .serializers import (
    FrequencySerializer,
    TransmissionSerializer,
    EncryptionKeySerializer,
    FullStationDataSerializer
)

class StationDataView(APIView):
    """
    Returns all frequencies, scheduled transmissions, current transmissions,
    and active encryption keys in one consolidated response.
    """
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        # Define your lookahead window for scheduled transmissions (e.g., next 24 hours)
        lookahead_time = now + timedelta(hours=24)

        # Frequencies
        frequencies = Frequency.objects.all()

        # Scheduled Transmissions (upcoming within the lookahead window)
        # Exclude 'completed' and 'cancelled' status
        scheduled_transmissions = Transmission.objects.filter(
            scheduled_time__gt=now, # Greater than current time
            scheduled_time__lte=lookahead_time, # Less than or equal to lookahead time
        ).exclude(status__in=['completed', 'cancelled', 'failed']).order_by('scheduled_time')

        # Current Transmissions (active right now)
        current_transmissions = Transmission.objects.filter(
            scheduled_time__lte=now, # Started by now
        ).exclude(status__in=['completed', 'cancelled', 'failed'])

        # Filter current_transmissions to only those actively "playing"
        current_transmissions_filtered = []
        for trans in current_transmissions:
            # Add a small buffer (e.g., 5 seconds) to duration for currently playing
            if trans.scheduled_time + timedelta(seconds=trans.duration_seconds + 5) > now:
                current_transmissions_filtered.append(trans)


        # Active Encryption Keys
        active_keys = EncryptionKey.objects.filter(
            is_active=True,
            valid_from__lte=now
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=now)
        )


        # Serialize all data
        data = {
            'frequencies': FrequencySerializer(frequencies, many=True).data,
            'scheduled_transmissions': TransmissionSerializer(scheduled_transmissions, many=True).data,
            'current_transmissions': TransmissionSerializer(current_transmissions_filtered, many=True).data,
            'encryption_keys': EncryptionKeySerializer(active_keys, many=True).data,
        }

        return Response(data)

class TransmissionSubmitView(generics.CreateAPIView):
    """
    Allows users to submit new transmission codes.
    """
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer

    def perform_create(self, serializer):
        frequency_number = self.request.data.get('frequency_number')
        code = self.request.data.get('code')
        transmission_type = self.request.data.get('transmission_type', 'numbers')

        if not frequency_number:
            raise serializers.ValidationError({"frequency_number": "This field is required."})

        try:
            frequency = Frequency.objects.get(number=frequency_number)
        except Frequency.DoesNotExist:
            raise serializers.ValidationError({"frequency_number": "Invalid frequency number."})

        # Calculate scheduled_time: e.g., 5 minutes from now + current offset
        # This ensures transmissions are scheduled a bit into the future from current time
        # For testing and a simple simulator, 5 minutes from now is fine.
        scheduled_time = timezone.now() + timedelta(minutes=5)
        duration_seconds = max(10, len(code) // 2) # Crude estimate

        serializer.save(
            frequency=frequency,
            scheduled_time=scheduled_time,
            duration_seconds=duration_seconds,
            status='scheduled'
        )