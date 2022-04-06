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

class Edge(QGraphicsItem):

    item_type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super().__init__()

        self._arrow_size = 10.0
        self._source_point = QPointF()
        self._dest_point = QPointF()
        # self.setAcceptedMouseButtons(Qt.NoButton)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setCacheMode(self.DeviceCoordinateCache)
        # self.setZValue(-1)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().add_edge(self)
        self.dest().add_edge(self)
        self.adjust()

    def item_type(self):
        return Edge.item_type

    def source_node(self):
        return self.source()

    def set_source_node(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def dest_node(self):
        return self.dest()

    def set_dest_node(self, node):
        self.dest = weakref.ref(node)
        self.adjust()

    def adjust(self):
        if not self.source() or not self.dest():
            return

        line = QLineF(self.mapFromItem(self.source(), 0, 0),
                      self.mapFromItem(self.dest(), 0, 0))
        length = line.length()

        if length == 0.0:
            return

        edge_offset = QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)

        self.prepareGeometryChange()
        self._source_point = line.p1() + edge_offset
        self._dest_point = line.p2() - edge_offset

    def boundingRect(self):
        if not self.source() or not self.dest():
            return QRectF()

        pen_width = 3
        extra = (pen_width + self._arrow_size) / 2.0

        width = self._dest_point.x() - self._source_point.x()
        height = self._dest_point.y() - self._source_point.y()
        rect = QRectF(self._source_point, QSizeF(width, height))
        return rect.normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return

        # Draw the line itself.
        line = QLineF(self._source_point, self._dest_point)

        if line.length() == 0.0:
            return

        painter.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        # angle = math.acos(line.dx() / line.length())
        # if line.dy() >= 0:
        #     angle = 2 * math.pi - angle

        # arrow_head1 = QPointF(math.sin(angle + math.pi / 3) * self._arrow_size,
        #                       math.cos(angle + math.pi / 3) * self._arrow_size)
        # source_arrow_p1 = self._source_point + arrow_head1
        # arrow_head2 = QPointF(math.sin(angle + math.pi - math.pi / 3) * self._arrow_size,
        #                       math.cos(angle + math.pi - math.pi / 3) * self._arrow_size)
        # source_arrow_p2 = self._source_point + arrow_head2

        # arrow_head1 = QPointF(math.sin(angle - math.pi / 3) * self._arrow_size,
        #                       math.cos(angle - math.pi / 3) * self._arrow_size)
        # dest_arrow_p1 = self._dest_point + arrow_head1
        # arrow_head2 = QPointF(math.sin(angle - math.pi + math.pi / 3) * self._arrow_size,
        #                       math.cos(angle - math.pi + math.pi / 3) * self._arrow_size)
        # dest_arrow_p2 = self._dest_point + arrow_head2

        # painter.setBrush(Qt.black)
        # painter.drawPolygon(QPolygonF([line.p1(), source_arrow_p1, source_arrow_p2]))
        # painter.drawPolygon(QPolygonF([line.p2(), dest_arrow_p1, dest_arrow_p2]))

    def mousePressEvent(self, event):
        self.update()
        # QGraphicsItem.mousePressEvent(self, event)
        super(Edge, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.scene().itemClicked.emit(self)

    def mouseReleaseEvent(self, event):
        self.update()
        QGraphicsItem.mouseReleaseEvent(self, event)

    def focusItemChanged(self, newItem, oldItem, reason):
        if newItem and reason == Qt.MouseFocusReason:
            print('item {} clicked!'.format(newItem))


class Node(QGraphicsItem):
    item_type = QGraphicsItem.UserType + 1

    def __init__(self, Ui_MainWindow, name=0):
        super().__init__()

        self.name = name
        # self.graph = weakref.ref(Ui_MainWindow)
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

    def add_edge(self, edge):
        self._edge_list.append(weakref.ref(edge))
        edge.adjust()

    def edges(self):
        return self._edge_list

    def calculate_forces(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self._new_pos = self.pos()
            return

        # Sum up all forces pushing this item away.
        xvel = 0.0
        yvel = 0.0
        for item in self.scene().items():
            if not isinstance(item, Node):
                continue

            line = QLineF(self.mapFromItem(item, 0, 0), QPointF(0, 0))
            dx = line.dx()
            dy = line.dy()
            l = 2.0 * (dx * dx + dy * dy)
            if l > 0:
                xvel += (dx * 150.0) / l
                yvel += (dy * 150.0) / l

        # Now subtract all forces pulling items together.
        weight = (len(self._edge_list) + 1) * 10.0
        for edge in self._edge_list:
            if edge().source_node() is self:
                pos = self.mapFromItem(edge().dest_node(), 0, 0)
            else:
                pos = self.mapFromItem(edge().source_node(), 0, 0)
            xvel += pos.x() / weight
            yvel += pos.y() / weight

        if qAbs(xvel) < 0.1 and qAbs(yvel) < 0.1:
            xvel = yvel = 0.0

        scene_rect = self.scene().sceneRect()
        self._new_pos = self.pos() + QPointF(xvel, yvel)
        self._new_pos.setX(min(max(self._new_pos.x(), scene_rect.left() + 10),
                               scene_rect.right() - 10))
        self._new_pos.setY(min(max(self._new_pos.y(), scene_rect.top() + 10),
                               scene_rect.bottom() - 10))
    
    def advance(self):
        if self._new_pos == self.pos():
            return False

        self.setPos(self._new_pos)
        return True

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for edge in self._edge_list:
                edge().adjust()
            # self.item_moved()

        return QGraphicsItem.itemChange(self, change, value)

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
        self.update()
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
        # self._edge_list = []
        self.current_number_nodes = 0
        self.mode = None
        self.pairNode = []
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
        # self.graphicsView.setEnabled(0)
        # self.graphicsView.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.btn_1: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_1')
        self.btn_2: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_2')
        self.btn_3: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_3')
        self.btn_4: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_4')

        self.btn_1.clicked.connect(lambda: self.addNode())
        self.btn_2.clicked.connect(lambda: self.addEdge())
        self.btn_3.clicked.connect(lambda: self.delNode())
        self.btn_4.clicked.connect(lambda: self.delEdge())
        self.create_ui()

        self.show()

    def create_ui(self):
        self.graphicsView._timer_id = 0
        self.scene = ItemClickableGraphicsScene(self)
        self.scene.itemClicked.connect(self.itemClicked)
        # self.scene.itemClicked.connect(self.edgeClicked)
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
        if self.mode == 'addNode':
            if self.graphicsView.x <= x <= self.graphicsView.x + self.graphicsView.width and self.graphicsView.y <= y <= self.graphicsView.height:
                node = Node(self.graphicsView, self.current_number_nodes)
                node.setPos(x, y)
                self._node_list.append(node)
                self.scene.addItem(node)
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.current_number_nodes += 1
            else:
                print("Out of view!")
        if self.mode == 'addEdge':
            # print(self.pairNode)
            if len(self.pairNode) == 2:
                self.scene.addItem(Edge(self.pairNode[0], self.pairNode[1]))
                # self._edge_list.append(Edge(self.pairNode[0], self.pairNode[1]))
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.pairNode = []
            
        # print(self.pairNode)

        # self.mode = None
        # print(self._node_list)
        # for item in self._node_list:
        #     # item.focusItemChanged.connect(self.focusChanged)
        #     self.rect_item = Node
        super().mousePressEvent(event)


    def itemClicked(self, item):
        self.update()
        # if item in self._node_list:
        #     print('Node {} clicked!'.format(item))
        # else:
        #     print('Edge {} clicked!'.format(item))
            
        if self.mode == 'delNode' and item in self._node_list:
            self.scene.removeItem(item)
            self._node_list.remove(item)
            self.scene.update()
            # print(item._edge_list)
            self.mode = 'delEdge'
            self.btn_1.setEnabled(1)
            self.btn_2.setEnabled(1)
            self.btn_3.setEnabled(1)
            self.btn_4.setEnabled(1)


        if self.mode == 'delEdge' and item not in self._node_list:
            self.scene.removeItem(item)
            self.scene.update()
            self.btn_1.setEnabled(1)
            self.btn_2.setEnabled(1)
            self.btn_3.setEnabled(1)
            self.btn_4.setEnabled(1)
            # self._edge_list.remove(item)

        if self.mode == 'addEdge' and item in self._node_list:
            if len(self.pairNode) <= 2:
                self.pairNode.append(item)
            # # for i in self.pairNode: 
            # # print(self.pairNode)
            # if len(self.pairNode) == 2:
            #     current_source_node = self.pairNode[0]
            #     current_des_node = self.pairNode[1]
            if len(self.pairNode) > 2:
                    self.pairNode = []
        # print(self._edge_list)
        # print(self.pairNode)
        # print(item._edge_list)

    # def edgeClicked(self, item):
    #     print('Edge {} clicked!'.format(item))

    def addNode(self):
        self.mode = 'addNode'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)

    def addEdge(self):
        self.mode = 'addEdge'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)

    def delNode(self):
        self.mode = 'delNode'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)

    def delEdge(self):
        self.mode = 'delEdge'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)

    def item_moved(self):
        if not self.graphicsView._timer_id:
            self.graphicsView._timer_id = self.startTimer(1000 / 25)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tmp = Ui_MainWindow()
    app.exec_()