import System


if __name__ == '__main__':
    parameters = System.get_start_parameters()
    if parameters:
        bookshop = System.System(*parameters)
        bookshop.start_system()
