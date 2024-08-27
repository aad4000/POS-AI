PROXY_FILE = 'lib/active_proxies.txt'

TIMEOUT = 120
PROXY_TIMEOUT = 10

CAPTCHA_MAX_ATTEMPTS = 8

GET_RESPONSE_MAX_ATTEMPS = 5

CONFIG_SELENIUM = {
    
    "amazon" : {
        "description_selector": "#productTitle",
        "price_selector": ["span.a-price-symbol", "span.a-price-whole", "span.a-price-fraction"],
        "captcha": "image_text"},
    "ar.aliexpress":{
        "description_selector": ".title--wrap--UUHae_g h1",
        "price_selector": ".price--currentPriceText--V8_y_b5",
        "captcha": "image_text"
    },

    
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
    "katranji":{ "description_selector": "div.text-xl.md\\:text-2xl.xl\\:text-3xl.font-bold.mb-4.w-3\\/4",
        "price_selector": "div.font-bold.text-\\[2\\.5rem\\]"},
    "alibaba":{
        "description_selector": "h1[title]",
        "price_selector": "div.product-price div.price-list div.price-item:first-of-type div.price span"
    },
    "newegg":{
        "description_selector": "h1.product-title",
        "price_selector":["li.price-current strong","li.price-current sup"]
    },
    "ayoubcomputers":{
        "description_selector": "h1.productView-title",
        "price_selector": "span.price.price--withoutTax.price--main"
    },
    "techzone.lb":{
       "description_selector" :"h1.product_title.entry-title.wd-entities-title",
        "price_selector":"p.price span.woocommerce-Price-amount"
    },
    "ebay":{
        "description_selector" : "h1.x-item-title__mainTitle span.ux-textspans.ux-textspans--BOLD",
        "price_selector" : "div.x-price-primary span.ux-textspans"

    },
    }

    

