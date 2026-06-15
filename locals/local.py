"""各种常量"""
import numpy as np
from pygame import locals

"""测试"""
TNIGHT = 1

#帮助
HELP = {
"基本操作":
            """
      wsad 移动(不会建议刷新大脑)
      c 合成界面  按空格合成选中物体
      q 丢弃
     空格 背包
     左键 攻击或点燃篝火   右键 放置
     滚轮 修改手持物
     在帮助界面按a可以回到目录
            """,

"大致玩法":
    """
    用木棍维持篝火,用篝火取暖,
    用火把攻击篝火以点燃
    别的自己研究,等你死了就赢了
    """,

"区域":
    """
初始雪地
  有灌木及未知生物
极寒之地
  有雪梨和蠕虫(但是雪梨为什么是在地里?)
暗黑领域
  通关的必经之地
另外，从出生点开始一直往右，下，左走
可以看到祭坛
    """
}
BOSSWORD = {
    "游戏目标": "到地图右侧用绝望核心唤醒绝望之眼，\n并将其击败",
    "恐惧之眼介绍": "不要想着一开始就用不稳定球炸死恐惧之眼，你会后悔的\n"
                "当发现自己在持续扣血时,请尽快远离他"
}
END = """？
我靠，你通关了？！
我台词呢？
（慌乱翻找中……）
咳咳
游戏名  绝境
制作用时  四个月
代码量  2400
感谢你的游玩
不是
感谢您的游玩
"""

#颜色
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
UIBORDER = (77, 77, 77)
UIIN = (150,) * 3
WHITE = (255, 255, 255)
SKYBLUE = (100, 100, 255)
ORANGE = (255, 165, 0)
PINK = (255, 0, 255)

# 窗口
HIEGHT = 800
WIDTH = 1000
SINGLE_RECT = (2500, 2000)  # 单位区域
NEARSIZE = (2000, 1600)  # 活动区域

# 其他
Z_NAME = ("ground", "main", "ui","flow_char")

# 玩家
PHP = 20  # 血量
PWARMTH = 300  # 温度
PS = 5  # 速度
PATT = 3  # 攻击
PATTRANGE = 100  # 攻击范围
PERANGE = 100  # 交互范围
PBAG = 40  # 背包容量

PWSAD = {locals.K_w: [0, -PS],
         locals.K_a: [-PS, 0],
         locals.K_s: [0, PS],
         locals.K_d: [PS, 0], }
EYEOFFSET = [8, -7]  # 眼偏移
EOFFSET = (0, -30)  # 标志偏移


# 黑色
BCOLOR = (30,) * 3
BLACKALPHA = 245

# 阴影
SHADOWSIZE = 100

def shadow(br=75, slow=25)->np.ndarray:
    """
    :param br: 亮
    :param slow: 渐变
    """
    size = br + slow
    x, y = np.ogrid[-size:size + 1, -size:size + 1]
    pos = (x**2+y**2)**0.5  # abs(x) + abs(y)
    a = np.zeros((size * 2 + 1,) * 2)
    slow_area = (pos >= br) & (pos <= size)
    a[slow_area] = BLACKALPHA * (pos[slow_area] - br) ** 0.5 // slow ** 0.5  # 渐变
    #a[slow_area] = 255 * (pos[slow_area] - br)  // slow   # 渐变
    a[pos > size] = BLACKALPHA
    return BLACKALPHA - a.astype(np.uint8)  # 转0~255正整数


SHADOW = shadow()
BIGSHADOW = shadow(120,50)
# print(shadow(10,3))

# 窗口
WINOFFSET = 40  # 上边距
GRIDSIZE = (40,)*2
MARGIN = 3  # 间距

# 掉落物
DSIZE = 30
DSPEED = 20