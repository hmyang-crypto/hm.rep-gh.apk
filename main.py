# -*- coding: utf-8 -*-
import json
import os
import re
import ssl
import sys
import threading
import time
import traceback
import urllib.request
import base64
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from functools import partial

# 💡 GitHub Raw 주소
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/hmyang-crypto/hm-rep/refs/heads/main/version.txt"
UPDATE_CODE_URL = "https://raw.githubusercontent.com/hmyang-crypto/hm-rep/refs/heads/main/main.py"
CURRENT_VERSION = "1.9.5.4"


def check_and_apply_update():
    try:
        print("🔍 서버에서 최신 업데이트 확인 중...")
        ssl_context = ssl._create_unverified_context()
        req = urllib.request.Request(
            UPDATE_CHECK_URL, headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            req, timeout=5, context=ssl_context
        ) as response:
            if response.status == 200:
                server_version = response.read().decode("utf-8").strip()

                if server_version > CURRENT_VERSION:
                    print(
                        f"🚀 새 버전 발견 ({server_version})! 코드를 다운로드합니다."
                    )
                    code_req = urllib.request.Request(
                        UPDATE_CODE_URL, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(
                        code_req, timeout=10, context=ssl_context
                    ) as new_code_response:
                        if new_code_response.status == 200:
                            app_dir = os.path.dirname(
                                os.path.abspath(__file__)
                            )
                            updated_file_path = os.path.join(
                                app_dir, "updated_main.py"
                            )

                            with open(
                                updated_file_path, "w", encoding="utf-8"
                            ) as f:
                                f.write(
                                    new_code_response.read().decode("utf-8")
                                )

                            print("✅ updated_main.py 최신 스크립트 저장 완료!")
                else:
                    app_dir = os.path.dirname(os.path.abspath(__file__))
                    old_script = os.path.join(app_dir, "updated_main.py")
                    if os.path.exists(old_script):
                        try:
                            os.remove(old_script)
                            print("🧹 과거 업데이트 임시파일 정리 완료")
                        except Exception:
                            pass
    except Exception as e:
        print(f"⚠️ 업데이트 확인 중 오류 (무시하고 앱 실행): {e}")


if "updated_main.py" not in os.path.basename(__file__):
    check_and_apply_update()

    _app_dir = os.path.dirname(os.path.abspath(__file__))
    _updated_script = os.path.join(_app_dir, "updated_main.py")

    if os.path.exists(_updated_script) and __name__ == "__main__":
        try:
            print("🔄 최신 업데이트 스크립트(updated_main.py)로 실행합니다...")
            with open(_updated_script, "r", encoding="utf-8") as _f:
                _code = _f.read()
            exec(
                compile(_code, _updated_script, "exec"),
                {"__name__": "__main__", "__file__": _updated_script},
            )
            sys.exit(0)
        except Exception as _exec_err:
            print("=" * 60)
            print("🚨 updated_main.py 실행 중 발생한 상세 에러:")
            traceback.print_exc()  # 💡 [핵심] 몇번째 줄에서 무슨 에러가 났는지 콘솔에 출력!
            print("=" * 60)
            print(f"⚠️ 업데이트 코드 실행 실패 (기본 main.py로 대체 실행): {_exec_err}")

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, platform

if platform == "android":
    try:
        from jnius import autoclass

        current_app = autoclass(
            "android.app.ActivityThread"
        ).currentApplication()
        context = current_app.getApplicationContext()
        user_data_dir = context.getFilesDir().getAbsolutePath()
        kivy_home_dir = os.path.join(user_data_dir, ".kivy")
        os.environ["KIVY_HOME"] = kivy_home_dir
        if not os.path.exists(kivy_home_dir):
            os.makedirs(kivy_home_dir)
    except Exception as e:
        print(f"🚨 KIVY_HOME 설정 오류: {e}")

if platform == "android":
    Window.softinput_mode = "below_target"
    from android.permissions import Permission, request_permissions
    from android.runnable import run_on_ui_thread
    from jnius import JavaException, PythonJavaClass, autoclass, java_method

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "replacement-463907-07ae6e152f37.json"
SPREADSHEET_NAME = "보충시트"
USER_SHEET_NAME = "사용자_목록"
TASK_SHEET_NAME = "보충작업_지시서"
LOG_SHEET_NAME = "작업완료_로그"
FCM_TOKEN_SHEET_NAME = "FCM_토큰"
LOCATION_CAPA_SHEET_NAME = "로케이션별재고 raw"

# 💡 [추가] 원복 작업 전용 상수 및 웹앱 URL
RETURN_TASK_SHEET_NAME = "원복작업_지시서"
RETURN_LOG_SHEET_NAME = "원복작업_로그"
GAS_PHOTO_UPLOAD_URL = "https://script.google.com/macros/s/AKfycbwVAMVWbBgSt0JdeTx08zr8YKU93bTt8Wt6muRlyHTQlLjc08UdxTYspon2p3pRShdG/exec"

SHEET_RANGES = {
    USER_SHEET_NAME: "A:AZ",
    TASK_SHEET_NAME: "A:AZ",
    LOG_SHEET_NAME: "A:AZ",
    FCM_TOKEN_SHEET_NAME: "A:AZ",
    LOCATION_CAPA_SHEET_NAME: "A:J",
    RETURN_TASK_SHEET_NAME: "A:AZ",  # 💡 필수 추가
    RETURN_LOG_SHEET_NAME: "A:AZ",   # 💡 필수 추가
}

try:
    LabelBase.register(name="Nanum", fn_regular="NanumSquareRoundEB.ttf")
    FONT_NAME = "Nanum"
except Exception as e:
    FONT_NAME = "Roboto"

PRIMARY_BLUE = get_color_from_hex("#1E88E5")
LIGHT_BLUE = get_color_from_hex("#E3F2FD")
FILTER_BG_GRAY = get_color_from_hex("#CFD8DC")
BG_GRAY = get_color_from_hex("#F4F7FA")
TEXT_DARK = get_color_from_hex("#212121")
TEXT_MUTED = get_color_from_hex("#757575")

# 💡 [추가] 원복 작업 전용 초록색 테마
RETURN_GREEN = get_color_from_hex("#2E7D32")
RETURN_LIGHT_GREEN = get_color_from_hex("#E8F5E9")

DEFAULT_FONT_STYLE = {
    "font_name": FONT_NAME,
    "font_size": dp(15),
    "color": TEXT_DARK,
}
Window.clearcolor = BG_GRAY

g_recent_completed_tasks = []


def safe_int(val, default=0):
    if val is None:
        return default
    try:
        clean_str = re.sub(r"[^\d]", "", str(val))
        return int(clean_str) if clean_str else default
    except Exception:
        return default


def get_barcode_from_task(task_dict):
    for key in ["상품바코드", "바코드", "상품 바코드", "BARCODE", "Barcode"]:
        val = task_dict.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return "N/A"


HISTORY_FILE_PATH = "recent_history.json"


def get_current_4am_cutoff():
    now = datetime.now()
    if now.hour < 4:
        cutoff = (now - timedelta(days=1)).replace(
            hour=4, minute=0, second=0, microsecond=0
        )
    else:
        cutoff = now.replace(hour=4, minute=0, second=0, microsecond=0)
    return cutoff


def load_recent_history():
    global g_recent_completed_tasks
    g_recent_completed_tasks.clear()
    if not os.path.exists(HISTORY_FILE_PATH):
        return

    try:
        with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        cutoff = get_current_4am_cutoff()
        filtered = []

        for item in data:
            dt_str = str(t(item, "완료일시", "")).strip()
            if dt_str:
                try:
                    item_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    if item_dt >= cutoff:
                        filtered.append(item)
                except Exception:
                    filtered.append(item)
            else:
                filtered.append(item)

        g_recent_completed_tasks = filtered[-15:]
        if len(filtered) != len(data):
            save_recent_history()
    except Exception as e:
        print(f"⚠️ 최근 완료 이력 불러오기 에러: {e}")


def save_recent_history():
    try:
        with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                g_recent_completed_tasks[-15:],
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception as e:
        print(f"⚠️ 최근 완료 이력 저장 에러: {e}")


def clear_recent_history_file():
    global g_recent_completed_tasks
    g_recent_completed_tasks.clear()
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            os.remove(HISTORY_FILE_PATH)
        except Exception:
            pass


def open_native_korean_input(
    title, hint, initial_text, callback, is_number=False
):
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            AlertDialog = autoclass("android.app.AlertDialog$Builder")
            EditText = autoclass("android.widget.EditText")
            InputType = autoclass("android.text.InputType")
            WindowManager = autoclass(
                "android.view.WindowManager$LayoutParams"
            )

            context = PythonActivity.mActivity
            builder = AlertDialog(context)
            builder.setTitle(title)

            input_field = EditText(context)
            input_field.setHint(hint)
            if initial_text:
                input_field.setText(str(initial_text))

            if is_number:
                input_field.setInputType(InputType.TYPE_CLASS_NUMBER)

            builder.setView(input_field)

            class PositiveClickListener(PythonJavaClass):
                __javainterfaces__ = [
                    "android/content/DialogInterface$OnClickListener"
                ]

                def __init__(self, cb, field):
                    super().__init__()
                    self.cb = cb
                    self.field = field

                @java_method("(Landroid/content/DialogInterface;I)V")
                def onClick(self, dialog, which):
                    res = self.field.getText().toString()
                    Clock.schedule_once(lambda dt: self.cb(res), 0.1)

            builder.setPositiveButton(
                "확인", PositiveClickListener(callback, input_field)
            )
            builder.setNegativeButton("취소", None)

            dialog = builder.create()

            window = dialog.getWindow()
            if window:
                window.setSoftInputMode(WindowManager.SOFT_INPUT_ADJUST_PAN)

            dialog.show()
            return
        except Exception as e:
            print(
                f"⚠️ 안드로이드 시스템 입력창 오류 (Kivy fallback 사용): {e}"
            )

    SingleInputPopup(
        title=title,
        hint_text=hint,
        initial_text=initial_text,
        input_type="number" if is_number else "text",
        on_confirm=callback,
    ).open()


class StyledButton(Button):

    def __init__(self, **kwargs):
        self.btn_bg_color = kwargs.pop("bg_color", PRIMARY_BLUE)
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        if "font_size" not in kwargs:
            self.font_size = dp(14)
        with self.canvas.before:
            self.bg_color_inst = Color(*self.btn_bg_color)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size

    def set_bg_color(self, color):
        self.btn_bg_color = color
        self.bg_color_inst.rgba = color


class StyledToggleButton(ToggleButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        if "font_size" not in kwargs:
            self.font_size = dp(14)
        with self.canvas.before:
            initial_bg = PRIMARY_BLUE if self.state == "down" else LIGHT_BLUE
            self.bg_color_inst = Color(*initial_bg)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.color = (1, 1, 1, 1) if self.state == "down" else TEXT_DARK
        self.bold = True if self.state == "down" else False
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._update_state,
        )

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size

    def _update_state(self, instance, value):
        if value == "down":
            self.bg_color_inst.rgba = PRIMARY_BLUE
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.bg_color_inst.rgba = LIGHT_BLUE
            self.color = TEXT_DARK
            self.bold = False

    def set_active_visual(self, is_active):
        if is_active:
            self.state = "down"
            self.bg_color_inst.rgba = PRIMARY_BLUE
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.state = "normal"
            self.bg_color_inst.rgba = LIGHT_BLUE
            self.color = TEXT_DARK
            self.bold = False

# 💡 [새로 추가됨] 원복 화면 전용 옅은 초록색 토글 버튼 클래스
class ReturnToggleButton(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        if "font_size" not in kwargs:
            self.font_size = dp(14)
        with self.canvas.before:
            initial_bg = RETURN_GREEN if self.state == "down" else RETURN_LIGHT_GREEN
            self.bg_color_inst = Color(*initial_bg)
            self.bg_rounded_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.color = (1, 1, 1, 1) if self.state == "down" else TEXT_DARK
        self.bold = True if self.state == "down" else False
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_state)

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size

    def _update_state(self, instance, value):
        if value == "down":
            self.bg_color_inst.rgba = RETURN_GREEN
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.bg_color_inst.rgba = RETURN_LIGHT_GREEN
            self.color = TEXT_DARK
            self.bold = False

    def set_active_visual(self, is_active):
        if is_active:
            self.state = "down"
            self.bg_color_inst.rgba = RETURN_GREEN
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.state = "normal"
            self.bg_color_inst.rgba = RETURN_LIGHT_GREEN
            self.color = TEXT_DARK
            self.bold = False


class StyledSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT_DARK
        if "font_size" not in kwargs:
            self.font_size = dp(13)
        with self.canvas.before:
            self.bg_color_inst = Color(*FILTER_BG_GRAY)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size


class KoreanSpinnerOption(SpinnerOption):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.font_size = dp(13)
        self.background_normal = ""
        self.background_color = get_color_from_hex("#37474F")


class TouchableBox(ButtonBehavior, BoxLayout):
    pass


class NotificationBanner(ButtonBehavior, BoxLayout):

    def __init__(self, text, on_press_callback=None, duration=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (0.95, None)
        self.height = dp(50)
        self.pos_hint = {"center_x": 0.5, "top": 1.2}
        self.padding = (dp(15), dp(5))
        self.spacing = dp(10)
        self.on_press_callback = on_press_callback
        self.auto_dismiss_duration = duration

        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.95)
            self.bg_rect = RoundedRectangle(
                size=self.size, pos=self.pos, radius=[dp(10)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)

        icon_label = Label(
            text="🔔",
            font_name=FONT_NAME,
            font_size=dp(20),
            size_hint_x=None,
            width=dp(30),
        )
        self.add_widget(icon_label)

        self.message_label = Label(
            text=text,
            font_name=FONT_NAME,
            font_size=dp(14),
            halign="left",
            valign="middle",
            markup=True,
            color=(1, 1, 1, 1),
        )
        self.message_label.bind(size=self.message_label.setter("text_size"))
        self.add_widget(self.message_label)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_press(self):
        if self.on_press_callback:
            self.on_press_callback()
        self.dismiss()

    def show(self, target_widget):
        target_widget.add_widget(self)
        anim = Animation(
            pos_hint={"center_x": 0.5, "top": 0.98}, duration=0.4, t="out_quad"
        )
        anim.start(self)
        Clock.schedule_once(self.dismiss, self.auto_dismiss_duration)

    def dismiss(self, *args):
        Clock.unschedule(self.dismiss)
        if not self.parent:
            return

        anim = Animation(
            pos_hint={"center_x": 0.5, "top": 1.2}, duration=0.4, t="in_quad"
        )
        anim.bind(on_complete=self._remove_widget)
        anim.start(self)

    def _remove_widget(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class ZoneMultiSelectDropDown(DropDown):

    def __init__(self, zone_counts_dict, selected_zones, on_apply, **kwargs):
        super().__init__(**kwargs)
        self.auto_dismiss = True
        self.on_apply = on_apply
        self.checkboxes = {}

        self.auto_width = False
        self.width = dp(150)

        container = BoxLayout(
            orientation="vertical",
            padding=dp(6),
            spacing=dp(3),
            size_hint=(None, None),
            width=dp(150),
            height=dp(280),
        )

        with container.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.bg_rect = RoundedRectangle(
                pos=container.pos, size=container.size, radius=[dp(8)]
            )
        container.bind(
            pos=lambda i, p: setattr(self.bg_rect, "pos", p),
            size=lambda i, s: setattr(self.bg_rect, "size", s),
        )

        all_active = (
            len(selected_zones) == len(zone_counts_dict)
            or "전체" in selected_zones
        )
        self.btn_toggle_all = Button(
            text="전체해제" if all_active else "전체선택",
            font_name=FONT_NAME,
            font_size=dp(11),
            bold=True,
            size_hint_y=None,
            height=dp(30),
            background_normal="",
            background_color=get_color_from_hex("#78909C"),
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        self.btn_toggle_all.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.btn_toggle_all.bind(on_press=self._on_toggle_all_press)
        container.add_widget(self.btn_toggle_all)

        scroll = ScrollView(size_hint_y=None, height=dp(190))
        grid = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for zone_name, count in zone_counts_dict.items():
            is_active = zone_name in selected_zones or "전체" in selected_zones

            item_box = TouchableBox(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(34),
                padding=(dp(8), 0),
                spacing=dp(4),
            )
            with item_box.canvas.before:
                Color(*get_color_from_hex("#EEEEEE"))
                bg = RoundedRectangle(
                    pos=item_box.pos, size=item_box.size, radius=[dp(4)]
                )
            item_box.bind(
                pos=lambda i, p, b=bg: setattr(b, "pos", p),
                size=lambda i, s, b=bg: setattr(b, "size", s),
            )

            lbl = Label(
                text=f"{zone_name} ({count}건)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=get_color_from_hex("#212121"),
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lambda i, s: setattr(i, "text_size", s))

            chk = CheckBox(
                active=is_active,
                size_hint_x=None,
                width=dp(26),
                color=PRIMARY_BLUE,
            )

            item_box.add_widget(lbl)
            item_box.add_widget(chk)

            item_box.bind(
                on_release=lambda inst, c=chk: setattr(c, "active", not c.active)
            )
            chk.bind(active=self._on_check_change)

            grid.add_widget(item_box)
            self.checkboxes[zone_name] = chk

        scroll.add_widget(grid)
        container.add_widget(scroll)

        btn_apply = Button(
            text="적용",
            font_name=FONT_NAME,
            font_size=dp(12),
            bold=True,
            size_hint_y=None,
            height=dp(34),
            background_normal="",
            background_color=PRIMARY_BLUE,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        btn_apply.bind(size=lambda i, s: setattr(i, "text_size", s))
        btn_apply.bind(on_press=self._on_apply_press)
        container.add_widget(btn_apply)

        self.add_widget(container)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_move(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            super().on_touch_up(touch)
            return True
        return super().on_touch_up(touch)

    def _on_check_change(self, checkbox, value):
        self._update_toggle_all_btn_text()

    def _on_toggle_all_press(self, instance):
        target_state = not all(chk.active for chk in self.checkboxes.values())
        for chk in self.checkboxes.values():
            chk.active = target_state
        self._update_toggle_all_btn_text()

    def _update_toggle_all_btn_text(self):
        all_selected = all(chk.active for chk in self.checkboxes.values())
        self.btn_toggle_all.text = "전체해제" if all_selected else "전체선택"

    def _on_apply_press(self, instance):
        selected = {
            zone for zone, chk in self.checkboxes.items() if chk.active
        }
        if not selected or len(selected) == len(self.checkboxes):
            selected = {"전체"}
        self.on_apply(selected)
        self.dismiss()


g_sheet_client = None
g_spreadsheet = None
g_worksheet_objects = {}
GSPREAD_LOADED = False
GSPREAD_ERROR_MSG = ""
g_cached_sheets = {}
g_cache_timestamps = {}
CACHE_DURATION = 60


def execute_with_retry(func, *args, **kwargs):
    max_retries = 5
    base_delay = 1.5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            if e.code in [429, 503]:
                delay = base_delay * (2**attempt)
                time.sleep(delay)
            else:
                raise e
        except Exception as e:
            raise e
    raise Exception(
        "🚨 구글 API 트래픽 초과 오류 누적으로 작업이 최종 실패했습니다."
    )


def invalidate_cache(sheet_name):
    if sheet_name in g_cached_sheets:
        del g_cached_sheets[sheet_name]
    if sheet_name in g_cache_timestamps:
        del g_cache_timestamps[sheet_name]


def initialize_gspread():
    global g_sheet_client, g_spreadsheet, GSPREAD_LOADED, GSPREAD_ERROR_MSG, g_worksheet_objects
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        GSPREAD_LOADED = False
        GSPREAD_ERROR_MSG = f"인증 키 파일 '{SERVICE_ACCOUNT_FILE}'을(를) 찾을 수 없습니다."
        print(f"\n🚨 '{SERVICE_ACCOUNT_FILE}' 파일이 없습니다!\n")
        return

    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        g_sheet_client = gspread.authorize(creds)
        g_spreadsheet = g_sheet_client.open(SPREADSHEET_NAME)
        g_worksheet_objects.clear()
        GSPREAD_LOADED = True
        print(f"✅ 구글 시트 연결 성공: [{SPREADSHEET_NAME}]")
    except Exception as e:
        GSPREAD_ERROR_MSG = str(e)
        GSPREAD_LOADED = False


def get_worksheet(worksheet_name):
    global g_spreadsheet, g_worksheet_objects
    if not GSPREAD_LOADED:
        initialize_gspread()
        if not GSPREAD_LOADED or not g_spreadsheet:
            raise Exception(f"구글 연결 실패: {GSPREAD_ERROR_MSG}")

    if worksheet_name in g_worksheet_objects:
        return g_worksheet_objects[worksheet_name]

    try:
        ws = execute_with_retry(g_spreadsheet.worksheet, worksheet_name)
        g_worksheet_objects[worksheet_name] = ws
        return ws
    except Exception:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        client = gspread.authorize(creds)
        g_spreadsheet = client.open(SPREADSHEET_NAME)
        g_worksheet_objects.clear()
        ws = execute_with_retry(g_spreadsheet.worksheet, worksheet_name)
        g_worksheet_objects[worksheet_name] = ws
        return ws


def get_sheet_data(sheet_name, force_refresh=False):
    now = time.time()
    last_updated = g_cache_timestamps.get(sheet_name, 0)
    if not force_refresh and (now - last_updated) < CACHE_DURATION:
        if sheet_name in g_cached_sheets:
            return g_cached_sheets[sheet_name]
    try:
        sheet = get_worksheet(sheet_name)
        target_range = SHEET_RANGES.get(sheet_name, "A:AA")
        raw_rows = execute_with_retry(sheet.get, target_range)
        records = []
        if raw_rows and len(raw_rows) > 0:
            headers = [str(h).strip() for h in raw_rows[0]]
            for row in raw_rows[1:]:
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))
                record_dict = {
                    headers[i]: row[i] for i in range(len(headers))
                }
                records.append(record_dict)
        g_cached_sheets[sheet_name] = records
        g_cache_timestamps[sheet_name] = now
        return records
    except Exception as e:
        if sheet_name in g_cached_sheets:
            return g_cached_sheets[sheet_name]
        raise e


def t(d, k, default=""):
    return d.get(k, default)


class LoadingPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "처리 중"
        self.title_font = FONT_NAME
        self.content = Label(
            text="데이터를 처리하는 중입니다...\n잠시만 기다려주세요.",
            font_name=FONT_NAME,
            font_size=dp(16),
        )
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False


class InfoPopup(Popup):

    def __init__(self, title, message, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = FONT_NAME
        self.size_hint = (0.9, 0.5)  # 팝업 높이 비율 확장 (짤림 방지)
        
        content = BoxLayout(
            orientation="vertical", padding=dp(15), spacing=dp(10)
        )
        
        message_label = Label(
            text=str(message),
            font_name=FONT_NAME,
            font_size=dp(15),
            markup=True,  # 💡 [핵심] BBCode 태그([color], [size]) 정상 적용 설정
            halign="center",
            valign="middle",
        )
        message_label.bind(
            width=lambda *x: message_label.setter("text_size")(
                message_label, (message_label.width, None)
            )
        )
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(message_label)
        content.add_widget(scroll_view)
        
        ok_button = StyledButton(
            text="확인", size_hint_y=None, height=dp(45)
        )
        ok_button.bind(on_press=self.dismiss)
        content.add_widget(ok_button)
        
        self.content = content


class SingleInputPopup(Popup):

    def __init__(
        self,
        title,
        hint_text,
        on_confirm,
        initial_text="",
        input_type="text",
        warning_text=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = FONT_NAME
        self.size_hint = (0.9, None)
        self.auto_dismiss = False
        self.on_confirm = on_confirm

        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15),
            size_hint_y=None,
        )
        main_layout.bind(minimum_height=main_layout.setter("height"))
        main_layout.bind(
            height=lambda instance, value: setattr(
                self, "height", value + dp(60)
            )
        )

        if warning_text:
            warning_label = Label(
                text=warning_text,
                font_name=FONT_NAME,
                font_size=dp(15),
                color=get_color_from_hex("#D32F2F"),
                markup=True,
                halign="center",
                size_hint_y=None,
            )
            warning_label.bind(
                width=lambda *x: warning_label.setter("text_size")(
                    warning_label, (warning_label.width, None)
                ),
                texture_size=lambda *x: warning_label.setter("height")(
                    warning_label, warning_label.texture_size[1]
                ),
            )
            main_layout.add_widget(warning_label)

        self.text_input = TextInput(
            text=initial_text,
            hint_text=hint_text,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            font_name=FONT_NAME,
            input_type=input_type,
        )
        button_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(10),
        )
        cancel_button = StyledButton(text="취소", bg_color=(0.6, 0.6, 0.6, 1))
        cancel_button.bind(on_press=self.dismiss)
        ok_button = StyledButton(text="확인")
        ok_button.bind(on_press=self._on_ok_press)

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(ok_button)
        main_layout.add_widget(self.text_input)
        main_layout.add_widget(button_layout)
        self.content = main_layout
        self.bind(on_open=lambda *a: setattr(self.text_input, "focus", True))

    def _on_ok_press(self, instance):
        self.on_confirm(self.text_input.text)
        self.dismiss()


# 최근 완료 이력 컴팩트 리스트 팝업 창
class RecentCompletedPopup(Popup):
    _is_opening = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "내 최근 완료 내역 (최신순)"
        self.title_font = FONT_NAME
        self.size_hint = (0.95, 0.85)

        self.layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(8)
        )

        self.loading_lbl = Label(
            text="최근 완료 내역을 불러오는 중입니다...",
            font_name=FONT_NAME,
            font_size=dp(15),
            color=PRIMARY_BLUE,
        )
        self.layout.add_widget(self.loading_lbl)

        btn_close = StyledButton(
            text="닫기",
            size_hint_y=None,
            height=dp(40),
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_close.bind(on_press=self.dismiss)
        self.layout.add_widget(btn_close)

        self.content = self.layout
        self.bind(on_open=self._async_load_data)

    def _async_load_data(self, *args):
        Clock.schedule_once(lambda dt: self._render_content(), 0.1)

    def _render_content(self):
        load_recent_history()
        self.layout.remove_widget(self.loading_lbl)

        if not g_recent_completed_tasks:
            no_data_lbl = Label(
                text="최근 완료된 보충 작업 이력이 없습니다.",
                font_name=FONT_NAME,
                font_size=dp(15),
                color=TEXT_MUTED,
            )
            self.layout.add_widget(no_data_lbl, index=len(self.layout.children))
        else:
            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
            grid.bind(minimum_height=grid.setter("height"))

            for item in reversed(g_recent_completed_tasks):
                grid.add_widget(self._create_compact_history_row(item))

            scroll.add_widget(grid)
            self.layout.add_widget(scroll, index=len(self.layout.children))

    def dismiss(self, *args):
        RecentCompletedPopup._is_opening = False
        super().dismiss(*args)

    @classmethod
    def open_safely(cls):
        if cls._is_opening:
            return
        cls._is_opening = True
        popup = cls()
        popup.open()

    def _create_compact_history_row(self, task_data):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(110),
            padding=dp(8),
            spacing=dp(6),
        )

        with row.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])
        row.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        info_box = BoxLayout(orientation="vertical", spacing=dp(2))

        equip_name = str(t(task_data, "장비", "N/A")).strip()
        comp_time = str(
            t(task_data, "완료일시", datetime.now().strftime("%H:%M"))
        ).strip()
        if len(comp_time) > 8:
            comp_time = comp_time[-8:-3]

        lbl_top = Label(
            text=f"[color=1E88E5][b][{equip_name}][/b][/color]  |  완료시간: [b]{comp_time}[/b]",
            font_name=FONT_NAME,
            font_size=dp(12),
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
        )
        lbl_top.bind(size=lambda i, s: setattr(i, "text_size", s))
        info_box.add_widget(lbl_top)

        prod_name = str(t(task_data, "상품명", "N/A")).strip()
        lbl_prod = Label(
            text=f"[b]{prod_name}[/b]",
            font_name=FONT_NAME,
            font_size=dp(13),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        lbl_prod.bind(size=lambda i, s: setattr(i, "text_size", s))
        info_box.add_widget(lbl_prod)

        bc_val = get_barcode_from_task(task_data)
        lbl_bc = Label(
            text=f"바코드: [b][color=1E88E5]{bc_val}[/color][/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
        )
        lbl_bc.bind(size=lambda i, s: setattr(i, "text_size", s))
        info_box.add_widget(lbl_bc)

        from_loc = str(t(task_data, "기존로케이션", "-")).strip()
        to_loc = str(t(task_data, "보충로케이션", "-")).strip()
        lbl_loc = Label(
            text=f"위치: [color=D32F2F][b]{from_loc}[/b][/color] ➔ [color=1E88E5][b]{to_loc}[/b][/color]",
            font_name=FONT_NAME,
            font_size=dp(12),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        lbl_loc.bind(size=lambda i, s: setattr(i, "text_size", s))
        info_box.add_widget(lbl_loc)

        req_q = t(task_data, "지시수량", 0)
        conf_q = t(task_data, "확인수량", 0)
        lbl_qty = Label(
            text=f"수량: 지시 {req_q}개 / [color=2E7D32][b]확인 {conf_q}개[/b][/color]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=TEXT_MUTED,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
        )
        lbl_qty.bind(size=lambda i, s: setattr(i, "text_size", s))
        info_box.add_widget(lbl_qty)

        row.add_widget(info_box)

        btn_reprint = StyledButton(
            text="[인쇄]",
            size_hint_x=None,
            width=dp(55),
            font_size=dp(12),
            bg_color=get_color_from_hex("#00897B"),
        )
        btn_reprint.bind(on_press=lambda x: self._prompt_reprint(task_data))
        row.add_widget(btn_reprint)

        return row

    def _prompt_reprint(self, task_data):
        app = App.get_running_app()

        def do_reprint():
            try:
                task_list_screen = app.root.get_screen("task_list")
                task_list_screen._start_print_job(task_data)
                app.show_toast("라벨 재인쇄를 요청했습니다.")
            except Exception as e:
                app.show_info_popup("오류", f"인쇄 오류: {e}")

        prod_name = str(t(task_data, "상품명", "선택 항목")).strip()
        app.show_confirmation_popup(
            title="라벨 재인쇄",
            message=f"[color=ffffff][{prod_name[:18]}]\n라벨 1장을 재인쇄하시겠습니까?[/color]",
            on_yes=do_reprint,
        )

class ScanFailureReasonPopup(Popup):
    def __init__(self, on_select_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "스캔 실패 사유 선택 🚨"
        self.title_font = FONT_NAME
        self.size_hint = (0.9, None)
        self.height = dp(340)
        self.auto_dismiss = False
        self.on_select_callback = on_select_callback

        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))

        # 💡 요청하신 3가지 프리셋 버튼
        presets = [
            "바코드 미인식(훼손포함)",
            "바코드 없음",
            "부자재",
        ]

        for reason in presets:
            btn = StyledButton(
                text=reason,
                size_hint_y=None,
                height=dp(45),
                bg_color=get_color_from_hex("#455A64"),
            )
            btn.bind(on_release=lambda inst, r=reason: self._select_reason(r))
            layout.add_widget(btn)

        # 💡 기타 사유 (수기 직접입력) 버튼
        btn_custom = StyledButton(
            text="✏️ 기타 사유 (직접입력)",
            size_hint_y=None,
            height=dp(45),
            bg_color=PRIMARY_BLUE,
        )
        btn_custom.bind(on_release=self._open_custom_input)
        layout.add_widget(btn_custom)

        # 취소 버튼
        btn_cancel = StyledButton(
            text="취소",
            size_hint_y=None,
            height=dp(40),
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_cancel.bind(on_press=self.dismiss)
        layout.add_widget(btn_cancel)

        self.content = layout

    def _select_reason(self, reason):
        self.on_select_callback(reason)
        self.dismiss()

    def _open_custom_input(self, instance):
        self.dismiss()
        open_native_korean_input(
            "기타 사유 입력",
            "사유를 직접 입력하세요",
            "",
            self.on_select_callback,
        )

class MultipleSkuSelectPopup(Popup):

    def __init__(self, matches, on_select, **kwargs):
        super().__init__(**kwargs)
        self.title = "검수 대상 선택 (중복 SKU)"
        self.size_hint = (0.9, 0.7)
        layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )
        layout.add_widget(
            Label(
                text="스캔한 바코드가 여러 건 존재합니다.\n대상을 선택해주세요.",
                font_name=FONT_NAME,
                size_hint_y=None,
                height=dp(40),
            )
        )

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        grid.bind(minimum_height=grid.setter("height"))

        for item in matches:
            task = item["task_data"]
            loc = t(task, "기존로케이션", t(task, "보충로케이션", "N/A"))
            qty = t(task, "지시수량", "0")
            btn = StyledButton(
                text=f"보관위치: {loc} | 지시수량: {qty}",
                size_hint_y=None,
                height=dp(55),
            )
            btn.bind(
                on_release=lambda instance, i=item: (
                    on_select(i),
                    self.dismiss(),
                )
            )
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.content = layout


class InspectionPopup(Popup):

    def __init__(self, card, task_list_screen, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.task_data = card.task_data
        self.task_list_screen = task_list_screen
        self.current_remarks = str(t(self.task_data, "비고", ""))
        self.target_location = str(t(self.task_data, "보충로케이션", "")).strip().upper()

        self.title = "검수 및 최종 로케이션 스캔"
        self.title_font = FONT_NAME
        self.size_hint = (0.95, None)
        self.height = dp(580)
        self.auto_dismiss = False

        main_layout = BoxLayout(
            orientation="vertical", padding=dp(15), spacing=dp(10)
        )

        total_qty = safe_int(t(self.task_data, "지시수량", 0))
        default_box_size = safe_int(
            t(self.task_data, "박스입수량", t(self.task_data, "박스 입수량", 1))
        )
        if default_box_size <= 0:
            default_box_size = 1

        product_name = str(t(self.task_data, "상품명", ""))
        is_invoice_only = default_box_size == 1 or "송장" in product_name

        info_label = Label(
            text=f"지시수량: [b]{total_qty}[/b] / 기본입수량: [b]{default_box_size}[/b]",
            font_name=FONT_NAME,
            font_size=dp(15),
            markup=True,
            size_hint_y=None,
            height=dp(25),
        )
        main_layout.add_widget(info_label)

        if is_invoice_only:
            warn_lbl = Label(
                text="[color=D32F2F][b][송장만 부착 항목] - 로케이션을 적지 마세요![/b][/color]",
                font_name=FONT_NAME,
                font_size=dp(13),
                markup=True,
                size_hint_y=None,
                height=dp(22),
            )
            main_layout.add_widget(warn_lbl)

        input_grid = GridLayout(
            cols=2, spacing=dp(10), size_hint_y=None, height=dp(150)
        )

        input_grid.add_widget(
            Label(
                text=f"박스 입수량 (기존 {default_box_size}):",
                font_name=FONT_NAME,
                font_size=dp(14),
            )
        )
        self.box_size_input = TextInput(
            text=str(default_box_size),
            multiline=False,
            input_type="number",
            font_name=FONT_NAME,
            font_size=dp(18),
            halign="center",
            readonly=True,
        )
        self.box_size_input.bind(
            on_touch_down=lambda instance, touch: self._touch_input(
                instance, touch, "박스 입수량 입력", True
            )
        )
        input_grid.add_widget(self.box_size_input)

        input_grid.add_widget(
            Label(text="박스 수량:", font_name=FONT_NAME, font_size=dp(14))
        )
        self.box_count_input = TextInput(
            hint_text="0",
            multiline=False,
            input_type="number",
            font_name=FONT_NAME,
            font_size=dp(18),
            halign="center",
            readonly=True,
        )
        self.box_count_input.bind(
            on_touch_down=lambda instance, touch: self._touch_input(
                instance, touch, "박스 수량 입력", True
            )
        )
        input_grid.add_widget(self.box_count_input)

        input_grid.add_widget(
            Label(text="낱개 수량:", font_name=FONT_NAME, font_size=dp(14))
        )
        self.rem_qty_input = TextInput(
            hint_text="0",
            multiline=False,
            input_type="number",
            font_name=FONT_NAME,
            font_size=dp(18),
            halign="center",
            readonly=True,
        )
        self.rem_qty_input.bind(
            on_touch_down=lambda instance, touch: self._touch_input(
                instance, touch, "낱개 수량 입력", True
            )
        )
        input_grid.add_widget(self.rem_qty_input)

        main_layout.add_widget(input_grid)

        loc_box = BoxLayout(
            orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(80)
        )
        
        lbl_target = Label(
            text=f"목표 적치위치: [color=1E88E5][b]{self.target_location}[/b][/color]",
            font_name=FONT_NAME,
            font_size=dp(14),
            markup=True,
            size_hint_y=None,
            height=dp(22),
            halign="left",
        )
        lbl_target.bind(size=lambda i, s: setattr(i, "text_size", s))
        loc_box.add_widget(lbl_target)

        loc_input_row = BoxLayout(
            orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(45)
        )

        self.final_location_input = TextInput(
            hint_text="로케이션 QR 스캔 시 자동 완결",
            multiline=False,
            font_name=FONT_NAME,
            font_size=dp(15),
            size_hint_x=0.7,
            readonly=True,
        )
        self.final_location_input.bind(
            on_touch_down=lambda instance, touch: self._touch_input(
                instance, touch, "로케이션 QR/바코드 수기입력", False
            )
        )
        loc_input_row.add_widget(self.final_location_input)

        btn_no_qr = StyledButton(
            text="QR없음",
            size_hint_x=0.3,
            font_size=dp(13),
            bg_color=get_color_from_hex("#E65100"),
        )
        btn_no_qr.bind(on_press=self.process_no_qr_action)
        loc_input_row.add_widget(btn_no_qr)

        loc_box.add_widget(loc_input_row)
        main_layout.add_widget(loc_box)

        top_button_grid = GridLayout(
            cols=2, size_hint_y=None, height=dp(50), spacing=dp(10)
        )
        cancel_button = StyledButton(text="취소", bg_color=(0.6, 0.6, 0.6, 1))
        cancel_button.bind(on_press=self.dismiss)
        ok_button = StyledButton(
            text="검수 완료 (수기입력용)", bg_color=get_color_from_hex("#00897B")
        )
        ok_button.bind(on_press=self.confirm_inspection)

        top_button_grid.add_widget(cancel_button)
        top_button_grid.add_widget(ok_button)
        main_layout.add_widget(top_button_grid)

        self.content = main_layout

    def _touch_input(self, instance, touch, title, is_num):
        if instance.collide_point(*touch.pos):
            def set_val(val):
                instance.text = str(val).strip().upper()
                if not is_num:
                    self.process_location_scan(instance.text)

            open_native_korean_input(title, title, instance.text, set_val, is_number=is_num)
            return True
        return False

    def process_no_qr_action(self, instance):
        app = App.get_running_app()

        box_size_str = self.box_size_input.text.strip()
        box_count_str = self.box_count_input.text.strip() or "0"
        rem_qty_str = self.rem_qty_input.text.strip() or "0"

        if not box_size_str.isdigit() or not box_count_str.isdigit() or not rem_qty_str.isdigit():
            app.show_info_popup("입력 오류", "수량을 올바르게 입력해주세요.")
            return

        box_size = int(box_size_str)
        box_count = int(box_count_str)
        rem_qty = int(rem_qty_str)

        calculated_total_qty = (box_size * box_count) + rem_qty

        if calculated_total_qty <= 0:
            app.show_info_popup(
                "수량 입력 필요",
                "수량이 입력되지 않았습니다!\n\n박스 수량 또는 낱개 수량을 먼저 입력해 주세요.",
            )
            return

        self.card.changed_box_size = box_size_str
        self.task_data["changed_box_size"] = box_size_str

        target_qty = safe_int(t(self.task_data, "지시수량", 0))
        if calculated_total_qty != target_qty:
            def proceed_no_qr():
                self._execute_no_qr_finalize(calculated_total_qty)

            app.show_confirmation_popup(
                title="[수량 이슈 경고]",
                message=(
                    f"지시수량: [color=FF8A80][b]{target_qty}개[/b][/color]\n"
                    f"검수수량: [color=81C784][b]{calculated_total_qty}개[/b][/color]\n\n"
                    f"수량이 일치하지 않습니다!\n다시 한번 확인 후 진행해주세요."
                ),
                on_yes=proceed_no_qr
            )
            return

        self._execute_no_qr_finalize(calculated_total_qty)

    # 💡 [핵심] 누락되었던 누락 QR 수기 완결 메서드 구현 (튕김 및 먹통 원인 차단)
    def _execute_no_qr_finalize(self, calculated_total_qty):
        # QR이 없어 목표 위치로 자동 기록 및 비고에 [QR없음 적치] 사유 자동 기재
        final_loc = self.target_location
        no_qr_remark = "[자석로케이션 필요]"
        
        curr_rem = str(self.current_remarks).strip()
        updated_rem = f"{curr_rem}\n{no_qr_remark}" if curr_rem else no_qr_remark

        self.task_list_screen._finalize_task_processing(
            card=self.card,
            final_qty=calculated_total_qty,
            split_qty=0,
            final_location=final_loc,
            updated_remarks=updated_rem,
        )
        self.dismiss()

    def process_location_scan(self, scanned_location):
        app = App.get_running_app()

        raw_loc = str(scanned_location).replace('\ufeff', '').strip()
        scanned_loc = re.sub(r'[^A-Za-z0-9\-_]', '', raw_loc).strip().upper()

        box_size_str = self.box_size_input.text.strip()
        box_count_str = self.box_count_input.text.strip() or "0"
        rem_qty_str = self.rem_qty_input.text.strip() or "0"

        if not box_size_str.isdigit() or not box_count_str.isdigit() or not rem_qty_str.isdigit():
            app.show_info_popup("입력 오류", "수량을 올바르게 입력해주세요.")
            return False

        box_size = int(box_size_str)
        box_count = int(box_count_str)
        rem_qty = int(rem_qty_str)

        calculated_total_qty = (box_size * box_count) + rem_qty

        if calculated_total_qty <= 0:
            app.show_info_popup(
                "수량 입력 필요",
                "수량이 입력되지 않았습니다!\n\n박스 수량 또는 낱개 수량을 먼저 입력한 뒤\n로케이션 QR을 스캔해 주세요.",
            )
            return False

        self.card.changed_box_size = box_size_str
        self.task_data["changed_box_size"] = box_size_str

        self.final_location_input.text = scanned_loc

        if scanned_loc != self.target_location:
            loc_msg = (
                f"[color=FF8A80][b]스캔한 로케이션이 일치하지 않습니다![/b][/color]\n\n"
                f"• 올바른 적치 위치:\n"
                f"[size=22dp][color=64B5F6][b]{self.target_location}[/b][/color][/size]\n\n"
                f"• 현재 스캔 위치:\n"
                f"[color=FF5252][b]{scanned_loc}[/b][/color]\n\n"
                f"지정된 올바른 위치에 적치 후 다시 스캔해 주세요."
            )
            app.show_info_popup("[로케이션 오류]", loc_msg)
            return False

        target_qty = safe_int(t(self.task_data, "지시수량", 0))
        if calculated_total_qty != target_qty:
            def proceed_scan_finalize():
                self._execute_scan_finalize(calculated_total_qty, scanned_loc)

            app.show_confirmation_popup(
                title="[수량 이슈 경고]",
                message=(
                    f"지시수량: [color=FF8A80][b]{target_qty}개[/b][/color]\n"
                    f"검수수량: [color=81C784][b]{calculated_total_qty}개[/b][/color]\n\n"
                    f"수량이 일치하지 않습니다!\n이대로 검수 완료하시겠습니까?"
                ),
                on_yes=proceed_scan_finalize
            )
            return False

        self._execute_scan_finalize(calculated_total_qty, scanned_loc)
        return True

    def _execute_scan_finalize(self, calculated_total_qty, scanned_loc):
        self.task_list_screen._finalize_task_processing(
            card=self.card,
            final_qty=calculated_total_qty,
            split_qty=0,
            final_location=scanned_loc,
            updated_remarks=self.current_remarks,
        )
        self.dismiss()

    def confirm_inspection(self, instance):
        scanned_location = self.final_location_input.text.strip().upper()
        if not scanned_location:
            App.get_running_app().show_info_popup("스캔 필요", "적치할 로케이션 QR/바코드를 스캔해 주세요.")
            return
        self.process_location_scan(scanned_location)

class NameEntryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation="vertical", padding=dp(30), spacing=dp(15)
        )

        layout.add_widget(
            Label(
                text="보충 업무 자동화",
                font_name=FONT_NAME,
                font_size=dp(28),
                bold=True,
                color=PRIMARY_BLUE,
                size_hint_y=0.2,
            )
        )

        layout.add_widget(
            Label(
                text=f"App Version: v{CURRENT_VERSION}",
                font_name=FONT_NAME,
                font_size=dp(13),
                color=TEXT_MUTED,
                size_hint_y=0.1,
            )
        )

        input_box = BoxLayout(
            orientation="vertical", spacing=dp(10), size_hint_y=0.3
        )
        input_box.add_widget(
            Label(
                text="작업자 이름을 입력해주세요",
                font_name=FONT_NAME,
                font_size=dp(16),
                color=TEXT_DARK,
            )
        )
        self.name_input = TextInput(
            hint_text="터치하여 이름 입력",
            multiline=False,
            font_name=FONT_NAME,
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            halign="center",
            readonly=True,
        )
        self.name_input.bind(on_touch_down=self.on_input_touch)
        input_box.add_widget(self.name_input)

        start_btn = StyledButton(
            text="작업 시작하기", size_hint_y=None, height=dp(55)
        )
        start_btn.bind(on_press=self.start_app)

        layout.add_widget(input_box)
        layout.add_widget(start_btn)
        layout.add_widget(Widget(size_hint_y=0.2))
        self.add_widget(layout)

    def on_input_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def set_name(val):
                if val.strip():
                    self.name_input.text = val.strip()

            open_native_korean_input(
                "작업자 이름 입력", "이름을 입력하세요", self.name_input.text, set_name
            )
            return True
        return False

    def on_enter(self, *args):
        app = App.get_running_app()
        saved_name = app.load_saved_user_name()
        if saved_name:
            self.name_input.text = saved_name

    def start_app(self, instance):
        name = self.name_input.text.strip()
        if not name:
            App.get_running_app().show_info_popup(
                "알림", "이름을 입력해야 합니다."
            )
            return
        app = App.get_running_app()

        if app.user_real_name and app.user_real_name != name:
            clear_recent_history_file()

        app.user_real_name = name
        app.save_user_name(name)
        self.manager.current = "main_menu"


class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(6)
        )
        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.layout.clear_widgets()
        app = App.get_running_app()

        # 1. 상단 인삿말 & 프린터 버튼 (기존 유지)
        top_bar = BoxLayout(size_hint_y=None, height=dp(40))
        welcome_box = BoxLayout(orientation="vertical", size_hint_x=0.75)
        welcome_box.add_widget(
            Label(
                text=f'"{app.user_real_name}"님',
                font_name=FONT_NAME,
                font_size=dp(18),
                bold=True,
                color=PRIMARY_BLUE,
                halign="left",
            )
        )
        welcome_box.add_widget(
            Label(
                text="오늘도 안전 작업하세요!",
                font_name=FONT_NAME,
                font_size=dp(13),
                color=TEXT_MUTED,
                halign="left",
            )
        )
        for child in welcome_box.children:
            child.bind(size=lambda i, s: setattr(i, "text_size", s))

        btn_printer = StyledButton(
            text="프린터",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(12),
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_printer.bind(
            on_press=lambda x: Factory.PrinterSettingsPopup().open()
        )

        top_bar.add_widget(welcome_box)
        top_bar.add_widget(btn_printer)
        self.layout.add_widget(top_bar)

        # 2. 실시간 보충 현황 요약 카드 (기존 유지)
        dash_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(125),
            padding=dp(8),
            spacing=dp(3),
        )
        with dash_card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=dash_card.pos, size=dash_card.size, radius=[dp(12)]
            )
        dash_card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        lbl_dash_title = Label(
            text="📊 실시간 보충 현황 요약",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            color=PRIMARY_BLUE,
            size_hint_y=None,
            height=dp(20),
            halign="left",
        )
        lbl_dash_title.bind(size=lambda i, s: setattr(i, "text_size", s))
        dash_card.add_widget(lbl_dash_title)

        grid = GridLayout(cols=3, spacing=dp(2))
        grid.add_widget(
            Label(
                text="구분",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )
        grid.add_widget(
            Label(
                text="대기중 (긴급)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )
        grid.add_widget(
            Label(
                text="작업중 (긴급)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )

        self.lbl_op_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_op_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid.add_widget(
            Label(
                text="오더피커",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid.add_widget(self.lbl_op_pending)
        grid.add_widget(self.lbl_op_working)

        self.lbl_reach_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_reach_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid.add_widget(
            Label(
                text="리치",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid.add_widget(self.lbl_reach_pending)
        grid.add_widget(self.lbl_reach_working)

        dash_card.add_widget(grid)

        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(0.85, 0.85, 0.85, 1)
            rect = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(
            pos=lambda i, p: setattr(rect, "pos", p),
            size=lambda i, s: setattr(rect, "size", s),
        )
        dash_card.add_widget(sep)

        grid_tot = GridLayout(
            cols=3, size_hint_y=None, height=dp(23), spacing=dp(2)
        )
        self.lbl_all_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_all_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid_tot.add_widget(
            Label(
                text="전체합계",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid_tot.add_widget(self.lbl_all_pending)
        grid_tot.add_widget(self.lbl_all_working)
        dash_card.add_widget(grid_tot)

        self.layout.add_widget(dash_card)

        # 3. 누적 처리량 정보 카드 (기존 유지)
        perf_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(64),
            padding=(dp(10), dp(4)),
            spacing=dp(2),
        )
        with perf_card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=perf_card.pos, size=perf_card.size, radius=[dp(10)]
            )
        perf_card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        load_recent_history()
        user_name_lower = str(app.user_real_name).strip().lower()

        all_sheet_tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=False)
        op_count = 0
        rc_count = 0

        for task in all_sheet_tasks:
            st = str(t(task, "상태")).strip()
            worker = str(t(task, "보충담당자", t(task, "작업 담당자", ""))).strip().lower()
            eq = str(t(task, "장비")).strip()

            if st in ["적치대기", "최종완료", "완료"] and worker == user_name_lower:
                if eq == "리치":
                    rc_count += 1
                else:
                    op_count += 1

        tot_my_count = op_count + rc_count

        now = datetime.now()
        if now.hour < 4:
            shift_start = (now - timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
        elif now.hour >= 18:
            shift_start = now.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            shift_start = now.replace(hour=9, minute=0, second=0, microsecond=0)

        elapsed_seconds = (now - shift_start).total_seconds()
        if elapsed_seconds <= 0:
            elapsed_hours = 0.5
        else:
            elapsed_hours = max(0.5, elapsed_seconds / 3600.0)

        op_pace = round(op_count / elapsed_hours, 1)

        self.lbl_title_row = Label(
            text=f"▶ [b]{app.user_real_name}님의 오늘 누적 처리량 : 총 {tot_my_count}건[/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=PRIMARY_BLUE,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_title_row.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_title_row)

        if op_pace < 30.0:
            op_msg = f"{op_pace}개/h (목표30) [color=E65100]● 속도 UP!💪[/color]"
        elif op_pace <= 34.0:
            op_msg = f"{op_pace}개/h (목표30) [color=2E7D32]● 훌륭해요!👏[/color]"
        else:
            op_msg = f"{op_pace}개/h (목표30) [color=D32F2F]★ 최고의 속도!⭐[/color]"

        self.lbl_row1 = Label(
            text=f"   ■ 오더피커: {op_count}건 │ {op_msg}",
            font_name=FONT_NAME,
            font_size=dp(10),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_row1.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_row1)

        self.lbl_row2 = Label(
            text=f"   ■ 리    치: {rc_count}건 │ --개/h (목표 미정) [color=757575]● 기준 미설정[/color]",
            font_name=FONT_NAME,
            font_size=dp(10),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_row2.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_row2)

        self.layout.add_widget(perf_card)

        # 💡 [수정 구역] 메인 버튼들 6개 ( 한 줄에 2개씩 2열 GridLayout 적용 )
        menu_grid = GridLayout(
            cols=2,
            spacing=dp(6),
            size_hint_y=None,
            height=dp(140)  # 3행 2열 높이에 맞춰 최적화
        )

        btn_replenish = StyledButton(
            text="[보충] 보충 작업",
            bg_color=PRIMARY_BLUE,
            font_size=dp(12),
        )
        btn_replenish.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "unified_replenish"
            )
        )

        # 💡 [신규 추가] 원복 작업 버튼 생성
        btn_return = StyledButton(
            text="[원복] 원복 작업",
            bg_color=get_color_from_hex("#2E7D32"),  # 주황색 계열로 확연한 구분
            font_size=dp(12),
        )
        btn_return.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "return_task_list"
            )
        )

        btn_inspect = StyledButton(
            text="[검수] 검수 목록 보기",
            bg_color=get_color_from_hex("#00897B"),
            font_size=dp(12),
        )
        btn_inspect.bind(on_press=self.go_to_inspect)

        btn_dashboard = StyledButton(
            text="[현황] 전체 작업 현황판",
            bg_color=get_color_from_hex("#3F51B5"),
            font_size=dp(12),
        )
        btn_dashboard.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "admin_dashboard"
            )
        )

        btn_emergency = StyledButton(
            text="보충 요청",
            bg_color=get_color_from_hex("#D32F2F"),
            font_size=dp(12),
        )
        btn_emergency.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "emergency_replenish"
            )
        )

        btn_sku_loc = StyledButton(
            text="SKU별 로케이션 검색",
            bg_color=get_color_from_hex("#E65100"),
            font_size=dp(11),
        )
        btn_sku_loc.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "sku_location_search"
            )
        )

        btn_recent = StyledButton(
            text="금일 완료 이력 (최근)",
            bg_color=get_color_from_hex("#43A047"),
            font_size=dp(11),
        )
        btn_recent.bind(on_press=lambda x: RecentCompletedPopup.open_safely())

        # 버튼 6개 순서대로 추가
        menu_grid.add_widget(btn_replenish)
        menu_grid.add_widget(btn_return)
        menu_grid.add_widget(btn_inspect)
        menu_grid.add_widget(btn_dashboard)
        menu_grid.add_widget(btn_emergency)
        menu_grid.add_widget(btn_sku_loc)
        menu_grid.add_widget(btn_recent)

        self.layout.add_widget(menu_grid)

        # 💡 버튼들과 하단 이름 변경 버튼 사이의 유격 확보
        self.layout.add_widget(Widget())

        # 4. 하단 우측 작업자 이름 변경 버튼 (기존 위치 및 여백 유지)
        bottom_box = BoxLayout(size_hint_y=None, height=dp(34))
        bottom_box.add_widget(Widget())  # 왼쪽 빈 공간 밀어내기
        change_btn = StyledButton(
            text="작업자 이름 변경",
            size_hint_x=None,
            width=dp(130),
            bg_color=get_color_from_hex("#FF7043"),
            font_size=dp(11),
        )
        change_btn.bind(
            on_press=lambda x: setattr(self.manager, "current", "name_entry")
        )
        bottom_box.add_widget(change_btn)
        self.layout.add_widget(bottom_box)

        # 백그라운드 데이터 로드
        threading.Thread(
            target=self._fetch_summary_counts, daemon=True
        ).start()

    def _fetch_summary_counts(self):
        try:
            tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=False)
            op_p, op_pu, op_w, op_wu = 0, 0, 0, 0
            rc_p, rc_pu, rc_w, rc_wu = 0, 0, 0, 0

            for task in tasks:
                st = str(t(task, "상태")).strip()
                eq = str(t(task, "장비")).strip()
                is_urg = t(task, "긴급여부") == "Y"

                if st == "대기":
                    if eq == "오더피커":
                        op_p += 1
                        if is_urg:
                            op_pu += 1
                    elif eq == "리치":
                        rc_p += 1
                        if is_urg:
                            rc_pu += 1
                elif st == "작업중":
                    if eq == "오더피커":
                        op_w += 1
                        if is_urg:
                            op_wu += 1
                    elif eq == "리치":
                        rc_w += 1
                        if is_urg:
                            rc_wu += 1

            tot_p, tot_pu = op_p + rc_p, op_pu + rc_pu
            tot_w, tot_wu = op_w + rc_w, op_wu + rc_wu

            Clock.schedule_once(
                lambda dt: self._update_summary_labels(
                    f"{op_p} [color=D32F2F]({op_pu})[/color]",
                    f"{op_w} [color=D32F2F]({op_wu})[/color]",
                    f"{rc_p} [color=D32F2F]({rc_pu})[/color]",
                    f"{rc_w} [color=D32F2F]({rc_wu})[/color]",
                    f"{tot_p} [color=D32F2F]({tot_pu})[/color]",
                    f"{tot_w} [color=D32F2F]({tot_wu})[/color]",
                )
            )
        except Exception:
            pass

    def _update_summary_labels(self, op_p, op_w, rc_p, rc_w, tot_p, tot_w):
        if hasattr(self, "lbl_op_pending") and self.lbl_op_pending.parent:
            self.lbl_op_pending.text = op_p
            self.lbl_op_working.text = op_w
            self.lbl_reach_pending.text = rc_p
            self.lbl_reach_working.text = rc_w
            self.lbl_all_pending.text = tot_p
            self.lbl_all_working.text = tot_w

    def go_to_inspect(self, instance):
        app = App.get_running_app()
        app.current_list_type = "검수인원"
        self.manager.current = "task_list"


class SkuLocationSearchScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw_inventory = []
        self.layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )

        top_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        top_bar.add_widget(
            StyledButton(
                text="< 메인",
                size_hint_x=0.2,
                bg_color=get_color_from_hex("#78909C"),
                on_press=lambda x: setattr(
                    self.manager, "current", "main_menu"
                ),
            )
        )
        top_bar.add_widget(
            Label(
                text="SKU별 로케이션 검색",
                font_name=FONT_NAME,
                font_size=dp(18),
                bold=True,
                color=TEXT_DARK,
            )
        )
        top_bar.add_widget(
            StyledButton(
                text="갱신", size_hint_x=0.2, on_press=lambda x: self.refresh()
            )
        )
        self.layout.add_widget(top_bar)

        search_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="터치하여 바코드 스캔/입력",
            multiline=False,
            font_name=FONT_NAME,
            font_size=dp(15),
            size_hint_x=0.8,
            readonly=True,
        )
        self.search_input.bind(on_touch_down=self.on_search_touch)

        btn_search = StyledButton(
            text="검색", size_hint_x=0.2, font_size=dp(14)
        )
        btn_search.bind(on_press=self.search_location)

        search_bar.add_widget(self.search_input)
        search_bar.add_widget(btn_search)
        self.layout.add_widget(search_bar)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_search_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def set_query(val):
                self.search_input.text = val
                self.search_location()

            open_native_korean_input(
                "바코드 입력", "바코드를 스캔하거나 입력하세요", "", set_query
            )
            return True
        return False

    def on_enter(self):
        app = App.get_running_app()
        if not app.user_real_name:
            app.user_real_name = app.load_saved_user_name() or ""
            if not app.user_real_name:
                self.manager.current = "name_entry"
                return

        self.search_input.text = ""
        self.grid.clear_widgets()
        self.grid.add_widget(
            Label(
                text="바코드를 스캔하면 점유 로케이션이 표로 나옵니다.",
                font_name=FONT_NAME,
                font_size=dp(15),
                color=TEXT_MUTED,
                size_hint_y=None,
                height=dp(100),
            )
        )

        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_inventory, daemon=True).start()

    def refresh(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_inventory, daemon=True).start()

    def _async_fetch_inventory(self):
        try:
            data = get_sheet_data(LOCATION_CAPA_SHEET_NAME, force_refresh=True)
            self.raw_inventory = data
            Clock.schedule_once(lambda dt: self.search_location())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", f"재고 시트 로드 실패: {err}"
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def handle_barcode_scan(self, barcode):
        self.search_input.text = str(barcode).strip()
        self.search_location()

    def search_location(self, instance=None):
        query = self.search_input.text.strip().lower()
        self.grid.clear_widgets()

        if not query:
            self.grid.add_widget(
                Label(
                    text="바코드를 스캔하면 점유 로케이션이 표로 나옵니다.",
                    font_name=FONT_NAME,
                    font_size=dp(15),
                    color=TEXT_MUTED,
                    size_hint_y=None,
                    height=dp(100),
                )
            )
            return

        grouped_results = defaultdict(list)
        for row in self.raw_inventory:
            bc = str(t(row, "바코드", t(row, "상품바코드", ""))).strip()
            sku = str(t(row, "SKU", t(row, "상품명", ""))).strip()

            if query in bc.lower() or query in sku.lower():
                grouped_results[bc].append(row)

        if not grouped_results:
            self.grid.add_widget(
                Label(
                    text=f"검색어 [{query}] 에 해당하는 로케이션 재고가 없습니다.",
                    font_name=FONT_NAME,
                    font_size=dp(14),
                    color=TEXT_MUTED,
                    size_hint_y=None,
                    height=dp(100),
                )
            )
            return

        for bc, rows in grouped_results.items():
            self.grid.add_widget(self._create_grouped_table_card(bc, rows))

    def _create_grouped_table_card(self, barcode, rows):
        sku_name = str(t(rows[0], "SKU", t(rows[0], "상품명", "N/A"))).strip()
        tot_qty = sum(safe_int(t(r, "로케이션 수량", 0)) for r in rows)

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(6),
        )

        table_height = dp(45) + dp(25) + (len(rows) * dp(22)) + dp(24)
        card.height = table_height

        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=card.pos, size=card.size, radius=[dp(10)]
            )
        card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        lbl_sku = Label(
            text=f"[b]{sku_name}[/b]",
            font_name=FONT_NAME,
            font_size=dp(14),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(22),
        )
        lbl_sku.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_sku)

        lbl_bc_tot = Label(
            text=f"바코드: [b][color=1E88E5]{barcode}[/color][/b]  |  총 재고: [b][color=D32F2F]{tot_qty}개[/color][/b]",
            font_name=FONT_NAME,
            font_size=dp(13),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        lbl_bc_tot.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_bc_tot)

        table_grid = GridLayout(cols=3, size_hint_y=None, spacing=dp(1))
        table_grid.height = dp(25) + (len(rows) * dp(22))

        th_type = Label(
            text="[b]유형[/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=get_color_from_hex("#37474F"),
            markup=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(25),
        )
        with th_type.canvas.before:
            Color(0.9, 0.93, 0.95, 1)
            Rectangle(pos=th_type.pos, size=th_type.size)
        th_type.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        th_loc = Label(
            text="[b]로케이션[/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=get_color_from_hex("#37474F"),
            markup=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(25),
        )
        with th_loc.canvas.before:
            Color(0.9, 0.93, 0.95, 1)
            Rectangle(pos=th_loc.pos, size=th_loc.size)
        th_loc.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        th_qty = Label(
            text="[b]수량[/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=get_color_from_hex("#37474F"),
            markup=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(25),
        )
        with th_qty.canvas.before:
            Color(0.9, 0.93, 0.95, 1)
            Rectangle(pos=th_qty.pos, size=th_qty.size)
        th_qty.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        table_grid.add_widget(th_type)
        table_grid.add_widget(th_loc)
        table_grid.add_widget(th_qty)

        for idx, r in enumerate(rows):
            loc_type_str = str(t(r, "로케이션 유형", t(r, "로케이션유형", "-"))).strip()
            loc_str = str(t(r, "로케이션", "N/A")).strip()
            qty_val = safe_int(t(r, "로케이션 수량", 0))

            bg_color = (0.97, 0.97, 0.97, 1) if idx % 2 == 1 else (1, 1, 1, 1)

            td_type = Label(
                text=f"{loc_type_str}",
                font_name=FONT_NAME,
                font_size=dp(11),
                color=TEXT_MUTED,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(22),
            )
            with td_type.canvas.before:
                Color(*bg_color)
                Rectangle(pos=td_type.pos, size=td_type.size)
            td_type.bind(
                pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
                size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
            )

            td_loc = Label(
                text=f"[b][color=D32F2F]{loc_str}[/color][/b]",
                font_name=FONT_NAME,
                font_size=dp(12),
                markup=True,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(22),
            )
            with td_loc.canvas.before:
                Color(*bg_color)
                Rectangle(pos=td_loc.pos, size=td_loc.size)
            td_loc.bind(
                pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
                size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
            )

            td_qty = Label(
                text=f"[b][color=1E88E5]{qty_val} 개[/color][/b]",
                font_name=FONT_NAME,
                font_size=dp(12),
                markup=True,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(22),
            )
            with td_qty.canvas.before:
                Color(*bg_color)
                Rectangle(pos=td_qty.pos, size=td_qty.size)
            td_qty.bind(
                pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
                size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
            )

            table_grid.add_widget(td_type)
            table_grid.add_widget(td_loc)
            table_grid.add_widget(td_qty)

        card.add_widget(table_grid)
        return card


