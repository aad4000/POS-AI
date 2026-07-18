# POS-AI

Price verification service built for a purchase order system. When an employee submits a
purchase order with a product link and a claimed price, this service scrapes the live
price from the vendor's page, compares it to the claimed one, and returns a match score
with a short written analysis. The idea is to catch wrong or outdated prices before an
order gets approved.

## Architecture

Flask app with one main endpoint. The request body is:

```json
{
  "url": "https://www.vendor.com/product/...",
  "description": "product description",
  "price": 250.00
}
```

and the response looks like:

```json
{
  "result": {
    "score": 95,
    "analysis": "The scraped price is slightly lower than the provided price..."
  }
}
```

The scraping strategy depends on the vendor. Each supported store has a config entry in
`scraper/static.py` with its CSS selectors:

- Static sites (several Lebanese electronics stores, eBay) are fetched with requests +
  BeautifulSoup, going through a rotating proxy list with retries.
- JavaScript-heavy sites (Amazon, AliExpress) go through headless Chrome with Selenium.
  Amazon sometimes serves its image captcha instead of the page, which is handled with
  AWS Textract OCR and a retry loop.

Supporting a new store is just adding its selectors to the config, no code changes.

The score itself is the percentage difference between the two prices, and Claude 3.5
Sonnet (through AWS Bedrock) writes the two-line analysis that goes back to the client.

## Running it

```
pip install -r requirements.txt
python index.py
```

Needs AWS credentials for Bedrock and Textract. `proxy/proxies.txt` holds the proxy pool,
`proxy/proxy_checker_service.py` filters the working ones into `valid_proxies.txt`.

The repo also has the deployment setup used on AWS: Dockerfile, ECS task definition
(`taskdef.json`), and CodeBuild/CodeDeploy specs.
