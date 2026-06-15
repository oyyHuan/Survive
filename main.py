import json
from sys import exit
from ui import *
from areas import *
import os

def init_world():
    """初始化世界"""
    read()

    def rain_all():
        """生成所有物体"""

        # 将各区域按名称分组，记录坐标
        area_dic:Dict[Area, list] = {}
        for x in range(3):
            for y in range(3):
                _area = area_list[y][x]
                if _area in area_dic:
                    area_dic[_area].append((w.x + x*s.width, w.y + y*s.height))
                else:
                    area_dic[_area] = [(w.x + x*s.width, w.y + y*s.height)]
        del _area

        def rain(obj:Type[Item], num:int,area:Area):
            for i in range(num):
                pos = random.choice(area_dic[area])
                pos = (random.randint(pos[0], pos[0] + s.width), random.randint(pos[1], pos[1] + s.height))
                obj(pos)

        def _create():
            rain(Shrub, 10, born)
            rain(SnowFruitPlant, 10, cold)
        life_alter.create = _create

        rain(Shrub, 40, born)
        rain(Unknown, 15,born)

        rain(Bug, 20, cold)
        rain(SnowFruitPlant, 20, cold)

        rain(Unknown, 30, dark)
        rain(Shrub, 10, dark)

        def t_rain_animal():
            """持续生成生物"""
            while True:
                if len(Animal.animals) < 100:
                    rain(Unknown, 4, born)
                    rain(Bug, 5, cold)
                    rain(Unknown, 6, dark)
                yield 650
        p(t_rain_animal())

    # 初始化区域
    s = Global.Area.single_area = pg.Rect((0,0),SINGLE_RECT)
    w = Global.Area.world_area = pg.Rect((0,0),(Global.Area.single_area.width*3,Global.Area.single_area.width*3))
    s.center = screen_rect.center
    w.center = screen_rect.center

    # 生成
    rain_all()

