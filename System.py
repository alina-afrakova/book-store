import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

from typing import List
from Book import Book
from Order import BookOrder
from BookShop import BookShop


def get_start_parameters():

    def check_file(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as in_file:
                return None
        except Exception as Exc:
            return Exc

    def collect_params():
        nonlocal entry, params, status

        for i, entr in enumerate(entry):
            params[i] = entr.get()
            if i < 3: params[i] = int(params[i])
            else:
                error = check_file(params[i]) 
                if error:
                    messagebox.showinfo('Error', f"Ошибка при открытии файла: {error}")
                    break
        else:
            status = True
            window.destroy()

    def set_default():
        nonlocal entry

        default = [10, 1, 5, "books.csv"]
        for i, param in enumerate(default):
            entry[i].delete(0, tk.END)
            entry[i].insert(0, param)


    window = tk.Tk()
    window.title("Book shop parameters")
    window['bg'] = '#e8e1ca'

    frame = tk.Frame(relief=tk.SUNKEN, borderwidth=3, bg='#e8e1ca')
    frame.pack()

    labels = ["Кол-во дней моделирования:", "Шаг моделирования:",
              "Диапазон кол-ва заказов в один день:", "Имя csv-файла с начальным ассортиментом:"]
    
    params = [None] * len(labels)
    entry = [None] * len(labels)
    status = False

    for i, text in enumerate(labels):
        label = tk.Label(master=frame, text=text, 
                         bg='#e8e1ca', font="calibri 10")
        if i < 3: 
            from_ = 1 if i > 0 else 10
            to = 10 if i > 0 else 30
            entry[i] = tk.Spinbox(master=frame, from_=from_, to=to, width=20, font="calibri 12")
        else:     
            entry[i] = tk.Entry(master=frame, width=21, font="calibri 12")

        label.grid(row=i, column=0, sticky="w")
        entry[i].grid(row=i, column=1)

    frame_buttons = tk.Frame(bg='#e8e1ca')
    frame_buttons.pack(fill=tk.X, ipadx=5, ipady=5)

    btn_submit = tk.Button(master=frame_buttons, text="OK", command=collect_params,
                            bg="#a7bdd1", activebackground="#6d98bf", font="calibri 10")
    btn_default = tk.Button(master=frame_buttons, text="По умолчанию", command=set_default,
                            bg="#a7bdd1", activebackground="#6d98bf", font="calibri 10")
    btn_submit.pack(side=tk.RIGHT, padx=10, ipadx=10)
    btn_default.pack(side=tk.RIGHT, ipadx=10)

    window.mainloop()
    if status: return params
    else:      return None
    


class Randomizer:
    publishing_days = range(1, 6) # диапазон кол-ва дней, в течении которого выполняется заявка в издательство
    #orders_num = range(1, 6)     # диапазон кол-ва заказов, которое может поступить в один день
    books_num = range(1, 5)       # диапазон кол-ва заказываемых книг одним заазчиком
    books_copies = range(1, 4)    # диапазон кол-ва копий при заказе конкретной книги

    def __init__(self, book_list: List[Book], orders_num: range, seed=1):
        random.seed(seed)
        self.book_list = book_list
        self.orders_num = orders_num
        with open("customers.txt") as names_file:
            self.customers = [name.strip() for name in names_file.readlines()]

    def generate_book_orders(self, day: int) -> List[BookOrder]:
        """ Функция генерации списка заказов на книги """
        orders = []
        for k in range(random.choice(self.orders_num)):
            books_num = random.choice(self.books_num)
            books_indexes = random.sample(range(len(self.book_list)), books_num)
            book_list = [None] * books_num
            for i, j in enumerate(books_indexes):
                book_list[i] = Book()
                book_list[i].copies_num = random.choice(self.books_copies)
                is_None = random.choices([0, 1, 2], [0.6, 0.2, 0.2]) [0]
                if is_None == 0:
                    book_list[i].name = self.book_list[j].name
                elif is_None == 1:
                    book_list[i].author = self.book_list[j].author
                else:
                    book_list[i].name = self.book_list[j].name
                    book_list[i].author = self.book_list[j].author

            customer = random.choice(self.customers)
            phone = '+79' + ''.join(random.choices([str(i) for i in range(10)], k=9))
            orders.append(BookOrder(day, customer, phone, book_list))
            orders[k].books_num = orders[k].get_books_num() 
        return orders


class System:
    def __init__(self, period: int, step: int, orders_num: int, file_name: str):
        self.system_period = period # период моделирования работы
        self.system_step = step     # шаг моделирования
        self.current_day = 0        # текущий день моделирования

        self.book_file = file_name  # имя csv-файла с начальным списком книг
        self.book_shop = BookShop(self.book_file)
        self.randomizer = Randomizer(self.book_shop.stock.book_list, range(1, orders_num + 1))
        self.statistics = {}        # подсчитанная статистика по магазину
        self.button_flag = True


    def start_system(self):
        """ Функция запуска книжного магазина, отрисовка начальных параметров """
        # ОКНО ПРИЛОЖЕНИЯ
        window = tk.Tk()
        window.title("Система контроля ассортимента книжного магазина")
        window.geometry("1100x690")
        window.resizable(width=False, height=False)
        window['bg'] = '#e8e1ca'
        self.window = window

        # КНИЖНЫЙ АССОРТИМЕНТ
        frame_1 = tk.Frame(window)
        frame_1.grid(row=0, column=0, padx=10, pady=20, sticky="nsew") 

        title = tk.Label(frame_1, text='Ассортимент магазина', bg='#ccc7b6', font=('Calibri', 10, 'bold'))
        title.grid(row=0, column=0, sticky="nwes")
        frame_books = tk.Frame(frame_1)
        frame_books.grid(row=1, column=0, sticky="s")

        book_scroll = tk.Scrollbar(frame_books)
        book_scroll.pack(side=tk.RIGHT, fill=tk.Y) # vertical scrollbar

        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 9)) # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 10)) # Modify the font of the headings
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders

        book_table = ttk.Treeview(frame_books, yscrollcommand=book_scroll.set, style="mystyle.Treeview", height=7)
        book_scroll.config(command=book_table.yview)
        book_table.pack()

        book_table['columns'] = self.book_shop.stock.headers + ["Цена", "Кол-во"]

        book_table.column("#0", width=0, stretch=tk.NO)
        for i, column in enumerate(book_table['columns']):
            if i == 0: w = 200
            elif i < 7: w = 120
            else: w = 70
            book_table.column(column, anchor="w", width=w)

        book_table.heading("#0", text="", anchor=tk.CENTER)
        for column in book_table['columns']:
            book_table.heading(column, text=column, anchor=tk.CENTER)

        self.book_table = book_table
        self.fill_book_table()


        # ЗАКАЗЫ НА КНИГИ И ЗАЯВКИ В ИЗДАТЕЛЬСТВО
        frame_2 = tk.Frame(window, bg='#e8e1ca')
        frame_2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew") 

        for k, text_title in enumerate(["Заказы на книги", "Заявки в издательства"]):
            frame_22 = tk.Frame(frame_2)
            frame_22.grid(row=0, column=k, padx=10, sticky="w" if k==0 else "e")

            title = tk.Label(frame_22, text=text_title, bg='#ccc7b6', font=('Calibri', 10, 'bold'))
            title.grid(row=0, column=0, sticky="nwes")
            frame_order = tk.Frame(frame_22)
            frame_order.grid(row=1, column=0, sticky="s") 

            scroll = tk.Scrollbar(frame_order)
            scroll.pack(side=tk.RIGHT, fill=tk.Y) 

            order_table = ttk.Treeview(frame_order, yscrollcommand=scroll.set, style="mystyle.Treeview", height=7)
            scroll.config(command=order_table.yview)
            order_table.pack()

            if k == 0: order_table['columns'] = ["Заказчик", "Книги", "Кол-во", "Статус", "День"]
            else: order_table['columns'] = ["Издательство", "Книги", "Кол-во", "Статус", "День"]

            order_table.column("#0", width=0, stretch=tk.NO)
            for i, column in enumerate(order_table['columns']):
                w = 70 if i >= 2 else 110
                w = 180 if i == 1 else w
                order_table.column(column, anchor="w", width=w)

            order_table.heading("#0", text="", anchor=tk.CENTER)
            for column in order_table['columns']:
                order_table.heading(column, text=column, anchor=tk.CENTER)


            if k == 0: self.order_table = order_table
            else: self.applic_table = order_table
             

        # СТАТИСТИКА И КНОПКИ
        frame_3 = tk.Frame(window, bg='#e8e1ca') # '#ded7bf')
        frame_3.grid(row=2, column=0, padx=10, pady=1, sticky="nsew")

        frame_stats = tk.Frame(frame_3, bg='snow3')
        frame_stats.grid(row=0, columnspan=3, padx=10, pady=10, sticky="w")

        title = tk.Label(frame_stats, text='Статистика магазина', bg='#ccc7b6', font=('Calibri', 10, 'bold'))
        title.grid(row=0, column=0, sticky="nwes")
        text_frame = tk.Frame(frame_stats)
        text_frame.grid(row=1, column=0, sticky="s")

        text_box = tk.Text(text_frame, height=10, wrap='word', font='calibri 12')
        text_box.pack(side=tk.LEFT, expand=True)

        scroll = tk.Scrollbar(text_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.BOTH) 
        text_box.config(yscrollcommand=scroll.set)
        scroll.config(command=text_box.yview)

        self.text_box = text_box

        self.show_statistics()

        frame_buttons = tk.Frame(frame_3, bg='#ded7bf', bd=5)
        frame_buttons.grid(row=0, column=3, padx=10, pady=60, sticky="e")

        buttons = [None] * 3
        button_text = ["Следующий день", "Завершить", "Начать сначала"]
        button_command = [self.make_step, self.make_all_steps, self.restart]
        for i in range(3): 
            buttons[i] = tk.Button(frame_buttons, text=button_text[i], background="#a7bdd1", foreground="black",
                                    activebackground="#6d98bf", justify="center", padx="5", pady="5", font="calibri 12",
                                    width=16, command=button_command[i])
            #buttons[i].pack()
            #buttons[i].place(x=5, y=50*i)
            buttons[i].grid(row=i, column=0, padx=5, pady=5, sticky="nsew")
            if i == 0: self.next_button = buttons[i]

        window.mainloop()


    def restart(self):
        self.current_day = 0
        self.book_shop = BookShop(self.book_file)
        self.statistics = {}
        self.show_statistics()

        self.next_button['text'] = "Следующий день"
        self.button_flag = True

        self.book_table.delete(*self.book_table.get_children())
        self.fill_book_table()

        self.order_table.delete(*self.order_table.get_children())
        self.applic_table.delete(*self.applic_table.get_children())


    def make_step(self):
        """ Функция выполнения одного шага: генерации заказов и их выполнения """
        if self.button_flag:
            if self.current_day == self.system_period:
                self.window.destroy()
                return

            self.current_day += self.system_step

            generated_orders = self.randomizer.generate_book_orders(self.current_day)
            prev_odd = len(self.book_shop.orders) % 2 != 0
            self.add_new_orders_to_table(generated_orders, self.order_table, prev_odd)

            self.book_shop.orders.extend(generated_orders)

            self.next_button['text'] = "Выполнить заказы"
            self.button_flag = False

        else:
            self.deal_with_book_orders()
            self.calculate_statistics()

            self.next_button['text'] = "Следующий день"
            self.button_flag = True

        self.show_statistics()

    
    def make_all_steps(self):
        """ Функция выполнения всех шагов """
        if self.current_day == self.system_period:
            self.window.destroy()
            return

        if not self.button_flag: self.make_step()
        for i in range(self.current_day, self.system_period):
            self.make_step()
            self.make_step()


    def deal_with_book_orders(self):
        """ Функция передачи заказов на книги в книжный магазин и обновления состояния системы после (список заказов и заявок) """
        new_applications = self.book_shop.try_to_execute_orders(self.current_day)

        prev_odd = len(self.book_shop.applications) % 2 != 0
        self.add_new_orders_to_table(new_applications, self.applic_table, prev_odd)

        self.check_publishing_applications()
        self.book_shop.get_arrived_books_from_publishing()

        self.change_orders_in_table(self.book_shop.orders[::-1], self.order_table)
        self.change_orders_in_table(self.book_shop.applications[::-1], self.applic_table)
        self.change_book_table()


    def check_publishing_applications(self):
        """ Функция проверки выполненных заявок в издательство, передачи их в книжный магазин для заполнения склада и обновления состояния системы после """
        for application in self.book_shop.applications:
            publishing_days = random.choice(self.randomizer.publishing_days)
            if application.day + publishing_days <= self.current_day:
                application.status = next(next(application.status))


    def add_new_orders_to_table(self, orders, order_table, prev_odd):
        for i, order in enumerate(orders):
            tag = ('even',) if (prev_odd + i) % 2 == 0 else ('odd',)
            id_order = order_table.insert(parent='', index=0, text='', open=False,
                                        values=(order.name, "", order.books_num, order.status.value, order.day), tags=tag)
            for j, book in enumerate(order.book_list):
                tag = ('even',) if (i + j + 1) % 2 == 0 else ('odd',)
                info = order.phone if j == 0 and order.__class__ == BookOrder else ""
                order_table.insert(parent=id_order, index='end', text='',
                                   values=(info, book.get_name(), book.copies_num, "", ""), tags=tag)
            order_table.tag_configure('odd', background='#d5e0eb')
            order_table.tag_configure('even', background='#c8d2db')


    def change_orders_in_table(self, orders, order_table):
        for i, order in enumerate(orders):
            order_to_change = order_table.get_children() [i]
            #print(order_to_change, order_table.item(order_to_change, 'values'))
            if int(order_table.item(order_to_change, 'values') [2]) != 0:
                order_table.item(order_to_change, values=(order.name, "", order.books_num, order.status.value, order.day))
                for j, book in enumerate(order.book_list):
                    book_to_change = order_table.get_children(order_to_change) [j]
                    info = order.phone if j == 0 and order.__class__ == BookOrder else ""
                    order_table.item(book_to_change, values=(info, book.get_name(), book.copies_num, "", ""))


    def fill_book_table(self):
        for i, book in enumerate(self.book_shop.stock.book_list):
            tag = ('even',) if i % 2 == 0 else ('odd',)
            self.book_table.insert(parent='', index='end', iid=i, text='',
                                   values=book.get_args(), tags=tag)
            self.book_table.tag_configure('odd', background='#d5e0eb')
            self.book_table.tag_configure('even', background='#c8d2db')
        

    def change_book_table(self):
        for i, book in enumerate(self.book_shop.stock.book_list):
            book_to_change = self.book_table.get_children() [i]
            self.book_table.item(book_to_change, text='', values=book.get_args())


    def calculate_statistics(self):
        """ Функция подсчета статистики """
        self.statistics["Кол-во проданных различных книг"] = len(list(filter(lambda b: b.copies_num != 0, self.book_shop.sold)))
        self.statistics["Кол-во проданных экземпляров книг"] = sum(map(lambda b: b.copies_num, self.book_shop.sold))
        self.statistics["Кол-во выполненных заказов"] = len(list(filter(lambda o: o.status.is_done(), self.book_shop.orders)))
        self.statistics["Топ самых продаваемых книг"] = self.book_shop.top_sold()
        self.statistics["Топ самых читаемых авторов"] = self.book_shop.top_sold(groupby="author")
        self.statistics["Топ самых популярных категорий"] = self.book_shop.top_sold(groupby="category")
        self.statistics["Прибыль магазина"] = self.book_shop.income


    def show_statistics(self):
        self.text_box.config(state='normal')
        self.text_box.delete(1.0, 'end')
        self.text_box.insert(tk.END, f"День: {self.current_day}\n")
        for i, (key, value) in enumerate(self.statistics.items()):
            if i < 3:
                self.text_box.insert(tk.END, f"{key}: {value} шт.\n")
                if i == 2: self.text_box.insert(tk.END, "\n")
            elif i == 6:
                self.text_box.insert(tk.END, f"{key}: {value} руб.")
            else:
                self.text_box.insert(tk.END, f"{key}:\n" + '\n'.join([f"{i+1}. {k} ({v})" 
                                                for i, (k, v) in enumerate(value.items())]) + '\n\n')
        self.text_box.config(state='disabled')
