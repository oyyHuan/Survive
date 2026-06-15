"""
在Actor基础上定义基本类
"""

from .basic import *

# noinspection PyAttributeOutsideInit
class Item(Actor):#生物和非生物
    """
    事件 use, onhand, ondie
    属性 dropped, hp, putable, set
    pos为None时不显示
    """
    def __init__(self,pos:Optional[Postype] = None,hp=float("inf"),name=None,**kwargs):
        self.dropped: Optional[List[Type[Item]]] = None
        self.type:Set[int] = set()
        self.hp = hp
        self._alpha = 255

        self.putable = False

        super().__init__(name,pos,z="main",show=(pos is not None),**kwargs)# 无pos则隐藏
        self.name=TOCH.get(self.name,self.name)  # 转中文名

    def update(self):
        super().update()

    def create_block(self,pos,color:Colortype = (0,0,0),**kwargs):
        obj=Item(pos,name="empty_block",parent=self)
        obj.image.fill(color)
        for att,value in kwargs.items():
            assert hasattr(obj,att)
            setattr(obj,att,value)
        return obj

    def attacked(self,num:int , obj:Actor):
        """被攻击"""
        if self.hp == float("inf"):
            return
        if obj is Global.p:
            if hasattr(Global.p.hand, "unbreaking"):
                Global.p.hand.unbreaking -= 2
        self.hp-=num

        if self.hp<=0:
            self.die(obj)
        self(self.t_shake())
    def die(self,obj):
        self.ondie()
        if self.dropped:
            for o in self.dropped:
                # noinspection PyArgumentList
                pos = (pg.Vector2(0,1) if self.pos == obj.pos else self.pos-obj.pos)
                pos.rotate_ip(random.randint(-30,30))
                Dropped(self.pos, pos, o)
        self.clean()

    """各种事件"""
    def onhand(self,ison):
        """被拿起或放下时"""
    def ondie(self):
        """当死亡时"""
    def onput(self):
        """当被放下时"""

    @property
    def near(self) -> bool:
        """判断是否在附近"""
        return near_rect.collidepoint(*self.rect.topleft)

    """渐变"""
    def t_shake(self):
        for d in(-1,1):
            for _ in range(3):
                self.pos.x-=2*d
                yield
    #透明度
    @property
    def alpha(self):return self._alpha
    @alpha.setter
    def alpha(self,value):
        self._alpha=value
        #print(self._alpha)
        self.image.set_alpha(self._alpha)

    # 大小(仅适用正方形)
    @property
    def size(self)->int:return self.rect.size[0]
    @size.setter
    def size(self,value):
        #assert self.rect.size[0]==self.rect.size[1]
        self.image:pg.Surface = pg.transform.scale(self.image,(value,value))
        self.rect.size=(value,value)
        self.update_pos()

    def is_tool(self):
        """判断是否为工具"""
        return T.tool in self.type

class Dropped(Actor):
    """掉落物"""
    def __init__(self,pos:Postype, way:pg.Vector2, obj:Union[Type[Item],Item]):
        self.obj = obj if type(obj) != type else obj()
        way.scale_to_length(DSPEED)
        self.speed = way
        super().__init__(pos=pos,z="ground")
        self(self.t_move())
    def __load_image__(self):
        self.image = pg.transform.scale(self.obj.image,(DSIZE,DSIZE))
        self.rect = self.image.get_rect()

    def t_move(self):
        change = self.speed/10  # 加速度
        for i in range(random.randint(7,13)):
            self.pos+=self.speed
            self.speed-=change
            yield
        while True:  # 判定是否被拾起
            if pg.sprite.collide_rect(self,Global.p) and Global.p.pick(self.obj)==0:
                # self.obj.onhand(True)
                self.obj.clean()
                self.clean()
            yield
            yield


class UI(Actor):

    #用于设置事件触发时处理方式
    f_set=lambda _obj,attr,value:(lambda obj:setattr(_obj,attr,value))#设置属性

    def __init__(self,pos:Postype,name=None,align='topleft',**kargs):
        self.align = align
        if not hasattr(self,"onclick"):self.onclick = None#点击时触发
        super().__init__(name,pos,z="ui",**kargs)
        self.after_init()  # 烦:(

    @property
    def absolute_rect(self)->pg.Rect:
        if self.parent is None:
            return self.rect
        else:
            p_rect = self.parent.absolute_rect
            #npos=pg.Vector2(*p_rect.topleft)+self.rect.topleft
            #print(npos)
            #print(self.rect.move(npos))
            return self.rect.move(*p_rect.topleft)

    def fill_image(self,size,bg_color=UIIN,border=UIBORDER):
        bs=2
        size=[i+bs for i in size]
        w,h=size
        self.image=pg.Surface((w,h))
        self.image.fill(bg_color)
        pg.draw.lines(self.image,border,True,
                      ((w-1,0),(w-1,h-1),(0,h-1),(0,0)),bs)


    def update_pos(self):
        if self.parent is not None:#烦死了
            p_pos=self.parent.rect.topleft
            self.parent.rect.topleft=(0,0)
            pos = getattr(self.parent.rect , self.align)#ui子对象矩形坐标取相对父对象坐标
            self.parent.rect.topleft = p_pos
            #print(p_pos,pos,self+pos)
        else:
            pos = getattr(screen_rect , self.align)
        setattr(self.rect,self.align,self+pos)
    def update(self):
        """事件检查"""
        if self.onclick is not None and Global.mouse_down:# 检查点击
            #print(Global.mouse_down)
            if self.absolute_rect.collidepoint(*Global.mouse_down.pos):
                self.onclick(self)# 触发事件
        if self.onkeydown is not None and Global.key_down is not None:  # 判断键盘是否按下
            self.onkeydown(self, Global.key_down)

        for i in self.child:
            i.update()

    def redraw(self):  # 通知子对象重绘
        if self.name:self.image=draw.dic[self.name].copy()# 重新获取图像,部分界面需手动获取
        for i in self.child:
            i.redraw()
        if self.parent:
            self.parent.image.blit(self.image,self.rect)

    def draw(self):
        screen.blit(self.image, self.rect)  # 子对象通过redraw重绘

    def cover_to_parent(self):
        """对于存在祖父元素的元素，更新子对象后绘制至上一级元素"""
        if self.parent and self.parent.parent:  # 存在祖父
            self.parent.cover_to_parent()
        self.parent.image.blit(self.image, self.rect)

    def load_image_by_size(self,size:Tuple[int,int],bg_color=UIIN,border=UIBORDER):
        """根据size填充,用于重写load_image"""
        self.fill_image(size,bg_color,border)
        self.rect = self.image.get_rect()
        self.update_pos()

    def after_init(self):
        """加载图片后执行,用于放入子元素"""