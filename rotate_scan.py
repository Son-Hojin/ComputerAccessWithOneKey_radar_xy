from pynput import keyboard

from PyQt5.QtCore import Qt, QPoint, QThread, QSize, QCoreApplication, QSettings
from PyQt5.QtGui import QPainter, QPen, QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication

from pixel_circle import generate_circle_coordinate, radius

import time
import pyautogui
import threading
import sys
import win32gui
#최종 파일. 주석 확인
pyautogui.FAILSAFE = False
 
app_name = "mouse_support_rotate"


click_type = 1 # 1은 단일 클릭, 2은 더블 클릭 


key_state = False # 키보드 입력 확인
change_signal = False # move event 중 change 시 rapaint 호출 위함

start_x = 0
start_y = 0
end_x = 0
end_y = 0

settings = QSettings("config.ini", QSettings.IniFormat)

#키 입력용 쓰레드
class key_listener(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.rep_check = False
        # 0은 누를 때, 1은 땔 때
        self.click_state = int(settings.value("SPIN/click_state"))

        self.target_key = getattr(keyboard.Key, settings.value("SPIN/target_key"))
        self.change_key = getattr(keyboard.Key, settings.value("SPIN/change_key"))
        self.end_key = getattr(keyboard.Key, settings.value("SPIN/end_key"))

    def on_press(self, key):
        global key_state
        global click_type
        global change_signal
        
        if self.click_state == 0:
            if self.rep_check == False:
                if key == self.target_key:
                    key_state = True
                    self.rep_check = True
                    
                elif key == self.change_key:
                    click_type = (click_type % 2) + 1
                    change_signal = True
                    self.rep_check = True

            

    def on_release(self, key):
        global key_state
        global click_type
        global change_signal

        if key == self.end_key:
            # Stop listener
            return False

        if self.click_state == 1:
            if key == self.target_key:
                key_state = True
            elif key == self.change_key:
                click_type = (click_type % 2) + 1
                change_signal = True
                
        self.rep_check = False
        

    def run(self):
    
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            
            listener.join()
            
        QCoreApplication.instance().quit()


def click(x_pos, y_pos):
    pyautogui.moveTo(x_pos, y_pos, _pause = False)
    if click_type == 1:
        pyautogui.click()
    elif click_type == 2:
        pyautogui.doubleClick()

def init_point():
        global start_x, start_y, end_x, end_y
        start_x = 0
        start_y = 0
        end_x = 0
        end_y = 0

class DisplayWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # listener = key_listener(self)
        # listener.start()

        win_control = WindowController(self)   
        win_control.start()
        #thread 실행

        r = int(settings.value("SPIN/line_color_r"))
        g = int(settings.value("SPIN/line_color_g"))
        b = int(settings.value("SPIN/line_color_b"))
        self.guide_line_thickness = int(settings.value("SPIN/guide_line_thickness"))
        self.click_pen = QPen(QColor(r, g, b), self.guide_line_thickness)
        self.click_pen.setCapStyle(Qt.RoundCap)

        r = int(settings.value("SPIN/d_line_color_r"))
        g = int(settings.value("SPIN/d_line_color_g"))
        b = int(settings.value("SPIN/d_line_color_b"))
        self.double_click_pen = QPen(QColor(r,g,b), self.guide_line_thickness, Qt.DashLine)
        self.double_click_pen.setCapStyle(Qt.RoundCap)

        self.line_opacity = float(settings.value("SPIN/line_opacity"))
        
    def paintEvent(self, event):
        
        painter = QPainter(self)
        painter.setOpacity(self.line_opacity)

        # 조건 따라 펜 설정
        if click_type == 2:
            painter.setPen(self.double_click_pen)
        else:
            painter.setPen(self.click_pen)

        
        if start_x != 0  and start_y != 0: #초기 상태
            painter.drawEllipse(QPoint(start_x, start_y), 35+self.guide_line_thickness, 35+self.guide_line_thickness)

        painter.drawLine(start_x, start_y, end_x, end_y)
        

def accurate_delay(delay):
    t = time.perf_counter() + delay/1000
    while time.perf_counter() < t:
        pass

def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def program_to_front():#미사용
    
    top_windows = []
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    for i in top_windows:
        if app_name in i[1].lower():
            try:
                win32gui.ShowWindow(i[0], 5)
                win32gui.SetForegroundWindow(i[0])
                break
            except:
                break

class WindowController(QThread):
    global key_state
    
    key_state = False
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # 추가 회전 시간
        self.rotate_wait = int(settings.value("SPIN/rotate_wait"))
        self.circle_point = generate_circle_coordinate()

        self.move_wait = int(settings.value("SPIN/move_wait"))

        self.rotate_time = int(settings.value("SPIN/rotate_time"))
        self.move_time = int(settings.value("SPIN/move_time"))

        self.rotate_delay = int(settings.value("SPIN/rotate_delay"))
        self.move_delay = int(settings.value("SPIN/move_delay"))

        self.current_state = 0

    def key_wait(self):
        while key_state == False:
            accurate_delay(0.1)
            pass
        return

    def spin_line(self):
        global end_x, end_y

        for x, y in self.circle_point:  
            if key_state == False:
                end_x = start_x + x
                end_y = start_y + y
                
                self.parent.repaint() # ~ 0.002
                accurate_delay(self.rotate_wait) #rotate_wait초 만큼 추가 회전
                
            else:
                break
    
    def init_point(self):
        global start_x, start_y, end_x, end_y
        start_x = 0
        start_y = 0
        end_x = 0
        end_y = 0

    def run(self):
        global key_state, start_x, start_y, end_x, end_y
        global change_signal
        while True:
            # program_to_front()
            count = 0
            if self.current_state == 0:
                self.init_point()
                self.current_state = 1

            self.parent.repaint()
            
            if self.current_state == 1:
                self.key_wait()
                start_x = pyautogui.position().x
                start_y = pyautogui.position().y

            key_state = False
            # program_to_front()
            first = True
            while key_state == False:
                for x, y in self.circle_point:  
                    if key_state == False:
                        end_x = start_x + x
                        end_y = start_y + y
                        
                        self.parent.repaint() # ~ 0.002
                        if first:
                            time.sleep(self.rotate_delay)
                            first = False
                        else:
                            accurate_delay(self.rotate_wait) #rotate_wait초 만큼 추가 회전
                        
                    else:
                        break
                count += 1
                if count == self.rotate_time:
                    break  
                
            if count == self.rotate_time and key_state != True:
                self.current_state = 0 # back to start
                continue

            self.key_wait()
            count = 0

            dx = (end_x - start_x)/radius()
            dy = (end_y - start_y)/radius()
            cur_x = start_x
            cur_y = start_y

            key_state = False
            first = True
            while key_state == False:
                cur_x += dx
                cur_y += dy
                pyautogui.moveTo(cur_x, cur_y, _pause = False)
                if first:
                    time.sleep(self.move_delay)
                    first = False
                else:
                    accurate_delay(self.move_wait)
                if change_signal == True:
                    change_signal = False
                    self.parent.repaint()
                    
                if cur_x <= 0 or cur_y <= 0 or cur_x>=pyautogui.size()[0] or cur_y >= pyautogui.size()[1] :
                    cur_x = start_x
                    cur_y = start_y
                    count += 1
                    if count == self.move_time:
                        break
            
            if count == self.move_time and key_state != True: 
                self.current_state = 2 #back to spin , 2 is nothing
                pyautogui.moveTo(start_x, start_y, _pause = False)
                continue

            # delete all paint and click
            self.init_point()
            self.parent.repaint() 
            click(cur_x, cur_y)

            key_state = False
            # program_to_front()
            self.current_state = 0 # successfull execution
        
listener = key_listener()
listener.daemon = True
listener.start()

app = QApplication(sys.argv)
app.setApplicationDisplayName(app_name)
app.setWindowIcon(QIcon('icon/rotate.png'))

window = DisplayWindow()

#WindowStaysOnTopHint -> win32gui 창 전환 불필요. 화상 키보드 아래에 배치
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
window.setAttribute(Qt.WA_NoSystemBackground, True)
window.setAttribute(Qt.WA_TranslucentBackground, True)

window.showFullScreen()

app.setOverrideCursor(Qt.PointingHandCursor)
sys.exit(app.exec())