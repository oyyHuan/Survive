from locals import *
class Area:
    def __init__(self, name, text_color = WHITE, bg_color = None, alpha = 100):
        """
        生成一块区域
        :param name: 区域名
        :param text_color: 进入后出现文本颜色
        :param bg_color: 背景氛围
        """
        self.name = name
        self.text_color = text_color
        self.bg_color = bg_color
        self.alpha = alpha

    def onenter(self):
        """进入时发生"""
    def onexit(self):
        """离开时发生"""
    def onin(self):
        """处于区域内持续发生"""

    def __hash__(self):
        return hash(self.name)


born = Area("初始雪地",alpha=0)
cold = Area("极寒之地", SKYBLUE, SKYBLUE)
dark = Area("暗夜领域", RED, BLACK, 190)

unable = Area("unable")

area_list = [[cold,born,dark],
             [cold,born,dark],
             [cold,born,dark]]