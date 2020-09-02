import pymysql.cursors


class Requests:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = database
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `status` = %s", (status,))
            result = self.cursor.fetchall()
            return result

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = %s', user_id)
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status = True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`) VALUES(%s,%s)", (user_id,status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `status` = %s WHERE `user_id` = %s", (status, user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()