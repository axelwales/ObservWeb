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

    def replace_fingerprint_aps(self):
        tempAPs = TempAccessPoint.objects.all()
        for tap in tempAPs:
            access_point, created = AccessPoint.objects.get_or_create(bssid=tap.bssid)
            fingerprints = Fingerprint.objects.filter(access_point__bssid__contains=tap.bssid)
            for f in fingerprints:
                f.access_point = access_point
                f.save()
