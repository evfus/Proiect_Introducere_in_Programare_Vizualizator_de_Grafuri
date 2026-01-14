import sys
from PySide6.QtWidgets import (QGraphicsView, QApplication, QMainWindow, 
QGraphicsItem, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, 
QGraphicsLineItem, QVBoxLayout, QSplitter, QDialog, QTableWidget, 
QWidget, QTableWidgetItem, QHeaderView, QMenu, QTextEdit, QPushButton, 
QMessageBox, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox, QLabel)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QAction, QPen, QColor, QImage
import math
from node_item import NodeItem, NodeLabelItem
from edge_item import EdgeItem
from cost_item import CostItem
from graph import Graph
from funct import dfs,bfs,dijkstra

class GraphScene(QGraphicsScene):
    
    FORCE_MODE = 0
    DRAW_MODE = 1
    DELETE_MODE = 2
    EDIT_MODE = 3
    update_nodes = Signal()
    update_edges = Signal()
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 800, 800)
        self.graph = Graph() 
        self.current_mode = self.DRAW_MODE
        self.node_counter = 0
        self.nodeID = 0
        self.clicked_item = None
        self.last_clicked_item = None
        self.deleted_nodes = []
        self.edge_preview = None

    def clear_scene(self):
        self.clear()
        self.graph.node_list.clear()
        self.graph.edge_list.clear()
        self.update_nodes.emit()
        self.update_edges.emit()
        self.node_counter = 0
        self.nodeID = 0
        self.clicked_item = None
        self.last_clicked_item = None
        self.deleted_nodes.clear()
        self.edge_preview = None

    def import_graph_with_pos(self):
        self.clear()
        
        file_path, _ = QFileDialog.getOpenFileName(caption = "Open Graph Source File", dir = "~/proiectIP/VizGraf_2.0")
        if not file_path:
            return
        
        self.graph.import_graph(file_path)

        node_list = self.graph.node_list
        edge_list = self.graph.edge_list

        for node in node_list.items():
            item = NodeItem(node[1][0], node[1][1], node[0])
            self.addItem(item)

        for i in range(0, len(edge_list), 3):
            curve_sign = 0
            source = self.itemAt(node_list[edge_list[i]][0], node_list[edge_list[i]][1], self.views()[0].transform())
            target = self.itemAt(node_list[edge_list[i + 1]][0], node_list[edge_list[i + 1]][1], self.views()[0].transform())
            
            source = source.parentItem()
            target = target.parentItem()
            
            if self.graph.isDirected is True:
                if source.has_other_arc(target):
                    curve_sign = 1
                    
            edge = EdgeItem(source, target, edge_list[i + 2], curve_sign)
            self.addItem(edge)
        self.update_nodes.emit()
        self.update_edges.emit()

    def import_graph_without_pos(self):
        self.clear()

        file_path, _ = QFileDialog.getOpenFileName(caption = "Open Graph Source File", dir = "~/proiectIP/VizGraf_2.0")
        if not file_path:
            return
        
        self.graph.import_graph(file_path)

        node_list = self.graph.node_list
        edge_list = self.graph.edge_list
        node_count = len(node_list)

        cx = 400
        cy = 400
        radius = 300
        
        for i, node in enumerate(node_list.items()):
            angle = math.pi * 2 * i / node_count
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))

            node[1][0] = x
            node[1][1] = y

            item = NodeItem(x, y, node[0])
            self.addItem(item)

        for i in range(0, len(edge_list), 3):
            curve_sign = 0
            source = self.itemAt(node_list[edge_list[i]][0], node_list[edge_list[i]][1], self.views()[0].transform())
            target = self.itemAt(node_list[edge_list[i + 1]][0], node_list[edge_list[i + 1]][1], self.views()[0].transform())
            
            source = source.parentItem()
            target = target.parentItem()
            
            if self.graph.isDirected is True:
                if source.has_other_arc(target):
                    curve_sign = 1
                    
            edge = EdgeItem(source, target, edge_list[i + 2], curve_sign)
            self.addItem(edge)

        self.update_nodes.emit()
        self.update_edges.emit()

    def export(self):
        file_path, _ = QFileDialog.getSaveFileName(caption = "Export Graph", dir = "~/proiectIP/VizGraf_2.0")
        if not file_path:
            return

        self.graph.export_graph(file_path)

    def export_scene_png(self):
        if self.edge_preview:
            self.stop_edge_preview()
        
        if self.clicked_item is not None:
            if isinstance(self.clicked_item, NodeItem):
                self.clicked_item.unfocused_color()
            elif isinstance(self.clicked_item, NodeLabelItem):
                self.clicked_item.parentItem().unfocused_color()
        
        area = self.sceneRect()
        
        image = QImage(area.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        file_path, _ = QFileDialog.getSaveFileName(caption = "Export Graph as PNG", dir = "~/proiectIP/VizGraf_2.0")
    
        if not file_path:
            painter.end()
            return
        
        if not file_path.lower().endswith('.png'):
            file_path += '.png'

        self.render(painter, image.rect(), area)
        painter.end()
        
        image.save(file_path, "PNG")

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
                    self.update_edges.emit()
                    self.delete_edge(item)
                item.curveSign = 0
                item.update_path()
                item.cost.update_cost_position()
                
    def set_mode(self, mode):
        if self.edge_preview:
            self.stop_edge_preview()
        
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
        self.edge_preview.setZValue(-2)

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
        
        if isinstance(self.clicked_item, QGraphicsLineItem):
            self.stop_edge_preview()

        if self.clicked_item is not None:
            if isinstance(self.clicked_item, NodeItem):
                self.clicked_item.unfocused_color()
            elif isinstance(self.clicked_item, NodeLabelItem):
                self.clicked_item.parentItem().unfocused_color()

        self.clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        if isinstance(self.clicked_item, NodeItem):
            self.last_clicked_node = self.clicked_item
        elif isinstance(self.clicked_item, NodeLabelItem):
            self.last_clicked_node = self.clicked_item.parentItem()

        if isinstance(self.clicked_item, NodeItem):
            self.clicked_item.focused_color()
        elif isinstance(self.clicked_item, NodeLabelItem):
            self.clicked_item.parentItem().focused_color()
        
        match self.current_mode:
            case self.FORCE_MODE:
                super().mousePressEvent(event)
                
            case self.DRAW_MODE:
                if isinstance(self.clicked_item, NodeLabelItem):
                    self.clicked_item = self.clicked_item.parentItem()

                if self.clicked_item is None:
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
                        self.update_nodes.emit()
                        self.last_clicked_item = None

                    else:
                        self.stop_edge_preview()

                elif isinstance(self.clicked_item, NodeItem):
                    if self.last_clicked_item is None:
                        self.last_clicked_item = self.clicked_item
                        self.start_edge_preview()
        
                    elif not self.clicked_item is self.last_clicked_item and not self.last_clicked_item.has_edge_to(self.clicked_item):
                        curve_sign = 0
                        if self.graph.isDirected == True:
                            item = self.last_clicked_item.has_other_arc(self.clicked_item)
                            if item is not None:
                                item.curveSign = 1
                                item.update_path()
                                item.cost.update_cost_position()
                                curve_sign = 1
                            else:
                                curve_sign = 0
                        
                        edge = EdgeItem(self.last_clicked_item, self.clicked_item, None, curve_sign)
                        self.addItem(edge)
                        self.graph.add_edge(self.last_clicked_item.node_id, self.clicked_item.node_id, None)
                        self.update_edges.emit()

                        self.stop_edge_preview()
                        self.last_clicked_item = self.clicked_item
                        self.start_edge_preview()

                    else:
                        self.stop_edge_preview()

                super().mousePressEvent(event)
                
            case self.DELETE_MODE:
                if isinstance(self.clicked_item, QGraphicsTextItem):
                    self.clicked_item = self.clicked_item.parentItem()
                if isinstance(self.clicked_item, CostItem):
                    self.clicked_item = self.clicked_item.parentItem()

                if isinstance(self.clicked_item, NodeItem):
                    for edge in list(self.clicked_item.edge_list):
                        self.graph.remove_edge(edge.source.node_id, edge.target.node_id)
                        self.delete_edge(edge)        

                    self.deleted_nodes.append(self.clicked_item.node_id)
                    self.graph.remove_node(self.clicked_item.node_id)
                    self.update_edges.emit()
                    self.update_nodes.emit()
                    self.removeItem(self.clicked_item)

                if isinstance(self.clicked_item, EdgeItem):
                    if self.graph.isDirected == True:
                        arc = self.clicked_item.source.has_other_arc(self.clicked_item.target)
                        if arc is not None:
                            arc.curveSign = 0
                            arc.update_path()
                            arc.cost.update_cost_position()
                    
                    self.graph.remove_edge(self.clicked_item.source.node_id, self.clicked_item.target.node_id)
                    self.update_edges.emit()
                    self.delete_edge(self.clicked_item)

                super().mousePressEvent(event) 

            case self.EDIT_MODE:
                if self.clicked_item is None and self.last_clicked_item:
                    self.last_clicked_item.clearFocus()
                    self.last_clicked_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)

                else:
                    if isinstance(self.clicked_item, NodeItem):
                        self.clicked_item = self.clicked_item.label
                    elif isinstance(self.clicked_item, CostItem):
                        self.clicked_item = self.clicked_item.label
                    elif isinstance(self.clicked_item, EdgeItem):
                        self.clicked_item = self.clicked_item.cost.label

                    self.clicked_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
                    self.clicked_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
                    
                    self.last_clicked_item = self.clicked_item
            
                super().mousePressEvent(event)
        self.check_lists()
    
