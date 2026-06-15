"""
定义有特殊功能的对象
"""
from .common import *

class Tool(Item):
    """
    unbreaking 耐久
    """
    def init_tool(self,unb:int = 100):
        self._unbreaking = unb
        self.type.add(T.tool)

    @property
    def unbreaking(self):
        return self._unbreaking
    @unbreaking.setter
    def unbreaking(self,value):
        if value<=0:
            assert self is Global.p.hand  # 必须手持
            Global.p.throw(Global.p.handchoice)
        self._unbreaking = value


class FireOrigin(Item):
    """
    火源
    """
    def init_fireorigin(self,time:int, start_fire = True, light = None):
        """time单位为秒"""
        self.fire_time = time
        self.is_firing = False
        self.light = light
        if start_fire:self(self.t_strat_fire())

    def onhand(self,ison):
        Light.turn(Global.p,ison, None if not hasattr(self, "light") else self.light)

    def t_strat_fire(self):
        Light(self)
        self.is_firing = True
        while self.fire_time > 0 and self.is_firing:
            self.fire_time -= 1
            yield 60
        self.is_firing = False
        Light.turn(self)
    
    def attacked(self,num:int , obj:Actor):
        super().attacked(num,obj)

# noinspection PyArgumentList
class Animal(Item):
    __attack_speed = 6  # 击退速度
    animals = pg.sprite.Group()
    def init_animal(self, hp = 20, speed = 0.5):
        Animal.animals.add(self)

        self.hp = hp
        self.speed = speed
        self.targets = 0  # 数字表示状态数，0为空闲
        self.target:Optional[Item] = None
        self.way = pg.Vector2(speed)
        self.have_attacked = False  # 攻击时使用

    def find(self,obj:Item, find_d, attack_d, sleep):
        """
        寻找攻击目标
        :param obj: 目标
        :param find_d: 寻找半径
        :param attack_d: 攻击半径
        :param sleep: 攻击间隔
        """
        def _find():
            while True:
                if self.target is None and self.mpos_to(Global.p)<find_d:  # 进入追击状态
                    self.target = obj
                if self.target:  # 处于追击状态
                    if self.target.hp<=0:break

                    if self.mpos_to(obj)<attack_d:  # 开始攻击
                        self.have_attacked = False
                        self.targets+=1
                        self(self.onattack(obj))
                        yield sleep
                        self.targets-=1  # 解除攻击间隔
                    elif self.mpos_to(obj)>find_d:  # 解除
                        self.target = None
                yield
        self(_find())


    def _move(self):
        if not self.near:
            return
        if self.targets>0:  # 只有空闲时移动
            return
        if self.target:  # 追击
            if self.pos!=Global.p.pos:
                self.way = (self.target.pos-self.pos).normalize()*self.speed
        else:  # 随处移动
            rand = random.randint(0, 180)
            if rand<3:
                self.way = pg.Vector2(self.speed).rotate(random.randint(0,360))
            elif rand<4:
                self.way = pg.Vector2(0)
        self.pos+=self.way

    def t_particle(self, name: str, live_time:int):
        """粒子效果"""
        def single_obj():
            o = Actor(name,(0,0), layer = self.pos.y)
            relate_pos = random.randint(-o.image.get_width()//2,o.image.get_width()//2),random.randint(-o.image.get_height(),0)
            o.pos = self.pos+relate_pos  # 随机坐标
            o(o.t_slow_del(live_time,30))
            def rise():
                while True:
                    o.pos.y-=0.2
                    yield
            o(rise())
        while True:
            if not self.near:
                yield 2
                continue
            single_obj()
            yield 10

    def t_shake(self):
        """击退,需提前设置way"""
        self.targets += 1
        for time,v in ((2,0.7),(3,2),(4,3)):
            for i in range(time):
                self.pos-=self.way//v
                yield
        yield 4
        self.targets -= 1
        self.way = pg.Vector2(self.speed)

    def mpos_to(self:Item,obj:Item):
        relate = self.pos-obj.pos
        return abs(relate.x)+abs(relate.y)
    def way_to(self,obj:Item):
        """获取方向"""
        relate = obj.pos-self.pos
        relate = pg.Vector2(1) if relate == pg.Vector2(0, 0) else relate.normalize()
        return relate

    def update(self):
        self._move()
        super().update()

    def onattack(self, other:Item):
        """攻击时，为生成器类型,other为攻击对象"""
        raise AssertionError

    def attacked(self, num: int, obj: Actor):
        relate = obj.pos-self.pos
        relate = relate if relate!=pg.Vector2(0,0) else pg.Vector2(1)
        self.way = self.__attack_speed*relate.normalize()
        super().attacked(num, obj)

    def attack(self,num:int, target:Item):
        if self.have_attacked:
            return
        self.have_attacked = True
        target.attacked(num, self)


class Food(Item):
    __ban_time=60
    eatable = True

    def init_food(self, add_hp = 3):
        self.__add_hp = add_hp

    def eat(self):
        if not self.eatable:
            return
        Global.p.throw(Global.p.handchoice)

        Global.p.hp+=self.__add_hp
        Global.hp = min(Global.p.hp,PHP)
        Global.p(self.__t_ban())

    def __t_ban(self):
        self.eatable = False
        yield self.__ban_time
        self.eatable = True


class Alter(Item):
    alter_group = pg.sprite.Group()
    def init_alter(self, protecter = False):
        self.hp = float("inf")
        self.event()
        if protecter:
            Alter.alter_group.add(self)

    def use(self):
        raise AssertionError


class Bomb(Item):
    # noinspection PyArgumentList
    def t_bomb(self, r, att, delay):
        """
        使炸弹爆炸
        :param r: 爆炸半径
        :param att: 伤害
        :param delay: 延迟
        """

        # noinspection PyShadowingNames
        def move(obj:Actor):
            time = random.randint(30,40)
            obj(obj.t_slow_del(time))
            for i in range(time):
                obj.pos.y-=random.randint(1,3)
                yield
        yield delay
        camera(camera.t_shake())
        for i in range(20):
            d = pg.Vector2(random.randint(0,r),0)
            d = self.pos+d.rotate(random.randint(0,360))
            obj = Actor("red_block", d)
            obj(move(obj))
        for i in self.find_target():
            if self.check_d(i, r):
                i.attacked(att, self)
        self.clean()


    def check_d(self, target:Item, r):
        if (self.pos - target.pos).length()<r:
            return True
        return False

    def find_target(self):
        for i in Animal.animals:
            yield i