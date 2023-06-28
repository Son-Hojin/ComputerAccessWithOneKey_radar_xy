from pynput import keyboard

from PyQt5.QtCore import Qt, QPoint, QThread, QSize, QCoreApplication, QSettings
from PyQt5.QtGui import QPainter, QPen, QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication

from pixel_circle import generate_circle_coordinate, radius

import time
import pyautogui
import threading
import sys
import win32gui #창 열람 방식이 바뀌어서 사용하지 않습니다. 이후 코드를 정리하면서 삭제할 예정입니다.

pyautogui.FAILSAFE = False
 
app_name = "mouse_support_rotate"


click_type = 1 # 1은 단일 클릭, 2은 더블 클릭 

#xy_scan은 rotate_scan 코드를 활용하였습니다. 중복되는 설명은 생략되는 부분이 있으니 이 파일을 먼저 참고해주세요

key_state = False # 키보드 입력 확인
change_signal = False # move event 중 change 시 rapaint 호출 위함. 입력 방식 변경 상태 저장

#반지름 선의 시작점과 끝점 좌표
start_x = 0
start_y = 0
end_x = 0
end_y = 0

settings = QSettings("config.ini", QSettings.IniFormat) #설정파일 값 조회

#키 입력용 쓰레드
class key_listener(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.rep_check = False #반복(키를 누르고 있을 때 여러번 입력이 들어가는 것) 방지.

        # 0은 누를 때, 1은 땔 때
        self.click_state = int(settings.value("SPIN/click_state"))

        #키 초기화. 
        self.target_key = getattr(keyboard.Key, settings.value("SPIN/target_key"))
        self.change_key = getattr(keyboard.Key, settings.value("SPIN/change_key"))
        self.end_key = getattr(keyboard.Key, settings.value("SPIN/end_key"))

    def on_press(self, key):
        global key_state
        global click_type
        global change_signal
        
        if self.click_state == 0: #press 감지
            if self.rep_check == False:     # 반복된 입력이 아니고
                if key == self.target_key:  # 지정한 키 입력일 때
                    key_state = True        # 입력 상태로 전환하고
                    self.rep_check = True   # 반복 방지
                    
                elif key == self.change_key:
                    click_type = (click_type % 2) + 1 # 0은 1로, 1은 0으로 전환
                    change_signal = True
                    self.rep_check = True

            

    def on_release(self, key):
        global key_state
        global click_type
        global change_signal

        if key == self.end_key: # 보호자 프로그램 종료 키. release 일 때만 적용
            # Stop listener
            return False

        if self.click_state == 1:
            if key == self.target_key: # release는 반복 문제가 없기 때문에 지정키 대응만 점검
                key_state = True
            elif key == self.change_key:
                click_type = (click_type % 2) + 1
                change_signal = True
                
        '''
        rep_check를 True로 만든 키인지 검사하는 코드가 없기 때문에
        a를 press한 상태에서 b를 press-release 했을 때 반복 입력이 됨.
        사용 환경이 별도의 키를 이용한다는 가정 하에 문제가 없다고 판단하여 제외함
        '''
        self.rep_check = False
        

    def run(self):
    
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as listener:
            
            listener.join()
        # keyboard Listener가 종료되었을 때: 프로그램 종료
        QCoreApplication.instance().quit()


def click(x_pos, y_pos):    # 지정 좌표에 클릭 수행
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

        # 설정 값 초기화
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

def windowEnumerationHandler(hwnd, top_windows):#미사용
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

# paint 값과 타이밍을 조절하는 컨트롤러 쓰레드
class WindowController(QThread):
    global key_state
    
    key_state = False
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # 추가 회전 시간 (기존 paint 함수 딜레이 + rotate_wait)
        self.rotate_wait = int(settings.value("SPIN/rotate_wait"))
        self.circle_point = generate_circle_coordinate()

        self.move_wait = int(settings.value("SPIN/move_wait")) # 마우스 커서 움직임 대기시간

        #제한 횟수: 이전 단계로 돌아가는 기준
        self.rotate_time = int(settings.value("SPIN/rotate_time"))
        self.move_time = int(settings.value("SPIN/move_time"))

        #시작 전 대기시간
        self.rotate_delay = int(settings.value("SPIN/rotate_delay"))
        self.move_delay = int(settings.value("SPIN/move_delay"))
        
        #동작 복귀를 위한 상태 값(0: 초기 1: 회전)
        self.current_state = 0

    def key_wait(self): # 키 입력 대기. 
        while key_state == False:
            accurate_delay(0.1)
            pass
        return

    def spin_line(self): # 좌표를 만들어서 키 입력때까지 회전함
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

    def run(self): #전체 동작 관리
        global key_state, start_x, start_y, end_x, end_y
        global change_signal
        while True:
            # program_to_front()
            count = 0
            if self.current_state == 0: #초기 상태일 때
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