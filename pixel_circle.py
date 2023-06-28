import pyautogui
import math

# useful to start with the point (r,0) on the positive X-axis
def radius_error(x, y, r):
    return abs(x**2 + y**2 - r**2)

#return next plot location
#True is plot at (x-1, y+1) False is plot at (x, y+1)
def check_next_plot(x, y, r):
    #return 2*(radius_error(x, y, r) + 2*y + 1) + 1 - 2*x > 0
    return radius_error(x-1, y+1, r) < radius_error(x, y+1, r)


#make octant axis to circle.
def octant_to_circle(octant):
    circle: list[(int,int)] = []

    #octant value to circle
    circle.extend(octant)
    
    #symmetry of y=x
    temp = []
    for axis in circle[::-1]:
        if axis[1] == axis[0]:
            continue
        temp.append((axis[1], axis[0]))
    circle.extend(temp)

    #symmetry of y=0
    temp = []
    for axis in circle[::-1]:
        if axis[0] == 0:
            continue
        temp.append((-axis[0], axis[1]))
    circle.extend(temp)

    #symmetry of x=0
    temp = []
    for axis in circle[::-1]:
        if axis[1] == 0:
            continue
        temp.append((axis[0], -axis[1]))
    circle.extend(temp)

    return circle



def radius():
    monitor_x = pyautogui.size()[0]
    monitor_y = pyautogui.size()[1]
    radius = int(math.sqrt(monitor_x**2 + monitor_y**2))

    return radius

#reduce point
def reduce_point(list):
    for i in range(len(list)-1, 0, -2):
        del list[i]

    return list

#radius is diagonal length of monitor
def generate_circle_coordinate():
    
    rad = radius()

    axis : list[(int, int)] = []
    #start point is (radius,0)
    x = rad
    y = 0
    while x > y:
        axis.append((x,y))
        if check_next_plot(x, y, rad):
            x -= 1
        y += 1

    axis.append((x,y))

    axis = octant_to_circle(axis)

    while len(axis) > 1000:
        axis = reduce_point(axis)
        
    return axis





