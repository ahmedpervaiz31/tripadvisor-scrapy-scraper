import scrapy
import sys
sys.path.append('..')
from items import RestaurantItem
sys.path.append('/spiders')

API_KEY = '5116d8272d3452283b011e9b4c578bf5'
MAX_PAGE_NUM = 4

class RestaurantSpider(scrapy.Spider):
    name = "restaurant_spider"
    start_urls = [
            'https://www.tripadvisor.com/Restaurants-g28926-California.html'
    ]
    pagination_url = 'https://www.tripadvisor.com/Restaurants-g28926-oa{offset}-California.html'
    proxy_url = "http://scraperapi:5116d8272d3452283b011e9b4c578bf5@proxy-server.scraperapi.com:8001"
    
    def generate_request(self, url, callback):
        return scrapy.Request(
            url=url,
            callback=callback,
            meta={"proxy": self.proxy_url}
        )
    
    def start_requests(self):
        return [self.generate_request(self.start_urls[0], self.parse)]

    def parse(self, response):
        # Start by scraping city links from the first page
        yield from self.scrape_cities(response)

        # Continue for next pages
        for page in range(2, MAX_PAGE_NUM):
            offset = (page - 1) * 20
            next_page_url = self.pagination_url.format(offset=offset)
            
            yield self.generate_request(next_page_url, self.scrape_cities)
        
    def scrape_cities(self, response):
        # if page 1
        if response.url == self.start_urls[0]:
            geo_name_links = response.css('div.geo_name a::attr(href)').getall()
            for city_link in geo_name_links:
                city_url = response.urljoin(city_link)
                yield {'city_url': city_url}
                
                # request to scrape restaurants
                yield self.generate_request(city_url, self.scrape_restaurants)
        else:
            # Scraping next pages
            li_elements = response.css('ul.geoList li')
            for li in li_elements:
                city_link = li.css('a::attr(href)').get()
                if not city_link:
                    continue
                
                city_url = response.urljoin(city_link)
                yield {'city_url': city_url}
                
                yield self.generate_request(city_url, self.scrape_restaurants)
            
    def scrape_restaurants(self, response):
        # get all links with /restaurant-review
        restaurant_links = response.css('a[href*="/Restaurant-Review"]::attr(href)').getall()

        for link in restaurant_links:
            restaurant_url = response.urljoin(link)
            
            yield {'restaurant_url': restaurant_url}
            
            yield self.generate_request(restaurant_url, self.scrape_restaurant_details)

                
    def scrape_restaurant_details(self, response):
        name = self.extract_name(response)
        rating = self.extract_rating(response)
        about, price_range, cuisine, special_diet, meals, features = self.extract_details(response)
        location, google_maps_link = self.extract_location(response)
        website = self.extract_website(response)
        email = self.extract_email(response)
        phone_number = self.extract_phone_number(response)

        restaurant_item = RestaurantItem(
            response.url, name, about, rating, price_range, cuisine, special_diet, meals, 
            features, location, google_maps_link, website, email, phone_number
        )

        yield restaurant_item
        
    def extract_name(self, response):
        name = response.css('div.biGQs._P.egaXP.rRtyp::text').get().strip()
        return name
    
    def extract_rating(self, response):
        rating_div = response.css('div.sOyfn.u.f.K')
        if not rating_div:
            return "N/A"
        
        rating = rating_div.css('span.biGQs._P.fiohW.uuBRH::text').get().strip()
        return rating

    def extract_details(self, response):
        details_dict = {
            'About': "N/A",
            'PRICE RANGE': "N/A",
            'CUISINES': "N/A",
            'Special Diets': "N/A",
            'Meals': "N/A",
            'FEATURES': "N/A"
        }
        
        titles = response.css('div.MJ > div.Wf > div.biGQs._P.ncFvv.NaqPn::text').getall().strip()
        details = response.css('div.biGQs._P.pZUbB.alXOW.eWlDX.GzNcM.ATzgx.UTQMg.TwpTY.hmDzD::text').getall().strip()
        
        for title, detail in zip(titles, details):
            if title in details_dict:
                details_dict[title] = detail

        return (
            details_dict['About'],
            details_dict['PRICE RANGE'],
            details_dict['CUISINES'],
            details_dict['Special Diets'],
            details_dict['Meals'],
            details_dict['FEATURES']
        )

    def extract_location(self, response):
        # Search for google link
        location_link_element = response.css('a[href^="https://maps.google.com/maps"]')

        # Get the link and address
        location_link = (location_link_element.css('::attr(href)').get() or "N/A").strip()
        location_address = (location_link_element.css('span::text').get() or "N/A").strip()
        
        return location_address, location_link

    def extract_website(self, response):
        website_link = response.css('a[href^="http"]::attr(href)').get() or "N/A"
        
        return website_link.strip()
        
    def extract_email(self, response):
        email_link = response.css('a[href^="mailto:"]::attr(href)').get() or "N/A"

        return email_link.replace('mailto:', '').strip()

    def extract_phone_number(self, response):
        phone_link = response.css('a[href^="tel:"]::attr(href)').get() or "N/A"
        
        return phone_link.replace('tel:', '').strip()
