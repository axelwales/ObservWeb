from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from map.models import Location
from map.serializers import LocationFingerprintSerializer

def index(request):
    return render(request, 'index.html')

class FingerprintList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationFingerprintSerializer

class FingerprintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationFingerprintSerializer
