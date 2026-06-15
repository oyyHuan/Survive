from pygame import Vector2
from materials import *


# noinspection PyUnresolvedReferences
class P(Item):  # 玩家
    """
    att 攻击力
    attrange 攻击范围
    """
    bag_type=np.dtype([("name",object) , ("num",np.uint8) , ("obj",object)])
    warmth_reduce = 3  # 每秒扣除温度
    add_hp_time = 105  # 回血间隔
    def __init__(self):
        # 阿巴阿巴
        class Note(Actor):
            SIZE = 15
            font = pg.font.SysFont("华文行楷", SIZE)

            def init(self):
                self.active = False
                self._obj: Optional[Item] = None
                self.show_time = 0

            def __load_image__(self):
                if self.obj is not None:
                    name = self.obj.name
                    width = (len(name) + 1) * Note.SIZE
                    self.image = pg.Surface((width, Note.SIZE), pg.SRCALPHA)
                    self.image.blit(Note.font.render(name, 1, BLACK), (Note.SIZE, 0))  # 文字
                    self.image.blit(pg.transform.scale(self.obj.image, (Note.SIZE, Note.SIZE)), (0,0))
                    self.show()
                else:
                    self.image = pg.Surface((1, 1), pg.SRCALPHA)
                self.rect = self.image.get_rect()
            @property
            def obj(self):return self._obj
            @obj.setter
            def obj(self, value):
                if value is None:return

                def delay_hide():
                    while self.show_time>0:
                        self.show_time-=1
                        yield
                    self.hide()

                if self.show_time == 0:self(delay_hide())
                self.show_time = 180
                self._obj = value
                self.__load_image__()

        super().__init__(screen.get_rect().center, PHP)
        self.direction = None
        self.eye = Actor("Peye", EYEOFFSET, parent=self)
        self.note = Note(pos=(0,-30),parent=self)
        self.__warmth = PWARMTH  # 温度
        self.magical_fruit = 0  # 魔法雪梨持续时间
        self.never_die = False

        self.bag=np.empty(PBAG, dtype=P.bag_type).view(np.recarray)
        self.area = ""  # 所处区域
        #print( '' in self.bag["name"])

        self(self.t_warmth())
        self(self.t_hp())

    def start_move(self, d):
        self.direction = d
        x = self.direction[0]
        if x: self.eye.pos.x = abs(x) // x * EYEOFFSET[0]

    def end_move(self):
        self.direction = None

    def pick(self,obj:Item,num:int=1)->int:
        """拾取物品,批量拾取可能不会分组"""
        bag=self.bag
        max_num=64 if T.tool not in obj.type else 1
        index = None
        name_in = bag.name == obj.name
        if obj.name in bag.name and np.any(bag[name_in].num<max_num):  # 优先堆叠
            index = np.argmax(name_in & (bag.num<max_num))
            pre_num = bag[index].num
            if num+pre_num > max_num:  # 分组堆叠
                bag[index].num = max_num
                rest = self.pick(obj,num+pre_num-max_num)
            else:
                bag[index].num=num+pre_num
                rest = 0
        elif np.any(~name_in):  # 分组
            res=(obj.name,num,obj)
            index=np.argmax(bag.name == None)
            bag[index]=res
            bag[index].name=obj.name
            if index==self.handchoice:
                obj.onhand(True)

            rest = 0
        else:rest = num  # 捡了个寂寞

        # 重绘背包
        if index is not None:
            Global.UI.Bag.redraw_grid(index)
        return rest

    def throw(self,target:int, num:int = 1):
        """
        减少某物品
        :param target: 所在索引
        :param num: 数量
        """
        bag = self.bag
        bag[target].num-=num
        if bag[target].num==0:
            bag[target].obj.onhand(False)
            bag[target] = (None,0,None)
        Global.UI.Bag.redraw_grid(target)

    def get_sum_of(self,ch_name:str):
        return self.bag[self.bag.name==ch_name].num.sum()

    def update(self):
        if Global.win_lock:
            self.direction = None
        if self.direction is not None:  # 移动
            self.pos += self.direction
            self(camera.move(self.direction, 1, 10))
        super().update()

    def onkeydown(self,_,e):
        if e.key==pg.K_SPACE:
            """打开背包"""
            if Global.win_lock and Global.UI.Bag.active:
                Global.UI.Bag.hide()
                Global.win_lock=False
            elif not Global.win_lock:
                Global.UI.Bag.show()
                Global.win_lock=True
        elif not Global.win_lock:
            """若未打开窗口"""
            if e.key==pg.K_q:
                hand = self.hand
                if hand:
                    Dropped(self.pos,-self.pos+pg.mouse.get_pos(),hand)
                    p.throw(p.handchoice)
            elif e.key==pg.K_c:
                Global.UI.Makewindow.open()

    def attack(self,o:Item):  # 攻击
        o.attacked(self.att,self)

    def attacked(self, num: int, obj: Actor):
        if self.hp <=0 or self.never_die:
            return
        super().attacked(num, obj)

    def t_shake(self):
        for _ in camera.t_shake():
            yield

    def t_warmth(self):
        """减少温度"""
        while True:
            yield 65
            flag = True
            for i in Global.warm_group:
                if Animal.mpos_to(i, self)<90:
                    flag = False
                    self.warmth+=13
            if flag:self.warmth-=self.warmth_reduce
    def t_hp(self):
        def green(obj):
            """回血特效"""
            obj(obj.t_slow_del(50))
            for _ in range(50):
                obj.pos.y-=1
                yield

        while True:
            if self.hp < PHP:
                if self.hp<=0:
                    break
                self.hp+=1
            for i in range(self.add_hp_time):
                if self.magical_fruit>0:
                    self.magical_fruit-=1
                    if self.magical_fruit % 65==0 and self.hp<PHP:
                        self.hp+=1
                        self.warmth+=1
                    if self.magical_fruit % 20==0:
                        # 回血特效
                        pos = (random.randint(-30, 30),random.randint(0, 30))
                        o = Actor("addhp", pos, parent = self)
                        o(green(o))
                yield

    @property
    def att(self):
        if hasattr(self.hand, "att"):
            return self.hand.att
        else:return PATT

    @property
    def attrange(self):
        if hasattr(self.hand, "attrange"):
            return self.hand.attrange
        else:
            return PATTRANGE

    # noinspection PyArgumentList
    def die(self, obj):
        """死亡特效"""
        peace = 5
        l = [(x, y) for x in range(0, 41, peace) for y in range(0, 41, peace)]  # 碎片坐标
        random.shuffle(l)

        # 碎片图像
        image = pg.Surface((peace, peace)).convert_alpha()
        image.fill((200,200,200))
        draw.dic["peace"] = image

        self.image = self.image.convert_alpha()

        def animation():
            # noinspection PyArgumentList
            def partical(part):
                """碎片移动"""
                part(part.t_slow_del(50))
                for i in range(50):
                    part.pos +=pg.Vector2(-2,-1)
                    pg.surfarray.pixels3d(part.image)[:]+=1
                    yield

            def show_black():
                """黑屏"""
                yield 100
                black = UI((0,0),"_Black", show=False)
                black.image.set_alpha(0)
                black.show()
                for a in range(4,256,4):
                    black.image.set_alpha(a)
                    yield
                yield 15
                Global.Fun.FlowChar("你睡着了", RED)

                # 处理后事
                Actor.g["main"].clear()
                Actor.g["ground"].clear()
                pg.event.set_allowed(None)  # 关闭事件接收
                pg.event.set_allowed(pg.QUIT)

            self(show_black())
            for x, y in l:
                # 清除
                alpha = pg.surfarray.pixels_alpha(self.image)
                endx,endy = x+peace, y+peace
                alpha[x:endx,y:endy]=0
                del alpha

                pos = (endx - 23, endy - 40)
                o = Actor("peace", pos + self.pos)
                o(partical(o))
                yield 2
        self(animation())

    # 手持物
    @property
    def hand(self) -> Tool:
        return self.bag[Global.UI.Bag1.choice].obj
    @property
    def handchoice(self) -> int:return Global.UI.Bag1.choice

    # 温度
    @property
    def warmth(self):
        return self.__warmth

    @warmth.setter
    def warmth(self, value):
        if value>=PWARMTH:
            self.__warmth=PWARMTH
            return
        elif value<=0:
            self.attacked(1,None)
            self.__warmth = 0
            return
        self.__warmth = value

    def put(self,pos):
        """放置"""
        d = 0
        hand = self.hand
        if hand is None:return  # 手持物为空

        if isinstance(hand,Food):  # 食用
            hand.eat()
            return

        if not hand.putable or d>PERANGE:  # 不可放置或距离过远
            return
        self.throw(self.handchoice)

        pos = pos+camera.pos
        hand.pos = pos
        hand.show()
        hand.onput()


