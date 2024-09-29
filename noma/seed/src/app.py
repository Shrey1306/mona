from flask import Flask, request, jsonify, session
from flask_session import Session
import yfinance as yf
import requests
import urllib.request
import pandas as pd
import json
from bs4 import BeautifulSoup
from flask_cors import CORS, cross_origin
import openai
openai.api_key = ""

app = Flask(__name__)

app.config["SECRET_KEY"] = ""  # Change this to a random secret key
app.config["SESSION_TYPE"] = "filesystem"  # Can be "redis", "memcached", "filesystem", etc.
Session(app)



CORS(app)

@app.route('/stock', methods=['GET'])
def get_stock_info():
    # Get ticker symbol from query parameter
    ticker_symbol = request.args.get('ticker', '').upper()
    url = "https://query2.finance.yahoo.com/v1/finance/esgChart?symbol=" + ticker_symbol

# Parse the HTML content of the page
    
    # Fetch stock information using yfinance
    stock = yf.Ticker(ticker_symbol)
    # Attempt to fetch stock info; if unavailable, return an error message
    stock_info = stock.info
    hist = stock.history()
    connection = urllib.request.urlopen(url)
    data = connection.read()
    data_2 = json.loads(data)

    try:
        Formatdata = data_2["esgChart"]["result"][0]["symbolSeries"]
        Formatdata_2 = pd.DataFrame(Formatdata)
    except: 
        Formatdata = "N/A"

    try: 
        esg = float(Formatdata_2.iloc[-1]["esgScore"])
        gs = float(Formatdata_2.iloc[-1]["governanceScore"])
        es = float(Formatdata_2.iloc[-1]["environmentScore"])
        ss = float(Formatdata_2.iloc[-1]["socialScore"])
    except: 
        esg = 0
        gs = 0
        es = 0
        ss = 0

    # Extracting relevant fields
    relevant_info = {
        "symbol": stock_info.get("symbol"),
        "companyName": stock_info.get("longName"),
        "sector": stock_info.get("sector"),
        "currentPrice": stock_info.get("currentPrice"),
        "marketCap": stock_info.get("marketCap"),
        "forwardPE": stock_info.get("forwardPE"),
        "dividendYield": stock_info.get("dividendYield"),
        "52WeekLow": stock_info.get("fiftyTwoWeekLow"),
        "52WeekHigh": stock_info.get("fiftyTwoWeekHigh"),
        "openPrice": stock_info.get("open"),
        "previousClose": stock_info.get("previousClose"),
        "volume": stock_info.get("volume"),
        "averageVolume": stock_info.get("averageVolume"),
        "marketCap": stock_info.get("marketCap"),
        "peRatio": stock_info.get("trailingPE"),
        "beta": stock_info.get("beta"),
        "dividendRate": stock_info.get("dividendRate"),
        "dividendYield": stock_info.get("dividendYield"),
        "exDividendDate": stock_info.get("exDividendDate"),
        "payoutRatio": stock_info.get("payoutRatio"),
        "fiftyDayAverage": stock_info.get("fiftyDayAverage"),
        "twoHundredDayAverage": stock_info.get("twoHundredDayAverage"),
        "news": stock.news[0:2],
        "day5": float(hist.iloc[-1]['Close']),
        "day4": float(hist.iloc[-2:-1]['Close']),
        "day3": float(hist.iloc[-3:-2]['Close']),
        "day2": float(hist.iloc[-4:-3]['Close']),
        "day1": float(hist.iloc[-5:-4]['Close']),
        "day0": float(hist.iloc[-6:-5]['Close']),
        "esg": esg, # give default values
        "gs": gs,
        "es": es,
        "ss": ss
    }

    return jsonify(relevant_info)

