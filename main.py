import sys
import weakref
import math

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import (QLineF, QPointF, QRandomGenerator, QRectF, QSizeF,
                            Qt, qAbs, pyqtSignal, QRect)
from PyQt5.QtGui import (QColor, QBrush, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QStyle, QWidget, QGridLayout, QDesktopWidget)

class Node(QGraphicsItem):
    item_type = QGraphicsItem.UserType + 1

    def __init__(self, Ui_MainWindow, name=0):
        super().__init__()

        self.name = name
        self.graph = weakref.ref(Ui_MainWindow)
        self._edge_list = []
        self._new_pos = QPointF()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

    def boundingRect(self):
        adjust = 2.0
        return QRectF(-10 - adjust, -10 - adjust,
                             23 + adjust, 23 + adjust)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        rect = QRect(-7, -7, 20, 20)
        painter.drawEllipse(rect)

        gradient = QRadialGradient(-3, -3, 10)
        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QColor(Qt.yellow).lighter(120))
            gradient.setColorAt(0, QColor(Qt.darkYellow).lighter(120))
        else:
            gradient.setColorAt(0, Qt.yellow)
            gradient.setColorAt(1, Qt.darkYellow)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(-10, -10, 20, 20)
        painter.drawText(rect, Qt.AlignCenter, str(self.name))

    def mousePressEvent(self, event):
        # self.update()
        # QGraphicsItem.mousePressEvent(self, event)
        super(Node, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.scene().itemClicked.emit(self)

    def mouseReleaseEvent(self, event):
        self.update()
        QGraphicsItem.mouseReleaseEvent(self, event)

    def focusItemChanged(self, newItem, oldItem, reason):
        if newItem and reason == Qt.MouseFocusReason:
            print('item {} clicked!'.format(newItem))

class ItemClickableGraphicsScene(QGraphicsScene):
    itemClicked = pyqtSignal(QGraphicsItem)

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._node_list = []
        self.current_number_nodes = 0
        uic.loadUi('main.ui', self)

        # ẩn phần dư của main windown chỉ để hiện background
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #| QtCore.Qt.WindowStaysOnTopHint)

        # cho hiển thị giữa màn hình
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        #Find Children
        self.graphicsView: QtWidgets.QGraphicsView = self.findChild(QtWidgets.QGraphicsView, 'graphicsView')
        # self.graphicsView.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.create_ui()
        
        self.show()

    def create_ui(self):
        self.graphicsView._timer_id = 0
        self.scene = ItemClickableGraphicsScene(self)
        self.scene.itemClicked.connect(self.itemClicked)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        # self.scene.focusItemChanged.connect(self.focusChanged)

        self.graphicsView.x = self.graphicsView.x()
        self.graphicsView.y = self.graphicsView.y()
        self.graphicsView.width = self.graphicsView.width()
        self.graphicsView.height = self.graphicsView.height()

        self.scene.setSceneRect(self.graphicsView.x, self.graphicsView.y, self.graphicsView.width, self.graphicsView.height)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setCacheMode(QGraphicsView.CacheBackground)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def mousePressEvent(self, event):
        p = event.pos() # relative to widget
        # print(p)
        # gp = self.graphicsView.mapToGlobal(p) # relative to screen
        # print(gp)
        # rw = self.graphicsView.window().mapFromGlobal(gp) # relative to window
        # print(rw)
        x, y = int(p.x()), int(p.y())
        # print(x, y)
        if self.graphicsView.x <= x <= self.graphicsView.x + self.graphicsView.width and self.graphicsView.y <= y <= self.graphicsView.height:
            node = Node(self.graphicsView, self.current_number_nodes)
            node.setPos(x, y)
            self._node_list.append(node)
            self.scene.addItem(node)
            self.current_number_nodes += 1
        else:
            print("Out of view!")
        # print(self._node_list)
        # for item in self._node_list:
        #     # item.focusItemChanged.connect(self.focusChanged)
        #     self.rect_item = Node
        super().mousePressEvent(event)

    def itemClicked(self, item):
        print('Node {} clicked!'.format(item.name))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tmp = Ui_MainWindow()
    app.exec_()