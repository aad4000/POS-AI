import requests
import threading

# Function to test a single proxy
def test_proxy(proxy, valid_proxies):
    url = "http://www.google.com"
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            print(f"Valid proxy found: {proxy}")
            valid_proxies.append(proxy)
    except requests.RequestException:
        pass

def main():
    # Read proxies from file
    with open("proxies.txt", "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]

    valid_proxies = []
    threads = []

    # Create a thread for each proxy
    for proxy in proxy_list:
        thread = threading.Thread(target=test_proxy, args=(proxy, valid_proxies))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Write valid proxies to file
    with open("valid_proxies.txt", "w") as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")

    print("Valid proxies have been saved to valid_proxies.txt")

if __name__ == "__main__":
    main()
