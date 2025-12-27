import sys
from PySide6.QtWidgets import (QGraphicsView, QApplication, QMainWindow, 
QGraphicsItem, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, 
QGraphicsLineItem, QVBoxLayout, QSplitter, QLabel, QDialog, QTableWidget, 
QWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QAction, QPen, QColor
from node_item import NodeItem, NodeLabelItem
from edge_item import EdgeItem
from cost_item import CostItem
from graph import Graph

class GraphScene(QGraphicsScene):
    
    FORCE_MODE = 0
    DRAW_MODE = 1
    DELETE_MODE = 2
    EDIT_MODE = 3
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 800, 800)
        self.graph = Graph() 
        #self.graph.import_graph()
        self.current_mode = self.DRAW_MODE
        self.node_counter = 0
        self.nodeID = 0
        self.last_clicked_item = None
        self.deleted_nodes = []
        self.edge_preview = None

    def set_directed_graph(self):
        if self.graph.isDirected == True:
            return
        
        self.graph.isDirected = True
        for item in self.items():
            if isinstance(item, EdgeItem):
                item.update_path()
    
    def set_undirected_graph(self):
        if self.graph.isDirected == False:
            return
        
        self.graph.isDirected = False
        for item in self.items():
            if isinstance(item, EdgeItem):
                if item.curveSign == 1:
                    other_arc = item.source.has_other_arc(item.target)
                    other_arc.curveSign = 0
                    self.graph.remove_edge(item.source.node_id, item.target.node_id)
                    self.delete_edge(item)
                item.curveSign = 0
                item.update_path()
                
    def set_mode(self, mode):
        if self.edge_preview:
            self.stop_edge_preview()
        
        if self.current_mode == mode:
            return
        
        if self.current_mode != self.FORCE_MODE and mode != self.FORCE_MODE:
            self.current_mode = mode
            self.last_clicked_item = None
            return

        elif mode == self.FORCE_MODE:
            for node in self.graph.node_list:
                item = self.itemAt(self.graph.node_list[node][0], self.graph.node_list[node][1], self.views()[0].transform())
                item.parentItem().setFlag(QGraphicsEllipseItem.ItemIsMovable, True)

        else:
            for node in self.graph.node_list:
                item = self.itemAt(self.graph.node_list[node][0], self.graph.node_list[node][1], self.views()[0].transform())
                item.parentItem().setFlag(QGraphicsEllipseItem.ItemIsMovable, False)
        
        self.current_mode = mode
        self.last_clicked_item = None
            
    def min_node(self):
        min = self.deleted_nodes[0]
        for node in self.deleted_nodes:
            if node < min:
                min = node
        return min

    def delete_edge(self, edge):
        edge.source.edge_list.remove(edge)
        edge.target.edge_list.remove(edge)
        
        self.removeItem(edge)

    def start_edge_preview(self):
        self.edge_preview = QGraphicsLineItem()
        
        self.edge_preview.setPen(QPen(QColor("black"), 2))
        self.edge_preview.setZValue(-1)

        pos = self.last_clicked_item.scenePos()
        self.edge_preview.setLine(pos.x(), pos.y(), pos.x(), pos.y())
        
        self.addItem(self.edge_preview)
    
    def stop_edge_preview(self):
        self.removeItem(self.edge_preview)
        self.edge_preview = None
        self.last_clicked_item = None

    def mouseMoveEvent(self, event):
        x = event.scenePos().x()
        y = event.scenePos().y()
        
        if self.edge_preview is not None:
            self.edge_preview.setLine(self.last_clicked_item.scenePos().x(), self.last_clicked_item.scenePos().y(), x-3, y-3)

        super().mouseMoveEvent(event)

    def check_lists(self):
        print(self.graph.edge_list)
        print()
        print(self.graph.node_list)
        print()
        print(self.deleted_nodes)
        print()

    def mousePressEvent(self, event):
        x = event.scenePos().x()
        y = event.scenePos().y()

        print(x, y)

        clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        match self.current_mode:
            case self.FORCE_MODE:
                super().mousePressEvent(event)
                
            case self.DRAW_MODE:
                if isinstance(clicked_item, NodeLabelItem):
                    clicked_item = clicked_item.parentItem()

                if clicked_item is None:
                    if self.edge_preview is None:
                        if not self.deleted_nodes:
                            self.node_counter += 1
                            while self.node_counter in self.graph.node_list:
                                self.node_counter += 1
                            
                            self.nodeID = self.node_counter
                        else:
                            self.nodeID = self.min_node()
                            self.deleted_nodes.remove(self.nodeID)

                        node = NodeItem(x, y, self.nodeID)
                        self.addItem(node)
                        self.graph.add_node(self.nodeID, x, y)
                        self.last_clicked_item = None

                    else:
                        self.stop_edge_preview()

                elif isinstance(clicked_item, NodeItem):
                    if self.last_clicked_item is None:
                        self.last_clicked_item = clicked_item
                        self.start_edge_preview()
        
                    elif not clicked_item is self.last_clicked_item and not self.last_clicked_item.has_edge_to(clicked_item):
                        curve_sign = 0
                        if self.graph.isDirected == True:
                            item = self.last_clicked_item.has_other_arc(clicked_item)
                            if item is not None:
                                item.curveSign = 1
                                item.update_path()
                                item.cost.update_cost_position()
                                curve_sign = 1
                            else:
                                curve_sign = 0
                        
                        edge = EdgeItem(self.last_clicked_item, clicked_item, None, curve_sign)
                        self.addItem(edge)
                        self.graph.add_edge(self.last_clicked_item.node_id, clicked_item.node_id, None)

                        self.stop_edge_preview()
                        self.last_clicked_item = clicked_item
                        self.start_edge_preview()

                    else:
                        self.stop_edge_preview()

                super().mousePressEvent(event)
                
            case self.DELETE_MODE:
                if isinstance(clicked_item, QGraphicsTextItem):
                    clicked_item = clicked_item.parentItem()
                if isinstance(clicked_item, CostItem):
                    clicked_item = clicked_item.parentItem()

                if isinstance(clicked_item, NodeItem):
                    for edge in list(clicked_item.edge_list):
                        self.graph.remove_edge(edge.source.node_id, edge.target.node_id)
                        self.delete_edge(edge)        

                    self.deleted_nodes.append(clicked_item.node_id)
                    self.graph.remove_node(clicked_item.node_id)
                    self.removeItem(clicked_item)

                if isinstance(clicked_item, EdgeItem):
                    if self.graph.isDirected == True:
                        arc = clicked_item.source.has_other_arc(clicked_item.target)
                        if arc is not None:
                            arc.curveSign = 0
                            arc.update_path()
                            arc.cost.update_cost_position()
                    
                    self.graph.remove_edge(clicked_item.source.node_id, clicked_item.target.node_id)
                    self.delete_edge(clicked_item)
                

                super().mousePressEvent(event) 

            case self.EDIT_MODE:

                if clicked_item is None and self.last_clicked_item:
                    self.last_clicked_item.clearFocus()
                    self.last_clicked_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)

                else:
                    if isinstance(clicked_item, NodeItem):
                        clicked_item = clicked_item.label
                    elif isinstance(clicked_item, CostItem):
                        clicked_item = clicked_item.label
                    elif isinstance(clicked_item, EdgeItem):
                        clicked_item = clicked_item.cost.label

                    clicked_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                    clicked_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
                    
                    self.last_clicked_item = clicked_item
                super().mousePressEvent(event)
        self.check_lists()
    
