import sqlite3
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Rectangle, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView

# Deteksi apakah berjalan di Android atau PC
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    Environment = autoclass('android.os.Environment')
    DOWNLOAD_DIR = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False
    DOWNLOAD_DIR = ""

# --------------------------
# SETUP DATABASE SQLITE
# --------------------------
def init_db():
    if IS_ANDROID:
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), "catatan_keuangan.db")
    else:
        db_path = "catatan_keuangan.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengeluaran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            kategori TEXT NOT NULL,
            nominal INTEGER NOT NULL,
            catatan TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengaturan (
            kunci TEXT PRIMARY KEY,
            nilai TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO pengaturan (kunci, nilai) VALUES ('anggaran', '2000000')")
    conn.commit()
    conn.close()

def get_db_connection():
    if IS_ANDROID:
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), "catatan_keuangan.db")
    else:
        db_path = "catatan_keuangan.db"
    return sqlite3.connect(db_path)

ICON_URLS = {
    'Makanan': 'https://cdn-icons-png.flaticon.com/512/3515/3515156.png',        
    'Transportasi': 'https://cdn-icons-png.flaticon.com/512/3174/3174834.png',    
    'Belanja': 'https://cdn-icons-png.flaticon.com/512/3081/3081559.png',         
    'Kesehatan': 'https://cdn-icons-png.flaticon.com/512/2966/2966327.png',       
    'Hiburan': 'https://cdn-icons-png.flaticon.com/512/3163/3163478.png',         
    'Lainnya': 'https://cdn-icons-png.flaticon.com/512/3143/3143498.png'          
}

def get_icon_kategori(kat):
    if not kat:
        return ICON_URLS['Lainnya']
    kat_clean = kat.strip().capitalize()
    return ICON_URLS.get(kat_clean, ICON_URLS['Lainnya'])

# --------------------------
# WIDGET IKON KUSTOM (VEKTOR)
# --------------------------
class NavIconBeranda(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*(self.parent.color_nav if self.parent else [0.7, 0.7, 0.7, 1]))
            cx, cy = self.center_x, self.center_y + 3
            Line(points=[cx - 10, cy - 2, cx, cy + 9, cx + 10, cy - 2], width=1.6, cap='round', joint='round')
            Line(rectangle=(cx - 8, cy - 9, 16, 11), width=1.6)
            Line(rectangle=(cx - 2.5, cy - 9, 5, 6), width=1.3)

class NavIconRiwayat(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*(self.parent.color_nav if self.parent else [0.7, 0.7, 0.7, 1]))
            cx, cy = self.center_x, self.center_y + 2
            Line(rounded_rectangle=(cx - 9, cy - 9, 18, 18, 4), width=1.6)
            Line(points=[cx, cy, cx, cy + 5], width=1.5, cap='round')
            Line(points=[cx, cy, cx + 4, cy], width=1.5, cap='round')

class NavIconGrafik(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*(self.parent.color_nav if self.parent else [0.7, 0.7, 0.7, 1]))
            cx, cy = self.center_x, self.center_y - 4
            Line(points=[cx - 10, cy - 6, cx - 10, cy + 12], width=1.5)
            Line(points=[cx - 10, cy - 6, cx + 10, cy - 6], width=1.5)
            Line(points=[cx - 7, cy - 2, cx - 1, cy + 4, cx + 3, cy + 1, cx + 8, cy + 9], width=1.8, cap='round', joint='round')

class NavIconAnggaran(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*(self.parent.color_nav if self.parent else [0.7, 0.7, 0.7, 1]))
            cx, cy = self.center_x, self.center_y + 2
            Line(rounded_rectangle=(cx - 10, cy - 8, 20, 14, 3), width=1.6)
            Line(points=[cx - 5, cy + 6, cx - 5, cy + 9, cx + 5, cy + 9, cx + 5, cy + 6], width=1.5, cap='round', joint='round')
            Rectangle(pos=(cx - 1.5, cy - 1), size=(3, 3))

class NavIconLainnya(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*(self.parent.color_nav if self.parent else [0.7, 0.7, 0.7, 1]))
            cx, cy = self.center_x, self.center_y + 2
            Rectangle(pos=(cx - 9, cy - 1.5), size=(3.5, 3.5))
            Rectangle(pos=(cx - 1.75, cy - 1.5), size=(3.5, 3.5))
            Rectangle(pos=(cx + 5.5, cy - 1.5), size=(3.5, 3.5))

class IconKalender(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.96, 0.45, 0.62, 1)
            cx, cy = self.center_x, self.center_y
            Line(rounded_rectangle=(cx - 8, cy - 9, 16, 16, 3), width=1.5)
            Line(points=[cx - 8, cy + 3, cx + 8, cy + 3], width=1.5)
            Line(points=[cx - 4, cy + 5, cx - 4, cy + 8], width=1.5, cap='round')
            Line(points=[cx + 4, cy + 5, cx + 4, cy + 8], width=1.5, cap='round')

class IconKategori(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.96, 0.45, 0.62, 1)
            cx, cy = self.center_x, self.center_y
            Line(rectangle=(cx - 8, cy - 7, 16, 14), width=1.5)
            Line(points=[cx - 5, cy + 2, cx + 5, cy + 2], width=1.5)
            Line(points=[cx - 5, cy - 2, cx + 2, cy - 2], width=1.5)

class IconCatatan(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.96, 0.45, 0.62, 1)
            cx, cy = self.center_x, self.center_y
            Line(points=[cx - 8, cy + 6, cx + 6, cy + 6], width=1.5, cap='round')
            Line(points=[cx - 8, cy, cx + 8, cy], width=1.5, cap='round')
            Line(points=[cx - 8, cy - 6, cx + 2, cy - 6], width=1.5, cap='round')

# --------------------------
# WIDGET CUSTOM LAINNYA
# --------------------------
class DonutChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_data(self, data):
        self.data = data
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if not self.data:
                Color(0.9, 0.9, 0.9, 1)
                Ellipse(pos=self.pos, size=self.size)
            else:
                start_angle = 0
                for color_rgba, pct in self.data:
                    end_angle = start_angle + (pct * 360)
                    Color(*color_rgba)
                    Ellipse(pos=self.pos, size=self.size, angle_start=start_angle, angle_end=end_angle)
                    start_angle = end_angle
            Color(1, 1, 1, 1)
            hole_w = self.width * 0.55
            hole_h = self.height * 0.55
            Ellipse(pos=(self.center_x - hole_w/2, self.center_y - hole_h/2), size=(hole_w, hole_h))

class BarChart7Days(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.daily_data = []
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_data(self, daily_data):
        self.daily_data = daily_data
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[14,])
            
            if not self.daily_data:
                return

            max_val = max([val for dt, val in self.daily_data]) or 1
            chart_x = self.x + 15
            chart_y = self.y + 35
            chart_w = self.width - 30
            chart_h = self.height - 55
            
            num_bars = len(self.daily_data)
            bar_total_w = chart_w / num_bars
            bar_w = bar_total_w * 0.55

            for i, (dt_str, val) in enumerate(self.daily_data):
                bx = chart_x + (i * bar_total_w) + (bar_total_w - bar_w) / 2
                bh = (val / max_val) * (chart_h - 15) if max_val > 0 else 2
                if bh < 4: bh = 4
                by = chart_y

                if val > 0:
                    Color(0.96, 0.45, 0.62, 1)
                else:
                    Color(0.92, 0.92, 0.92, 1)
                
                RoundedRectangle(pos=(bx, by), size=(bar_w, bh), radius=[bar_w/2, bar_w/2, 0, 0])

