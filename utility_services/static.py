PROXY_FILE = 'lib/active_proxies.txt'

TIMEOUT = 120
PROXY_TIMEOUT = 10

CAPTCHA_MAX_ATTEMPTS = 8

GET_RESPONSE_MAX_ATTEMPS = 5

CONFIG_SELENIUM = {
    "gamebroslb": {
        "description_selector": "div.product__title h1",
        "price_selector":"span.price-item.price-item--regular",
    },
    "460estore": {
        "description_selector": "h1.namne_details",
        "price_selector": "span[itemprop='price'][content='5']"
    },
    "amazon" : {
        "description_selector": "#productTitle",
        "price_selector": "span.a-offscreen",
        "captcha" : "image_text"
    }

}

CONFIG_BS4 = {
    "gamebroslb": {
        "description_selector": "div.product__title h1",
        "price_selector":"span.price-item.price-item--regular",
    },
    "460estore": {
        "description_selector": "h1.namne_details",
        "price_selector": "span[itemprop='price'][content='5']"
    },
    "amazon" : {
        "description_selector": "#productTitle",
        "price_selector": "span.a-offscreen",
        "captcha" : "image_text"
    }

}