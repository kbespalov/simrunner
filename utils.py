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
        print colors.WARNING + ' -- ' + item + colors.ENDC
