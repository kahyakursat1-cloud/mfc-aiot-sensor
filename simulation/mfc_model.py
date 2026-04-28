"""
MFC Basit Enerji Üretim Modeli
Gerçek sistemi doğrulamadan önce dijital ikizi test etmek için.
"""

import random


class MFC:
    def __init__(self, generation_rate: float = 0.0005):
        """
        generation_rate: Joule/adım — varsayılan ~150 µW @ 10 dk döngü
        """
        self.generation_rate = generation_rate

    def generate_energy(self) -> float:
        """Bir adımda üretilen enerji (J). ±%20 rastgele gürültü ekler."""
        noise = random.uniform(-0.0001, 0.0001)
        return max(0.0, self.generation_rate + noise)
