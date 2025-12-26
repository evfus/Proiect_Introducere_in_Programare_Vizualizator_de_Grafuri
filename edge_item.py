from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF
from cost_item import CostItem
import math

class EdgeItem(QGraphicsPathItem):
    def __init__(self, source_node, target_node, costValue, curve_sign):
        super().__init__()
        self.source = source_node
        self.target = target_node
        self.arrow_size = 15
        self.costValue = costValue
        self.center = None
        self.curveSign = curve_sign

        self.setPen(QPen(QColor("black"), 3))
        self.setZValue(0)
        
        self.update_path()

        self.cost = CostItem(self, self.costValue)

        self.source.edge_list.append(self)
        self.target.edge_list.append(self)

    def mousePressEvent(self, event):
        if self.scene().current_mode == 3:
            self.cost.setVisible(True)
            self.cost.label.setFocus()
        
        super().mousePressEvent(event)

    def update_path(self):
        p1 = self.source.scenePos()
        p2 = self.target.scenePos()
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        direction = QPointF(math.cos(angle), math.sin(angle))
            
        p2 = p2 - direction * 25
        p1 = p1 + direction * 25

        path = QPainterPath(p1)
        
        if self.source.scene().graph.isDirected == False:
            path.lineTo(p2)
        else:
            arrow_size = 15
            arrow_angle = math.radians(30)

            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            length = math.hypot(dx, dy)

            nx = -dy / length
            ny =  dx / length

            curve_offset = 70 * self.curveSign

            mid = (p1 + p2) / 2
            control = QPointF(
                mid.x() + nx * curve_offset,
                mid.y() + ny * curve_offset
            )

            path.quadTo(control, p2)
            self.center = (control + mid)/2

            tx = p2.x() - control.x()
            ty = p2.y() - control.y()
            angle = math.atan2(ty, tx)

            left = QPointF(
                p2.x() - arrow_size * math.cos(angle - arrow_angle),
                p2.y() - arrow_size * math.sin(angle - arrow_angle)
            )

            right = QPointF(
                p2.x() - arrow_size * math.cos(angle + arrow_angle),
                p2.y() - arrow_size * math.sin(angle + arrow_angle)
            )

            path.moveTo(p2)
            path.lineTo(left)
            path.lineTo(right)
            path.closeSubpath()
        self.setPath(path)

