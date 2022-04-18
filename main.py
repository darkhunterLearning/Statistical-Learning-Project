import sys
import weakref
import math
from math import inf
import random

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import (QLineF, QPointF, QRandomGenerator, QRectF, QSizeF,
                            Qt, qAbs, pyqtSignal, QRect, QTimer)
from PyQt5.QtGui import (QColor, QBrush, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient, QFont)
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QStyle, QWidget, QGridLayout, QDesktopWidget, QGraphicsLineItem, QMessageBox)

import dijkstra
from collections import defaultdict

class UndirectedEdge(QGraphicsItem):

    item_type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super().__init__()
        self.name = [sourceNode.name, destNode.name]
        self._arrow_size = 5
        self._source_point = QPointF()
        self._dest_point = QPointF()
        self.height = 10
        self.w = random.randint(1,50)
        self.status = 0
        # self.setAcceptedMouseButtons(Qt.NoButton)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        # self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().add_edge(self)
        self.dest().add_edge(self)
        self.adjust()

    def item_type(self):
        return UndirectedEdge.item_type

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

        pen_width = 1
        extra = (pen_width + self._arrow_size) / 2.0

        width = self._dest_point.x() - self._source_point.x()
        height = self._dest_point.y() - self._source_point.y()
        rect = QRectF(self._source_point, QSizeF(width, height))
        return rect.normalized().adjusted(-extra, -extra, extra, extra)


    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return
        if self.status == 0:
            color = Qt.black
        if self.status == 1:
            color = Qt.red
        painter.setPen(QPen(color, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        dx = abs((self._dest_point.x() + self._source_point.x()) / 2)
        dy = abs((self._dest_point.y() + self._source_point.y()) / 2)

        # print(dx, dy)

        painter.setFont(QFont("Arial", 10))
        painter.drawText(dx, dy+20, str(self.w))

        line = QLineF(self._source_point, self._dest_point)
        painter.drawLine(line)

    def mousePressEvent(self, event):
        # self.update()
        # QGraphicsItem.mousePressEvent(self, event)
        super(UndirectedEdge, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.scene().itemClicked.emit(self)

    def mouseReleaseEvent(self, event):
        self.update()
        QGraphicsItem.mouseReleaseEvent(self, event)

    def focusItemChanged(self, newItem, oldItem, reason):
        if newItem and reason == Qt.MouseFocusReason:
            print('item {} clicked!'.format(newItem))

class DirectedEdge(QGraphicsItem):

    item_type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super().__init__()
        self.name = [sourceNode.name, destNode.name]
        self._arrow_size = 5
        self._source_point = QPointF()
        self._dest_point = QPointF()
        self.height = 10
        self.w = random.randint(1, 20)
        self.status = 0
        # self.setAcceptedMouseButtons(Qt.NoButton)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        # self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().add_edge(self)
        self.dest().add_edge(self)
        self.adjust()

    def item_type(self):
        return DirectedEdge.item_type

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

        pen_width = 1
        extra = (pen_width + self._arrow_size) / 2.0

        width = self._dest_point.x() - self._source_point.x()
        height = self._dest_point.y() - self._source_point.y()
        rect = QRectF(self._source_point, QSizeF(width, height))
        return rect.normalized().adjusted(-extra, -extra, extra, extra)

    def calculate(self):
        # print(self._source_point.x(), self._source_point.y())
        # print(self._dest_point.x(), self._dest_point.y())

         # We first calculate the distance covered by our edge
        dX = self._dest_point.x() - self._source_point.x()
        dY = self._dest_point.y() - self._source_point.y()
        distance = math.sqrt(pow(dX, 2) + pow(dY, 2))
        # print("dX, dY, distance:")
        # print(dX, dY, distance)

        # Then we create a straight line from our start point to our end point and shorten its length
        newLine = QLineF(self._source_point, self._dest_point)
        newLine.setLength(newLine.length() - 15);

        # Then we calculate the coordinates of our midpoint
        mX = (self._dest_point.x() + newLine.p2().x()) / 2
        mY = (self._dest_point.y() + newLine.p2().y()) / 2

        # print("mX, mY:")
        # print(mX, mY)

        # And the coordinates of our control point. We use the edges height as a scaling factor
        # to determine the 'height' of the control point on a line perpendicular to our 
        # original line (newLine).
        cX = self.height * (-1 * (dY / distance)) + mX
        cY = self.height * (dX / distance) + mY
        self.controlPoint = QPointF(cX, cY)
        # print('controlPoint')
        # print(self.controlPoint)

        # We create another line from our control point to our end point and shorten its length
        self.ghostLine = QLineF(self.controlPoint, self._dest_point)
        self.ghostLine.setLength(self.ghostLine.length() - 5)
        # print('ghostLine')
        # print(self.ghostLine)

        # Then we do the calculations we need to create our arrowhead
        angle = math.acos(self.ghostLine.dx() / self.ghostLine.length())
        # print(angle)
        if self.ghostLine.dy() >= 0:
            angle = 2 * math.pi - angle

        self.arrowP1 = self.ghostLine.p2() - QPointF(math.sin(angle + math.pi /3) * self._arrow_size, 
                                           math.cos(angle + math.pi / 3) * self._arrow_size)
        self.arrowP2 = self.ghostLine.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3) * self._arrow_size, 
                                           math.cos(angle + math.pi - math.pi / 3) * self._arrow_size)

        # print('arrowP1, arrowP2:')
        # print(self.arrowP1, self.arrowP2)

        # self.setLine(newLine)
        self.prepareGeometryChange()


    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return

        if self.status == 0:
            color = Qt.black
        if self.status == 1:
            color = Qt.red

        painter.setPen(QPen(color, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        self.calculate()
        
        path = QPainterPath()
        path.moveTo(self._source_point)
        path.quadTo(self.controlPoint, self.ghostLine.p2())

        painter.drawPolygon(QPolygonF([self.ghostLine.p2(), self.arrowP1, self.arrowP2]))
        painter.strokePath(path, QPen(color))

        dx = abs((self._dest_point.x() + self._source_point.x()) / 2)
        dy = abs((self._dest_point.y() + self._source_point.y()) / 2)

        # print(self._source_point.y())
        # print(dy)

        painter.setFont(QFont("Arial", 10))

        if self._source_point.x() < dx:
            painter.drawText(self._source_point.x() + 20, dy, str(self.w))
            
        else:
            painter.drawText(self._source_point.x() - 20, dy, str(self.w))
            


    def mousePressEvent(self, event):
        # self.update()
        # QGraphicsItem.mousePressEvent(self, event)
        super(DirectedEdge, self).mousePressEvent(event)
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
        self.status = 0
        # self.setCacheMode(self.DeviceCoordinateCache)
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
        try:
            if change == QGraphicsItem.ItemPositionChange:
                # print(self._edge_list)
                for edge in self._edge_list:
                    edge().adjust()
                # self.item_moved()
        except:
            pass
            # self.update()
        return QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        rect = QRect(-7, -7, 20, 20)
        painter.drawEllipse(rect)

        gradient = QRadialGradient(-3, -3, 10)

        if self.status == 0:
            color1 = QColor(Qt.yellow)
            color2 = QColor(Qt.darkYellow)
        if self.status == 1:
            color1 = QColor(Qt.red)
            color2 = QColor(Qt.darkRed)

        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, color1.lighter(120))
            gradient.setColorAt(0, color2.lighter(120))
        else:
            gradient.setColorAt(0, color1)
            gradient.setColorAt(1, color2)

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

        self.undirected_node_list = []
        self.directed_node_list = []
        self.graph_type = 'Undirected'
        self.adj_undirected_matrix = []
        self.adj_directed_matrix = []
        self.undirected_edges = [] # this var is used for storage edge UI
        self.directed_edges = []
        self.list_undirected_edges = [] # this var is used for storage edge backend
        self.list_directed_edges = []
        self.undirected_current_number_nodes = 0
        self.directed_current_number_nodes = 0
        self.mode = None
        self.undirected_idx = 0
        self.directed_idx = 0
        self.undirected_frames = []
        self.directed_frames = []
        self.undirected_pairNode = []
        self.directed_pairNode = []
        self.all_undirected_path = []
        self.all_directed_path = []
        self.undirected_BFS_result = ''
        self.directed_BFS_result = ''
        self.undirected_DFS_result = ''
        self.directed_DFS_result = ''
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
        self.undirectedView: QtWidgets.QGraphicsView = self.findChild(QtWidgets.QGraphicsView, 'undirectedView')
        self.directedView: QtWidgets.QGraphicsView = self.findChild(QtWidgets.QGraphicsView, 'directedView')
        # self.graphicsView.setEnabled(0)
        # self.graphicsView.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.lbl_head: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_head')
        self.lbl_body: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_body')
        self.lbl_foot: QtWidgets.QLabel = self.findChild(QtWidgets.QLabel, 'lbl_foot')

        self.grb_graph_type: QtWidgets.QGroupBox = self.findChild(QtWidgets.QGroupBox, 'grb_graph_type')

        self.rbtn_undirected: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rbtn_undirected')
        self.rbtn_directed: QtWidgets.QRadioButton = self.findChild(QtWidgets.QRadioButton, 'rbtn_directed')

        self.textbox: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'textbox')

        self.btn_1: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_1')
        self.btn_2: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_2')
        self.btn_3: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_3')
        self.btn_4: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_4')
        self.btn_5: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_5')
        self.btn_6: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_6')
        self.btn_7: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_7')
        self.btn_8: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_8')
        self.btn_9: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_9')
        self.btn_10: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_10')
        self.btn_11: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'btn_11')
        self.btn_6.setEnabled(0)
        self.btn_7.setEnabled(0)
        self.btn_8.setEnabled(0)

        self.spb_source: QtWidgets.QSpinBox = self.findChild(QtWidgets.QSpinBox, 'spb_source')
        self.spb_des: QtWidgets.QSpinBox = self.findChild(QtWidgets.QSpinBox, 'spb_des')

        self.btn_1.clicked.connect(lambda: self.addNode())
        self.btn_2.clicked.connect(lambda: self.addEdge())
        self.btn_3.clicked.connect(lambda: self.delNode())
        self.btn_4.clicked.connect(lambda: self.delEdge())
        self.btn_5.clicked.connect(lambda: self.setEdgeW())
        self.btn_6.clicked.connect(lambda: self.Dijkstra())
        self.btn_7.clicked.connect(lambda: self.refresh())
        self.btn_8.clicked.connect(lambda: self.allPath())
        self.btn_9.clicked.connect(lambda: self.BellmanFord())
        self.btn_10.clicked.connect(lambda: self.BFS())
        self.btn_11.clicked.connect(lambda: self.DFS())

        self.rbtn_undirected.toggled.connect(self.graphType)
        # self.rbtn_directed.toggled.connect(self.graphType)


        self.create_ui()

        self.show()

    def create_ui(self):
        self.undirectedView._timer_id = 0
        self.directedView._timer_id = 0
        self.scene_1 = ItemClickableGraphicsScene(self)
        self.scene_2 = ItemClickableGraphicsScene(self)
        self.scene_1.itemClicked.connect(self.itemClicked)
        self.scene_2.itemClicked.connect(self.itemClicked)
        # self.scene.itemClicked.connect(self.edgeClicked)
        self.scene_1.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.scene_2.setItemIndexMethod(QGraphicsScene.NoIndex)
        # self.scene.focusItemChanged.connect(self.focusChanged)

        self.undirectedView.x = self.undirectedView.x()
        self.undirectedView.y = self.undirectedView.y()
        self.undirectedView.width = self.undirectedView.width()
        self.undirectedView.height = self.undirectedView.height()

        self.scene_1.setSceneRect(self.undirectedView.x, self.undirectedView.y, self.undirectedView.width, self.undirectedView.height)
        self.undirectedView.setScene(self.scene_1)
        self.undirectedView.setCacheMode(QGraphicsView.CacheBackground)
        self.undirectedView.setRenderHint(QPainter.Antialiasing)
        self.undirectedView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.undirectedView.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.directedView.x = self.directedView.x()
        self.directedView.y = self.directedView.y()
        self.directedView.width = self.directedView.width()
        self.directedView.height = self.directedView.height()

        self.scene_2.setSceneRect(self.directedView.x, self.directedView.y, self.directedView.width, self.directedView.height)
        self.directedView.setScene(self.scene_2)
        self.directedView.setCacheMode(QGraphicsView.CacheBackground)
        self.directedView.setRenderHint(QPainter.Antialiasing)
        self.directedView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.directedView.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def mousePressEvent(self, event):
        if self.graph_type == 'Undirected':
            p = event.pos() # relative to widget
            # print(p)
            # gp = self.graphicsView.mapToGlobal(p) # relative to screen
            # print(gp)
            # rw = self.graphicsView.window().mapFromGlobal(gp) # relative to window
            # print(rw)
            x, y = int(p.x()), int(p.y())
            # print(x, y)
            if self.mode == 'addNode':
                if self.undirectedView.x <= x <= self.undirectedView.x + self.undirectedView.width and self.undirectedView.y <= y <= self.undirectedView.y + self.undirectedView.height:
                    node = Node(self.undirectedView, self.undirected_current_number_nodes)
                    node.setPos(x, y)

                    self.undirected_node_list.append(node)
                    self.scene_1.addItem(node)

                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)
                    self.btn_6.setEnabled(1)
                    self.btn_7.setEnabled(1)
                    self.btn_8.setEnabled(1)

                    self.undirected_current_number_nodes += 1

                    self.adj_undirected_matrix = []

                    for i in range(self.undirected_current_number_nodes):
                        self.adj_undirected_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                    # change adj_matrix after this based on self.undirected_edges
                    for x, y, w in self.undirected_edges:
                       self.adj_undirected_matrix[int(x)][int(y)] = w
                       self.adj_undirected_matrix[int(y)][int(x)] = w

                    self.mode = None
                else:
                    print("Out of view!")
            if self.mode == 'addEdge':
                # print(self.pairNode)
                if len(self.undirected_pairNode) == 2:
                    edge = UndirectedEdge(self.undirected_pairNode[0], self.undirected_pairNode[1])
                    edge_2 = UndirectedEdge(self.undirected_pairNode[1], self.undirected_pairNode[0])

                    self.list_undirected_edges.append(edge)
                    self.list_undirected_edges.append(edge_2)

                    self.scene_1.addItem(edge)
                    self.undirected_edges.append([self.undirected_pairNode[0].name, self.undirected_pairNode[1].name, edge.w])
                    
                    self.adj_undirected_matrix = []

                    for i in range(self.undirected_current_number_nodes):
                        self.adj_undirected_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                    # change adj_matrix after this based on self.undirected_edges
                    for x, y, w in self.undirected_edges:
                       self.adj_undirected_matrix[int(x)][int(y)] = w
                       self.adj_undirected_matrix[int(y)][int(x)] = w

                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)
                    self.undirected_pairNode = []
                    self.mode = None
            
        if self.graph_type == 'Directed':
            p = event.pos() # relative to widget
            x, y = int(p.x()), int(p.y())
            # print(x, y)
            if self.mode == 'addNode':
                if self.directedView.x <= x <= self.directedView.x + self.directedView.width and self.directedView.y <= y <= self.directedView.y + self.directedView.height:
                    node = Node(self.directedView, self.directed_current_number_nodes)
                    node.setPos(x, y)

                    self.directed_node_list.append(node)
                    self.scene_2.addItem(node)

                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)

                    self.directed_current_number_nodes += 1
                    self.adj_directed_matrix = []


                    for i in range(self.directed_current_number_nodes):
                        self.adj_directed_matrix.append([0 for i in range(self.directed_current_number_nodes)])
                    # change adj_matrix after this based on self.directed_edges
                    for x, y, w in self.directed_edges:
                       self.adj_directed_matrix[int(x)][int(y)] = w

                    # for m in self.adj_directed_matrix:
                    #     print(m)

                    self.mode = None
                else:
                    print("Out of view!")
            if self.mode == 'addEdge':
                # print(self.pairNode)
                if len(self.directed_pairNode) == 2:
                    edge = DirectedEdge(self.directed_pairNode[0], self.directed_pairNode[1])

                    self.list_directed_edges.append(edge)

                    self.scene_2.addItem(edge)

                    self.directed_edges.append([self.directed_pairNode[0].name, self.directed_pairNode[1].name, edge.w])

                    self.adj_directed_matrix = []

                    for i in range(self.directed_current_number_nodes):
                        self.adj_directed_matrix.append([0 for i in range(self.directed_current_number_nodes)])
                    # change adj_matrix after this based on self.directed_edges
                    for x, y, w in self.directed_edges:
                       self.adj_directed_matrix[int(x)][int(y)] = w

                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)
                    self.directed_pairNode = []
                    self.mode = None

                    # for m in self.adj_directed_matrix:
                    #     print(m)

        # self.mode = None
        # print(self._node_list)
        # for item in self._node_list:
        #     # item.focusItemChanged.connect(self.focusChanged)
        #     self.rect_item = Node
        super().mousePressEvent(event)


    def itemClicked(self, item):
        # if item in self.undirected_node_list:
        #     print('Node {} clicked!'.format(item.name))
        # else:
        #     print('Edge {} clicked!'.format(item.name))
        
        if self.graph_type == 'Undirected':
            self.scene_1.update()
            # for m in self.adj_undirected_matrix:
            #     print(m)
            if self.mode == 'delNode' and item in self.undirected_node_list:
                tmp = 0
                # Verify edge before delete
                self.undirected_edges = [edge for edge in self.undirected_edges if item.name not in edge]

                for edge in self.undirected_edges:
                        edge[0] -= 1
                        edge[1] -= 1
                
                for edge in self.list_undirected_edges:
                    if item.name in edge.name:
                        self.list_undirected_edges.remove(edge)

                self.scene_1.removeItem(item)
                self.undirected_node_list.remove(item)
                self.undirected_current_number_nodes -= 1

                for node in self.undirected_node_list:
                    node.name = tmp
                    tmp += 1

                self.scene_1.update()
                self.undirectedView.update()
               
                self.adj_undirected_matrix = []
                for i in range(self.undirected_current_number_nodes):
                    self.adj_undirected_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                # change adj_matrix after this based on self.undirected_edges
                try:
                    for x, y, w in self.undirected_edges:
                        if item.name == x or item.name == y:
                            self.adj_undirected_matrix[int(x)][int(y)] = 0
                            self.adj_undirected_matrix[int(y)][int(x)] = 0
                        self.adj_undirected_matrix[int(x)][int(y)] = w
                        self.adj_undirected_matrix[int(y)][int(x)] = w
                except:
                    print("Error!")

                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.mode = None


            if self.mode == 'delEdge' and item  not in self.undirected_node_list:

                for edge in self.undirected_edges:
                        if item.name[0] == edge[0] and item.name[1] == edge[1]:
                            self.undirected_edges.remove(edge)

                self.list_undirected_edges.remove(item)

                if item.name in self.undirected_edges:
                     self.undirected_edges.remove(item.name)

                self.adj_undirected_matrix = []
                for i in range(self.undirected_current_number_nodes):
                    self.adj_undirected_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                # change adj_matrix after this based on self.undirected_edges
                for x, y, w in self.undirected_edges:
                       self.adj_undirected_matrix[int(x)][int(y)] = w
                       self.adj_undirected_matrix[int(y)][int(x)] = w

                self.scene_1.removeItem(item)
                self.scene_1.update()
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.mode = None
                # self._edge_list.remove(item)

            if self.mode == 'addEdge' and item in self.undirected_node_list:
                if len(self.undirected_pairNode) <= 2:
                    self.undirected_pairNode.append(item)
                if len(self.undirected_pairNode) > 2:
                        self.undirected_pairNode = []

            if self.mode == 'setEdgeW':
                number = self.textbox.text()
                try:
                    number = int(number)
                    item.w = number
                    for edge in self.undirected_edges:
                        if item.name[0] == edge[0] and item.name[1] == edge[1]:
                            edge[2] = number
                        
                    self.adj_undirected_matrix[item.name[0]][item.name[1]] = number
                    self.adj_undirected_matrix[item.name[1]][item.name[0]] = number
                except Exception:
                    QMessageBox.about(self, 'Error','Input can only be a number')
                    pass
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.btn_6.setEnabled(1)
                self.btn_7.setEnabled(1)
                self.btn_8.setEnabled(1)
                self.mode = None

        if self.graph_type == 'Directed':
            self.scene_2.update()
            # for m in self.adj_directed_matrix:
            #     print(m)

            if self.mode == 'delNode' and item in self.directed_node_list:  

                tmp = 0
                # Verify edge before delete
                self.directed_edges = [edge for edge in self.directed_edges if item.name not in edge]

                for edge in self.directed_edges:
                        edge[0] -= 1
                        edge[1] -= 1
                
                for edge in self.list_directed_edges:
                    if item.name in edge.name:
                        self.list_directed_edges.remove(edge)

                self.scene_2.removeItem(item)
                self.directed_node_list.remove(item)
                self.directed_current_number_nodes -= 1

                for node in self.directed_node_list:
                    node.name = tmp
                    tmp += 1

                self.scene_2.update()
                self.directedView.update()
               
                self.adj_directed_matrix = []
                for i in range(self.directed_current_number_nodes):
                    self.adj_directed_matrix.append([0 for i in range(self.directed_current_number_nodes)])
                # change adj_matrix after this based on self.undirected_edges
                try:
                    for x, y, w in self.directed_edges:
                        if item.name == x or item.name == y:
                            self.adj_directed_matrix[int(x)][int(y)] = 0
                        self.adj_directed_matrix[int(x)][int(y)] = w
                except:
                    print("Error!")

                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.mode = None

            if self.mode == 'delEdge' and item  not in self.directed_node_list:

                for edge in self.directed_edges:
                        if item.name[0] == edge[0] and item.name[1] == edge[1]:
                            self.directed_edges.remove(edge)

                self.list_directed_edges.remove(item)

                if item.name in self.directed_edges:
                     self.directed_edges.remove(item.name)

                self.adj_directed_matrix = []
                for i in range(self.directed_current_number_nodes):
                    self.adj_directed_matrix.append([0 for i in range(self.directed_current_number_nodes)])
                # change adj_matrix after this based on self.undirected_edges
                for x, y, w in self.directed_edges:
                       self.adj_directed_matrix[int(x)][int(y)] = w

                self.scene_2.removeItem(item)
                self.scene_2.update()
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.mode = None
                # self._edge_list.remove(item)

            if self.mode == 'addEdge' and item in self.directed_node_list:
                if len(self.directed_pairNode) <= 2:
                    self.directed_pairNode.append(item)
                if len(self.directed_pairNode) > 2:
                        self.directed_pairNode = []


            if self.mode == 'setEdgeW':
                number = self.textbox.text()
                # try:
                number = int(number)
                item.w = number
                for edge in self.directed_edges:
                    if item.name[0] == edge[0] and item.name[1] == edge[1]:
                        edge[2] = number
                    
                self.adj_directed_matrix[item.name[0]][item.name[1]] = number
                    
                # except Exception:
                #     QMessageBox.about(self, 'Error','Input can only be a number')
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.btn_6.setEnabled(1)
                self.btn_7.setEnabled(1)
                self.btn_8.setEnabled(1)
                self.mode = None
    # def edgeClicked(self, item):
    #     print('Edge {} clicked!'.format(item))

    def addNode(self):
        self.mode = 'addNode'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)
        self.btn_5.setEnabled(0)

    def addEdge(self):
        self.mode = 'addEdge'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)
        self.btn_5.setEnabled(0)

    def delNode(self):
        self.mode = 'delNode'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)
        self.btn_5.setEnabled(0)

    def delEdge(self):
        self.mode = 'delEdge'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)
        self.btn_5.setEnabled(0)

    def setEdgeW(self):
        self.mode = 'setEdgeW'
        self.btn_1.setEnabled(0)
        self.btn_2.setEnabled(0)
        self.btn_3.setEnabled(0)
        self.btn_4.setEnabled(0)
        self.btn_5.setEnabled(0)
        self.textbox.setEnabled(1)

    def Dijkstra(self):
        self.lbl_head.setText('''
        function Dijkstra(Graph, source):
            for each vertex v in Graph.Vertices:
                dist[v] ← INFINITY
                prev[v] ← UNDEFINED
                add v to Q
                dist[source] ← 0 
                               ''')
        # for m in self.adj_undirected_matrix: 
        #     print(m)
        self.lbl_body.setText('''
            while Q is not empty:
                u ← vertex in Q with min dist[u]
                remove u from Q
                            ''')
        self.lbl_foot.setText('''
            for each neighbor v of u still in Q:
                alt ← dist[u] + Graph.Edges(u, v)
                if alt < dist[v]:              
                    dist[v] ← alt
                    prev[v] ← u
                            ''')
        start = self.spb_source.value()
        end = self.spb_des.value()
        self.lbl_head.setStyleSheet("background-color:green")
        if self.graph_type == 'Undirected':
            n = len(self.adj_undirected_matrix)
            dist = [inf]*n
            dist[start] = self.adj_undirected_matrix[start][start]  # 0
            spVertex = [False]*n
            parent = [-1]*n
            path = [{}]*n

            if not self.undirected_frames: 
                for count in range(n):
                    minix = inf
                    u = 0

                    for v in range(len(spVertex)):
                        if spVertex[v] == False and dist[v] <= minix:
                            minix = dist[v]
                            u = v
                    spVertex[u] = True
                    self.undirected_frames.append([u])
                    for v in range(n):
                        if not(spVertex[v]) and self.adj_undirected_matrix[u][v] != 0 and dist[u] + self.adj_undirected_matrix[u][v] < dist[v]:

                            parent[v] = u
                            dist[v] = dist[u] + self.adj_undirected_matrix[u][v]
                        if self.adj_undirected_matrix[u][v] != 0:                
                            self.undirected_frames.append([u, v])
                
                for i in range(n):
                    j = i
                    s = []
                    while parent[j] != -1:
                        s.append(j)
                        j = parent[j]
                    s.append(start)
                    path[i] = s[::-1]

                # if end >= 0:
                #     print(dist[end], path[end])  
                # else: 
                #     print(dist, path)
        
            try:
                # print(self.undirected_frames[self.undirected_idx])
                if len(self.undirected_frames[self.undirected_idx]) == 1:
                    self.undirected_node_list[self.undirected_frames[self.undirected_idx][0]].status = 1
                    self.lbl_body.setStyleSheet("background-color:yellow")
                    self.lbl_foot.setStyleSheet("background-color:white")
                else:
                    self.lbl_body.setStyleSheet("background-color:white")
                    self.lbl_foot.setStyleSheet("background-color:yellow")
                    # for edge in self.list_undirected_edges:
                    #     edge.status = 0
                    for edge in self.list_undirected_edges:
                        if self.undirected_frames[self.undirected_idx] == edge.name:
                            edge.status = 1
                        else:
                            edge.status = 0
                self.undirected_idx += 1
                self.scene_1.update()
            except:
                for edge in self.list_undirected_edges:
                    edge.status = 0
                shortest_path = dijkstra.find_shortest_path(self.adj_undirected_matrix, start, end)
                shortest_dis = dijkstra.find_shortest_distance(self.adj_undirected_matrix, start, end)
                # print(shortest_path)
                list_edges = list(zip(shortest_path, shortest_path[1:]))
                list_edges = [list(edge) for edge in list_edges]
                # print(list_edges)
                # [print(edge.name) for edge in self.list_undirected_edges]
                for edge in self.list_undirected_edges:
                    for path_edge in list_edges:
                        if edge.name == path_edge:
                            edge.status = 1
                            # print(str(edge.name)+ ' and ' + str(path_edge))

                self.lbl_head.setStyleSheet("background-color:white")
                self.lbl_body.setStyleSheet("background-color:white")
                self.lbl_foot.setStyleSheet("background-color:white")
                self.scene_1.update()
                QMessageBox.about(self, 'Done','Shortest path from ' + str(start) + ' to ' + str(end) + 
                                            ' is ' + str(shortest_path) + '. Length ' + str(shortest_dis))
        else:
            # print(dijkstra.find_shortest_path(self.adj_directed_matrix, start, end))
            n = len(self.adj_directed_matrix)
            dist = [inf]*n
            dist[start] = self.adj_directed_matrix[start][start]  # 0
            spVertex = [False]*n
            parent = [-1]*n
            path = [{}]*n

            if not self.directed_frames: 
                for count in range(n):
                    minix = inf
                    u = 0

                    for v in range(len(spVertex)):
                        if spVertex[v] == False and dist[v] <= minix:
                            minix = dist[v]
                            u = v
                    spVertex[u] = True
                    self.directed_frames.append([u])
                    for v in range(n):
                        if not(spVertex[v]) and self.adj_directed_matrix[u][v] != 0 and dist[u] + self.adj_directed_matrix[u][v] < dist[v]:
                            parent[v] = u
                            dist[v] = dist[u] + self.adj_directed_matrix[u][v]
                        if self.adj_directed_matrix[u][v] != 0:                
                            self.directed_frames.append([u, v])
                
                for i in range(n):
                    j = i
                    s = []
                    while parent[j] != -1:
                        s.append(j)
                        j = parent[j]
                    s.append(start)
                    path[i] = s[::-1]

                # if end >= 0:
                #     print(dist[end], path[end])  
                # else: 
                #     print(dist, path)
        
            try:
                # print(self.directed_frames[self.directed_idx])
                if len(self.directed_frames[self.directed_idx]) == 1:
                    self.directed_node_list[self.directed_frames[self.directed_idx][0]].status = 1
                    self.lbl_body.setStyleSheet("background-color:yellow")
                    self.lbl_foot.setStyleSheet("background-color:white")
                else:
                    self.lbl_body.setStyleSheet("background-color:white")
                    self.lbl_foot.setStyleSheet("background-color:yellow")
                    for edge in self.list_directed_edges:
                        edge.status = 0
                    for edge in self.list_directed_edges:
                        if self.directed_frames[self.directed_idx] == edge.name:
                            edge.status = 1
                self.directed_idx += 1
                self.scene_2.update()
            except:
                for edge in self.list_directed_edges:
                    edge.status = 0
                shortest_path = dijkstra.find_shortest_path(self.adj_directed_matrix, start, end)
                shortest_dis = dijkstra.find_shortest_distance(self.adj_directed_matrix, start, end)
                print(shortest_path)
                list_edges = list(zip(shortest_path, shortest_path[1:]))
                list_edges = [list(edge) for edge in list_edges]

                for edge in self.list_directed_edges:
                    for path_edge in list_edges:
                        if edge.name == path_edge:
                            edge.status = 1
                            # print(str(edge.name)+ ' and ' + str(path_edge))
                self.lbl_head.setStyleSheet("background-color:white")
                self.lbl_body.setStyleSheet("background-color:white")
                self.lbl_foot.setStyleSheet("background-color:white")
                self.scene_2.update()
                QMessageBox.about(self, 'Done','Shortest path from ' + str(start) + ' to ' + str(end) + 
                                            ' is ' + str(shortest_path) + '. Length ' + str(shortest_dis))

    def BellmanFord(self):
        # print('BellmanFord')
        # print('Undirected')
        # for x, y, w in self.undirected_edges:
        #     print(x, y, w)
        # print('----------')
        # print('Directed')
        # for x, y, w in self.directed_edges:
        #     print(x, y, w)
        self.lbl_head.setText('''
        function bellmanFord(Graph, source):
            for each vertex v in Graph.Vertices:
                dist[v] ← INFINITY
                prev[v] ← UNDEFINED
            dist[source] ← 0 
                               ''')
        # for m in self.adj_undirected_matrix: 
        #     print(m)
        self.lbl_body.setText('''
            for each vertex v in Graph.Vertices:           
                for each edge (U,V) in Graph.Edges:
                    tempDistance ← distance[U] + edge_weight(U, V)
                    if tempDistance < distance[V]:
                        distance[V] ← tempDistance
                        previous[V] ← U
                            ''')
        self.lbl_foot.setText('''
            for each edge (U,V) in Graph.Edges:
                If distance[U] + edge_weight(U, V) < distance[V]:
                    Error: Negative Cycle Exists
                            ''')


        start = self.spb_source.value()
        end = self.spb_des.value()

        if self.graph_type == 'Undirected':
            dist = [inf] * self.undirected_current_number_nodes
            dist[start] = 0
            # print(dist)
            list_frames = []

            for _ in range(self.undirected_current_number_nodes):
                list_frames.append([_])
                for u, v, w in self.undirected_edges:
                    if u == _ :
                        list_frames.append([u, v])
                if _ == self.undirected_current_number_nodes - 1:    
                    list_frames.append([-1])
            # print(duplicate(list_frames, self.directed_current_number_nodes))

            for _ in range(self.undirected_current_number_nodes - 1):
                # Update dist value and parent index of the adjacent vertices of
                # the picked vertex. Consider only those vertices which are still in
                # queue
                for u, v, w in self.undirected_edges:
                #     # print('dist[u] ' + str(dist[u]))
                #     # print('u ' + str(u))
                    # print('u: ' + str(u) + ' v: ' + str(v))
                    if dist[u] != inf and dist[u] + w < dist[v]:
                            dist[v] = dist[u] + w
                #             # print('dist[v] ' + str(dist[v]))
                #             print('u: ' + str(u) + ' v: ' + str(v))
            hasNegativeCycle = False
            for u, v, w in self.undirected_edges:
                    if dist[u] != inf and dist[u] + w < dist[v]:
                            # print("Graph contains negative weight cycle")
                            hasNegativeCycle = True
                            break

            self.undirected_frames = duplicate(list_frames, self.undirected_current_number_nodes)
            
            if hasNegativeCycle:
                    self.lbl_foot.setStyleSheet("background-color:red")
                    QMessageBox.about(self, 'Done','Graph contains negative weight cycle')
            else:
                try:
                    # print(self.directed_frames[self.directed_idx])
                    self.lbl_body.setStyleSheet("background-color:yellow")
                    if len(self.undirected_frames[self.undirected_idx]) == 1:
                        if self.undirected_frames[self.undirected_idx][0] == -1:
                            for node in self.undirected_node_list:
                                node.status = 0
                            for edge in self.list_undirected_edges:
                                edge.status = 0

                        else:
                            self.undirected_node_list[self.undirected_frames[self.undirected_idx][0]].status = 1  
                    else:
                        for edge in self.list_undirected_edges:
                            edge.status = 0
                        for edge in self.list_undirected_edges:
                            if self.undirected_frames[self.undirected_idx] == edge.name:
                                edge.status = 1
                    self.undirected_idx += 1
                    self.scene_1.update()
                except:
                    for edge in self.list_undirected_edges:
                        edge.status = 0

                    # print("Vertex Distance from Source")
                    # for i in range(self.directed_current_number_nodes):
                    #     print("{0}\t\t{1}".format(i, dist[i]))

                    
                    self.lbl_head.setStyleSheet("background-color:white")
                    self.lbl_body.setStyleSheet("background-color:white")
                    self.lbl_foot.setStyleSheet("background-color:white")
                    self.scene_1.update()

                    text_info = ''
                    for i in range(self.undirected_current_number_nodes):
                        path = "Shortest path length from {0} to {1} is {2}".format(start, i, dist[i])
                        text_info += path + '\n' 
                    
                    QMessageBox.about(self, 'Vertex Distance from Source', text_info)
        else:
            dist = [inf] * self.directed_current_number_nodes
            dist[start] = 0
            # print(dist)
            list_frames = []

            for _ in range(self.directed_current_number_nodes):
                list_frames.append([_])
                for u, v, w in self.directed_edges:
                    if u == _ :
                        list_frames.append([u, v])
                if _ == self.directed_current_number_nodes - 1:    
                    list_frames.append([-1])
            # print(duplicate(list_frames, self.directed_current_number_nodes))

            for _ in range(self.directed_current_number_nodes - 1):
                # Update dist value and parent index of the adjacent vertices of
                # the picked vertex. Consider only those vertices which are still in
                # queue
                for u, v, w in self.directed_edges:
                #     # print('dist[u] ' + str(dist[u]))
                #     # print('u ' + str(u))
                    # print('u: ' + str(u) + ' v: ' + str(v))
                    if dist[u] != inf and dist[u] + w < dist[v]:
                            dist[v] = dist[u] + w
                #             # print('dist[v] ' + str(dist[v]))
                #             print('u: ' + str(u) + ' v: ' + str(v))
            hasNegativeCycle = False
            for u, v, w in self.directed_edges:
                    if dist[u] != inf and dist[u] + w < dist[v]:
                            # print("Graph contains negative weight cycle")
                            hasNegativeCycle = True
                            break

            self.directed_frames = duplicate(list_frames, self.directed_current_number_nodes)

            if hasNegativeCycle:
                    self.lbl_foot.setStyleSheet("background-color:red")
                    QMessageBox.about(self, 'Done','Graph contains negative weight cycle')
            else:
                try:
                    # print(self.directed_frames[self.directed_idx])
                    self.lbl_body.setStyleSheet("background-color:yellow")
                    if len(self.directed_frames[self.directed_idx]) == 1:
                        if self.directed_frames[self.directed_idx][0] == -1:
                            for node in self.directed_node_list:
                                node.status = 0
                            for edge in self.list_directed_edges:
                                edge.status = 0

                        else:
                            self.directed_node_list[self.directed_frames[self.directed_idx][0]].status = 1  
                    else:
                        for edge in self.list_directed_edges:
                            edge.status = 0
                        for edge in self.list_directed_edges:
                            if self.directed_frames[self.directed_idx] == edge.name:
                                edge.status = 1
                    self.directed_idx += 1
                    self.scene_2.update()
                except:
                    for edge in self.list_directed_edges:
                        edge.status = 0

                    # print("Vertex Distance from Source")
                    # for i in range(self.directed_current_number_nodes):
                    #     print("{0}\t\t{1}".format(i, dist[i]))

                    
                    self.lbl_head.setStyleSheet("background-color:white")
                    self.lbl_body.setStyleSheet("background-color:white")
                    self.lbl_foot.setStyleSheet("background-color:white")
                    self.scene_2.update()

                    text_info = ''
                    for i in range(self.directed_current_number_nodes):
                        path = "Shortest path length from {0} to {1} is {2}".format(start, i, dist[i])
                        text_info += path + '\n' 
                    
                    QMessageBox.about(self, 'Vertex Distance from Source', text_info)

        # print(duplicate(list_frames, self.directed_current_number_nodes))

    def BFS(self):
        self.lbl_head.setText('''
        procedure BFS(G, root) is
            let Q be a queue
            label root as explored
            Q.enqueue(root) 
                             ''')
        # for m in self.adj_undirected_matrix: 
        #     print(m)
        self.lbl_body.setText('''
            while Q is not empty do
                v := Q.dequeue()
                if v is the goal then
                    return v
                            ''')
        self.lbl_foot.setText('''
                for all edges from v to w in G.adjacentEdges(v) do
                    if w is not labeled as explored then
                        label w as explored
                        Q.enqueue(w)
                            ''')
        start = self.spb_source.value()
        end = self.spb_des.value()
        
        if self.graph_type == 'Undirected':
            if not self.undirected_frames: 
                visited = [False] * self.undirected_current_number_nodes
                q = [start]
         
                # Set source as visited
                visited[start] = True
         
                while q:
                    vis = q[0]
         
                    # Print current node
                    # print(vis, end = ' ')
                    # print(vis)
                    self.undirected_BFS_result += str(vis) + ' '
                    self.undirected_frames.append([vis])
                    q.pop(0)
                     
                    # For every adjacent vertex to
                    # the current vertex
                    for i in range(self.undirected_current_number_nodes):
                        if (self.adj_undirected_matrix[vis][i] != 0 and
                              (not visited[i])):
                                   
                            # Push the adjacent node
                            # in the queue
                            q.append(i)
                             
                            # set
                            visited[i] = True
                            # print(vis, i)
                            self.undirected_frames.append([vis, i])

            # print(self.undirected_frames)
            try:
                # print(self.undirected_frames[self.undirected_idx])
                if len(self.undirected_frames[self.undirected_idx]) == 1:
                    self.undirected_node_list[self.undirected_frames[self.undirected_idx][0]].status = 1
                    self.lbl_body.setStyleSheet("background-color:orange")
                    self.lbl_foot.setStyleSheet("background-color:yellow")
                else:
                    self.lbl_body.setStyleSheet("background-color:white")
                    # self.lbl_foot.setStyleSheet("background-color:yellow")
                    # for edge in self.list_undirected_edges:
                    #     edge.status = 0
                    for edge in self.list_undirected_edges:
                        if self.undirected_frames[self.undirected_idx] == edge.name:
                            edge.status = 1
                self.undirected_idx += 1
                self.scene_1.update()
            except:
                for edge in self.list_undirected_edges:
                    edge.status = 0
                # self.lbl_head.setStyleSheet("background-color:white")
                self.lbl_body.setStyleSheet("background-color:white")
                self.lbl_foot.setStyleSheet("background-color:white")
                self.scene_1.update()
                QMessageBox.about(self, 'Done', "BFS's result: " + self.undirected_BFS_result)
        else:
            if not self.directed_frames: 
                visited = [False] * self.directed_current_number_nodes
                q = [start]
         
                # Set source as visited
                visited[start] = True
         
                while q:
                    vis = q[0]
         
                    # Print current node
                    # print(vis, end = ' ')
                    # print(vis)
                    self.directed_BFS_result += str(vis) + ' '
                    self.directed_frames.append([vis])
                    q.pop(0)
                     
                    # For every adjacent vertex to
                    # the current vertex
                    for i in range(self.directed_current_number_nodes):
                        if (self.adj_directed_matrix[vis][i] != 0 and
                              (not visited[i])):
                                   
                            # Push the adjacent node
                            # in the queue
                            q.append(i)
                             
                            # set
                            visited[i] = True
                            # print(vis, i)
                            self.directed_frames.append([vis, i])

            # print(self.undirected_frames)
            try:
                # print(self.undirected_frames[self.undirected_idx])
                if len(self.directed_frames[self.directed_idx]) == 1:
                    self.directed_node_list[self.directed_frames[self.directed_idx][0]].status = 1
                    self.lbl_body.setStyleSheet("background-color:orange")
                    self.lbl_foot.setStyleSheet("background-color:yellow")
                else:
                    self.lbl_body.setStyleSheet("background-color:white")
                    # self.lbl_foot.setStyleSheet("background-color:yellow")
                    # for edge in self.list_undirected_edges:
                    #     edge.status = 0
                    for edge in self.list_directed_edges:
                        if self.directed_frames[self.directed_idx] == edge.name:
                            edge.status = 1
                self.directed_idx += 1
                self.scene_2.update()
            except:
                for edge in self.list_directed_edges:
                    edge.status = 0
                # self.lbl_head.setStyleSheet("background-color:white")
                self.lbl_body.setStyleSheet("background-color:white")
                self.lbl_foot.setStyleSheet("background-color:white")
                self.scene_2.update()
                QMessageBox.about(self, 'Done', "BFS's result: " + self.directed_BFS_result)

    def DFS(self):
        # print('DFS')

        start = self.spb_source.value()
        end = self.spb_des.value()

        if self.graph_type == 'Undirected':
            if not self.undirected_frames: 
                adj_list = matrixToList(self.adj_undirected_matrix)
                input_matrix = list(adj_list.values())

                # for m in self.adj_undirected_matrix:
                #     print(m)

                # for m in test_list:
                #     print(m)

                # Create a array of visited node
                visited = [False for i in range(self.undirected_current_number_nodes)]
             
                # Vector to track last visited road
                road_used = []
             
                # Initialize all the node with false
                for i in range(self.undirected_current_number_nodes):
                    visited[i] = False
             
                # Call the function
                try:
                    self.undirected_frames = dfsUtil(start, self.undirected_current_number_nodes, visited, road_used, -1, 0, input_matrix)
                except:
                    self.undirected_frames.append([-1])

              
            if self.undirected_frames[0][0] == -1:
                QMessageBox.about(self, 'Warning', "DFS implement for connected undirected graph only! Please try again!")
            else:
                try:
                    self.undirected_node_list[self.undirected_frames[self.undirected_idx][0]].status = 1

                    for node in self.undirected_node_list:
                        if self.undirected_frames[self.undirected_idx][0] != node.name: 
                            node.status = 0

                    self.undirected_idx += 1
                    self.scene_1.update()
                except:
                    for node in self.undirected_node_list:
                        node.status = 0
                    # self.lbl_head.setStyleSheet("background-color:white")
                    self.scene_1.update()
                    QMessageBox.about(self, 'Done', "DFS's result: " + str(self.undirected_frames))

        else:
            QMessageBox.about(self, 'Warning', "DFS implement for connected undirected graph only! Please try again!")


    def refresh(self):
        for node in self.undirected_node_list:
            node.status = 0
        for node in self.directed_node_list:
            node.status = 0
        for edge in self.list_undirected_edges:
            edge.status = 0
        for edge in self.list_directed_edges:
            edge.status = 0
        self.directed_frames = []
        self.undirected_frames = []
        self.undirected_idx = 0
        self.directed_idx = 0
        self.undirected_BFS_result = ''
        self.directed_BFS_result = ''
        self.lbl_head.setStyleSheet("background-color:white")
        self.lbl_body.setStyleSheet("background-color:white")
        self.lbl_foot.setStyleSheet("background-color:white")
        self.scene_1.update()
        self.scene_2.update()
        # print('OK')

    def allPath(self):
        start = self.spb_source.value()
        end = self.spb_des.value()
        # self.all_undirected_path = []
        # self.all_directed_path = []
        if self.graph_type == 'Undirected':
            for node in range(self.undirected_current_number_nodes):
                path = dijkstra.find_shortest_path(self.adj_undirected_matrix, start, node)
                path_length = dijkstra.find_shortest_distance(self.adj_undirected_matrix, start, node)
                txt = 'Shortest path from ' + str(start) + ' to ' + str(node) + ' is ' + str(path) + '. Length ' + str(path_length)
                self.all_undirected_path.append(txt)
            # print(self.all_undirected_path)
            text_info = ''
            for path in self.all_undirected_path:
                text_info += path + '\n' 
            QMessageBox.about(self, 'All path', text_info)
        else:
            for node in range(self.directed_current_number_nodes):
                path = dijkstra.find_shortest_path(self.adj_directed_matrix, start, node)
                path_length = dijkstra.find_shortest_distance(self.adj_directed_matrix, start, node)
                txt = 'Shortest path from ' + str(start) + ' to ' + str(node) + ' is ' + str(path) + '. Length ' + str(path_length)
                self.all_directed_path.append(txt)

            text_info = ''
            for path in self.all_directed_path:
                text_info += path + '\n' 
            QMessageBox.about(self, 'All path', text_info)

    def item_moved(self):
        if not self.graphicsView._timer_id:
            self.graphicsView._timer_id = self.startTimer(1000 / 25)

    def graphType(self):
        if self.rbtn_directed.isChecked():
            self.graph_type = 'Directed'
        else:
            self.graph_type = 'Undirected'

        # print(self.graph_type)

