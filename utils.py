class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_list(title, items):
    print colors.HEADER + title + colors.ENDC
    for item in items:
        print colors.WARNING + ' -- ' + str(item) + colors.ENDC


def remove_double_spaces(string):
    # remove unnecessary spaces
    while True:
        tmp = string.replace("  ", " ")
        if string == tmp:
            break
        string = tmp


def retry(attempts, on_error):
    def decorator(func):
        def wrapper(*args, **kwargs):
            while attempts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    on_error(e)

        return wrapper

    return decorator