def running()->NoReturn:
    bg=draw.dic["background"]#获取背景
    w,h=bg.get_size()

    def search_aim(e):
        """查找攻击目标,仅限main图层"""
        def search(x: Actor)->bool:
            if x is p or not isinstance(x,Item):  # 确保为可攻击对象,玩家不能自残
                return False
            relate = x.pos - p.pos
            d = max(abs(relate.x),abs(relate.y))  # 范围为方形
            return d <= p.attrange

        aims = filter(search, Actor.g["main"])
        if not aims:  # 无目标,忽略
            return
        for o in aims:
            if o.rect.collidepoint(e.pos):
                p.attack(o)
                break

    def check_event():#检查事件
        #判定交互标识是否显示
        mpos, target = 99, None  # target下方if语句直接调用
        if not Global.win_lock:  # 仅在未锁定时显示
            for i in is_active(Global.e_group):  # 交互
                #print(1)
                rpos=i.pos-Global.p.pos
                _mdis=abs(rpos.x)+abs(rpos.y)
                #print(_mdis)
                if _mdis < PERANGE and _mdis < mpos:#取最小距离
                    mpos,target=_mdis,i
            if target is not None:
                #print(1)
                e_sign.pos=target+EOFFSET
                e_sign.update()
                e_sign.show()
            else:e_sign.hide()
        else:e_sign.hide()


        for e in pg.event.get():
            if e.type==pg.QUIT:
                write()
                exit()
            if not Global.win_lock:  # 锁住时不判定
                # 当键盘按下
                if e.type==pg.KEYDOWN:
                    if e.key in PWSAD:
                        Global.p.start_move(PWSAD[e.key])#玩家开始移动
                    elif e.key==pg.K_e and target is not None:#交互
                        target.use()
                # 当键盘松开
                elif e.type==pg.KEYUP:
                    if e.key in PWSAD and Global.p.direction==PWSAD[e.key]:
                        Global.p.end_move()#松开,玩家停止移动

                # 当鼠标按下
                elif e.type == pg.MOUSEBUTTONDOWN:
                    # 当滚轮滚动
                    if e.button in (pg.BUTTON_WHEELUP,pg.BUTTON_WHEELDOWN):
                        move = -1 if e.button==pg.BUTTON_WHEELUP else 1
                        bag1 = Global.UI.Bag1
                        bag1[(bag1.choice + move) % 8].onclick(bag1[(bag1.choice + move) % 8])

                    # 左键(攻击)
                    if e.button==1:
                        search_aim(e)

                    # 右键放置
                    elif e.button==3:
                        p.put(pg.mouse.get_pos())

            # 任何状态 鼠标或键盘按下
            if e.type==pg.MOUSEBUTTONDOWN:
                Global.mouse_down=e
            elif e.type==pg.KEYDOWN:
                Global.key_down=e  # 传输事件
                if e.key==pg.K_F1:exit()  # 退出

            # if TEST:  # 测试操作
            #     if e.type==pg.KEYDOWN:
            #         if e.key==pg.K_l:  # 开关灯
            #             Global.UI.black.off=not Global.UI.black.off
            #         elif e.key==pg.K_f:  # 获取帧率
            #             print(clock.get_fps())

    def check_area():
        """检查区域"""
        if not Global.Area.world_area.collidepoint(*p.pos):  # 出界
            p.area = unable.name
            if random.randint(0,60)<1:
                FlowChar("出界了智障，给老子回去", color = RED)
            return

        single, world = Global.Area.single_area, Global.Area.world_area
        left = world.left
        for x in range(3):
            right = single.width + left
            if p.pos.x<right:  # 确定x坐标
                top = world.top
                for y in range(3):
                    bottom = top + single.height
                    if p.pos.y<bottom:  # 确定y坐标
                        # noinspection PyTypeHints
                        area = area_list[y][x]
                        if p.area!=area.name:  # 更新所属区域
                            p.area=area.name
                            FlowChar(f"你已进入 [{area.name}]", color=area.text_color)
                            Global.UI.mask.set_color(area.bg_color)
                            Global.UI.mask.set_alpha(area.alpha)
                        break
                    top = bottom
                break
            left = right

    def update():  # 更新屏幕

        def for_all(f):
            """遍历Actor.g"""
            # noinspection PyShadowingNames
            for i in Z_NAME:  # 运行任务
                for _ in actors[i]:getattr(_,f)()

        actors=Actor.g
        # near_list = Global.Area.near_list = list(filter(
        #     lambda actor:Global.Area.near_area.colliderect(actor.rect), actors["main"]))

        actors["main"].sort(key=lambda act: act.layer if act.layer is not None else act.pos.y)  # 排序

        camera.run_task()
        for_all("update")  # 运行任务
        
        cx,cy=camera.pos  # 背景
        cx%=w
        cy%=h
        while cx<0:
            cx+=w
        while cy<0:
            cy+=h
        for x in range(int(-cx),WIDTH,w):
            for y in range(int(-cy),HIEGHT,h):
                screen.blit(bg,(x,y))
                
        for_all("draw")# 重绘
        pg.display.flip()
    while True:
        # 重置事件
        Global.mouse_down=None
        Global.key_down=None

        check_event()
        check_area()
        update()
        clock.tick(70)

# =========== 读写文件 =========== #
file_name = ""
def read():
    global file_name

    def init_bag():
        p.pick(Torch(), 1)
        p.pick(Stick(), 20)

    file_name = None
    for file in os.listdir("SAVE"):
        if file.startswith("_"):
            file_name = file
            break
    # 创建存档
    if file_name is None:
        with open("SAVE\\_data.json", "w"):
            pass
        file_name = "_data.json"
        init_bag()
        return
    # 读取
    with open(f"SAVE\\{file_name}", "r") as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            init_bag()
            return

    p.hp = data["hp"]
    p.warmth = data["warmth"]

    # 读取背包
    bag = data["bag"]
    for item_name,num in bag:
        item = eval(item_name)()
        if hasattr(item, "unbreaking"):
            p.pick(item, 1)
            item.unbreaking = num
        else:
            p.pick(item, num)

        if hasattr(p.hand, "onhand"):
            p.hand.onhand(True)

def write():
    if p.hp <= 0:
        return

    _bag = p.bag[p.bag.num > 0]  # 背包数据
    data = {
        "hp": p.hp,
        "warmth": p.warmth,
        "bag": [[type(item.obj).__name__, int(item.num)]
                if not hasattr(item.obj, "unbreaking")
                else [type(item.obj).__name__, item.obj.unbreaking]
                for item in _bag],
    }
    with open(f"SAVE\\{file_name}", "w") as f:
        json.dump(data, f)

reset()
init_world()
running()