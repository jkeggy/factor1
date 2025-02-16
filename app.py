from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('h2').text.strip() if soup.find('h2') else ''

        # Extract subtitle
        subtitle = soup.find('h4').text.strip() if soup.find('h4') else ''

        # Extract description and ingredients
        description_div = soup.find('div', class_='web-1u68b9m')
        if description_div:
            description = description_div.find('p').text.strip() if description_div.find('p') else ''
            ingredients_paragraphs = description_div.find_all('p')
            ingredients = ingredients_paragraphs.text.strip() if len(ingredients_paragraphs) > 1 else ''
        else:
            description = ''
            ingredients = ''

        # Extract image
        image = soup.find('img')['src'] if soup.find('img') else ''

        # Extract nutrition information
        nutrition_div = soup.find('div', attrs={'data-test-id': 'recipe-nutrition'})
        nutrition_raw = nutrition_div.text.strip() if nutrition_div else ''
        nutrition_info = format_nutrition_info(nutrition_raw)

        return jsonify({
            'title': title,
            'subtitle': subtitle,
            'image_url': image,
            'description': description,
            'ingredients': ingredients,
            'nutrition_info': nutrition_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to format nutrition information
def format_nutrition_info(nutrition_raw):
    # Remove "Per serving"
    nutrition_raw = nutrition_raw.replace("Per serving", "").strip()
    # Use regex to find key-value pairs
    pattern = r'([a-zA-Z ]+): (\d+\.?\d* [a-zA-Z%]+)'
    nutrition_pairs = re.findall(pattern, nutrition_raw)
    # Join the pairs into a formatted string
    formatted_nutrition = ", ".join([f"{key}: {value}" for key, value in nutrition_pairs])
    return formatted_nutrition

if __name__ == '__main__':
    app.run(debug=True)