class LegendItemDetail(BoxLayout):
    def __init__(self, color_rgba, label_text, pct_text, val_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = "24dp"
        self.spacing = "10dp"

        dot = Widget(size_hint_x=None, width="14dp")
        with dot.canvas.before:
            Color(*color_rgba)
            self.ellipse = Ellipse(size=(12, 12))
        def update_ellipse(instance, val):
            self.ellipse.pos = (instance.center_x - 6, instance.center_y - 6)
        dot.bind(pos=update_ellipse, size=update_ellipse)

        lbl_name = Label(text=label_text, color=[0.3, 0.3, 0.3, 1], font_size="12sp", halign='left')
        lbl_name.bind(size=lbl_name.setter('text_size'))
        
        lbl_pct = Label(text=pct_text, color=[0.5, 0.5, 0.5, 1], font_size="12sp", halign='left')
        lbl_pct.bind(size=lbl_pct.setter('text_size'))

        lbl_val = Label(text=val_text, color=[0.2, 0.2, 0.2, 1], font_size="12sp", bold=True, halign='right')
        lbl_val.bind(size=lbl_val.setter('text_size'))

        self.add_widget(dot)
        self.add_widget(lbl_name)
        self.add_widget(lbl_pct)
        self.add_widget(lbl_val)

class AnggaranCategoryRow(BoxLayout):
    def __init__(self, kategori, nominal_str, max_nominal_str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = "55dp"
        self.padding = [15, 8, 15, 8]
        self.spacing = "10dp"

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12,])
        self.bind(pos=self._update_rect, size=self._update_rect)

        icon_box = BoxLayout(size_hint=(None, None), size=("36dp", "36dp"), pos_hint={"center_y": 0.5})
        with icon_box.canvas.before:
            Color(0.99, 0.88, 0.92, 1)
            RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[18,])
        
        img_url = get_icon_kategori(kategori)
        img_icon = AsyncImage(source=img_url, size_hint=(0.6, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5}, color=[0.96, 0.45, 0.62, 1])
        icon_box.add_widget(img_icon)
        self.add_widget(icon_box)

        lbl_kat = Label(text=kategori, color=[0.2, 0.2, 0.2, 1], font_size="13sp", bold=True, halign='left', pos_hint={"center_y": 0.5})
        lbl_kat.bind(size=lbl_kat.setter('text_size'))
        self.add_widget(lbl_kat)

        right_box = BoxLayout(orientation='vertical', size_hint=(None, None), size=("130dp", "40dp"), pos_hint={"center_y": 0.5}, spacing="2dp")
        lbl_nom = Label(text=nominal_str, color=[0.9, 0.3, 0.4, 1], font_size="13sp", bold=True, halign='right')
        lbl_nom.bind(size=lbl_nom.setter('text_size'))
        lbl_max = Label(text=max_nominal_str, color=[0.6, 0.6, 0.6, 1], font_size="10sp", halign='right')
        lbl_max.bind(size=lbl_max.setter('text_size'))
        right_box.add_widget(lbl_nom)
        right_box.add_widget(lbl_max)
        self.add_widget(right_box)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ItemCard(ButtonBehavior, BoxLayout):
    def __init__(self, main_text, sub_text, nominal_text, kategori="", item_id=None, app_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [15, 12, 15, 12]
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = "70dp"
        self.item_id = item_id
        self.app_instance = app_instance
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14,])
        self.bind(pos=self._update_rect, size=self._update_rect)

        icon_box = BoxLayout(size_hint=(None, None), size=("45dp", "45dp"), pos_hint={"center_y": 0.5})
        with icon_box.canvas.before:
            Color(0.99, 0.88, 0.92, 1)
            RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[22.5,])
        
        img_url = get_icon_kategori(kategori)
        img_icon = AsyncImage(source=img_url, size_hint=(0.6, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5}, color=[0.96, 0.45, 0.62, 1])
        icon_box.add_widget(img_icon)
        self.add_widget(icon_box)

        text_box = BoxLayout(orientation='vertical', spacing="3dp", pos_hint={"center_y": 0.5})
        lbl_main = Label(text=main_text, color=[0.15, 0.15, 0.15, 1], font_size='14sp', bold=True, halign='left')
        lbl_main.bind(size=lbl_main.setter('text_size'))
        lbl_sub = Label(text=sub_text, color=[0.55, 0.55, 0.55, 1], font_size='11sp', halign='left')
        lbl_sub.bind(size=lbl_sub.setter('text_size'))
        text_box.add_widget(lbl_main)
        text_box.add_widget(lbl_sub)
        self.add_widget(text_box)

        right_box = BoxLayout(orientation='horizontal', size_hint=(None, None), size=("120dp", "45dp"), pos_hint={"center_y": 0.5}, spacing="8dp")
        lbl_nominal = Label(text=nominal_text, color=[0.9, 0.3, 0.4, 1], font_size='13sp', bold=True, halign='right')
        lbl_nominal.bind(size=lbl_nominal.setter('text_size'))
        right_box.add_widget(lbl_nominal)
        self.add_widget(right_box)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_release(self):
        if self.app_instance and self.item_id:
            self.app_instance.buka_screen_edit(self.item_id)