# --- 통합 보충 작업 카드 뷰어 ---
class UnifiedTaskCard(RecycleDataViewBehavior, BoxLayout):
    index = NumericProperty(0)
    task_data = DictProperty({})
    is_claimed = BooleanProperty(False)
    is_checked = BooleanProperty(False)
    card_screen = ObjectProperty(None)
    card_bg_color = ListProperty([1, 1, 1, 1])

    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        self.index = index
        self.task_data = data.get("task_data", {})
        self.is_claimed = data.get("is_claimed", False)
        self.is_checked = data.get("is_checked", False)
        self.card_screen = data.get("card_screen", None)

        is_urgent = self.task_data.get("긴급여부") == "Y"
        shelf_val = str(
            t(
                self.task_data,
                "선반렉 여부",
                t(
                    self.task_data,
                    "선반랙 여부",
                    t(self.task_data, "선반렉", t(self.task_data, "선반랙", "")),
                ),
            )
        ).strip().upper()
        is_shelf_rack = (shelf_val == "Y") or ("선반" in shelf_val)

        if is_urgent:
            self.card_bg_color = get_color_from_hex("#FFCDD2")
        elif is_shelf_rack:
            self.card_bg_color = get_color_from_hex("#E3F2FD")
        else:
            self.card_bg_color = [1, 1, 1, 1]

        raw_equip = str(t(self.task_data, "장비", ""))
        if raw_equip == "리치":
            display_tag = "[color=0000FF][리치][/color]"
        elif raw_equip == "오더피커":
            display_tag = "[color=1E88E5][오더피커][/color]"
        else:
            display_tag = ""

        client_name = str(t(self.task_data, "고객사", t(self.task_data, "화주사", ""))).strip()
        client_tag = f" [color=555555][{client_name}][/color]" if client_name else ""

        self.ids.lbl_equip.text = f"[b]{display_tag}{client_tag}[/b]"

        existing_qty = safe_int(t(self.task_data, "기존수량", 0))
        req_qty = safe_int(t(self.task_data, "지시수량", 0))
        remaining_qty = existing_qty - req_qty
        self.ids.lbl_stock_info.text = f"기존: [b]{existing_qty}[/b]\n보충후: [b][color=1E88E5]{remaining_qty}[/color][/b]"

        qty_per_box = safe_int(
            t(self.task_data, "박스입수량", t(self.task_data, "박스 입수량", 0))
        )
        product_name = str(t(self.task_data, "상품명", t(self.task_data, "SKU명", "N/A")))
        
        is_invoice_only = (qty_per_box == 1) or ("(송장만부착)" in product_name) or ("송장" in product_name)
        is_inbox = str(t(self.task_data, "인박스여부", "")).strip().upper() == "Y"

        tag_prefix = ""
        if is_urgent:
            tag_prefix += "[color=D32F2F][긴급][/color] "
        if is_shelf_rack:
            tag_prefix += "[color=1565C0][선반렉][/color] "

        self.ids.lbl_product.text = f"[b]{tag_prefix}{product_name}[/b]"
        self.ids.lbl_barcode.text = f"바코드: {get_barcode_from_task(self.task_data)}"

        from_loc = str(t(self.task_data, "기존로케이션", "-"))
        to_loc = str(t(self.task_data, "보충로케이션", "-"))
        self.ids.lbl_loc.text = (
            f"[color=D32F2F]{from_loc}[/color] ➔ [color=1E88E5]{to_loc}[/color]"
        )

        conf_qty_val = self.task_data.get("confirmed_quantity", t(self.task_data, "확인수량", ""))
        active_count = safe_int(conf_qty_val, 0) if str(conf_qty_val).isdigit() else 0

        target_box_ea_calc = (
            f"({req_qty // qty_per_box}B / {req_qty % qty_per_box}E)"
            if qty_per_box > 0
            else f"({req_qty}E)"
        )

        if self.is_claimed:
            self.ids.lbl_main_qty.text = f"지시: {req_qty} / [color=D32F2F]{active_count}[/color] [color=1E88E5]{target_box_ea_calc}[/color]"
        else:
            self.ids.lbl_main_qty.text = f"지시: [b]{req_qty}[/b] [color=1E88E5]{target_box_ea_calc}[/color]"

        if is_invoice_only:
            box_notice_str = f"박스입수: {qty_per_box}  [color=FF1744][b](박스 수기작성 금지 - 단품/송장전용)[/b][/color]"
        else:
            box_notice_str = f"박스입수: {qty_per_box}"

        if is_inbox:
            box_notice_str += "  [color=D32F2F][b][인박스 확인 필요][/b][/color]"

        self.ids.lbl_box_info.text = box_notice_str

        self.ids.box_check.opacity = 1
        self.ids.box_check.disabled = False
        self.ids.box_check.active = self.is_checked

        # 💡 [핵심] 수량입력 버튼 동적 제어 로직
        is_no_barcode_sku = product_name.strip().startswith("★")
        has_qty_entered = str(conf_qty_val).strip().isdigit() and int(str(conf_qty_val).strip()) > 0
        is_manual_unlocked = self.task_data.get("manual_qty_unlocked", False)

        can_show_qty_btn = is_no_barcode_sku or has_qty_entered or is_manual_unlocked

        if self.is_claimed:
            self.ids.btn_action_box.height = dp(40)
            self.ids.btn_action_box.opacity = 1
            self.ids.btn_action_box.disabled = False

            if can_show_qty_btn:
                self.ids.btn_qty_input.text = "수량입력"
                self.ids.btn_qty_input.set_bg_color(PRIMARY_BLUE)
            else:
                self.ids.btn_qty_input.text = "스캔불가"
                self.ids.btn_qty_input.set_bg_color(get_color_from_hex("#78909C"))
        else:
            self.ids.btn_action_box.height = 0
            self.ids.btn_action_box.opacity = 0
            self.ids.btn_action_box.disabled = True

    def on_checkbox_active(self, checkbox, value):
        if self.card_screen:
            self.card_screen.toggle_card_check(self.task_data, value)

    def handle_card_btn(self, action_name):
        if self.card_screen:
            product_name = str(t(self.task_data, "상품명", t(self.task_data, "SKU명", ""))).strip()
            is_no_barcode_sku = product_name.startswith("★")
            conf_q_val = str(self.task_data.get("confirmed_quantity", t(self.task_data, "확인수량", ""))).strip()
            has_qty_entered = conf_q_val.isdigit() and int(conf_q_val) > 0
            is_manual_unlocked = self.task_data.get("manual_qty_unlocked", False)

            can_show_qty_btn = is_no_barcode_sku or has_qty_entered or is_manual_unlocked

            if action_name == "qty":
                if can_show_qty_btn:
                    self.card_screen.handle_my_task_action("qty", self.task_data)
                else:
                    self._prompt_scan_fallback()
            else:
                self.card_screen.handle_my_task_action(action_name, self.task_data)

    def _prompt_scan_fallback(self):
        app = App.get_running_app()

        def on_confirm_fallback(reason):
            clean_reason = reason.strip()
            if not clean_reason:
                return

            # 1. 시간 및 사유 포맷팅
            ts = datetime.now().strftime("%H:%M")
            formatted_entry = f"[{ts} 스캔불가사유: {clean_reason}]"

            # 2. 기존 비고 가져와서 병합
            curr_rem = str(
                self.task_data.get("remarks_text", t(self.task_data, "비고", ""))
            ).strip()
            updated_remarks = (
                f"{curr_rem}\n{formatted_entry}" if curr_rem else formatted_entry
            )

            # 3. 로컬 메모리 동기화 및 수량입력 버튼 잠금 해제
            self.task_data["manual_qty_unlocked"] = True
            self.task_data["remarks_text"] = updated_remarks
            self.task_data["비고"] = updated_remarks

            if self.card_screen and hasattr(self.card_screen, "raw_all_tasks"):
                task_id = t(self.task_data, "작업ID")
                for task in self.card_screen.raw_all_tasks:
                    if t(task, "작업ID") == task_id:
                        task["manual_qty_unlocked"] = True
                        task["remarks_text"] = updated_remarks
                        task["비고"] = updated_remarks
                        break

            # 4. 구글 시트 비고 실시간 비동기 업데이트
            task_id = str(t(self.task_data, "작업ID"))

            def _async_update_sheet_remarks():
                try:
                    sheet = get_worksheet(TASK_SHEET_NAME)
                    headers = [str(h).strip() for h in sheet.row_values(1)]
                    if "비고" in headers and "작업ID" in headers:
                        task_id_col = headers.index("작업ID") + 1
                        remarks_col = headers.index("비고") + 1

                        all_ids = sheet.col_values(task_id_col)
                        if task_id in all_ids:
                            row_idx = all_ids.index(task_id) + 1
                            sheet.update_cell(
                                row_idx, remarks_col, updated_remarks
                            )
                            invalidate_cache(TASK_SHEET_NAME)
                            print(
                                f"✅ 구글 시트 비고 실시간 업데이트 완료: {updated_remarks}"
                            )
                except Exception as e:
                    print(f"⚠️ 비고 실시간 시트 업데이트 에러: {e}")

            threading.Thread(
                target=_async_update_sheet_remarks, daemon=True
            ).start()

            app.show_toast("스캔불가 사유가 비고란에 기록되었습니다.")

            # 5. 수량 입력 팝업 즉시 열기
            self.card_screen.handle_my_task_action("qty", self.task_data)

        # 💡 스캔실패 사유 선택 팝업 오픈
        ScanFailureReasonPopup(on_select_callback=on_confirm_fallback).open()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            if app and app.root and app.root.current == "task_list":
                task_list_screen = app.root.get_screen("task_list")
                task_list_screen.open_task_from_scan({"task_data": self.task_data})
                return True
        return super().on_touch_down(touch)

