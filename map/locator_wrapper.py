from map.models import Location, Fingerprint
from map.locator import Locator


class LocatorWrapper(object):

    def __init__(self, data):
        self.data = self.process_data(data["fingerprint_set"])
        self.fingerprints = self.process_fingerprints(self.data)
        self.bssids = set(self.data.keys()) | self.fingerprints['all_bssids']

    def process_data(self, data):
        result = dict()
        for ap in data:
            bssid = ap['bssid'][:16]
            if bssid not in result:
                result[bssid] = [ap['rssi']]
            else:
                result[bssid].append(ap['rssi'])
        for bssid in result:
            result[bssid] = sum(result[bssid]) / float(len(result[bssid]))
        return result

    def process_fingerprints(self, fingerprint_data):

        fingerprints = Fingerprint.objects \
            .filter(access_point__bssid__in=self.data.keys()) \
            .values_list('pk', flat=True)
        fingerprinted_locations = Location.objects \
            .filter(fingerprint__in=list(fingerprints)) \
            .distinct()
        locations = list(fingerprinted_locations)

        result = dict(all_bssids=set(), fingerprints=[])
        for l in locations:
            bssids = set()
            coords = (l.lat, l.lng)
            aps = dict()
            for fingerprint in l.fingerprint_set.all() \
                    .order_by('access_point__bssid') \
                    .values_list('access_point__bssid', 'rssi'):
                result['all_bssids'].add(fingerprint[0])
                bssids.add(fingerprint[0])
                aps[fingerprint[0]] = fingerprint[1]
            result['fingerprints'].append({'coords': coords, 'bssids': bssids, 'aps': aps})

        return result

    def get_estimate(self):

        in_vector = self.create_input_vector()
        source_vectors = self.create_source_vectors()

        locator = Locator()
        estimate = locator.get_location_estimate(in_vector, source_vectors, 4)

        result = {'lat': -1, 'lng': -1}
        if (len(estimate) > 0):
            result = {'lat':estimate[0], 'lng':estimate[1]}

        return result

    def create_input_vector(self):
        unmatched_bssids = self.bssids - self.fingerprints['all_bssids']
        missing_bssids = self.bssids - set(self.data.keys())
        temp_head = [(bssid, -100) for bssid in missing_bssids]
        temp_tail = []
        for bssid, rssi in self.data.items():
            pair = (bssid, rssi)
            if bssid not in unmatched_bssids:
                temp_head.append(pair)
            else:
                temp_tail.append(pair)
        temp_head.sort(key=lambda pair: pair[0])
        temp_tail.sort(key=lambda pair: pair[0])
        return [rssi for bssid, rssi in temp_head] \
            + [rssi for bssid, rssi in temp_tail]

    def create_source_vectors(self):
        result = []
        input_only_bssids = self.bssids - self.fingerprints['all_bssids']
        for fingerprint in self.fingerprints['fingerprints']:
            missing_bssids = self.bssids - fingerprint['bssids'] - input_only_bssids
            for bssid in missing_bssids:
                fingerprint['aps'][bssid] = -100
            temp_head = [item for item in fingerprint['aps'].items()]
            temp_tail = [(bssid, -100) for bssid in input_only_bssids]
            temp_head.sort(key=lambda pair: pair[0])
            temp_tail.sort(key=lambda pair: pair[0])
            result.append(
                [fingerprint['coords'][0], fingerprint['coords'][1]] +
                [ap[1] for ap in temp_head] +
                [ap[1] for ap in temp_tail]
            )
        return result

