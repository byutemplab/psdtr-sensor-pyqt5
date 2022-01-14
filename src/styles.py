from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import matplotlib.pyplot as plt
import seaborn as sns

# ========== PYQT5 STYLES ============


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        return QSize(180, 40)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class QCustomTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)


class QCustomProxyStyle(QProxyStyle):
    def drawControl(self, element, opt, painter, widget):
        if element == QStyle.CE_TabBarTabLabel:
            r = QRect(opt.rect)
            w = 0 if opt.icon.isNull() else opt.rect.width() + \
                self.pixelMetric(QStyle.PM_TabBarIconSize)
            r.setHeight(opt.fontMetrics.width(opt.text) + w)
            r.moveBottom(opt.rect.bottom())
            opt.rect = r
        QProxyStyle.drawControl(self, element, opt, painter, widget)


# ========== CUSTOM COLORS ============

# CB91_Blue = '#2CBDFE'
# CB91_Green = '#47DBCD'
# CB91_Pink = '#F3A0F2'
# CB91_Purple = '#9D2EC5'
# CB91_Violet = '#661D98'
# CB91_Amber = '#F5B14C'

# ========== CUSTOM MATPLOTLIB STYLE ============

sns.set(font='Franklin Gothic Book',
        style=None,
        rc={'axes.axisbelow': False,
            'axes.edgecolor': 'lightgrey',
            'axes.facecolor': 'None',
            'axes.grid': False,
            'axes.labelcolor': 'dimgrey',
            # 'axes.spines.right': False,
            # 'axes.spines.top': False,
            'figure.facecolor': 'white',
            'lines.solid_capstyle': 'round',
            'patch.edgecolor': 'w',
            'patch.force_edgecolor': True,
            # 'text.color': 'dimgrey',
            'xtick.bottom': False,
            'xtick.color': 'dimgrey',
            'xtick.direction': 'out',
            'xtick.top': False,
            'xtick.major.pad': 0.1,
            'ytick.color': 'dimgrey',
            'ytick.direction': 'out',
            'ytick.left': False,
            'ytick.right': False,
            'ytick.major.pad': 0.1, })

sns.set_context("notebook", rc={"font.size": 8,
                                "axes.titlesize": 10,
                                "axes.labelsize": 8,
                                'xtick.labelsize': 'small',
                                'ytick.labelsize': 'small'})