@cross_origin
@app.route('/func', methods=['GET'])
def runbackend():
    cntxt = request.args.get('cntxt', "I am interested in solar energy")
    new = request.args.get('new', "true")

    if new == "true":
        session.clear()


    if 'messages' not in session:
        session['messages'] = [
            {"role": "system", "content": "You are an AI assistant tasked with helping users build investment portfolios centered around responsible and sustainable companies. Your role is to analyze users' social goals and generate a tailored sample portfolio comprising 5 to 6 companies that align with those goals. The output must strictly adhere to the following format and guidelines:\n\n1. **Output Format**: Present the portfolio as JSON data. The JSON object should include an array of companies, where each company is represented as an object with two attributes: `ticker` (the company's stock ticker symbol) and `percentage` (the proportion of the portfolio allocated to this company, expressed as a percentage). \n\n2. **Justification**: After the list of companies, include a `justification` field within the JSON object. This field should contain a brief explanation detailing why each company was selected, emphasizing their alignment with the specified social goal.\n\n3. **Constraints**:\n   - The total percentage across all companies should sum to 100%.\n   - Only include company tickers and their respective portfolio percentages in the list of companies.\n   - Ensure the justification provides a clear connection between the companies chosen and the user's social goal.\n\n4. **Example Output Structure**:\n```json\n{\n  \"portfolio\": [\n    {\"ticker\": \"XXXX\", \"percentage\": 20},\n    {\"ticker\": \"YYYY\", \"percentage\": 20},\n    {\"ticker\": \"ZZZZ\", \"percentage\": 20},\n    {\"ticker\": \"AAAA\", \"percentage\": 20},\n    {\"ticker\": \"BBBB\", \"percentage\": 20}\n  ],\n  \"justification\": \"Each company selected for this portfolio focuses on [specific social goal], making them ideal for a responsible and sustainable investment strategy. [Brief explanation of each company's relevance].\"\n}\n```\n\nEnsure your response contains no additional text or data outside of this JSON structure. Your goal is to provide a concise, clear, and informative portfolio recommendation that aligns with the user's social objectives, formatted for easy integration and further analysis."}
        ]

    session['messages'].append({"role": "user", "content": cntxt})


    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=session['messages'],
            temperature=0.7,
            max_tokens=300,
    )
            
            # Extracting and printing the AI's response
    ai_message = response.choices[0].message['content'].strip()
    session['messages'].append({"role": "system", "content": ai_message})
    try:
        print(json.loads(ai_message))
    except:
        session.clear()
        cntxt = "I am interested in solar energy"
        if 'messages' not in session:
            session['messages'] = [
                {"role": "system", "content": "You are an AI assistant tasked with helping users build investment portfolios centered around responsible and sustainable companies. Your role is to analyze users' social goals and generate a tailored sample portfolio comprising 5 to 6 companies that align with those goals. The output must strictly adhere to the following format and guidelines:\n\n1. **Output Format**: Present the portfolio as JSON data. The JSON object should include an array of companies, where each company is represented as an object with two attributes: `ticker` (the company's stock ticker symbol) and `percentage` (the proportion of the portfolio allocated to this company, expressed as a percentage). \n\n2. **Justification**: After the list of companies, include a `justification` field within the JSON object. This field should contain a brief explanation detailing why each company was selected, emphasizing their alignment with the specified social goal.\n\n3. **Constraints**:\n   - The total percentage across all companies should sum to 100%.\n   - Only include company tickers and their respective portfolio percentages in the list of companies.\n   - Ensure the justification provides a clear connection between the companies chosen and the user's social goal.\n\n4. **Example Output Structure**:\n```json\n{\n  \"portfolio\": [\n    {\"ticker\": \"XXXX\", \"percentage\": 20},\n    {\"ticker\": \"YYYY\", \"percentage\": 20},\n    {\"ticker\": \"ZZZZ\", \"percentage\": 20},\n    {\"ticker\": \"AAAA\", \"percentage\": 20},\n    {\"ticker\": \"BBBB\", \"percentage\": 20}\n  ],\n  \"justification\": \"Each company selected for this portfolio focuses on [specific social goal], making them ideal for a responsible and sustainable investment strategy. [Brief explanation of each company's relevance].\"\n}\n```\n\nEnsure your response contains no additional text or data outside of this JSON structure. Your goal is to provide a concise, clear, and informative portfolio recommendation that aligns with the user's social objectives, formatted for easy integration and further analysis."}
            ]

        session['messages'].append({"role": "user", "content": cntxt})


        response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=session['messages'],
                temperature=0.7,
                max_tokens=300,
        )
                
                # Extracting and printing the AI's response
        ai_message = response.choices[0].message['content'].strip()
        session['messages'].append({"role": "system", "content": ai_message})


    return jsonify(ai_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
