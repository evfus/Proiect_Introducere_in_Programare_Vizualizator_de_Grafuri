from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtCore import Qt

class CostLabelItem(QGraphicsTextItem):
    def __init__(self, cost):
        if cost == "None":
            super().__init__("")
        else:
            super().__init__(str(cost))

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)

        self.setDefaultTextColor(Qt.black)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    
    def isValid(self):
        new_cost = self.toPlainText()
        scene = self.scene()
        source_node = self.parentItem().start.node_id
        target_node = self.parentItem().end.node_id

        if new_cost == "" or new_cost == "None":
            self.parentItem().setVisible(False)
            scene.graph.update_cost(source_node, target_node, None)
            scene.update_edges.emit()
            self.parentItem().costValue = None
            return
        
        if not new_cost.isdigit():
            if self.parentItem().costValue is None:
                self.setPlainText("")
                self.parentItem().setVisible(False)
            else:
                self.setPlainText(str(self.parentItem().costValue))
            return

        new_cost = int(new_cost)
        
        scene.graph.update_cost(source_node, target_node, new_cost)
        scene.update_edges.emit()
        self.parentItem().costValue = new_cost
        self.value = new_cost

    def focusOutEvent(self, event):
        self.isValid()
        super().focusOutEvent(event)

class CostItem(QGraphicsRectItem):
    def __init__(self, edge, cost, width=25, height=25):
        super().__init__(0, 0, width, height)

        self.start = edge.source
        self.end = edge.target
        self.value = cost
        self.setParentItem(edge)

        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("gray"),2))
        
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        
        self.label = CostLabelItem(str(self.value))
        self.label.setParentItem(self)
        
        if self.value is None or self.value == "None":
            self.setVisible(False)
        
        self.update_cost_position()
    
    def update_cost_position(self):
        if self.parentItem().source.scene().graph.isDirected:
            xC = self.parentItem().center.x()
            yC = self.parentItem().center.y()
        else:
            xC = (self.start.x() + self.end.x())/2
            yC = (self.start.y() + self.end.y())/2
        self.setPos(xC-12.5, yC-12.5)

    def mousePressEvent(self, event):
        self.setVisible(True)
        if self.scene().current_mode == 3:
            self.label.setFocus()
        super().mousePressEvent(event)
