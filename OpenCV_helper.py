#Скрипт, которые делает скан рисунков
import cv2
from PIL import Image
import numpy as np

def scan_image(image_path = None, alpha = 1, beta = 0, image = None):
    if image is None:
        #Загружаем изображение
        raw_image = Image.open(image_path)
        #raw_image = cv2.imread(image_path)
    else:
        raw_image = image.copy()
    image_cv = cv2.cvtColor(np.array(raw_image), cv2.COLOR_RGB2BGR)
    image = cv2.convertScaleAbs(image_cv, alpha=alpha, beta=beta)
    #Преобразуем изображение в черно-белый формат
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, threshold_image = cv2.threshold(gray_image, 127, 255, 0)

    # Преобразуем изображение в формат RGBA, чтобы добавить прозрачность
    image_alpha = cv2.cvtColor(threshold_image, cv2.COLOR_RGB2RGBA)
    white_mask = np.all(image_alpha[:, :, :3] == [255, 255, 255], axis=-1)
    black_mask = np.all(image_alpha[:, :, :3] == [0, 0, 0], axis=-1)

    image_black = image_alpha.copy()
    image_black[white_mask, 3] = 0
    image_white = image_black.copy()
    image_white[black_mask, :] = [255, 255, 255, 255]
    
    return image_white, image_black