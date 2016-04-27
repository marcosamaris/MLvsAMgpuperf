import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.ensemble.forest import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn import svm
import logging
from pandas import DataFrame

#TODO: check negatively predicted values
#TODO: use different linear models

#Gradient tree boosting 
#http://scikit-learn.org/stable/modules/classes.html#module-sklearn.ensemble

logging.basicConfig(filename='prediction_results.log',filemode='w',level=logging.INFO)

#========================Preparing the data===================================#

#Import all dataset
roundNumber = 5;
architecuteList = pd.Series(["Kepler","Maxwell"]);
appIncludeList = pd.Series(["matMul","dotProd","matrix_sum","subSeqMax","vectorAdd"]);

for i in range(0,appIncludeList.size):
	
	dataset = np.genfromtxt('dataset_'+appIncludeList[i]+'.csv', dtype=float, delimiter=',', skip_header =1);
	print dataset.shape;

	#Calculate: number of samples,features, output index, training set size ..
	featureStart = 1;
	samplesStart = 0;
	samplesCount = dataset.shape[0];
	columnsCount = dataset.shape[1];
	featuresCount = dataset.shape[1]-1;
	outputIndex = dataset.shape[1]-1;

	trainingSetCount = int(80 * samplesCount /100);
	
	for j in range(0,architecuteList.size):	
		
		shape = pd.read_csv("result_shape.csv");
		shape=shape.set_index('Type');

		if (appIncludeList[i] == "matMul" and architecuteList[j]== "Kepler"):
			samplesStart = 0; 
			trainingSetCount =375;
			samplesCount = 439;

		if (appIncludeList[i] == "matMul" and architecuteList[j]== "Maxwell"):
			samplesStart = 440; 
			trainingSetCount =870;
			samplesCount = 967;

		if (appIncludeList[i] == "dotProd" and architecuteList[j]== "Kepler"):
			samplesStart = 0; 
			trainingSetCount =274;
			samplesCount = 342;

		if (appIncludeList[i] == "dotProd" and architecuteList[j]== "Maxwell"):
			samplesStart = 343; 
			trainingSetCount =619;
			samplesCount = 652;

		if (appIncludeList[i] == "matrix_sum" and architecuteList[j]== "Kepler"):
			samplesStart = 0; 
			trainingSetCount =505;
			samplesCount = 630;

		if (appIncludeList[i] == "matrix_sum" and architecuteList[j]== "Maxwell"):
			samplesStart = 631; 
			trainingSetCount =1135;
			samplesCount = 1260;

		if (appIncludeList[i] == "subSeqMax" and architecuteList[j]== "Kepler"):
			samplesStart = 0; 
			trainingSetCount =277;
			samplesCount = 345;

		if (appIncludeList[i] == "subSeqMax" and architecuteList[j]== "Maxwell"):
			samplesStart = 346; 
			trainingSetCount =622;
			samplesCount = 684;

		if (appIncludeList[i] == "vectorAdd" and architecuteList[j]== "Kepler"):
			samplesStart = 0; 
			trainingSetCount =253;
			samplesCount = 321;

		if (appIncludeList[i] == "vectorAdd" and architecuteList[j]== "Maxwell"):
			samplesStart = 322; 
			trainingSetCount =598;
			samplesCount = 621;

		print trainingSetCount
		#For training set: separate the feature set from the target attributes
		X = dataset[samplesStart:trainingSetCount,featureStart:featuresCount]; # last one not included
		y = dataset[samplesStart:trainingSetCount,outputIndex];

		#True Output values that will be used in calcuating the accuracy of prediction
		y_true = dataset[trainingSetCount+1:samplesCount,outputIndex]
		print y_true

		#Scale values with mean = zero and standard deviation =1
		std_scale = preprocessing.StandardScaler().fit(X)
		X_std = std_scale.transform(X)
		#print X_std;

		#Scale test set
		X_val = dataset[trainingSetCount+1:samplesCount,featureStart:featuresCount];
		X_val_std = std_scale.transform(X_val)
		#print X_val_std;

		def printErrors(lr,modelType):
			training_error = lr.score(X_std,y);
			training_error = round(training_error,roundNumber)
			print "Training error = " + str(training_error) + ", best is 1.0";
			shape['Training error'][modelType] = training_error

			test_error = lr.score(X_val_std,y_true );
			test_error = round(test_error,roundNumber)
			print "Test error = " + str(test_error) + ", best is 1.0";
			shape['Test error'][modelType] = test_error

			#Calculating prediction error
			error = mean_absolute_error(y_true,y_pred);
			error = round(error,roundNumber)
			print "Mean absolute error: " + str(error) + ", best is zero";
			shape['Mean absolute error'][modelType] = error;

			error = mean_squared_error(y_true, y_pred) 
			error = round(error,roundNumber)
			print "Mean squared error: " + str(error) + ", best is zero";
			shape['Mean squared error'][modelType] = error;

			accuracy = np.mean( np.divide(y_pred,y_true) ) * 100
			print accuracy
			shape['Accuracy'][modelType] = accuracy 

			#print y_pred;
		   	
			return

		print "======================Application: "+appIncludeList[i];
		logging.info("======================Application: "+appIncludeList[i]);
		#=====================Ordinary Least Squares Linear model======================================
		print "=====================Ordinary Least Squares================"
		logging.info("=====================Ordinary Least Squares================" );
		#Training phase
		lr = linear_model.LinearRegression();
		lr.fit(X_std,y);

		#Prediction for test set
		y_pred = lr.predict(X_val_std)

		printErrors(lr,"ordinary");

		#===================Ridge Regression==========================================
		print "=======================Ridge Regression=================="
		logging.info("=======================Ridge Regression==================");
		#Try different regularization parameters
		ridgeCV = linear_model.RidgeCV(alphas=[0.01,0.1,0.3,0.6, 1.0,3.0,6.0, 10.0])

		ridgeCV.fit(X_std,y);
		print "Used alpha: " + str(ridgeCV.alpha_);

		y_pred = ridgeCV.predict(X_val_std);

		printErrors(ridgeCV,"ridge");

		#=========================LASSO ==============================

		print "=======================LASSO Regression=================="
		logging.info("=======================LASSO Regression==================");
		#Try different regularization parameters
		lassoCV = linear_model.LassoCV(alphas=[0.01,0.1,0.3,0.6, 1.0,3.0,6.0, 10.0])

		lassoCV.fit(X_std,y);
		print "Used alpha: " + str(lassoCV.alpha_);

		y_pred = lassoCV.predict(X_val_std);

		printErrors(lassoCV,"lasso");
		#=========================Elastic Net ====================================
		print "================Elastic Net ===================="	
		logging.info("================Elastic Net ====================");
		enet = linear_model.ElasticNetCV(l1_ratio = [.1, .5, .7, .9, .95, .99, 1] ,alphas=[0.01,0.1,0.3,0.6, 1.0,3.0,6.0, 10.0] );

		enet.fit(X_std,y);
		print "Used alpha: " + str(enet.alpha_);
		print "Used l1_ratio: " + str(enet.l1_ratio_);

		y_pred = enet.predict(X_val_std);

		printErrors(enet,"elastic_net");
		#=======================Support Vector Regression=============================
		print "================Support Vector Regression===================="
		logging.info("================Support Vector Regression===================="); 
		svmR = svm.SVR();

		svmR.fit(X_std,y);

		y_pred = svmR.predict(X_val_std);

		printErrors(svmR,"support_vector_regression");

		#====================Random Forest Regressor==========================
		print "=========Random Forest Regressor==========="
		logging.info("=========Random Forest Regressor===========");
		randomForest = RandomForestRegressor(n_estimators=10);

		randomForest.fit(X_std,y);

		y_pred = randomForest.predict(X_val_std);

		printErrors(randomForest,"random_forest_regressor");

		shape.to_csv("results_"+appIncludeList[i]+"_"+architecuteList[j]+".csv");