# --- 올인원 통합 보충 작업 화면 ---
class UnifiedReplenishScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_main_tab = "PENDING"
        self.active_equip_filter = "ORDERPICKER"
        self.only_urgent = False
        self.selected_from_zones = {"전체"}
        self.selected_to_zones = {"전체"}
        self.sort_asc = True
        self.is_filter_expanded = True

        self.raw_all_tasks = []
        self.checked_task_ids = set()

        self.layout = BoxLayout(
            orientation="vertical", padding=dp(8), spacing=dp(4)
        )

        header = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        btn_back = StyledButton(
            text="< 뒤로",
            size_hint_x=0.18,
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_back.bind(
            on_press=lambda x: setattr(self.manager, "current", "main_menu")
        )

        lbl_title = Label(
            text="보충 작업 통합 컨트롤",
            font_name=FONT_NAME,
            font_size=dp(15),
            bold=True,
            color=TEXT_DARK,
        )

        btn_recent = StyledButton(
            text="최근완료",
            size_hint_x=0.22,
            font_size=dp(12),
            bg_color=get_color_from_hex("#43A047"),
        )
        btn_recent.bind(on_press=lambda x: RecentCompletedPopup.open_safely())

        btn_refresh = StyledButton(
            text="갱신", size_hint_x=0.18, font_size=dp(12)
        )
        btn_refresh.bind(on_press=self.refresh_button_click) # 💡 전용 갱신 버튼 이벤트 바인딩

        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_recent)
        header.add_widget(btn_refresh)
        self.layout.add_widget(header)

        self.btn_toggle_filter = StyledButton(
            text="🔍 필터 설정 닫기 ▲ (대기작업 / 오더피커)",
            size_hint_y=None,
            height=dp(32),
            bg_color=get_color_from_hex("#546E7A"),
            font_size=dp(12),
        )
        self.btn_toggle_filter.bind(on_press=self.toggle_filter_panel)
        self.layout.add_widget(self.btn_toggle_filter)

        self.filter_panel = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            spacing=dp(4),
        )

        main_tab_box = BoxLayout(
            size_hint_y=None, height=dp(36), spacing=dp(5)
        )
        self.btn_tab_pending = StyledToggleButton(
            text="대기 작업",
            group="main_tab",
            state="down",
            size_hint_x=0.5,
            font_size=dp(14),
            markup=True,
        )
        self.btn_tab_pending.bind(
            on_press=lambda x: self.switch_main_tab("PENDING")
        )

        self.btn_tab_my = StyledToggleButton(
            text="내 작업",
            group="main_tab",
            state="normal",
            size_hint_x=0.5,
            font_size=dp(14),
            markup=True,
        )
        self.btn_tab_my.bind(on_press=lambda x: self.switch_main_tab("MY"))

        main_tab_box.add_widget(self.btn_tab_pending)
        main_tab_box.add_widget(self.btn_tab_my)
        self.filter_panel.add_widget(main_tab_box)

        equip_filter_box = BoxLayout(
            size_hint_y=None, height=dp(32), spacing=dp(5)
        )

        self.btn_eq_op = StyledToggleButton(
            text="오더피커",
            group="equip_filter",
            state="down",
            font_size=dp(12),
        )
        self.btn_eq_op.bind(
            on_press=lambda x: self.switch_equip_filter("ORDERPICKER")
        )

        self.btn_eq_reach = StyledToggleButton(
            text="리치", group="equip_filter", state="normal", font_size=dp(12)
        )
        self.btn_eq_reach.bind(
            on_press=lambda x: self.switch_equip_filter("REACH")
        )

        self.btn_eq_all = StyledToggleButton(
            text="전체", group="equip_filter", state="normal", font_size=dp(12)
        )
        self.btn_eq_all.bind(
            on_press=lambda x: self.switch_equip_filter("ALL")
        )

        equip_filter_box.add_widget(self.btn_eq_op)
        equip_filter_box.add_widget(self.btn_eq_reach)
        equip_filter_box.add_widget(self.btn_eq_all)
        self.filter_panel.add_widget(equip_filter_box)

        opt_toolbar = BoxLayout(
            size_hint_y=None, height=dp(32), spacing=dp(3)
        )

        self.btn_from_zone = StyledButton(
            text="보관: 전체", size_hint_x=0.30, font_size=dp(11)
        )
        self.btn_from_zone.bind(on_press=self.open_from_zone_popup)

        self.btn_to_zone = StyledButton(
            text="이동: 전체", size_hint_x=0.30, font_size=dp(11)
        )
        self.btn_to_zone.bind(on_press=self.open_to_zone_popup)

        self.btn_sort = StyledButton(
            text="▲",
            size_hint_x=0.12,
            font_size=dp(12),
            bg_color=get_color_from_hex("#546E7A"),
        )
        self.btn_sort.bind(on_press=self.toggle_sort_order)

        chk_box = BoxLayout(size_hint_x=0.28, spacing=dp(2))
        self.chk_urgent = CheckBox(
            active=False, size_hint_x=None, width=dp(20), color=RETURN_GREEN
        )
        self.chk_urgent.bind(active=self.on_urgent_check_change)
        lbl_urg = Label(
            text="긴급만",
            font_name=FONT_NAME,
            font_size=dp(12),
            color=TEXT_DARK,
            halign="left",
            valign="middle",
        )
        lbl_urg.bind(size=lambda i, s: setattr(i, "text_size", s))

        chk_box.add_widget(self.chk_urgent)
        chk_box.add_widget(lbl_urg)
        opt_toolbar.add_widget(self.btn_from_zone)
        opt_toolbar.add_widget(self.btn_to_zone)
        opt_toolbar.add_widget(self.btn_sort)
        opt_toolbar.add_widget(chk_box)
        self.filter_panel.add_widget(opt_toolbar)

        self.layout.add_widget(self.filter_panel)

        list_header = BoxLayout(
            size_hint_y=None, height=dp(26), padding=(dp(5), 0)
        )
        self.lbl_status_count = Label(
            text="대기 작업 (오더피커) : 0건",
            font_name=FONT_NAME,
            font_size=dp(13),
            color=TEXT_MUTED,
            halign="left",
        )
        self.lbl_status_count.bind(
            size=lambda i, s: setattr(i, "text_size", s)
        )

        self.chk_all = CheckBox(
            size_hint_x=None, width=dp(26), color=PRIMARY_BLUE
        )
        self.chk_all.bind(active=self.on_check_all_change)
        self.lbl_chk_all = Label(
            text="전체선택",
            font_name=FONT_NAME,
            font_size=dp(12),
            color=TEXT_DARK,
            size_hint_x=None,
            width=dp(55),
        )

        list_header.add_widget(self.lbl_status_count)
        list_header.add_widget(self.chk_all)
        list_header.add_widget(self.lbl_chk_all)
        self.layout.add_widget(list_header)

        self.rv = RecycleView()
        self.rv_layout = RecycleBoxLayout(
            default_size=(None, dp(218)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
            spacing=dp(8),
        )
        self.rv_layout.bind(minimum_height=self.rv_layout.setter("height"))
        self.rv.add_widget(self.rv_layout)
        self.rv.viewclass = "UnifiedTaskCard"
        self.layout.add_widget(self.rv)

        self.action_bar = BoxLayout(
            size_hint_y=None, height=dp(42), padding=(dp(5), 0)
        )
        self.action_bar.add_widget(Widget())

        self.btn_main_action = StyledButton(
            text="+ 선택 항목 할당받기 (0)",
            size_hint_x=None,
            width=dp(210),
            bg_color=RETURN_GREEN,
            bold=True,
            font_size=dp(13),
        )
        self.btn_main_action.bind(on_press=self.handle_main_action)
        self.action_bar.add_widget(self.btn_main_action)
        self.layout.add_widget(self.action_bar)

        self.add_widget(self.layout)

    def reset_filters(self):
        self.selected_from_zones = {"전체"}
        self.selected_to_zones = {"전체"}
        self.btn_from_zone.text = "보관: 전체"
        self.btn_to_zone.text = "이동: 전체"
        self.active_equip_filter = "ORDERPICKER"
        self.btn_eq_all.set_active_visual(False)
        self.btn_eq_op.set_active_visual(True)
        self.btn_eq_reach.set_active_visual(False)
        self.only_urgent = False
        self.chk_urgent.active = False
        self.sort_asc = True
        self.btn_sort.text = "▲"

    def open_from_zone_popup(self, instance):
        try:
            app = App.get_running_app()
            user_name = str(app.user_real_name).strip().lower()

            from_counts = Counter()
            for task in self.raw_all_tasks:
                status = str(t(task, "상태")).strip()
                assignee = str(t(task, "작업 담당자")).strip().lower()
                if self.active_main_tab == "PENDING":
                    if status != "대기" or assignee != "":
                        continue
                else:
                    if status != "작업중" or assignee != user_name:
                        continue

                loc = str(t(task, "기존로케이션")).strip().upper()
                if loc:
                    from_counts[f"{loc[0]}존"] += 1

            def apply_from_zones(selected_set):
                self.selected_from_zones = selected_set
                if "전체" in selected_set or not selected_set:
                    self.btn_from_zone.text = "보관: 전체"
                else:
                    zones_str = ",".join(sorted(selected_set)).replace("존", "")
                    self.btn_from_zone.text = f"보관: {zones_str}"
                self.apply_filters_and_render()

            dropdown = ZoneMultiSelectDropDown(
                dict(sorted(from_counts.items())), self.selected_from_zones, apply_from_zones
            )
            dropdown.open(instance)
        except Exception as e:
            print(f"⚠️ 보관 존 드롭다운 오픈 에러: {e}")

    def open_to_zone_popup(self, instance):
        try:
            app = App.get_running_app()
            user_name = str(app.user_real_name).strip().lower()

            to_counts = Counter()
            for task in self.raw_all_tasks:
                status = str(t(task, "상태")).strip()
                assignee = str(t(task, "작업 담당자")).strip().lower()
                if self.active_main_tab == "PENDING":
                    if status != "대기" or assignee != "":
                        continue
                else:
                    if status != "작업중" or assignee != user_name:
                        continue

                loc = str(t(task, "보충로케이션")).strip().upper()
                if loc:
                    to_counts[f"{loc[0]}존"] += 1

            def apply_to_zones(selected_set):
                self.selected_to_zones = selected_set
                if "전체" in selected_set or not selected_set:
                    self.btn_to_zone.text = "이동: 전체"
                else:
                    zones_str = ",".join(sorted(selected_set)).replace("존", "")
                    self.btn_to_zone.text = f"이동: {zones_str}"
                self.apply_filters_and_render()

            dropdown = ZoneMultiSelectDropDown(
                dict(sorted(to_counts.items())), self.selected_to_zones, apply_to_zones
            )
            dropdown.open(instance)
        except Exception as e:
            print(f"⚠️ 이동 존 드롭다운 오픈 에러: {e}")

    def toggle_sort_order(self, instance):
        self.sort_asc = not self.sort_asc
        self.btn_sort.text = "▲" if self.sort_asc else "▼"
        self.apply_filters_and_render()

    def toggle_filter_panel(self, instance=None):
        self.is_filter_expanded = not self.is_filter_expanded
        if self.is_filter_expanded:
            if self.filter_panel not in self.layout.children:
                target_idx = len(self.layout.children) - 2
                self.layout.add_widget(self.filter_panel, index=target_idx)
            self._update_filter_button_text("닫기 ▲")
        else:
            if self.filter_panel in self.layout.children:
                self.layout.remove_widget(self.filter_panel)
            self._update_filter_button_text("열기 ▼")

    def _update_filter_button_text(self, arrow):
        tab_str = "대기작업" if self.active_main_tab == "PENDING" else "내 작업"
        eq_str = (
            "전체"
            if self.active_equip_filter == "ALL"
            else (
                "오더피커"
                if self.active_equip_filter == "ORDERPICKER"
                else "리치"
            )
        )
        self.btn_toggle_filter.text = (
            f"🔍 필터 설정 {arrow} ({tab_str} / {eq_str})"
        )

    def on_enter(self):
        app = App.get_running_app()
        if not app.user_real_name:
            app.user_real_name = app.load_saved_user_name() or ""
            if not app.user_real_name:
                self.manager.current = "name_entry"
                return

        self.reset_filters()

        self.active_main_tab = "PENDING"
        self.btn_tab_pending.set_active_visual(True)
        self.btn_tab_my.set_active_visual(False)

        self.btn_eq_all.set_active_visual(False)
        self.btn_eq_op.set_active_visual(True)
        self.btn_eq_reach.set_active_visual(False)

        self.is_filter_expanded = True
        if self.filter_panel not in self.layout.children:
            target_idx = len(self.layout.children) - 2
            self.layout.add_widget(self.filter_panel, index=target_idx)
        self._update_filter_button_text("닫기 ▲")

        self.fetch_data()

    def handle_barcode_scan(self, barcode):
        # 💡 영어, 숫자, 하이픈(-)만 남김
        clean_bc = re.sub(r'[^A-Za-z0-9\-]', '', str(barcode)).strip().upper()

        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        # 1. 내 작업('작업중') 중 매칭되는 모든 항목 검색
        my_matches = [
            t_item
            for t_item in self.raw_all_tasks
            if str(t(t_item, "상태")).strip() == "작업중"
            and str(t(t_item, "작업 담당자")).strip().lower() == user_name
            and re.sub(r'[^A-Za-z0-9\-]', '', str(get_barcode_from_task(t_item))).strip().upper() == clean_bc
        ]

        if my_matches:
            if self.active_main_tab != "MY":
                self.switch_main_tab("MY")

            # 💡 [핵심 해결 1] 매칭된 항목이 1개일 때
            if len(my_matches) == 1:
                target_task = my_matches[0]
                target_task["manual_qty_unlocked"] = True
                
                task_list_screen = self.manager.get_screen("task_list")
                dummy_card = type("DummyCard", (), {"task_data": target_task})()
                task_list_screen.open_quantity_popup(dummy_card, card_ref=self)
            
            # 💡 [핵심 해결 2] 같은 로케이션/바코드 작업이 여러 개일 때 (중복 팝업 오프닝)
            else:
                # 중복 팝업용 데이터 포맷팅
                formatted_matches = [{"task_data": task} for task in my_matches]

                def _on_select_task(selected_item):
                    sel_task = selected_item["task_data"]
                    sel_task["manual_qty_unlocked"] = True
                    task_list_screen = self.manager.get_screen("task_list")
                    dummy_card = type("DummyCard", (), {"task_data": sel_task})()
                    task_list_screen.open_quantity_popup(dummy_card, card_ref=self)

                MultipleSkuSelectPopup(
                    matches=formatted_matches, on_select=_on_select_task
                ).open()

        else:
            # 2. 대기 목록 중 매칭되는 바코드 찾기
            pending_matches = [
                t_item
                for t_item in self.raw_all_tasks
                if str(t(t_item, "상태")).strip() == "대기"
                and re.sub(r'[^A-Za-z0-9\-]', '', str(get_barcode_from_task(t_item))).strip().upper() == clean_bc
            ]
            if pending_matches:
                task_id = t(pending_matches[0], "작업ID")
                self.checked_task_ids.add(task_id)
                self.apply_filters_and_render()
                app.show_info_popup(
                    "스캔 알림",
                    f"['내 작업' 목록에 없는 상품입니다]\n대기 목록의 [{clean_bc}] 항목이 체크 선택되었습니다.\n하단의 [할당받기]를 먼저 눌러주세요.",
                )
            else:
                app.show_info_popup(
                    "스캔 오류",
                    f"스캔한 바코드 [{clean_bc}] 에 해당하는 작업을 찾을 수 없습니다.",
                )

    # 💡 [v1.8.9.3] 갱신 버튼 전용 안전 갱신 메서드
    def refresh_button_click(self, instance=None):
        self.fetch_data()

    def fetch_data(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_data, daemon=True).start()

    def _async_fetch_data(self):
        try:
            tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=True)
            self.raw_all_tasks = tasks
            Clock.schedule_once(lambda dt: self.apply_filters_and_render())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def switch_main_tab(self, tab_mode):
        self.active_main_tab = tab_mode
        self.checked_task_ids.clear()
        self.chk_all.active = False

        self.reset_filters()

        if tab_mode == "MY":
            self.btn_main_action.text = "↩ 선택 항목 일괄 반납 (0)"
            self.btn_main_action.set_bg_color(get_color_from_hex("#FF7043"))
        else:
            self.btn_main_action.text = "+ 선택 항목 할당받기 (0)"
            self.btn_main_action.set_bg_color(PRIMARY_BLUE)

        self._update_filter_button_text(
            "닫기 ▲" if self.is_filter_expanded else "열기 ▼"
        )
        self.apply_filters_and_render()

    def switch_equip_filter(self, eq_mode):
        self.active_equip_filter = eq_mode
        self.btn_eq_all.set_active_visual(eq_mode == "ALL")
        self.btn_eq_op.set_active_visual(eq_mode == "ORDERPICKER")
        self.btn_eq_reach.set_active_visual(eq_mode == "REACH")
        self._update_filter_button_text(
            "닫기 ▲" if self.is_filter_expanded else "열기 ▼"
        )
        self.apply_filters_and_render()

    def on_urgent_check_change(self, checkbox, value):
        self.only_urgent = value
        self.apply_filters_and_render()

    def toggle_card_check(self, task_data, is_checked):
        task_id = t(task_data, "작업ID")
        if is_checked:
            self.checked_task_ids.add(task_id)
        else:
            self.checked_task_ids.discard(task_id)

        for item in self.rv.data:
            if t(item["task_data"], "작업ID") == task_id:
                item["is_checked"] = is_checked
                break

        action_prefix = (
            "↩ 선택 항목 일괄 반납"
            if self.active_main_tab == "MY"
            else "+ 선택 항목 할당받기"
        )
        self.btn_main_action.text = (
            f"{action_prefix} ({len(self.checked_task_ids)})"
        )

    def on_check_all_change(self, checkbox, value):
        self.rv.data = [{**item, "is_checked": value} for item in self.rv.data]
        self.rv.refresh_from_data()
        if value:
            for item in self.rv.data:
                self.checked_task_ids.add(t(item["task_data"], "작업ID"))
        else:
            self.checked_task_ids.clear()

        action_prefix = (
            "↩ 선택 항목 일괄 반납"
            if self.active_main_tab == "MY"
            else "+ 선택 항목 할당받기"
        )
        self.btn_main_action.text = (
            f"{action_prefix} ({len(self.checked_task_ids)})"
        )

    def apply_filters_and_render(self):
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        eq_all_tot, eq_all_urg = 0, 0
        eq_op_tot, eq_op_urg = 0, 0
        eq_reach_tot, eq_reach_urg = 0, 0

        pending_urg_count = 0
        my_urg_count = 0

        for task in self.raw_all_tasks:
            status = str(t(task, "상태")).strip()
            assignee = str(t(task, "작업 담당자")).strip().lower()
            is_urg = t(task, "긴급여부") == "Y"

            if status == "대기" and assignee == "":
                if is_urg:
                    pending_urg_count += 1
            elif status == "작업중" and assignee == user_name:
                if is_urg:
                    my_urg_count += 1

            if self.active_main_tab == "PENDING":
                if status != "대기" or assignee != "":
                    continue
            else:
                if status != "작업중" or assignee != user_name:
                    continue

            equip = str(t(task, "장비")).strip()

            eq_all_tot += 1
            if is_urg:
                eq_all_urg += 1

            if equip == "오더피커":
                eq_op_tot += 1
                if is_urg:
                    eq_op_urg += 1
            elif equip == "리치":
                eq_reach_tot += 1
                if is_urg:
                    eq_reach_urg += 1

        urg_font_sz = int(dp(12))
        self.btn_tab_pending.markup = True
        self.btn_tab_pending.text = f"대기 작업 [color=FF9800][size={urg_font_sz}](긴급: {pending_urg_count})[/size][/color]"

        self.btn_tab_my.markup = True
        self.btn_tab_my.text = f"내 작업 [color=FF9800][size={urg_font_sz}](긴급: {my_urg_count})[/size][/color]"

        self.btn_tab_pending.set_active_visual(
            self.active_main_tab == "PENDING"
        )
        self.btn_tab_my.set_active_visual(self.active_main_tab == "MY")

        self.btn_eq_all.markup = True
        self.btn_eq_all.text = f"전체 ({eq_all_tot} / [color=D32F2F]{eq_all_urg}[/color])"

        self.btn_eq_op.markup = True
        self.btn_eq_op.text = f"오더피커 ({eq_op_tot} / [color=D32F2F]{eq_op_urg}[/color])"

        self.btn_eq_reach.markup = True
        self.btn_eq_reach.text = f"리치 ({eq_reach_tot} / [color=D32F2F]{eq_reach_urg}[/color])"

        filtered_list = []
        for task in self.raw_all_tasks:
            status = str(t(task, "상태")).strip()
            assignee = str(t(task, "작업 담당자")).strip().lower()
            equip = str(t(task, "장비")).strip()

            if self.active_main_tab == "PENDING":
                if status != "대기" or assignee != "":
                    continue
            else:
                if status != "작업중" or assignee != user_name:
                    continue

            if (
                self.active_equip_filter == "ORDERPICKER"
                and equip != "오더피커"
            ):
                continue
            if self.active_equip_filter == "REACH" and equip != "리치":
                continue

            from_loc = str(t(task, "기존로케이션")).strip().upper()
            to_loc = str(t(task, "보충로케이션")).strip().upper()

            if "전체" not in self.selected_from_zones:
                from_zone = f"{from_loc[0]}존" if from_loc else ""
                if from_zone not in self.selected_from_zones:
                    continue

            if "전체" not in self.selected_to_zones:
                to_zone = f"{to_loc[0]}존" if to_loc else ""
                if to_zone not in self.selected_to_zones:
                    continue

            if self.only_urgent and t(task, "긴급여부") != "Y":
                continue

            filtered_list.append(task)

        filtered_list.sort(
            key=lambda x: (
                t(x, "긴급여부") != "Y",
                t(x, "기존로케이션", ""),
            ),
            reverse=not self.sort_asc,
        )

        rv_items = []
        is_my_mode = self.active_main_tab == "MY"
        for task in filtered_list:
            task_id = t(task, "작업ID")
            rv_items.append(
                {
                    "task_data": task,
                    "is_claimed": is_my_mode,
                    "is_checked": (task_id in self.checked_task_ids),
                    "card_screen": self,
                }
            )

        self.rv.data = rv_items
        self.rv.refresh_from_data()

        tab_name = "대기 작업" if not is_my_mode else "내 작업"
        eq_name = (
            "전체"
            if self.active_equip_filter == "ALL"
            else (
                "오더피커"
                if self.active_equip_filter == "ORDERPICKER"
                else "리치"
            )
        )
        self.lbl_status_count.text = (
            f"{tab_name} ({eq_name}) : {len(filtered_list)}건"
        )

    def handle_main_action(self, instance):
        if self.active_main_tab == "PENDING":
            self.claim_checked_tasks(instance)
        else:
            self.batch_return_checked_tasks(instance)

    def claim_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup(
                "알림", "할당받을 작업을 선택해주세요."
            )
            return
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_claim_tasks, daemon=True).start()

    def _async_claim_tasks(self):
        try:
            app = App.get_running_app()
            sheet = get_worksheet(TASK_SHEET_NAME)

            all_rows = execute_with_retry(sheet.get, "A:AA")
            if not all_rows or len(all_rows) < 2:
                raise Exception("시트 데이터를 불러올 수 없습니다.")

            headers = [str(h).strip() for h in all_rows[0]]
            assignee_col = headers.index("작업 담당자") + 1
            status_col = headers.index("상태") + 1

            cells_to_update = []
            already_taken_count = 0

            for row_idx, row in enumerate(all_rows[1:], start=2):
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))

                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                task_id = str(t(row_dict, "작업ID")).strip()

                if task_id in self.checked_task_ids:
                    curr_status = str(t(row_dict, "상태")).strip()
                    curr_assignee = str(
                        t(
                            row_dict,
                            "작업 담당자",
                            t(row_dict, "담당자", ""),
                        )
                    ).strip()

                    if curr_status in ["대기", ""] and curr_assignee == "":
                        cells_to_update.append(
                            gspread.Cell(
                                row_idx, assignee_col, app.user_real_name
                            )
                        )
                        cells_to_update.append(
                            gspread.Cell(row_idx, status_col, "작업중")
                        )
                    else:
                        already_taken_count += 1

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            invalidate_cache(TASK_SHEET_NAME)
            self.checked_task_ids.clear()

            if already_taken_count > 0 and len(cells_to_update) == 0:
                Clock.schedule_once(
                    lambda dt: app.show_info_popup(
                        "할당 실패",
                        "선택하신 작업이 이미 다른 작업자에게 할당되었습니다.\n목록을 자동으로 갱신합니다.",
                    )
                )
            elif already_taken_count > 0:
                Clock.schedule_once(
                    lambda dt: app.show_info_popup(
                        "부분 할당 완료",
                        f"이미 다른 사용자가 가져간 {already_taken_count}건을 제외하고 할당되었습니다.",
                    )
                )
            else:
                Clock.schedule_once(lambda dt: self.on_claim_success())

            Clock.schedule_once(lambda dt: self.fetch_data())

        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def on_claim_success(self):
        App.get_running_app().show_toast("선택한 작업이 '내 작업'으로 할당되었습니다.")
        self.switch_main_tab("MY")

    def batch_return_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup(
                "알림", "반납할 작업을 선택해주세요."
            )
            return
        App.get_running_app().show_confirmation_popup(
            "일괄 반납 확인",
            f"선택한 {len(self.checked_task_ids)}건의 작업을 반납하시겠습니까?",
            lambda: self._start_async_batch_return(),
        )

    def _start_async_batch_return(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(
            target=self._async_batch_return, daemon=True
        ).start()

    def _async_batch_return(self):
        try:
            sheet = get_worksheet(TASK_SHEET_NAME)
            all_rows = execute_with_retry(sheet.get, "A:AA")
            if not all_rows or len(all_rows) < 2:
                raise Exception("시트 데이터를 불러올 수 없습니다.")

            headers = [str(h).strip() for h in all_rows[0]]
            assignee_col = headers.index("작업 담당자") + 1
            status_col = headers.index("상태") + 1
            task_id_col = headers.index("작업ID") + 1

            all_ids = sheet.col_values(task_id_col)
            cells_to_update = []

            for task_id in self.checked_task_ids:
                if task_id in all_ids:
                    row_idx = all_ids.index(task_id) + 1
                    cells_to_update.append(
                        gspread.Cell(row_idx, assignee_col, "")
                    )
                    cells_to_update.append(
                        gspread.Cell(row_idx, status_col, "대기")
                    )

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            for task in self.raw_all_tasks:
                if t(task, "작업ID") in self.checked_task_ids:
                    task["상태"] = "대기"
                    task["작업 담당자"] = ""

            invalidate_cache(TASK_SHEET_NAME)
            self.checked_task_ids.clear()

            Clock.schedule_once(
                lambda dt: App.get_running_app().show_toast("선택한 작업이 일괄 반납되었습니다.")
            )
            Clock.schedule_once(lambda dt: self.apply_filters_and_render())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def handle_my_task_action(self, action_name, task_data):
        task_list_screen = self.manager.get_screen("task_list")
        dummy_card = type("DummyCard", (), {"task_data": task_data})()

        if action_name == "return":
            task_list_screen.return_task(dummy_card)
        elif action_name == "qty":
            task_list_screen.open_quantity_popup(dummy_card, card_ref=self)
        elif action_name == "fail":
            task_list_screen.process_failure(dummy_card)
        elif action_name == "remarks":
            task_list_screen.prompt_for_remarks(dummy_card)
        elif action_name == "complete":
            App.get_running_app().current_list_type = "보충인원"
            task_list_screen.process_task(dummy_card)


# --- 검수 및 액션 처리 전용 화면 ---
class TaskListScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_tasks_data = []

    def on_enter(self, *args):
        app = App.get_running_app()
        if not app.user_real_name:
            app.user_real_name = app.load_saved_user_name() or ""
            if not app.user_real_name:
                self.manager.current = "name_entry"
                return
        # 💡 진입 시에도 깜빡임 없도록 show_loading=False
        self.refresh_list(force_refresh=True, show_loading=False)

    # 💡 show_loading 파라미터로 백그라운드 자동 갱신 팝업 차단
    def refresh_list(self, force_refresh=True, show_loading=False):
        if show_loading:
            App.get_running_app().show_loading_popup()
        threading.Thread(
            target=self._perform_get_tasks,
            args=(force_refresh, show_loading),
            daemon=True,
        ).start()

    def _perform_get_tasks(self, force_refresh, show_loading=False):
        try:
            all_tasks = get_sheet_data(
                TASK_SHEET_NAME, force_refresh=force_refresh
            )
            filtered_task_data = [
                task
                for task in all_tasks
                if str(t(task, "상태")).strip() == "적치대기"
            ]

            task_map = {
                t(task, "작업ID"): (i + 2, task)
                for i, task in enumerate(all_tasks)
            }
            my_tasks = [
                {
                    "task_data": task,
                    "task_screen": self,
                    "row_index": task_map.get(t(task, "작업ID"), (0, None))[0],
                }
                for task in filtered_task_data
                if t(task, "작업ID") in task_map
            ]

            self.all_tasks_data = my_tasks
            Clock.schedule_once(lambda dt: self.update_recycle_view())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            # 💡 버튼을 직접 클릭한 경우에만 로딩 팝업 닫기
            if show_loading:
                Clock.schedule_once(
                    lambda dt: App.get_running_app().dismiss_loading_popup()
                )

    def update_recycle_view(self):
        query = (
            self.ids.search_input.text.strip().lower()
            if "search_input" in self.ids
            else ""
        )
        filtered_data = []
        for item in self.all_tasks_data:
            task = item["task_data"]
            product_name = str(t(task, "상품명", "")).lower()
            barcode = get_barcode_from_task(task).lower()
            if not query or query in product_name or query in barcode:
                filtered_data.append(item)

        if hasattr(self.ids, "task_list_rv"):
            self.ids.task_list_rv.data = filtered_data
            self.ids.task_list_rv.refresh_from_data()

    def search_tasks(self, instance=None):
        self.update_recycle_view()

    # 💡 [추가] 검색창 터치 시 안드로이드 네이티브 입력창 띄우기
    def on_search_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def set_query(val):
                instance.text = val
                self.search_tasks()

            open_native_korean_input(
                "검색어 입력", "SKU명 또는 바코드 검색", instance.text, set_query
            )
            return True
        return False

   # 💡 [바로 여기에 음영 처리된 코드가 들어가야 합니다!]
    def handle_barcode_scan(self, barcode):
        clean_bc = str(barcode).strip().upper()

        for child in Window.children:
            if isinstance(child, InspectionPopup):
                child.process_location_scan(clean_bc)
                return

        matches = [
            item for item in self.all_tasks_data
            if get_barcode_from_task(item["task_data"]) == clean_bc
        ]

        if not matches:
            App.get_running_app().show_info_popup(
                "알림", f"스캔한 바코드[{clean_bc}]는 검수 대상 목록에 없습니다."
            )
            return

        if len(matches) == 1:
            self.open_task_from_scan(matches[0])
        else:
            MultipleSkuSelectPopup(
                matches=matches, on_select=self.open_task_from_scan
            ).open()

    def open_task_from_scan(self, item_data):
        dummy_card = type(
            "DummyCard", (), {"task_data": item_data["task_data"]}
        )()
        InspectionPopup(card=dummy_card, task_list_screen=self).open()

    def _perform_update_and_log(self, card, updates, msg):
        try:
            sheet = get_worksheet(TASK_SHEET_NAME)
            headers = [str(h).strip() for h in sheet.row_values(1)]
            task_id = str(t(card.task_data, "작업ID"))

            task_id_col_idx = headers.index("작업ID") + 1
            all_task_ids = sheet.col_values(task_id_col_idx)

            if task_id not in all_task_ids:
                raise Exception(
                    f"작업ID [{task_id}]를 시트에서 찾을 수 없습니다."
                )

            row_idx = all_task_ids.index(task_id) + 1
            cells = []

            for key, val in updates.items():
                if key in headers:
                    col_idx = headers.index(key) + 1
                    cells.append(gspread.Cell(row_idx, col_idx, str(val)))

            if cells:
                sheet.update_cells(cells)

            updated_task_data = dict(card.task_data)
            updated_task_data.update(updates)

            try:
                log_sheet = get_worksheet(LOG_SHEET_NAME)
                log_headers = [str(h).strip() for h in log_sheet.row_values(1)]
                log_row = [str(updated_task_data.get(h, "")) for h in log_headers]
                log_sheet.append_row(log_row)
            except Exception as log_err:
                print(f"⚠️ 로그 시트 기록 중 경고: {log_err}")

            invalidate_cache(TASK_SHEET_NAME)
            invalidate_cache(LOG_SHEET_NAME)
            Clock.schedule_once(lambda dt: self.on_action_success(msg))
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def open_quantity_popup(self, card, card_ref=None):
        initial_val = ""

        def on_confirm_qty(text):
            val = text.strip()
            if val.isdigit():
                task_id = t(card.task_data, "작업ID")

                if card_ref and hasattr(card_ref, "raw_all_tasks"):
                    for task in card_ref.raw_all_tasks:
                        if t(task, "작업ID") == task_id:
                            task["confirmed_quantity"] = val
                            task["확인수량"] = val
                            break

                card.task_data["confirmed_quantity"] = val
                card.task_data["확인수량"] = val

                if card_ref and hasattr(card_ref, "apply_filters_and_render"):
                    card_ref.apply_filters_and_render()

                App.get_running_app().show_toast(
                    f"수량 '{val}'(이)가 임시 저장되었습니다."
                )
            else:
                App.get_running_app().show_info_popup(
                    "오류", "숫자만 입력해야 합니다."
                )

        open_native_korean_input(
            "확인 수량 입력",
            "수량 입력",
            initial_val,
            on_confirm_qty,
            is_number=True,
        )

    def prompt_for_remarks(self, card):

        def on_confirm_rem(text):
            if not text.strip():
                return
            app = App.get_running_app()
            ts = datetime.now().strftime("%y-%m-%d %H:%M")
            formatted = f"[{ts} {app.user_real_name}] {text.strip()}"
            curr = card.task_data.get(
                "remarks_text", t(card.task_data, "비고", "")
            )
            updated_text = f"{curr}\n{formatted}" if curr else formatted
            card.task_data["remarks_text"] = updated_text
            card.task_data["비고"] = updated_text

            app.show_toast("비고가 임시 저장되었습니다. 완료 시 시트에 기재됩니다.")

        open_native_korean_input(
            "비고 추가", "비고 내용 입력", "", on_confirm_rem
        )

    def process_failure(self, card):

        def on_confirm_fail(reason):
            if not reason.strip():
                return
            app = App.get_running_app()
            updates = {
                "상태": "보충실패",
                "실패사유": reason.strip(),
                "보충담당자": app.user_real_name,
                "완료일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            app.show_loading_popup()
            threading.Thread(
                target=self._perform_update_and_log,
                args=(card, updates, "보충 실패 처리 되었습니다."),
                daemon=True,
            ).start()

        open_native_korean_input(
            "실패 사유 입력", "사유 입력", "", on_confirm_fail
        )

    def process_task(self, card):
        app = App.get_running_app()

        if app.current_list_type == "검수인원":
            InspectionPopup(card=card, task_list_screen=self).open()
            return

        qty_val = str(
            card.task_data.get(
                "confirmed_quantity", t(card.task_data, "확인수량", "")
            )
        ).strip()
        if not qty_val.isdigit() or int(qty_val) == 0:
            app.show_info_popup(
                "입력 오류",
                "수량입력 버튼을 눌러 확인 수량을 먼저 입력해주세요.",
            )
            return

        conf_q = int(qty_val)
        card.task_data["확인수량"] = conf_q

        # 💡 [보정] 스캔불가 사유가 담긴 비고 텍스트를 최우선으로 추출
        current_remarks = str(
            card.task_data.get(
                "remarks_text", t(card.task_data, "비고", "")
            )
        ).strip()

        req_q = safe_int(t(card.task_data, "지시수량", 0))
        if conf_q != req_q:
            app.show_confirmation_popup(
                title="수량 불일치 경고 🚨",
                message=f"[color=ffffff]지시수량([color=FF8A80][b]{req_q}개[/b][/color])과 확인수량([color=81C784][b]{conf_q}개[/b][/color])이 다릅니다.\n이대로 보충 완료 처리를 진행하시겠습니까?[/color]",
                on_yes=lambda: self._finalize_task_processing(
                    card,
                    conf_q,
                    0,
                    None,
                    current_remarks,  # 👈 비고 전달
                ),
            )
            return

        self._finalize_task_processing(
            card,
            conf_q,
            0,
            None,
            current_remarks,  # 👈 비고 전달
        )

    def _start_print_job(self, card_data):
        try:
            app = App.get_running_app()
            default_printer = app.load_default_printer()
            if not default_printer:
                return

            qty_per_box = safe_int(
                t(card_data, "박스입수량", t(card_data, "박스 입수량", 0))
            )
            prod_name = str(t(card_data, "상품명", ""))
            is_invoice_only = qty_per_box == 1 or "송장" in prod_name

            # 💡 [수정] 확인수량 기반 인쇄 데이터 세팅
            conf_qty_val = card_data.get("confirmed_quantity", t(card_data, "확인수량", t(card_data, "지시수량", 0)))
            printed_qty = safe_int(conf_qty_val)

            label_info = {
                "바코드": get_barcode_from_task(card_data),
                "보관 로케이션": str(t(card_data, "기존로케이션", "N/A")),
                "출고 로케이션": str(t(card_data, "보충로케이션", "N/A")),
                "긴급여부": (t(card_data, "긴급여부") == "Y"),
                "송장전용": is_invoice_only,
                "확인수량": printed_qty,
                "박스입수량": qty_per_box,
            }
            threading.Thread(
                target=self._print_thread,
                args=(default_printer, label_info, 1),
                daemon=True,
            ).start()
        except Exception as e:
            print(f"🔴 프린터 작업 에러 무시됨: {e}")

    def _print_thread(self, address, label_info, quantity):
        try:
            printer = BluetoothPrinter(address)
            if printer.connect():
                try:
                    printer.print_outbound_label_cpcl(label_info, quantity)
                except Exception:
                    pass
                finally:
                    printer.disconnect()
        except Exception as e:
            print(f"🔴 블루투스 인쇄 실패: {e}")

    def _finalize_task_processing(
        self, card, final_qty, split_qty, final_location, updated_remarks
    ):
        app = App.get_running_app()

        default_box_size = safe_int(
            t(card.task_data, "박스입수량", t(card.task_data, "박스 입수량", 1))
        )
        
        changed_box_size = getattr(card, "changed_box_size", None) or card.task_data.get("changed_box_size", None)

        if changed_box_size and safe_int(changed_box_size) > 0 and safe_int(changed_box_size) != default_box_size:
            new_box_size = safe_int(changed_box_size)
            change_log = f"입수량 변경 : {new_box_size}"
            current_rem_str = str(updated_remarks or "").strip()
            
            if current_rem_str:
                if "입수량 변경" in current_rem_str:
                    updated_remarks = re.sub(
                        r"(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] )?입수량 변경 : \d+",
                        change_log,
                        current_rem_str
                    )
                else:
                    updated_remarks = f"{current_rem_str}\n{change_log}"
            else:
                updated_remarks = change_log

        # 💡 [핵심 추가] 검수 작업일 때, 보충 수량과 검수 수량이 다르면 비고란에 자동 기록
        if app.current_list_type == "검수인원":
            # 보충 작업 시 입력했던 기존 수량 (확인수량 필드 참조)
            replenished_qty = safe_int(t(card.task_data, "확인수량", t(card.task_data, "지시수량", 0)))
            
            # 수량이 서로 불일치할 경우
            if final_qty != replenished_qty:
                diff = final_qty - replenished_qty
                diff_str = f"+{diff}" if diff > 0 else f"{diff}"
                
                # 형식 1 텍스트 포맷 생성
                mismatch_log = f"[수량 불일치] 보충: {replenished_qty}개 ➔ 검수: {final_qty}개 (차이: {diff_str}개)"
                
                curr_rem = str(updated_remarks or "").strip()
                # 기존 비고가 있으면 줄바꿈(\n) 후 추가
                if curr_rem:
                    updated_remarks = f"{curr_rem}\n{mismatch_log}"
                else:
                    updated_remarks = mismatch_log

            updates = {
                "상태": "최종완료",
                "검수담당자": app.user_real_name,
                "최종완료일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "확인수량": str(final_qty),
                "비고": updated_remarks,
                "최종적치위치": final_location,
            }
            app.show_loading_popup()
            threading.Thread(
                target=self._perform_update_and_log,
                args=(card, updates, "검수 작업이 '최종완료' 처리 되었습니다."),
                daemon=True,
            ).start()
            return

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        updates = {
            "상태": "적치대기",
            "보충담당자": app.user_real_name,
            "완료일시": now_str,
            "확인수량": str(final_qty),
            "비고": updated_remarks,
        }

        completed_record = dict(card.task_data)
        completed_record.update(updates)
        g_recent_completed_tasks.append(completed_record)
        if len(g_recent_completed_tasks) > 15:
            g_recent_completed_tasks.pop(0)

        save_recent_history()

        def run_sheet_update():
            app.show_loading_popup()
            threading.Thread(
                target=self._perform_update_and_log,
                args=(card, updates, "보충작업이 완료되어 '적치대기' 상태로 전환되었습니다."),
                daemon=True,
            ).start()

        def on_yes_print():
            try:
                self._start_print_job(card.task_data)
            except Exception:
                pass
            run_sheet_update()

        app.show_confirmation_popup(
            title="인쇄 및 완료",
            message="[color=ffffff]보충 완료 및 적치대기 처리합니다.\n라벨 1장을 인쇄하시겠습니까?[/color]",
            on_yes=on_yes_print,
            on_no=run_sheet_update,
        )

    def _perform_update_and_log(self, card, updates, msg):
        try:
            sheet = get_worksheet(TASK_SHEET_NAME)
            headers = [str(h).strip() for h in sheet.row_values(1)]
            
            card_task_data = getattr(card, "task_data", {})
            is_merged = card_task_data.get("is_merged", False) or getattr(card, "is_merged", False)
            merged_sources = card_task_data.get("merged_sources", []) or getattr(card, "merged_sources", [])

            log_entries = []  # 💡 기록용 로그 데이터 수집 배열

            # 💡 다중 선택 통합 검수 완료 시
            if is_merged and merged_sources:
                task_id_col_idx = headers.index("작업ID") + 1
                all_task_ids = sheet.col_values(task_id_col_idx)
                
                cells = []
                for src_item in merged_sources:
                    src_task = src_item.get("task_data", {})
                    target_id = str(t(src_task, "작업ID")).strip()
                    
                    if target_id in all_task_ids:
                        row_idx = all_task_ids.index(target_id) + 1
                        for key, val in updates.items():
                            if key in headers:
                                col_idx = headers.index(key) + 1
                                cells.append(gspread.Cell(row_idx, col_idx, str(val)))
                    
                    # 로그 기록을 위한 데이터 세팅
                    merged_updated_task = dict(src_task)
                    merged_updated_task.update(updates)
                    log_entries.append(merged_updated_task)

                if cells:
                    sheet.update_cells(cells)
                    
            # 💡 단일 선택 검수 완료 시
            else:
                task_id = str(t(card.task_data, "작업ID"))
                task_id_col_idx = headers.index("작업ID") + 1
                all_task_ids = sheet.col_values(task_id_col_idx)

                if task_id not in all_task_ids:
                    raise Exception(f"작업ID [{task_id}]를 시트에서 찾을 수 없습니다.")

                row_idx = all_task_ids.index(task_id) + 1
                cells = []

                for key, val in updates.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        cells.append(gspread.Cell(row_idx, col_idx, str(val)))

                if cells:
                    sheet.update_cells(cells)
                
                # 로그 기록을 위한 데이터 세팅
                single_updated_task = dict(card.task_data)
                single_updated_task.update(updates)
                log_entries.append(single_updated_task)

            # ==========================================
            # 💡 [조건 추가 구역] 작업완료 로그 시트 기록
            # ==========================================
            # 🚨 "상태"가 "최종완료"일 때만 로그 시트에 기록되도록 조건문(if) 추가
            if log_entries and updates.get("상태") == "최종완료":
                try:
                    log_sheet = get_worksheet(LOG_SHEET_NAME)
                    log_headers = [str(h).strip() for h in log_sheet.row_values(1)]
                    
                    rows_to_append = []
                    for entry in log_entries:
                        row = [str(entry.get(h, "")) for h in log_headers]
                        rows_to_append.append(row)
                    
                    # 1건이면 append_row, 다중건이면 append_rows 사용
                    if len(rows_to_append) == 1:
                        log_sheet.append_row(rows_to_append[0])
                    else:
                        log_sheet.append_rows(rows_to_append)
                        
                    invalidate_cache(LOG_SHEET_NAME)
                except Exception as log_err:
                    print(f"⚠️ 로그 시트 기록 중 경고: {log_err}")

            invalidate_cache(TASK_SHEET_NAME)
            Clock.schedule_once(lambda dt: self.on_action_success(msg))

        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def on_action_success(self, msg):
        App.get_running_app().dismiss_loading_popup()
        App.get_running_app().show_toast(msg)

        # 💡 [핵심 수정] 작업 처리 직후 0.5초 서버 저장 안정화 후 화면 즉시 자동 최신화
        def _safe_refresh_ui(dt):
            try:
                app = App.get_running_app()
                if app and app.root:
                    curr_screen = app.root.current_screen
                    if hasattr(curr_screen, "fetch_data"):
                        curr_screen.fetch_data()
                    elif hasattr(curr_screen, "refresh_list"):
                        curr_screen.refresh_list(force_refresh=True)
            except Exception as e:
                print(f"🔴 UI 리프레시 예외 무시: {e}")

        Clock.schedule_once(_safe_refresh_ui, 0.5)

# --- 💡 라인 보충 긴급 요청 및 소통 전용 독립 화면 (Screen) ---
# --- 💡 라인 보충 긴급 요청 및 소통 전용 독립 화면 (속도 최적화 적용) ---
class EmergencyReplenishScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tab = "NEW"
        self.status_filter = "ALL"
        self.hidden_req_ids = set()
        self.raw_requests_cache = []  # 💡 [핵심] 시트 데이터 메모리 캐시 변수

        self.layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        top_bar = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        btn_back = StyledButton(
            text="< 메인",
            size_hint_x=0.2,
            bg_color=get_color_from_hex("#78909C")
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, "current", "main_menu"))

        lbl_title = Label(
            text="🚨 라인 보충 긴급 요청 및 소통 센터",
            font_name=FONT_NAME,
            font_size=dp(16),
            bold=True,
            color=TEXT_DARK
        )

        btn_refresh = StyledButton(
            text="갱신",
            size_hint_x=0.18,
            font_size=dp(12)
        )
        btn_refresh.bind(on_press=lambda x: self.fetch_status_data(force_refresh=True))

        top_bar.add_widget(btn_back)
        top_bar.add_widget(lbl_title)
        top_bar.add_widget(btn_refresh)
        self.layout.add_widget(top_bar)

        tab_box = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(40))
        self.btn_tab_new = StyledToggleButton(
            text="긴급 보충 요청", state="down", font_size=dp(13)
        )
        self.btn_tab_new.bind(on_release=lambda x: self.switch_view("NEW"))

        self.btn_tab_status = StyledToggleButton(
            text="요청 현황 & 데스크 회신", state="normal", font_size=dp(13)
        )
        self.btn_tab_status.bind(on_release=lambda x: self.switch_view("STATUS"))

        tab_box.add_widget(self.btn_tab_new)
        tab_box.add_widget(self.btn_tab_status)
        self.layout.add_widget(tab_box)

        self.content_area = BoxLayout(orientation="vertical", spacing=dp(5))
        self.layout.add_widget(self.content_area)

        self.add_widget(self.layout)

    def on_enter(self):
        self.fetch_status_data(force_refresh=False)
        self.switch_view(self.active_tab)

    # 💡 [핵심] 현황 탭 클릭/이동 시 시트 최신화 자동 수집
    def switch_view(self, view_mode):
        self.active_tab = view_mode
        self.content_area.clear_widgets()

        if view_mode == "NEW":
            self.btn_tab_new.set_active_visual(True)
            self.btn_tab_status.set_active_visual(False)
            self._render_new_request_view()
        else:
            self.btn_tab_new.set_active_visual(False)
            self.btn_tab_status.set_active_visual(True)
            # 💡 현황 탭으로 넘어올 때 강제 갱신 트리거
            self.fetch_status_data(force_refresh=True)
            self._render_status_view()

    def fetch_status_data(self, force_refresh=False):
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        def _async_fetch():
            try:
                sheet_data = get_sheet_data("도급 보충 요청 시트", force_refresh=force_refresh)
                my_reqs = []
                if sheet_data:
                    for r in sheet_data:
                        req_user = str(t(r, "요청자", t(r, "요청 자", ""))).strip().lower()
                        if req_user == user_name:
                            my_reqs.append(r)
                self.raw_requests_cache = my_reqs
                
                # 요청 현황 탭을 보는 중이면 메인 UI 스레드에서 안전하게 화면 즉시 새로고침
                if self.active_tab == "STATUS":
                    Clock.schedule_once(lambda dt: self._render_status_view())
            except Exception as e:
                print(f"요청 현황 데이터 로드 실패: {e}")

        threading.Thread(target=_async_fetch, daemon=True).start()

    # 1. 신규 보충 요청 뷰
    def _render_new_request_view(self):
        layout = BoxLayout(orientation="vertical", spacing=dp(8))

        search_box = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(45))
        self.search_input = TextInput(
            hint_text="터치하여 입력 / 바코드 스캔...",
            font_name=FONT_NAME,
            font_size=dp(14),
            multiline=False,
            size_hint_x=0.75,
            readonly=True,
        )
        self.search_input.bind(on_touch_down=self._on_search_input_touch)
        search_box.add_widget(self.search_input)

        btn_do_search = StyledButton(
            text="검색",
            size_hint_x=0.25,
            font_size=dp(14),
            bg_color=PRIMARY_BLUE
        )
        btn_do_search.bind(on_press=lambda x: self._start_async_search(self.search_input.text))
        search_box.add_widget(btn_do_search)

        layout.add_widget(search_box)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.results_grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.results_grid.bind(minimum_height=self.results_grid.setter("height"))
        self.scroll.add_widget(self.results_grid)
        layout.add_widget(self.scroll)

        self.content_area.add_widget(layout)
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(
            Label(text="바코드를 스캔하거나 입력 후 [검색]을 눌러주세요.", font_name=FONT_NAME, size_hint_y=None, height=dp(40), color=TEXT_MUTED)
        )

    def _start_async_search(self, query):
        if not query.strip():
            App.get_running_app().show_toast("검색어를 입력해 주세요.")
            return

        self.results_grid.clear_widgets()
        self.results_grid.add_widget(
            Label(text="재고 마스터 검색 중...", font_name=FONT_NAME, size_hint_y=None, height=dp(40), color=PRIMARY_BLUE)
        )
        threading.Thread(target=self._search_master_stock, args=(query,), daemon=True).start()

    def _on_search_input_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def set_search_query(val):
                instance.text = str(val).strip()
                self._start_async_search(instance.text)

            open_native_korean_input(
                "검색어 입력", "바코드 숫자 또는 SKU 일부 입력", instance.text, set_search_query
            )
            return True
        return False

    def _search_master_stock(self, query):
        master_data = []
        try:
            master_data = get_sheet_data(LOCATION_CAPA_SHEET_NAME, force_refresh=True)
        except Exception as e:
            print(f"로케이션별재고 raw 참조 실패: {e}")

        seen_skus = set()
        matched_items = []
        clean_query = query.strip().lower()

        if master_data:
            for row in master_data:
                loc_type = str(t(row, "로케이션 유형", t(row, "로케이션유형", ""))).strip()
                if loc_type != "B2C출고":
                    continue

                bc = str(t(row, "바코드", t(row, "상품바코드", ""))).strip()
                prod_name = str(t(row, "SKU", t(row, "상품명", ""))).strip()
                partner = str(t(row, "파트너명", t(row, "고객사", "-"))).strip()
                loc = str(t(row, "로케이션", "-")).strip()
                loc_qty = str(t(row, "로케이션 수량", t(row, "로케이션수량", "0"))).strip()

                if not bc or bc.upper() in ["N/A", "NONE", ""]:
                    continue

                bc_lower = bc.lower()
                prod_lower = prod_name.lower()

                if not clean_query or (clean_query in bc_lower) or (clean_query in prod_lower):
                    combo_key = f"{bc}_{prod_name}_{loc}"
                    if combo_key not in seen_skus:
                        seen_skus.add(combo_key)
                        matched_items.append({
                            "barcode": bc,
                            "product_name": prod_name if prod_name else "SKU 정보 없음",
                            "partner": partner,
                            "location": loc,
                            "loc_qty": loc_qty
                        })

        Clock.schedule_once(lambda dt: self._render_search_results(matched_items, query))

    def _render_search_results(self, matched_items, query):
        self.results_grid.clear_widgets()

        if not matched_items:
            self.results_grid.add_widget(
                Label(text="SKU 정보 없음", font_name=FONT_NAME, size_hint_y=None, height=dp(40), color=TEXT_MUTED)
            )
            return

        for data in matched_items[:30]:
            card = TouchableBox(
                orientation="vertical",
                size_hint_y=None,
                height=dp(82),
                padding=(dp(12), dp(8)),
                spacing=dp(4)
            )
            with card.canvas.before:
                Color(1, 1, 1, 1)
                bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
            card.bind(
                pos=lambda i, p, b=bg_rect: setattr(b, "pos", p),
                size=lambda i, s, b=bg_rect: setattr(b, "size", s)
            )

            prod_text = f"[{data['barcode']}] {data['product_name']}"
            lbl_prod = Label(
                text=prod_text,
                font_name=FONT_NAME,
                font_size=dp(13),
                bold=True,
                color=get_color_from_hex("#1565C0"),
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                size_hint_y=None,
                height=dp(22)
            )
            lbl_prod.bind(size=lambda i, s: setattr(i, "text_size", s))
            card.add_widget(lbl_prod)

            lbl_partner = Label(
                text=f"• 파트너명: {data['partner']}",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                size_hint_y=None,
                height=dp(18)
            )
            lbl_partner.bind(size=lambda i, s: setattr(i, "text_size", s))
            card.add_widget(lbl_partner)

            lbl_info = Label(
                text=f"• 출고위치: [b]{data['location']}[/b]  |  B2C재고: [b][color=D32F2F]{data['loc_qty']}개[/color][/b]",
                font_name=FONT_NAME,
                font_size=dp(12),
                markup=True,
                color=TEXT_DARK,
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(18)
            )
            lbl_info.bind(size=lambda i, s: setattr(i, "text_size", s))
            card.add_widget(lbl_info)

            card.bind(on_release=lambda inst, d=data: self._send_request(d))
            self.results_grid.add_widget(card)

    def _send_request(self, data):
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip()

        def _async_send():
            try:
                sheet = get_worksheet("도급 보충 요청 시트")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                req_id = f"REQ-{datetime.now().strftime('%M%S')}"
                
                row_data = [
                    req_id,
                    ts,
                    user_name,
                    data["partner"],
                    data["product_name"],
                    data["barcode"],
                    data["location"],
                    "라인 재고 부족 / 보충 필요",
                    "요청중",
                    "",
                    ""
                ]
                sheet.append_row(row_data)
                invalidate_cache("도급 보충 요청 시트")
                
                # 💡 [핵심 보완] 구글 시트 저장 반영 대기(0.5초) 후 강제 최신화 갱신
                time.sleep(0.5)
                self.fetch_status_data(force_refresh=True)

                Clock.schedule_once(lambda dt: app.show_toast("데스크로 보충 요청이 전송되었습니다!"))
                Clock.schedule_once(lambda dt: self.switch_view("STATUS"))
            except Exception as e:
                Clock.schedule_once(lambda dt: app.show_info_popup("오류", f"보충 요청 전송 실패: {e}"))

        app.show_confirmation_popup(
            title="긴급 보충 요청",
            message=f"[{data['barcode']}]\n{data['product_name'][:18]}\n\n데스크로 긴급 보충 요청을 전송하시겠습니까?",
            on_yes=lambda: threading.Thread(target=_async_send, daemon=True).start()
        )

    # 💡 [속도 보완] 메모리 데이터(`self.raw_requests_cache`)를 사용하여 초고속 화면 렌더링
    def _render_status_view(self):
        self.content_area.clear_widgets()

        status_container = BoxLayout(orientation="vertical", spacing=dp(6))

        filter_bar = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(34))
        
        statuses = [
            ("ALL", "전체"),
            ("PENDING", "요청중"),
            ("DONE", "확인완료")
        ]

        for code, label_text in statuses:
            btn_st = StyledToggleButton(
                text=label_text,
                size_hint_x=0.33,
                font_size=dp(12),
                group="status_filter_grp",
                state="down" if self.status_filter == code else "normal"
            )
            btn_st.bind(on_release=lambda inst, c=code: self._set_status_filter(c))
            filter_bar.add_widget(btn_st)

        status_container.add_widget(filter_bar)

        scroll = ScrollView(size_hint=(1, 1))
        status_grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        status_grid.bind(minimum_height=status_grid.setter("height"))
        scroll.add_widget(status_grid)

        now = datetime.now()
        cutoff_time = now - timedelta(hours=24)
        
        valid_requests = []
        for req in self.raw_requests_cache:
            req_id = str(t(req, "요청 ID", t(req, "요청ID", ""))).strip()
            
            if req_id in self.hidden_req_ids:
                continue

            ts_str = str(t(req, "요청시각", "")).strip()
            if ts_str:
                try:
                    req_dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if req_dt < cutoff_time:
                        continue
                except Exception:
                    pass
            
            req_status = str(t(req, "처리상태", "요청중")).strip()

            if self.status_filter == "PENDING" and req_status != "요청중":
                continue
            elif self.status_filter == "DONE" and req_status == "요청중":
                continue

            valid_requests.append(req)

        display_requests = valid_requests[-20:]

        if not display_requests:
            status_grid.add_widget(
                Label(text="해당 상태의 내 보충 요청 내역이 없습니다.", 
                      font_name=FONT_NAME, font_size=dp(13), size_hint_y=None, height=dp(60), color=TEXT_MUTED, halign="center")
            )
        else:
            for req in reversed(display_requests):
                status = str(t(req, "처리상태", "요청중")).strip()
                reply_msg = str(t(req, "회신 메세지", t(req, "회신메시지", ""))).strip()
                manager_name = str(t(req, "담당자", "")).strip()
                bc = str(t(req, "바코드", "")).strip()
                sku_name = str(t(req, "SKU명", t(req, "상품명", ""))).strip()
                partner_name = str(t(req, "고객사", t(req, "파트너명", "-"))).strip()
                req_id = str(t(req, "요청 ID", t(req, "요청ID", ""))).strip()
                ts_raw = str(t(req, "요청시각", "")).strip()
                ts = ts_raw.split()[-1] if len(ts_raw.split()) > 1 else ts_raw

                bg_hex = "#FFFFFF"
                if "보충지시 완료" in status or "보충지시완료" in status or "지시" in status:
                    bg_hex = "#E0F2F1"
                elif "조치안내" in status or "회신" in status:
                    bg_hex = "#FFE0B2"
                elif "재고없음" in status or "품절" in status:
                    bg_hex = "#FFCDD2"

                card_box = TouchableBox(
                    orientation="vertical", 
                    padding=(dp(12), dp(8)), 
                    spacing=dp(3), 
                    size_hint_y=None, 
                    height=dp(118)
                )
                with card_box.canvas.before:
                    Color(rgba=get_color_from_hex(bg_hex))
                    bg_r = RoundedRectangle(pos=card_box.pos, size=card_box.size, radius=[dp(8)])
                card_box.bind(
                    pos=lambda inst, val, b=bg_r: setattr(b, "pos", val), 
                    size=lambda inst, val, b=bg_r: setattr(b, "size", val)
                )

                id_tag = f"[{req_id}] " if req_id else ""
                lbl_sku = Label(
                    text=f"{id_tag}[{bc}] {sku_name}",
                    font_name=FONT_NAME,
                    font_size=dp(13),
                    bold=True,
                    color=get_color_from_hex("#1565C0"),
                    size_hint_y=None,
                    height=dp(22),
                    halign="left",
                    valign="middle",
                    shorten=True,
                    shorten_from="right"
                )
                lbl_sku.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                card_box.add_widget(lbl_sku)

                lbl_client = Label(
                    text=f"• 고객사명: {partner_name}",
                    font_name=FONT_NAME,
                    font_size=dp(12),
                    color=TEXT_DARK,
                    size_hint_y=None,
                    height=dp(18),
                    halign="left",
                    valign="middle",
                    shorten=True,
                    shorten_from="right"
                )
                lbl_client.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                card_box.add_widget(lbl_client)

                mgr_text = f" (담당: {manager_name})" if manager_name else ""
                lbl_status_row = Label(
                    text=f"• 상태: [b]{status}[/b]{mgr_text}  |  요청시각: {ts}",
                    font_name=FONT_NAME,
                    font_size=dp(12),
                    markup=True,
                    color=TEXT_DARK,
                    size_hint_y=None,
                    height=dp(18),
                    halign="left",
                    valign="middle"
                )
                lbl_status_row.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                card_box.add_widget(lbl_status_row)

                reply_row = BoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(26))

                if reply_msg:
                    reply_text = f"• 회신: {reply_msg}"
                    reply_color = get_color_from_hex("#D84315")
                elif status == "요청중":
                    reply_text = "• 회신: 회신 대기 중..."
                    reply_color = TEXT_MUTED
                else:
                    reply_text = "• 회신: -"
                    reply_color = TEXT_MUTED

                lbl_reply = Label(
                    text=reply_text,
                    font_name=FONT_NAME,
                    font_size=dp(12),
                    bold=True if reply_msg else False,
                    color=reply_color,
                    halign="left",
                    valign="middle",
                    shorten=True,
                    shorten_from="right"
                )
                lbl_reply.bind(size=lambda inst, val: setattr(inst, "text_size", val))
                reply_row.add_widget(lbl_reply)

                if ("조치안내" in status or "재고없음" in status or reply_msg) and "완료" not in status:
                    btn_rereq = StyledButton(
                        text="재요청",
                        size_hint_x=None,
                        width=dp(55),
                        font_size=dp(11),
                        bg_color=get_color_from_hex("#E65100")
                    )
                    btn_rereq.bind(on_release=lambda inst, r=req: self._prompt_re_request(r))
                    reply_row.add_widget(btn_rereq)

                btn_delete = StyledButton(
                    text="삭제",
                    size_hint_x=None,
                    width=dp(50),
                    font_size=dp(11),
                    bg_color=get_color_from_hex("#D32F2F")
                )
                btn_delete.bind(on_release=lambda inst, r=req: self._prompt_delete_request(r))
                reply_row.add_widget(btn_delete)

                card_box.add_widget(reply_row)
                status_grid.add_widget(card_box)

        status_container.add_widget(scroll)
        self.content_area.add_widget(status_container)

    def _set_status_filter(self, code):
        self.status_filter = code
        self._render_status_view()

    def _prompt_delete_request(self, req_data):
        app = App.get_running_app()
        req_id = str(t(req_data, "요청 ID", t(req_data, "요청ID", ""))).strip()
        sku_name = str(t(req_data, "SKU명", t(req_data, "상품명", ""))).strip()

        def _do_local_delete():
            if req_id:
                self.hidden_req_ids.add(req_id)
            app.show_toast("어플 화면에서 삭제되었습니다. (시트 데이터 변경 없음)")
            self._render_status_view()

        app.show_confirmation_popup(
            title="보충 요청 삭제",
            message=f"[{sku_name[:18]}]\n\n이 요청 항목을 어플 목록에서 지우시겠습니까?\n(구글 시트에는 영향을 주지 않습니다)",
            on_yes=_do_local_delete
        )

    def _prompt_re_request(self, req_data):
        app = App.get_running_app()
        req_id = str(t(req_data, "요청 ID", t(req_data, "요청ID", ""))).strip()
        sku_name = str(t(req_data, "SKU명", t(req_data, "상품명", ""))).strip()

        # 기존 기록 데이터 추출
        old_reason = str(t(req_data, "요청사유", "")).strip()
        old_reply = str(t(req_data, "회신 메세지", t(req_data, "회신메시지", ""))).strip()

        def _async_re_send():
            try:
                sheet = get_worksheet("도급 보충 요청 시트")
                headers = [str(h).strip() for h in sheet.row_values(1)]
                
                req_id_col = headers.index("요청 ID") + 1 if "요청 ID" in headers else headers.index("요청ID") + 1
                all_ids = sheet.col_values(req_id_col)

                if req_id in all_ids:
                    row_idx = all_ids.index(req_id) + 1
                    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 💡 기존 이력 보존하여 요청사유 업데이트
                    # (기존 사유/회신 메시지가 있으면 뒤에 누적 기록)
                    history_text = ""
                    if old_reply:
                        history_text = f" (이전회신: {old_reply})"
                    
                    new_reason = f"[재요청 {now_ts[-8:-3]}] 라인 재고 재확인 요청{history_text}"
                    if old_reason:
                        updated_reason = f"{old_reason}\n{new_reason}"
                    else:
                        updated_reason = new_reason

                    # 💡 기존 행의 지정된 컬럼만 최신화 (상태: '요청중', 회신 메세지: 초기화)
                    cells = [
                        gspread.Cell(row_idx, headers.index("요청시각") + 1, now_ts),
                        gspread.Cell(row_idx, headers.index("요청사유") + 1, updated_reason),
                        gspread.Cell(row_idx, headers.index("처리상태") + 1, "요청중"),
                        gspread.Cell(row_idx, headers.index("회신 메세지") + 1, "")  # 회신란은 초기화하여 새 회신 대기
                    ]
                    
                    sheet.update_cells(cells)
                    invalidate_cache("도급 보충 요청 시트")
                    
                    time.sleep(0.5)
                    self.fetch_status_data(force_refresh=True)

                    Clock.schedule_once(lambda dt: app.show_toast("데스크로 재요청이 전송되었습니다!"))
            except Exception as e:
                Clock.schedule_once(lambda dt: app.show_info_popup("오류", f"재요청 전송 실패: {e}"))

        app.show_confirmation_popup(
            title="보충 재요청",
            message=f"[{sku_name[:18]}]\n\n기존 요청건({req_id})의 상태를\n'요청중'으로 최신화하여 재전송하시겠습니까?",
            on_yes=lambda: threading.Thread(target=_async_re_send, daemon=True).start()
        )

class AdminDashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_tasks = []
        self.raw_inventory = []
        self.layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )

        top_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        top_bar.add_widget(
            StyledButton(
                text="< 메인",
                size_hint_x=0.15,
                bg_color=get_color_from_hex("#78909C"),
                on_press=lambda x: setattr(
                    self.manager, "current", "main_menu"
                ),
            )
        )
        top_bar.add_widget(
            Label(
                text="전체 작업 현황판",
                font_name=FONT_NAME,
                font_size=dp(15),
                bold=True,
                color=TEXT_DARK,
                size_hint_x=0.35,
            )
        )
        top_bar.add_widget(
            StyledButton(
                text="갱신", size_hint_x=0.15, on_press=lambda x: self.refresh()
            )
        )

        # AdminDashboardScreen __init__ 내 상단 바 구역
        btn_emergency_chat = StyledButton(
            text="보충요청/소통",
            size_hint_x=0.35,
            font_size=dp(12),
            bg_color=get_color_from_hex("#D32F2F")
        )
        # 💡 [보정] 안전한 화면 전환 바인딩
        btn_emergency_chat.bind(
            on_release=lambda inst: Clock.schedule_once(
                lambda dt: setattr(self.manager, "current", "emergency_replenish"), 0.05
            )
        )
        top_bar.add_widget(btn_emergency_chat)
        self.layout.add_widget(top_bar)

        search_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        self.search_input = TextInput(
            hint_text="터치하여 바코드/SKU 검색",
            multiline=False,
            font_name=FONT_NAME,
            font_size=dp(15),
            size_hint_x=0.8,
            readonly=True,
        )
        self.search_input.bind(on_touch_down=self.on_search_touch)

        btn_search = StyledButton(
            text="검색", size_hint_x=0.2, font_size=dp(14)
        )
        btn_search.bind(on_press=self.search_tasks)

        search_bar.add_widget(self.search_input)
        search_bar.add_widget(btn_search)
        self.layout.add_widget(search_bar)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_search_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            def set_query(val):
                self.search_input.text = val
                self.search_tasks()

            open_native_korean_input(
                "검색어 입력", "바코드 또는 SKU 검색", "", set_query
            )
            return True
        return False

    def on_enter(self):
        app = App.get_running_app()
        if not app.user_real_name:
            app.user_real_name = app.load_saved_user_name() or ""
            if not app.user_real_name:
                self.manager.current = "name_entry"
                return

        self.search_input.text = ""
        self.grid.clear_widgets()
        self.grid.add_widget(
            Label(
                text="바코드를 스캔하거나 입력 후 검색해 주세요.",
                font_name=FONT_NAME,
                font_size=dp(15),
                color=TEXT_MUTED,
                size_hint_y=None,
                height=dp(100),
            )
        )

        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_all, daemon=True).start()

    def refresh(self, instance=None):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_all, daemon=True).start()

    def _async_fetch_all(self):
        try:
            tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=True)
            inventory = get_sheet_data(LOCATION_CAPA_SHEET_NAME, force_refresh=True)
            self.all_tasks = tasks
            self.raw_inventory = inventory
            Clock.schedule_once(lambda dt: self.search_tasks())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", str(err)
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def handle_barcode_scan(self, barcode):
        self.search_input.text = str(barcode).strip()
        self.search_tasks()

    def search_tasks(self, instance=None):
        query = self.search_input.text.strip().lower()
        self.grid.clear_widgets()

        if not query:
            self.grid.add_widget(
                Label(
                    text="바코드를 스캔하거나 입력 후 검색해 주세요.",
                    font_name=FONT_NAME,
                    font_size=dp(15),
                    color=TEXT_MUTED,
                    size_hint_y=None,
                    height=dp(100),
                )
            )
            return

        matches = []
        for task in self.all_tasks:
            bc = get_barcode_from_task(task).lower()
            sku = str(t(task, "상품명", "")).strip().lower()
            if query in bc or query in sku:
                matches.append(task)

        if not matches:
            self.grid.add_widget(
                Label(
                    text=f"검색어 [{query}] 에 해당하는 작업 건이 없습니다.",
                    font_name=FONT_NAME,
                    font_size=dp(14),
                    color=TEXT_MUTED,
                    size_hint_y=None,
                    height=dp(100),
                )
            )
            return

        for task in matches:
            self.grid.add_widget(self._create_dashboard_card(task))

    def toggle_urgent_status(self, task_data, card_widget):
        task_id = str(t(task_data, "작업ID")).strip()
        current_urg = task_data.get("긴급여부") == "Y"
        new_urg_val = "N" if current_urg else "Y"
        action_name = "긴급해제" if current_urg else "긴급전환"

        def perform_toggle():
            App.get_running_app().show_loading_popup()
            threading.Thread(
                target=self._async_toggle_urgent,
                args=(
                    task_id,
                    new_urg_val,
                    action_name,
                    task_data,
                    card_widget,
                ),
                daemon=True,
            ).start()

        App.get_running_app().show_confirmation_popup(
            title=f"{action_name} 확인",
            message=f"해당 작업을 [{action_name}] 처리하시겠습니까?",
            on_yes=perform_toggle,
        )

    def _async_toggle_urgent(
        self, task_id, new_urg_val, action_name, task_data, card_widget
    ):
        try:
            sheet = get_worksheet(TASK_SHEET_NAME)
            headers = [str(h).strip() for h in sheet.row_values(1)]

            if "긴급여부" not in headers or "작업ID" not in headers:
                raise Exception(
                    "시트에 '긴급여부' 또는 '작업ID' 열이 존재하지 않습니다."
                )

            task_id_col = headers.index("작업ID") + 1
            urg_col = headers.index("긴급여부") + 1

            all_ids = sheet.col_values(task_id_col)
            if task_id not in all_ids:
                raise Exception(
                    f"작업ID [{task_id}]를 시트에서 찾을 수 없습니다."
                )

            row_idx = all_ids.index(task_id) + 1
            sheet.update_cell(row_idx, urg_col, new_urg_val)

            task_data["긴급여부"] = new_urg_val
            for task in self.all_tasks:
                if str(t(task, "작업ID")).strip() == task_id:
                    task["긴급여부"] = new_urg_val
                    break

            invalidate_cache(TASK_SHEET_NAME)

            Clock.schedule_once(
                lambda dt: App.get_running_app().show_toast(
                    f"[{action_name}] 처리가 완료되었습니다."
                )
            )
            # 💡 [핵심] 처리 완료 직후 현황판 즉시 자동 갱신
            Clock.schedule_once(lambda dt: self.refresh(None), 0.2)

        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup(
                    "오류", f"긴급 처리 중 오류: {e}"
                )
            )
        finally:
            Clock.schedule_once(
                lambda dt: App.get_running_app().dismiss_loading_popup()
            )

    def _create_dashboard_card(self, task):
        status = str(t(task, "상태", "대기")).strip()
        is_urgent = t(task, "긴급여부") == "Y"
        barcode_val = get_barcode_from_task(task)

        out_stock_qty = 0
        if barcode_val != "N/A" and self.raw_inventory:
            for row in self.raw_inventory:
                loc_type = str(t(row, "로케이션 유형", "")).strip()
                bc = str(t(row, "바코드", t(row, "상품바코드", ""))).strip()
                if loc_type == "B2C출고" and bc == barcode_val:
                    out_stock_qty += safe_int(t(row, "로케이션 수량", 0))

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(132),
            padding=dp(10),
            spacing=dp(3),
        )

        bg_color = get_color_from_hex("#FFCDD2") if is_urgent else [1, 1, 1, 1]

        with card.canvas.before:
            Color(*bg_color)
            RoundedRectangle(
                pos=card.pos, size=card.size, radius=[dp(10)]
            )
        card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        top_row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(5))
        st_color = (
            "[color=1E88E5]"
            if status == "작업중"
            else (
                "[color=00897B]"
                if status in ["적치대기", "최종완료"]
                else (
                    "[color=E65100]" if status == "보충실패" else "[color=757575]"
                )
            )
        )
        urg_tag = "[color=D32F2F][긴급][/color] " if is_urgent else ""

        lbl_status = Label(
            text=f"{st_color}[b][{status}][/b][/color] {urg_tag}",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            halign="left",
            valign="middle",
        )
        lbl_status.bind(size=lambda i, s: setattr(i, "text_size", s))
        top_row.add_widget(lbl_status)

        btn_urg_toggle = StyledButton(
            text="긴급 해제" if is_urgent else "긴급 전환",
            size_hint_x=None,
            width=dp(75),
            font_size=dp(11),
            bg_color=(
                get_color_from_hex("#D32F2F")
                if not is_urgent
                else get_color_from_hex("#78909C")
            ),
        )
        btn_urg_toggle.bind(
            on_press=lambda x: self.toggle_urgent_status(task, card)
        )
        top_row.add_widget(btn_urg_toggle)

        card.add_widget(top_row)

        product_name = str(t(task, "상품명", "N/A")).strip()
        lbl_prod = Label(
            text=f"[b]{product_name}[/b]",
            font_name=FONT_NAME,
            font_size=dp(14),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(22),
        )
        lbl_prod.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_prod)

        lbl_bc = Label(
            text=f"바코드: [b][color=1E88E5]{barcode_val}[/color][/b]",
            font_name=FONT_NAME,
            font_size=dp(13),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        lbl_bc.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_bc)

        to_loc = str(t(task, "보충로케이션", "-")).strip()
        lbl_info = Label(
            text=f"출고 위치: [b][color=1E88E5]{to_loc}[/color][/b]  │  📦 B2C출고재고: [b][color=D32F2F]{out_stock_qty}개[/color][/b] [color=757575](정확한 수량 X / 참고용)[/color]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        lbl_info.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_info)

        req_qty = t(task, "지시수량", 0)
        conf_qty = t(task, "확인수량", 0)
        raw_time = str(t(task, "완료일시", t(task, "최종완료일시", ""))).strip()

        time_str = ""
        if status in ["적치대기", "최종완료", "완료"] and raw_time:
            time_str = f" | [color=2E7D32][b]완료시간: {raw_time}[/b][/color]"

        lbl_sub = Label(
            text=f"지시: {req_qty} / 확인: {conf_qty}{time_str}",
            font_name=FONT_NAME,
            font_size=dp(12),
            color=TEXT_MUTED,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        lbl_sub.bind(size=lambda i, s: setattr(i, "text_size", s))
        card.add_widget(lbl_sub)

        return card


class CompletedHistoryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )
        top = BoxLayout(size_hint_y=None, height=dp(45))
        top.add_widget(
            StyledButton(
                text="< 메인",
                size_hint_x=0.2,
                bg_color=get_color_from_hex("#78909C"),
                on_press=lambda x: setattr(
                    self.manager, "current", "main_menu"
                ),
            )
        )
        top.add_widget(
            Label(
                text="금일 완료 이력",
                font_name=FONT_NAME,
                font_size=dp(18),
                bold=True,
                color=TEXT_DARK,
            )
        )
        layout.add_widget(top)
        self.add_widget(layout)


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )
        header = BoxLayout(size_hint_y=None, height=dp(45))
        header.add_widget(
            StyledButton(
                text="< 메인",
                size_hint_x=0.2,
                bg_color=get_color_from_hex("#78909C"),
                on_press=lambda x: setattr(
                    self.manager, "current", "main_menu"
                ),
            )
        )
        header.add_widget(
            Label(
                text="프린터 설정",
                font_name=FONT_NAME,
                font_size=dp(18),
                bold=True,
                color=TEXT_DARK,
            )
        )
        layout.add_widget(header)
        layout.add_widget(
            StyledButton(
                text="프린터 연결 설정",
                size_hint_y=None,
                height=dp(55),
                on_press=lambda x: Factory.PrinterSettingsPopup().open(),
            )
        )
        self.add_widget(layout)


class PrinterSettingsPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "프린터 설정"
        self.title_font = FONT_NAME
        self.size_hint = (0.9, None)
        self.height = dp(350)
        self.auto_dismiss = False
        self.found_devices = {}
        layout = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )
        self.current_lbl = Label(
            text="현재 프린터: "
            + (App.get_running_app().load_default_printer() or "미설정"),
            font_name=FONT_NAME,
        )
        layout.add_widget(self.current_lbl)
        self.spinner = StyledSpinner(
            text="기기를 선택하세요",
            font_name=FONT_NAME,
            option_cls=KoreanSpinnerOption,
            size_hint_y=None,
            height=dp(45),
        )
        layout.add_widget(self.spinner)

        btn_scan = StyledButton(
            text="주변 기기 검색",
            on_press=self.scan_devices,
            size_hint_y=None,
            height=dp(45),
        )
        btn_save = StyledButton(
            text="기본 프린터로 저장",
            on_press=self.save_printer,
            size_hint_y=None,
            height=dp(45),
        )
        btn_close = StyledButton(
            text="닫기",
            on_press=self.dismiss,
            size_hint_y=None,
            height=dp(45),
            bg_color=(0.6, 0.6, 0.6, 1),
        )
        layout.add_widget(btn_scan)
        layout.add_widget(btn_save)
        layout.add_widget(btn_close)
        self.content = layout

    def scan_devices(self, instance):
        if platform != "android" or not autoclass:
            return
        try:
            adapter = autoclass(
                "android.bluetooth.BluetoothAdapter"
            ).getDefaultAdapter()
            if not adapter.isEnabled():
                return
            self.found_devices.clear()
            for dev in adapter.getBondedDevices().toArray():
                self.found_devices[dev.getName()] = dev.getAddress()
            self.spinner.values = (
                list(self.found_devices.keys())
                if self.found_devices
                else ["페어링된 기기 없음"]
            )
        except Exception:
            pass

    def save_printer(self, instance):
        name = self.spinner.text
        if name in self.found_devices:
            App.get_running_app().save_default_printer(
                self.found_devices[name]
            )
            self.current_lbl.text = "현재 프린터: " + self.found_devices[name]
            self.dismiss()


class BluetoothPrinter:

    def __init__(self, device_address):
        self.mac_address = device_address
        self.socket = None
        self.stream = None

    def connect(self):
        if platform != "android":
            return False

        for attempt in range(2):
            try:
                BluetoothAdapter = autoclass(
                    "android.bluetooth.BluetoothAdapter"
                )
                UUID = autoclass("java.util.UUID")
                device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(
                    self.mac_address
                )
                spp_uuid = UUID.fromString(
                    "00001101-0000-1000-8000-00805F9B34FB"
                )
                self.socket = device.createRfcommSocketToServiceRecord(
                    spp_uuid
                )
                self.socket.connect()
                self.stream = self.socket.getOutputStream()
                time.sleep(0.3)
                return True
            except Exception as e:
                print(f"⚠️ 블루투스 연결 시도 {attempt + 1}회 실패: {e}")
                self.disconnect()
                time.sleep(0.5)
        return False

    def disconnect(self):
        try:
            if self.stream:
                self.stream.close()
        except Exception:
            pass
        try:
            if self.socket:
                self.socket.close()
        except Exception:
            pass
        self.stream = None
        self.socket = None

    # 💡 [보정] 하단 수량 잘림 방지 (구분선 위치 바짝 올림 & 폰트 크기/좌표 축소)
    def print_outbound_label_cpcl(self, label_info: dict, quantity: int):
        if not self.stream:
            return False

        try:
            barcode_suffix = label_info.get("바코드", "N/A")[-6:]
            from_loc = label_info.get("보관 로케이션", "N/A")
            loc_raw = label_info.get("출고 로케이션", "N/A")
            loc1 = loc_raw.split("-", 1)[0] if "-" in loc_raw else loc_raw
            loc2 = loc_raw.split("-", 1)[1] if "-" in loc_raw else ""

            is_urgent = label_info.get("긴급여부", False)
            is_invoice_only = label_info.get("송장전용", False)

            conf_qty = safe_int(label_info.get("확인수량", 0))
            box_size = safe_int(label_info.get("박스입수량", 1))
            if box_size <= 0:
                box_size = 1

            tag_str = ""
            if is_urgent:
                tag_str += "[긴급건] "
            if is_invoice_only:
                tag_str += "[송장만]"

            # 박스 / 낱개 계산 수식 문자열 생성
            if box_size > 1:
                b_cnt = conf_qty // box_size
                e_cnt = conf_qty % box_size
                qty_str = f"수량 : {conf_qty} ({b_cnt} BOX + {e_cnt} EA)"
            else:
                qty_str = f"수량 : {conf_qty} ({conf_qty} EA)"

            # CPCL 인쇄 명령 구성
            cmd = f"! 0 200 200 800 {quantity}\r\nLEFT\r\nSETMAG 1 1\r\nTEXT 4 1 20 35 [보관] {from_loc}\r\n"
            cmd += f"SETMAG 2 2\r\nTEXT 4 1 20 75 {barcode_suffix}\r\n"
            if tag_str:
                cmd += f"RIGHT\r\nSETMAG 2 2\r\nTEXT 4 1 500 75 {tag_str}\r\nLEFT\r\n"

            # 1. 상단 구분선 및 중앙 출고 로케이션 영역
            cmd += f"LINE 20 165 556 165 4\r\nCENTER\r\nSETMAG 4 4\r\nTEXT 4 1 0 210 {loc1}\r\nSETMAG 3 3\r\nTEXT 4 1 0 380 {loc2}\r\n"

            # 💡 2. 하단 구분선 위치를 Y=500으로 바짝 올림 (기존 540에서 위로 40px 이동)
            cmd += f"LINE 20 500 556 500 3\r\nLEFT\r\n"

            # 💡 3. 수량 폰트 크기를 SETMAG 1 2 로 축소 (가로 비율 줄임) 및 Y=520 위치에 출력 (잘림 완전 방지)
            cmd += f"SETMAG 1 2\r\nTEXT 4 1 20 520 {qty_str}\r\nSETMAG 1 1\r\nFORM\r\nPRINT\r\n"

            self.stream.write(cmd.encode("cp949"))
            self.stream.flush()
            time.sleep(0.2)
            # ------------------ 💡 [여기서부터 추가!] ------------------
            box_size = safe_int(label_info.get("박스입수량", 1))
            sku_name = str(label_info.get("상품명", label_info.get("SKU명", "")))
            is_invoice_only = label_info.get("송장전용", False)

            # 💡 입수량이 1이거나 SKU명/상품명에 '(송장만부착)'이 들어있으면 팝업 노출
            if (box_size == 1) or ("(송장만부착)" in sku_name) or is_invoice_only:
                Clock.schedule_once(
                    lambda dt: App.get_running_app().show_info_popup(
                        " 수기 작성 절대 금지",
                        "해당 상품은 [단품/송장만부착] 출고 박스입니다!\n\n"
                        "라벨이 붙지 않은 나머지 박스 겉면에\n"
                        "[매직/펜으로 로케이션을 적지 마세요]\n\n"
                        "※ 박스 훼손 시 반품 사유가 됩니다.",
                    )
                )
            # ------------------ 💡 [여기까지 추가!] ------------------
            return True
        except Exception as e:
            print(f"🔴 CPCL 전송 중 에러: {e}")
            return False
        finally:
            self.disconnect()


Builder.load_string(
    """
<TaskListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        BoxLayout:
            size_hint_y: None
            height: dp(45)
            spacing: dp(10)
            
            StyledButton:
                text: '< 메인'
                size_hint_x: 0.25
                on_press: root.manager.current = 'main_menu'
            Label:
                text: '검수 목록 보기'
                size_hint_x: 0.5
                font_name: app.FONT_NAME
                font_size: dp(18)
                bold: True
                color: (0.1, 0.1, 0.1, 1)
            StyledButton:
                text: '새로고침'
                size_hint_x: 0.25
                on_press: root.refresh_list(force_refresh=True, show_loading=True)

        BoxLayout:
            size_hint_y: None
            height: dp(45)
            spacing: dp(5)
            TextInput:
                id: search_input
                hint_text: 'SKU명 또는 바코드 검색'
                multiline: False
                font_name: app.FONT_NAME
                size_hint_x: 0.8
                readonly: True  # 💡 [추가] 직접키보드 입력 방지 (포커스로 인한 v 입력 차단)
                on_touch_down: root.on_search_touch(self, args[1])  # 💡 [추가]
            StyledButton:
                text: '검색'
                size_hint_x: 0.2
                on_press: root.search_tasks()

        RecycleView:
            id: task_list_rv
            viewclass: 'UnifiedTaskCard'
            RecycleBoxLayout:
                default_size: None, dp(218)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(8)

<UnifiedTaskCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(10)
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: root.card_bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12),]

    BoxLayout:
        size_hint_y: None
        height: dp(26)
        spacing: dp(5)
        Label:
            id: lbl_equip
            font_name: app.FONT_NAME
            font_size: dp(14)
            halign: 'left'
            valign: 'middle'
            markup: True
            size_hint_x: 0.45
            text_size: self.width, None
        Label:
            id: lbl_stock_info
            font_name: app.FONT_NAME
            font_size: dp(12)
            color: (0.3, 0.3, 0.3, 1)
            halign: 'right'
            valign: 'middle'
            markup: True
            size_hint_x: 0.45
            text_size: self.width, None
        CheckBox:
            id: box_check
            size_hint_x: None
            width: dp(30)
            color: (0.12, 0.53, 0.9, 1)
            on_active: root.on_checkbox_active(self, self.active)

    Label:
        id: lbl_product
        font_name: app.FONT_NAME
        font_size: dp(15)
        color: (0,0,0,1)
        halign: 'left'
        valign: 'middle'
        markup: True
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
        on_texture_size: self.height = self.texture_size[1]

    BoxLayout:
        size_hint_y: None
        height: dp(18)
        Label:
            id: lbl_barcode
            font_name: app.FONT_NAME
            font_size: dp(12)
            color: (0.4, 0.4, 0.4, 1)
            halign: 'left'
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: dp(25)
        Label:
            id: lbl_loc
            font_name: app.FONT_NAME
            font_size: dp(16)
            bold: True
            markup: True
            halign: 'left'
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: dp(26)
        Label:
            id: lbl_main_qty
            font_name: app.FONT_NAME
            font_size: dp(18)
            bold: True
            halign: 'left'
            valign: 'middle'
            markup: True
            color: (0.12, 0.53, 0.9, 1)
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: dp(18)
        Label:
            id: lbl_box_info
            font_name: app.FONT_NAME
            font_size: dp(12)
            color: (0.3, 0.3, 0.3, 1)
            markup: True
            halign: 'left'
            text_size: self.width, None

    GridLayout:
        id: btn_action_box
        cols: 5
        size_hint_y: None
        height: dp(40)
        spacing: dp(4)
        opacity: 0
        disabled: True

        StyledButton:
            text: "반납"
            font_size: dp(12)
            bg_color: (0.9, 0.6, 0, 1)
            on_press: root.handle_card_btn('return')
        StyledButton:
            id: btn_qty_input  # 👈 [핵심] ID 추가
            text: "수량입력"
            font_size: dp(12)
            on_press: root.handle_card_btn('qty')
        StyledButton:
            text: "실패"
            font_size: dp(12)
            bg_color: (1, 0.3, 0.3, 1)
            on_press: root.handle_card_btn('fail')
        StyledButton:
            text: "비고"
            font_size: dp(12)
            on_press: root.handle_card_btn('remarks')
        StyledButton:
            text: "완료"
            font_size: dp(12)
            bg_color: (0.1, 0.8, 0.5, 1)
            on_press: root.handle_card_btn('complete')
"""
)

Factory.register("PrinterSettingsPopup", cls=PrinterSettingsPopup)

class MultiLocationSelectPopup(Popup):
    def __init__(self, locations, on_select, **kwargs):
        super().__init__(**kwargs)
        self.title = "로케이션 상세 층수 선택"
        self.title_font = FONT_NAME
        self.size_hint = (0.85, None)
        self.height = dp(80) + (len(locations) * dp(50))
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(
            text="하나의 QR에 여러 로케이션이 존재합니다.\n적치하신 [color=FF9800][b]정확한 층수[/b][/color]를 선택해 주세요.", 
            font_name=FONT_NAME, markup=True, halign="center", size_hint_y=None, height=dp(40)
        ))
        
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        
        for loc in locations:
            btn = StyledButton(text=f"📍 {loc}", size_hint_y=None, height=dp(45), bg_color=PRIMARY_BLUE)
            btn.bind(on_release=lambda inst, l=loc: (on_select(l), self.dismiss()))
            grid.add_widget(btn)
            
        btn_cancel = StyledButton(text="취소", size_hint_y=None, height=dp(40), bg_color=get_color_from_hex("#78909C"))
        btn_cancel.bind(on_press=self.dismiss)
        
        layout.add_widget(grid)
        layout.add_widget(btn_cancel)
        self.content = layout

