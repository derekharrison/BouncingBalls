import numpy as np
import matplotlib.pyplot as plt
from numpy import *
import matplotlib.animation as manimation

plt.rcParams['animation.ffmpeg_path']='ffmpeg.exe'
writer=manimation.FFMpegWriter(bitrate=20000, fps=120)

fig = plt.figure(figsize=(8,8))

#Parameters
h_1 = 5.0   #Initial height of the ball
x_1 = 0     #Intial x position
vx_1 = 3.0  #Initial x velocity of the ball    
vy_1 = 0.1  #Initial y velocity of the ball
h_2 = 5.0   #Initial height of the ball
x_2 = 2     #Intial x position
vx_2 = -3.0 #Initial x velocity of the ball    
vy_2 = 0.1  #Initial y velocity of the ball
Rp = 0.2    #Radius of the ball
m = 1       #Mass of the balls
g = -9.81   #Acceleration constant
dt = 0.01   #Time step size
nt = 2500   #Number of time steps
lwall = -3  #Location of left wall
rwall = 6   #Location of right wall

#Some definitions
coll_partner_is_lwall = 'left_wall'
coll_partner_is_rwall = 'right_wall'
coll_partner_is_ground = 'ground'
coll_partner_is_particles = 'particle'
part_1_coll_with_wall = 'part_one_collides_with_wall'
part_2_coll_with_wall = 'part_two_collides_with_wall'
small_num = 1e-6

#Functions
def calc_min_coll_time_walls(h, vy, x, vx):
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

def calc_min_coll_time_particles(h_1, vy_1, x_1, vx_1, h_2, vy_2, x_2, vx_2):
    rab = [x_2 - x_1, h_2 - h_1]
    vab = [vx_2 - vx_1, vy_2 - vy_1]
    Disc = np.dot(rab,vab)*np.dot(rab,vab)-np.dot(vab, vab)*(np.dot(rab, rab)-(2*Rp)*(2*Rp))
    coll_time_particle = dt
    if Disc > 0:
        coll_time_particle = (-np.dot(rab, vab) - sqrt(Disc)) / np.dot(vab, vab)

    return coll_time_particle

def update_positions(min_coll_time, x, h, vx, vy):
    x = x + vx*min_coll_time*(1 - small_num)
    h = h + vy*min_coll_time*(1 - small_num)

    return x, h

def update_velocities(min_coll_time, coll_partner, part_id_for_wall_colls, x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2):
    if min_coll_time < dt and part_id_for_wall_colls is part_1_coll_with_wall:
        if coll_partner is coll_partner_is_ground:
            vy_1 = -vy_1*0.9
        elif coll_partner is coll_partner_is_lwall:
            vx_1 = -vx_1
        elif coll_partner is coll_partner_is_rwall:
            vx_1 = -vx_1

    elif min_coll_time < dt and part_id_for_wall_colls is part_2_coll_with_wall:
        if coll_partner is coll_partner_is_ground:
            vy_2 = -vy_2*0.9
        elif coll_partner is coll_partner_is_lwall:
            vx_2 = -vx_2
        elif coll_partner is coll_partner_is_rwall:
            vx_2 = -vx_2
            
    elif min_coll_time < dt and coll_partner is coll_partner_is_particles:
            v_1, v_2 = update_velocity_part_coll(x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2)
            vx_1 = v_1[0]
            vy_1 = v_1[1]
            vx_2 = v_2[0]
            vy_2 = v_2[1]            
    elif min_coll_time >= dt:
        vy_1 = vy_1 + g*min_coll_time
        vy_2 = vy_2 + g*min_coll_time

    return vx_1, vy_1, vx_2, vy_2

def update_velocity_part_coll(x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2):
    ra = np.array([x_1, h_1])
    va = np.array([vx_1, vy_1])
    rb = np.array([x_2, h_2])
    vb = np.array([vx_2, vy_2])
    n = (ra-rb)/sqrt(np.dot((ra-rb), (ra-rb)))
                       
    del_v = n*np.dot((va - vb), n)
                      
    #Update velocities                      
    vx_1 = vx_1 - del_v[0]
    vy_1 = vy_1 - del_v[1]
    vx_2 = vx_2 + del_v[0]
    vy_2 = vy_2 + del_v[1]

    v_1 = [vx_1, vy_1]
    v_2 = [vx_2, vy_2]

    return v_1, v_2

def calc_min_coll_time_and_partners(min_coll_time_1,
                                    min_coll_time_2,
                                    coll_time_particles,
                                    coll_partner_1,
                                    coll_partner_2):
    min_coll_time = dt
    coll_partner = 'none'
    part_id_for_wall_colls = 'none'
    if min_coll_time_1 < min_coll_time:
        min_coll_time = min_coll_time_1
        coll_partner = coll_partner_1
        part_id_for_wall_colls = part_1_coll_with_wall
    if min_coll_time_2 < min_coll_time:
        min_coll_time = min_coll_time_2
        coll_partner = coll_partner_2
        part_id_for_wall_colls = part_2_coll_with_wall
    if coll_time_particles < min_coll_time and coll_time_particles > 0:
        min_coll_time = coll_time_particles
        coll_partner = coll_partner_is_particles
        part_id_for_wall_colls = 'none'
        
    return min_coll_time, coll_partner, part_id_for_wall_colls
    

def perform_simulation(nt, x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2):
    f = open("data.txt", "w")
    for t_step in range(0, nt):
        min_coll_time_1, coll_partner_1 = calc_min_coll_time_walls(h_1, vy_1, x_1, vx_1)
        min_coll_time_2, coll_partner_2 = calc_min_coll_time_walls(h_2, vy_2, x_2, vx_2)
        coll_time_particles = calc_min_coll_time_particles(h_1, vy_1, x_1, vx_1, h_2, vy_2, x_2, vx_2)
        min_coll_time, coll_partner, part_id_for_wall_colls = calc_min_coll_time_and_partners(min_coll_time_1, min_coll_time_2, coll_time_particles,
                                                                                              coll_partner_1, coll_partner_2)
        x_1, h_1 = update_positions(min_coll_time, x_1, h_1, vx_1, vy_1)
        x_2, h_2 = update_positions(min_coll_time, x_2, h_2, vx_2, vy_2)
        vx_1, vy_1, vx_2, vy_2 = update_velocities(min_coll_time, coll_partner, part_id_for_wall_colls, x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2)
        
        x_str_1 = str(x_1)
        h_str_1 = str(h_1)

        x_str_2 = str(x_2)
        h_str_2 = str(h_2)
        
        f.write(x_str_1)
        f.write(" ")
        f.write(h_str_1)
        f.write(" ")
        f.write(x_str_2)
        f.write(" ")
        f.write(h_str_2)
        f.write("\n")
        
    f.close()

def animate(i):
    print(i)
    fig.clear()
    ax = plt.axes(xlim=(lwall, rwall), ylim=(0, 10))
    x_c = [x_c_1[i], x_c_2[i]]
    h_c = [h_c_1[i], h_c_2[i]]
    cont = plt.scatter(x_c, h_c, s=300, c='blue')
    return cont

#Perform calculations
perform_simulation(nt, x_1, h_1, vx_1, vy_1, x_2, h_2, vx_2, vy_2)

#Read data
data = 'data.txt'
x_c_1, h_c_1, x_c_2, h_c_2 = np.genfromtxt(data, unpack=True)

#Create video of results
size_t = nt 
anim = manimation.FuncAnimation(fig, animate, frames=size_t, repeat=False)
print("Done Animation, start saving")
anim.save('bouncy_ball.mp4', writer=writer, dpi=200)
