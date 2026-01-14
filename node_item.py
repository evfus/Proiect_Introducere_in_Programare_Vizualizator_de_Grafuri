from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

class NodeLabelItem(QGraphicsTextItem):
    def __init__(self, node_id):
        super().__init__(str(node_id))

        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.setFont(font)

        self.setDefaultTextColor(Qt.black)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
    def isValid(self):
        current_id = self.parentItem().node_id
        new_id = self.toPlainText()

        if not new_id.isdigit():
            self.setPlainText(str(current_id))
            return
        
        new_id = int(new_id)
        scene = self.scene()
        
        if new_id in scene.graph.node_list:
            self.setPlainText(str(current_id))
            return
        
        else:
            self.parentItem().node_id = new_id
            scene.deleted_nodes.append(current_id)
            scene.graph.change_node(current_id, new_id)

            if new_id in scene.deleted_nodes:
                scene.deleted_nodes.remove(new_id)
            
            scene.update_nodes.emit()
            scene.update_edges.emit()
        
    def focusOutEvent(self, event):
        self.isValid()
        super().focusOutEvent(event)
    

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, x, y, nodeID, radius=50):
        super().__init__(-radius/2, -radius/2, radius, radius)
        
        self.edge_list = []
        
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("black"), 3))

        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges, True)
        
        self.node_id = nodeID 
        self.hasMoved = False

        self.label = NodeLabelItem(self.node_id)
        self.label.setParentItem(self)
        
        self.label.setPos(-radius/4 + 2, -radius/4 - 7)

        self.setPos(x,y)
    
    def itemChange(self, change, value):
        scene = self.scene()
        if scene is not None:
            if change == QGraphicsItem.ItemPositionChange:
                for edge in self.edge_list:
                    edge.update_path()
                    edge.cost.update_cost_position()

                self.hasMoved = True
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        if self.scene().current_mode == 3:
            self.label.setFocus()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        scene = self.scene()
        if scene.current_mode == 0 and self.hasMoved is True:
                scene.graph.update_node_position(self.node_id, self.scenePos().x(), self.scenePos().y())
                scene.update_nodes.emit()
                self.hasMoved = False

        super().mouseReleaseEvent(event)

    def has_edge_to(self, target):
        if self.scene().graph.isDirected == True:
            for edge in self.edge_list:
                if edge.source is self and edge.target is target:
                    return True
        else:
            for edge in self.edge_list:
                if (edge.source is self and edge.target is target) or (edge.source is target and edge.target is self):
                    return True
        return False
    
    def has_other_arc(self, target):
        for edge in self.edge_list:
                if edge.source is target and edge.target is self:
                    return edge
        return None
    
    def focused_color(self):
        self.setPen(QPen(QColor("green"), 4))
        self.setBrush(QBrush(QColor(144, 238, 144, 255))) 

    def visited_color(self):
        self.setPen(QPen(QColor("gray"), 3))
        self.setBrush(QBrush(QColor(211, 211, 211, 255)))

    def unfocused_color(self):
        self.setPen(QPen(QColor("black"), 3))
        self.setBrush(QBrush(Qt.transparent))
