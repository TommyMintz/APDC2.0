#!/usr/bin/python
#
#The Automated Digital Photo Collage
#A program that renders a time lapse collage
#
#http://tommymintz.com/adpc/
#
#Released under the GNU General Public Liscence
#
#January 2014
#
#ver 2.1.27.14

import pygame
import numpy
import sys
import os
import subprocess
import time
import Image
import ImageFilter
import ImageChops
import ImageOps

#----numgen code section ---#
#numgen.imgno is used throughout the program to track the most current count.
#numgen.imgno is used instead of time and date because of lack of clock battery on the raspberry pi
#num.imgno is stored in a sepearte file, numgen.py

#creates 'numgen.py' and sets numgen.imgno=1 if numgen.py file is not found.
sys.path.append('~/')
try:
  import numgen
  print 'numgen file found. numgen.imgno =', numgen.imgno
except ImportError, err:
  print 'no numgen file found. generated new sequence.'
  f = open('numgen.py', 'w')
  initialwrite = f.write('imgno = 1\n')
  f.close()
  import numgen
  print 'numgen imagenumber is now', numgen.imgno

# adds 1 to the numgen.imgno variable and writes it to the numgen.py file... set to 'a' on keyboard in main loop
def adder():
  f = open('numgen.py', 'w')
  numgen.imgno +=1
  initialwrite = f.write('imgno = %s' %(numgen.imgno))
  f.close()
  
  print 'from adder(): numgen is now', numgen.imgno

#-----end numgen code section ------#

#-------initialise screen section ------#
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()  
global screen
#screen = pygame.display.set_mode ((1024,768), pygame.FULLSCREEN)#opens pygame fullscreen
screen = pygame.display.set_mode ((800,600), pygame.NOFRAME)#open pygame screen that windowed 
pygame.mouse.set_visible(0) #Hide mouse

#fill backgroaund
global background
background = pygame.Surface(screen.get_size())
background = background.convert()    # converts pixels for fast pygame display
background.fill((255,255,255))  #make white rectangle size of background on background surface
#-----end screen init -----#



#----- internal  functions ---#


#shoots photo using a shell command. needs raspberry pi camera to work.
def shootphoto():
  try:
    # subprocess.call (["raspistill -t 1500 -o photo%s.jpg -h 768 -w 1024 -op 100 -f" %numgen.imgno], shell=True)
    # above is non rotated camera below is rotated. use one.
    subprocess.call (["raspistill -t 1000 -o photo%s.jpg -w 1024 -h 768 -rot 180 -op 120 -f" %numgen.imgno], shell=True)
    
    print 'shot photo%s.jpg' %numgen.imgno
    adder()
    print 'numgen.imgno is now', numgen.imgno 
  except: 
    print 'no camera function on shootphoto', sys.exc_info[0], sys_exc_info[1]

#opens jpg photo into numpy array 
def openphoto():
  try:
    image = Image.open("photo%s.jpg" %(numgen.imgno - 1)) 
    print 'opened image', (numgen.imgno - 1)
    return image
  except:
    print 'unable to open the jpg to make numpy array'
    
def setbase():
  #opens the previous photo%s.jpg photo and returns it as a numpy array to be base image 
  # ? also set base to global ?
  base = openphoto()
  print 'base is now defined in setbase()'
  return base


#display some text
def displaysometext(showthistext):
  background.fill((255,255,255))
  font = pygame.font.Font(None, 36)
  text = font.render(showthistext, 1, (10, 10, 10))
  textpos = text.get_rect()
  textpos.centerx = background.get_rect().centerx
  textpos.centery = background.get_rect().centery
  background.blit(text, textpos)  # blit text to surface
  screen.blit(background, (0,0))  # blit surface to screen
  pygame.display.flip()

  background.fill((255,255,255))

#display a specified jpg 
def showimage(image):
  num = image
  print 'in showimage, trying collage%s.jpg' %num
  try:
    image = pygame.image.load('collage%s.jpg' %num)
    image = pygame.Surface.convert(image)
    screen.blit(image, (0,0))  # blit surface to screen
    pygame.display.flip() 
  except:
     displaysometext('Unable to load an image. Try the other button')

#show image with text overlay
def showimageandtext(imagenum, text):
  #print 'in showimageandtext, trying collage%s.jpg' %imagenum, text
  try:
    image = pygame.image.load('collage%s.jpg' %imagenum).convert()

    sprite = pygame.sprite.Sprite()
    sprite.image = image
    sprite.rect = image.get_rect()

    font = pygame.font.Font(None, 36)
    text = font.render(text, 1, (10, 10, 10))

    sprite.image.blit(text, sprite.rect)

    group = pygame.sprite.Group()
    group.add(sprite)
    group.draw(screen)
    pygame.display.flip()
    
  except Exception, e:
    displaysometext('Unable to load %s.' %imagenum) 
    #print 'hai. i caut a prblum in showimageandtext(image, text)', e

