from flask import Flask, render_template, redirect, request
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options 
from time import sleep 
import json
import csv 

app = Flask(__name__)

options = Options()
options.headless = True


df = pd.read_csv('1XBetCrash.csv')
driver = None

@app.route('/', methods=['POST','GET'])
def index():
	return render_template('index.html')

@app.route('/crash', methods=['POST','GET'])
def crash():
	global driver
	driver = webdriver.Firefox(options=options)
	driver.get('https://1xbet.com/fr/allgamesentrance/crash')
	WebDriverWait(driver, 60).until(
			EC.presence_of_element_located((By.CLASS_NAME, 'games-project-frame__item'))
		)
	sleep(5)
	iframe = driver.find_element(By.CLASS_NAME, 'games-project-frame__item')
	driver.switch_to.frame(iframe)
	sleep(5)
	return "ok"
	
@app.route('/bombe', methods=['POST','GET'])
def bombe():
	div = driver.find_element(By.CLASS_NAME, "crash-players-bets__total")
	mises = div.find_element(By.CLASS_NAME,"crash-total__value--bets")
	players = div.find_element(By.CLASS_NAME, "crash-total__value--players")
	player = players.text
	mise = mises.text.replace('MAD','')
	beta = []
	data = {"player":player,"mise":mise}
	beta.append(data)
	return beta

@app.route('/cote',methods=['GET','POST'])
def cote():
	player = request.form.get('player')
	mise = request.form.get('mise')
	cote = request.form.get('cote')
	data = [{"Player":int(player),"Mise":float(mise),"Multiplier":float(cote)}]
	with open('1XBetCrash.csv', mode='r', newline='') as fichier_csv:
	    reader = csv.reader(fichier_csv)
	    en_tete = next(reader)
	    nombre_de_lignes = sum(1 for ligne in reader if any(cellule.strip() for cellule in ligne))
	    if nombre_de_lignes < 30 :
	    	with open('1XBetCrash.csv',mode='a',newline='') as fichier_csv:
	    		fieldnames = ["Player","Mise","Multiplier"]
	    		writer = csv.DictWriter(fichier_csv, fieldnames=fieldnames)
	    		writer.writerows(data)
	    	return "bombe"
	    else :
	    	df = pd.read_csv('1XBetCrash.csv')
	    	y = df['Multiplier']
	    	X = df.drop(columns=['Multiplier'])
	    	scaler = StandardScaler()
	    	X = scaler.fit_transform(X)
	    	train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.3, random_state=123)
	    	linear_reg = LinearRegression()
	    	linear_reg.fit(train_X, train_y)
	    	tree_reg = DecisionTreeRegressor(random_state=123)
	    	tree_reg.fit(train_X, train_y)
	    	forest_reg = RandomForestRegressor(n_estimators=100, random_state=123)
	    	forest_reg.fit(train_X, train_y)
	    	nn_reg = MLPRegressor(hidden_layer_sizes=(100,), max_iter=1000, random_state=123)
	    	nn_reg.fit(train_X, train_y)
	    	beta = []
	    	for model in [linear_reg, tree_reg, forest_reg, nn_reg]:
			    predictions = []
			    for i in range(1, 11):
			        next_X = X[-i].reshape(1, -1)
			        next_y = model.predict(next_X)[0]
			        predictions.append(f"{next_y}")
	    	for predict in predictions:
	    		beta.append(predict)
	    	with open('1XBetCrash.csv', mode='w', newline='') as fichier_csv:
	    		writer = csv.writer(fichier_csv)
	    		writer.writerow(en_tete)
	    	return beta
	    	

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
