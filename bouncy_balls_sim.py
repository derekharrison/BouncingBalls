import numpy as np
import matplotlib.pyplot as plt
from numpy import *
import matplotlib.animation as manimation

plt.rcParams['animation.ffmpeg_path']='ffmpeg.exe'
writer=manimation.FFMpegWriter(bitrate=20000, fps=120)

fig = plt.figure(figsize=(8,8))

#Parameters
h = 5.0     #Initial height of the ball
Rp = 0.2    #Radius of the ball
vx = 3.0    #Initial x velocity of the ball    
vy = 0.1    #Initial y velocity of the ball
g = -9.81   #Acceleration constant
x = 0       #Intial x position
dt = 0.01   #Time step size
nt = 2000   #Number of time steps
lwall = -3  #Location of left wall
rwall = 6   #Location of right wall

#Some definitions
coll_partner_is_lwall = 'left_wall'
coll_partner_is_rwall = 'right_wall'
coll_partner_is_ground = 'ground'
small_num = 1e-8

#Functions
def calc_min_coll_time_and_partner(h, vy, x, vx):
    min_coll_time = dt
    coll_partner = 'none'

    tcg = (Rp - h)/(vy + 1e-50)
    if tcg < min_coll_time and tcg >= 0:
        min_coll_time = tcg
        coll_partner = coll_partner_is_ground
        
    tcw = (lwall + Rp - x)/vx
    if tcw < min_coll_time and tcw >= 0:
        min_coll_time = tcw
        coll_partner = coll_partner_is_lwall

    tce = (rwall - Rp - x)/vx
    if tce < min_coll_time and tce >= 0:
        min_coll_time = tce
        coll_partner = coll_partner_is_rwall

    return min_coll_time, coll_partner

def update_positions(min_coll_time, x, h, vx, vy):
    x = x + vx*min_coll_time*(1 - small_num)
    h = h + vy*min_coll_time*(1 - small_num)

    return x, h

def update_velocities(min_coll_time, coll_partner, vx, vy):
    if min_coll_time < dt:
        if coll_partner is coll_partner_is_ground:
            vy = -vy*0.9
        elif coll_partner is coll_partner_is_lwall:
            vx = -vx
        elif coll_partner is coll_partner_is_rwall:
            vx = -vx
    else:
        vy = vy + g*min_coll_time

    return vx, vy

def perform_simulation(nt, x, h, vx, vy):
    f = open("data.txt", "w")
    for t_step in range(0, nt):
        min_coll_time, coll_partner = calc_min_coll_time_and_partner(h, vy, x, vx)
        x, h = update_positions(min_coll_time, x, h, vx, vy)
        vx, vy = update_velocities(min_coll_time, coll_partner, vx, vy)
        x_str = str(x)
        h_str = str(h)
        f.write(x_str)
        f.write(" ")
        f.write(h_str)
        f.write("\n")
        
    f.close()

def animate(i):
    print(i)
    fig.clear()
    ax = plt.axes(xlim=(lwall, rwall), ylim=(0, 10))
    cont = plt.scatter(x_c[i], h_c[i], s=300, c='blue')
    return cont

#Perform calculations
perform_simulation(nt, x, h, vx, vy)

#Read data
data = 'data.txt'
x_c, h_c = np.genfromtxt(data, unpack=True)

#Create video of results
size_t = nt 
anim = manimation.FuncAnimation(fig, animate, frames=size_t, repeat=False)
print("Done Animation, start saving")
anim.save('bouncy_ball.mp4', writer=writer, dpi=200)
