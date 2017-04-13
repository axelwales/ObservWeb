from django.db import models

# Create your models here.
class Location(models.Model):
    lat = models.FloatField('latitude')
    lng = models.FloatField('longitude')
    class Meta:
       unique_together = ("lat", "lng")


class AccessPoint(models.Model):
    bssid = models.CharField("MAC Address", unique=True, max_length=18)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)

class Fingerprint(models.Model):
    access_point = models.ForeignKey(AccessPoint, null=True, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, db_index=True, null=True, on_delete=models.CASCADE)
    rssi = models.IntegerField(null=True)