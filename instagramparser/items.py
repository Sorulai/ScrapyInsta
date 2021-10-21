# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramparserItem(scrapy.Item):
    # define the fields for your item here like:
    main_name = scrapy.Field()
    name = scrapy.Field()
    id_user = scrapy.Field()
    photo = scrapy.Field()
    status = scrapy.Field()
    _id = scrapy.Field()

