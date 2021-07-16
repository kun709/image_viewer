import cv2
import os
import time
import numpy as np
import parmap
import ctypes
from multiprocessing import Process, Manager, shared_memory, cpu_count
from turbojpeg import TurboJPEG


SCALE = 1340
CORE = cpu_count()


def jpg_reader(path, mode=0):
    return TurboJPEG().decode(open(path, "rb").read(), mode)


def resize_img(cvImg_dict):
    cvImg = cvImg_dict['img']
    height, width, channel = cvImg.shape

    cvImg_result = np.zeros((SCALE, SCALE, channel), dtype=np.uint8)
    cvImg_result += 255

    if (height < SCALE) and (width < SCALE):
        gap_x = (SCALE - width) // 2
        gap_y = (SCALE - height) // 2
        cvImg_result[gap_y:gap_y + height, gap_x:gap_x + width] = cvImg
    elif height > width:
        size = (int(width * SCALE / height), SCALE)
        gap = (SCALE - size[0]) // 2
        cvImg_result[:, gap:gap + size[0]] = cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA)
    else:
        size = (SCALE, int(height * SCALE / width))
        gap = (SCALE - size[1]) // 2
        cvImg_result[gap:gap + size[1], :] = cv2.resize(cvImg, size, interpolation=cv2.INTER_AREA)

    cvImg_dict['img'] = cvImg_result
    return cvImg_dict


def sub_process(input_list):
    return [resize_img(x) for x in input_list]


def imread_process(input_list):
    return [{'img': cv2.imread(x, 1), 'name': x.split('/')[-1]} for x in input_list]


def get_image_list(img_path, dir_list):
    img_full_path = [img_path + d for d in dir_list]
    print('data length :', len(img_full_path))
    if True:
        current = time.time()
        splited_data = np.array_split(img_full_path, CORE)
        image_list = parmap.map(imread_process, splited_data, pm_pbar=False, pm_processes=CORE)
        print(time.time() - current)
    else:
        current = time.time()
        image_list = np.array_split([cv2.imread(path) for path in img_full_path], CORE)
        print(time.time() - current)

    current = time.time()
    image_list_resized = parmap.map(sub_process, image_list, pm_pbar=False, pm_processes=CORE)
    print(time.time() - current)

    result = list()
    for re in image_list_resized:
        for r in re:
            result.append(r)
    return result


if __name__ == '__main__':
    img_path = 'E:/hitomi_downloader_GUI/hitomi_downloaded/[Shennai Misha][1685887]/'
    dir_list = os.listdir(img_path)

    get_image_list(img_path, dir_list)

    # current = time.time()
    # img2 = jpg_reader(img_path, 0)
    # print(time.time() - current)

    # print(img2.shape)
    # cv2.imshow('image', img2)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
