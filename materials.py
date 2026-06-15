"""
一般物品
中文名等信息在item_local中定义
"""

from basic_class import *

# =============== 一般材料 =============== #
class Stick(Item):
    add_fire_time = 20

class UnknownPeace(Item):pass

class Magic(Item):pass

class BallPeace(Item):pass

# =============== 祭坛相关 =============== #
class Stone(Item):pass

class LuckStone(Item):pass

class LifeRock(Item):pass

class Key(Item):pass