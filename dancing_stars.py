'''
2018-03-17
Visualize stars in HYG dataset. Renders stars with locations calculated as fnc of time.
Dataset can be found here: https://github.com/astronexus/HYG-Database 

Contribution to r/dataisbeautiful vizualisation competition, March 2018
https://www.reddit.com/r/dataisbeautiful/comments/825mg6/battle_dataviz_battle_for_the_month_of_march_2018/ 

Colours for stars based on stellar type from 
http://www.vendian.org/mncharity/dir3/starcolor/
'''

import csv
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont

'''
Define
    dataset
    image size: width, height
    FoV width in degrees
    Direction for observation
    Constellation
    Time scale
'''

#define
filename='hygdata_v3.csv'
im_size_x = 1500#image width [px]
im_size_y = 750#image height [px]
direction=[0,-45] #direction of view [deg] [84,10] orion
fov_hor=180
time=range(-12000,1,100)

'''
Calculate
    px size
    image height in degrees
    image limits in degrees
'''
px_size_deg=1.0*fov_hor/im_size_x
print "px size [deg] " +str(px_size_deg)
fov_vert=im_size_y*px_size_deg
print "fov_vert " + str(fov_vert)
#Calc field of view limits in deg
asc_min=direction[0]-fov_hor/2
asc_max=direction[0]+fov_hor/2
dec_min=direction[1]-fov_vert/2
dec_max=direction[1]+fov_vert/2

print "asc_min " + str(asc_min)
print "asc_max " + str(asc_max)
print "dec_min " + str(dec_min)
print "dec_max " + str(dec_max)

'''
Import data
'''
csv_input_file=open(filename)
#read data
csv_reader=csv.reader(csv_input_file, delimiter=',')
#skip header
headers=next(csv_reader)
#skip sol
sol=next(csv_reader)

#import data
no_stars=0
asc=[]#ascension, in hours
dec=[]#declination, in degrees
v_asc=[]#proper motion, milliarcseconds
v_dec=[]#proper motion, milliarcseconds
mag=[]#apparent magnitude
stellar_type=[]#Stellar type
for row in csv_reader:
    no_stars+=1
    asc.append(float(row[7]))
    dec.append(float(row[8]))
    v_asc.append(float(row[10]))
    v_dec.append(float(row[11]))
    mag.append(float(row[13]))
    stellar_type.append(row[15])
print str(no_stars) + " stars imported"

'''
Convert data to degrees
'''
for ind in range(len(asc)):
    asc[ind]=(asc[ind]/24)*360 - 180#rescale and shift to interval -180:180
    v_asc[ind]=(v_asc[ind]/(1000*3600*24))*360
    v_dec[ind]=(v_dec[ind]/(1000*3600*24))*360

'''
create image
'''
#max_mag=max(mag)
#first time loop, find brightest spot in movie
print "Looking for max_mag in all frames"
max_mag=0
for t in time:
    #print "Time t = " + str(t) +", looking for max_mag"
    tmp_mag=np.zeros([im_size_x,im_size_y])
    for ind in range(len(asc)):
        #calculate location
        asc_tmp=asc[ind]+t*v_asc[ind]
        dec_tmp=dec[ind]+t*v_dec[ind]
        #check if star is in FoV
        if (asc_tmp>asc_min) and (asc_tmp<asc_max) and (dec_tmp>dec_min) and (dec_tmp<dec_max):
            tmp_x = int((asc_tmp-asc_min)/px_size_deg)
            tmp_y = int(im_size_y-(dec_tmp-dec_min)/px_size_deg)
            tmp_mag[tmp_x,tmp_y]+=mag[ind]
    if np.max(tmp_mag)>max_mag:
        max_mag=np.max(tmp_mag)
print "...Found max_mag: " + str(max_mag)
            
