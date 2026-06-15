"""绘制图片"""
import os
import pygame as pg
from pygame import Surface,transform
from locals.local import *

__all__=["dic"]
dic={}
def add(name):
    dic.update({name:img})

"""玩家"""
img=Surface((40,40))
img.fill((200,200,200))
add("P")
#眼
SIZE=(5,7)
eye=Surface(SIZE)
eye.fill((0,0,0))
img=Surface((15,SIZE[1]))
img.fill((255,255,255))
img.blit(eye,(0,0))
img.blit(eye,(15-SIZE[0],0))
img.set_colorkey((255,255,255))
add("Peye")


#背景
SIZE=(200,160)
img=Surface(SIZE)
img.fill((170,170,175))
rand=np.random.rand(*SIZE)>0.9
pg.surfarray.pixels3d(img)[rand]=(140,140,195)#处理
img=pg.transform.scale(img,(500,400))
del rand
add("background")

#阴影
img=Surface((SHADOWSIZE*2+1,)*2,pg.SRCALPHA)
img.fill((0,)*3)
pg.surfarray.pixels_alpha(img)[::]=SHADOW
add("shadow")

#黑色
img=Surface((WIDTH,HIEGHT),pg.SRCALPHA)
img.fill(BCOLOR)
add("Black")

img=Surface((WIDTH,HIEGHT))
img.fill(BCOLOR)
add("_Black")


"""杂物"""
#页
img=Surface((450,600))
img.fill((255, 252, 202))
add("Paperwindow")

def load_all():
    for file in os.listdir("image"):
        img=pg.image.load(os.path.join("image",file))
        #a=pg.PixelArray(img)
        #a.replace((255,255,255),(0,0,0,0))
        #dic.update({file:img})
        #a.close()
        dic[os.path.splitext(file)[0]]=img

show_image=None