from collections import UserDict
import re
from datetime import datetime, timedelta
from typing import Tuple, List

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            # return "Give me name and phone please."
            return f"Error: {str(e)}"
        except IndexError:
            # return "Enter the argument for the command."
            return "Error: Missing required arguments."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    return inner

def parse_input(user_input: str) -> Tuple[str, List[str]]:
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
          if not value:
                raise ValueError("Name cannot be empty")
          super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
        # another variant:
        #   if not re.match(r"^\d{10}$", value):
                raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
        if self.is_future_date(parsed_date):
            raise ValueError("Birthday cannot be in the future")
        
        super().__init__(parsed_date)
    
    
    @staticmethod
    def is_future_date(date):
        return date > datetime.today().date()
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        if phone_number in [p.value for p in self.phones]:
            raise ValueError("This phone number is already added.")
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        if phone_number not in [p.value for p in self.phones]:
            raise ValueError("Phone number not found.")
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value
                return "Phone number updated."
        raise ValueError("Phone number not found")

    def find_phone(self, phone_number):
        return next((phone for phone in self.phones if phone.value == phone_number), None)
    
    def get_phones(self):
        return "; ".join(phone.value for phone in self.phones) if self.phones else "No phone numbers"
    
    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday is already set and cannot be changed.")
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Birthday not set"

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Not set"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
         self.data[record.name.value] = record
    
    def find(self, name):
         return self.data.get(name, None)
    
    def delete(self, name):
         if name in self.data:
              del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if today <= birthday_this_year <= next_week:
                    # Find next Monday
                    if birthday_this_year.weekday() in (5, 6):  # Saturday = 5, Sunday = 6
                        days_to_monday = 7 - birthday_this_year.weekday()
                        congratulation_date = birthday_this_year + timedelta(days=days_to_monday)
                    else:
                        congratulation_date = birthday_this_year
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays
    
    def list_all_contacts(self):
        # return {name: record.get_phones() for name, record in self.data.items()}
        if not self.data:
            return "No contacts in the address book."
        return "\n".join(f"{name}: {record.get_phones()}" for name, record in self.data.items())
       
@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Name, old phone, and new phone are required.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return record.edit_phone(old_phone, new_phone)

@input_error
def show_phone(args, book):
    if not args:
        raise ValueError("Name is required.")
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return f"{name}'s phone numbers: {record.get_phones()}"

@input_error
def show_all_contacts(_, book: AddressBook):
    return book.list_all_contacts()

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Name and birthday are required.")
    name, date = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(date)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    if not args:
        raise ValueError("Name is required.")
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return f"{name}'s birthday: {record.show_birthday()}"

@input_error
def birthdays(_, book: AddressBook):
    return book.get_upcoming_birthdays()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all_contacts(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()