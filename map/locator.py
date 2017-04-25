from math import sqrt

class Locator(object):

    def __init__(self):
        pass

    def get_location_estimate(self, target_vector, source_vectors, num_neighbors):
        neighbors = self.get_k_nearest_neighbors(target_vector, source_vectors, num_neighbors)
        return self.get_weighted_average([[n[0], n[1]] for n in neighbors])

    def get_k_nearest_neighbors(self, target_vector, source_vectors, k):
        neighbors = [[v[0], v[1], self.calc_euclidian_distance(v[2:], target_vector)] for v in source_vectors]
        neighbors.sort(key=lambda x: x[2])
        return neighbors[:k]

    def calc_euclidian_distance(self, v1, v2):
        if (len(v1) != len(v2)):
            return 'error'
        distance = sum([((v1i - v2i)**2) for v1i, v2i in zip(v1, v2)])
        return sqrt(distance)

    def get_weighted_average(self, coord_vectors):
        divisor = 2**len(coord_vectors) - 1
        weighted_coord_vectors = [[vij * (2 ** (len(coord_vectors) - i - 1)) / divisor for vij in vi] for i, vi in enumerate(coord_vectors)]
        return list(map(sum, zip(*weighted_coord_vectors)))