#second time loop to draw stars
print "Drawing stars"
for t in time:           
    image_array=np.zeros([im_size_x,im_size_y,3])
    print "...year "+ str(t)
    #loop stars
    for ind in range(len(asc)):
        #calcualte location
        asc_tmp=asc[ind]+t*v_asc[ind]
        dec_tmp=dec[ind]+t*v_dec[ind]
        #check if star in FoV
        if (asc_tmp>asc_min) and (asc_tmp<asc_max) and (dec_tmp>dec_min) and (dec_tmp<dec_max):
            #assign colour based on stellar type
            if "O" in stellar_type[ind]:
                tmp_col=np.array([155,176,255])
                #print str(ind)+"O"
            elif "B" in stellar_type[ind]:
                tmp_col=([170,191,255])
                #print (str(ind))+"B"
            elif "A" in stellar_type[ind]:
                tmp_col=([202,215,255])
                #print (str(ind))+"A"
            elif "F" in stellar_type[ind]:
                tmp_col=([155,176,255])
                #print (str(ind))+"F"
            elif "G" in stellar_type[ind]:
                tmp_col=([255,244,234])
                #print (str(ind))+"G"
            elif "K" in stellar_type[ind]:
                tmp_col=([255,210,161])
                #print (str(ind))+"K"
            elif "M" in stellar_type[ind]:
                tmp_col=([255,204,111])
                #print (str(ind))+"M"
            else:
                #print str(ind)+"White"
                tmp_col=([255,255,255])#white by default
                
            tmp_x = int((asc_tmp-asc_min)/px_size_deg)
            tmp_y = int(im_size_y-(dec_tmp-dec_min)/px_size_deg)
            #draw star size based on magnitude
            enlargement = 0
            '''
            #after playing around with making high magnitude stars larger, I decided against.
            #Code kept anyhow
            #enlargement=int(round(mag[ind]/10)) #div 10 gives values 0,1,2 (for values in dataset)
            if mag[ind]>=15:
                enlargement=1
            if mag[ind]>=20:
                enlargement=2
            '''
            for x_minor in range(tmp_x-enlargement,tmp_x+enlargement+1,1):
                for y_minor in range(tmp_y-enlargement,tmp_y+enlargement+1,1):
                    if (x_minor>0) and (x_minor<im_size_x-1) and (y_minor>0) and (y_minor<im_size_y-1):
                        image_array[x_minor,y_minor,0]+=tmp_col[0]*mag[ind]/max_mag
                        image_array[x_minor,y_minor,1]+=tmp_col[1]*mag[ind]/max_mag
                        image_array[x_minor,y_minor,2]+=tmp_col[2]*mag[ind]/max_mag
        
    '''
    Create image
    '''
    img=Image.new('RGB',(im_size_x,im_size_y),'black')
    pixels=img.load()
    for x in range(im_size_x):
        for y in range(im_size_y):
            pixels[x,y]=(int(image_array[x,y,0]),int(image_array[x,y,1]),int(image_array[x,y,2]))

    '''
    Adjust image
        Gaussian creates blur
        Autocontrast changes contrast range
        Text adds time label
    '''
    contrast=0.01
    im_blurred= img.filter(ImageFilter.GaussianBlur(radius=1))
    im_blur_con=ImageOps.autocontrast(im_blurred, cutoff=contrast)#set contrast, cutoff % pixels becom black/saturated
    #im_blur_con.show()
    draw_text = ImageDraw.Draw(im_blur_con)
    fnt=ImageFont.truetype('arial.ttf', int(.03*im_size_y))
    
    if t+2000<0:
        year_str=str(-1*(t+2000)) + " B.C."
    elif t+2000>=0:
        year_str=str(t+2000)+" A.D."

    w,h=draw_text.textsize(year_str)
    draw_text.text((im_size_x-50-w,10),year_str, font=fnt, fill=(255,255,255))
    #im_blur_con.show()

    '''
    Save image
    '''
    outputlocation="output\\"
    savename="image_%dx%d_contr %.2f_%05d yrs.png"%(fov_hor,fov_vert,contrast, t)
    im_blur_con.save(outputlocation+savename,format="png")
    print "...Saved "  + savename

print "\n\n Finished rendering stars for all time points."
