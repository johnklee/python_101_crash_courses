from datetime import datetime


UNKNOWN_EMPLOYEE = ('?', '?', 0, datetime.now(), '?')

employee_info_dict = {
    # UID: (Name, Job, Salary, On board date)
    1: ('John', 'Developer', 12345, datetime.strptime('2023-03-01', '%Y-%m-%d'), 'address1'),
    2: ('Mary', 'Manager', 45000, datetime.strptime('2022-01-12', '%Y-%m-%d'), 'address2'),
    3: ('Ken', 'CEO', 999999, datetime.strptime('2021-06-06', '%Y-%m-%d'), 'address3'),
}

def get_employee(uid: int) -> tuple[str, str, int, datetime]:
    return  employee_info_dict.get(uid, UNKNOWN_EMPLOYEE)
