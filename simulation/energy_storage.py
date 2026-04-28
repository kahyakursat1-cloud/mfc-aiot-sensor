"""
Süper Kapasitör Enerji Depolama Modeli
"""


class SuperCapacitor:
    def __init__(self, capacity: float = 1.0):
        """
        capacity: Joule cinsinden maksimum depolama kapasitesi
        1F @ 2.7V → E = 0.5 × 1 × 2.7² ≈ 3.6 J
        """
        self.capacity = capacity
        self.energy = 0.0

    def charge(self, amount: float):
        """Enerji ekle, kapasiteyi aşma."""
        self.energy = min(self.capacity, self.energy + amount)

    def consume(self, amount: float) -> bool:
        """
        Enerji tüket.
        Yeterli enerji varsa tüketir ve True döner.
        Yoksa False döner (iletim iptal sinyali).
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    @property
    def soc(self) -> float:
        """State of Charge: 0.0–1.0"""
        return self.energy / max(self.capacity, 1e-9)
