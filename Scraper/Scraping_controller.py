# controller.py
from flask import request, send_file, jsonify
import os

from flask import request, jsonify
from .Scraping_service import filter_active_proxies, get_valid_proxy, scrape_price_and_description

def filter_proxies():
    """
    Handles the POST request to filter active proxies from a text file and returns the filtered proxies as a text file.
    """
    data = request.get_json()
    input_file = data.get('input_file')
    output_file = data.get('output_file')
    
    if not input_file or not output_file:
        return jsonify({"error": "input_file and output_file are required"}), 400
    
    # Call the service to filter active proxies
    result = filter_active_proxies(input_file, output_file)
    
    if not result["active_proxies"]:
        return jsonify({"error": "No active proxies found"}), 200
    
    # Check if the output file was created
    if not os.path.exists(output_file):
        return jsonify({"error": "Failed to create the output file"}), 500

    # Return the output file as a response
    return send_file(output_file, as_attachment=True, download_name=os.path.basename(output_file))

def fetch_product():
    data = request.get_json()
    url = data.get('url')
    proxy_file = 'lib/active_proxies.txt'
    max_retries = data.get('max_retries', 5)
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    proxies_json = get_valid_proxy(proxy_file)

    if "error" in proxies_json:
        return jsonify(proxies_json), 500

    proxies = proxies_json['proxies']
    retry_count = 0

    for proxy in proxies:
        if retry_count >= max_retries:
            return jsonify({"error": f"Reached maximum retry limit of {max_retries}."})

        if proxy.startswith("http://") or proxy.startswith("https://"):
            result = scrape_price_and_description(url, proxy)
            
            if "price" in result and "description" in result:
                return jsonify(result)
        
        retry_count += 1

    return jsonify({"error": "All proxies failed."}), 500
