from enum import Enum, unique


@unique
class Behaviour(Enum):
    click           = 0  # click
    combieSwipe     = 1  
    rightSwipe      = 2  # right slide (finger slide from left to right and release)
    leftSwipe       = 3  # left slide
    downSwipe       = 4  # down slide
    upSwipe         = 5  # up slide
    tripleSwipe     = 6  # three finger slide (sliding with three finger, used to screenshot)
    rightScroll     = 7  # right drag (finger slide from left to right and hold for a while)
    leftScroll      = 8  # left drag
    downScroll      = 9  # down drag
    upScroll        = 10 # up drag
    longClick       = 11 # long click (finger touch the screen and hold for a while)
    doubleClick     = 12 # double click
    doubleSwipe     = 13 # two finger slide (from center to edge, used to zoom in the picture)
    noneBehaviour   = 14 # no act
    misDoubleClick1 = 15 # variant double click 1 (click twice, and the second click takes a little longer)
    misDoubleClick2 = 16 # variant double click 2 (click twice, and the first click takes a little longer)
    misLongClick1   = 17 # variant long click
    misRightSwipe   = 18 # variant right slide (right slide immediately after clicking)
    misLeftSwipe    = 19 # variant left slide
    misDownSwipe    = 20 # variant down slide
    misUpSwipe      = 21 # variant up slide
    misRightScroll1 = 22 # variant right drag1 (right drag immediately after clicking)
    misLeftScroll1  = 23 # variant left drag1
    misDownScroll1  = 24 # variant down drag1
    misUpScroll1    = 25 # variant up drag1
    misRightScroll2 = 26 # variant right drag2 (long click immediately after right dragging)
    misLeftScroll2  = 27 # variant left drag2
    misDownScroll2  = 28 # variant down drag2
    misUpScroll2    = 29 # variant up drag2
    misRightScroll3 = 30 # variant right drag3 (drag from left to center and hold for a while, then drag from center to right)
    misLeftScroll3  = 31 # variant left drag3
    misDownScroll3  = 32 # variant down drag3
    misUpScroll3    = 33 # variant up drag3
    misRightScroll4 = 34 # variant right drag4 (right drag immediately after right sliding)
    misLeftScroll4  = 35 # variant left drag4
    misDownScroll4  = 36 # variant down drag4
    misUpScroll4    = 37 # variant up drag4
    misRightScroll5 = 38 # variant right drag5 (drag from left to center and release, then drag from center to right)
    misLeftScroll5  = 39 # variant left drag5
    misDownScroll5  = 40 # variant down drag5
    misUpScroll5    = 41 # variant up drag5
    misLongClick2   = 42 # long click for a short time (finger touch the screen and hold for a while, but time shorter than long click)

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