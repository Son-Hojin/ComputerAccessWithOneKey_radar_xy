# ComputerAccessWithOneKey_radar_xy

Python version: 3.8.10<br>
그 외 라이브러리 버전은 requirements.txt 파일에 있습니다.<br>
.exe 파일 생성)<br>> pyinstaller -w -F --icon=./icon/rotate.ico rotate_scan.py<br>> pyinstaller -w -F --icon=./icon/xy.ico xy_scan.py 

<h3>업로드 파일 설명</h3>
<ul>
  <li>icon/              : 아이콘이 저장되어 있는 폴더</li>
  <li>config.ini         : 설정값을 저장하고 조회하는 파일</li>
  <li>pixel_circle.py    : 모니터 사이즈에 따라 이동 좌표를 계산</li>
  <li>requirements.txt   : 사용한 라이브러리 버전 pip에 그대로 사용 가능</li>
  <li>rotate_scan.py     : 원형스캔</li>
  <li>xy_scan.py         : 지점스캔</li>
</ul>
