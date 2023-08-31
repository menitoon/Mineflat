import random
import math
import os


class PerlinNoise:

    __slots__ = "size", "gradient_vectors", "SEED"

    def __init__(self, size=(20, 20)):
        self.size = size  # taille d'un carré (20x20 par défaut)
        self.gradient_vectors = {}
        self.SEED = 0.0
        
  
        #if os.path.isfile("Chunks/seed.txt"):
        #    self.SEED = float(open("Chunks/seed.txt", "r").read())
          
        #else:
        #  seed_file = open("Chunks/seed.txt", "w")
        #  self.SEED = random.random()
        #  seed_file.write(str(self.SEED))
        # seed_file.close()
          

    def smoothstep(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
      

    def get_chunk_position(self, position : list):
        # donne la position du chunk dans laquelle cette celle-ci se trouve genre (30, 40) -> (0.5, 0.0) si la taille est 20x20
        return (position[0] % self.size[0] / self.size[0], position[1] % self.size[1] / self.size[1])

    def get_chunk_id(self, position : list):
        # donne dans quel chunk la position se trouve (30, 40) -> (1, 2)
        return (math.floor(position[0] / self.size[0]), math.floor(position[1] / self.size[1]))

    def set_seed(self, position):
        # met une seed unique pour obtenir toujours le même gradient a telle position
        random.seed(str((position[0] * 31 + position[1] * 37) + self.SEED))

    def get_gradient(self, position):
        # donne un gradient qui sera toujours le même pour une position donnée (si la seed de base est la même)
        self.set_seed(position)
        angle = random.uniform(0, math.pi * 2)
        return (math.cos(angle), math.sin(angle))

    def get_vector(self, vector, corner):
        # donne la direction d'un vecteur par rapport à un coin
        dist = (vector[0] - corner[0], vector[1] - corner[1])
        magnitude = math.sqrt(dist[0] ** 2 + dist[1] ** 2)  # obtient la magnitude d'un vecteur pour le normaliser
        if magnitude == 0:
            return (0, 0)
        # retourne la direction normalisée
        return (dist[0] / magnitude, dist[1] / magnitude)

    def lerp(self, a, b, t):
        # interpolation linéaire
        return a + (b - a) * t

    def get_dot_product(self, vec_one, vec_two):
        # produit scalaire
        return vec_one[0] * vec_two[0] + vec_one[1] * vec_two[1]

    def reset_gradient_cache(self):
        self.gradient_vectors = {}

    def get_perlin_at(self, position):
        # donne la valeur d'un pixel à une position donnée
        
        fract = self.get_chunk_position(position)  # donne les coordonnées dans le carré genre (0.5, 0.5)
        chunk = self.get_chunk_id(position)  # donne dans quel chunk la position se trouve

        # les coins
        x0 = chunk  # haut-gauche
        x1 = (chunk[0] + 1, chunk[1])  # haut-droite
        y0 = (chunk[0], chunk[1] + 1)  # bas-gauche
        y1 = (chunk[0] + 1, chunk[1] + 1)  # bas-droite

        # on calcule les gradients
        gradient_a = self.gradient_vectors.get(x0)
        gradient_b = self.gradient_vectors.get(x1)  # HAUT droite
        gradient_c = self.gradient_vectors.get(y0)
        gradient_d = self.gradient_vectors.get(y1)

        if gradient_a is None:
            gradient_a = self.get_gradient(x0)  # HAUT gauche
            self.gradient_vectors[x0] = gradient_a
        if gradient_b is None:
            gradient_b = self.get_gradient(x1)  # HAUT droite
            self.gradient_vectors[x1] = gradient_b
        if gradient_c is None:
            gradient_c = self.get_gradient(y0)  # BAS gauche
            self.gradient_vectors[y0] = gradient_c
        if gradient_d is None:
            gradient_d = self.get_gradient(y1)  # BAS droite
            self.gradient_vectors[y1] = gradient_d

        # les vecteurs qui s'orientent vers les coins
        vector_a = fract
        vector_b = (fract[0] - 1, fract[1])
        vector_c = (fract[0], fract[1] - 1)
        vector_d = (fract[0] - 1, fract[1] - 1 )



        # on calcule les produits scalaires
        dot_a = self.get_dot_product(vector_a, gradient_a)
        dot_b = self.get_dot_product(vector_b, gradient_b)
        dot_c = self.get_dot_product(vector_c, gradient_c)
        dot_d = self.get_dot_product(vector_d, gradient_d)

        # on fait une interpolation entre les côtés de x (haut et bas)

        u = self.smoothstep(fract[0])
        v = self.smoothstep(fract[1])

        x_up = self.lerp(dot_a, dot_b, u)
        x_down = self.lerp(dot_c, dot_d,u)

        # et pour finir on fait une interpolation entre ces deux côtés
        value = self.lerp(x_up, x_down, v)

        return value


