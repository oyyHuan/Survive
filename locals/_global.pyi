import pygame as pg

import items,typing
import ui


class Global:  #存储全局变量，模块间传递信息
    import items

    win_lock = False

    mouse_down = None
    key_down = None

    p:items.P
    e_group: pg.sprite.Group
    warm_group: pg.sprite.Group

    class UI:
        Data = ui.Data
        HpData: ui.Data
        Paperwindow:ui.Paperwindow
        Makewindow:ui.Makewindow
        Bag1:ui.Bag1
        Bag:ui.Bag
        mask:ui.Mask
        black:ui.Black

    class Area:
        near_list:typing.List[items.Item]  # 活跃区域
        near_area:pg.Rect
        single_area:pg.Rect
        world_area:pg.Rect

    class Fun:
        FlowChar = ui.FlowChar