class Paper(Actor):
    def init(self):
        self.event()
        self.z="ground"

    @staticmethod
    def use():
        Global.UI.Paperwindow.open()


class CampFire(FireOrigin):
    def init(self):
        self.putable = True

    def onput(self):
        self.event()
        self.hp=20
        self.dropped = [Stick]*random.randint(1,3)
        self.init_fireorigin(40)

    def use(self):
        hand = p.hand
        if hasattr(hand,"add_fire_time"):  # 增加燃料
            self.fire_time+=hand.add_fire_time
            if self.fire_time>60:  # 限制燃烧时间
                self.fire_time = 60
            p.throw(p.handchoice)
        Global.Fun.FlowChar(f"剩余燃烧时间：{self.fire_time}")

    def firing(self):
        def color_slow(obj:Item):
            l=[(YELLOW,0),(RED,70),(GREY,50)]  # 颜色，渐变时间
            prec=np.array(l[0][0],dtype=float)
            for color,time in l[1:]:
                color=(np.array(color,dtype=float)-prec)/time  # 渐变量
                for i in range(time):
                    prec+=color
                    obj.image.fill(prec)
                    yield
        def block_slow(obj:Item):
            for i in range(60):
                if i%3!=0:
                    obj.size+=1
                obj.pos.y-=1
                obj.alpha-=3
                yield 2
            obj.clean()#移除对象
        yield
        yield
        while self.is_firing:#生成火焰🔥
            if not self.near:#离角色太远则不生成
                yield
                continue
            block=self.create_block((0,3),YELLOW,size=10,alpha=190)
            block(block_slow(block))
            block(color_slow(block))
            yield 60
        Global.warm_group.remove(self)  # 停止供热

    def onhand(self, ison):pass

    def attacked(self, num: int, obj: P):
        if obj is Global.p and isinstance(obj.hand,Torch):  # 点燃
            if self.fire_time>0 and not self.is_firing:
                self(self.t_strat_fire())
            return
        super().attacked(num, obj)

    def t_strat_fire(self):
        Global.warm_group.add(self)  # 提供热量
        self(self.firing())
        return super().t_strat_fire()


