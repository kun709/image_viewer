import sys
import os
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout,\
    QGroupBox, QSpinBox, QLCDNumber, QLineEdit, QCheckBox

from image_view import get_image, get_image_list, cv2qpix, check_type
from file_tree import get_artist_tree, update_artist_widget, load_likeability, open_tree
from util import str_clean
from toolbox import gray_img, BGR_img


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.path = 'E:/hitomi_downloader_GUI/hitomi_downloaded/'
        self.img_loc = 0
        self.img_view = False
        self.read_page = 0
        self.img_path = ''
        self.selected_img = None
        self.load_page = 0
        self.img_list = []
        self.dir_list = []

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.timeout_img_load)

        self.lbl_img = QLabel()
        self.lbl_img.setFixedSize(1390, 1390)
        self.lbl_img.setAlignment(Qt.AlignCenter)

        self.pbar = QProgressBar(self)
        self.pbar.setFixedWidth(400)
        self.pbar.setValue(0)

        tool = [
            self.show_page(),
            self.histogram_group(),
            self.BGR_group(),
            self.ddr_timer_group(),
            self.extra_checkbox()
        ]
        tool_box = QVBoxLayout()
        for t in tool:
            tool_box.addWidget(t)

        self.lbl_img.setPixmap(cv2qpix(get_image('84551220_p0.jpg')['img']))

        self.qTree = get_artist_tree(self.path)
        self.qTree.setFixedWidth(400)
        self.qTree.itemSelectionChanged.connect(self.handleSC)
        load_likeability(self.qTree)
        tree_box = QVBoxLayout()
        tree_box.addWidget(self.qTree)
        tree_box.addWidget(self.pbar)

        main_box = QHBoxLayout()
        main_box.addLayout(tree_box)
        main_box.addWidget(self.lbl_img)
        main_box.addLayout(tool_box)

        self.setLayout(main_box)

        self.setWindowTitle('Hitomi Viewer')
        self.resize(2000, 1000)
        self.move(620, 0)
        self.show()

    def set_main_image(self):
        img = self.img_list[self.img_loc]['img']
        img_type = check_type(img)
        if img_type == 'numpy':
            # image filtering
            if self.histo_io:
                img = gray_img(img, low=self.histo_value)
            if self.BGR_io:
                img = BGR_img(img, self.BGR_value)
            # show image
            self.lbl_img.setPixmap(cv2qpix(img))
        elif img_type == 'gif':
            if self.lbl_img.movie() is not None:
                self.lbl_img.movie().stop()
            self.lbl_img.setMovie(img)
            img.start()
        else:
            print('Fail')

    def wheelEvent(self, e, min_page=12):
        if self.img_view:
            if (self.load_page < (self.img_loc + 2)) and (self.load_page < (len(self.dir_list) - 3)):
                self.img_list += get_image_list(self.img_path,
                                                self.dir_list[self.load_page:self.load_page+min_page])
                self.load_page = min(self.load_page + min_page, len(self.dir_list))
                self.pbar.setValue(int(100 * self.load_page / len(self.dir_list)))
                self.img_list.sort(key=lambda x: str_clean(x['name']))
            if e.angleDelta().y() < 0:  # next image
                if self.img_loc < (len(self.img_list) - 1):
                    self.img_loc += 1
            else:
                if 0 < self.img_loc:
                    self.img_loc -= 1
            if self.read_page < self.img_loc:
                self.read_page = self.img_loc
                if self.read_page == 1:
                    self.selected_img.setText(3, str(int(self.selected_img.text(3)) + 2))
                elif self.read_page > 1:
                    self.selected_img.setText(3, str(int(self.selected_img.text(3)) + 1))
                update_artist_widget(self.qTree)
            self.set_page_indicator()
            self.set_main_image()

    def timeout_img_load(self):
        if self.load_page < len(self.dir_list):
            self.img_list.append(get_image(self.img_path + self.dir_list[self.load_page]))
            self.load_page += 1
            self.pbar.setValue(int(100 * self.load_page / len(self.dir_list)))
            self.set_page_indicator()
            if self.load_page == len(self.dir_list):
                self.timer.stop()
        else:
            self.timer.stop()

    def handleSC(self, start_page=3):
        selected_img = self.qTree.selectedItems()[0]
        self.pbar.setValue(0)
        if selected_img.text(1) != '':
            self.img_loc = 0
            self.img_view = True
            self.read_page = 0
            self.selected_img = selected_img
            self.img_path = self.path + selected_img.text(4) + '/'
            self.dir_list = os.listdir(self.img_path)
            self.dir_list.sort(key=lambda x: str_clean(x))

            self.img_list = [get_image(self.img_path + self.dir_list[i]) for i in range(start_page)]

            self.load_page = start_page
            self.timer.start()
            self.set_main_image()

    def histogram_group(self):
        self.groupbox_histo = QGroupBox('Histogram Adjustment')
        self.groupbox_histo.setCheckable(True)
        self.groupbox_histo.setChecked(False)
        self.histo_io = False
        self.histo_value = 70

        dark_spin = QSpinBox()
        dark_spin.setRange(0, 254)
        dark_spin.setSingleStep(1)
        dark_spin.setValue(self.histo_value)
        dark_spin.valueChanged.connect(self.histo_group_spin)

        self.groupbox_histo.clicked.connect(self.histo_group_click)

        vbox = QVBoxLayout()
        vbox.addWidget(dark_spin)
        self.groupbox_histo.setLayout(vbox)
        self.groupbox_histo.setMaximumHeight(70)
        return self.groupbox_histo

    def histo_group_click(self):
        self.groupbox_BGR.setChecked(False)
        self.BGR_io = False
        self.histo_io = self.groupbox_histo.isChecked()
        self.set_main_image()

    def BGR_group(self):
        self.groupbox_BGR = QGroupBox('BRG Adjustment')
        self.groupbox_BGR.setCheckable(True)
        self.groupbox_BGR.setChecked(False)
        self.BGR_io = False
        self.BGR_value = [255, 255, 255]

        slider_list = list()
        for i, (name, func) in enumerate(zip(['b', 'r', 'g'],
                                             [self.BGR_group_spin_r,
                                              self.BGR_group_spin_g,
                                              self.BGR_group_spin_b])):
            # dark_spin = QSlider(Qt.Horizontal, self)
            dark_spin = QSpinBox()
            dark_spin.setRange(1, 255)
            dark_spin.setSingleStep(1)
            dark_spin.setValue(255)
            dark_spin.valueChanged.connect(func)
            slider_list.append(dark_spin)

        self.groupbox_BGR.clicked.connect(self.rgb_group_click)

        vbox = QVBoxLayout()
        for i, name in enumerate(['R', 'G', 'B']):
            lbl = QLabel()
            lbl.setText(name)

            layout = QHBoxLayout()
            layout.addWidget(lbl)
            layout.addWidget(slider_list[i])
            vbox.addLayout(layout)
        self.groupbox_BGR.setLayout(vbox)
        self.groupbox_BGR.setMaximumHeight(100)
        return self.groupbox_BGR

    def rgb_group_click(self):
        self.groupbox_histo.setChecked(False)
        self.histo_io = False
        self.BGR_io = self.groupbox_BGR.isChecked()
        self.set_main_image()

    def histo_group_spin(self, q_value):
        self.histo_value = q_value
        self.set_main_image()

    def BGR_group_spin_r(self, q_value):
        self.BGR_value[2] = q_value
        self.set_main_image()

    def BGR_group_spin_g(self, q_value):
        self.BGR_value[1] = q_value
        self.set_main_image()

    def BGR_group_spin_b(self, q_value):
        self.BGR_value[0] = q_value
        self.set_main_image()

    def ddr_timer_group(self):
        self.groupbox_ddr_timer = QGroupBox('DDR Timer')

        self.timer_ddr = QTimer(self)
        self.start_time = QTime.currentTime()
        self.timer_ddr.setInterval(1000)
        self.timer_ddr.timeout.connect(self.timeout_ddr)

        self.lcd = QLCDNumber()
        self.lcd.display('')
        self.lcd.setDigitCount(8)
        self.timeout_ddr()

        layout = QVBoxLayout()
        subLayout = QHBoxLayout()

        self.btnStart = QPushButton("시작")
        self.btnStart.clicked.connect(self.onStartButtonClicked)

        self.btnStop = QPushButton("멈춤")
        self.btnStop.clicked.connect(self.onStopButtonClicked)

        layout.addWidget(self.lcd)

        subLayout.addWidget(self.btnStart)
        subLayout.addWidget(self.btnStop)
        layout.addLayout(subLayout)

        self.btnStop.setEnabled(False)

        self.groupbox_ddr_timer.setLayout(layout)
        self.groupbox_ddr_timer.setMaximumHeight(100)
        return self.groupbox_ddr_timer

    def timeout_ddr(self):
        second_gap = self.start_time.secsTo(QTime.currentTime()) % 86400
        result = ''
        for _ in range(2):
            result = ':' + str(second_gap % 60).zfill(2) + result
            second_gap //= 60
        result = str(second_gap).zfill(2) + result
        self.lcd.display(result)

    def onStartButtonClicked(self):
        self.timer_ddr.start()
        self.start_time = QTime.currentTime()
        self.btnStop.setEnabled(True)
        self.btnStart.setEnabled(False)

    def onStopButtonClicked(self):
        self.timer_ddr.stop()
        self.btnStop.setEnabled(False)
        self.btnStart.setEnabled(True)

    def show_page(self):
        self.groupbox_page = QGroupBox('Page')
        self.page_lbl = QLabel(self)
        self.page_lbl.setText('/    0     load    0 pages')

        self.qle = QLineEdit(self)
        self.qle.textChanged[str].connect(self.PageChanged)
        self.qle.setAlignment(Qt.AlignRight)

        layout = QHBoxLayout()
        layout.addWidget(self.qle)
        layout.addWidget(self.page_lbl)

        self.groupbox_page.setLayout(layout)
        self.groupbox_page.setMaximumHeight(50)
        return self.groupbox_page

    def extra_checkbox(self):
        self.groupbox_extra = QGroupBox('Extra checkbox')

        cb_tree_open = QCheckBox('All tree open', self)
        cb_tree_open.stateChanged.connect(self.change_tree_open)

        layout = QVBoxLayout()
        layout.addWidget(cb_tree_open)

        self.groupbox_extra.setLayout(layout)
        self.groupbox_extra.setMaximumHeight(50)
        return self.groupbox_extra

    def change_tree_open(self, state):
        if state == Qt.Checked:
            open_tree(self.qTree, True)
        else:
            open_tree(self.qTree, False)

    def set_page_indicator(self):
        page = str(self.selected_img.text(2))
        self.qle.setText(str(self.img_loc + 1))
        self.page_lbl.setText('/ {:>4}     load {:>4} pages'.format(page, str(self.load_page)))
        pass

    def PageChanged(self, text):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

