from urllib.parse import urlparse
from flask import request, jsonify
from .Scraping_service import handle_katranji, handle_ayoub_computer, fetch_product, handle_alibaba, handle_newegg, handle_techzone, generate_prompt, get_completion,handle_amazon
import json

# Mapping of company domains to their respective handler functions
known_companies = {
    "katranji.com": handle_katranji,
    "ayoubcomputers.com": handle_ayoub_computer,
    "www.alibaba.com": handle_alibaba,
    "newegg.com": handle_newegg,
    "techzone.com.lb": handle_techzone
}
known_companiess={
    "www.amazon.com": handle_amazon,
}

def check_validity():
    data = request.get_json()

    # Validate input data
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    description = data.get('description')
    if not description:
        return jsonify({"error": "Description is required"}), 400

    price = data.get('price')
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

    # Extract scraped price and description
    scraped_price = result.get('price')
    scraped_description = result.get('description')

    # Generate prompt for Claude model
    prompt = generate_prompt(price, description, scraped_price, scraped_description)

    # Interact with Claude model to get comparison results
    try:
        comparison_result = get_completion(prompt)
        
        # Extract the JSON content from Claude's text response
        result_text = comparison_result[0]['text']

        # Find the start of the JSON object in the text response
        start_index = result_text.find("{")
        end_index = result_text.rfind("}") + 1
        
        if start_index != -1 and end_index != -1:
            # Extract and parse the JSON object
            json_string = result_text[start_index:end_index]
            parsed_json = json.loads(json_string)

            formatted_result = {
                "score": parsed_json.get("match_score"),
                "is_match": parsed_json.get("is_match"),
                "analysis": parsed_json.get("analysis")
            }
            return jsonify({"result": formatted_result})
        else:
            return jsonify({"error": "Failed to extract JSON from the response."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
