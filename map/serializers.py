from rest_framework import serializers
from map.models import Location, Fingerprint, AccessPoint

class FingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer(read_only=True)
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = Fingerprint
        fields = ('id', 'location', 'access_point','rssi')

class NestedFingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer(read_only=True)

    class Meta:
        model = Fingerprint
        fields = ('id', 'access_point','rssi')

class LocationFingerprintSerializer(serializers.ModelSerializer):
	fingerprints = NestedFingerprintSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng', 'fingerprints')

class NestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng')

class AccessPointSerializer(serializers.ModelSerializer):
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = AccessPoint
        fields = ('bssid', 'location')

class NestedAccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = ('bssid')