#print the collage%s.jpg in subprocess.call
def printer(number):
  try:
    showimageandtext(number, 'Attempting to print collage%s.jpg. Please be patient.' %number)
    subprocess.call (['lp ~/collage%s.jpg' %number], shell=True)
  except Exception, e:
    print 'Exception caught in printing', e, sys.exc_info()[0]



#try to show some text
displaysometext('Please stand aside. The Automated Digital Photo Collage is calibrating.')
time.sleep(3)




# ---- inner loop entered using buttons --- #
#stay in for 10 seconds since last button push
def viewingloop():
  num1 = numgen.imgno -3
  showimageandtext(num1, 'This is collage%s.jpg' %num1)
  clickcount = 0
  viewloop = 10
  c = int(numgen.imgno) + clickcount
  while viewloop > 0:
    try:
      for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
          pygame.quit()
          sys.exit()

        #show last image with y key  
        elif event.type ==  pygame.KEYDOWN and event.key == pygame.K_y:
          clickcount = clickcount - 1
          c = int(numgen.imgno) + clickcount
          showimageandtext(c, 'This is collage%s.jpg' %c)
          viewloop = 10

        #show next image with d key  
        elif event.type ==  pygame.KEYDOWN and event.key == pygame.K_d:
          clickcount = clickcount + 1
          c = int(numgen.imgno) + clickcount
          showimageandtext(c, 'This is collage%s.jpg' %c)
          viewloop = 10

        #restart with the k key  
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
          pygame.quit()
          python = sys.executable
          os.execl(python, python, * sys.argv)

        #print with the j button
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
          try:
            c = numgen.imgno + clickcount  
            printer(c)
          except Exception, e:
            print 'program problem in print attempt', e
            
       
    except Exception, e:
      print 'Program problem in inner loop', e

    time.sleep(1)
    try:
      if viewloop > 1:  
        showimageandtext(c, 'This is collage%s.jpg. It will remain on screen for %s more seconds. ' %(c, viewloop))
      if viewloop == 1:  
        showimageandtext(c, 'This is collage%s.jpg. It will remain on screen for %s more second. ' %(c, viewloop))
    except Exception, e:
      print 'Unable to display how long screen will remain', e
        
    viewloop = viewloop - 1
  return


#check to see if button has been pressed
def checkbuttons():
  try:
    for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
          pygame.quit()
          sys.exit()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
          print 'check buttons caught d pushed'
          viewingloop() 
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_y:
          print 'check buttons caught y pushed' 
          viewingloop()
      # restart program with k  
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
          pygame.quit()
          python = sys.executable
          os.execl(python, python, * sys.argv)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
          printer(numgen.imgno)
                      
       
  except Exception, e:
      print 'Program problem in check buttons', e







    

#---- main is called collage():  

def collage():  
  shootphoto()
  #make blur of base 
  base = setbase()
  blurbase = base.filter(ImageFilter.BLUR)
  print 'base is blurred'
  collage = base
  print 'collage set to base'

  mainloop = 0
  while mainloop < 50:
    print 'mainloop is', mainloop
    try:  
      checkbuttons()
      shootphoto()
      checkbuttons()
      newphoto = openphoto()
      print 'new photo shot'
      #blur the new photo
      blurphoto = newphoto.filter(ImageFilter.BLUR)
      checkbuttons()
      print 'new photo blurred'
      #make alphachannel
      alphachannel = ImageChops.difference(blurbase, blurphoto)
      checkbuttons()
      #alphachannel.save('alphadif%s.jpg' %numgen.imgno)
      alphachannel = ImageOps.grayscale(alphachannel)
      checkbuttons()
      #alphachannel.save('alphagre%s.jpg' %numgen.imgno)
      alphachannel = Image.eval(alphachannel, lambda px:0 if px <15 else 255)
      checkbuttons()
      print 'alphachannel generated'
      alphachannel.save('alphaeval%s.jpg' %numgen.imgno)
      #optional alphachannel blur
      alphachannel = alphachannel.filter(ImageFilter.BLUR)
      checkbuttons()
      alphachannel.convert('1')
    
      #use alphachannel to mask newphoto over oldcollage
      collage.paste(newphoto, None, alphachannel)
      collage.save('collage%s.jpg' %numgen.imgno)
      checkbuttons()
      
      #-----  done making new collage   

      mainloop = mainloop + 1      

      # --- update display
      showimageandtext(numgen.imgno, ' Most recent collage')
      
      time.sleep(3)
      
    except Exception, e:
      print 'program problem in collage loop', e


  #restart program when complete
  pygame.quit()
  python = sys.executable
  os.execl(python, python, * sys.argv)    
      
go = collage()
