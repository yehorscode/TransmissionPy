# TransmissionPy/api/urls.py

from django.urls import path
# Make sure your views are correctly imported here:
from .views import StationDataView, TransmissionSubmitView

urlpatterns = [
    # This defines the 'station_data/' part after '/api/'
    path('station_data/', StationDataView.as_view(), name='station_data'),
    path('submit_transmission/', TransmissionSubmitView.as_view(), name='submit_transmission'),
    # You might have other paths here later
]