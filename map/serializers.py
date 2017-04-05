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

    def create(self, validated_data):
        fingerprints_data = validated_data.pop('fingerprints')
        location = Location.objects.create(**validated_data)
        for fingerprint_data in fingerprints_data:
            access_point_data = fingerprint_data.pop('access_point')
            AccessPoint.objects.create(**access_point_data)
            Fingerprint.objects.create(location=location, **fingerprint_data)
        return location

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