class Shrub(Item):  # 画的跟始一样
    def init(self):  # 画的真的跟史一样
        self.hp = 10
        self.dropped = [Stick]*random.randint(1,3)


# =============== 火把 =============== #
class Torch(FireOrigin,Tool):
    def init(self):
        self.hp = 10
        self.putable = False
        self.light = None
        self.init_tool(80)

    def onhand(self, ison):
        super().onhand(ison)
        if ison:
            def using():
                hand = Global.p.handchoice
                while True:
                    self.unbreaking-=1
                    Global.UI.Bag.redraw_grid(hand)
                    yield 60
            self.using = Global.p(using())
        else:Global.p.task.remove(self.using)


class Torch1(Torch):
    att = 5
    attrange = 150
    def init(self):
        self.hp = 10
        self.init_tool(300)
        self.light = 1


# =============== 生物 =============== #
class Unknown(Animal):
    def init(self):
        self.dropped = [UnknownPeace]*random.randint(0,3)

        self.init_animal(10,2)
        self(self.t_particle("unknow_particle",30))
        self.find(Global.p, 300, 200, 120)

    def update(self):
        super().update()

    def onattack(self,other:Item):
        rush_speed = 8
        self.way = self.way_to(other)
        for i in range(30):
            if self.mpos_to(other)<30:
                self.attack(3,other)
            self.pos+=self.way*rush_speed
            if self.targets>1:  # 攻击打断(处于击退状态)
                break
            yield

    def attacked(self, num: int, obj: Actor):
        super().attacked(num, obj)


