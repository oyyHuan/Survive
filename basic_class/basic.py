"""
定义摄像机，Actor，光源等类
"""

from locals import *

#初始化
pg.init()
pg.display.set_caption("绝境")
clock=pg.time.Clock()

screen=pg.display.set_mode((WIDTH,HIEGHT),pg.DOUBLEBUF)
screen_rect=screen.get_rect()

near_rect=pg.rect.Rect((0,0),NEARSIZE)  # 活动区域(加载特效)
Global.Area.near_area = pg.Rect((-WIDTH,HIEGHT),(WIDTH*3,HIEGHT*3))  # 更新区域(图层，碰撞判定等)

draw.load_all()

class Task:#任务
    def __init__(self,g):
        self.g=g
        self.lock = 0

    def run(self):
        """
        运行:传回数字,延迟相应帧数
        """
        if self.lock>0:
            self.lock-=1
            return
        res=next(self.g)
        if res is not None:
            self.lock=res#上锁


class Camera:
    def __init__(self):
        # noinspection PyArgumentList
        self.pos=pg.Vector2(0,0)
        self.task=[]
    def move(self,v,n=1,delay=0):
        yield delay
        for i in range(n):
            self.pos+=v

    def __call__(self:Any,g)->Task:#将生成器放入任务列表
        assert g is not None#检查g
        task = Task(g)
        self.task.append(task)
        return task
    def run_task(self:Any):#运行所有任务
        for i in self.task:
            try:i.run()
            except StopIteration:self.task.remove(i)

    def t_shake(self):
        for v,time in ((1,3),(-1,6),(1,3)):
            for _ in range(time):
                self.pos.x +=v*6
                yield


class Actor(pg.sprite.Sprite):
    g:Dict[str,List] = {}
    Global.e_group = pg.sprite.Group()
    Global.warm_group = pg.sprite.Group()
    for z_name in Z_NAME:#设置图层
        g.update({z_name:[]})
    del z_name

    __slow_hide_dic = {}  # 暂存渐隐数据

    def __init__(self,name="",pos=None,z="main",parent=None,show=True,layer=None):
        super().__init__()

        self.image:pg.Surface
        self.rect:pg.Rect#通过__load_image__定义
        self.child:List

        self.name=name
        # noinspection PyArgumentList
        self.pos=None if pos is None else pg.Vector2(*pos)
        self.parent = parent
        self.active:bool = show
        self.z=z
        self.layer = layer
        self.child=[]
        self.task=[]
        if not hasattr(self,"onkeydown"):self.onkeydown=None

        self.init()  # event，show可通过init修改
        self.__load_image__()

        if parent is None:  # 设置所在列表
            self.group=Actor.g[z]  # 有父对象不加入列表
        else:
            self.group=self.parent.child  # 加入父对象的子对象列表
        if self.active:
            self.group.append(self)

    def run_task(self):
        Camera.run_task(self)
    def __call__(self,f:Generator)->Task:
        return Camera.__call__(self,f)

    def event(self):  # 开启交互判定
        assert hasattr(self,"use")
        if self.pos:
            Global.e_group.add(self)
    def init(self):
        pass

    def show(self):
        if not self.active:
            self.group.append(self)
            self.active=True
            for _ in self.child:
                self.active=True
    def hide(self):
        if self.active:
            self.group.remove(self)
            self.active=False
            for _ in self.child:
                self.active=False#show,hide
    def sh_h(self):
        if self.active:self.hide()
        else:self.show()

    def __load_image__(self):#加载图片,仅在__init__调用
        if self.name is None:
            self.name=self.__class__.__name__  # 根据类设置name
        self.image:Imagetype = draw.dic[self.name].copy()
        self.rect:pg.rect.Rect = self.image.get_rect()
        if self.pos is not None:self.update_pos()
    def update_pos(self):
        if self.parent is not None:
            self.rect.center=self.parent.rect.center+self.pos#对齐中心
        else:
            self.rect.midbottom=self.pos-Global.camera.pos#以底部中心为中心
    def update(self):
        self.run_task()#运行任务
        if self.onkeydown is not None and Global.key_down is not None:#判断键盘是否按下
            self.onkeydown(self,Global.key_down)
        for i in self.child.copy():#更新子对象
            i.update()

    def draw(self):
        self.update_pos()#更新坐标

        #print("d")
        screen.blit(self.image,self.rect)
        for i in self.child:#绘制子对象
            i.draw()

    def clean(self):
        """移除"""
        self.kill()
        self.clean_child()
        if self.active:self.group.remove(self)
    def clean_child(self,l:list =None):
        if l is None:#移除所有子对象
            for i in self.child.copy():
                i.clean()
        else:
            for i in l:
                i.clean()


    def t_slow_del(self,time:int, delay = 0):
        """渐隐，结束后移除"""
        yield delay
        if f"{self.name}//time" in Actor.__slow_hide_dic:
            alpha = Actor.__slow_hide_dic[f"{self.name}//time"]
        else:
            alpha = pg.surfarray.pixels_alpha(self.image)//time
            Actor.__slow_hide_dic[f"{self.name}//time"] = alpha  # 暂存

        for i in range(time):
            pg.surfarray.pixels_alpha(self.image)[:]-=alpha
            yield
        self.clean()

    def __add__(self,other)->pg.Vector2:#计算坐标
        if hasattr(other,"pos"):
            return self.pos+other.pos
        else:
            return self.pos+other

    def is_equal(self,other:type)->bool:
        return isinstance(self,other)


def is_active(g:pg.sprite.Group)->filter:
    return filter(lambda x:x.active,g)
# def rand_offset(x:Tuple[int,int],y)->Tuple[int,int]:
#     return random.randint(x[0],x[1]),random.randint(y[0],y[1])


class Light:
    l=[]  # 存储光
    origins=pg.sprite.Group()  # 存储光源
    def __new__(cls, origin:Actor,size:int = None):
        if origin.pos is None:
            return None  #无坐标不发光
        obj = object.__new__(cls)
        return obj
    def __init__(self,origin:Actor,size:int = None):  # 光
        """Light(origin)"""
        self.size=size
        self.origin=origin  # 发光物

        Light.l.append(self)
        Light.origins.add(self.origin)
        if self.size is None:  # 默认光照数据
            self.size=SHADOWSIZE
            self.alpha=SHADOW
        elif size==1:
            self.alpha = BIGSHADOW
            self.size = BIGSHADOW.shape[0]//2
        self.rect=pg.Rect(0,0,self.size*2+1,self.size*2+1)

    def update(self):
        if self.origin not in Light.origins:
            self.remove()#发光物被移除,移除光
            return
        elif not self.origin.active:
            return
        self.rect.center=self.origin.rect.center#更新坐标

    def remove(self):
        Light.l.remove(self)
        Light.origins.remove(self.origin)

    @staticmethod
    def turn(obj:Actor, flag:bool = False, size = None):
        """打开或关闭光源，默认关闭"""
        if flag:
            Light(obj, size)
        else:
            for light in Light.l:  # 找到对应光源并移除
                if light.origin is obj:
                    light.remove()
                    return
            raise RuntimeError(f"{obj} is not in Light.origins")

def reset():
    pass

# 游戏初始化
Global.camera=Camera()
camera=Global.camera

if draw.show_image:
    t=Actor(draw.show_image,(200,50))
    Light(t)