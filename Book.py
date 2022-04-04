from enum import Enum


class ThemeLabel(Enum):
    UNKN = 'Неизвестно'
    PEOP = 'Люди'
    LIFE = 'Жизнь'
    LOVE = 'Любовь'
    VAMP = 'Вампиры'
    TRAV = 'Путешествия'
    FUTU = 'Будущее'
    MAGI = 'Магия'
    PROD = 'Продуктивность'

    @classmethod
    def _missing_(cls, value):
        return ThemeLabel.UNKN


class CategoryLabel(Enum):
    UNKN = 'Неизвестно'
    DETE = 'Детектив'
    FANT = 'Фэнтези'
    FICT = 'Научная фантастика'
    DRAM = 'Драма'
    HORR = 'Ужасы'
    ROMA = 'Роман'
    BIOG = 'Биография'

    @classmethod
    def _missing_(cls, value):
        return CategoryLabel.UNKN


class Book:
    def __init__(self, name=None, author=None, book_args=[None] * 5, margin=None, start_rating=None, copies_num=None):
        self.name, self.author = name, author
        self.publishing, self.year, self.pages_num, self.theme, self.category = book_args
        self.theme = ThemeLabel(self.theme)
        self.category = CategoryLabel(self.category)

        self.margin, self.start_rating, self.copies_num = margin, start_rating, copies_num
        self.rating = self.start_rating

        if not self.pages_num: self.pages_num = 100
        if not self.margin: self.margin = 0
        self.price = int(self.pages_num * (1 + self.margin / 100))

    def get_args(self):
        return self.name, self.author, self.publishing, self.year, \
               self.pages_num, self.theme.value, self.category.value, self.price, self.copies_num

    def get_name(self):
        if self.name and self.author:
            *author1, author2 = self.author.split()
            author = author1[0][0] + '.' + author2
            return ", ".join([author, self.name])
        elif self.name: 
            return self.name
        elif self.author: 
            return self.author
        else:
            return 111

    def __str__(self):
        return f"{self.author}, {self.name}, {self.publishing}, {self.year}, {self.copies_num}"

    def __eq__(self, other):
        return self.name == other.name


    def recalculate_price(self, day_num): 
        ''' Функция перерасчет цены с учетом измененной наценки на данный день эксперимента '''
        if (2022 - self.year) < day_num and self.margin != 0:
            self.margin -= 1
            self.price = int(self.pages_num * (1 + self.margin / 100))


    def recalculate_rating(self, orders_num, all_orders): # пересчет рейтинга книги
        ''' Функция пересчет рейтинга книги в зависимости от кол-ва её заказов '''
        self.rating = orders_num / all_orders * 10
        self.rating += self.start_rating
        self.rating = round(self.rating, 2)
        if self.rating > 10: self.rating = 10
