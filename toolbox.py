import numpy as np


def BGR_img(img, BGR=[255, 255, 255]):
    image = img.copy()
    image = image.astype(np.float)
    for i in range(3):
        image[:, :, i] = image[:, :, i] * BGR[i] / 255
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image


def gray_img(img, low=70, upper=255):
    image = img.copy()
    gray = 0.1140 * image[:, :, 0] + 0.5870 * image[:, :, 1] + 0.2989 * image[:, :, 2]
    for i in range(3):
        image[:, :, i] = gray
    image = (image.astype(np.float) - low) / (upper - low)
    image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    return image


def check_gray(img):
    w, h, c = img.shape
    crop_img = img[w//2:w//2+10, h//2:h//2+10]
    return np.all(crop_img[:, :, 0] == crop_img[:, :, 1])
