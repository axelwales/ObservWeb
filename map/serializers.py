from rest_framework import serializers
from map.models import Location, Fingerprint, AccessPoint

class NestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng')

class NestedAccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = ('bssid',)

class NestedFingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer()

    class Meta:
        model = Fingerprint
        fields = ('id', 'access_point','rssi')

class AccessPointSerializer(serializers.ModelSerializer):
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = AccessPoint
        fields = ('bssid', 'location')

class FingerprintSerializer(serializers.ModelSerializer):
    access_point = NestedAccessPointSerializer(read_only=True)
    location = NestedLocationSerializer(read_only=True)

    class Meta:
        model = Fingerprint
        fields = ('id', 'location', 'access_point','rssi')

class LocationFingerprintSerializer(serializers.ModelSerializer):
    fingerprint_set = NestedFingerprintSerializer(many=True)

    def create(self, validated_data):
        fingerprint_set_data = validated_data.pop('fingerprint_set')
        location = Location.objects.create(lat=validated_data['lat'],lng=validated_data['lng'])
        for fingerprint_data in fingerprint_set_data:
            access_point_data = fingerprint_data.pop('access_point')
            access_point = None
            try:
                access_point = AccessPoint.objects.get(bssid__exact=access_point_data['bssid'])
            except AccessPoint.DoesNotExist:
                access_point = AccessPoint.objects.create(**access_point_data)
            fingerprint = Fingerprint(access_point=access_point, location=instance, rssi=fingerprint_data['rssi'])
            fingerprint.save()
            location.objects.fingerprint_set.add(fingerprint)
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
            try:
                access_point = AccessPoint.objects.get(pk=access_point_data['bssid'])
            except AccessPoint.DoesNotExist:
                access_point = AccessPoint.objects.create(**access_point_data)
            fingerprint = Fingerprint(id=fingerprint_data['id'], access_point=access_point, location=instance, rssi=fingerprint_data['rssi'])
            fingerprint.save()

        return instance

    class Meta:
        model = Location
        fields = ('id', 'lat', 'lng', 'fingerprint_set')
