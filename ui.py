from items import *
from copy import copy


class Black(UI):
    def __init__(self):
        self.off = TNIGHT
        super().__init__((0, 0))

    def draw(self):
        if not self.off:
            return
        alpha = np.empty((WIDTH, HIEGHT), dtype=np.uint8)
        alpha.fill(BLACKALPHA)

        for i in Light.l:
            i.update()  #更新光

            clip: pg.rect.Rect = i.rect.clip(self)  #重合部分
            if clip is None:
                continue
            b_area = alpha[clip.left:clip.right, clip.top:clip.bottom]  #黑色部分重叠区域
            left, top = clip.left - i.rect.left, clip.top - i.rect.top
            w_area = i.alpha[left:left + clip.size[0], top:top + clip.size[1]]  #光源重叠区域

            bright = w_area >= b_area
            b_area[bright] = 0
            b_area[~bright] -= w_area[~bright]

        pg.surfarray.pixels_alpha(self.image)[::] = alpha  #重置透明度
        super().draw()


class Mask(UI):
    time = 40
    def init(self):
        self.__color = None
        self.__alpha = 0
    def __load_image__(self):
        self.load_image_by_size(screen_rect.size, (0,0,0))
        self.image.set_alpha(0)

    def set_color(self, color):
        pre_color = self.__color
        if color is None:
            self.__color = None
            return
        if self.__color is None:
            self.__color = np.array(color)
            return
        color = -(self.__color - np.array(color)) / self.time
        def change():
            nonlocal pre_color
            for i in range(self.time):
                pre_color+=color
                self.image.fill(pre_color)
                yield
        self(change())

    def set_alpha(self, alpha):
        _alpha = self.__alpha
        self.__alpha = alpha
        alpha = (alpha - _alpha) / self.time
        def change():
            nonlocal _alpha
            for i in range(self.time):
                _alpha += alpha
                self.image.set_alpha(int(_alpha))
                yield

        Global.p(change())

