from newsapi import NewsApiClient
from dbase.connection import DbConnect
from dbase.models import News
from settings import TIME_ZONE, NEWS_UPDATE_INTERVAL, NEWS_API_KEY, NEWS_SETTINGS

from toolbox import ToolBox

session = DbConnect.get_session()
logger = ToolBox.get_logger('news')


class NewsMethods:
    """
    NewsApi wrapper
    """
    last_grab = None

    def __init__(self):
        self.api = NewsApiClient(api_key=NEWS_API_KEY)
        logger.debug('news daemon initialised')
        last_news = News().get_last()
        if last_news:
            self.last_grab = last_news.created_at
        if not self.last_grab:
            current_news = self.grab_and_store()
            self.last_grab = current_news.created_at

    def start(self):
        """
        main loop
        :return:
        """
        import datetime
        import time
        logger.debug('news daemon started')
        while True:
            time_delta = datetime.datetime.now(tz=TIME_ZONE) - TIME_ZONE.fromutc(self.last_grab)
            if time_delta.seconds > NEWS_UPDATE_INTERVAL * 60:
                self.grab_and_store()
                time.sleep(5)
            else:
                time.sleep(5)

    def grab_and_store(self):
        headlines = self.api.get_top_headlines(**NEWS_SETTINGS)
        decrypt = headlines['articles']
        news_item = None
        for article in decrypt:
            news_item = News(author=article['author'], title=article['title'],
                             source=article['source']['id'])
            session.add(news_item)
            session.commit()
        return news_item
