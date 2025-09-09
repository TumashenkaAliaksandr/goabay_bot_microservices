import sys
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QApplication,
    QTextEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QFormLayout, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

API_BASE = 'http://164.92.198.72//api/products/'
ORDERS_API_BASE = 'http://164.92.198.72//api/orders/'  # пример API для заказов
CREATE_PRODUCT_API = 'http://164.92.198.72//api/products/create/'  # пример API создания продукта

class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.show_product_details)

        self.detail_widget = QTextEdit()
        self.detail_widget.setReadOnly(True)

        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setStyleSheet("border: 1px solid black")

        details_layout = QVBoxLayout()
        details_layout.addWidget(self.detail_widget)
        details_layout.addWidget(self.image_label)

        self.layout.addWidget(self.list_widget, 2)
        self.layout.addLayout(details_layout, 3)

        self.setLayout(self.layout)

        self.products = []
        self.fetch_products()

    def fetch_products(self):
        try:
            response = requests.get(API_BASE)
            response.raise_for_status()
            self.products = response.json()
            self.list_widget.clear()
            for product in self.products:
                self.list_widget.addItem(f"{product['name']} - {product['price']} ₽")
        except Exception as e:
            self.list_widget.clear()
            self.list_widget.addItem(f"Ошибка загрузки: {e}")

    def show_product_details(self, current, previous):
        if not current:
            self.detail_widget.clear()
            self.image_label.clear()
            return
        index = self.list_widget.row(current)
        prod = self.products[index]
        details = f"Название: {prod['name']}\nЦена: {prod['price']} ₽\nОписание:\n{prod.get('desc', 'отсутствует')}"
        self.detail_widget.setText(details)

        image_url = prod.get('image')
        if image_url:
            try:
                img_data = requests.get(image_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio))
            except Exception:
                self.image_label.clear()
        else:
            self.image_label.clear()

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Создаем фигуру matplotlib и канвас для отображения графика
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.plot_sample()

    def plot_sample(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        # Пример простого графика
        x = [1, 2, 3, 4, 5]
        y = [10, 5, 8, 12, 7]
        ax.plot(x, y, marker='o')
        ax.set_title("Пример графика продаж")
        ax.set_xlabel("Период")
        ax.set_ylabel("Продажи")
        self.canvas.draw()

class OrdersTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID заказа', 'Покупатель', 'Дата', 'Сумма'])

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.orders = []
        self.fetch_orders()

    def fetch_orders(self):
        try:
            response = requests.get(ORDERS_API_BASE)
            response.raise_for_status()
            self.orders = response.json()
            self.table.setRowCount(len(self.orders))
            for row, order in enumerate(self.orders):
                self.table.setItem(row, 0, QTableWidgetItem(str(order.get('id'))))
                self.table.setItem(row, 1, QTableWidgetItem(order.get('customer_name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(order.get('date', '')))
                self.table.setItem(row, 3, QTableWidgetItem(str(order.get('total', ''))))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Ошибка: {e}"))

class ProductFormTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.submit_btn = QPushButton("Создать продукт")

        layout.addRow("Название:", self.name_input)
        layout.addRow("Цена:", self.price_input)
        layout.addRow("Описание:", self.desc_input)
        layout.addRow(self.submit_btn)

        self.setLayout(layout)

        self.submit_btn.clicked.connect(self.create_product)

    def create_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        desc = self.desc_input.text().strip()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Название и цена обязательны!")
            return

        try:
            price_val = float(price)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом!")
            return

        data = {
            "name": name,
            "price": price_val,
            "desc": desc
        }
        try:
            response = requests.post(CREATE_PRODUCT_API, json=data)
            response.raise_for_status()
            QMessageBox.information(self, "Успех", "Продукт создан успешно!")
            # Опционально очищаем форму после успешного создания
            self.name_input.clear()
            self.price_input.clear()
            self.desc_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании продукта:\n{e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Админ панель проекта")

        self.tabs = QTabWidget()

        self.products_tab = ProductsTab()
        self.stats_tab = StatisticsTab()
        self.orders_tab = OrdersTab()
        self.form_tab = ProductFormTab()

        self.tabs.addTab(self.products_tab, "Продукты")
        self.tabs.addTab(self.stats_tab, "Статистика")
        self.tabs.addTab(self.orders_tab, "Заказы")
        self.tabs.addTab(self.form_tab, "Управление продуктами")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.resize(1000, 700)
    main_win.show()
    sys.exit(app.exec_())
