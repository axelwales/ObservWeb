from map.models import Location
from map.locator import Locator


class LocatorWrapper(object):

    def __init__(self):
        pass

    def get_estimate(self, target_fingerprint_data):

        fingerprint_data = target_fingerprint_data["fingerprint_set"]

        raw_fingerprints = self.get_raw_fingerprints(fingerprint_data)

        averaged_fingerprints = \
            self.get_averaged_fingerprints(raw_fingerprints)

        target_bssid_set = set(self.get_bssids(fingerprint_data))
        bssid_set = set(
            [ap[0] for ap in [loc[1] for loc in averaged_fingerprints]]
        )
        bssid_set = target_bssid_set | bssid_set

        bssids_missing = bssid_set - target_bssid_set
        target_full_data = [
            (fingerprint['bssid'], int(fingerprint['rssi']))
            for fingerprint in fingerprint_data
        ] + [(bssid, -100) for bssid in bssids_missing]

        target_full_data.sort(key=lambda ap: ap[0])
        t_vector = map(lambda ap: ap[1], target_full_data)

        for fingerprint in averaged_fingerprints:
            bssids_missing = bssid_set \
                - set([bssid for bssid, rssi in fingerprint[1]])
            fingerprint[1] = fingerprint[1] \
                + [(bssid, -100) for bssid in bssids_missing]
            fingerprint[1].sort(key=lambda ap: ap[0])

        s_vectors = [
            [f[0][0], f[0][1], *map(lambda ap: ap[1], f[1])]
            for f in averaged_fingerprints
        ]

        locator = Locator()
        estimate = locator.get_location_estimate(t_vector, s_vectors, 4)

        return {'lat': estimate[0], 'lng': estimate[1]}

    def get_raw_fingerprints(self, fingerprint_data):

        bssids = self.get_bssids(fingerprint_data)

        fingerprinted_locations = Location.objects \
            .filter(fingerprint__access_point__bssid__in=bssids)

        return [
            [
                (l.lat, l.lng),
                [
                    (fingerprint.access_point.bssid, fingerprint.rssi)
                    for fingerprint in l.fingerprint_set
                ]
            ]
            for l in fingerprinted_locations
        ]

    def get_bssids(self, fingerprint_data):
        return [
            fingerprint['bssid']
            for fingerprint
            in fingerprint_data
        ]

    def get_averaged_fingerprints(self, raw_fingerprints):

        averaged_fingerprints = []
        for fingerprint in raw_fingerprints:
            fingerprint[1].sort(key=lambda ap: ap[0])
            bssid = fingerprint[1][0][0]
            sum = 0
            count = 0
            averaged_fingerprint = [fingerprint[0], []]
            for ap in fingerprint[1]:
                if (bssid != ap[0]):
                    averaged_fingerprint[1].append(
                        (bssid, float(sum) / float(count))
                    )
                    bssid = ap
                    sum = 0
                    count = 0
                sum += ap[1]
                count += 1
            averaged_fingerprints.append(averaged_fingerprint)
        return averaged_fingerprints
