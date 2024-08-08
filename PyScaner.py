from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np
import OpenCV_helper as sc


class ScalableGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(ScalableGraphicsView, self).__init__(*args, **kwargs)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        
        self.is_dragging = False  # Флаг для отслеживания перетаскивания
        self.last_mouse_pos = QtCore.QPoint()  # Последняя позиция мыши

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()  # Запоминаем позицию мыши при нажатии
            self.setCursor(QtCore.Qt.ClosedHandCursor)  # Меняем курсор на "рука"

        super(ScalableGraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.translateView(delta)  # Перемещаем вид
        super(ScalableGraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(QtCore.Qt.ArrowCursor)  # Возвращаем курсор в исходное состояние

        super(ScalableGraphicsView, self).mouseReleaseEvent(event)

    def translateView(self, delta):
        # Перемещаем сцену
        delta_x = delta.x()
        delta_y = delta.y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta_x)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta_y)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(656, 539)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.choose = QtWidgets.QPushButton(self.centralwidget)
        self.choose.setGeometry(QtCore.QRect(20, 0, 82, 28))
        self.choose.setObjectName("choose")
        self.change = QtWidgets.QPushButton(self.centralwidget)
        self.change.setGeometry(QtCore.QRect(110, 0, 82, 28))
        self.change.setObjectName("change")
        self.graphicsView = ScalableGraphicsView(self.centralwidget)  # Используем наш подкласс
        self.graphicsView.setGeometry(QtCore.QRect(20, 40, 611, 481))
        self.graphicsView.setObjectName("graphicsView")
        self.save = QtWidgets.QPushButton(self.centralwidget)
        self.save.setGeometry(QtCore.QRect(200, 0, 82, 28))
        self.save.setObjectName("change_2")

        self.alpha_slider = QtWidgets.QSlider(self.centralwidget)
        self.alpha_slider.setGeometry(QtCore.QRect(640, 40, 16, 481))
        self.alpha_slider.setOrientation(QtCore.Qt.Vertical)
        self.alpha_slider.setObjectName("alpha_slider")

        # Установка минимального, максимального значений и начального значения для alpha_slider
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(120)
        self.alpha_slider.setValue(30)  # Установить начальное значение


        self.beta_slider = QtWidgets.QSlider(self.centralwidget)
        self.beta_slider.setGeometry(QtCore.QRect(0, 40, 16, 481))
        self.beta_slider.setOrientation(QtCore.Qt.Vertical)
        self.beta_slider.setObjectName("beta_slider")
        # Установка минимального, максимального значений и начального значения для beta_slider
        self.beta_slider.setMinimum(-5)
        self.beta_slider.setMaximum(115)
        self.beta_slider.setValue(0)  # Установить начальное значение


        # Добавляем сочетание клавиш для вставки изображения из буфера обмена
        self.shortcut_paste = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), MainWindow)
        self.shortcut_paste.activated.connect(self.paste_from_clipboard)


        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Подключаем кнопку к слоту
        self.choose.clicked.connect(self.open_file_dialog)
        self.change.clicked.connect(self.change_black_white)
        self.save.clicked.connect(self.save_image)

        self.alpha_slider.valueChanged.connect(self.alpha_slider_changed)
        self.beta_slider.valueChanged.connect(self.beta_slider_changed)




        # Переменная для хранения пути к файлу
        self.image_path = None
        self.cv_image = None
        #Сначала будем показывать черно изображение
        self.black = True

        self.factor_alpha = 1
        self.factor_beta = 0

    def paste_from_clipboard(self):
        clipboard = QtGui.QGuiApplication.clipboard()
        image = clipboard.pixmap().toImage()
        if not image.isNull():
            self.image_path = None
            # Преобразуем QImage в формат, который поддерживает OpenCV
            image = image.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
            width, height = image.width(), image.height()
            bytes_per_line = 4 * width
            image_data = image.bits().asstring(bytes_per_line * height)
            self.cv_image = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width, 4))

            # Конвертируем изображение из формата BGRA в BGR
            self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGRA2BGR)
            self.image_white, self.image_black = sc.scan_image(image = self.cv_image)
            print("ctrl + V")
            self.update()
        print("ctrl + V без фото")
    def alpha_slider_changed(self):
        self.factor_alpha = self.alpha_slider.value() / 30.0
        print(f"alpha: {self.factor_alpha}")
        if self.image_path is not None:
            self.image_white, self.image_black = sc.scan_image(f"{self.image_path}", self.factor_alpha, self.factor_beta)
        else:
            self.image_white, self.image_black = sc.scan_image(image = self.cv_image, alpha = self.factor_alpha, beta = self.factor_beta)
        self.update()

    def beta_slider_changed(self):
        self.factor_beta = self.beta_slider.value() / 30.0
        print(f"beta: {self.factor_beta}")
        if self.image_path is not None:
            self.image_white, self.image_black = sc.scan_image(f"{self.image_path}", self.factor_alpha, self.factor_beta)
        else:
            self.image_white, self.image_black = sc.scan_image(image = self.cv_image, alpha = self.factor_alpha, beta = self.factor_beta)
        self.update()

    def save_image(self):
        # Открываем диалоговое окно для выбора файла
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save Image File", "",
                                                            "Images (*.png);;All Files (*)", options=options)
        if file_path:
            # Если расширение не указано, добавляем .png
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            # Определяем, какое изображение сохранить
            if self.black:
                image = self.image_black
            else:
                image = self.image_white
            
            # Сохраняем изображение в формате PNG
            cv2.imwrite(file_path, image)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Сканер"))
        self.choose.setText(_translate("MainWindow", "choose..."))
        self.change.setText(_translate("MainWindow", "change"))
        self.save.setText(_translate("MainWindow", "save"))
    # Сменяем черно-белое изображение
    def change_black_white(self):
        self.black = not self.black
        self.update()
    # Слот для открытия диалогового окна
    def open_file_dialog(self):
        # Открываем диалоговое окно для выбора файла изображения
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Choose Image File", "",
                                                   "Images (*.png *.jpg *.bmp *.gif);;All Files (*)", options=options)
        if file_path:
            self.cv_image = None
            self.image_path = str(file_path)  # Сохраняем путь к файлу в переменной
            print(f"Выбранный файл: {self.image_path}")  # Печатаем путь к файлу в консоль
            self.image_white, self.image_black = sc.scan_image(f"{self.image_path}")
            self.update()
    def display_image(self):
        if self.black:
            image = self.image_black
        else:
            image = self.image_white
        height, width, channel = image.shape
        bytes_per_line = 4 * width
        q_image = QtGui.QImage(image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGBA8888)

        # Создаем сцену и добавляем изображение
        scene = QtWidgets.QGraphicsScene()
        pixmap = QtGui.QPixmap.fromImage(q_image)
        scene.addPixmap(pixmap)

        # Устанавливаем сцену в QGraphicsView
        self.graphicsView.setScene(scene)

        # Масштабируем изображение, чтобы оно поместилось в области просмотра
        self.graphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)


    
    def update(self):
        self.display_image()

# Создаем приложение и главное окно
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()  # Показываем окно
    sys.exit(app.exec_())  # Запускаем основной цикл приложения
