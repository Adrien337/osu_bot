from beatmap.models import Circle
from player.base import BasePlayer


class CirclePlayer(BasePlayer):
    def hit(self, circle: Circle):
        """
        Joue un cercle simple.
        """
        # On clique exactement au temps de l'objet
        self.click_at(circle.x, circle.y, circle.time)