# --------------------------
# LAYOUT UTAMA (KIVY LANGUAGE)
# --------------------------
KV = '''
<SpinnerOption>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: [0.35, 0.12, 0.22, 1]
    font_size: "13sp"
    bold: True
    height: "44dp"
    size_hint_y: None
    canvas.before:
        Color:
            rgba: [0.98, 0.86, 0.90, 1] if self.state == 'normal' else [0.92, 0.75, 0.82, 1]
        RoundedRectangle:
            pos: self.x + 2, self.y + 2
            size: self.width - 4, self.height - 4
            radius: [8,]

<NavButton@ButtonBehavior+BoxLayout>:
    orientation: 'vertical'
    padding: ["2dp", "4dp", "2dp", "4dp"]
    spacing: "2dp"
    text: ''
    color_nav: [0.7, 0.7, 0.7, 1]
    
    Label:
        text: root.text
        color: root.color_nav
        font_size: '10sp'
        bold: True
        size_hint_y: 0.35
        halign: 'center'
        valign: 'middle'

<FormInputBox@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: "50dp"
    padding: ["15dp", "5dp", "15dp", "5dp"]
    spacing: "10dp"
    canvas.before:
        Color:
            rgba: 0.96, 0.96, 0.96, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]

<FilterChip@Button>:
    text: ''
    size_hint: None, None
    size: self.texture_size[0] + 24, "34dp"
    background_normal: ''
    background_color: 0, 0, 0, 0
    font_size: "12sp"
    bold: True
    color: [0.96, 0.45, 0.62, 1] if self.state == 'normal' else [1, 1, 1, 1]
    canvas.before:
        Color:
            rgba: [1, 1, 1, 1] if self.state == 'normal' else [0.96, 0.45, 0.62, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [17,]
        Color:
            rgba: [0.96, 0.45, 0.62, 0.4] if self.state == 'normal' else [0.96, 0.45, 0.62, 1]
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 17)
            width: 1

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.99, 0.96, 0.97, 1
        Rectangle:
            pos: self.pos
            size: self.size

    ScreenManager:
        id: sm

        # ==========================================
        # 1. HALAMAN BERANDA
        # ==========================================
        Screen:
            name: 'beranda'
            ScrollView:
                BoxLayout:
                    orientation: 'vertical'
                    padding: "20dp"
                    spacing: "15dp"
                    size_hint_y: None
                    height: self.minimum_height

                    RelativeLayout:
                        size_hint_y: None
                        height: "55dp"
                        BoxLayout:
                            orientation: 'vertical'
                            pos_hint: {'x': 0, 'center_y': 0.5}
                            Label:
                                text: "Beranda"
                                color: [0.1, 0.1, 0.1, 1]
                                font_size: "26sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None
                            Label:
                                text: "Halo! Semangat hari ini :)"
                                color: [0.96, 0.45, 0.62, 1]
                                font_size: "12sp"
                                halign: 'left'
                                text_size: self.width, None

                    RelativeLayout:
                        size_hint_y: None
                        height: "155dp"
                        canvas.before:
                            Color:
                                rgba: 0.96, 0.45, 0.62, 1
                            RoundedRectangle:
                                pos: 0, 0
                                size: self.size
                                radius: [18,]
                        Label:
                            text: "Total Pengeluaran Bulan Ini"
                            color: 1, 1, 1, 0.9
                            font_size: "12sp"
                            pos_hint: {'x': 0.08, 'top': 0.85}
                            size_hint: None, None
                            size: self.texture_size
                        Label:
                            id: lbl_total_beranda
                            text: "Rp 0"
                            color: 1, 1, 1, 1
                            font_size: "32sp"
                            bold: True
                            pos_hint: {'x': 0.08, 'center_y': 0.5}
                            size_hint: None, None
                            size: self.texture_size
                        Label:
                            id: lbl_dari_anggaran
                            text: "Dari anggaran Rp 0"
                            color: 1, 1, 1, 0.7
                            font_size: "11sp"
                            pos_hint: {'x': 0.08, 'y': 0.25}
                            size_hint: None, None
                            size: self.texture_size
                        Label:
                            id: lbl_persen_anggaran
                            text: "0%"
                            color: 1, 1, 1, 0.8
                            font_size: "11sp"
                            bold: True
                            pos_hint: {'right': 0.92, 'y': 0.25}
                            size_hint: None, None
                            size: self.texture_size
                        
                        BoxLayout:
                            pos_hint: {'x': 0.08, 'y': 0.12}
                            size_hint: 0.84, None
                            height: "5dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 0.3
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [2.5,]
                            BoxLayout:
                                id: bar_persen_anggaran
                                size_hint_x: 0.001
                                canvas.before:
                                    Color:
                                        rgba: 1, 1, 1, 1
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [2.5,]
                            Widget:
                                id: bar_persen_sisa
                                size_hint_x: 0.999

                    GridLayout:
                        cols: 2
                        spacing: "15dp"
                        size_hint_y: None
                        height: "90dp"
                        BoxLayout:
                            orientation: 'vertical'
                            padding: ["15dp", "15dp", "15dp", "15dp"]
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [15,]
                            Label:
                                text: "Pengeluaran Hari Ini"
                                color: [0.5, 0.5, 0.5, 1]
                                font_size: "11sp"
                                halign: 'left'
                                text_size: self.width, None
                            Label:
                                id: lbl_hari_ini
                                text: "Rp 0"
                                color: [0.1, 0.1, 0.1, 1]
                                font_size: "16sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None
                            Label:
                                id: lbl_jml_transaksi
                                text: "0 transaksi"
                                color: [0.6, 0.6, 0.6, 1]
                                font_size: "10sp"
                                halign: 'left'
                                text_size: self.width, None

                        BoxLayout:
                            orientation: 'vertical'
                            padding: ["15dp", "15dp", "15dp", "15dp"]
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [15,]
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_y: None
                                height: "20dp"
                                Label:
                                    text: "Sisa Anggaran"
                                    color: [0.5, 0.5, 0.5, 1]
                                    font_size: "11sp"
                                    halign: 'left'
                                    text_size: self.width, None
                                Button:
                                    text: "Edit"
                                    color: [0.5, 0.5, 0.5, 1]
                                    font_size: "10sp"
                                    size_hint_x: None
                                    width: "30dp"
                                    background_normal: ''
                                    background_color: 0,0,0,0
                                    on_release: app.buka_dialog_anggaran()
                            Widget:
                                size_hint_y: None
                                height: "5dp"
                            Label:
                                id: lbl_sisa_anggaran
                                text: "Rp 0"
                                color: [0.15, 0.6, 0.4, 1]
                                font_size: "16sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None

                    BoxLayout:
                        orientation: 'vertical'
                        padding: ["15dp", "15dp", "15dp", "15dp"]
                        spacing: "15dp"
                        size_hint_y: None
                        height: "190dp"
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [15,]
                        Label:
                            text: "Kategori Pengeluaran"
                            color: [0.1, 0.1, 0.1, 1]
                            font_size: "14sp"
                            bold: True
                            size_hint_y: None
                            height: "20dp"
                            halign: 'left'
                            text_size: self.width, None
                        BoxLayout:
                            spacing: "15dp"
                            RelativeLayout:
                                size_hint_x: 0.4
                                DonutChart:
                                    id: donut_chart_beranda
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    size_hint: None, None
                                    size: "95dp", "95dp"
                            GridLayout:
                                id: layout_legend_beranda
                                cols: 1
                                size_hint_x: 0.6
                                spacing: "6dp"

                    Button:
                        text: "+ Tambah Pengeluaran"
                        size_hint_y: None
                        height: "52dp"
                        background_normal: ''
                        background_color: 0,0,0,0
                        color: 1, 1, 1, 1
                        font_size: "15sp"
                        bold: True
                        on_release: app.buka_screen_tambah()
                        canvas.before:
                            Color:
                                rgba: 0.96, 0.45, 0.62, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [26,] 

        # ==========================================
        # 2. HALAMAN TAMBAH PENGELUARAN
        # ==========================================
        Screen:
            name: 'form'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'beranda'
                    Label:
                        text: "Tambah Pengeluaran"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"
                        padding: [0, 5, 0, 10]

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Tanggal"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconKalender:
                                    size_hint_x: None
                                    width: "20dp"
                                TextInput:
                                    id: form_tanggal
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
                        
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Kategori"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconKategori:
                                    size_hint_x: None
                                    width: "20dp"
                                Spinner:
                                    id: form_kategori
                                    text: "Makanan"
                                    values: ('Makanan', 'Transportasi', 'Belanja', 'Kesehatan', 'Hiburan', 'Lainnya')
                                    background_normal: ''
                                    background_color: [0,0,0,0]
                                    color: [0.1, 0.1, 0.1, 1]
                                    font_size: "14sp"
                                    text_size: self.width, None
                                    halign: 'left'
                                    valign: 'middle'
                                    option_cls: 'SpinnerOption'
                                    option_height: "44dp"

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Nominal"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                Label:
                                    text: "Rp"
                                    color: [0.96, 0.45, 0.62, 1]
                                    font_size: "15sp"
                                    bold: True
                                    size_hint_x: None
                                    width: "30dp"
                                TextInput:
                                    id: form_nominal
                                    hint_text: "25000"
                                    input_filter: "int"
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Keterangan (opsional)"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconCatatan:
                                    size_hint_x: None
                                    width: "20dp"
                                TextInput:
                                    id: form_catatan
                                    hint_text: "Contoh: Beli nasi ayam"
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
                        
                        Widget:
                            size_hint_y: None
                            height: "10dp"

                        AnchorLayout:
                            anchor_x: 'center'
                            size_hint_y: None
                            height: "55dp"
                            Button:
                                text: "Simpan"
                                size_hint: None, None
                                size: "220dp", "48dp"
                                background_normal: ''
                                background_color: 0,0,0,0
                                color: 1, 1, 1, 1
                                font_size: "15sp"
                                bold: True
                                on_release: app.simpan_transaksi()
                                canvas.before:
                                    Color:
                                        rgba: 0.96, 0.45, 0.62, 1
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [24,]

        # ==========================================
        # 3. RIWAYAT
        # ==========================================
        Screen:
            name: 'riwayat'
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'beranda'
                    Label:
                        text: "Riwayat Transaksi"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: "46dp"
                    padding: ["15dp", "5dp", "15dp", "5dp"]
                    spacing: "10dp"
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [23,]
                    Label:
                        text: "O"
                        color: [0.7, 0.7, 0.7, 1]
                        size_hint_x: None
                        width: "18dp"
                        font_size: "14sp"
                    TextInput:
                        id: input_cari
                        hint_text: "Cari transaksi..."
                        multiline: False
                        background_color: [0,0,0,0]
                        foreground_color: [0.1, 0.1, 0.1, 1]
                        cursor_color: [0.96, 0.45, 0.62, 1]
                        font_size: "13sp"
                        padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
                        on_text: app.filter_riwayat(self.text)

                ScrollView:
                    size_hint_y: None
                    height: "40dp"
                    do_scroll_y: False
                    do_scroll_x: True
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: None
                        width: self.minimum_width
                        spacing: "8dp"
                        padding: [2, 2, 2, 2]
                        FilterChip:
                            text: "Semua"
                            on_release: app.filter_kategori_riwayat("Semua")
                        FilterChip:
                            text: "Makanan"
                            on_release: app.filter_kategori_riwayat("Makanan")
                        FilterChip:
                            text: "Transportasi"
                            on_release: app.filter_kategori_riwayat("Transportasi")
                        FilterChip:
                            text: "Belanja"
                            on_release: app.filter_kategori_riwayat("Belanja")
                        FilterChip:
                            text: "Kesehatan"
                            on_release: app.filter_kategori_riwayat("Kesehatan")
                        FilterChip:
                            text: "Hiburan"
                            on_release: app.filter_kategori_riwayat("Hiburan")
                        FilterChip:
                            text: "Lainnya"
                            on_release: app.filter_kategori_riwayat("Lainnya")

                ScrollView:
                    BoxLayout:
                        id: list_riwayat_lengkap
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "10dp"

        # ==========================================
        # 4. HALAMAN EDIT TRANSAKSI
        # ==========================================
        Screen:
            name: 'edit_transaksi'
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'riwayat'
                    Label:
                        text: "Edit Transaksi"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"
                        padding: [0, 5, 0, 10]

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Tanggal"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconKalender:
                                    size_hint_x: None
                                    width: "20dp"
                                TextInput:
                                    id: edit_tanggal
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
                        
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Kategori"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconKategori:
                                    size_hint_x: None
                                    width: "20dp"
                                Spinner:
                                    id: edit_kategori
                                    text: "Makanan"
                                    values: ('Makanan', 'Transportasi', 'Belanja', 'Kesehatan', 'Hiburan', 'Lainnya')
                                    background_normal: ''
                                    background_color: [0,0,0,0]
                                    color: [0.1, 0.1, 0.1, 1]
                                    font_size: "14sp"
                                    text_size: self.width, None
                                    halign: 'left'
                                    valign: 'middle'
                                    option_cls: 'SpinnerOption'
                                    option_height: "44dp"

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Nominal"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                Label:
                                    text: "Rp"
                                    color: [0.96, 0.45, 0.62, 1]
                                    font_size: "15sp"
                                    bold: True
                                    size_hint_x: None
                                    width: "30dp"
                                TextInput:
                                    id: edit_nominal
                                    input_filter: "int"
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: "75dp"
                            spacing: "6dp"
                            Label:
                                text: "Keterangan (opsional)"
                                color: [0.3, 0.3, 0.3, 1]
                                font_size: "13sp"
                                halign: 'left'
                                text_size: self.width, None
                            FormInputBox:
                                IconCatatan:
                                    size_hint_x: None
                                    width: "20dp"
                                TextInput:
                                    id: edit_catatan
                                    background_color: [0,0,0,0]
                                    foreground_color: [0.1, 0.1, 0.1, 1]
                                    cursor_color: [0.96, 0.45, 0.62, 1]
                                    font_size: "14sp"
                                    padding_y: [self.height / 2.0 - (self.line_height / 2.0), 0]
                        
                        Widget:
                            size_hint_y: None
                            height: "10dp"

                        AnchorLayout:
                            anchor_x: 'center'
                            size_hint_y: None
                            height: "55dp"
                            Button:
                                text: "Simpan Perubahan"
                                size_hint: None, None
                                size: "220dp", "48dp"
                                background_normal: ''
                                background_color: 0,0,0,0
                                color: 1, 1, 1, 1
                                font_size: "15sp"
                                bold: True
                                on_release: app.simpan_perubahan_transaksi()
                                canvas.before:
                                    Color:
                                        rgba: 0.96, 0.45, 0.62, 1
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [24,]

                        AnchorLayout:
                            anchor_x: 'center'
                            size_hint_y: None
                            height: "55dp"
                            Button:
                                text: "Hapus Transaksi"
                                size_hint: None, None
                                size: "220dp", "48dp"
                                background_normal: ''
                                background_color: 0,0,0,0
                                color: [0.9, 0.3, 0.3, 1]
                                font_size: "15sp"
                                bold: True
                                on_release: app.hapus_transaksi_sedang_diedit()
                                canvas.before:
                                    Color:
                                        rgba: [0.95, 0.85, 0.85, 1]
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [24,]

        # ==========================================
        # 5. GRAFIK
        # ==========================================
        Screen:
            name: 'grafik'
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'beranda'
                    Label:
                        text: "Grafik"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: "42dp"
                    padding: [4, 4, 4, 4]
                    spacing: "5dp"
                    canvas.before:
                        Color:
                            rgba: 0.93, 0.93, 0.93, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [21,]
                    Button:
                        id: btn_tab_kategori
                        text: "Kategori"
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.1, 0.1, 0.1, 1]
                        bold: True
                        font_size: "13sp"
                        on_release: app.pilih_tab_grafik('kategori')
                        canvas.before:
                            Color:
                                rgba: [1, 1, 1, 1] if self.color[0] == 0.1 else [0,0,0,0]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]
                    Button:
                        id: btn_tab_bulanan
                        text: "Bulanan"
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.6, 0.6, 0.6, 1]
                        bold: True
                        font_size: "13sp"
                        on_release: app.pilih_tab_grafik('bulanan')
                        canvas.before:
                            Color:
                                rgba: [1, 1, 1, 1] if self.color[0] == 0.1 else [0,0,0,0]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"
                        padding: [0, 0, 0, 10]

                        BoxLayout:
                            orientation: 'vertical'
                            padding: "18dp"
                            spacing: "15dp"
                            size_hint_y: None
                            height: "330dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14,]
                            
                            Label:
                                id: lbl_judul_kartu_grafik
                                text: "Pengeluaran per Kategori"
                                color: [0.15, 0.15, 0.15, 1]
                                font_size: "15sp"
                                bold: True
                                size_hint_y: None
                                height: "20dp"
                                halign: 'left'
                                text_size: self.width, None

                            RelativeLayout:
                                size_hint_y: None
                                height: "130dp"
                                DonutChart:
                                    id: donut_chart_halaman
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    size_hint: None, None
                                    size: "120dp", "120dp"
                                Label:
                                    id: lbl_total_donut_grafik
                                    text: "Total\\nRp 0"
                                    color: [0.2, 0.2, 0.2, 1]
                                    font_size: "11sp"
                                    bold: True
                                    halign: 'center'
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                            GridLayout:
                                id: layout_detail_kategori_grafik
                                cols: 1
                                size_hint_y: None
                                height: "110dp"
                                spacing: "4dp"

                        BoxLayout:
                            orientation: 'vertical'
                            padding: "18dp"
                            spacing: "12dp"
                            size_hint_y: None
                            height: "210dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14,]

                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_y: None
                                height: "20dp"
                                Label:
                                    text: "Tren Pengeluaran 7 Hari Terakhir"
                                    color: [0.15, 0.15, 0.15, 1]
                                    font_size: "15sp"
                                    bold: True
                                    halign: 'left'
                                    text_size: self.width, None

                            RelativeLayout:
                                size_hint_y: None
                                height: "120dp"
                                BarChart7Days:
                                    id: barchart_7days
                                    size_hint: 1, 1
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                            BoxLayout:
                                id: layout_xaxis_dates
                                orientation: 'horizontal'
                                size_hint_y: None
                                height: "15dp"

        # ==========================================
        # 6. ANGGARAN
        # ==========================================
        Screen:
            name: 'anggaran'
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'beranda'
                    Label:
                        text: "Anggaran"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"
                        padding: [0, 0, 0, 10]

                        RelativeLayout:
                            size_hint_y: None
                            height: "140dp"
                            canvas.before:
                                Color:
                                    rgba: 0.96, 0.45, 0.62, 1
                                RoundedRectangle:
                                    pos: 0, 0
                                    size: self.size
                                    radius: [16,]
                            Label:
                                text: "Anggaran Bulanan"
                                color: 1, 1, 1, 0.9
                                font_size: "13sp"
                                pos_hint: {'x': 0.08, 'top': 0.82}
                                size_hint: None, None
                                size: self.texture_size
                            Label:
                                id: lbl_anggaran_utama_page
                                text: "Rp 2.000.000"
                                color: 1, 1, 1, 1
                                font_size: "28sp"
                                bold: True
                                pos_hint: {'x': 0.08, 'center_y': 0.52}
                                size_hint: None, None
                                size: self.texture_size
                            Label:
                                id: lbl_anggaran_persen_page
                                text: "65%"
                                color: 1, 1, 1, 0.9
                                font_size: "12sp"
                                bold: True
                                pos_hint: {'right': 0.92, 'y': 0.28}
                                size_hint: None, None
                                size: self.texture_size
                            
                            BoxLayout:
                                pos_hint: {'x': 0.08, 'y': 0.18}
                                size_hint: 0.84, None
                                height: "6dp"
                                canvas.before:
                                    Color:
                                        rgba: 1, 1, 1, 0.3
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [3,]
                                BoxLayout:
                                    id: bar_anggaran_page_fill
                                    size_hint_x: 0.65
                                    canvas.before:
                                        Color:
                                            rgba: 1, 1, 1, 1
                                        RoundedRectangle:
                                            pos: self.pos
                                            size: self.size
                                            radius: [3,]
                                Widget:
                                    id: bar_anggaran_page_empty
                                    size_hint_x: 0.35

                        Label:
                            text: "Rincian"
                            color: [0.15, 0.15, 0.15, 1]
                            font_size: "15sp"
                            bold: True
                            size_hint_y: None
                            height: "25dp"
                            halign: 'left'
                            text_size: self.width, None

                        BoxLayout:
                            id: layout_rincian_anggaran_list
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: "10dp"

                        Widget:
                            size_hint_y: None
                            height: "10dp"

                        AnchorLayout:
                            anchor_x: 'center'
                            size_hint_y: None
                            height: "55dp"
                            Button:
                                text: "Atur Anggaran"
                                size_hint: None, None
                                size: "220dp", "48dp"
                                background_normal: ''
                                background_color: 0,0,0,0
                                color: 1, 1, 1, 1
                                font_size: "15sp"
                                bold: True
                                on_release: app.buka_dialog_anggaran()
                                canvas.before:
                                    Color:
                                        rgba: 0.96, 0.45, 0.62, 1
                                    RoundedRectangle:
                                        pos: self.pos
                                        size: self.size
                                        radius: [24,]

        # ==========================================
        # 7. HALAMAN PENGATURAN / LAINNYA
        # ==========================================
        Screen:
            name: 'lainnya'
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'beranda'
                    Label:
                        text: "Pengaturan"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "12dp"
                        padding: [0, 5, 0, 10]

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: "60dp"
                            padding: [15, 10, 15, 10]
                            spacing: "15dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14,]
                            Label:
                                text: "📊"
                                size_hint_x: None
                                width: "26dp"
                                font_size: "16sp"
                            Label:
                                text: "Laporan Keuangan"
                                color: [0.2, 0.2, 0.2, 1]
                                font_size: "14sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None
                                pos_hint: {'center_y': 0.5}
                            Button:
                                text: "Lihat"
                                size_hint: None, None
                                size: "80dp", "36dp"
                                pos_hint: {'center_y': 0.5}
                                background_normal: ''
                                background_color: [0.96, 0.45, 0.62, 1]
                                color: [1, 1, 1, 1]
                                font_size: "12sp"
                                bold: True
                                on_release: app.buka_laporan_bulanan()

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: "60dp"
                            padding: [15, 10, 15, 10]
                            spacing: "15dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14,]
                            Label:
                                text: "ℹ️"
                                size_hint_x: None
                                width: "26dp"
                                font_size: "16sp"
                            Label:
                                text: "Tentang CatatUang App"
                                color: [0.2, 0.2, 0.2, 1]
                                font_size: "14sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None
                                pos_hint: {'center_y': 0.5}

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: "60dp"
                            padding: [15, 10, 15, 10]
                            spacing: "15dp"
                            canvas.before:
                                Color:
                                    rgba: 1, 1, 1, 1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [14,]
                            Label:
                                text: "⚠️"
                                size_hint_x: None
                                width: "26dp"
                                font_size: "16sp"
                            Label:
                                text: "Reset Semua Data"
                                color: [0.9, 0.3, 0.3, 1]
                                font_size: "14sp"
                                bold: True
                                halign: 'left'
                                text_size: self.width, None
                                pos_hint: {'center_y': 0.5}
                            Button:
                                text: "Reset"
                                size_hint_y: None
                                height: "36dp"
                                size_hint_x: None
                                width: "80dp"
                                pos_hint: {'center_y': 0.5}
                                background_normal: ''
                                background_color: [0.95, 0.85, 0.85, 1]
                                color: [0.9, 0.3, 0.3, 1]
                                font_size: "12sp"
                                bold: True
                                on_release: app.reset_data()

        # ==========================================
        # 8. HALAMAN LAPORAN (DENGAN PERIODE & PILIH TANGGAL HARIAN)
        # ==========================================
        Screen:
            name: 'laporan_bulanan'
            BoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"

                RelativeLayout:
                    size_hint_y: None
                    height: "50dp"
                    Button:
                        text: "<"
                        font_size: "18sp"
                        bold: True
                        color: [0.1, 0.1, 0.1, 1]
                        size_hint: None, None
                        size: "30dp", "30dp"
                        pos_hint: {'x': 0, 'center_y': 0.5}
                        background_normal: ''
                        background_color: 0,0,0,0
                        on_release: sm.current = 'lainnya'
                    Label:
                        text: "Laporan Keuangan"
                        color: [0.1, 0.1, 0.1, 1]
                        font_size: "18sp"
                        bold: True
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                # Pilihan Periode Laporan
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: "42dp"
                    padding: [4, 4, 4, 4]
                    spacing: "5dp"
                    canvas.before:
                        Color:
                            rgba: 0.93, 0.93, 0.93, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [21,]
                    Button:
                        id: btn_lap_harian
                        text: "Harian"
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.6, 0.6, 0.6, 1]
                        bold: True
                        font_size: "13sp"
                        on_release: app.pilih_periode_laporan('harian')
                        canvas.before:
                            Color:
                                rgba: [1, 1, 1, 1] if self.color[0] == 0.1 else [0,0,0,0]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]
                    Button:
                        id: btn_lap_bulanan
                        text: "Bulanan"
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.1, 0.1, 0.1, 1]
                        bold: True
                        font_size: "13sp"
                        on_release: app.pilih_periode_laporan('bulanan')
                        canvas.before:
                            Color:
                                rgba: [1, 1, 1, 1] if self.color[0] == 0.1 else [0,0,0,0]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]
                    Button:
                        id: btn_lap_tahunan
                        text: "Tahunan"
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.6, 0.6, 0.6, 1]
                        bold: True
                        font_size: "13sp"
                        on_release: app.pilih_periode_laporan('tahunan')
                        canvas.before:
                            Color:
                                rgba: [1, 1, 1, 1] if self.color[0] == 0.1 else [0,0,0,0]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [18,]

                # Panel Pilih Tanggal Harian (Pink Kalem / Agak Putih)
                BoxLayout:
                    id: layout_pilih_tanggal_harian
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: "0dp"
                    opacity: 0
                    spacing: "8dp"
                    Spinner:
                        id: spin_hari
                        text: "01"
                        values: tuple(str(i).zfill(2) for i in range(1, 32))
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.35, 0.12, 0.22, 1]
                        font_size: "13sp"
                        bold: True
                        option_cls: 'SpinnerOption'
                        option_height: "44dp"
                        on_text: app.ubah_tanggal_harian(self.text, 'hari')
                        canvas.before:
                            Color:
                                rgba: [0.98, 0.86, 0.90, 1]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [10,]
                    Spinner:
                        id: spin_bulan_harian
                        text: "Januari"
                        values: ('Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember')
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.35, 0.12, 0.22, 1]
                        font_size: "13sp"
                        bold: True
                        option_cls: 'SpinnerOption'
                        option_height: "44dp"
                        on_text: app.ubah_tanggal_harian(self.text, 'bulan')
                        canvas.before:
                            Color:
                                rgba: [0.98, 0.86, 0.90, 1]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [10,]
                    Spinner:
                        id: spin_tahun_harian
                        text: "2026"
                        values: tuple(str(y) for y in range(2024, 2051))
                        background_normal: ''
                        background_color: [0,0,0,0]
                        color: [0.35, 0.12, 0.22, 1]
                        font_size: "13sp"
                        bold: True
                        option_cls: 'SpinnerOption'
                        option_height: "44dp"
                        on_text: app.ubah_tanggal_harian(self.text, 'tahun')
                        canvas.before:
                            Color:
                                rgba: [0.98, 0.86, 0.90, 1]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [10,]

                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"
                        padding: [0, 5, 0, 10]

                        RelativeLayout:
                            size_hint_y: None
                            height: "150dp"
                            canvas.before:
                                Color:
                                    rgba: 0.96, 0.45, 0.62, 1
                                RoundedRectangle:
                                    pos: 0, 0
                                    size: self.size
                                    radius: [18,]
                            Label:
                                id: lbl_lap_judul_total
                                text: "Total Pengeluaran Bulan Ini"
                                color: 1, 1, 1, 0.9
                                font_size: "12sp"
                                pos_hint: {'x': 0.08, 'top': 0.82}
                                size_hint: None, None
                                size: self.texture_size
                            Label:
                                id: lbl_lap_total_nominal
                                text: "Rp 0"
                                color: 1, 1, 1, 1
                                font_size: "28sp"
                                bold: True
                                pos_hint: {'x': 0.08, 'center_y': 0.52}
                                size_hint: None, None
                                size: self.texture_size
                            Label:
                                id: lbl_lap_info_tambahan
                                text: "Rata-rata harian: Rp 0"
                                color: 1, 1, 1, 0.8
                                font_size: "12sp"
                                pos_hint: {'x': 0.08, 'y': 0.18}
                                size_hint: None, None
                                size: self.texture_size

                        Label:
                            id: lbl_lap_judul_rincian
                            text: "Rincian Kategori Bulan Ini"
                            color: [0.15, 0.15, 0.15, 1]
                            font_size: "15sp"
                            bold: True
                            size_hint_y: None
                            height: "25dp"
                            halign: 'left'
                            text_size: self.width, None

                        BoxLayout:
                            id: layout_lap_rincian_kategori
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: "10dp"

    # ==========================================
    # MENU BAWAH
    # ==========================================
    BoxLayout:
        size_hint_y: None
        height: "65dp"
        padding: ["5dp", "4dp", "5dp", "4dp"]
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        NavButton:
            text: "Beranda"
            color_nav: [0.96, 0.45, 0.62, 1] if sm.current == 'beranda' else [0.7, 0.7, 0.7, 1]
            on_release: sm.current = 'beranda'
            NavIconBeranda:
                size_hint_y: 0.65
        
        NavButton:
            text: "Riwayat"
            color_nav: [0.96, 0.45, 0.62, 1] if sm.current == 'riwayat' else [0.7, 0.7, 0.7, 1]
            on_release: sm.current = 'riwayat'
            NavIconRiwayat:
                size_hint_y: 0.65
        
        NavButton:
            text: "Grafik"
            color_nav: [0.96, 0.45, 0.62, 1] if sm.current == 'grafik' else [0.7, 0.7, 0.7, 1]
            on_release: sm.current = 'grafik'
            NavIconGrafik:
                size_hint_y: 0.65
        
        NavButton:
            text: "Anggaran"
            color_nav: [0.96, 0.45, 0.62, 1] if sm.current == 'anggaran' else [0.7, 0.7, 0.7, 1]
            on_release: sm.current = 'anggaran'
            NavIconAnggaran:
                size_hint_y: 0.65
        
        NavButton:
            text: "Lainnya"
            color_nav: [0.96, 0.45, 0.62, 1] if sm.current == 'lainnya' else [0.7, 0.7, 0.7, 1]
            on_release: sm.current = 'lainnya'
            NavIconLainnya:
                size_hint_y: 0.65
'''