class GraphView(QGraphicsView):
    def __init__(self, scene):
        super().__init__()

        self.scene = scene
        self.setScene(self.scene)

        self.setBackgroundBrush(Qt.white)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VizGraf")

        self.scene = GraphScene()
        self.view = GraphView(self.scene)

        self.node_table = QTableWidget()
        self.edge_table = QTableWidget()

        self.setup_node_table()
        self.setup_edge_table()

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(self.node_table)
        right_layout.addWidget(self.edge_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.view)
        splitter.addWidget(right_panel)

        self.setCentralWidget(splitter)

        self.toolbar = self.addToolBar("Tools")

        self.force_action = QAction("Force", self)
        self.draw_action = QAction("Draw", self)
        self.delete_action = QAction("Delete", self)
        self.edit_action = QAction("Edit", self)
        self.directed_graph = QAction("Directed", self)
        self.undirected_graph = QAction("Undirected", self)

        self.toolbar.addAction(self.force_action)
        self.toolbar.addAction(self.draw_action)
        self.toolbar.addAction(self.delete_action)
        self.toolbar.addAction(self.edit_action)
        self.toolbar.addAction(self.directed_graph)
        self.toolbar.addAction(self.undirected_graph)

        self.force_action.triggered.connect(lambda: self.scene.set_mode(0))
        self.draw_action.triggered.connect(lambda: self.scene.set_mode(1))
        self.delete_action.triggered.connect(lambda: self.scene.set_mode(2))
        self.edit_action.triggered.connect(lambda: self.scene.set_mode(3))
        self.directed_graph.triggered.connect(lambda: self.scene.set_directed_graph())
        self.undirected_graph.triggered.connect(lambda: self.scene.set_undirected_graph())

        self.update_node_table()

    def setup_node_table(self):
        self.node_table.setColumnCount(3)
        header = self.node_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.node_table.setHorizontalHeaderLabels(["Node ID", "X", "Y"])
    
    def setup_edge_table(self):
        self.edge_table.setColumnCount(3)
        
        header = self.edge_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.edge_table.setHorizontalHeaderLabels(["Source", "Target", "Cost"])

    def update_node_table(self):
        node_list = self.scene.graph.node_list

        self.node_table.blockSignals(True)
        self.node_table.setRowCount(len(node_list))

        for row in range(len(node_list)):
            node, position = list(node_list.items())[row]

            id = QTableWidgetItem(str(node))
            x = QTableWidgetItem(str(position[0]))
            y = QTableWidgetItem(str(position[1]))
            
            self.node_table.setItem(row, 0, id)
            self.node_table.setItem(row, 1, x)
            self.node_table.setItem(row, 2, y)
        
        self.node_table.blockSignals(False)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())