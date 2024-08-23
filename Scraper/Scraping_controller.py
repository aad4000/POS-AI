from urllib.parse import urlparse
from flask import request, send_file, jsonify
import os
from .Scraping_service import handle_katranji, handle_ayoub_computers, fetch_product, handle_alibaba

known_companies = {
    "katranji.com": handle_katranji,
    "ayoubcomputers.com": handle_ayoub_computers,
    "www.alibaba.com": handle_alibaba
}

def check_validity():
    data = request.get_json()
    
    # Check if required fields are provided
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    description = data.get('description')
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    price = data.get('price')
    if not price:
        return jsonify({"error": "Price is required"}), 400
    
    # Check if price is a valid number
    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "Price must be a number"}), 400
    
    # Check if the URL is valid
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return jsonify({"error": "Invalid URL"}), 400
    except ValueError:
        return jsonify({"error": "Invalid URL"}), 400

    # Fetch product information
    result = fetch_product(url)
    if "error" in result:
        return jsonify(result), 400  # Return the error with a 400 status code
    
    return jsonify(result)
