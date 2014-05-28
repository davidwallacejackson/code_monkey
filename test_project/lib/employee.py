'''Classes and helper functions for managing Employees'''
from test_project import settings

class Employee(object):

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.pay_rate = settings.BASE_PAY

    def full_name(self):
        return self.first_name + ' ' + self.last_name


class CodeMonkey(Employee):
    """He writes code."""
    def __init__(self, *args, **kwargs):
        super(CodeMonkey, self).__init__(*args, **kwargs)
        self.is_up = False
        self.can_work = False

    things_code_monkey_like = [
        'fritos',
        'tab',
        'mountain_dew',
        'you']

    def get_up(self):
        self.is_up = True

    def get_coffee(self):
        self.can_work = True

    def write_goddamned_login_page(self):
        print("...done.")
