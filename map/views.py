from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from map.models import Location
from map.serializers import LocationFingerprintSerializer
from map.locator_wrapper import LocatorWrapper


def index(request):
    return render(request, 'index.html')


class FingerprintList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationFingerprintSerializer


class FingerprintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationFingerprintSerializer


class LocationEstimate(APIView):
    """
    View to estimate location.
    """

    parser_classes = (JSONParser,)

    def post(self, request):
        """
        Return a location estimate.
        """
        estimate = LocatorWrapper.get_estimate(request.data)
        return Response(estimate)
