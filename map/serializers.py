from rest_framework import serializers
from map.models import Location, Fingerprint, AccessPoint, DedicatedGroup

class NestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng')
        validators = []

class NestedAccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = ('bssid',)
        validators = []
        extra_kwargs = {
            'bssid': {'validators': []},
        }

class NestedFingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer()

    class Meta:
        model = Fingerprint
        fields = ('id', 'access_point','rssi')
        validators = []
        extra_kwargs = {
            'access_point': {'validators': []},
        }

class AccessPointSerializer(serializers.ModelSerializer):
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = AccessPoint
        fields = ('bssid', 'location')
        validators = []
        extra_kwargs = {
            'location': {'validators': []},
        }

class DedicatedGroupSerializer(serializers.ModelSerializer):
    accesspoint_set = NestedAccessPointSerializer(many=True)
    label = serializers.CharField(max_length=50)

    def create(self, validated_data):
        access_point_set_data = validated_data.pop('accesspoint_set')
        group, created = DedicatedGroup.objects.get_or_create(**validated_data)
        for access_point_data in access_point_set_data:
            access_point, created = AccessPoint.objects.get_or_create(**access_point_data)
            access_point.group = group
            access_point.save()
        return group

    class Meta:
        model = DedicatedGroup
        fields = ('label', 'accesspoint_set')
        validators = []
        extra_kwargs = {
            'accesspoint_set': {'validators': []},
        }

class FingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer(read_only=True)
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = Fingerprint
        fields = ('id', 'location', 'access_point','rssi')
        validators = []
        extra_kwargs = {
            'location': {'validators': []},
            'access_point': {'validators': []},
        }

class LocationFingerprintSerializer(serializers.ModelSerializer):
    fingerprint_set = NestedFingerprintSerializer(many=True)

    def create(self, validated_data):
        fingerprint_set_data = validated_data.pop('fingerprint_set')
        location, created = Location.objects.get_or_create(**validated_data)
        for fingerprint_data in fingerprint_set_data:
            access_point_data = fingerprint_data.pop('access_point')
            access_point, created = AccessPoint.objects.get_or_create(**access_point_data)
            fingerprint = Fingerprint.objects.create(access_point = access_point, location=location, **fingerprint_data)
        return location

    def update(self, instance, validated_data):

        instance.lat = validated_data['lat']
        instance.lng = validated_data['lng']
        instance.save()

        fingerprint_ids = [fingerprint['id'] for fingerprint in validated_data['fingerprint_set_data']]
        for fingerprint in instance.fingerprint_set:
            if fingerprint.id not in fingerprint_ids:
                fingerprint.delete()

        for fingerprint_data in validated_data['fingerprint_set_data']:
            access_point_data = fingerprint_data.pop('access_point')
            access_point, created = AccessPoint.objects.get_or_create(**access_point_data)
            fingerprint = Fingerprint(access_point=access_point, location=instance, **fingerprint_data)
            fingerprint.save()

        return instance

    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng', 'fingerprint_set')
        validators = []
        extra_kwargs = {
            'fingerprint_set': {'validators': []},
        }
