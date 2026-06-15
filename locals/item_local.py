#存储物品相关设置

"""中英文名字对照"""
TOCH={
    "Stick": "木棍",
    "CampFire": "篝火",
    "Torch": "火把",
    "Torch1": "强化火把",
    "UnknownPeace": "未知碎片",
    "SnowFruit": "雪梨",
    "MagicSnowFruit": "魔法雪梨",
    "Magic": "魔法粉尘",
    "BallPeace": "不稳定碎片",
    "Ball1": "仿制不稳定球",
    "LuckStone": "祈愿之石",
    "LifeRock": "生命精华",
    "Stone": "黄寒玉",
    "Key": "绝望核心",
}
TOEN = {value:key for key,value in TOCH.items()}  # 通过中文获取英文


class T:
    """
    物品类型(弃用)
    """

    tool = 1


class MakeMethod:
    def __init__(self,result,describe,material:dict,num=1):
        """
        生成合成配方
        :param result: 合成物
        :param describe: 描述
        :param material: 材料 {物品名:数}
        :param num: 合成数
        """
        self.result=result
        self.material = tuple(material.items())
        self.describe=describe
        self.num:int = num

make_table = [
    [
        "火把","阿巴阿巴",
        {"木棍":3}
    ],[
        "强化火把","比火把强，但怎么跟粘了屎一样",
        {"木棍": 5, "黄寒玉": 1, "魔法粉尘":4}
    ],[
        "篝火","给予你温暖\n站在上面会有神奇的效果，你不会被\n烫伤",
        {"木棍":7}
    ],[
        "祈愿之石","对祈愿祭坛使用它，\n可以得到惊喜与惊吓",
        {"魔法粉尘":3, "未知碎片":2}
    ],[
        "生命精华","对生命祭坛使用它，\n可以生成更多资源",
        {"未知碎片": 10}
    ],[
        "绝望核心","做了就知道干什么的了",
        {"黄寒玉": 3,"魔法粉尘":20, "未知碎片":25}
    ],[
        "仿制不稳定球","完全原创，无抄袭",
        {"不稳定碎片": 2, "未知碎片": 2, "魔法粉尘": 1}
    ]
]
make_table = [MakeMethod(*args) for args in make_table]