from map.models import AccessPoint, Fingerprint, TempAccessPoint, TempFingerprint, Location
from django.db.models import Avg, Count
from django.db.utils import IntegrityError


class Massager(object):

    def __init__(self):
        pass

    def create_truncated_aps(self):
        aps = AccessPoint.objects.all()
        for ap in aps:
            bssid = ap.bssid[:len(ap.bssid) - 1]
            try:
                TempAccessPoint.objects.create(bssid=bssid)
            except IntegrityError:
                pass


    def average_existing_fingerprints(self):
        tempAPs = TempAccessPoint.objects.all()
        for tap in tempAPs:
            fingerprints = Fingerprint.objects.filter(access_point__bssid__contains=tap.bssid) \
                .values('location') \
                .annotate(rssi=Avg('rssi'))
            for f in fingerprints:
                location = Location.objects.get(pk=f['location'])
                TempFingerprint.objects.create(temp_ap=tap, location=location, rssi=f['rssi'])

    def avg_count(self):
        tempAPs = TempAccessPoint.objects.all()
        for tap in tempAPs:
            fingerprints = Fingerprint.objects.filter(access_point__bssid__contains=tap.bssid) \
                .values('location') \
                .annotate(count=Count('location'))
            for f in fingerprints:
                location = Location.objects.get(pk=f['location'])
                tf = TempFingerprint.objects.get(temp_ap=tap, location=location)
                tf.count = f['count']
                tf.save()


    def replace_aps(self):
        tempAPs = TempAccessPoint.objects.all()
        for tap in tempAPs:
            AccessPoint.objects.create(bssid=tap.bssid)

    def replace_fingerprints(self):
        fingerprints = TempFingerprint.objects.all()
        for f in fingerprints:
            access_point = AccessPoint.objects.get(bssid=f.temp_ap.bssid)
            Fingerprint.objects.create(
                location=f.location,
                access_point=access_point,
                rssi=f.rssi,
                count=f.count,
                direction=f.NORTH
            )
