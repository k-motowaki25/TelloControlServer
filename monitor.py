import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from server import Server
import threading


class MonitorPanel(QGraphicsView):
    COLOR = {'0': QColor('#4080ff'), '1': QColor('#40ff40'), '2': QColor('#ff4040')}
    DEFAULT_CIRCLE_SIZE = 10

    def __init__(self, tellos, coords):
        super().__init__()
        self.tellos = tellos
        self.coords = coords
        self.circles = {'0': {}, '1': {}, '2': {}}
        self.circle_size = 10
        self.w = self.size().width()
        self.h = self.size().height()
        self.init_ui()

    def init_ui(self):
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.init_circle()
        self.init_timer()

    def init_circle(self):
        def create_circle(self, color, coord_type):
            offset = self.circle_size / 2
            ellipse = QGraphicsEllipseItem(offset, offset, self.circle_size, self.circle_size)
            self.scene.addItem(ellipse)

            if coord_type == 'curt':
                ellipse.setPen(QPen(Qt.NoPen))
                ellipse.setBrush(color)
            elif coord_type == 'goal':
                pen = QPen(color)
                pen.setWidth(self.circle_size // 3)
                ellipse.setPen(pen)
                ellipse.setBrush(QBrush(Qt.NoBrush))

            ellipse.setVisible(False)
            return ellipse
        
        for id in self.circles.keys():
            for coord_type in ['curt', 'goal']:
                self.circles[id][coord_type] = create_circle(self, self.COLOR[id], coord_type)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1)
    
    def resizeEvent(self, event):
        '''ウィンドウサイズの変更時に呼ばれる'''
        super().resizeEvent(event)
        new_size = event.size()
        new_w = new_size.width()
        new_h = new_size.height()
        self.scene.setSceneRect(0, 0, new_w, new_h)
        self.w = self.size().width()
        self.h = self.size().height()
        self.circle_size = max(self.DEFAULT_CIRCLE_SIZE, min(self.w, self.h)//20)

    def update_position(self):
        circle_offset = self.circle_size / 2
        for id in self.circles.keys():
            if id in self.tellos:
                tello = self.tellos[id]
                for coord, circle in zip(tello.coords.values(), self.circles[id].values()):
                    x, y, z = coord.values()
                    if self.coords == 'xz':
                        x = x * self.w - circle_offset
                        y = (1 - z) * self.h - circle_offset
                    elif self.coords == 'y':
                        x = 0.5 * self.w - circle_offset
                        y = y * self.h - circle_offset
                    circle.setRect(x, y, self.circle_size, self.circle_size)
                    circle.setVisible(True)
            else:
                for circle in self.circles[id].values():
                    circle.setVisible(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 300)
        self.labels = {'operation': None, 'coord': None, 'tello': None}

        self.server = Server('0.0.0.0', 12345)
        server_connection_thread = threading.Thread(target=self.server.listen)
        server_connection_thread.start()
        
        # 大枠の設定
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setColumnStretch(0, 7)
        self.layout.setColumnStretch(1, 3)

        # 描画パネルの設定
        self.graph_panel = QWidget()
        self.layout.addWidget(self.graph_panel, 0, 0)
        self.graph_panel.setStyleSheet('background-color: #222;')

        self.graph_layout = QGridLayout(self.graph_panel)
        self.graph_layout.setSpacing(20)
        self.graph_layout.setColumnStretch(0, 20)
        self.graph_layout.setColumnStretch(1, 1)

        tellos = self.server.devices['tello']

        #   x, z座標描画領域の設定
        xz_graph = MonitorPanel(tellos, 'xz')
        self.graph_layout.addWidget(xz_graph, 0, 0)
        xz_graph.setStyleSheet('background-color: #000;')
        xz_graph.setMinimumSize(50, 50)
        
        #   y座標描画領域の設定
        y_graph = MonitorPanel(tellos, 'y')
        self.graph_layout.addWidget(y_graph, 0, 1)
        y_graph.setStyleSheet('background-color: #000;')
        y_graph.setMinimumSize(12, 12) # 円のサイズ分確保

        # 接続状況パネルの設定
        self.connect_panel = QWidget()
        self.layout.addWidget(self.connect_panel, 0, 1)
        self.connect_panel.setStyleSheet('background-color: #333;')

        self.connect_layout = QGridLayout(self.connect_panel)

        #   デバイスラベルの設定
        for key in self.labels.keys():
            self.labels[key] = QLabel()
            self.connect_layout.addWidget(self.labels[key])
        self.update_labels()

        self.update_labels_timer = QTimer(self)
        self.update_labels_timer.timeout.connect(self.update_labels)
        self.update_labels_timer.start(100)

    def update_labels(self):
        for device_type, device_ids in self.server.devices.items():
            self.labels[device_type].setText(f'{device_type}: {list(device_ids.keys())}')


app = QApplication(sys.argv)
font = QFont('SF Mono', 10)
app.setFont(font)

with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())

main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())
