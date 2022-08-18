from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SceneWindowBase(QGraphicsView):
    def __init__(self):
        super(SceneWindowBase, self).__init__()
        self._logoPath = Path(__file__).parent.parent / "res/logo.png"
        self._logoPixmap = QPixmap(str(self._logoPath))
        self._logoLabel = QLabel()

        self._setUI()

    def _setUI(self):
        self._setWidget()
        self._setLayout()

    def _setWidget(self):
        self.setObjectName("sceneWindowBase")
        self._logoLabel.setPixmap(self._logoPixmap)
        self._logoLabel.setAlignment(Qt.AlignCenter)

    def _setLayout(self):
        hLayout = QHBoxLayout(self)
        hLayout.addWidget(self._logoLabel)


    #     self._minGap = 4                                    # 最小线间隔
    #     self._maxGap = 14                                   # 最大线间隔
    #     self._gap = (self._minGap + self._maxGap) / 2       # 当前线间隔
    #     self._startX = self.width() / 2                     # 竖线初始x坐标（从窗口中间开始）
    #     self._startY = self.height() / 2                    # 横线初始y坐标（从窗口中间开始）
    #     self._lightPen = QPen(QColor(222, 222, 222))        # 两只粗细不同的画笔
    #     self._darkPen = QPen(QColor(222, 222, 222))
    #     self._darkPen.setWidth(2)
    #
    #     self._setUI()
    #
    # def _setUI(self):
    #     self._setWidget()
    #
    # def _setWidget(self):
    #     self._setBackgroundColor()
    #
    # def _setBackgroundColor(self):
    #     palette = QPalette()
    #     palette.setColor(QPalette.Background, QColor(250, 250, 250))
    #     self.setPalette(palette)
    #     self.setAutoFillBackground(True)
    #
    # def _drawRowLines(self, painter):
    #     lineCount = 0
    #     biggerY = self._startY
    #     smallerY = self._startY
    #
    #     painter.setPen(self._darkPen)
    #
    #     while True:
    #         painter.drawLine(QPointF(0.0, biggerY), QPointF(self.width(), biggerY))
    #         painter.drawLine(QPointF(0.0, smallerY), QPointF(self.width(), smallerY))
    #
    #         biggerY += self._gap
    #         smallerY -= self._gap
    #         if smallerY <= 0 or biggerY >= self.height():
    #             break
    #
    #         # 每间隔一定数量的线，就画一条粗一点的横线
    #         lineCount += 1
    #         if lineCount == 10:
    #             painter.setPen(self._darkPen)
    #             lineCount = 0
    #         else:
    #             painter.setPen(self._lightPen)
    #
    # def _drawColLines(self, painter):
    #     """画竖线"""
    #     lineCount = 0
    #     biggerX = self._startX
    #     smallerX = self._startX
    #
    #     painter.setPen(self._darkPen)
    #
    #     while True:
    #         painter.drawLine(QPointF(biggerX, 0.0), QPointF(biggerX, self.height()))
    #         painter.drawLine(QPointF(smallerX, 0.0), QPointF(smallerX, self.height()))
    #
    #         biggerX += self._gap
    #         smallerX -= self._gap
    #         if smallerX <= 0 or biggerX >= self.width():
    #             break
    #
    #         # 每间隔一定数量的线，就画一条粗一点的竖线
    #         lineCount += 1
    #         if lineCount == 10:
    #             painter.setPen(self._darkPen)
    #             lineCount = 0
    #         else:
    #             painter.setPen(self._lightPen)
    #
    # def paintEvent(self, event):
    #     super(SceneWindowBase, self).paintEvent(event)
    #     painter = QPainter(self)
    #     self._drawRowLines(painter)
    #     self._drawColLines(painter)
    #
    # def wheelEvent(self, event):
    #     """滚轮控制线间隔"""
    #     super(SceneWindowBase, self).wheelEvent(event)
    #     if event.angleDelta().y() > 0:
    #         self._gap += 0.07
    #     elif event.angleDelta().y() < 0:
    #         self._gap -= 0.07
    #
    #     if self._gap >= self._maxGap:
    #         self._gap = self._minGap
    #     elif self._gap <= self._minGap:
    #         self._gap = self._maxGap
    #
    #     self.update()
    #
    # def resizeEvent(self, event):
    #     super(SceneWindowBase, self).resizeEvent(event)
    #     self._startX = self.width() / 2
    #     self._startY = self.height() / 2
    #     self.update()