class FlowChar(Actor):
    """
    飘字，文本居中
    """
    def __init__(self,text:str, color=WHITE,pos:Postype=(WIDTH//2,HIEGHT//2)):
        """
        飘字
        :param text:飘字文本
        :param color: 颜色
        :param pos: 坐标(文本居中)
        """
        self.text = text
        self.color = color
        super().__init__(pos = pos,z="flow_char")

        def flow():
            time = 20
            speed = (0,-2)
            alpha = pg.surfarray.pixels_alpha(self.image) // 10
            for i in range(time):
                self.pos+=speed
                if time//2==i:
                    yield 100
                if i>=time-10:
                    surf = pg.surfarray.pixels_alpha(self.image)
                    surf-=alpha
                    del surf
                yield
            self.clean()
        self(flow())

    def __load_image__(self):
        width,hieght = Text.normal.size(self.text)
        self.image = pg.Surface((width,hieght),pg.SRCALPHA)
        self.rect = pg.Rect(0,0,width,hieght)
        self.image.blit(Text.normal.render(self.text, 1, self.color), (0, 0))
        self.update_pos()
    def update_pos(self):
        self.rect.center = self.pos
Global.Fun.FlowChar = FlowChar


class Window(UI):
    def __init__(self, size=None):
        self.size = size
        self.will_clean_child = True
        super().__init__((0, WINOFFSET), align="midtop", show=False)
    def __load_image__(self):
        if self.size is not None:
            self.fill_image(self.size)
            self.rect = self.image.get_rect()
            self.update_pos()
        else:
            super().__load_image__()

    def open(self):
        Global.win_lock = True  #锁定
        self.redraw()
        self.show()

    def close(self):
        Global.win_lock = False
        if self.will_clean_child:self.clean_child()
        self.hide()

    def cancel_button(self, name, pos = (-20,20)):
        obj = UI(pos, name, "topright", parent=self)

        def cancel(*args):
            self.close()

        obj.onclick = cancel
        return obj

    def text_button(self, bg_name, pos, text: str, color=BLACK, font: pg.font.Font = None):
        if font is None:
            font = Text.normal

        class TextButton(UI):
            def __load_image__(self):
                size = pg.font.Font.size(font, text)
                self.image = pg.transform.scale(draw.dic[bg_name], size)
                self.rect = self.image.get_rect()
                self.image.blit(font.render(text, 1, color), (0, 0))
                #print(self.rect)

        TextButton(pos, bg_name, parent=self)

    def text(self, *args, **kwargs):
        return Text(*args, parent=self, **kwargs)


class Text(UI):
    title = pg.font.SysFont("华文新魏", 40)
    normal = pg.font.SysFont("华文行楷", 20)
    describe = pg.font.SysFont("华文行楷", 15)
    link = pg.font.SysFont("华文行楷", 20)
    link.set_underline(1)

    # noinspection PyArgumentList
    def __init__(self, text: str, pos:Postype, parent: UI, color=(0, 0, 0), font=normal, bg=None, load_rect=False):
        self.text = text
        self.color = color
        self.font = font
        self.bg = bg
        self.load_rect = load_rect

        super().__init__(pos, parent=parent)
        #self.parent.child.append(self)

    def redraw(self):
        #直接调用会出事
        #print(1)
        pos = copy(self.pos)
        offset = self.font.size(self.text)[1] + 5
        for i in self.text.split("\n"):  #换行（tnnd换行代码还得老子手动写）
            surf = self.font.render(i, 1, self.color, self.bg)
            self.parent.image.blit(surf, pos)
            pos[1] += offset

    def update(self):
        if self.onclick is None: return
        if self.load_rect:  #只有开启点击判定会加载矩形
            self.update_pos()
        super().update()  #判定点击有用

    def __load_image__(self):
        if self.load_rect:  #加载矩形（text不能有换行符）
            size = self.font.size(self.text)
            self.rect = pg.rect.Rect(*(0, 0) + size)
            self.update_pos()


class Data(UI):
    def __init__(self,data_name:str, max_num:int, pos, color:Colortype, hight = 10, length = 130):
        self.data_name = data_name
        self.maxnum = max_num
        self.color = color
        self.hight = hight
        self.length = length
        self.pre_data = None
        self.data = None
        super().__init__(pos)

    def __load_image__(self):
        self.load_image_by_size((self.length,self.hight),self.color,self.color)

    def update(self):
        self.pre_data = self.data
        self.data = min(max(0,eval(self.data_name)), self.maxnum)
        if self.data!=self.pre_data:  # 数据变化
            self.image = pg.Surface((int(self.length/self.maxnum*self.data) , self.hight))
            self.image.fill(self.color)
        # super().update()


class Grid(UI):
    font=pg.font.SysFont("simhei",12)
    def init(self):
        self.inner_image: Optional[pg.Surface] = None
        self.inner_text: Union[str, int] = ""
        self.inner_color = WHITE
        self.ind = 0  # 索引

    def f_choose(self,*args):
        last=self.parent.choice
        self.parent.choice = self.ind
        if last>=0:
            self.parent.redraw_grid(last)
        self.parent.redraw_grid(self.ind)

    def __load_image__(self):
        self.image = pg.Surface(GRIDSIZE)
        self.rect = self.image.get_rect()
        self.update_pos()

    def redraw(self):
        """image,text,color"""
        bg_color =(170,)*3
        arg={} if self.ind!=self.parent.choice else {"border":(255,)*3}
        self.fill_image(GRIDSIZE,bg_color,**arg)
        if self.inner_image is not None:
            self.image.blit(pg.transform.scale(self.inner_image,((GRIDSIZE[0]-MARGIN),)*2),
                            (MARGIN,MARGIN))
        if self.inner_text != "":
            self.image.blit(Grid.font.render(str(self.inner_text),1,self.inner_color),(MARGIN,MARGIN))
        super().redraw()


class GridFrame(UI):
    """
    init_frame 初始化
    通过redraw_grid重绘
    """

    # noinspection PyShadowingNames
    def init_frame(self, size: Tuple[int, int], h: Optional[int] = None, w: Optional[int] = None,
                   onclick = None, choice:int = -1,**kargs):
        """
        :param size: 格子行列
        :param h: 自定义高
        :param w: 自定义宽
        :param onclick: 格子被点击时
        :param choice: 初始选择
        :param kargs: 其他属性
        """
        size_fun = lambda x, i: x if h is not None else size[i] * (GRIDSIZE[0]+MARGIN) + MARGIN
        self.w = size_fun(w, 0)
        self.h = size_fun(h, 1)
        self.choice = choice

        #图像
        self.image = pg.Surface((self.w, self.h))
        self.rect = self.image.get_rect()

        for i in range(size[0] * size[1]):  # 网格
            x, y =i % size[0] * (GRIDSIZE[0]+MARGIN)+MARGIN, i // size[0] * (GRIDSIZE[1]+MARGIN)+MARGIN
            #print(x,y,i)
            grid = Grid((x, y), parent=self)
            grid.ind = i
            grid.onclick = onclick
            [setattr(grid,name,value) for name,value in kargs.items()]

        self.update_pos()
        self.redraw()

    def __load_image__(self): pass  #图像通过init_frame加载

    def redraw(self):
        self.fill_image((self.w, self.h))
        super().redraw()

    def redraw_grid(self,index):
        self[index].redraw()
    def onchoose(self,index):
        """格子被点击时运行"""

    def __getitem__(self, item)->Grid:
        return self.child[item]

# 快捷栏
class Bag1(GridFrame):
    def init(self):
        def onclick(obj:Grid,*_):
            last = Global.p.hand
            if last: last.onhand(False)

            Grid.f_choose(obj)
            Global.p.note.obj = Global.p.bag[obj.ind].obj

            last = Global.p.hand
            if last: last.onhand(True)
        self.init_frame((1, 8),onclick=onclick)
        self.choice = 0
    def redraw_grid(self,index):
        bag:np.recarray =Global.p.bag
        data = bag[index]
        grid = self[index]
        if data.obj:
            grid.inner_image = data.obj.image  # 更新图像
            grid.inner_text = data.num  if T.tool not in data.obj.type else data.obj.unbreaking# 数字
            grid.inner_color = WHITE if T.tool not in data.obj.type else GREY
        else:
            grid.inner_image,grid.inner_text = None,""
        grid.redraw()

# 背包
class Bag(Bag1):
    def init(self):
        def onclick(obj,*args):
            last=self.choice
            index = obj.ind
            bag = Global.p.bag
            if last == -1 :
                Grid.f_choose(obj)
            else:
                lasthand = p.hand
                bag[[index, last]] = bag[[last, index]]  # 互换
                newhand = p.hand
                if lasthand is not newhand:  # 手持物改变
                    if lasthand: lasthand.onhand(False)
                    if newhand: newhand.onhand(True)

                self.choice = -1  # 重置选择
            self.redraw_grid(last)
            self.redraw_grid(index)

        self.init_frame((8,5),onclick=onclick)
        self.active=False
    def redraw_grid(self,index):
        if index<8:
            Global.UI.Bag1.redraw_grid(index)  # 更新快捷栏
        super().redraw_grid(index)

class Paperwindow(Window):
    def open(self):
        def back(obj, e):
            if e.key == pg.K_a:
                self.page = None
                self.redraw()

        self.page = None
        self.onkeydown = back
        super().open()

    def redraw(self):
        def click_link(obj, *args):
            #print(obj.text,1)
            self.page = obj.text
            self.redraw()

        self.clean_child()
        self.cancel_button("Paper_cancel_button")
        #print(1)
        #print(self.child)

        offset = [30, 30]
        if self.page is None:  #目录
            self.text("目录", offset.copy(), font=Text.title)
            offset[0] = 70
            for i in HELP:
                offset[1] += 50
                i = self.text(i, offset.copy(), font=Text.link, load_rect=1)  #按钮
                i.onclick = click_link
        else:  #文档
            Text(self.page, offset.copy(), self, font=Text.title)
            offset[0] = 30
            offset[1] += 50
            Text(HELP[self.page], offset.copy(), self, font=Text.normal)
        #print(self.child)
        super().redraw()

# 合成
make = make_table[0]  # 当前选择
class Makewindow(Window):
    """
    left
    right material_frame
    """
    class Left(GridFrame):
        black_rect = pg.Surface((100,100),pg.SRCALPHA)
        black_rect.fill((0,0,0,128))  # 阴影

        """选择配方"""
        def init(self):
            def onclick(obj:Grid,*_):
                global make

                if obj.ind>=len(make_table):
                    return
                obj.f_choose()
                make = make_table[obj.ind]
                self.cover_to_parent()
                self.parent.right.redraw()
            self.init_frame((6,8),onclick=onclick, choice=0, dark = True)

        # noinspection PyUnresolvedReferences
        def redraw_grid(self,index):
            assert index>=0
            grid = self[index]
            _make = make_table[index]
            grid.inner_image = eval(TOEN[_make.result])().image  # 图片

            # 判定能否合成
            grid.dark = False
            for mat,num in _make.material:
                if Global.p.get_sum_of(mat)<num:
                    grid.dark = True  # 材料不足
                    break
            if grid.dark:
                grid.inner_image.blit(Makewindow.Left.black_rect,(0,0))
            super().redraw_grid(index)

    class Right(UI):
        class MaterialFrame(GridFrame):
            """材料框"""
            def init(self):
                self.init_frame((3,2))

            def redraw_grid(self,index):
                """重绘材料"""
                obj = self[index]
                if index>=len(make.material):
                    obj.inner_image,obj.inner_text = None,""
                else:
                    mater = eval(TOEN[make.material[index][0]])()  # 材料
                    num = make.material[index][1]  # 所需数量
                    obj.inner_image,obj.inner_text = mater.image,num
                    obj.inner_color = RED if Global.p.get_sum_of(mater.name)<num else WHITE  # 判断是否足够
                super().redraw_grid(index)

        def __load_image__(self):
            self.load_image_by_size((240,347))
        def after_init(self):
            self.material_frame = Makewindow.Right.MaterialFrame((0,50),parent = self, align="center")
            self.text = Text("",(53,33),parent = self,font = Text.normal)
            self.node = Text("",(3,56),parent = self,font = Text.describe)

        def redraw(self):
            """重绘右边"""
            self.__load_image__()
            obj:Item = eval(TOEN[make.result])()
            self.text.text = obj.name
            self.node.text = make.describe
            image = pg.transform.scale(obj.image,(50,50))
            self.image.blit(image,(3,3))

            for i in range(6):
                self.material_frame.redraw_grid(i)

            super().redraw()
            self.parent.cancel.redraw()  # 避免关闭按钮被挡

    def init(self):
        self.will_clean_child = False
        self.size = (510, 353)
    def after_init(self):
        self.left = Makewindow.Left((3,3),parent = self)
        self.right = Makewindow.Right((267,3),parent = self)
        self.cancel = self.cancel_button("normal_cancel_button", (-5, 5))

    def open(self):
        super().open()

    def redraw(self):
        for i in range(len(make_table)):  # 重绘左边
            self.left.redraw_grid(i)
        super().redraw()

    def onkeydown(self,_,e):
        if e.key==pg.K_SPACE:
            # noinspection PyUnresolvedReferences
            if self.left[self.left.choice].dark:  # 材料不足
                FlowChar("材料不足的问题蛤",color=RED)
                return
            elif 0 not in Global.p.bag.num:  # 背包空间不足
                FlowChar("背包太胖了，塞不下的问题",color=RED)
                return
            else:
                for name,num in make.material:
                    # 找到合适索引
                    bag = Global.p.bag
                    pre_index = np.ogrid[0:40]  # 背包索引
                    m_mask = bag.name==name
                    min_index = np.argmin(bag.num[m_mask])  # 筛选后索引
                    index = pre_index[m_mask][min_index]
                    Global.p.throw(index,num)

                result = eval(TOEN[make.result])
                if result is Key:
                    FlowChar("帮助文档已更新！", color=GREEN)
                    HELP.update(BOSSWORD)
                else:
                    FlowChar(f"{make.result}+{make.num}",color = GREEN)
                Global.p.pick(result(),make.num)
                self.redraw()


    @property
    def left_choice(self)->int:
        return self.left.choice


# 小地图
class SmallMap(UI):
    color = (150,)*3
    def __load_image__(self):
        self.load_image_by_size((70,)*2, SmallMap.color)

    def update(self):
        self.image.fill(SmallMap.color)
        w = Global.Area.world_area
        pos = (p.pos - w.topleft) / w.width * self.rect.width  # 计算坐标
        self.image.fill(GREEN, (pos, (5,)*2))

        if (Boss.boss is not None) and Boss.boss.hp>0:
            pos = (Boss.boss.pos - w.topleft) / w.width * self.rect.width  # 计算坐标
            self.image.fill(RED, (pos, (5,) * 2))
        super().update()


# print(pg.font.get_fonts())
# 初始化UI
if __name__ != "__main__":
    Global.UI.Data = Data
    Global.UI.black = Black()
    Global.UI.mask = Mask((0,0))
    Global.UI.Paperwindow = Paperwindow()
    Global.UI.Makewindow = Makewindow()

    Global.UI.Bag1 = Bag1((20, 0), align="midleft")
    Global.UI.Bag = Bag((0,0),align="center")

    SmallMap((7,57))
    Global.UI.HpData = Data("Global.p.hp",PHP,(7, 20),RED)
    Data("Global.p.warmth", PWARMTH,(7, 40),ORANGE)