def duplicate(testList, n):
    return testList*n

def matrixToList(a):
    adjList = defaultdict(list)
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] != 0:
               adjList[i].append(j)
    return adjList

# Function to print the complete DFS-traversal
def dfsUtil(u, node, visited, road_used, parent, it, adj, result=None):

    if result is None:  # create a new result if no intermediate was given
        result = []

    c = 0
 
    # Check if all th node is visited
    # or not and count unvisited nodes
    for i in range(node):
        if (visited[i]):
            c += 1
 
    # If all the node is visited return
    if (c == node):
        return
 
    # Mark not visited node as visited
    visited[u] = True
 
    # Track the current edge
    road_used.append([parent, u])
    # print(road_used)
    # Print the node
    result.append([u])
    # print(u, end = " ")
 
    # Check for not visited node and proceed with it.
    for x in adj[u]:
        # Call the DFs function if not visited
        if (not visited[x]):
            dfsUtil(x, node, visited, road_used, u, it + 1, adj, result)
    
 
    # Backtrack through the last visited nodes
    
    for y in road_used:
        if (y[1] == u):
            dfsUtil(y[0], node, visited, road_used, u, it + 1, adj, result)
    

    return result

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tmp = Ui_MainWindow()
    # app.exec_()
    tmp.show()
    sys.exit(app.exec())