# TransmissionPy/api/serializers.py

from rest_framework import serializers
from .models import Frequency, Transmission, EncryptionKey # Import your models

class FrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Frequency
        fields = ['id', 'number', 'name', 'description']

class EncryptionKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptionKey
        fields = ['id', 'key_value', 'description', 'valid_from', 'valid_until', 'is_active']
        # If you want to expose the associated_transmission ID:
        # fields = ['id', 'key_value', 'description', 'valid_from', 'valid_until', 'is_active', 'associated_transmission']


class TransmissionSerializer(serializers.ModelSerializer):
    # Nested serializer to include frequency details directly in the transmission data
    # We use read_only=True because the frontend sends frequency_number, not a Frequency object
    frequency = FrequencySerializer(read_only=True)
    # If you linked EncryptionKey to Transmission as `released_key`
    # released_key = EncryptionKeySerializer(read_only=True)


    class Meta:
        model = Transmission
        # Important: 'frequency' here refers to the *serialized* frequency object for GET requests.
        # For POST/PUT/PATCH, you'll handle `frequency_number` in the view, not here.
        fields = [
            'id', 'frequency', 'code', 'transmission_type',
            'scheduled_time', 'duration_seconds', 'status',
            # 'released_key' # Uncomment if you enabled this in Transmission model and want it in the API output
        ]
        read_only_fields = ['status', 'scheduled_time', 'duration_seconds']
        # ^ Make scheduled_time and duration_seconds read-only here
        # because they are calculated/set by the backend in `perform_create`

# --- For the main data endpoint (StationDataView) ---
class FullStationDataSerializer(serializers.Serializer):
    frequencies = FrequencySerializer(many=True)
    scheduled_transmissions = TransmissionSerializer(many=True)
    current_transmissions = TransmissionSerializer(many=True)
    encryption_keys = EncryptionKeySerializer(many=True) # General list of active keys