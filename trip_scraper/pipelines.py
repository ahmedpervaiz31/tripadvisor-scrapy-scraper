# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from mysql.connector import Error
from scrapy.exceptions import DropItem


class TripScraperPipeline:
    def __init__(self):
        pass
    
    def open_spider(self, spider):
        try:
            self.connect_db = mysql.connector.connect(
                host=spider.settings.get('MYSQL_HOST'),
                database=spider.settings.get('MYSQL_DATABASE'),
                user=spider.settings.get('MYSQL_USER'),
                password=spider.settings.get('MYSQL_PASSWORD')
            )
            self.cursor = self.connect_db.cursor()
            spider.logger.info("MySQL connection set up")
        except:
            spider.logger.error(f"Cannot connect to MySql {Error}")
            raise Error
        
    def close_spider(self, spider):
        if self.connect_db.is_connected():
            self.connect_db.commit()
            self.cursor.close()
            self.connect_db.close()
            spider.logger.info("MySQL connection closed.")
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        name = adapter.get('restaurant_name')

        # duplicate check on name (PK)
        if self.check_duplicate(name, spider):
            spider.logger.info(f"Duplicate item found: {name}")
            raise DropItem(f"Duplicate item found: {name}")

        # Insert item into the Db
        try:
            self.cursor.execute(
                """
                INSERT INTO restaurants (restaurant_name, url, about, rating, price_range, cuisine, 
                                         special_diet, meals, features, location, 
                                         google_maps_link, website, email, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    adapter.get('url'),
                    adapter.get('about'),
                    adapter.get('rating'),
                    adapter.get('price_range'),
                    adapter.get('cuisine'),
                    adapter.get('special_diet'),
                    adapter.get('meals'),
                    adapter.get('features'),
                    adapter.get('location'),
                    adapter.get('google_maps_link'),
                    adapter.get('website'),
                    adapter.get('email'),
                    adapter.get('phone_number')
                )
            )
            self.connect_db.commit()
            spider.logger.info(f"Item inserted: {name}")
        except Error as e:
            spider.logger.error(f"Error inserting item: {e}")
            raise DropItem(f"Error inserting item: {e}")

        return item  
        
    def check_duplicate(self, name, spider):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM restaurants WHERE restaurant_name = %s", (name,))
            result = self.cursor.fetchone()
            if result and result[0] > 0:
                return True
            return False
        
        except Error as e:
            spider.logger.error(f"Error checking for duplicate: {e}")
            raise DropItem(f"Error checking for duplicate: {e}")