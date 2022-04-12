import sys
import weakref
import math
import random

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import (QLineF, QPointF, QRandomGenerator, QRectF, QSizeF,
                            Qt, qAbs, pyqtSignal, QRect)
from PyQt5.QtGui import (QColor, QBrush, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient, QFont)
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                               QGraphicsView, QStyle, QWidget, QGridLayout, QDesktopWidget, QGraphicsLineItem, QMessageBox)

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

        pen_width = 3
        extra = (pen_width + self._arrow_size) / 2.0

        width = self._dest_point.x() - self._source_point.x()
        height = self._dest_point.y() - self._source_point.y()
        rect = QRectF(self._source_point, QSizeF(width, height))
        return rect.normalized().adjusted(-extra, -extra, extra, extra)


    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return

        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        dx = abs((self._dest_point.x() + self._source_point.x()) / 2)
        dy = abs((self._dest_point.y() + self._source_point.y()) / 2)

        # print(dx, dy)

        painter.setFont(QFont("Arial", 12))
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
        self._arrow_size = 5
        self._source_point = QPointF()
        self._dest_point = QPointF()
        self.height = 10
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

        pen_width = 3
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

        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        self.calculate()
        
        path = QPainterPath()
        path.moveTo(self._source_point)
        path.quadTo(self.controlPoint, self.ghostLine.p2())

        painter.drawPolygon(QPolygonF([self.ghostLine.p2(), self.arrowP1, self.arrowP2]))
        painter.strokePath(path, QPen(Qt.black))


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

        self.undirected_node_list = []
        self.directed_node_list = []
        self.graph_type = 'Undirected'
        self.adj_matrix = []
        self.edges = []
        self.undirected_current_number_nodes = 0
        self.directed_current_number_nodes = 0
        self.mode = None
        self.undirected_pairNode = []
        self.directed_pairNode = []
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

        self.btn_1.clicked.connect(lambda: self.addNode())
        self.btn_2.clicked.connect(lambda: self.addEdge())
        self.btn_3.clicked.connect(lambda: self.delNode())
        self.btn_4.clicked.connect(lambda: self.delEdge())
        self.btn_5.clicked.connect(lambda: self.setEdgeW())
        self.btn_6.clicked.connect(lambda: self.showMatrix())

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

                    self.undirected_current_number_nodes += 1

                    self.adj_matrix = []

                    for i in range(self.undirected_current_number_nodes):
                        self.adj_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                    # change adj_matrix after this based on self.edges
                    for x, y, w in self.edges:
                       self.adj_matrix[int(x)][int(y)] = w
                       self.adj_matrix[int(y)][int(x)] = w

                    self.mode = None
                else:
                    print("Out of view!")
            if self.mode == 'addEdge':
                # print(self.pairNode)
                if len(self.undirected_pairNode) == 2:
                    edge = UndirectedEdge(self.undirected_pairNode[0], self.undirected_pairNode[1])
                    self.scene_1.addItem(edge)
                    self.edges.append([self.undirected_pairNode[0].name, self.undirected_pairNode[1].name, edge.w])
                    
                    self.adj_matrix = []

                    for i in range(self.undirected_current_number_nodes):
                        self.adj_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                    # change adj_matrix after this based on self.edges
                    for x, y, w in self.edges:
                       self.adj_matrix[int(x)][int(y)] = w
                       self.adj_matrix[int(y)][int(x)] = w

                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)
                    self.undirected_pairNode = []
                    self.mode = None
            
        if self.graph_type == 'Directed':
            p = event.pos() # relative to widget
            # print(p)
            # gp = self.graphicsView.mapToGlobal(p) # relative to screen
            # print(gp)
            # rw = self.graphicsView.window().mapFromGlobal(gp) # relative to window
            # print(rw)
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
                    self.adj_matrix = []
                    self.mode = None
                else:
                    print("Out of view!")
            if self.mode == 'addEdge':
                # print(self.pairNode)
                if len(self.directed_pairNode) == 2:
                    self.scene_2.addItem(DirectedEdge(self.directed_pairNode[0], self.directed_pairNode[1]))
                    self.btn_1.setEnabled(1)
                    self.btn_2.setEnabled(1)
                    self.btn_3.setEnabled(1)
                    self.btn_4.setEnabled(1)
                    self.btn_5.setEnabled(1)
                    self.directed_pairNode = []
                    self.mode = None

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
            if self.mode == 'delNode' and item in self.undirected_node_list:

                # for edge in self.edges:
                #     print(type(edge))
                #     if item.name in edge:
                #         self.edges.remove(edge) 
                self.edges = [edge for edge in self.edges if item.name not in edge]


                self.scene_1.removeItem(item)
                self.undirected_node_list.remove(item)
                self.undirected_current_number_nodes -= 1

                self.scene_1.update()
                # print(item._edge_list)
                # self.mode = 'delEdge'

                self.adj_matrix = []
                for i in range(self.undirected_current_number_nodes):
                    self.adj_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                # change adj_matrix after this based on self.edges
                for x, y, w in self.edges:
                       self.adj_matrix[int(x)][int(y)] = w
                       self.adj_matrix[int(y)][int(x)] = w

                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.mode = None


            if self.mode == 'delEdge' and item  not in self.undirected_node_list:

                for edge in self.edges:
                        if item.name[0] == edge[0] and item.name[1] == edge[1]:
                            self.edges.remove(edge)

                if item.name in self.edges:
                     self.edges.remove(item.name)

                self.adj_matrix = []
                for i in range(self.undirected_current_number_nodes):
                    self.adj_matrix.append([0 for i in range(self.undirected_current_number_nodes)])
                # change adj_matrix after this based on self.edges
                for x, y, w in self.edges:
                       self.adj_matrix[int(x)][int(y)] = w
                       self.adj_matrix[int(y)][int(x)] = w

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
                    for edge in self.edges:
                        if item.name[0] == edge[0] and item.name[1] == edge[1]:
                            edge[2] = number
                        
                    self.adj_matrix[item.name[0]][item.name[1]] = number
                    self.adj_matrix[item.name[1]][item.name[0]] = number
                except Exception:
                    QMessageBox.about(self, 'Error','Input can only be a number')
                    pass
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.btn_5.setEnabled(1)
                self.mode = None

        if self.graph_type == 'Directed':
            if self.mode == 'delNode' and item in self.directed_node_list:
                self.scene_2.removeItem(item)
                self.directed_node_list.remove(item)
                self.scene_2.update()
                # print(item._edge_list)
                # self.mode = 'delEdge'
                self.btn_1.setEnabled(1)
                self.btn_2.setEnabled(1)
                self.btn_3.setEnabled(1)
                self.btn_4.setEnabled(1)
                self.mode = None

            if self.mode == 'delEdge' and item  not in self.directed_node_list:
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

    def showMatrix(self):
        print(self.edges)
        for m in self.adj_matrix: 
            print(m)


    def item_moved(self):
        if not self.graphicsView._timer_id:
            self.graphicsView._timer_id = self.startTimer(1000 / 25)

    def graphType(self):
        if self.rbtn_directed.isChecked():
            self.graph_type = 'Directed'
        else:
            self.graph_type = 'Undirected'

        # print(self.graph_type)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tmp = Ui_MainWindow()
    app.exec_()