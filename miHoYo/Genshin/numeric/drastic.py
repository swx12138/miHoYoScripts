# -- coding: utf-8 --

from . import Resistance


class Drastic(object):
    def __init__(self, em, res: Resistance, buff=0, level=90) -> None:
        self._LevelFactor = 1446.85 if level == 90 else 0
        self._ResistanceFactor = res.Number()
        self._BaseRate = -1
        self._ElementMastery = em
        self._Buff = buff

    def boom(self):
        _Eb = (16 * self._ElementMastery) / (self._ElementMastery + 2000)
        return self._LevelFactor * self._ResistanceFactor * self._BaseRate * (1 + _Eb + self._Buff)


class Blossom(Drastic):
    def __init__(self, em, res: Resistance, buff=0, level=90) -> None:
        super().__init__(em, res, buff, level)
        self._BaseRate = 2
