# Система контроля ассортимента книжного магазина

### Файловая структура системы
* **`Book.py`** — описание и реализация класса _`Воок`_, а также перечислимых классов _`ThemeLabel`_ и _`CategoryLabel`_

* **`Order.py`** — описание и реализация классов _`Order`_, _`BookOrder`_ и _`PublishingOrder`_, а также перечислимого класса OrderStatus

* **`BookShop.py`** — описание и реализация классов _`Stock`_ и _`BookShop`_

* **`System.py`** — описание и реализация классов _`Randomizer`_ и _`System`_, а также функции начального экрана с заданием параметров _`get_start_parameters`_

* **`main.py`** — запуск функции _get_start_parameters_, и передача полученных параметров в инициализацию системы _System_, запуск системы

* **`books.csv`** — файл с начальным ассортиментом магазина - списком книг с их параметрами

* **`customers.txt`** — файл с фамилиями потенциальных покупателей

---
### Запуск программы:  
`python3 main.py`
