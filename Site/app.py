from flask import Flask, request, jsonify, g
import pandas as pd
from flask_cors import CORS
from opt import optimize
from selenium import webdriver 
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins
driver = None

@app.route('/process-info', methods=['POST'])
def process_info():
    data = request.json
    draft_id = data.get('draft_id')
    
    # Call your Python function with the provided parameters
    result = optimize(draft_id)
    return jsonify(result)

@app.route('/launch-ESPN', methods=['POST'])
def launch_ESPN():
    global driver 
    data = request.json
    browser = data.get('browser')
    if browser == 'chrome':
        driver = webdriver.Chrome()
    elif browser == 'firefox':
        driver = webdriver.Firefox()
    elif browser == 'safari':
        driver = webdriver.Safari()
    elif browser == 'edge':
        driver = webdriver.Edge()
        
    driver.get('https://www.espn.com/fantasy/football/')
    g.driver = driver
    return 'ESPN launched successfully'
    
@app.route('/scrape-ESPN', methods=['POST'])
def scrape_ESPN():
    global driver
    return driver.find_element("xpath", '//*[@id="news-feed"]/section[1]/section/a/div/div[3]/h2').text

@app.route('/scrape-ESPN2', methods=['POST'])
def scrape_ESPN2():
    df = pd.read_csv('roster.csv')
    return df.to_json()

if __name__ == '__main__':
    app.run(debug=True)