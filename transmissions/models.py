from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Frequency(models.Model):
    number = models.IntegerField(
        unique=True,
        help_text="Channel (frequency) number from 1 to 30 (1-30)",
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    name = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Short name for the frequency (e.g., 'Whisper', 'Static')",
    )
    description = models.TextField(
        blank=True, help_text="A longer description for the frequency channel."
    )

    class Meta:
        ordering = ["number"]
        verbose_name_plural = "Frequencies"  # Good practice for Django Admin

    def __str__(self):
        if self.name:
            return f"{self.number} - {self.name}"
        return str(self.number)


class Transmission(models.Model):
    frequency = models.ForeignKey(
        Frequency, on_delete=models.CASCADE, related_name="transmissions"
    )

    code = models.TextField(
        help_text="Raw transmission data (e.g., '2341424', 'SOS', 'VICTOR CHARLIE 7')"
    )

    transmission_type_choices = [
        ("numbers", "Numbers"),
        ("names", "Names"),
        ("mixed", "Mixed"),  # If you allow both in one code string
    ]
    transmission_type = models.CharField(
        max_length=20,
        choices=transmission_type_choices,
        default="numbers",
        help_text="How the code should be interpreted for TTS (e.g., 'one two three' or 'alpha bravo charlie')",
    )

    scheduled_time = models.DateTimeField(
        db_index=True,
        help_text="The exact UTC time when this transmission is scheduled to begin.",
    )
    duration_seconds = models.IntegerField(
        default=10,
        help_text="Estimated duration of the TTS audio in seconds. Used for tracking current transmissions.",
    )

    status_choices = [
        ("scheduled", "Scheduled"),  # Waiting for its turn
        ("transmitting", "Transmitting"),  # Currently playing on the frontend
        ("completed", "Completed"),  # Finished playing
        ("cancelled", "Cancelled"),  # Manually cancelled
        ("failed", "Failed"),  # E.g., TTS generation error
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default="scheduled",
        help_text="Current status of the transmission.",
    )

    # Optional: Who submitted it?
    # submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) # When the record was created in DB

    class Meta:
        ordering = ["scheduled_time"]  # Default ordering for transmissions
        verbose_name_plural = "Transmissions"

    def __str__(self):
        return f"Transmission '{self.code[:30]}...' on Freq {self.frequency.number} at {self.scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}"


class EncryptionKey(models.Model):
    key_value = models.CharField(
        max_length=255,
        unique=True,
        help_text="The actual key string (e.g., 'XRAY23DELTA' or a sequence of numbers)",
    )
    description = models.TextField(
        blank=True,
        help_text="Context or purpose of this key (e.g., 'Decryption key for 4.78 MHz messages on July 18th')",
    )
    # This might be tricky if the key is *part* of a transmission's code
    # If a key is just something *known* by the system or revealed *separately*
    # Then this field is for linking what transmission it *applies to*.
    # If the key itself IS the code for a specific transmission, you'd model that via `Transmission.code`
    # and maybe a specific `transmission_type='key_reveal'`.
    # Let's keep this as a general key registry.
    associated_transmission = models.OneToOneField(
        Transmission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="released_key",  # Changed related_name for clarity
        help_text="Optional: If this key was explicitly released as part of this transmission's payload.",
    )

    valid_from = models.DateTimeField(
        default=timezone.now,
        help_text="When this key becomes active or was first introduced.",
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key expires (optional, for time-limited keys).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls if the key is currently considered usable by the system/users.",
    )

    class Meta:
        ordering = ["-valid_from", "key_value"]  # Order by newest first
        verbose_name_plural = "Encryption Keys"

    def __str__(self):
        return self.key_value
