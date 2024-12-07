from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By # This needs to be used 

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"chromedriver.exe"

            # Initialize the path to the Chrome WebDriver executable using the Service class
            driver = webdriver.Chrome(DRIVER_PATH)
            searchString = request.form['content'].replace(" ","")

            # searchString = "iphone+15"
            flipkart_url = f"https://www.flipkart.com/search?q={searchString}"

            driver.get(flipkart_url)

            page_text = driver.page_source
            flipkart_html = bs(page_text,"html.parser")
            bigboxes = flipkart_html.findAll("div",{"class":"cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]

            # Example relative link extracted from a Flipkart product listing
            productLink="https://www.flipkart.com"+box.div.div.div.a["href"]

            try:
                driver.get(productLink)
                # Wait for the page to load
                WebDriverWait(driver,100).until(EC.presence_of_element_located((By.CLASS_NAME, "ZmyHeo")))
                time.sleep(5)  # Additional wait to ensure complete loading
                prodRes = driver.page_source
            finally:
                driver.quit()

            # Parse HTML with BeautifulSoup
            prod_html = bs(prodRes, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "RcXBOT"})

            reviews = []

            for commentbox in commentboxes:
                try:
                    c = prod_html.find_all('div', {'class': "x+7QT1"})
                    price = price_element=c[0].div.div.div.text
                    
                except Exception as e:    
                    price = 'Price not found: ' + str(e)

                try:
                    e=  prod_html.find_all('div', {'class': "C7fEHH"})
                    product_name = d[0].div.text
                    
                except Exception as e:    
                    product_name = 'Price not found: ' + str(e)

                try:
                    b = commentbox.div.div.find_all('div', {'class': 'row gHqwa8'})
                    name = b[0].div.p.text
                except Exception as e:
                    name = 'Name not found: ' + str(e)

                try:
                    rating = commentbox.div.div.div.div.text
                except Exception as e:
                    rating = 'Rating not found: ' + str(e)

                try:
                    commentHead = commentbox.div.div.div.p.text
                except Exception as e:
                    commentHead = 'Comment Head not found: ' + str(e)

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    custComment = 'Comment not found: ' + str(e)

                mydict = {"Price": price, "Product": product_name, "Customer Name": name, "Rating": rating, "Heading": commentHead, "Comment": custComment}
                reviews.append(mydict)
                   
                writer.writerows(reviews)

            client = ("mongodb+srv://mangeshsambare1:sambaremangesh123@cluster0.cw3cocl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db = client['flipkart_scrap1']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)    