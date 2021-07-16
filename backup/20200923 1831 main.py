import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout
import os
import multiprocessing

from image_view import get_image
from file_tree import get_artist_tree
from util import *


def get_img_list(img_list, img_path, dir_list):
    for i, p in enumerate(dir_list):
        img_list.append({'img': get_image(img_path + p), 'name': p})


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.path = 'E:/hitomi_downloader_GUI/hitomi_downloaded/'
        self.img_loc = 0
        self.img_path = ''
        self.img_list = []

        manager = multiprocessing.Manager()
        self.return_dict = manager.dict()

        self.lbl_img = QLabel()
        self.pbar = QProgressBar(self)
        self.pbar.setFixedWidth(400)
        self.pbar.setValue(0)

        btn1 = QPushButton('&Button1', self)
        btn1.setCheckable(True)
        btn1.toggle()

        qImg = get_image('84365202_p0.png')
        self.lbl_img.setPixmap(qImg)

        self.qTree = get_artist_tree(self.path)
        self.qTree.setFixedWidth(400)
        # qTree.itemClicked.connect(self.onItemClicked)
        self.qTree.itemSelectionChanged.connect(self.handleSC)

        tree_box = QVBoxLayout()
        tree_box.addWidget(self.qTree)
        tree_box.addWidget(self.pbar)

        main_box = QHBoxLayout()
        main_box.addLayout(tree_box)
        main_box.addWidget(self.lbl_img)
        main_box.addWidget(btn1)

        self.setLayout(main_box)

        self.setWindowTitle('Hitomi Viewer')
        self.resize(2000, 1000)
        self.move(620, 0)
        self.show()

    def wheelEvent(self, e):  # e ; QWheelEvent
        if len(self.img_list) == 1:
            temp_list = os.listdir(self.img_path)
            temp_list.sort(key=str2int)
            for i, p in enumerate(temp_list):
                self.img_list.append(get_image(self.img_path + p))
                self.pbar.setValue(int(100 * i / (len(temp_list) - 1)))
        if len(self.img_list) > 0:
            if e.angleDelta().y() < 0:  # next image
                if self.img_loc < (len(self.img_list) - 1):
                    self.img_loc += 1
            else:
                if 0 < self.img_loc:
                    self.img_loc -= 1

            self.lbl_img.setPixmap(self.img_list[self.img_loc])

    def handleSC(self):
        selected_img = self.qTree.selectedItems()[0]
        if selected_img.text(1) != '':
            self.img_loc = 0
            self.img_path = self.path + '/' + selected_img.text(4) + '/'

            temp_list = os.listdir(self.img_path)
            temp_list.sort(key=str2int)
            self.img_list = [get_image(self.img_path + temp_list[0])]
            self.lbl_img.setPixmap(self.img_list[self.img_loc])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
