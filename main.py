from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    def __str__(self):
        return self._value


class Phone(Field):
    @Field.value.setter
    def value(self, new_value):
        if not str(new_value).isdigit() or len(str(new_value)) != 10:
            raise ValueError("Phone number must have 10 digits and contain only numbers.")
        self._value = new_value

    def __str__(self):
        return str(self._value)


class Birthday(Field):
    @Field.value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Incorrect data format, should be DD-MM-YYYY")
        self._value = new_value

    def days_to_next_birthday(self):
        today = datetime.today()
        b_day = datetime.strptime(self._value, "%d-%m-%Y").replace(year=today.year)
        if today > b_day:
            b_day = b_day.replace(year=today.year+1)
        delta = b_day - today
        return delta.days
    

class Record:
    def __init__(self, name: str, birthday: str = None):
        self.name = Name(name)
        self.phones = []
        if birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(str(Phone(phone)))

    def remove_phone(self, phone: str):
        self.phones.remove(str(Phone(phone)))

    def edit_phone(self, old_phone: str, new_phone: str):
        index = self.phones.index(str(Phone(old_phone)))
        self.phones[index] = str(Phone(new_phone))

    def find_phone(self, phone: str):
        for p in self.phones:
            if phone == p:
                return p
        return None
    
    def days_to_birthday(self):
        if self.birthday:
            return self.birthday.days_to_next_birthday()
        else:
            return "Birthday not set."


class AddressBook(UserDict):
    def __init__(self, page_size=5):
        super().__init__()
        self.page_size = page_size

    def __iter__(self):
        return AddressBookIterator(self.data.values(), self.page_size)

    def add_record(self, record: Record):
        self.data[str(record.name.value)] = record

    def find(self, name: str):
        return self.data.get(name, None)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

class AddressBookIterator:
    def __init__(self, records, page_size):
        self.records = list(records)
        self.page_size = page_size
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.records):
            raise StopIteration

        records_slice = self.records[self.index:self.index+self.page_size]
        self.index += self.page_size
        return records_slice

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Wrong user name"
        except ValueError as ve:
            return str(ve)
        except IndexError:
            return "Give me name and phone please"
    return inner

@input_error
def hello(*args):
    return "How can I help you?"


@input_error
def add(address_book: AddressBook, name, phone, birthday=None):
    name_obj = Name(name)
    phone_obj = Phone(phone)
    record = address_book.find(name)
    
    if record:
        record.add_phone(phone_obj)
        if birthday:
            record.birthday = Birthday(birthday)
    else:
        new_record = Record(name_obj, birthday)
        new_record.add_phone(phone_obj)
        address_book.add_record(new_record)

    return "Contact added!"


@input_error
def change(address_book: AddressBook, name, old_phone, new_phone):
    old_phone_obj = Phone(old_phone)
    new_phone_obj = Phone(new_phone)
    record = address_book.find(name)
    
    if not record:
        raise KeyError
    print (record.phones)
    if str(old_phone_obj) not in record.phones:
        raise ValueError("Old phone number not found!")

    record.edit_phone(old_phone_obj, new_phone_obj)
    return "Phone number changed!"


@input_error
def phone(address_book: AddressBook, name: str):
    record = address_book.find(name)
    
    if not record:
        raise KeyError

    return ", ".join([str(phone) for phone in record.phones])


@input_error
def remove_phone(address_book: AddressBook, name, phone):
    phone_obj = Phone(phone)
    record = address_book.find(name)
    
    if not record:
        raise KeyError

    if phone_obj not in record.phones:
        raise ValueError("Phone number not found!")

    record.remove_phone(phone_obj)
    return "Phone number removed!"


@input_error
def show_all(address_book: AddressBook, page_size=None):
    if page_size:
        address_book.page_size = int(page_size)
    
    pages = []
    for page in address_book:
        page_output = "\n".join([f"{str(record.name.value)}: {', '.join([str(phone) for phone in record.phones])}" for record in page])
        pages.append(page_output)
    return "\n----\n".join(pages)

@input_error
def delete_record(address_book: AddressBook, name):
    if not address_book.find(name):
        raise KeyError("Record not found!")

    address_book.delete(name)
    return f"Record for {name} deleted!"


def good_bye(data):
    return 'Good bye!'


@input_error
def days_to_birthday(address_book: AddressBook, name):
    record = address_book.find(name)
    
    if not record:
        raise KeyError
    
    if not record.birthday:
        return "Birthday not set for this contact."

    return f"Days to next birthday: {record.birthday.days_to_next_birthday()}"


def parse_command(full_command):
    split_command = full_command.split(' ', 1)
    primary_command = split_command[0]
    data = split_command[1] if len(split_command) > 1 else ""

    function_to_execute = None
    for func, cmds in COMMANDS.items():
        if primary_command in cmds:
            function_to_execute = func
            break

    # Перевіряємо, чи може команда бути двослівною
    if not function_to_execute:
        potential_two_word_command = full_command.split(' ', 2)
        if len(potential_two_word_command) > 1:
            two_word_command = " ".join(potential_two_word_command[:2])
            for func, cmds in COMMANDS.items():
                if two_word_command in cmds:
                    function_to_execute = func
                    data = potential_two_word_command[2] if len(potential_two_word_command) > 2 else ""
                    break

    return function_to_execute, data


COMMANDS = {
    hello: ['hello'],
    add: ['add'],
    change: ['change'],
    remove_phone: ['remove'],
    delete_record: ['delete'],
    phone: ['phone'],
    show_all: ['show all'],
    days_to_birthday: ['birthday'],
    good_bye: ['good bye', 'close', 'exit']
}


@input_error
def main():
    address_book = AddressBook()

    while True:
        command = input("Enter command: ").lower()

        command_name, data = parse_command(command)

        func = command_name

        if not func:
            print("Command not found!")
            continue

        print(func(address_book, *data.split()))

        if command_name == good_bye:
            
            break

if __name__ == "__main__":
    main()

