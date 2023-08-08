from enum import Enum, unique


@unique
class Behaviour(Enum):
    click = 0  # 单击                                   click
    combieSwipe = 1  #
    rightSwipe = 2  # 右滑                              right slide (finger slide from left to right and release)
    leftSwipe = 3  # 左滑                               left slide
    downSwipe = 4  # 下滑                               down slide
    upSwipe = 5  # 上滑                                 up slide
    tripleSwipe = 6  # 三指滑动                         three finger slide (sliding with three finger, used to screenshot)
    rightScroll = 7  # 右滚动                           right drag (finger slide from left to right and hold for a while)
    leftScroll = 8  # 左滚动                            left drag
    downScroll = 9  # 下滚动                            down drag
    upScroll = 10  # 上滚动                             up drag
    longClick = 11  # 长按                              long click (finger touch the screen and hold for a while)
    doubleClick = 12  # 双击                            double click
    doubleSwipe = 13  # 二指滑动                         two finger slide (from center to edge, used to zoom in the picture)
    noneBehaviour = 14  # 无操作                        no act
    misDoubleClick1 = 15  # 第一次单击第二次时间稍长       variant double click 1 (click twice, and the second click takes a little longer)
    misDoubleClick2 = 16  # 第一次时间稍长，第二次单击     variant double click 2 (click twice, and the first click takes a little longer)
    misLongClick1 = 17  # 单击一下再长按                 variant long click

    misRightSwipe = 18  # 右滑mis 单机后右滑             variant right slide (right slide immediately after clicking)
    misLeftSwipe = 19  # 左滑mis                        variant left slide
    misDownSwipe = 20  # 下滑mis                        variant down slide
    misUpSwipe = 21  # 上滑mis                          variant up slide

    misRightScroll1 = 22  # 右滚动mis1  单击后拖动       variant right drag1 (right drag immediately after clicking)
    misLeftScroll1 = 23  # 左滚动                       variant left drag1
    misDownScroll1 = 24  # 下滚动                       variant down drag1
    misUpScroll1 = 25  # 上滚动                         variant up drag1

    misRightScroll2 = 26  # 右滚动mis2  拖动后长按       variant right drag2 (long click immediately after right dragging)
    misLeftScroll2 = 27  # 左滚动                       variant left drag2
    misDownScroll2 = 28  # 下滚动                       variant down drag2
    misUpScroll2 = 29  # 上滚动                         variant up drag2

    misRightScroll3 = 30  # 右滚动mis3  拖动后长按拖动    variant right drag3 (drag from left to center and hold for a while, then drag from center to right)
    misLeftScroll3 = 31  # 左滚动                       variant left drag3
    misDownScroll3 = 32  # 下滚动                       variant down drag3
    misUpScroll3 = 33  # 上滚动                         variant up drag3

    misRightScroll4 = 34  # 右滚动mis4  滑动后拖动       variant right drag4 (right drag immediately after right sliding)
    misLeftScroll4 = 35  # 左滚动                       variant left drag4
    misDownScroll4 = 36  # 下滚动                       variant down drag4
    misUpScroll4 = 37  # 上滚动                         variant up drag4

    misRightScroll5 = 38  # 右滚动mis5  拖动中断又拖动   variant right drag5 (drag from left to center and release, then drag from center to right)
    misLeftScroll5 = 39  # 左滚动                       variant left drag5
    misDownScroll5 = 40  # 下滚动                       variant down drag5
    misUpScroll5 = 41  # 上滚动                         variant up drag5

    misLongClick2 = 42  # 短时间的长按                   long click for a short time (finger touch the screen and hold for a while, but time shorter than long click)

    sysHome = 43  # home button gesture in full screen display mode
    sysMenu = 44  # menu button gesture in full screen display mode
    sysExit = 45  # exit button gesture in full screen display mode


@unique
class ErroProType(Enum):
    ProcError = 0
    RamError = 1
    NetError = 2


clickActList = [Behaviour.click,Behaviour.doubleClick]

longClickList = [Behaviour.click,Behaviour.doubleClick,Behaviour.longClick,Behaviour.misLongClick2]

downSwipeActList = [Behaviour.downSwipe,Behaviour.tripleSwipe]

otherSwipeActList = [Behaviour.leftSwipe,Behaviour.leftScroll]


orderBehavList = [Behaviour.click,Behaviour.longClick]