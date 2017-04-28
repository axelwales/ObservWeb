from django.db import models


# Create your models here.
class DedicatedGroup(models.Model):
    label = models.CharField("MAC Address", unique=True, max_length=50, null=True)


class Location(models.Model):
    lat = models.FloatField('latitude')
    lng = models.FloatField('longitude')

    class Meta:
        unique_together = ("lat", "lng")


class TempAccessPoint(models.Model):
    bssid = models.CharField(unique=True, max_length=17)


class AccessPoint(models.Model):
    bssid = models.CharField(unique=True, max_length=18)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(DedicatedGroup, null=True, on_delete=models.SET_NULL)


class TempFingerprint(models.Model):
    temp_ap = models.ForeignKey(TempAccessPoint, db_index=True, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, db_index=True, null=True, on_delete=models.CASCADE)
    rssi = models.IntegerField(null=True)
    count = models.IntegerField(null=True)


class Fingerprint(models.Model):
    NORTH = "north"
    EAST = "east"
    WEST = "west"
    SOUTH = "south"
    DIRECTION_CHOICES = (
        (NORTH, "North"),
        (EAST, "East"),
        (WEST, "West"),
        (SOUTH, "South")
    )
    access_point = models.ForeignKey(AccessPoint, db_index=True, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, db_index=True, null=True, on_delete=models.CASCADE)
    rssi = models.IntegerField(null=True)
    direction = models.CharField(choices=DIRECTION_CHOICES, null=True, max_length=5)
