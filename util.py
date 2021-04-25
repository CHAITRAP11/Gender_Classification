import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
import cv2
import pickle
import sklearn

#load model files
haar = cv2.CascadeClassifier('./model/haarcascade_frontalface_default.xml')

#load pickle files
mean = pickle.load(open('./model/mean.pickle', 'rb'))
model_svm = pickle.load(open('./model/model_svm.pickle', 'rb'))
model_pca = pickle.load(open('./model/pca_50.pickle', 'rb'))  

gender = ['Male', 'Female']

font = cv2.FONT_HERSHEY_SIMPLEX


def pipeline_model(path, filename, color='bgr'):
	# step-1: read image in cv2
	#img = cv2.imread(path)
    # step-2: convert into gray scale
    img = cv2.imread(path)
    if color == 'bgr':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # step-3: crop faces
    count={"Male":0,"Female":0}
    
    faces = haar.detectMultiScale(gray, 1.5, 3)
    for x, y, w, h in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,255,0), 2) # drawing rectangle
        roi = gray[y:y+h, x:x+w] # crop image
        #step-4 : normalization
        roi = roi/255
        #step-5 : resizing
        size = roi.shape[1]
        if size>100:
            roi_resize = cv2.resize(roi, (100,100), cv2.INTER_AREA) #shrink
        else:
            roi_resize = cv2.resize(roi, (100,100), cv2.INTER_CUBIC) #Enlarge
        #step-6 : flattenning (1, 10000)
        roi_reshape = roi_resize.reshape(1, 10000)

        #step-7 : subtract with mean
        roi_mean = roi_reshape - mean

        #step-8 : Eigen image
        eigen_img = model_pca.transform(roi_mean)

        #step-9 : Predict with svm model
        results = model_svm.predict_proba(eigen_img)[0]
        #print(results)
        predict = results.argmax() # 0-male, 1-female
        print(predict)
        if predict==1:
        	count["Female"]+=1
        else:
        	count["Male"]+=1
        score = results[predict]

        #step-10 : 
        text = "%s : %0.2f"%(gender[predict], score)
        cv2.putText(img, text, (x,y), font, 1, (255,255,0), 2)

    cv2.imwrite('./static/predict/{}'.format(filename),img)

    return gender[predict],count["Male"],count["Female"]
    
