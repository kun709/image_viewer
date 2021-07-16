from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import parmap
from multiprocessing import cpu_count
from PyQt5.QtGui import QMovie

CORE = cpu_count()
SCALE = 1370


def cv2qpix(cv_img_brg):
    cv_img = cv2.cvtColor(cv_img_brg, cv2.COLOR_BGR2RGB)
    height, width, channel = cv_img.shape
    return QPixmap(QImage(cv_img.data, width, height, cv_img.strides[0], QImage.Format_RGB888))


def check_type(file):
    file_type = type(file)
    if file_type == np.ndarray:
        return 'numpy'
    elif file_type == QMovie:
        return 'gif'
    return 'unknown'


def get_image(x):
    if x.endswith('jpg'):
        return resize_img({'img': cv2.imread(x, 1), 'name': x.split('/')[-1]})
    elif x.endswith('gif'):
        return resize_img({'img': QMovie(x), 'name': x.split('/')[-1]})


def resize_img(cvImg_dict):
    cvImg = cvImg_dict['img']
    img_type = check_type(cvImg)
    if img_type == 'numpy':
        height, width, channel = cvImg.shape

        if (height < SCALE) and (width < SCALE):
            return cvImg_dict
        if height > width:
            size = (int(width * SCALE / height), SCALE)
            cvImg_dict['img'] = cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA)
        else:
            size = (SCALE, int(height * SCALE / width))
            cvImg_dict['img'] = cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA)
        return cvImg_dict
    elif img_type == 'gif':
        return cvImg_dict


def resize_img_with_border(cvImg_dict):
    cvImg = cvImg_dict['img']
    height, width, channel = cvImg.shape

    cvImg_result = np.zeros((SCALE, SCALE, channel), dtype=np.uint8)
    cvImg_result += 255

    if (height < SCALE) and (width < SCALE):
        gap_x = (SCALE - width) // 2
        gap_y = (SCALE - height) // 2
        cvImg_result = cv2.copyMakeBorder(cvImg, gap_y, SCALE - gap_y - height, gap_x, SCALE - gap_x - width,
                                          cv2.BORDER_CONSTANT, value=(255, 255, 255))
    elif height > width:
        size = (int(width * SCALE / height), SCALE)
        gap = (SCALE - size[0]) // 2
        cvImg_result = cv2.copyMakeBorder(cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA),
                                          0, 0, gap, SCALE - gap - size[0], cv2.BORDER_CONSTANT, value=(255, 255, 255))
    else:
        size = (SCALE, int(height * SCALE / width))
        gap = (SCALE - size[1]) // 2
        cvImg_result = cv2.copyMakeBorder(cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA),
                                          gap, SCALE - gap - size[1], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))

    cvImg_dict['img'] = cvImg_result
    return cvImg_dict


def sub_process(input_list):
    return [resize_img(x) for x in input_list]


def imread_process(input_list):
    output_list = list()
    for x in input_list:
        if x.endswith('jpg'):
            output_list.append({'img': cv2.imread(x, 1), 'name': x.split('/')[-1]})
        elif x.endswith('gif'):
            output_list.append({'img': QMovie(x), 'name': x.split('/')[-1]})
    return output_list


def get_image_list(img_path, dir_list):
    img_full_path = [img_path + d for d in dir_list]
    # image_list = [cv2.imread(path) for path in img_full_path]

    splited_data = np.array_split(img_full_path, CORE)
    image_list = parmap.map(imread_process, splited_data, pm_pbar=False, pm_processes=CORE)
    image_list_resized = parmap.map(sub_process, image_list, pm_pbar=False, pm_processes=CORE)
    result = list()
    for re in image_list_resized:
        for r in re:
            result.append(r)
    return result