class ReturnInspectionPopup(Popup):
    def __init__(self, card_data, task_list_screen, **kwargs):
        super().__init__(**kwargs)
        self.task_data = card_data
        self.task_list_screen = task_list_screen
        self.assign_type = str(t(self.task_data, "지정구분", "지정")).strip()
        self.target_location = str(t(self.task_data, "원복로케이션", "")).strip().upper()
        self.current_remarks = str(t(self.task_data, "비고", ""))
        
        self.title = "원복 수량 입력 및 로케이션 스캔 (사진 촬영)"
        self.title_font = FONT_NAME
        self.size_hint = (0.95, None)
        self.height = dp(650)  # 수량 칸이 들어가므로 높이 확장
        self.auto_dismiss = False
        
        main_layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        
        # 💡 1. 다중 추천/지정 로케이션 표시 영역 (흰색 글씨로 시인성 확보)
        self.recommend_lbl = Label(
            text="로케이션 정보를 분석 중입니다...", 
            font_name=FONT_NAME, markup=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(100)
        )
        main_layout.add_widget(self.recommend_lbl)
        
        # 💡 2. 수량 입력 구역 (보충 검수 화면과 완벽 동일)
        total_qty = safe_int(t(self.task_data, "지시수량", 0))
        default_box_size = safe_int(t(self.task_data, "박스입수량", 1))
        if default_box_size <= 0: default_box_size = 1
        
        info_label = Label(
            text=f"지시수량: [b]{total_qty}[/b] / 기본입수량: [b]{default_box_size}[/b]",
            font_name=FONT_NAME, font_size=dp(15), markup=True, size_hint_y=None, height=dp(25), color=(1, 1, 1, 1)
        )
        main_layout.add_widget(info_label)
        
        input_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(150))
        input_grid.add_widget(Label(text=f"박스 입수량 (기존 {default_box_size}):", font_name=FONT_NAME, font_size=dp(14), color=(1, 1, 1, 1)))
        self.box_size_input = TextInput(text=str(default_box_size), multiline=False, input_type="number", font_name=FONT_NAME, font_size=dp(18), halign="center", readonly=True)
        self.box_size_input.bind(on_touch_down=lambda instance, touch: self._touch_input(instance, touch, "박스 입수량 입력", True))
        input_grid.add_widget(self.box_size_input)
        
        input_grid.add_widget(Label(text="박스 수량:", font_name=FONT_NAME, font_size=dp(14), color=(1, 1, 1, 1)))
        self.box_count_input = TextInput(hint_text="0", multiline=False, input_type="number", font_name=FONT_NAME, font_size=dp(18), halign="center", readonly=True)
        self.box_count_input.bind(on_touch_down=lambda instance, touch: self._touch_input(instance, touch, "박스 수량 입력", True))
        input_grid.add_widget(self.box_count_input)
        
        input_grid.add_widget(Label(text="낱개 수량:", font_name=FONT_NAME, font_size=dp(14), color=(1, 1, 1, 1)))
        self.rem_qty_input = TextInput(hint_text="0", multiline=False, input_type="number", font_name=FONT_NAME, font_size=dp(18), halign="center", readonly=True)
        self.rem_qty_input.bind(on_touch_down=lambda instance, touch: self._touch_input(instance, touch, "낱개 수량 입력", True))
        input_grid.add_widget(self.rem_qty_input)
        main_layout.add_widget(input_grid)
        
        # 💡 3. 로케이션 스캔 및 QR없음 버튼
        loc_input_row = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(45))
        self.final_location_input = TextInput(hint_text="로케이션 스캔 시 사진 촬영 진행", multiline=False, font_name=FONT_NAME, font_size=dp(14), size_hint_x=0.7, readonly=True)
        self.final_location_input.bind(on_touch_down=lambda instance, touch: self._touch_input(instance, touch, "로케이션 수기입력", False))
        loc_input_row.add_widget(self.final_location_input)
        
        btn_no_qr = StyledButton(text="QR없음", size_hint_x=0.3, font_size=dp(13), bg_color=get_color_from_hex("#E65100"))
        btn_no_qr.bind(on_press=self.process_no_qr_action)
        loc_input_row.add_widget(btn_no_qr)
        main_layout.add_widget(loc_input_row)
        
        # 💡 4. 취소 및 수기입력 촬영 버튼
        top_button_grid = GridLayout(cols=2, size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_button = StyledButton(text="취소 (뒤로가기)", bg_color=(0.6, 0.6, 0.6, 1))
        cancel_button.bind(on_press=self.dismiss)
        ok_button = StyledButton(text="수기입력 촬영", bg_color=RETURN_GREEN)
        ok_button.bind(on_press=self.confirm_inspection)
        top_button_grid.add_widget(cancel_button)
        top_button_grid.add_widget(ok_button)
        main_layout.add_widget(top_button_grid)
        
        self.content = main_layout
        self.bind(on_open=self._check_recommendation)

    def _touch_input(self, instance, touch, title, is_num):
        if instance.collide_point(*touch.pos):
            def set_val(val):
                instance.text = str(val).strip().upper()
                if not is_num:
                    self.process_location_scan(instance.text)
            open_native_korean_input(title, title, instance.text, set_val, is_number=is_num)
            return True
        return False

    # 💡 [요청 반영] 고객사 라인별 보유 수량 기반 복수 추천
    def _check_recommendation(self, *args):
        if self.assign_type == "지정":
            self.recommend_lbl.text = f"지정된 적치위치: [size=20dp][b][color=64B5F6]{self.target_location}[/color][/b][/size]\n[color=B0BEC5](수량 입력 후 해당 위치를 스캔하세요)[/color]"
            return
            
        def _find_zone():
            client_name = str(t(self.task_data, "고객사", "")).strip()
            if not client_name: 
                Clock.schedule_once(lambda dt: setattr(self.recommend_lbl, 'text', "💡 고객사 정보가 없어 추천할 수 없습니다."))
                return
            
            try:
                inventory = get_sheet_data(LOCATION_CAPA_SHEET_NAME)
                zone_counts = defaultdict(int)
                for row in inventory:
                    if str(t(row, "고객사", t(row, "파트너명", ""))).strip() == client_name:
                        loc = str(t(row, "로케이션", "")).strip().upper()
                        if loc: zone_counts[loc[0] + "존"] += 1
                
                if zone_counts:
                    # 내림차순 정렬 후 상위 3개 추출
                    sorted_zones = sorted(zone_counts.items(), key=lambda x: x[1], reverse=True)
                    top_zone = sorted_zones[0][0]
                    
                    summary_lines = [f"{z}({cnt}라인)" for z, cnt in sorted_zones[:3]]
                    summary_str = " / ".join(summary_lines)
                    
                    disp_text = (
                        f"💡 [b]{client_name}[/b] 보관 라인: {summary_str}\n\n"
                        f"➡️ 추천 빈 적치존: [size=20dp][b][color=FFB300]{top_zone}[/color][/b][/size]"
                    )
                    Clock.schedule_once(lambda dt: setattr(self.recommend_lbl, 'text', disp_text))
                else:
                    Clock.schedule_once(lambda dt: setattr(self.recommend_lbl, 'text', "💡 추천 불가 (고객사 재고 없음)"))
            except Exception:
                pass
                
        threading.Thread(target=_find_zone, daemon=True).start()

    def _get_calculated_qty(self):
        box_size_str = self.box_size_input.text.strip()
        box_count_str = self.box_count_input.text.strip() or "0"
        rem_qty_str = self.rem_qty_input.text.strip() or "0"
        if not box_size_str.isdigit() or not box_count_str.isdigit() or not rem_qty_str.isdigit():
            return -1
        return (int(box_size_str) * int(box_count_str)) + int(rem_qty_str)

    # 💡 QR없음 버튼 액션
    def process_no_qr_action(self, instance):
        qty = self._get_calculated_qty()
        if qty < 0:
            App.get_running_app().show_info_popup("입력 오류", "수량을 올바르게 입력해주세요.")
            return
        if qty == 0:
            App.get_running_app().show_info_popup("수량 입력 필요", "박스/낱개 수량을 먼저 입력해주세요.")
            return
        
        self.task_data["changed_box_size"] = self.box_size_input.text.strip()
        self._verify_qty_and_proceed(qty, self.target_location, no_qr=True)

    # 💡 로케이션 QR 스캔 액션
    def process_location_scan(self, scanned_text):
        qty = self._get_calculated_qty()
        if qty <= 0:
            App.get_running_app().show_info_popup("수량 확인", "수량을 먼저 입력한 뒤 로케이션 QR을 스캔해 주세요.")
            return False
            
        self.task_data["changed_box_size"] = self.box_size_input.text.strip()
        raw_loc = str(scanned_text).replace('\ufeff', '').strip()
        
        if "," in raw_loc:
            loc_list = [l.strip().upper() for l in raw_loc.split(",") if l.strip()]
            if len(loc_list) > 1:
                MultiLocationSelectPopup(locations=loc_list, on_select=lambda loc: self._verify_loc_and_proceed(loc, qty)).open()
                return True
                
        self._verify_loc_and_proceed(re.sub(r'[^A-Za-z0-9\-_]', '', raw_loc).strip().upper(), qty)
        return True

    def confirm_inspection(self, instance):
        scanned_loc = self.final_location_input.text.strip().upper()
        if not scanned_loc:
            App.get_running_app().show_info_popup("스캔 필요", "적치할 로케이션을 스캔하거나 입력해 주세요.")
            return
        self.process_location_scan(scanned_loc)

    def _verify_loc_and_proceed(self, selected_loc, qty):
        app = App.get_running_app()
        if self.assign_type == "지정":
            if selected_loc != self.target_location:
                app.show_info_popup("❌ 로케이션 오류", f"지정된 로케이션이 아닙니다!\n• 올바른 위치: [color=64B5F6]{self.target_location}[/color]\n• 현재 스캔: [color=FF5252]{selected_loc}[/color]")
                return
            self._verify_qty_and_proceed(qty, selected_loc, no_qr=False)
        else:
            self._verify_qty_and_proceed(qty, selected_loc, no_qr=False)

    def _verify_qty_and_proceed(self, final_qty, final_loc, no_qr=False):
        app = App.get_running_app()
        target_qty = safe_int(t(self.task_data, "지시수량", 0))
        
        def do_next():
            if no_qr:
                curr_rem = str(self.current_remarks).strip()
                self.current_remarks = f"{curr_rem}\n[자석로케이션 필요]" if curr_rem else "[자석로케이션 필요]"
            
            # 💡 4단계(카메라)로 수량, 로케이션 정보 전달
            self.task_data["확인수량"] = final_qty
            self.task_data["비고"] = self.current_remarks
            app.show_toast(f"✅ 수량 및 위치 확인 완료\n카메라를 실행합니다.")
            self.task_list_screen.open_camera(final_loc, self.task_data)
            self.dismiss()

        if final_qty != target_qty:
            app.show_confirmation_popup(
                title="[수량 불일치 경고]",
                message=f"지시수량: [color=FF8A80][b]{target_qty}개[/b][/color]\n검수수량: [color=81C784][b]{final_qty}개[/b][/color]\n\n수량이 다릅니다. 이대로 촬영을 진행하시겠습니까?",
                on_yes=do_next
            )
        else:
            do_next()

# =========================================================================
# 💡 원복 작업 통합 컨트롤 화면
# =========================================================================
class ReturnTaskListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_main_tab = "PENDING"
        self.active_equip_filter = "ALL"
        self.only_urgent = False
        self.selected_from_zones = {"전체"}
        self.selected_to_zones = {"전체"}
        self.sort_asc = True
        self.is_filter_expanded = True

        self.raw_all_tasks = []
        self.checked_task_ids = set()

        self.layout = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(4))

        header = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        btn_back = StyledButton(text="< 메인", size_hint_x=0.18, bg_color=get_color_from_hex("#78909C"))
        btn_back.bind(on_press=lambda x: setattr(self.manager, "current", "main_menu"))

        lbl_title = Label(text="원복 작업 통합 컨트롤", font_name=FONT_NAME, font_size=dp(15), bold=True, color=TEXT_DARK)

        # 💡 [수정됨] 갱신 버튼 배경색(RETURN_GREEN) 추가
        btn_refresh = StyledButton(text="갱신", size_hint_x=0.25, font_size=dp(12), bg_color=RETURN_GREEN)
        btn_refresh.bind(on_press=self.refresh_button_click)

        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_refresh)
        self.layout.add_widget(header)

        self.btn_toggle_filter = StyledButton(text="🔍 필터 설정 닫기 ▲ (대기작업 / 전체)", size_hint_y=None, height=dp(32), bg_color=get_color_from_hex("#546E7A"), font_size=dp(12))
        self.btn_toggle_filter.bind(on_press=self.toggle_filter_panel)
        self.layout.add_widget(self.btn_toggle_filter)

        self.filter_panel = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(112), spacing=dp(4))

        main_tab_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(5))
        # 💡 [수정됨] StyledToggleButton ➔ ReturnToggleButton 으로 교체
        self.btn_tab_pending = ReturnToggleButton(text="대기 작업", group="ret_main_tab", state="down", size_hint_x=0.5, font_size=dp(14), markup=True)
        self.btn_tab_pending.bind(on_press=lambda x: self.switch_main_tab("PENDING"))

        # 💡 [수정됨] StyledToggleButton ➔ ReturnToggleButton 으로 교체
        self.btn_tab_my = ReturnToggleButton(text="내 작업", group="ret_main_tab", state="normal", size_hint_x=0.5, font_size=dp(14), markup=True)
        self.btn_tab_my.bind(on_press=lambda x: self.switch_main_tab("MY"))

        main_tab_box.add_widget(self.btn_tab_pending)
        main_tab_box.add_widget(self.btn_tab_my)
        self.filter_panel.add_widget(main_tab_box)

        equip_filter_box = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(5))
        # 💡 [수정됨] StyledToggleButton ➔ ReturnToggleButton 으로 교체
        self.btn_eq_op = ReturnToggleButton(text="오더피커(지정)", group="ret_equip_filter", state="normal", font_size=dp(12))
        self.btn_eq_op.bind(on_press=lambda x: self.switch_equip_filter("ORDERPICKER"))

        # 💡 [수정됨] StyledToggleButton ➔ ReturnToggleButton 으로 교체
        self.btn_eq_reach = ReturnToggleButton(text="리치(미지정)", group="ret_equip_filter", state="normal", font_size=dp(12))
        self.btn_eq_reach.bind(on_press=lambda x: self.switch_equip_filter("REACH"))

        # 💡 [수정됨] StyledToggleButton ➔ ReturnToggleButton 으로 교체
        self.btn_eq_all = ReturnToggleButton(text="전체", group="ret_equip_filter", state="down", font_size=dp(12))
        self.btn_eq_all.bind(on_press=lambda x: self.switch_equip_filter("ALL"))

        equip_filter_box.add_widget(self.btn_eq_op)
        equip_filter_box.add_widget(self.btn_eq_reach)
        equip_filter_box.add_widget(self.btn_eq_all)
        self.filter_panel.add_widget(equip_filter_box)

        opt_toolbar = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(3))
        # 💡 [수정됨] bg_color=RETURN_GREEN 추가
        self.btn_from_zone = StyledButton(text="보관: 전체", size_hint_x=0.30, font_size=dp(11), bg_color=RETURN_GREEN)
        self.btn_from_zone.bind(on_press=self.open_from_zone_popup)

        # 💡 [수정됨] bg_color=RETURN_GREEN 추가
        self.btn_to_zone = StyledButton(text="이동: 전체", size_hint_x=0.30, font_size=dp(11), bg_color=RETURN_GREEN)
        self.btn_to_zone.bind(on_press=self.open_to_zone_popup)

        self.btn_sort = StyledButton(text="▲", size_hint_x=0.12, font_size=dp(12), bg_color=get_color_from_hex("#546E7A"))
        self.btn_sort.bind(on_press=self.toggle_sort_order)

        chk_box = BoxLayout(size_hint_x=0.28, spacing=dp(2))
        self.chk_urgent = CheckBox(active=False, size_hint_x=None, width=dp(20), color=PRIMARY_BLUE)
        self.chk_urgent.bind(active=self.on_urgent_check_change)
        lbl_urg = Label(text="긴급만", font_name=FONT_NAME, font_size=dp(12), color=TEXT_DARK, halign="left", valign="middle")
        lbl_urg.bind(size=lambda i, s: setattr(i, "text_size", s))
        chk_box.add_widget(self.chk_urgent)
        chk_box.add_widget(lbl_urg)
        
        opt_toolbar.add_widget(self.btn_from_zone)
        opt_toolbar.add_widget(self.btn_to_zone)
        opt_toolbar.add_widget(self.btn_sort)
        opt_toolbar.add_widget(chk_box)
        self.filter_panel.add_widget(opt_toolbar)

        self.layout.add_widget(self.filter_panel)

        list_header = BoxLayout(size_hint_y=None, height=dp(26), padding=(dp(5), 0))
        self.lbl_status_count = Label(text="대기 작업 (전체) : 0건", font_name=FONT_NAME, font_size=dp(13), color=TEXT_MUTED, halign="left")
        self.lbl_status_count.bind(size=lambda i, s: setattr(i, "text_size", s))

        self.chk_all = CheckBox(size_hint_x=None, width=dp(26), color=RETURN_GREEN)
        self.chk_all.bind(active=self.on_check_all_change)
        self.lbl_chk_all = Label(text="전체선택", font_name=FONT_NAME, font_size=dp(12), color=TEXT_DARK, size_hint_x=None, width=dp(55))

        list_header.add_widget(self.lbl_status_count)
        list_header.add_widget(self.chk_all)
        list_header.add_widget(self.lbl_chk_all)
        self.layout.add_widget(list_header)

        self.rv = RecycleView()
        self.rv_layout = RecycleBoxLayout(default_size=(None, dp(218)), default_size_hint=(1, None), size_hint_y=None, orientation="vertical", spacing=dp(8))
        self.rv_layout.bind(minimum_height=self.rv_layout.setter("height"))
        self.rv.add_widget(self.rv_layout)
        self.rv.viewclass = "UnifiedTaskCard"
        self.layout.add_widget(self.rv)

        self.action_bar = BoxLayout(size_hint_y=None, height=dp(42), padding=(dp(5), 0))
        self.action_bar.add_widget(Widget())

        self.btn_main_action = StyledButton(text="+ 선택 항목 할당받기 (0)", size_hint_x=None, width=dp(210), bg_color=PRIMARY_BLUE, bold=True, font_size=dp(13))
        self.btn_main_action.bind(on_press=self.handle_main_action)
        self.action_bar.add_widget(self.btn_main_action)
        self.layout.add_widget(self.action_bar)

        self.add_widget(self.layout)

    def reset_filters(self):
        self.selected_from_zones = {"전체"}
        self.selected_to_zones = {"전체"}
        self.btn_from_zone.text = "보관: 전체"
        self.btn_to_zone.text = "이동: 전체"
        self.active_equip_filter = "ALL"
        self.btn_eq_all.set_active_visual(True)
        self.btn_eq_op.set_active_visual(False)
        self.btn_eq_reach.set_active_visual(False)
        self.only_urgent = False
        self.chk_urgent.active = False
        self.sort_asc = True
        self.btn_sort.text = "▲"

    def open_from_zone_popup(self, instance):
        try:
            app = App.get_running_app()
            user_name = str(app.user_real_name).strip().lower()
            from_counts = Counter()
            for task in self.raw_all_tasks:
                status = str(t(task, "상태")).strip()
                # 💡 [헤더 반영] 작업자 (X열)
                assignee = str(t(task, "작업자", "")).strip().lower()
                if self.active_main_tab == "PENDING":
                    if status != "대기" or assignee != "": continue
                else:
                    if status != "작업중" or assignee != user_name: continue

                loc = str(t(task, "기존로케이션", "")).strip().upper()
                if loc: from_counts[f"{loc[0]}존"] += 1

            def apply_from_zones(selected_set):
                self.selected_from_zones = selected_set
                if "전체" in selected_set or not selected_set:
                    self.btn_from_zone.text = "보관: 전체"
                else:
                    zones_str = ",".join(sorted(selected_set)).replace("존", "")
                    self.btn_from_zone.text = f"보관: {zones_str}"
                self.apply_filters_and_render()

            dropdown = ZoneMultiSelectDropDown(dict(sorted(from_counts.items())), self.selected_from_zones, apply_from_zones)
            dropdown.open(instance)
        except Exception:
            pass

    def open_to_zone_popup(self, instance):
        try:
            app = App.get_running_app()
            user_name = str(app.user_real_name).strip().lower()
            to_counts = Counter()
            for task in self.raw_all_tasks:
                status = str(t(task, "상태")).strip()
                # 💡 [헤더 반영] 작업자 (X열)
                assignee = str(t(task, "작업자", "")).strip().lower()
                if self.active_main_tab == "PENDING":
                    if status != "대기" or assignee != "": continue
                else:
                    if status != "작업중" or assignee != user_name: continue

                # 💡 [헤더 반영] 원복로케이션 (J열)
                loc = str(t(task, "원복로케이션", "")).strip().upper()
                if loc: to_counts[f"{loc[0]}존"] += 1

            def apply_to_zones(selected_set):
                self.selected_to_zones = selected_set
                if "전체" in selected_set or not selected_set:
                    self.btn_to_zone.text = "이동: 전체"
                else:
                    zones_str = ",".join(sorted(selected_set)).replace("존", "")
                    self.btn_to_zone.text = f"이동: {zones_str}"
                self.apply_filters_and_render()

            dropdown = ZoneMultiSelectDropDown(dict(sorted(to_counts.items())), self.selected_to_zones, apply_to_zones)
            dropdown.open(instance)
        except Exception:
            pass

    def toggle_sort_order(self, instance):
        self.sort_asc = not self.sort_asc
        self.btn_sort.text = "▲" if self.sort_asc else "▼"
        self.apply_filters_and_render()

    def toggle_filter_panel(self, instance=None):
        self.is_filter_expanded = not self.is_filter_expanded
        if self.is_filter_expanded:
            if self.filter_panel not in self.layout.children:
                target_idx = len(self.layout.children) - 2
                self.layout.add_widget(self.filter_panel, index=target_idx)
            self._update_filter_button_text("닫기 ▲")
        else:
            if self.filter_panel in self.layout.children:
                self.layout.remove_widget(self.filter_panel)
            self._update_filter_button_text("열기 ▼")

    def _update_filter_button_text(self, arrow):
        tab_str = "대기작업" if self.active_main_tab == "PENDING" else "내 작업"
        eq_str = "전체" if self.active_equip_filter == "ALL" else ("오더피커" if self.active_equip_filter == "ORDERPICKER" else "리치")
        self.btn_toggle_filter.text = f"🔍 필터 설정 {arrow} ({tab_str} / {eq_str})"

    def on_enter(self):
        app = App.get_running_app()
        if not app.user_real_name:
            app.user_real_name = app.load_saved_user_name() or ""
            if not app.user_real_name:
                self.manager.current = "name_entry"
                return

        self.reset_filters()
        self.active_main_tab = "PENDING"
        self.btn_tab_pending.set_active_visual(True)
        self.btn_tab_my.set_active_visual(False)

        self.is_filter_expanded = True
        if self.filter_panel not in self.layout.children:
            target_idx = len(self.layout.children) - 2
            self.layout.add_widget(self.filter_panel, index=target_idx)
        self._update_filter_button_text("닫기 ▲")

        self.fetch_data()

    def refresh_button_click(self, instance=None):
        self.fetch_data()

    def fetch_data(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_data, daemon=True).start()

    def _async_fetch_data(self):
        try:
            tasks = get_sheet_data(RETURN_TASK_SHEET_NAME, force_refresh=True)
            self.raw_all_tasks = tasks
            Clock.schedule_once(lambda dt: self.apply_filters_and_render())
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def switch_main_tab(self, tab_mode):
        self.active_main_tab = tab_mode
        self.checked_task_ids.clear()
        self.chk_all.active = False
        self.reset_filters()

        if tab_mode == "MY":
            self.btn_main_action.text = "↩ 선택 항목 할당해제 (0)"
            self.btn_main_action.set_bg_color(get_color_from_hex("#FF7043"))
        else:
            self.btn_main_action.text = "+ 선택 항목 할당받기 (0)"
            # 💡 [수정됨] PRIMARY_BLUE ➔ RETURN_GREEN 으로 교체
            self.btn_main_action.set_bg_color(RETURN_GREEN)

        self._update_filter_button_text("닫기 ▲" if self.is_filter_expanded else "열기 ▼")
        self.apply_filters_and_render()

    def switch_equip_filter(self, eq_mode):
        self.active_equip_filter = eq_mode
        self.btn_eq_all.set_active_visual(eq_mode == "ALL")
        self.btn_eq_op.set_active_visual(eq_mode == "ORDERPICKER")
        self.btn_eq_reach.set_active_visual(eq_mode == "REACH")
        self._update_filter_button_text("닫기 ▲" if self.is_filter_expanded else "열기 ▼")
        self.apply_filters_and_render()

    def on_urgent_check_change(self, checkbox, value):
        self.only_urgent = value
        self.apply_filters_and_render()

    def toggle_card_check(self, task_data, is_checked):
        task_id = t(task_data, "작업ID")
        if is_checked:
            self.checked_task_ids.add(task_id)
        else:
            self.checked_task_ids.discard(task_id)

        for item in self.rv.data:
            if t(item["task_data"], "작업ID") == task_id:
                item["is_checked"] = is_checked
                break

        action_prefix = "↩ 선택 항목 할당해제" if self.active_main_tab == "MY" else "+ 선택 항목 할당받기"
        self.btn_main_action.text = f"{action_prefix} ({len(self.checked_task_ids)})"

    def on_check_all_change(self, checkbox, value):
        self.rv.data = [{**item, "is_checked": value} for item in self.rv.data]
        self.rv.refresh_from_data()
        if value:
            for item in self.rv.data:
                self.checked_task_ids.add(t(item["task_data"], "작업ID"))
        else:
            self.checked_task_ids.clear()

        action_prefix = "↩ 선택 항목 할당해제" if self.active_main_tab == "MY" else "+ 선택 항목 할당받기"
        self.btn_main_action.text = f"{action_prefix} ({len(self.checked_task_ids)})"

    def apply_filters_and_render(self):
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        eq_all_tot, eq_all_urg = 0, 0
        eq_op_tot, eq_op_urg = 0, 0
        eq_reach_tot, eq_reach_urg = 0, 0
        pending_urg_count, my_urg_count = 0, 0

        for task in self.raw_all_tasks:
            status = str(t(task, "상태")).strip()
            # 💡 [헤더 반영] 작업자
            assignee = str(t(task, "작업자", "")).strip().lower()
            # 원복 시트엔 긴급여부가 없으므로 N으로 처리
            is_urg = t(task, "긴급여부", "N") == "Y"

            if status == "대기" and assignee == "":
                if is_urg: pending_urg_count += 1
            elif status == "작업중" and assignee == user_name:
                if is_urg: my_urg_count += 1

            if self.active_main_tab == "PENDING":
                if status != "대기" or assignee != "": continue
            else:
                if status != "작업중" or assignee != user_name: continue

            equip = str(t(task, "장비")).strip()
            eq_all_tot += 1
            if is_urg: eq_all_urg += 1

            if equip == "오더피커":
                eq_op_tot += 1
                if is_urg: eq_op_urg += 1
            elif equip == "리치":
                eq_reach_tot += 1
                if is_urg: eq_reach_urg += 1

        urg_font_sz = int(dp(12))
        self.btn_tab_pending.markup = True
        self.btn_tab_pending.text = f"대기 작업 [color=FF9800][size={urg_font_sz}](긴급: {pending_urg_count})[/size][/color]"

        self.btn_tab_my.markup = True
        self.btn_tab_my.text = f"내 작업 [color=FF9800][size={urg_font_sz}](긴급: {my_urg_count})[/size][/color]"

        self.btn_eq_all.markup = True
        self.btn_eq_all.text = f"전체 ({eq_all_tot} / [color=D32F2F]{eq_all_urg}[/color])"

        self.btn_eq_op.markup = True
        self.btn_eq_op.text = f"오더피커 ({eq_op_tot} / [color=D32F2F]{eq_op_urg}[/color])"

        self.btn_eq_reach.markup = True
        self.btn_eq_reach.text = f"리치 ({eq_reach_tot} / [color=D32F2F]{eq_reach_urg}[/color])"

        filtered_list = []
        for task in self.raw_all_tasks:
            status = str(t(task, "상태")).strip()
            # 💡 [헤더 반영] 작업자
            assignee = str(t(task, "작업자", "")).strip().lower()
            equip = str(t(task, "장비")).strip()

            if self.active_main_tab == "PENDING":
                if status != "대기" or assignee != "": continue
            else:
                if status != "작업중" or assignee != user_name: continue

            if self.active_equip_filter == "ORDERPICKER" and equip != "오더피커": continue
            if self.active_equip_filter == "REACH" and equip != "리치": continue

            from_loc = str(t(task, "기존로케이션")).strip().upper()
            # 💡 [헤더 반영] 원복로케이션
            to_loc = str(t(task, "원복로케이션", "")).strip().upper()

            if "전체" not in self.selected_from_zones:
                from_zone = f"{from_loc[0]}존" if from_loc else ""
                if from_zone not in self.selected_from_zones: continue

            if "전체" not in self.selected_to_zones:
                to_zone = f"{to_loc[0]}존" if to_loc else ""
                if to_zone not in self.selected_to_zones: continue

            if self.only_urgent and t(task, "긴급여부", "N") != "Y": continue

            filtered_list.append(task)

        filtered_list.sort(key=lambda x: (t(x, "긴급여부", "N") != "Y", t(x, "기존로케이션", "")), reverse=not self.sort_asc)

        rv_items = []
        is_my_mode = self.active_main_tab == "MY"
        for task in filtered_list:
            task_id = t(task, "작업ID")
            rv_items.append({
                "task_data": task,
                "is_claimed": is_my_mode,
                "is_checked": (task_id in self.checked_task_ids),
                "card_screen": self,
            })

        self.rv.data = rv_items
        self.rv.refresh_from_data()

        tab_name = "대기 작업" if not is_my_mode else "내 작업"
        eq_name = "전체" if self.active_equip_filter == "ALL" else ("오더피커" if self.active_equip_filter == "ORDERPICKER" else "리치")
        self.lbl_status_count.text = f"{tab_name} ({eq_name}) : {len(filtered_list)}건"

    # ==========================
    # 할당 및 할당해제 (반납) 로직
    # ==========================
    def handle_main_action(self, instance):
        if self.active_main_tab == "PENDING":
            self.claim_checked_tasks(instance)
        else:
            self.batch_return_checked_tasks(instance)

    def claim_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup("알림", "할당받을 작업을 선택해주세요.")
            return
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_claim_tasks, daemon=True).start()

    def _async_claim_tasks(self):
        try:
            app = App.get_running_app()
            sheet = get_worksheet(RETURN_TASK_SHEET_NAME)

            all_rows = execute_with_retry(sheet.get, "A:AA")
            if not all_rows or len(all_rows) < 2:
                raise Exception("시트 데이터를 불러올 수 없습니다.")

            headers = [str(h).strip() for h in all_rows[0]]
            # 💡 [헤더 반영] 시트의 X열 '작업자'를 정확히 찾습니다.
            if "작업자" not in headers:
                raise Exception("시트에서 '작업자' 열을 찾을 수 없습니다.")
            assignee_col = headers.index("작업자") + 1
            status_col = headers.index("상태") + 1

            cells_to_update = []
            already_taken_count = 0

            for row_idx, row in enumerate(all_rows[1:], start=2):
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))

                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                task_id = str(t(row_dict, "작업ID")).strip()

                if task_id in self.checked_task_ids:
                    curr_status = str(t(row_dict, "상태")).strip()
                    # 💡 [헤더 반영] 기존 '작업자' 데이터 추출
                    curr_assignee = str(t(row_dict, "작업자", "")).strip()

                    if curr_status in ["대기", ""] and curr_assignee == "":
                        cells_to_update.append(gspread.Cell(row_idx, assignee_col, app.user_real_name))
                        cells_to_update.append(gspread.Cell(row_idx, status_col, "작업중"))
                    else:
                        already_taken_count += 1

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            invalidate_cache(RETURN_TASK_SHEET_NAME)
            self.checked_task_ids.clear()

            if already_taken_count > 0 and len(cells_to_update) == 0:
                Clock.schedule_once(lambda dt: app.show_info_popup("할당 실패", "선택하신 작업이 이미 다른 작업자에게 할당되었습니다."))
            elif already_taken_count > 0:
                Clock.schedule_once(lambda dt: app.show_info_popup("부분 할당 완료", f"이미 다른 사용자가 가져간 {already_taken_count}건을 제외하고 할당되었습니다."))
            else:
                Clock.schedule_once(lambda dt: self.on_claim_success())

            Clock.schedule_once(lambda dt: self.fetch_data())

        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def on_claim_success(self):
        App.get_running_app().show_toast("선택한 원복 작업이 '내 작업'으로 할당되었습니다.")
        self.switch_main_tab("MY")

    def batch_return_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup("알림", "할당 해제할 작업을 선택해주세요.")
            return
        App.get_running_app().show_confirmation_popup("할당 해제 확인", f"선택한 {len(self.checked_task_ids)}건의 작업을 다시 대기상태로 되돌리겠습니까?", lambda: self._start_async_batch_return())

    def _start_async_batch_return(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_batch_return, daemon=True).start()

    def _async_batch_return(self):
        try:
            sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
            all_rows = execute_with_retry(sheet.get, "A:AA")
            
            headers = [str(h).strip() for h in all_rows[0]]
            # 💡 [헤더 반영] '작업자' 컬럼 초기화 목적
            if "작업자" not in headers:
                raise Exception("시트에서 '작업자' 열을 찾을 수 없습니다.")
            assignee_col = headers.index("작업자") + 1
            status_col = headers.index("상태") + 1
            task_id_col = headers.index("작업ID") + 1

            all_ids = sheet.col_values(task_id_col)
            cells_to_update = []

            for task_id in self.checked_task_ids:
                if task_id in all_ids:
                    row_idx = all_ids.index(task_id) + 1
                    cells_to_update.append(gspread.Cell(row_idx, assignee_col, ""))
                    cells_to_update.append(gspread.Cell(row_idx, status_col, "대기"))

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            invalidate_cache(RETURN_TASK_SHEET_NAME)
            self.checked_task_ids.clear()

            Clock.schedule_once(lambda dt: App.get_running_app().show_toast("선택한 작업이 할당 해제되었습니다."))
            Clock.schedule_once(lambda dt: self.fetch_data())
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    # ==========================
    # 원복 스캔 및 카드 액션 제어 (수량/비고/실패 등 보충화면 버튼 호환)
    # ==========================
    def handle_barcode_scan(self, barcode):
        clean_bc = re.sub(r'[^A-Za-z0-9\-]', '', str(barcode)).strip().upper()
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        for child in Window.children:
            if isinstance(child, ReturnInspectionPopup):
                child.process_location_scan(clean_bc)
                return

        my_matches = [
            t_item for t_item in self.raw_all_tasks
            if str(t(t_item, "상태")).strip() == "작업중"
            # 💡 [헤더 반영] 작업자
            and str(t(t_item, "작업자", "")).strip().lower() == user_name
            and re.sub(r'[^A-Za-z0-9\-]', '', str(get_barcode_from_task(t_item))).strip().upper() == clean_bc
        ]

        if my_matches:
            if self.active_main_tab != "MY":
                self.switch_main_tab("MY")

            if len(my_matches) == 1:
                ReturnInspectionPopup(card_data=my_matches[0]["task_data"], task_list_screen=self).open()
            else:
                MultipleSkuSelectPopup(matches=[{"task_data": t} for t in my_matches], on_select=lambda d: ReturnInspectionPopup(card_data=d["task_data"], task_list_screen=self).open()).open()
        else:
            pending_matches = [
                t_item for t_item in self.raw_all_tasks
                if str(t(t_item, "상태")).strip() == "대기"
                and re.sub(r'[^A-Za-z0-9\-]', '', str(get_barcode_from_task(t_item))).strip().upper() == clean_bc
            ]
            if pending_matches:
                task_id = t(pending_matches[0], "작업ID")
                self.checked_task_ids.add(task_id)
                self.apply_filters_and_render()
                app.show_info_popup("스캔 알림", f"['내 작업' 목록에 없는 상품입니다]\n대기 목록의 [{clean_bc}] 항목이 체크 선택되었습니다.\n하단의 [할당받기]를 먼저 눌러주세요.")
            else:
                app.show_info_popup("스캔 오류", f"스캔한 바코드 [{clean_bc}] 에 해당하는 원복 작업을 찾을 수 없습니다.")

    def handle_my_task_action(self, action_name, task_data):
        app = App.get_running_app()
        
        # 1. 수량 입력 및 완료 버튼 -> 원복 검수 팝업 호출
        if action_name in ["qty", "complete"]:
            # 💡 [수정됨] task_list_screen=self 인자 추가 (이것이 튕김의 원인이었습니다!)
            ReturnInspectionPopup(card_data=task_data, task_list_screen=self).open()
            
        # 2. 반납 버튼 -> 할당 해제 (🚨 이 두 줄이 실수로 지워져서 에러가 났습니다!)
        elif action_name == "return":
            self.checked_task_ids.add(t(task_data, "작업ID"))
            self.batch_return_checked_tasks(None)
            
        # 3. 비고 입력 버튼
        elif action_name == "remarks":
            def on_confirm_rem(text):
                if not text.strip(): return
                ts = datetime.now().strftime("%y-%m-%d %H:%M")
                formatted = f"[{ts} {app.user_real_name}] {text.strip()}"
                curr = str(task_data.get("remarks_text", t(task_data, "비고", ""))).strip()
                updated_text = f"{curr}\n{formatted}" if curr else formatted
                task_data["remarks_text"] = updated_text
                task_data["비고"] = updated_text
                app.show_toast("비고가 임시 저장되었습니다. 완료 시 시트에 기재됩니다.")
            open_native_korean_input("비고 추가", "비고 내용 입력", "", on_confirm_rem)
            
        # 4. 실패(원복불가) 버튼
        elif action_name == "fail":
            def on_confirm_fail(reason):
                if not reason.strip(): return
                updates = {
                    "상태": "원복실패",
                    "비고": f"[실패사유] {reason.strip()}",
                    # 💡 [헤더 반영] 작업자
                    "작업자": app.user_real_name,
                    "완료일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                app.show_loading_popup()
                threading.Thread(target=self._update_task_sheet_only, args=(task_data, updates, "원복 실패 처리되었습니다."), daemon=True).start()
            open_native_korean_input("실패 사유 입력", "원복 실패 사유 입력", "", on_confirm_fail)
    # ==========================
    # 사진 촬영 및 최종 완료 처리 로직
    # ==========================
    def open_camera(self, final_loc, task_data):
        if platform != "android":
            App.get_running_app().show_info_popup("PC 모드", "PC에서는 카메라를 사용할 수 없어 임시 링크로 완료 처리합니다.")
            self._finalize_return(task_data, final_loc, "https://pc-test-dummy-url.com")
            return

        try:
            from plyer import camera
            app_dir = App.get_running_app().user_data_dir
            self.current_photo_path = os.path.join(app_dir, "return_temp.jpg")
            
            self._current_task_data = task_data
            self._current_final_loc = final_loc
            camera.take_picture(filename=self.current_photo_path, on_complete=self.on_camera_complete)
        except Exception as e:
            App.get_running_app().show_info_popup("카메라 오류", f"카메라를 실행할 수 없습니다: {e}")

    def on_camera_complete(self, filepath):
        if not os.path.exists(filepath):
            App.get_running_app().show_info_popup("알림", "사진 촬영이 취소되었습니다.")
            return

        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._upload_photo_and_complete, args=(filepath,), daemon=True).start()

    def _upload_photo_and_complete(self, filepath):
        try:
            with open(filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            payload = {
                "fileName": f"원복_{t(self._current_task_data, '작업ID')}.jpg",
                "mimeType": "image/jpeg",
                "base64Data": encoded_string
            }

            req = urllib.request.Request(GAS_PHOTO_UPLOAD_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))

            if res_data.get("status") == "success":
                photo_url = res_data.get("url")
                Clock.schedule_once(lambda dt: self._finalize_return(self._current_task_data, self._current_final_loc, photo_url))
            else:
                raise Exception(res_data.get("message", "업로드 실패"))
                
        except Exception as e:
            Clock.schedule_once(lambda dt: App.get_running_app().show_info_popup("사진 업로드 오류", f"구글 드라이브 업로드 실패: {e}"))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def _finalize_return(self, task_data, final_loc, photo_url):
        app = App.get_running_app()
        
        # 💡 [수량/입수량 변경 비고란 자동 기재 로직]
        final_qty = safe_int(t(task_data, "확인수량", 0))
        req_qty = safe_int(t(task_data, "지시수량", 0))
        updated_remarks = str(t(task_data, "비고", ""))
        
        default_box_size = safe_int(t(task_data, "박스입수량", 1))
        changed_box_size = safe_int(task_data.get("changed_box_size", 0))
        
        if changed_box_size > 0 and changed_box_size != default_box_size:
            change_log = f"입수량 변경 : {changed_box_size}"
            if "입수량 변경" not in updated_remarks:
                updated_remarks = f"{updated_remarks}\n{change_log}" if updated_remarks else change_log

        if final_qty != req_qty:
            diff = final_qty - req_qty
            diff_str = f"+{diff}" if diff > 0 else f"{diff}"
            mismatch_log = f"[수량 불일치] 지시: {req_qty}개 ➔ 원복: {final_qty}개 (차이: {diff_str}개)"
            updated_remarks = f"{updated_remarks}\n{mismatch_log}" if updated_remarks else mismatch_log

        updates = {
            "상태": "원복완료",
            "최종적치": final_loc,
            "확인수량": str(final_qty),
            "비고": updated_remarks,
            "작업자": app.user_real_name,
            "완료일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "사진": photo_url
        }

        # ... (이후 _do_update() 로직은 동일하게 유지) ...

        def _do_update():
            try:
                # 1. 지시서 시트 업데이트
                t_sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
                headers = [str(h).strip() for h in t_sheet.row_values(1)]
                task_id = str(t(task_data, "작업ID"))
                all_ids = t_sheet.col_values(headers.index("작업ID") + 1)
                
                if task_id in all_ids:
                    row_idx = all_ids.index(task_id) + 1
                    cells = [gspread.Cell(row_idx, headers.index(k) + 1, v) for k, v in updates.items() if k in headers]
                    t_sheet.update_cells(cells)

                # 2. 💡 로그 시트에도 똑같이 저장
                try:
                    l_sheet = get_worksheet(RETURN_LOG_SHEET_NAME)
                    l_headers = [str(h).strip() for h in l_sheet.row_values(1)]
                    
                    log_data = dict(task_data)
                    log_data.update(updates)
                    
                    l_sheet.append_row([str(log_data.get(h, "")) for h in l_headers])
                    invalidate_cache(RETURN_LOG_SHEET_NAME)
                except Exception as log_e:
                    print(f"로그 시트 저장 에러 (무시됨): {log_e}")
                
                invalidate_cache(RETURN_TASK_SHEET_NAME)
                Clock.schedule_once(lambda dt: app.show_toast("✅ 원복 작업이 안전하게 완료되었습니다!"))
                Clock.schedule_once(lambda dt: self.fetch_data())
                
            except Exception as e:
                Clock.schedule_once(lambda dt: app.show_info_popup("시트 기록 오류", str(e)))
            finally:
                Clock.schedule_once(lambda dt: app.dismiss_loading_popup())

        app.show_loading_popup()
        threading.Thread(target=_do_update, daemon=True).start()

    def _update_task_sheet_only(self, task_data, updates, msg):
        try:
            t_sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
            headers = [str(h).strip() for h in t_sheet.row_values(1)]
            task_id = str(t(task_data, "작업ID"))
            all_ids = t_sheet.col_values(headers.index("작업ID") + 1)
            
            if task_id in all_ids:
                row_idx = all_ids.index(task_id) + 1
                cells = [gspread.Cell(row_idx, headers.index(k) + 1, v) for k, v in updates.items() if k in headers]
                t_sheet.update_cells(cells)
            
            invalidate_cache(RETURN_TASK_SHEET_NAME)
            Clock.schedule_once(lambda dt: App.get_running_app().show_toast(msg))
            Clock.schedule_once(lambda dt: self.fetch_data())
        except Exception as e:
            Clock.schedule_once(lambda dt: App.get_running_app().show_info_popup("오류", str(e)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

# =========================================================================

class MainApp(App):
    FONT_NAME = FONT_NAME

    def build(self):
        self.user_real_name = self.load_saved_user_name() or ""
        self.current_list_type = None
        self.loading_popup = LoadingPopup()
        self._scan_buffer = ""
        self._last_keystroke_time = 0
        self.last_known_pending_task_ids = set()

        load_recent_history()

        Window.bind(on_key_down=self._on_keyboard_down)

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(NameEntryScreen(name="name_entry"))
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(UnifiedReplenishScreen(name="unified_replenish"))
        sm.add_widget(TaskListScreen(name="task_list"))
        sm.add_widget(AdminDashboardScreen(name="admin_dashboard"))
        sm.add_widget(SkuLocationSearchScreen(name="sku_location_search"))
        
        # 💡 [필수] 독립 화면 정상 등록 확인!
        sm.add_widget(EmergencyReplenishScreen(name="emergency_replenish"))

        # 💡 [신규 추가] 원복 작업 화면 등록
        sm.add_widget(ReturnTaskListScreen(name="return_task_list"))
        
        sm.add_widget(CompletedHistoryScreen(name="completed_history"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "name_entry"

        return sm

    def _on_keyboard_down(self, window, key, scancode, codepoint, modifier):
        current_time = time.time()
        # 0.25초 지연 시 버퍼 리셋
        if current_time - self._last_keystroke_time > 0.25:
            self._scan_buffer = ""
        self._last_keystroke_time = current_time

        # 💡 [엔터키(13, 40) 수신 시]
        if key in [13, 40]:
            if self._scan_buffer:
                raw_data = str(self._scan_buffer).strip()
                
                # 🚨 핵심: 버퍼에 단독으로 'V' 또는 'v'만 들어있다면 스캐너 붙여넣기 찌꺼기이므로 무시!
                if raw_data.upper() == "V":
                    # 버퍼를 지우지 않고 뒤따라올 바코드 텍스트를 기다립니다.
                    return True

                self.process_global_scan(raw_data)
                self._scan_buffer = ""
            return True

        # 순수 아스키 문자 수집
        if codepoint and codepoint.isprintable() and ord(codepoint) >= 32:
            self._scan_buffer += codepoint
        return False

    def process_global_scan(self, barcode):
        raw_str = str(barcode).replace('\ufeff', '').strip()

        # 💡 [보정] 언더바(_) 및 하이픈(-) 모두 허용
        clean_barcode = re.sub(r'[^A-Za-z0-9\-_]', '', raw_str).strip()

        if self.root and clean_barcode:
            curr_screen = self.root.current_screen
            if hasattr(curr_screen, "handle_barcode_scan"):
                curr_screen.handle_barcode_scan(clean_barcode)

    def on_start(self):
        threading.Thread(target=initialize_gspread, daemon=True).start()
        Clock.schedule_interval(self.check_for_new_tasks, 30)

        if platform == "android":
            try:
                request_permissions(
                    [
                        Permission.POST_NOTIFICATIONS,
                        Permission.BLUETOOTH_SCAN,
                        Permission.BLUETOOTH_CONNECT,
                        Permission.BLUETOOTH_ADMIN,
                        Permission.ACCESS_FINE_LOCATION,
                        Permission.CAMERA,                 # 💡 필수
                        Permission.WRITE_EXTERNAL_STORAGE, # 💡 필수
                        Permission.READ_EXTERNAL_STORAGE,  # 💡 필수
                    ]
                )
            except Exception as e:
                print(f"🔴 권한 요청 오류: {e}")

    def check_for_new_tasks(self, *args):
        if self.root and any(
            isinstance(w, NotificationBanner) for w in Window.children
        ):
            return
        threading.Thread(target=self._perform_task_check, daemon=True).start()

    def _perform_task_check(self):
        try:
            # 1. 신규 작업 지시서 알림 및 백그라운드 갱신 데이터 동기화
            all_tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=True)
            pending_tasks = [
                task for task in all_tasks if str(t(task, "상태")).strip() == "대기"
            ]
            current_pending_task_ids = {
                str(t(task, "작업ID")) for task in pending_tasks
            }

            if self.last_known_pending_task_ids:
                new_task_ids = current_pending_task_ids - self.last_known_pending_task_ids
                if new_task_ids:
                    new_tasks = [
                        task for task in pending_tasks if str(t(task, "작업ID")) in new_task_ids
                    ]
                    if new_tasks:
                        Clock.schedule_once(
                            lambda dt: self.show_notification_banner(new_tasks)
                        )

            self.last_known_pending_task_ids = current_pending_task_ids

            # 2. 💡 [핵심 추가] 현재 열려있는 화면별 30초 주기 백그라운드 자동 최신화
            if self.root:
                curr_screen_name = self.root.current
                
                # A. 검수 탭 화면 자동 갱신
                if curr_screen_name == "task_list":
                    try:
                        task_screen = self.root.get_screen("task_list")
                        Clock.schedule_once(lambda dt: task_screen.refresh_list(force_refresh=False))
                    except Exception:
                        pass
                        
                # B. 전체 작업 현황판 자동 갱신
                elif curr_screen_name == "admin_dashboard":
                    try:
                        dash_screen = self.root.get_screen("admin_dashboard")
                        dash_screen.all_tasks = all_tasks
                        Clock.schedule_once(lambda dt: dash_screen.search_tasks())
                    except Exception:
                        pass

                # C. 도급 보충 요청 및 소통 화면 자동 갱신
                elif curr_screen_name == "emergency_replenish" and self.user_real_name:
                    try:
                        user_name = str(self.user_real_name).strip().lower()
                        replenish_requests = get_sheet_data("도급 보충 요청 시트", force_refresh=True)
                        em_screen = self.root.get_screen("emergency_replenish")
                        
                        my_reqs = [
                            r for r in replenish_requests 
                            if str(t(r, "요청자", t(r, "요청 자", ""))).strip().lower() == user_name
                        ]
                        em_screen.raw_requests_cache = my_reqs
                        
                        if em_screen.active_tab == "STATUS":
                            Clock.schedule_once(lambda dt: em_screen._render_status_view())
                    except Exception:
                        pass

            # 3. 데스크 회신 실시간 알림 체크
            if self.user_real_name:
                user_name = str(self.user_real_name).strip().lower()
                replenish_requests = g_cached_sheets.get("도급 보충 요청 시트", [])
                
                for req in replenish_requests:
                    req_user = str(t(req, "요청자", "")).strip().lower()
                    status = str(t(req, "처리상태", "")).strip()
                    reply = str(t(req, "회신 메세지", t(req, "회신메시지", ""))).strip()
                    req_id = str(t(req, "요청 ID", t(req, "요청ID", ""))).strip()

                    if req_user == user_name and (reply or "조치안내" in status):
                        last_reply_key = f"REPLY_SEEN_{req_id}_{reply}_{status}"
                        if not getattr(self, last_reply_key, False):
                            setattr(self, last_reply_key, True)
                            sku_name = str(t(req, "SKU명", "")).strip()[:12]
                            msg = f"💬 [데스크 회신 도착] [{sku_name}]\n내용: {reply if reply else status}"
                            
                            Clock.schedule_once(
                                lambda dt, m=msg: self.show_desk_reply_banner(m)
                            )
                            break
        except Exception as e:
            print(f"⚠️ 백그라운드 체크 오류 (무시): {e}")

    # 💡 [안전 보정] 데스크 회신 알림 클릭 시 독립 화면 안전 전환
    def show_desk_reply_banner(self, message):
        self.play_notification_sound()
        
        def safe_go_to_status_screen():
            if self.root:
                try:
                    em_screen = self.root.get_screen("emergency_replenish")
                    em_screen.switch_view("STATUS") # 쓰레드 안전 전환
                except Exception as e:
                    print(f"⚠️️ 화면 전환 예외 무시: {e}")
                self.root.current = "emergency_replenish"

        banner = NotificationBanner(
            text=message, 
            on_press_callback=lambda: Clock.schedule_once(lambda dt: safe_go_to_status_screen(), 0.1), 
            duration=5
        )
        banner.show(Window)

    def play_notification_sound(self):
        if platform != "android":
            return
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            RingtoneManager = autoclass("android.media.RingtoneManager")
            context = PythonActivity.mActivity.getApplicationContext()
            notification_uri = RingtoneManager.getDefaultUri(
                RingtoneManager.TYPE_NOTIFICATION
            )
            if notification_uri:
                ringtone = RingtoneManager.getRingtone(
                    context, notification_uri
                )
                ringtone.play()
        except Exception as e:
            print(f"🔴 시스템 소리 재생 예외: {e}")

    def show_notification_banner(self, new_tasks):
        if not self.root or self.root.current == "name_entry":
            return

        self.play_notification_sound()

        has_urgent = any(t(task, "긴급여부") == "Y" for task in new_tasks)
        equipment_counts = defaultdict(int)
        for task in new_tasks:
            equip = t(task, "장비", "기타")
            equipment_counts[equip] += 1

        summary_parts = [
            f"{eq} {num}건" for eq, num in equipment_counts.items()
        ]
        summary_text = ", ".join(summary_parts)

        message = "새로운 "
        if has_urgent:
            message += "[color=FF3333][긴급][/color] "
        message += f"작업 발생: {summary_text}"

        def go_to_replenish_screen():
            if self.root:
                self.root.current = "unified_replenish"

        banner = NotificationBanner(
            text=message, on_press_callback=go_to_replenish_screen
        )
        banner.show(Window)

    def show_toast(self, message, duration=2):
        banner = NotificationBanner(text=message, duration=duration)
        banner.show(Window)

    def get_config_path(self):
        return "user_config.json"

    def save_user_name(self, name):
        try:
            with open(self.get_config_path(), "w") as f:
                json.dump({"user_name": name}, f)
        except Exception:
            pass

    def load_saved_user_name(self):
        path = self.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f).get("user_name")
            except Exception:
                None
        return None

    def save_default_printer(self, address):
        try:
            with open("printer_config.json", "w") as f:
                json.dump({"default_printer": address}, f)
        except Exception:
            pass

    def load_default_printer(self):
        if os.path.exists("printer_config.json"):
            try:
                with open("printer_config.json", "r") as f:
                    return json.load(f).get("default_printer")
            except Exception:
                None
        return None

    def show_loading_popup(self):
        if not self.loading_popup.parent:
            self.loading_popup.open()

    def dismiss_loading_popup(self):
        self.loading_popup.dismiss()

    def show_info_popup(self, title, message):
        InfoPopup(title, message).open()

    def show_confirmation_popup(self, title, message, on_yes, on_no=None):
        popup_content = BoxLayout(
            orientation="vertical", spacing=dp(10), padding=dp(15)
        )
        msg_label = Label(
            text=str(message),
            halign="center",
            valign="middle",
            markup=True,
            color=(1, 1, 1, 1),
            size_hint_y=1,
            font_size=dp(16),
            font_name=FONT_NAME,
        )
        msg_label.bind(size=msg_label.setter("text_size"))
        
        button_layout = BoxLayout(
            size_hint_y=None, height=dp(45), spacing=dp(10)
        )
        btn_yes = StyledButton(text="예")
        btn_no = StyledButton(text="아니오")
        button_layout.add_widget(btn_yes)
        button_layout.add_widget(btn_no)
        
        popup_content.add_widget(msg_label)
        popup_content.add_widget(button_layout)
        
        popup = Popup(
            title=title,
            title_font=FONT_NAME,
            content=popup_content,
            size_hint=(0.88, 0.45),  # 💡 [핵심] 팝업 창 높이 및 비율 증대
            auto_dismiss=False,
            background_color=(0.3, 0.3, 0.3, 0.95),
        )

        def yes_action(instance):
            popup.dismiss()
            if on_yes:
                Clock.schedule_once(lambda dt: on_yes(), 0.1)

        def no_action(instance):
            popup.dismiss()
            if on_no:
                Clock.schedule_once(lambda dt: on_no(), 0.1)

        btn_yes.bind(on_press=yes_action)
        btn_no.bind(on_press=no_action)
        popup.open()


if __name__ == "__main__":
    MainApp().run()