class Bug(Animal):
    class Bugbody(Actor):
        def init(self):
            self(self.t_slow_del(30, 30))

    def init(self):
        self.draw_time = 10  # 绘制间隔
        self.init_animal(10,3)
        self.find(Global.p, 300, 30, 60)

        self.dropped = [Magic]*random.randint(0,3)

    def onattack(self, other: Item):
        self.attack(2, other)
        yield

    def __load_image__(self):
        self.rect:pg.Rect = pg.Rect(0, 0, 55, 55)  # 不加载图片

    def draw(self):
        self.update_pos()

    def update(self):
        if self.mpos_to(Global.p)<250:
            self.draw_time = (self.draw_time - 1) % 10
            if self.draw_time==0:  # 绘制身体
                self.Bugbody("BugBody", self.pos)
        super().update()


class Protecter(Item):
    __offset = 100
    __hp = 3
    def init(self):
        self.dropped = [BallPeace]
        self.hp = self.__hp
        # self.init_animal(self.__hp, 0)

        self(self.t_attack())

    def t_attack(self):
        while True:
            d = self.pos - Global.p.pos
            d = max(abs(d.x), abs(d.y))
            if d<200:
                Ball(self.pos)
                yield random.randint(50,160)
            yield 300

    def back(self):  # 复活
        self.hp = self.__hp
        self.show()

    def die(self, obj):
        self.hide()
        super().die(obj)

        def back():
            yield 600
            self.back()
        p(back())

    @staticmethod
    def init_all():
        for a in Alter.alter_group:
            Protecter(a + (-Protecter.__offset, 0))
            Protecter(a + (+Protecter.__offset, 0))


# =============== 雪梨 =============== #
class SnowFruitPlant(Item):
    def init(self):
        self.dropped = [SnowFruit] * random.randint(1,2)
        self.hp = 3
class SnowFruit(Food):
    def init(self):
        self.init_food()
class MagicSnowFruit(Food):
    def init(self):
        self.init_food()

    def eat(self):
        super().eat()
        if self.eatable:
            p.magical_fruit = 1100


# =============== 炸弹 =============== #
class Ball(Bomb, Animal):
    def init(self):
        self(self.t_bomb(200, 10, 140))
        self.init_animal(7,1)
        self.find(p,200,-1,0)
        # self.hp = 7

    def find_target(self):
        yield p  # 只攻击玩家


class Ball1(Bomb):
    def init(self):
        self.putable = True
    def onput(self):
        self(self.t_bomb(370, 10, 120))


# =============== 祭坛 =============== #
class LifeAlter(Alter):
    def init(self):
        self.init_alter(False)
        self.create = None  # 在main中重新定义

    def use(self):
        if isinstance(p.hand, LifeRock):
            p.throw(p.handchoice)
            p.attacked(10, self)
            self.create()
        else:
            Global.Fun.FlowChar("需要生命精华", RED)


class LuckyAlter(Alter):
    get = [SnowFruit, SnowFruit, Torch, Stick, Stone, Stone, BallPeace] * 2 + [MagicSnowFruit]
    def init(self):
        self.init_alter(True)

    # noinspection PyArgumentList
    def use(self):
        if isinstance(p.hand,LuckStone):
            p.throw(p.handchoice)
            if random.random()>0.8:
                Ball(self.pos)
            else:
                o = random.choice(self.get)
                way = p.pos-self.pos
                Dropped(self.pos,  way if way else Vector2(0,1), o)
        else:
            Global.Fun.FlowChar("需要祈愿之石",RED)


# =============== boss =============== #
class BossRock(Alter):
    awake = False
    def init(self):
        self.init_alter(False)

    def use(self):
        if self.awake:# 避免被重复唤醒
            return

        if not isinstance(p.hand, Key):
            Global.Fun.FlowChar("需要绝望核心", RED)
            return
        p.throw(p.handchoice)
        self.awake = True

        # 激活
        # noinspection PyTypeChecker
        def awake():
            for i in range(30):
                ball.pos.y -= (30 - i) // 5 + 1
                yield 2
            for i in range(20):
                ball.pos.y += 1
                yield 2
            yield 20
            ball.find_target = lambda: (_ for _ in [])
            ball.pos = self.pos
            ball(Bomb.t_bomb(ball, 100, 0, 0))
            Boss(self.pos)
        ball = Actor("redEye", self.pos+(-5, 0),layer=self.pos.y)
        ball(awake())

