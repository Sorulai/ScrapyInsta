from pymongo import MongoClient

client = MongoClient('localhost', 27017)
mongo_base = client.instagramParser

user_str = input('Введите ник пользователя: ')
user_str_2 = input('Введите кого хотите найти, подписчиков или подписки: ')


def request_db(username, status_us, db):
    if username in db.list_collection_names():
        collection = db[username]
        if status_us.lower() == 'подписчики':
            return collection.find({'status': 'followers'})
        elif status_us.lower() == 'подписки':
            return collection.find({'status': 'following'})


for i in request_db(user_str, user_str_2, mongo_base):
    print(i)
