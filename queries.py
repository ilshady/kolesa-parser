import pymysql.cursors


class Queries:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = database
        self.cursor = self.connection.cursor()
        #print("connected")

    def get_subscriptions(self, status = True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `status` = %s", (status))
            result = self.cursor.fetchall()
            #print("get_subscriptions")
            return result

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = %s', user_id)
            result = self.cursor.fetchall()
            #print("subscriber_exists")
            return bool(len(result))

    def add_subscriber(self, user_id, status = True):
        """Добавляем нового подписчика"""
        with self.connection:
            #print("add_subscriber")
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`) VALUES(%s,%s)", (user_id,status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            #print("update_subscription")
            return self.cursor.execute("UPDATE `users` SET `status` = %s WHERE `user_id` = %s", (status, user_id))
    
    def check_item_db(self):
        """Получаем все записи с таблицы"""
        with self.connection:
            result = self.cursor.execute('SELECT post_id,link FROM posts')
            result = self.cursor.fetchmany(10)
            #print(result)
            return result
    def send_to_db(self,post_id,link):
        with self.connection:
            #print("send_to_db")
            return self.cursor.execute("INSERT INTO posts (post_id, link ) VALUES (%s,%s)",(post_id, link))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()