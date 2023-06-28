from PyQt5.QtCore import QSettings

settings = QSettings("config.ini", QSettings.IniFormat)

print(settings.value("SPIN/click_type")) # read
settings.setValue("SPIN/click_type", 2) # write
print(settings.value("SPIN/click_type"))
settings.sync() # save