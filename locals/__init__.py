#import typing
#print(typing.__all__)

import random
from .local import *
from .item_local import *
from ._global import *
import locals.draw
import pygame as pg

from typing import *
#Ztype=typing.Literal["ground", "main", "ui"]
Colortype=Tuple[int,int,int]
Postype=Union[Tuple[int,int],List[int],pg.Vector2]
Imagetype=pg.Surface