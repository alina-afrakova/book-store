import csv
from copy import deepcopy
from typing import List, Tuple
from Book import Book
from Order import PublishingOrder


class Stock:
    min_copies = 3   # минимальое кол-во копий книги, которые должны быть на складе
    start_copies = 5 # начальное кол-во копий каждой книги

    def __init__(self, books_file: str,  *shop_args: Tuple[int]):
        self.book_list = self.extract_books(books_file, shop_args)
        self.num_books  = len(self.book_list) * self.start_copies 

    def extract_books(self, books_file: str, shop_args: Tuple[int]) -> List[Book]:
        """ Функция излечения начального списка книг (с их инициализацией) из csv-файла """
        with open(books_file, 'r', encoding='utf-8') as in_file:
            csv_reader = csv.reader(in_file, delimiter=';') # quoting = csv.QUOTE_NONNUMERIC, quotechar='"')
            self.headers = next(csv_reader)
            book_list = []
            to_int = lambda s: int(s) if s else None
            for row in csv_reader:
                row[-3], row[-4] = to_int(row[-3]), to_int(row[-4]) # год издания и кол-во страниц
                name, author = row[:2]
                start_rating = shop_args[-1]
                if row[-4] >= 2020: margin = shop_args[1]
                else: margin = shop_args[0]
                book = Book(name, author, row[2:], margin, start_rating, self.start_copies)
                book_list.append(book)
        return book_list


    def lookup(self, book: Book) -> Book:
        """ Функция поиска книги по названию/автору, возвращает найденную книгу со склада """
        find_book = None
        if book.name is None:
            ind = self.find_the_last(book.author)

        elif book in self.book_list:
            ind = self.book_list.index(book)

        find_book = self.book_list[ind]

        #return ind
        return find_book


    def find_the_last(self, author: str) -> int:
        """ Функция нахождения последней выпущенной книги автора """
        last_year, last_book = 0, None
        for i, book in enumerate(self.book_list):
            if book.author == author and book.year > last_year:
                last_year = book.year
                last_book = book
        return i
        #last_book = max(filter(lambda book: book.author == author, self.book_list), key=lambda book: book.year)


    def remove(self, book: Book, copies: int):
        """ Функция изъятия copies экземпляров книги book со склада """
        need_copies = 0
        book.copies_num -= copies
        if book.copies_num < 0:
            need_copies = abs(book.copies_num)
            book.copies_num = 0
        return need_copies


    def check_min_copies(self) -> List[Tuple[Book, int]]:
        ''' Функция проверки всех книг на наличие минимального кол-ва копий '''
        refill = []
        for book in self.book_list:
            if book.copies_num < self.min_copies:
                refill.append((book, self.min_copies - book.copies_num))
        return refill


    def add(self, books: List[Book]):
        """ Функция добавления на склад списка книг """
        for book in books:
            ind = self.book_list.index(book)
            self.book_list[ind].copies_num += book.copies_num
            book.copies_num = 0


class BookShop:
    start_margin = 5  # стартовая розничная наценка
    margin_new = 15   # розничная наценка для новых книг
    start_rating = 5  # стартовой рейтинг

    def __init__(self, books_file: str):
        self.stock = Stock(books_file, self.start_margin, self.margin_new, self.start_rating)
        self.orders = []
        self.sold = [deepcopy(book) for book in self.stock.book_list]
        for book in self.sold: book.copies_num = 0
        self.applications = []
        self.income = 0

    def try_to_execute_orders(self, day: int) -> List[PublishingOrder]:
        """ Функция, пытающаяся выполнить все возможные заказы из списка текущих заказов, возвращает список новых заявок в издательство """
        applic_before = len(self.applications)

        for order in filter(lambda o: not o.status.is_done(), self.orders):
            need_order_copies, was_need_copies = 0, 0
            for book in filter(lambda b: b.copies_num != 0, order.book_list):

                find_book = self.stock.lookup(book)
                need_copies = self.stock.remove(find_book, book.copies_num)

                if need_copies > 0:
                    self.add_application(find_book, need_copies, day)

                self.add_sold(find_book, book.copies_num - need_copies)
    
                need_order_copies += need_copies
                was_need_copies += book.copies_num

                book.copies_num = need_copies

            if need_order_copies == was_need_copies:             # ни одну книгу не выдали, статус не изменяется
                continue
            if order.status.is_recv() and need_order_copies > 0: # часть книг выданы, но остались те, которые еще нужно выдать
                order.status = next(order.status)
            elif need_order_copies == 0:                         # полностью выполнен заказ, все книги выданы
                order.status = next(next(order.status))

            order.books_num = order.get_books_num() 

        for book, copies in self.stock.check_min_copies():
            self.add_application(book, copies, day)


        sum_sold = sum(map(lambda b: b.copies_num, self.sold))
        for book in self.sold:
            book.recalculate_rating(book.copies_num, sum_sold)

        for book in self.stock.book_list:
            book.recalculate_price(day)

        return self.applications[applic_before:]


    def add_application(self, book: Book, copies: int, day: int):
        """ Функция добавления книги в список заявок на издательство по имени изда-ва """
        need_book = Book(name=book.name, author=book.author, copies_num=copies)
        application = PublishingOrder(day, book.publishing, [need_book])
        # если уже есть заявка в это же издательство в этот день, добавляем книгу к списку этой заявки
        if application in self.applications:
            ind = self.applications.index(application)
            application = self.applications[ind]
            # если такая книга уже есть в списке книг заявки, то увеличиваем кол-во ее копий на необходимое число
            if book in application.book_list:
                ind = application.book_list.index(book)
                need_book = application.book_list[ind]
                need_book.copies_num += copies
            else:
                application.book_list.append(need_book)
        else:
            self.applications.append(application)
        
        application.books_num += copies


    def add_sold(self, book: Book, copies_num: int):
        """ Функция добавления книги в список проданных книг """
        ind = self.sold.index(book)
        self.sold[ind].copies_num += copies_num
        self.income += book.price * copies_num


    def get_arrived_books_from_publishing(self):
        """ Функция, пополняющая склад книгами, прибывших из издательства"""
        for application in filter(lambda a: a.books_num != 0, self.applications):
            if application.status.is_done():
                self.stock.add(application.book_list)
                application.books_num = 0


    def top_sold(self, groupby : str = "book"):
        """ Вспомогательная функция для подсчета статистики среди проданных книг """
        if groupby == "book":
            top_list = sorted(self.sold, key=lambda b: b.copies_num, reverse=True) [:3]
            top_list = {book.get_name() : ', '.join(map(str, [book.rating, book.copies_num])) for book in top_list}

        elif groupby == "author":
            top_list = {}
            authors = set(map(lambda b: b.author, self.sold))
            for author in authors:
                sum_copies = sum(map(lambda b: b.copies_num, filter(lambda b: b.author == author, self.sold)))
                top_list[author] = sum_copies
            top_list = dict(sorted(top_list.items(), key=lambda t: t[1], reverse=True) [:3])

        elif groupby == "category":
            top_list = {}
            categories = set(map(lambda b: b.category, self.sold))
            for category in categories:
                sum_copies = sum(map(lambda b: b.copies_num, filter(lambda b: b.category == category, self.sold)))
                top_list[category.value] = sum_copies
            top_list = dict(sorted(top_list.items(), key=lambda t: t[1], reverse=True) [:3])

        return top_list