class GraphView(QGraphicsView):
    def __init__(self, scene):
        super().__init__()

        self.scene = scene
        self.setScene(self.scene)

        self.setBackgroundBrush(Qt.white)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

class CodeEditWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Code Editor")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        file_path, _ = QFileDialog.getOpenFileName(caption = "Open Algorithm Source File", dir = "~/proiectIP/VizGraf_2.0")

        self.code_editor = QTextEdit()
        layout.addWidget(self.code_editor)
        
        if not file_path:
            self.code_editor.setPlaceholderText("Write your python code here:")
        else:
            file = open(file_path, 'r')
            algorithm = file.read()
            self.code_editor.setPlainText(algorithm)
        
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_code)
        buttons_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.code_editor.clear)
        buttons_layout.addWidget(self.clear_button)

        self.import_algo_button = QPushButton("Import Algorithm")
        self.import_algo_button.clicked.connect(self.update_code_window)
        buttons_layout.addWidget(self.import_algo_button)


        buttons_layout.addStretch()

    def update_code_window(self):
        file_path, _ = QFileDialog.getOpenFileName(caption = "Open Algorithm Source File")

        if file_path:
            file = open(file_path, 'r')
            algorithm = file.read()
            self.code_editor.setPlainText(algorithm)

    def run_code(self):
        code = self.code_editor.toPlainText()
        print("")
        try:
            exec(code)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

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

        right_layout.addWidget(QLabel("Node List"))
        right_layout.addWidget(self.node_table)
        right_layout.addWidget(QLabel("Edge List"))
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
        self.clear_scene = QAction("Clear Graph", self)
        self.directed_graph = QAction("Directed", self)
        self.undirected_graph = QAction("Undirected", self)
        self.import_graph = QAction("Import Graph", self)
        self.export_graph = QAction("Export Graph", self)
        self.algo_action = QAction("Algoritmi", self)
        self.custom_code = QAction("Functions", self)

        import_menu = QMenu(self)
        import_with_pos = QAction("With Positioning", self)
        import_without_pos = QAction("Without Positioning", self)
        
        import_menu.addAction(import_with_pos)
        import_menu.addAction(import_without_pos)
        self.import_graph.setMenu(import_menu)

        export_menu = QMenu(self)
        export_as_png = QAction("As PNG", self)

        export_menu.addAction(export_as_png)
        self.export_graph.setMenu(export_menu)

        algo_menu = QMenu(self)
        self.dfs_action = QAction("Run DFS", self)
        self.bfs_action = QAction("Run BFS", self)
        self.dijkstra_action = QAction("Run Dijkstra", self)

        algo_menu.addAction(self.dfs_action)
        algo_menu.addAction(self.bfs_action)
        algo_menu.addAction(self.dijkstra_action)
        self.algo_action.setMenu(algo_menu)
        
        self.toolbar.addAction(self.force_action)
        self.toolbar.addAction(self.draw_action)
        self.toolbar.addAction(self.delete_action)
        self.toolbar.addAction(self.edit_action)
        self.toolbar.addAction(self.clear_scene)
        self.toolbar.addAction(self.directed_graph)
        self.toolbar.addAction(self.undirected_graph)
        self.toolbar.addAction(self.import_graph)
        self.toolbar.addAction(self.export_graph)
        self.toolbar.addAction(self.algo_action)
        self.toolbar.addAction(self.custom_code)

        self.force_action.triggered.connect(lambda: self.scene.set_mode(0))
        self.draw_action.triggered.connect(lambda: self.scene.set_mode(1))
        self.delete_action.triggered.connect(lambda: self.scene.set_mode(2))
        self.edit_action.triggered.connect(lambda: self.scene.set_mode(3))

        self.clear_scene.triggered.connect(self.scene.clear_scene)

        self.directed_graph.triggered.connect(self.scene.set_directed_graph)
        self.undirected_graph.triggered.connect(self.scene.set_undirected_graph)
        
        self.import_graph.triggered.connect(self.scene.import_graph_with_pos)
        import_with_pos.triggered.connect(self.scene.import_graph_with_pos)        
        import_without_pos.triggered.connect(self.scene.import_graph_without_pos)
        
        self.export_graph.triggered.connect(self.scene.export)
        export_as_png.triggered.connect(self.scene.export_scene_png)

        self.dfs_action.triggered.connect(self.run_dfs)
        self.bfs_action.triggered.connect(self.run_bfs)
        self.dijkstra_action.triggered.connect(self.run_dijkstra)

        self.custom_code.triggered.connect(self.create_code_window)

        self.scene.update_edges.connect(self.update_edge_table)
        self.scene.update_nodes.connect(self.update_node_table)

        self.node_table.itemChanged.connect(self.node_table_change)
        self.edge_table.itemChanged.connect(self.edge_table_change)

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
        self.node_table.setRowCount(len(node_list) + 1)

        for row in range(len(node_list)):
            node, position = list(node_list.items())[row]

            id = QTableWidgetItem(str(node))
            x = QTableWidgetItem(str(position[0]))
            y = QTableWidgetItem(str(position[1]))

            item = self.scene.itemAt(position[0], position[1], self.scene.views()[0].transform())
            item = item.parentItem()

            id.setData(Qt.UserRole, item)
            x.setData(Qt.UserRole, item)
            y.setData(Qt.UserRole, item)

            self.node_table.setItem(row, 0, id)
            self.node_table.setItem(row, 1, x)
            self.node_table.setItem(row, 2, y)
        
        self.node_table.setItem(len(node_list), 0, QTableWidgetItem(""))
        self.node_table.setItem(len(node_list), 1, QTableWidgetItem(""))
        self.node_table.setItem(len(node_list), 2, QTableWidgetItem(""))
        
        self.node_table.blockSignals(False)
        
    def update_edge_table(self):
        edge_list = self.scene.graph.edge_list

        self.edge_table.blockSignals(True)
        self.edge_table.setRowCount(len(edge_list)/3)

        for row in range(0, len(edge_list), 3):
            source = QTableWidgetItem(str(edge_list[row]))
            target = QTableWidgetItem(str(edge_list[row + 1]))
            if edge_list[row + 2] == None or edge_list == "" or edge_list[row + 2] == "None":
                cost_value = ""
            else:
                cost_value = edge_list[row + 2]
            cost = QTableWidgetItem(str(cost_value))

            source_x, source_y = list(self.scene.graph.node_list[edge_list[row]])
            source_node = self.scene.itemAt(source_x, source_y, self.scene.views()[0].transform())
            source_node = source_node.parentItem()
            
            for edge in source_node.edge_list:
                if edge.source is source_node and edge.target.node_id == edge_list[row + 1]:
                    item = edge
                    break

            source.setData(Qt.UserRole, item)
            target.setData(Qt.UserRole, item)
            cost.setData(Qt.UserRole, item)

            self.edge_table.setItem(row/3, 0, source)
            self.edge_table.setItem(row/3, 1, target)
            self.edge_table.setItem(row/3, 2, cost)
        
        self.edge_table.blockSignals(False)

    def node_table_change(self, item: QTableWidgetItem):
        node = item.data(Qt.UserRole)
        node_list = self.scene.graph.node_list
        if node is not None:
            match item.column():
                case 0:
                    new_id = item.text()
                    if new_id.isdigit():
                        node.label.setPlainText(str(new_id))
                        node.label.isValid()
                        self.update_edge_table()

                        if node.node_id != int(new_id):
                            self.node_table.blockSignals(True)
                            item.setText(str(node.node_id))
                            self.node_table.blockSignals(False)
                    else:
                        self.node_table.blockSignals(True)
                        item.setText(str(node.node_id))
                        self.node_table.blockSignals(False)

                case 1:
                    new_x = item.text()
                    try:
                        float(new_x)
                    except ValueError:
                        return
                    node.setPos(float(new_x), node.scenePos().y())
                    for edge in node.edge_list:
                        edge.update_path()
                        edge.cost.update_cost_position()
                    self.scene.graph.update_node_position(node.node_id, new_x, int(node.scenePos().y()))

                case 2:
                    new_y = item.text()
                    try:
                        float(new_y)
                    except ValueError:
                        return
                    node.setPos(node.scenePos().x(), float(new_y))
                    for edge in node.edge_list:
                        edge.update_path()
                        edge.cost.update_cost_position()
                    self.scene.graph.update_node_position(node.node_id, int(node.scenePos().x()), new_y)
        else:
            match item.column():
                case 0:
                    nodeID = item.text()

                    if nodeID.isdigit():
                        nodeID = int(nodeID)

                        if nodeID not in node_list.keys():
                            if nodeID in self.scene.deleted_nodes:
                                self.scene.deleted_nodes.remove(nodeID)

                            node_list[nodeID] = [400, 400]

                            node = NodeItem(400, 400, nodeID)
                            self.scene.addItem(node)
                            
                            window.update_node_table()
                    else:
                        self.node_table.blockSignals(True)
                        item.setText("")
                        self.node_table.blockSignals(False)
                
                case 1:
                    nodeX = item.text()
                    if nodeX.isdigit():
                        nodeX = int(nodeX)
                        if not self.scene.deleted_nodes:
                                self.scene.node_counter += 1
                                while self.scene.node_counter in node_list:
                                    self.scene.node_counter += 1

                                nodeID = self.scene.node_counter
                        else:
                            nodeID = self.scene.min_node()
                            self.scene.deleted_nodes.remove(nodeID)

                        node_list[nodeID] = [nodeX, 400]
                        node = NodeItem(nodeX, 400, nodeID)
                        self.scene.addItem(node)

                        window.update_node_table()
                    else:
                        self.node_table.blockSignals(True)
                        item.setText("")
                        self.node_table.blockSignals(False)

                case 2:
                    nodeY = item.text()
                    if nodeY.isdigit():
                        nodeY = int(nodeY)
                        if not self.scene.deleted_nodes:
                                self.scene.node_counter += 1
                                while self.scene.node_counter in node_list:
                                    self.scene.node_counter += 1

                                nodeID = self.scene.node_counter
                        else:
                            nodeID = self.scene.min_node()
                            self.scene.deleted_nodes.remove(nodeID)

                        node_list[nodeID] = [400, nodeY]
                        node = NodeItem(400, nodeY, nodeID)
                        self.scene.addItem(node)

                        window.update_node_table()
                    else:
                        self.node_table.blockSignals(True)
                        item.setText("")
                        self.node_table.blockSignals(False)

    def edge_table_change(self, item: QTableWidgetItem):
        edge = item.data(Qt.UserRole)
        match item.column():
            case 0:
                if item.text().isdigit():
                    if int(item.text()) not in list(self.scene.graph.node_list.keys()):
                        nodeID = int(item.text())
                        if nodeID in self.scene.deleted_nodes:
                            self.scene.deleted_nodes.remove(nodeID)

                        node = NodeItem(400, 400, nodeID)
                        self.scene.addItem(node)
                        self.scene.graph.add_node(nodeID, 400, 400)
                        self.scene.graph.edge_list[item.row() * 3] = nodeID
                        self.update_node_table()
                        node.edge_list.append(edge)
                        edge.source.edge_list.remove(edge)
                        edge.source = node
                        edge.cost.start = node
                        edge.update_path()
                        edge.cost.update_cost_position()
                    
                    else:
                        x = self.scene.graph.node_list[int(item.text())][0]
                        y = self.scene.graph.node_list[int(item.text())][1]
                        new_source = self.scene.itemAt(x, y, self.scene.views()[0].transform())
                        new_source = new_source.parentItem()    
                        
                        if edge.target != new_source and edge.source != new_source and not new_source.has_edge_to(edge.target):
                            self.scene.graph.edge_list[item.row() * 3] = new_source.node_id
                            
                            if edge.curveSign == 1:
                                second_arc = edge.source.has_other_arc(edge.target)
                                edge.curveSign = 0
                                second_arc.curveSign = 0
                                second_arc.update_path()
                                second_arc.cost.update_cost_position()

                            edge.source.edge_list.remove(edge)
                            edge.source = new_source
                            edge.cost.start = new_source
                            new_source.edge_list.append(edge)

                            if self.scene.graph.isDirected:
                                second_arc = edge.source.has_other_arc(edge.target)
                                if second_arc is not None:
                                    edge.curveSign = 1
                                    second_arc.curveSign = 1
                                    second_arc.update_path()
                                    second_arc.cost.update_cost_position()

                            edge.update_path()
                            edge.cost.update_cost_position()

                        else:
                            self.edge_table.blockSignals(True)
                            item.setText(str(edge.source.node_id))
                            self.edge_table.blockSignals(False)

                else: 
                    self.edge_table.blockSignals(True)
                    item.setText(str(edge.source.node_id))
                    self.edge_table.blockSignals(False)

            case 1:
                if item.text().isdigit():
                    if int(item.text()) not in list(self.scene.graph.node_list.keys()):
                        nodeID = int(item.text())
                        if nodeID in self.scene.deleted_nodes:
                            self.scene.deleted_nodes.remove(nodeID)
                        node = NodeItem(400, 400, nodeID)
                        self.scene.addItem(node)
                        self.scene.graph.add_node(nodeID, 400, 400)
                        self.scene.graph.edge_list[item.row() * 3 + 1] = nodeID
                        self.update_node_table()
                        node.edge_list.append(edge)
                        edge.target.edge_list.remove(edge)
                        edge.target = node
                        edge.cost.end = node
                        edge.update_path()
                        edge.cost.update_cost_position()
                    
                    else:
                        x = self.scene.graph.node_list[int(item.text())][0]
                        y = self.scene.graph.node_list[int(item.text())][1]
                        new_target = self.scene.itemAt(x, y, self.scene.views()[0].transform())
                        new_target = new_target.parentItem()    
                        
                        if edge.source != new_target and edge.target != new_target:
                            self.scene.graph.edge_list[item.row() * 3 + 1] = new_target.node_id

                            if edge.curveSign == 1:
                                second_arc = edge.source.has_other_arc(edge.target)
                                edge.curveSign = 0
                                second_arc.curveSign = 0
                                second_arc.update_path()
                                second_arc.cost.update_cost_position()

                            edge.target.edge_list.remove(edge)
                            edge.target = new_target
                            edge.cost.end = new_target
                            new_target.edge_list.append(edge)

                            if self.scene.graph.isDirected:
                                second_arc = edge.source.has_other_arc(edge.target)
                                if second_arc is not None:
                                    edge.curveSign = 1
                                    second_arc.curveSign = 1
                                    second_arc.update_path()
                                    second_arc.cost.update_cost_position()

                            edge.update_path()
                            edge.cost.update_cost_position()

                        else:
                            self.edge_table.blockSignals(True)
                            item.setText(str(edge.target.node_id))
                            self.edge_table.blockSignals(False)

                else: 
                    self.edge_table.blockSignals(True)
                    item.setText(str(edge.target.node_id))
                    self.edge_table.blockSignals(False)
            case 2:
                if item.text().isdigit() or item.text() == "" or item.text() == "None":
                    edge.cost.label.setPlainText(item.text())
                    edge.cost.setVisible(True)
                    self.edge_table.blockSignals(True)
                    edge.cost.label.isValid()
                    self.edge_table.blockSignals(False)
            
                else:
                    self.edge_table.blockSignals(True)
                    item.setText(str(edge.costValue))
                    self.edge_table.blockSignals(False)
            
    def create_code_window(self):
        self.code_window = CodeEditWindow()
        self.code_window.show()
    
    def start_animation(self, node_ids_list):
        if not node_ids_list:
            return
        
        for item in self.scene.items():
            if hasattr(item, 'unfocused_color'):
                item.unfocused_color()

        self.animation_step = 0
        self.traversal_order = node_ids_list
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_next_node)
        self.timer.start(1000)

    def animate_next_node(self):
        if self.animation_step < len(self.traversal_order):
            if self.animation_step > 0:
                previous_node_id = self.traversal_order[self.animation_step - 1]
                for item in self.scene.items():
                    if hasattr(item, 'node_id') and item.node_id == previous_node_id:
                        item.visited_color()
                        break
                    
            node_id = self.traversal_order[self.animation_step]
            for item in self.scene.items():
                if hasattr(item, 'node_id') and item.node_id == node_id:
                    item.focused_color()
                    break
            self.animation_step += 1
        else:
            self.timer.stop()

    def run_dfs(self):
        if not self.scene.graph.node_list:
            return
        
        available_nodes = [str(node_id) for node_id in self.scene.graph.node_list.keys()]
        node_id_str, ok = QInputDialog.getItem(self, "Start DFS", "Alege nodul de start:", available_nodes, 0, False)

        if ok and node_id_str:
            start_node = int(node_id_str)
            order_list = dfs(self.scene.graph, start_node)
            self.start_animation(order_list)
    
    def run_bfs(self):
        if not self.scene.graph.node_list:
            return
            
        available_nodes = [str(node_id) for node_id in self.scene.graph.node_list.keys()]
        node_id_str, ok = QInputDialog.getItem(self, "Start BFS", "Alege nodul de start:", available_nodes, 0, False)

        if ok and node_id_str:
            start_node = int(node_id_str)      
            order_list = bfs(self.scene.graph, start_node)
            self.start_animation(order_list)
    
    def run_dijkstra(self):
        if not self.scene.graph.node_list:
            return
            
        available_nodes = [str(node_id) for node_id in self.scene.graph.node_list.keys()]
        
        start_id, ok1 = QInputDialog.getItem(self, "Dijkstra", "Selectează Sursa:", available_nodes, 0, False)
        if not ok1: return      #sursa
        
        target_id, ok2 = QInputDialog.getItem(self, "Dijkstra", "Selectează Destinația:", available_nodes, 0, False)
        if not ok2: return      #destinatie

        result = dijkstra(self.scene.graph, int(start_id), int(target_id))

        if result == "ERROR_COST":
            QMessageBox.critical(self, "Eroare Costuri", "Toate muchiile trebuie să aibă un cost valid pentru Dijkstra!")
            return
            
        if not result:
            QMessageBox.information(self, "Info", "Nu există drum între aceste noduri.")
            return

        for item in self.scene.items():
            if hasattr(item, 'unfocused_color'):
                item.unfocused_color()
        
        self.start_animation(result)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    window.update_node_table()
    sys.exit(app.exec())
