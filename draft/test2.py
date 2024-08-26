import re

def extract_numerical_price(price_str):
    # Remove any commas and currency symbols from the price string
    cleaned_price_str = re.sub(r'[^\d\.]', '', price_str)
    
    # Find the first sequence of digits, optionally followed by a decimal point and more digits
    match = re.search(r'\d+\.?\d*', cleaned_price_str)
    
    if match:
        return float(match.group())
    else:
        raise ValueError("No numerical part found in the price string.")

def calculate_match_score(user_price, scraped_price):
       
    # Extract the numerical part of the scraped price
    fscraper_price = extract_numerical_price(scraped_price)
    
    # Ensure both prices are now floats
    user_price = float(user_price)
    fscraper_price = float(fscraper_price)
    print(user_price, fscraper_price)
    # Calculate the absolute difference between the prices
    absolute_difference = abs(user_price - fscraper_price)
    
    # Calculate the percentage difference relative to the user-provided price
    percentage_difference = (absolute_difference / user_price) * 100
    
    # Calculate the match score
    score = max(0, 100 - percentage_difference)
    
    # Return the score as an integer
    return int(score)
def main():
    x="$3,099.00"
    y="129.45"
    score=calculate_match_score(y,x)
    print(score)

if __name__ == "__main__":
    main()
