import yt_scraper.youscrape
import pprint

if __name__ == "__main__":
    print("Hello")
    scraper = yt_scraper.youscrape.YouScraper()
    gmm_channel = scraper.get_channel_info("UC4PooiX37Pld1T8J5SYT-SQ", return_info={"viewCount", "subscriberCount", "keywords"})
    pprint.pprint(gmm_channel)

    print("Channel List for cooking channels")
    cooking_channels = scraper.search_channels("cooking channels in usa", 10, topicId="/m/02wbm")
    pprint.pprint(len(cooking_channels))