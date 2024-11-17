import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt

from paddleocr import PaddleOCR
from PIL import Image,ImageDraw,ImageFont
paddleocr = PaddleOCR() # 推理模型路径

def ocr(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = paddleocr.ocr(image)
    pilimg = Image.fromarray(image)
    draw = ImageDraw.Draw(pilimg)  # 图片上打印

    font = ImageFont.truetype("simsun.ttc", 20, encoding="utf-8")
    for line in result:
        for word in line:
            # word[0] 是检测框的四个顶点坐标，word[1] 是识别的文字
            box = word[0]
            text = word[1][0]
            confidence = word[1][1]
            # print("text",text)
            # print("confidence",confidence)
            # 将检测框绘制到图片上
            points = np.array([[int(p[0]), int(p[1])] for p in box], np.int32)
            # cv2.polylines(img, [points], isClosed=True, color=(0, 255, 0), thickness=2)
            draw.text((int(box[0][0]), int(box[0][1])), text, (255, 0, 0), font=font)
            # draw.text(text_position, text, font=font, fill=(255, 0, 0))
            # 将识别的文字绘制到图片上
        # cv2.putText(img, text, (int(box[0][0]), int(box[0][1])), font, 0.5, (0, 0, 255), 2)
    # cv2.putText(img, "你好", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cvimage = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)
    return cvimage

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCV Camera in Qt")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建一个垂直布局
        layout = QVBoxLayout(central_widget)

        # 创建一个 QLabel 用于显示图像
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # 初始化 OpenCV 摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            sys.exit(1)

        # 创建一个定时器，用于定期更新图像
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000)  # 每 30 毫秒更新一次

    def update_frame(self):
        # 读取一帧
        ret, frame = self.cap.read()
        if ret:
            # 将 OpenCV 图像转换为 QImage

            rgb_image=ocr(frame)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

            # 显示图像
            self.image_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        # 释放摄像头资源
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())