# boss状态
UNATTACKABLE = 0
NORMAL = 1
class Boss(Animal):
    boss = None
    def init(self):
        Boss.boss = self
        self.counter = 0  # 计数器
        self.color = np.array(RED)

        self.init_animal(230, 0.2)
        Global.UI.Data("Boss.boss.hp", 200, (365,20), PINK, 7, 280)  # 血条
        self(self.t_particle("unknow_particle", 50))
        self(self.t_main())
        self.dropped = []

    def attacked(self, num: int, obj: Actor):
        if self.hp<=0:
            return
        if self.state == UNATTACKABLE:
            p.attacked(num, obj)  # 反伤
            return
        super().attacked(num, obj)

    def t_main(self):
        self.eye = Item((0, 0), name="bossEye", parent=self)
        self.eye.alpha = 64

        self.change_to_unattackable()
        while True:
            if self.mpos_to(p) > 650:
                yield 3
                continue

            self.counter -= 1

            # 激光
            if self.state == UNATTACKABLE:
                if self.mpos_to(p) > 500:
                    self.counter = 0  # 技能打断
                elif self.counter % 50 == 0:
                    p.attacked(2, self)

            if self.counter == 0:
                if self.state == UNATTACKABLE:
                    self(self.t_change_color(RED))
                    self.state = NORMAL
                else:
                    # 发动技能
                    flag = random.random()
                    if flag < 0.45:
                        self.change_to_unattackable()
                        continue
                    elif flag < 0.7:
                        if clock.get_fps() >=55:
                            self.create_unknown()
                        else:
                            Bug(p.pos)
                    else:
                        Bug(p.pos)
                self.counter = random.randint(270,550)  # 等待至下一次发动技能

            # 回血
            if self.hp < 100 and self.counter % 30 == 0:
                self.hp +=1
            yield

    #=============== 技能 =============== #
    def change_to_unattackable(self):
        """进入无敌状态"""
        self.state = UNATTACKABLE
        self.counter = random.randint(300,500)
        self(self.t_change_color(ORANGE))

    def draw(self):
        super().draw()
        if self.state == UNATTACKABLE:
            pg.draw.line(screen, ORANGE, self.eye.rect.center, p.rect.center, 7)

    def create_unknown(self):
        def task():
            for i in range(3):
                Unknown(self.pos)
                yield 20
        self(task())

    # ============= 辅助函数 ============= #
    def t_change_color(self, color):
        _color = (np.array(color) - self.color) // 30
        for i in range(30):
            self.color += _color
            try:
                self.eye.image.fill(self.color)
            except TypeError:
                break
            yield
        self.color = color
        self.eye.image.fill(self.color)

    # ============== 其它 ============== #
    def die(self, obj):
        """死亡特效"""
        if p.hp<=0:
            return
        p.never_die = True
        Global.UI.HpData.clean()
        self.task.clear()

        def the_last_function():
            """结束!!!!!!!!!!!!!!"""
            for txt in END.split():
                Global.Fun.FlowChar(txt, WHITE)
                yield 200

        def arise():
            for i in range(70):
                self.pos.y-=1
                yield
            Global.UI.black.off = False
            self.find_target = lambda: (_ for _ in [])
            self.pos = self.pos
            # noinspection PyTypeChecker
            p(Bomb.t_bomb(self, 100, 0, 0))

            p(the_last_function())
        self(arise())

    def attack(self, num: int, target: Item):
        if self.hp > 0:
            super().attack(num, target)


if __name__!="__main__":
    p=Global.p=P()
    paper=Global.paper=Paper(None,p.pos+(0,-20))  # 帮助

    e_sign=Actor("E",(0,0),z="ui",show=False)  # 交互标志
    e_sign_image = pg.surfarray.pixels_alpha(e_sign.image)
    e_sign_image[e_sign_image>0]//=2
    del e_sign_image

    fire = CampFire(p.pos+(-70,20))
    fire.onput()
    fire.hp = float("inf")
    del fire

    """祭坛"""
    life_alter = LifeAlter(p+(0,1600))
    lucky_alter = LuckyAlter(p+(-1600,0))
    BossRock(p + (1600, 0))
    Protecter.init_all()