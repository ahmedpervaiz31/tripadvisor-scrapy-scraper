# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class RestaurantItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    about = scrapy.Field()
    rating = scrapy.Field()
    price_range = scrapy.Field()
    cuisine = scrapy.Field()
    special_diet = scrapy.Field()
    meals = scrapy.Field()
    features = scrapy.Field()
    location = scrapy.Field()
    google_maps_link = scrapy.Field()
    website = scrapy.Field()
    email = scrapy.Field()
    phone_number = scrapy.Field()