from flask import Flask, render_template, request , flash, jsonify
import sys                    
import cv2                      
from PIL import Image
from collections import Counter
import base64
import numpy as np

app = Flask(__name__) 

@app.route('/') 
def home(): 
	return render_template('index.html') 

@app.route('/check', methods=['POST']) 
def check():
  ##########################READING IMAGE###############################
  #jsonimg = request.json['image']
  error = None
  success = None
  #Requests image from browser
  image = request.files['image']

  #changes the image to base64
  image_string = base64.b64encode(image.read())
  # print(image_string)
  image = image_string  # raw data with base64 encoding
  #decoded_data = base64.b64decode(image)

  #decode the image from base 64 and reads the image
  decoded_data = base64.b64decode(image_string)
  np_data = np.fromstring(decoded_data,np.uint8)
  img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
  #print(img)
  rows, cols, _ = img.shape
  #print("Rows", rows)
  #print("Cols", cols)
  #crops the top part of the image for head detection
  imgtop = img[0: 9, 53: 74]

  #crops the rest of the image for background detection
  img = img[0: 100, 0: 128]
  cv2.imshow('cropped', imgtop)
  cv2.waitKey(0)

  #counts the total number of pixels
  manual_count = {}
  w, h, channels = img.shape
  total_pixels = w*h
  print(total_pixels)
  ############################ IMAGE ANALYSIS ###################################
  #finding the 20 most common colours in the image body
  for y in range(0, h):
    for x in range(0, w):
      RGB = (img[x, y, 2], img[x, y, 1], img[x, y, 0])
      if RGB in manual_count:
        manual_count[RGB] += 1
      else:
        manual_count[RGB] = 1
  number_counter = Counter(manual_count).most_common(20)

  #showing the percentage of the top 10 most common pixels

  n = 1
  m=0
  for rgb, value in number_counter:

  #calculates the average of the first 10 rgb 
    if n <= 10:
      m += ((float(value)/total_pixels)*100)
      n += 1
  #   print(rgb, value, ((float(value)/total_pixels)*100))
  # print('average',m)
  percentage_of_first = (float(number_counter[0][1])/total_pixels)
  # print(number_counter[0][0][0])
  # print(percentage_of_first)

  #detecting the percentage of white-ish values
  if (percentage_of_first > 0.5) and ((number_counter[0][0][0] and number_counter[0][0][1] and number_counter[0][0][2]) >=230) :
    if m >= 78:
      # print('inavlid image, Reason: face too small')
      # error = 'inavlid image, Reason: face too small'
      return jsonify({'message':'Invalid Image',
                        'success':False}) 
    else:
      # print("Background color is ", number_counter[0][0])
      # print('valid image')
      # success = 'valid image, Image background color is within range'
      return jsonify({'message':'Valid Image',
                        'success':True}) 
  else:
    red = 0
    green = 0
    blue = 0
    sample = 10
    for top in range(0, sample):
      red += number_counter[top][0][0]
      green += number_counter[top][0][1]
      blue += number_counter[top][0][2]

    average_red = red / sample
    average_green = green / sample
    average_blue = blue / sample
    if (average_red and average_green and average_blue) >= 230:
      if m >= 65:
        # print('inavlid image, Reason: face too small')
        #error = 'inavlid image, Reason: face too small'
        return jsonify({'message':'Invalid Image',
                          'success':False})
      # print('background is white or off white')
      else:
        manual_count = {}
        w, h, channels = imgtop.shape
        total_pixels = w*h
        # print(total_pixels)
        for y in range(0, h):
          for x in range(0, w):
            RGB = (imgtop[x, y, 2], imgtop[x, y, 1], imgtop[x, y, 0])
            if RGB in manual_count:
              manual_count[RGB] += 1
            else:
              manual_count[RGB] = 1
        number_counter = Counter(manual_count).most_common(10)
        # print(len(number_counter))
        red = 0
        green = 0
        blue = 0
        sample = len(number_counter)
        for top in range(0, sample):
          red += number_counter[top][0][0]
          green += number_counter[top][0][1]
          blue += number_counter[top][0][2]

        average_red = red / sample
        average_green = green / sample
        average_blue = blue / sample
        # print(average_red, average_blue, average_green)
        if (average_red and average_green and average_blue) <= 239:
          # print('invalid image, Reason: Head')
          #error = 'invalid image, Reason: Head'
          return jsonify({'message':'Invalid Image',
                            'success':False})
        else:
            # print('valid image, Image background color is within range')
            #success = 'valid image, Image background color is within range'
            # print(image.decode("utf-8"))
            return jsonify({'message':'Valid Image',
                            'success':True}) 
    else:
      # print('background is not white or off white')
      # print('invalid image, Reason: background color is not within range')
      # error = 'invalid image, Reason: background color is not within range'
      return jsonify({'message':'Invalid Image, please use a white background image',
                      'success':False}) 

    # print("Average RGB for top ten is: (", average_red, ", ", average_green, ", ", average_blue, ")")


if __name__ == '__main__': 
	app.run(debug=True, host='127.0.0.1', port=5000) 
