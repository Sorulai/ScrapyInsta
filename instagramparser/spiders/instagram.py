import json
import re

import scrapy
from scrapy.http import HtmlResponse
from instagramparser.items import InstagramparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'michele.squad394'
    password = '#PWD_INSTAGRAM_BROWSER:9:1634746522:AVdQAHh/bsvJtF6H87t0yOLQkoE098G7/BRE0BhRUrvqq/5wPax+4re4MejlYiZcmLrzFXDgziPH0dn4zXY2TJp1M9tp2f3yDExB8DdFYX1jqaVyJui8cTZ2IxRAuMUdKLug5jJDFRfheuiX'
    list_users = ['_asya_0395', 'diachkina_elena']
    url = 'https://i.instagram.com/api/v1/friendships'
    follow = ['following/?', 'followers/?']

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={
                'username': self.inst_login,
                'enc_password': self.password
            },
            headers={
                'x-csrftoken': csrf
            }
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.list_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        count = 12
        search_surface = 'follow_list_page'

        for i in self.follow:
            users_following = f'{self.url}/{user_id}/{i}count={count}&search_surface={search_surface}'
            yield response.follow(
                users_following,
                callback=self.users_friends_parse,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'count': count,
                    'search_surface': search_surface,
                    'i': i
                }
            )

    def users_friends_parse(self, response: HtmlResponse, username, user_id, count, search_surface, i):
        j_data = response.json()
        if j_data.get('big_list'):
            max_id = j_data.get('next_max_id')
            users_following = f'{self.url}/{user_id}/{i}count={count}&max_id={max_id}&search_surface={search_surface}'
            yield response.follow(
                users_following,
                callback=self.users_friends_parse,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'count': count,
                    'search_surface': search_surface,
                    'i': i
                }
            )
            posts = j_data.get('users')
            for post in posts:
                name = post.get('full_name')
                friend_id = post.get('pk')
                photo = post.get('profile_pic_url')
                main_name = username
                status = i.replace('/?', '')

                item = InstagramparserItem(
                    main_name=main_name,
                    name=name,
                    id_user=friend_id,
                    photo=photo,
                    status=status
                )
                yield item

    @staticmethod
    def fetch_csrf_token(text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    @staticmethod
    def fetch_user_id(text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
