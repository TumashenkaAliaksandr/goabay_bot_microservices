import sys
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QApplication,
    QTextEdit, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QFormLayout, QLineEdit, QMessageBox, QRadioButton, QButtonGroup, QGroupBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

API_BASE = 'http://164.92.198.72//api/products/'
ORDERS_API_BASE = 'http://164.92.198.72//api/orders/'
CREATE_PRODUCT_API = 'http://164.92.198.72//api/products/create/'


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

        self.figure = plt.figure(figsize=(6, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.radio_group_box = QGroupBox("Выберите тип графика")
        self.radio_layout = QHBoxLayout()

        self.hist_radio = QRadioButton("Гистограмма")
        self.pie_radio = QRadioButton("Круговая диаграмма")
        self.bar_radio = QRadioButton("Бар-чарт")
        self.scatter_radio = QRadioButton("Диаграмма рассеяния")
        self.heatmap_radio = QRadioButton("Тепловая карта")
        self.threeD_radio = QRadioButton("3D график")

        self.radio_layout.addWidget(self.hist_radio)
        self.radio_layout.addWidget(self.pie_radio)
        self.radio_layout.addWidget(self.bar_radio)
        self.radio_layout.addWidget(self.scatter_radio)
        self.radio_layout.addWidget(self.heatmap_radio)
        self.radio_layout.addWidget(self.threeD_radio)

        self.radio_group_box.setLayout(self.radio_layout)
        layout.addWidget(self.radio_group_box)
        self.setLayout(layout)

        self.load_data_from_api()

        # Подключение переключения графиков
        self.hist_radio.toggled.connect(self.update_plot)
        self.pie_radio.toggled.connect(self.update_plot)
        self.bar_radio.toggled.connect(self.update_plot)
        self.scatter_radio.toggled.connect(self.update_plot)
        self.heatmap_radio.toggled.connect(self.update_plot)
        self.threeD_radio.toggled.connect(self.update_plot)

        self.hist_radio.setChecked(True)
        self.update_plot()

    def load_data_from_api(self):
        try:
            response = requests.get(API_BASE)
            response.raise_for_status()
            products = response.json()

            self.prices = []
            for p in products:
                price = p.get('price', 0)
                try:
                    price_val = float(price)
                except (ValueError, TypeError):
                    price_val = 0
                self.prices.append(price_val)

            categories_raw = [p.get('category', 'Без категории') for p in products]
            categories_str = []
            for cat in categories_raw:
                if isinstance(cat, list):
                    cat_str = ', '.join(cat)
                else:
                    cat_str = str(cat)
                categories_str.append(cat_str)
            self.categories = list(set(categories_str))

            self.cat_sizes = []
            for category in self.categories:
                total = 0.0
                for p in products:
                    p_cat = p.get('category', 'Без категории')
                    if isinstance(p_cat, list):
                        p_cat_str = ', '.join(p_cat)
                    else:
                        p_cat_str = str(p_cat)
                    if p_cat_str == category:
                        price = p.get('price', 0)
                        try:
                            price_val = float(price)
                        except (ValueError, TypeError):
                            price_val = 0
                        total += price_val
                self.cat_sizes.append(total)

            self.months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май']
            self.sales = [20, 34, 30, 35, 27]
            import numpy as np
            self.x_scatter = np.random.rand(100)
            self.y_scatter = np.random.rand(100)
            self.z_scatter = np.random.rand(100)
            self.data_matrix = np.random.rand(8, 8)

        except Exception as e:
            print("Ошибка при загрузке данных из API:", e)
            self.prices = []
            self.categories = []
            self.cat_sizes = []
            self.months = []
            self.sales = []
            self.x_scatter = []
            self.y_scatter = []
            self.z_scatter = []
            self.data_matrix = []

    def update_plot(self):
        self.figure.clf()

        if self.hist_radio.isChecked():
            self.plot_histogram()
        elif self.pie_radio.isChecked():
            self.plot_pie()
        elif self.bar_radio.isChecked():
            self.plot_bar()
        elif self.scatter_radio.isChecked():
            self.plot_scatter()
        elif self.heatmap_radio.isChecked():
            self.plot_heatmap()
        elif self.threeD_radio.isChecked():
            self.plot_3d()

        self.canvas.draw()

    def plot_histogram(self):
        ax = self.figure.add_subplot(111)
        ax.hist(self.prices, bins=20, color='blue', alpha=0.7)
        ax.set_title('Распределение цен продуктов (Гистограмма)')
        ax.set_xlabel('Цена')
        ax.set_ylabel('Количество')

    def plot_pie(self):
        ax = self.figure.add_subplot(111)
        ax.pie(self.cat_sizes, labels=self.categories, autopct='%1.1f%%',
               shadow=True, startangle=140)
        ax.set_title('Доля продаж по категориям')

    def plot_bar(self):
        ax = self.figure.add_subplot(111)
        ax.bar(self.months, self.sales, color='green')
        ax.set_title('Продажи по месяцам')
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма продаж')

    def plot_scatter(self):
        ax = self.figure.add_subplot(111)
        sc = ax.scatter(self.x_scatter, self.y_scatter, c=self.z_scatter, cmap='plasma')
        self.figure.colorbar(sc, ax=ax)
        ax.set_title('Диаграмма рассеяния')

    def plot_heatmap(self):
        ax = self.figure.add_subplot(111)
        cax = ax.matshow(self.data_matrix, cmap='coolwarm')
        self.figure.colorbar(cax)
        ax.set_title('Тепловая карта корреляций')

    def plot_3d(self):
        ax = self.figure.add_subplot(111, projection='3d')
        x = np.linspace(-6, 6, 30)
        y = np.linspace(-6, 6, 30)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x ** 2 + y ** 2))
        ax.plot_surface(x, y, z, cmap='viridis')
        ax.set_title('3D поверхность')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

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
    main_win.resize(1200, 800)
    main_win.show()
    sys.exit(app.exec_())