class CatatUangApp(App):
    def build(self):
        init_db()
        self.kategori_filter_aktif = "Semua"
        self.tab_grafik_aktif = "kategori"
        self.periode_laporan_aktif = "bulanan"
        
        now = datetime.now()
        self.pilih_hari = now.strftime("%d")
        self.pilih_bulan_angka = now.strftime("%m")
        self.pilih_tahun = now.strftime("%Y")
        
        return Builder.load_string(KV)

    def on_start(self):
        self.muat_data()
        if 'spin_hari' in self.root.ids:
            self.root.ids.spin_hari.text = self.pilih_hari
        nama_bln_indo_rev = {"01": "Januari", "02": "Februari", "03": "Maret", "04": "April", "05": "Mei", "06": "Juni", 
                             "07": "Juli", "08": "Agustus", "09": "September", "10": "Oktober", "11": "November", "12": "Desember"}
        if 'spin_bulan_harian' in self.root.ids:
            self.root.ids.spin_bulan_harian.text = nama_bln_indo_rev.get(self.pilih_bulan_angka, "Januari")
        if 'spin_tahun_harian' in self.root.ids:
            # Memperbarui range tahun dari 2024 sampai 2050
            self.root.ids.spin_tahun_harian.values = tuple(str(y) for y in range(2024, 2051))
            self.root.ids.spin_tahun_harian.text = self.pilih_tahun

    def pilih_tab_grafik(self, tab):
        self.tab_grafik_aktif = tab
        if 'btn_tab_kategori' in self.root.ids and 'btn_tab_bulanan' in self.root.ids:
            if tab == 'kategori':
                self.root.ids.btn_tab_kategori.color = [0.1, 0.1, 0.1, 1]
                self.root.ids.btn_tab_bulanan.color = [0.6, 0.6, 0.6, 1]
                if 'lbl_judul_kartu_grafik' in self.root.ids:
                    self.root.ids.lbl_judul_kartu_grafik.text = "Pengeluaran per Kategori"
            else:
                self.root.ids.btn_tab_kategori.color = [0.6, 0.6, 0.6, 1]
                self.root.ids.btn_tab_bulanan.color = [0.1, 0.1, 0.1, 1]
                if 'lbl_judul_kartu_grafik' in self.root.ids:
                    self.root.ids.lbl_judul_kartu_grafik.text = "Pengeluaran per Bulan"
        self.muat_data()

    def muat_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT nilai FROM pengaturan WHERE kunci = 'anggaran'")
        anggaran_val = int(cursor.fetchone()[0])
        anggaran_str = f"Rp {anggaran_val:,}".replace(",", ".")
        
        if 'lbl_anggaran_display' in self.root.ids:
            self.root.ids.lbl_anggaran_display.text = anggaran_str
        if 'lbl_anggaran_utama_page' in self.root.ids:
            self.root.ids.lbl_anggaran_utama_page.text = anggaran_str
        if 'lbl_dari_anggaran' in self.root.ids:
            self.root.ids.lbl_dari_anggaran.text = f"Dari anggaran {anggaran_str}"

        bulan_ini = datetime.now().strftime("%Y-%m")
        cursor.execute("SELECT SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ?", (f"{bulan_ini}%",))
        total_bulan = cursor.fetchone()[0] or 0
        if 'lbl_total_beranda' in self.root.ids:
            self.root.ids.lbl_total_beranda.text = f"Rp {total_bulan:,}".replace(",", ".")

        hari_ini = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT nominal FROM pengeluaran WHERE tanggal = ?", (hari_ini,))
        transaksi_harian = cursor.fetchall()
        total_hari = sum(t[0] for t in transaksi_harian)
        jml_transaksi = len(transaksi_harian)
        
        if 'lbl_hari_ini' in self.root.ids:
            self.root.ids.lbl_hari_ini.text = f"Rp {total_hari:,}".replace(",", ".")
            self.root.ids.lbl_jml_transaksi.text = f"{jml_transaksi} transaksi"

        sisa_anggaran = anggaran_val - total_bulan
        if 'lbl_sisa_anggaran' in self.root.ids:
            self.root.ids.lbl_sisa_anggaran.text = f"Rp {sisa_anggaran:,}".replace(",", ".")

        persen_anggaran = (total_bulan / anggaran_val * 100) if anggaran_val > 0 else 0
        if persen_anggaran > 100: persen_anggaran = 100
        
        if 'lbl_persen_anggaran' in self.root.ids:
            self.root.ids.lbl_persen_anggaran.text = f"{int(persen_anggaran)}%"
            w_fill = persen_anggaran / 100 if persen_anggaran > 0 else 0.001
            w_empty = (1 - w_fill) if w_fill < 1 else 0.001
            self.root.ids.bar_persen_anggaran.size_hint_x = w_fill
            self.root.ids.bar_persen_sisa.size_hint_x = w_empty

        if 'lbl_anggaran_persen_page' in self.root.ids:
            self.root.ids.lbl_anggaran_persen_page.text = f"{int(persen_anggaran)}%"
            self.root.ids.bar_anggaran_page_fill.size_hint_x = w_fill
            self.root.ids.bar_anggaran_page_empty.size_hint_x = w_empty

        cursor.execute("SELECT kategori, SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ? GROUP BY kategori", (f"{bulan_ini}%",))
        kategori_data = cursor.fetchall()
        kategori_dict = {kat: nom for kat, nom in kategori_data}

        warna_kategori = {
            'Makanan': [0.96, 0.35, 0.45, 1],
            'Transportasi': [1.0, 0.65, 0.1, 1],
            'Belanja': [0.3, 0.55, 0.95, 1],
            'Kesehatan': [0.3, 0.8, 0.65, 1],
            'Hiburan': [0.7, 0.4, 0.8, 1],
            'Lainnya': [0.8, 0.6, 0.7, 1]
        }

        chart_data = []
        if 'layout_legend_beranda' in self.root.ids:
            legend_beranda = self.root.ids.layout_legend_beranda
            legend_beranda.clear_widgets()

            if total_bulan > 0:
                for kat, total_kat in kategori_data:
                    pct = total_kat / total_bulan
                    col = warna_kategori.get(kat, [0.6, 0.6, 0.6, 1])
                    chart_data.append((col, pct))
                    legend_item = LegendItemDetail(color_rgba=col, label_text=kat, pct_text=f"{int(pct*100)}%", val_text="")
                    legend_beranda.add_widget(legend_item)
            
            self.root.ids.donut_chart_beranda.set_data(chart_data)

        if 'layout_rincian_anggaran_list' in self.root.ids:
            rincian_layout = self.root.ids.layout_rincian_anggaran_list
            rincian_layout.clear_widgets()

            semua_kategori = ['Makanan', 'Transportasi', 'Belanja', 'Kesehatan', 'Hiburan', 'Lainnya']
            porsi_bawaan = {'Makanan': 800000, 'Transportasi': 400000, 'Belanja': 500000, 'Kesehatan': 300000, 'Hiburan': 200000, 'Lainnya': 400000}

            for kat in semua_kategori:
                terpakai = kategori_dict.get(kat, 0)
                alokasi_kat = int(anggaran_val * (porsi_bawaan.get(kat, 300000) / 2000000))
                terpakai_str = f"Rp {terpakai:,}".replace(",", ".")
                alokasi_str = f"(Rp {alokasi_kat:,})".replace(",", ".")
                
                row = AnggaranCategoryRow(kategori=kat, nominal_str=terpakai_str, max_nominal_str=alokasi_str)
                rincian_layout.add_widget(row)

        if 'layout_detail_kategori_grafik' in self.root.ids:
            legend_grafik = self.root.ids.layout_detail_kategori_grafik
            legend_grafik.clear_widgets()

            if self.tab_grafik_aktif == 'kategori':
                if 'lbl_total_donut_grafik' in self.root.ids:
                    self.root.ids.lbl_total_donut_grafik.text = f"Total\nRp {total_bulan:,}".replace(",", ".")

                grafik_chart_data = []
                if total_bulan > 0:
                    for kat, total_kat in kategori_data:
                        pct = total_kat / total_bulan
                        col = warna_kategori.get(kat, [0.6, 0.6, 0.6, 1])
                        grafik_chart_data.append((col, pct))
                        nom_str = f"Rp {total_kat:,}".replace(",", ".")
                        item_leg = LegendItemDetail(color_rgba=col, label_text=kat, pct_text=f"{int(pct*100)}%", val_text=nom_str)
                        legend_grafik.add_widget(item_leg)
                self.root.ids.donut_chart_halaman.set_data(grafik_chart_data)
            else:
                cursor.execute("SELECT SUBSTR(tanggal, 1, 7) as bulan, SUM(nominal) FROM pengeluaran GROUP BY bulan ORDER BY bulan DESC LIMIT 5")
                bulanan_data = cursor.fetchall()
                total_semua_bulan = sum(b[1] for b in bulanan_data) if bulanan_data else 0

                if 'lbl_total_donut_grafik' in self.root.ids:
                    self.root.ids.lbl_total_donut_grafik.text = f"Total\nRp {total_semua_bulan:,}".replace(",", ".")

                warna_bulan = [
                    [0.96, 0.45, 0.62, 1],
                    [0.3, 0.55, 0.95, 1],
                    [1.0, 0.65, 0.1, 1],
                    [0.3, 0.8, 0.65, 1],
                    [0.7, 0.4, 0.8, 1]
                ]

                bulanan_chart_data = []
                nama_bulan_indo = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mei", "06": "Jun", 
                                   "07": "Jul", "08": "Ags", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des"}

                for idx, (thn_bln, total_bln) in enumerate(bulanan_data):
                    pct = (total_bln / total_semua_bulan) if total_semua_bulan > 0 else 0
                    col = warna_bulan[idx % len(warna_bulan)]
                    bulanan_chart_data.append((col, pct))
                    
                    try:
                        y, m = thn_bln.split("-")
                        label_bln = f"{nama_bulan_indo.get(m, m)} {y}"
                    except:
                        label_bln = thn_bln

                    nom_str = f"Rp {total_bln:,}".replace(",", ".")
                    item_leg = LegendItemDetail(color_rgba=col, label_text=label_bln, pct_text=f"{int(pct*100)}%", val_text=nom_str)
                    legend_grafik.add_widget(item_leg)

                self.root.ids.donut_chart_halaman.set_data(bulanan_chart_data)

        if 'barchart_7days' in self.root.ids and 'layout_xaxis_dates' in self.root.ids:
            today = datetime.now().date()
            days_data = []
            xaxis_layout = self.root.ids.layout_xaxis_dates
            xaxis_layout.clear_widgets()

            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                d_str = d.strftime("%Y-%m-%d")
                cursor.execute("SELECT SUM(nominal) FROM pengeluaran WHERE tanggal = ?", (d_str,))
                val = cursor.fetchone()[0] or 0
                days_data.append((d_str, val))
                
                lbl_dt = Label(text=d.strftime("%d/%m"), color=[0.5, 0.5, 0.5, 1], font_size="10sp", halign='center')
                xaxis_layout.add_widget(lbl_dt)

            self.root.ids.barchart_7days.set_data(days_data)

        self.filter_riwayat("")
        conn.close()

    def filter_kategori_riwayat(self, kategori):
        self.kategori_filter_aktif = kategori
        keyword = self.root.ids.input_cari.text if 'input_cari' in self.root.ids else ""
        self.filter_riwayat(keyword)

    def filter_riwayat(self, keyword):
        conn = get_db_connection()
        cursor = conn.cursor()
        list_riwayat = self.root.ids.list_riwayat_lengkap
        list_riwayat.clear_widgets()

        query = "SELECT id, tanggal, kategori, nominal, catatan FROM pengeluaran WHERE 1=1"
        params = []

        if self.kategori_filter_aktif != "Semua":
            query += " AND kategori = ?"
            params.append(self.kategori_filter_aktif)

        if keyword:
            query += " AND (kategori LIKE ? OR catatan LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        query += " ORDER BY id DESC"
        cursor.execute(query, params)

        for item in cursor.fetchall():
            item_id, tgl, kat, nom, cat = item
            try:
                dt_obj = datetime.strptime(tgl, "%Y-%m-%d")
                bulan_indo = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
                tgl_format = f"{dt_obj.day} {bulan_indo[dt_obj.month - 1]} {dt_obj.year}"
            except:
                tgl_format = tgl

            main_title = cat if cat else kat
            sub_title = f"{kat} • {tgl_format}"
            nominal_str = f"-Rp {nom:,}".replace(",", ".")

            card = ItemCard(
                main_text=main_title, 
                sub_text=sub_title, 
                nominal_text=nominal_str,
                kategori=kat,
                item_id=item_id,
                app_instance=self
            )
            list_riwayat.add_widget(card)
        conn.close()

    def buka_laporan_bulanan(self):
        self.pilih_periode_laporan("bulanan")
        self.root.ids.sm.current = 'laporan_bulanan'

    def ubah_tanggal_harian(self, val, jenis_ubah):
        indo_to_angka = {"Januari": "01", "Februari": "02", "Maret": "03", "April": "04", "Mei": "05", "Juni": "06",
                         "Juli": "07", "Agustus": "08", "September": "09", "Oktober": "10", "November": "11", "Desember": "12"}
        if jenis_ubah == 'hari':
            self.pilih_hari = val
        elif jenis_ubah == 'bulan':
            self.pilih_bulan_angka = indo_to_angka.get(val, "01")
        elif jenis_ubah == 'tahun':
            self.pilih_tahun = val
        
        if self.periode_laporan_aktif == 'harian':
            self.pilih_periode_laporan('harian')

    def pilih_periode_laporan(self, jenis):
        self.periode_laporan_aktif = jenis
        if 'btn_lap_harian' in self.root.ids and 'btn_lap_bulanan' in self.root.ids and 'btn_lap_tahunan' in self.root.ids:
            self.root.ids.btn_lap_harian.color = [0.1, 0.1, 0.1, 1] if jenis == 'harian' else [0.6, 0.6, 0.6, 1]
            self.root.ids.btn_lap_bulanan.color = [0.1, 0.1, 0.1, 1] if jenis == 'bulanan' else [0.6, 0.6, 0.6, 1]
            self.root.ids.btn_lap_tahunan.color = [0.1, 0.1, 0.1, 1] if jenis == 'tahunan' else [0.6, 0.6, 0.6, 1]

        if 'layout_pilih_tanggal_harian' in self.root.ids:
            if jenis == 'harian':
                self.root.ids.layout_pilih_tanggal_harian.height = "45dp"
                self.root.ids.layout_pilih_tanggal_harian.opacity = 1
            else:
                self.root.ids.layout_pilih_tanggal_harian.height = "0dp"
                self.root.ids.layout_pilih_tanggal_harian.opacity = 0

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now()
        nama_bulan_indo = {"01": "Januari", "02": "Februari", "03": "Maret", "04": "April", "05": "Mei", "06": "Juni", 
                           "07": "Juli", "08": "Agustus", "09": "September", "10": "Oktober", "11": "November", "12": "Desember"}

        if jenis == "harian":
            target_date = f"{self.pilih_tahun}-{self.pilih_bulan_angka}-{self.pilih_hari}"
            cursor.execute("SELECT SUM(nominal) FROM pengeluaran WHERE tanggal = ?", (target_date,))
            total_val = cursor.fetchone()[0] or 0
            
            nama_bln_str = nama_bulan_indo.get(self.pilih_bulan_angka, "")
            if 'lbl_lap_judul_total' in self.root.ids:
                self.root.ids.lbl_lap_judul_total.text = f"Total Pengeluaran Tanggal {int(self.pilih_hari)} {nama_bln_str} {self.pilih_tahun}"
            if 'lbl_lap_info_tambahan' in self.root.ids:
                self.root.ids.lbl_lap_info_tambahan.text = f"Tanggal: {self.pilih_hari}-{self.pilih_bulan_angka}-{self.pilih_tahun}"
            if 'lbl_lap_judul_rincian' in self.root.ids:
                self.root.ids.lbl_lap_judul_rincian.text = "Rincian Kategori Tanggal Ini"

            cursor.execute("SELECT kategori, SUM(nominal) FROM pengeluaran WHERE tanggal = ? GROUP BY kategori", (target_date,))
            kategori_data = cursor.fetchall()

        elif jenis == "bulanan":
            target_month = now.strftime("%Y-%m")
            m_str = now.strftime("%m")
            y_str = now.strftime("%Y")
            cursor.execute("SELECT SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ?", (f"{target_month}%",))
            total_val = cursor.fetchone()[0] or 0

            hari_ini_tgl = now.day
            rata_harian = int(total_val / hari_ini_tgl) if hari_ini_tgl > 0 else 0

            if 'lbl_lap_judul_total' in self.root.ids:
                self.root.ids.lbl_lap_judul_total.text = f"Total Pengeluaran Bulan {nama_bulan_indo.get(m_str, m_str)}"
            if 'lbl_lap_info_tambahan' in self.root.ids:
                self.root.ids.lbl_lap_info_tambahan.text = f"Rata-rata harian: Rp {rata_harian:,}".replace(",", ".")
            if 'lbl_lap_judul_rincian' in self.root.ids:
                self.root.ids.lbl_lap_judul_rincian.text = f"Rincian Kategori Bulan {nama_bulan_indo.get(m_str, m_str)}"

            cursor.execute("SELECT kategori, SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ? GROUP BY kategori", (f"{target_month}%",))
            kategori_data = cursor.fetchall()

        else:  # tahunan
            target_year = now.strftime("%Y")
            cursor.execute("SELECT SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ?", (f"{target_year}%",))
            total_val = cursor.fetchone()[0] or 0

            bulan_berjalan = now.month
            rata_bulanan = int(total_val / bulan_berjalan) if bulan_berjalan > 0 else 0

            if 'lbl_lap_judul_total' in self.root.ids:
                self.root.ids.lbl_lap_judul_total.text = f"Total Pengeluaran Tahun {target_year}"
            if 'lbl_lap_info_tambahan' in self.root.ids:
                self.root.ids.lbl_lap_info_tambahan.text = f"Rata-rata bulanan: Rp {rata_bulanan:,}".replace(",", ".")
            if 'lbl_lap_judul_rincian' in self.root.ids:
                self.root.ids.lbl_lap_judul_rincian.text = f"Rincian Kategori Tahun {target_year}"

            cursor.execute("SELECT kategori, SUM(nominal) FROM pengeluaran WHERE tanggal LIKE ? GROUP BY kategori", (f"{target_year}%",))
            kategori_data = cursor.fetchall()

        if 'lbl_lap_total_nominal' in self.root.ids:
            self.root.ids.lbl_lap_total_nominal.text = f"Rp {total_val:,}".replace(",", ".")

        if 'layout_lap_rincian_kategori' in self.root.ids:
            lap_layout = self.root.ids.layout_lap_rincian_kategori
            lap_layout.clear_widgets()

            if total_val > 0:
                for kat, total_kat in kategori_data:
                    pct = int((total_kat / total_val) * 100)
                    nom_str = f"Rp {total_kat:,}".replace(",", ".")
                    max_str = f"{pct}% dari total"
                    row = AnggaranCategoryRow(kategori=kat, nominal_str=nom_str, max_nominal_str=max_str)
                    lap_layout.add_widget(row)
            else:
                lap_layout.add_widget(Label(text="Belum ada transaksi pada periode ini.", color=[0.5, 0.5, 0.5, 1], font_size="13sp", size_hint_y=None, height="40dp"))

        conn.close()

    def buka_screen_edit(self, item_id):
        self.id_transaksi_sedang_diedit = item_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tanggal, kategori, nominal, catatan FROM pengeluaran WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            tgl, kat, nom, cat = row
            if 'edit_tanggal' in self.root.ids:
                self.root.ids.edit_tanggal.text = tgl
            if 'edit_kategori' in self.root.ids:
                self.root.ids.edit_kategori.text = kat
            if 'edit_nominal' in self.root.ids:
                self.root.ids.edit_nominal.text = str(nom)
            if 'edit_catatan' in self.root.ids:
                self.root.ids.edit_catatan.text = cat if cat else ""
            
            self.root.ids.sm.current = 'edit_transaksi'

    def simpan_perubahan_transaksi(self):
        if not self.id_transaksi_sedang_diedit:
            return
        
        tgl = self.root.ids.edit_tanggal.text
        kat = self.root.ids.edit_kategori.text
        nom = self.root.ids.edit_nominal.text
        cat = self.root.ids.edit_catatan.text

        if nom:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE pengeluaran SET tanggal = ?, kategori = ?, nominal = ?, catatan = ? WHERE id = ?", 
                           (tgl, kat, int(nom), cat, self.id_transaksi_sedang_diedit))
            conn.commit()
            conn.close()
            self.muat_data()
            self.root.ids.sm.current = 'riwayat'

    def hapus_transaksi_sedang_diedit(self):
        if not self.id_transaksi_sedang_diedit:
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pengeluaran WHERE id = ?", (self.id_transaksi_sedang_diedit,))
        conn.commit()
        conn.close()
        self.muat_data()
        self.root.ids.sm.current = 'riwayat'

    def buka_dialog_anggaran(self):
        content = BoxLayout(orientation='vertical', spacing='12dp', padding='15dp')
        
        self.input_anggaran_baru = TextInput(
            hint_text="Ketik nominal baru (misal: 3000000)",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height="45dp"
        )
        
        btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height="45dp")
        btn_batal = Button(
            text="Batal", 
            background_normal='', background_color=[0.9, 0.9, 0.9, 1], color=[0.3, 0.3, 0.3, 1], bold=True,
            on_release=lambda x: self.popup_anggaran.dismiss()
        )
        btn_simpan = Button(
            text="Simpan", 
            background_normal='', background_color=[0.96, 0.45, 0.62, 1], color=[1, 1, 1, 1], bold=True,
            on_release=lambda x: self.simpan_anggaran_dari_popup()
        )
        btn_box.add_widget(btn_batal)
        btn_box.add_widget(btn_simpan)
        
        content.add_widget(Label(text="Ubah Target Anggaran", color=[0.96, 0.45, 0.62, 1], font_size="16sp", bold=True, size_hint_y=None, height="20dp"))
        content.add_widget(Label(text="Tentukan batas pengeluaranmu.", color=[0.4, 0.4, 0.4, 1], font_size="12sp", size_hint_y=None, height="15dp"))
        content.add_widget(self.input_anggaran_baru)
        content.add_widget(Widget())
        content.add_widget(btn_box)

        self.popup_anggaran = Popup(
            title="Atur Anggaran", title_color=[1, 1, 1, 0], title_size="0sp",
            content=content, size_hint=(0.85, 0.4), background_color=[1, 1, 1, 1], separator_height=0
        )
        self.popup_anggaran.open()

    def simpan_anggaran_dari_popup(self):
        val = self.input_anggaran_baru.text
        if val:
            self.update_anggaran(val)
            self.popup_anggaran.dismiss()

    def update_anggaran(self, anggaran_baru):
        if anggaran_baru:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO pengaturan (kunci, nilai) VALUES ('anggaran', ?)", (anggaran_baru,))
            conn.commit()
            conn.close()
            self.muat_data()

    def buka_screen_tambah(self):
        self.root.ids.sm.current = 'form'
        self.root.ids.form_tanggal.text = datetime.now().strftime("%Y-%m-%d")
        self.root.ids.form_nominal.text = ""
        self.root.ids.form_catatan.text = ""

    def simpan_transaksi(self):
        tgl = self.root.ids.form_tanggal.text
        kat = self.root.ids.form_kategori.text
        nom = self.root.ids.form_nominal.text
        cat = self.root.ids.form_catatan.text
        if nom:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pengeluaran (tanggal, kategori, nominal, catatan) VALUES (?, ?, ?, ?)", (tgl, kat, int(nom), cat))
            conn.commit()
            conn.close()
            self.muat_data()
            self.root.ids.sm.current = 'beranda'

    def reset_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pengeluaran")
        conn.commit()
        conn.close()
        self.muat_data()

if __name__ == '__main__':
    CatatUangApp().run()
