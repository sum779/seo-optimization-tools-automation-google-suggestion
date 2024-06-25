from flask import Flask, render_template, request, jsonify, send_file
from bs4 import BeautifulSoup
import requests
import pandas as pd
import io
from io import BytesIO

app = Flask(__name__)

def get_google_suggestions(query, hl='en'):
    url = f"https://www.google.com/complete/search?hl={hl}&output=toolbar&q={query}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'xml')
    suggestions = [suggestion['data'] for suggestion in soup.find_all('suggestion')]
    return suggestions

def get_extended_suggestions(base_query, hl='en'):
    extended_suggestions = set()
    extended_suggestions.update(get_google_suggestions(base_query, hl))
    for char in 'abcdefghijklmnopqrstuvwxyz':
        extended_suggestions.update(get_google_suggestions(base_query + ' ' + char, hl))
    return list(extended_suggestions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggestions', methods=['POST'])
def suggestions():
    base_query = request.form['query']
    all_suggestions = {}
    all_suggestions["Google Suggest completions"] = get_google_suggestions(base_query)
    all_suggestions["Can questions"] = get_google_suggestions("Can " + base_query)
    all_suggestions["How questions"] = get_google_suggestions("How " + base_query)
    all_suggestions["Where questions"] = get_google_suggestions("Where " + base_query)
    all_suggestions["Versus"] = get_google_suggestions(base_query + " versus")
    all_suggestions["For"] = get_google_suggestions(base_query + " for")
    return render_template('results.html', suggestions=all_suggestions)

@app.route('/download', methods=['POST'])
def download():
    base_query = request.form['query']
    all_suggestions = {}
    all_suggestions["Google Suggest completions"] = get_google_suggestions(base_query)
    all_suggestions["Can questions"] = get_google_suggestions("Can " + base_query)
    all_suggestions["How questions"] = get_google_suggestions("How " + base_query)
    all_suggestions["Where questions"] = get_google_suggestions("Where " + base_query)
    all_suggestions["Versus"] = get_google_suggestions(base_query + " versus")
    all_suggestions["For"] = get_google_suggestions(base_query + " for")

# Create a DataFrame from the suggestions
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in all_suggestions.items()]))

    # Save the DataFrame to a CSV file
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    # Return the CSV file as a response
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),  # Use io.BytesIO for binary data
        mimetype='text/csv',
        as_attachment=True,
        download_name='data.csv'
    )  # Add the closing parenthesis here

if __name__ == '__main__':
    app.run(debug=True)
