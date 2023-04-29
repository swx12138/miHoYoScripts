# -- coding: utf-8 --

from abc import abstractmethod


class ISection:
    @abstractmethod
    def Number(this) -> float:
        pass


class Attack(ISection):
    """攻击区"""

    def __init__(this, base: int, weapon: int, buff: float, extern: int) -> None:
        super().__init__()
        this.__White = base + weapon
        this.__Green = this.__White * (1 + buff) + extern

    def Number(this) -> float:
        return this.__White + this.__Green


class Multipiler(ISection):
    """倍率区"""

    def __init__(this, ablity_rate: list, independent: float) -> None:
        """
        ablity_rate - 技能倍率
        independent - 独立乘区
        """
        super().__init__()
        this.__Mul = sum(ablity_rate) * (1 + independent)

    def Number(this):
        return this.__Mul


class Bouns(ISection):
    """增伤区"""

    def __init__(this, bouns: list) -> None:
        super().__init__()
        this.__Bouns = 1 + sum(bouns)

    def Number(this):
        return this.__Bouns


class Critical(ISection):
    """爆伤区"""

    def __init__(this, crit: float, crit_dmg: float) -> None:
        super().__init__()
        if crit > 5:
            crit /= 100
        if crit_dmg > 100:
            crit_dmg /= 100
        this.__Bouns = 1 + crit * crit_dmg

    def Number(this):
        return this.__Bouns


class Reaction(ISection):
    """反应区"""

    def __init__(this, base, ElementMastery, Up) -> None:
        """
        base - 基础反应倍率
        ElementMastery - 元素精通
        Up - 反应系数提升（一般为圣遗物提升）
        """
        super().__init__()
        this.__EM = 2.78 * ElementMastery / (ElementMastery + 1400)
        this.__Bouns = base * (1 + this.__EM + Up)

    def Number(this):
        return this.__Bouns


class Defense(ISection):
    """防御区 暂时不使用"""

    def __init__(this, IngLevel, EdLevel, DefBuf) -> None:
        """
        IngLevel - 人物等级
        EdLevel - 怪物等级
        """
        super().__init__()
        this.__IngLevel = IngLevel + 100
        this.__EdLevel = EdLevel + 100
        this.__Defbuf = 1 + DefBuf

    def Number(this):
        return this.__IngLevel / (this.__Defbuf * (this.__IngLevel + this.__EdLevel))


class Resistance(ISection):
    """抗性区"""

    def __init__(this, YuanKangxing, JianKang, JiaKang) -> None:
        super().__init__()
        this.__R = YuanKangxing - JianKang + JiaKang

    def Number(this):
        if this.__R > 0.75:
            return 1 / (this.__R * 4 + 1)
        elif this.__R < 0:
            return 1 - this.__R / 2
        else:
            return 1 - this.__R
