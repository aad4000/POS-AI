from urllib.parse import urlparse
from flask import Flask, request, jsonify
from .Scraping_service import (
    handle_katranji, handle_ayoub_computer, fetch_product, 
    handle_alibaba, handle_newegg, handle_techzone, generate_prompt, 
    get_completion, handle_amazon, calculate_match_score, extract_numerical_price
)
import json

app = Flask(__name__)

# Mapping of company domains to their respective handler functions
known_companies = {
    "katranji.com": handle_katranji,
    "ayoubcomputers.com": handle_ayoub_computer,
    "www.alibaba.com": handle_alibaba,
    "newegg.com": handle_newegg,
    "techzone.com.lb": handle_techzone,
    "www.amazon.com": handle_amazon,
}


def check_validity():
    data = request.get_json()

    # Validate input data
    url = data.get('url')
    description = data.get('description')
    price = data.get('price')

    if not url:
        return jsonify({"error": "URL is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not price:
        return jsonify({"error": "Price is required"}), 400

    # Ensure price is a valid number
    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "Price must be a number"}), 400

    # Validate URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({"error": "Invalid URL"}), 400
    except ValueError:
        return jsonify({"error": "Invalid URL"}), 400

    # Fetch product information based on the URL
    result = fetch_product(url)
    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    # Extract scraped price
    scraped_price = result.get('price')
    if not scraped_price:
        return jsonify({"error": "Scraped price not found"}), 500

    # Debugging information
    print(f"Raw scraped_price: {scraped_price}, type: {type(scraped_price)}")

    # Determine if the scraped price is a string or a float
    if isinstance(scraped_price, str):
        try:
              
            extracted_price = extract_numerical_price(scraped_price)  # Extract numeric value from string
        except ValueError as e:
            return jsonify({"error": f"Price extraction failed: {str(e)}"}), 500
    elif isinstance(scraped_price, (int, float)):
        extracted_price = float(scraped_price)  # Ensure it's a float
    else:
        return jsonify({"error": f"Unexpected price format: {scraped_price} of type {type(scraped_price)}"}), 500

    # Debugging information after extraction
    print(f"Extracted numeric price: {extracted_price}, type: {type(extracted_price)}")

    # Generate prompt for the Claude model
    score = calculate_match_score(price, extracted_price)
    prompt = generate_prompt(price, extracted_price, score)

    # Interact with the Claude model to get comparison results
    try:
        comparison_result = get_completion(prompt)

        # Check if the response is empty or invalid
        if not comparison_result:
            return jsonify({"error": "No response received from Claude model."}), 500

        # Extract the JSON content from Claude's text response
        if isinstance(comparison_result, list) and 'text' in comparison_result[0]:
            result_text = comparison_result[0]['text']
        else:
            return jsonify({"error": "Unexpected response format from Claude model."}), 500

        # Find the start and end of the JSON object in the text response
        start_index = result_text.find("{")
        end_index = result_text.rfind("}") + 1

        if start_index != -1 and end_index != -1:
            # Extract and parse the JSON object
            json_string = result_text[start_index:end_index]
            parsed_json = json.loads(json_string)

            formatted_result = {
                "score": parsed_json.get("match_score"),
                "analysis": parsed_json.get("analysis")
            }
            return jsonify({"result": formatted_result})
        else:
            return jsonify({"error": "Failed to extract JSON from the response."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


