from flask_login import UserMixin
class UserLogin(UserMixin):

    # берем пользователя по айпи и загружаем в него всю информацию

    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    # def is_authenticated(self):     #Скрыты из-за USER_MIXIN
    #     # функция проверки авторизации пользователя
    #     return True
    #
    # def is_active(self):
    #     # функция проверки что пользователь активен
    #     return True
    #
    # def is_anonymous(self):
    #     # функция определяюща неавторизованных пользователей
    #     return False

    def get_id(self):
        # функция определяющая уникальный идентификатор(должен быть представлен в виде unicode-строки)
        return str(self.__user['id'])
    def getName(self):
        return self.__user['name'] if