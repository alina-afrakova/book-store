from enum import Enum


class OrderStatus(Enum):
    RECV = 'Поступил'
    PART = 'Частично исполнен'
    DONE = 'Выполнен'

    def __next__(status):
        if status == OrderStatus.RECV:
            return OrderStatus.PART
        elif status == OrderStatus.PART:
            return OrderStatus.DONE
        else: return status

    def is_done(self):
        return self == OrderStatus.DONE

    def is_recv(self):
        return self == OrderStatus.RECV


class Order:
    def __init__(self, day):
        self.day = day
        self.status = OrderStatus.RECV
        self.books_num = 0


class BookOrder(Order):
    def __init__(self, day, *order_args):
        super().__init__(day)
        self.name, self.phone, self.book_list = order_args

    def get_books_num(self):
        return sum(map(lambda b: b.copies_num, self.book_list))


class PublishingOrder(Order):
    def __init__(self, day, *order_args):
        super().__init__(day)
        self.name, self.book_list = order_args

    def __eq__(self, other):
        return self.name == other.name and self.day == other.day
