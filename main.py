from collections import UserDict
from datetime import date, datetime
import string
import json


class NameTooShortError(Exception):
    pass


class NameStartsFromLowError(Exception):
    pass


class AddressBook(UserDict):
    def __init__(self, n=1):
        super().__init__()
        self.n = n

    def add_record(self, record) -> None:
        self.data[record.name.value] = record

    def iterator(self, n):
        address_book_str = ""
        i = 1
        for v in self.data.values():
            phones_str = ""
            for el in v.phones:
                phones_str += el.value + ", "
            phones_str = phones_str.strip().removesuffix(",")
            address_book_str += (
                f"name: {v.name.value}, birthday: {v.birthday.value}, phones: {phones_str}"
                + "\n"
            )
            if i >= n:
                yield address_book_str.removesuffix("\n")
                address_book_str = ""
                i = 0
            i += 1

    def save_to_disk(self, filename):
        adress_book = {}
        for k, v in self.items():
            phones = []
            for phone in v.phones:
                phones.append(phone.value)
            adress_book[k] = {
                "name": v.name.value,
                "birthday": v.birthday.value.strftime("%d-%m-%Y"),
                "phones": phones,
            }

        with open(filename, "w") as fh:
            json.dump(adress_book, fh)

    def load_from_disk(self, filename):
        with open(filename, "r") as fh:
            adress_book = json.load(fh)

        for k, v in adress_book.items():
            record = Record(
                Name(v["name"]), Phone(v["phones"][0]), Birthday(v["birthday"])
            )
            if len(v["phones"]) > 1:
                for phone in v["phones"][1:]:
                    record.add(phone)
            self.add_record(record)


class Record:
    def __init__(self, name, phone=None, birthday=None) -> None:
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add(self, phone) -> None:
        self.phones.append(phone)

    def delete(self, phone) -> None:
        self.phones.remove(phone)

    def edit(self, old_phone, new_phone):
        for ph in self.phones:
            if ph.value == old_phone:
                ph.value = new_phone

    def days_to_birthday(self) -> date:
        if not birthday_in_this_year:
            return None

        birthday_in_this_year = date(
            year=date.today().year, month=self.birthday.mounth, day=self.birthday.day
        )
        birthday_in_next_year = date(
            year=date.today().year + 1,
            month=self.birthday.mounth,
            day=self.birthday.day,
        )
        today = date.today()
        return (
            birthday_in_this_year - today
            if birthday_in_this_year - today > 0
            else birthday_in_next_year - today
        )


class Field:
    def __init__(self) -> None:
        self.__value = None


class Name(Field):
    def __init__(self, name) -> None:
        super().__init__()
        self.value = name

    @property
    def value(self) -> object:
        return self.__value

    @value.setter
    def value(self, new_value) -> None:
        try:
            if len(new_value) < 3:
                raise NameTooShortError
            if new_value[0] not in string.ascii_uppercase:
                raise NameStartsFromLowError

            self.__value = new_value
        except NameTooShortError:
            print("Name is too short, need more than 3 symbols. Try again.")
        except NameStartsFromLowError:
            print("Name should start from capital letter. Try again.")


class Phone(Field):
    def __init__(self, phone) -> None:
        super().__init__()
        self.value = phone

    @property
    def value(self) -> object:
        return self.__value

    @value.setter
    def value(self, new_value) -> None:
        phone_valid = True

        for i in new_value:
            if (i < "0" or i > "9") and i != "+":
                print("Phone not valid")
                phone_valid = False
                break

        if phone_valid:
            new_phone = (
                new_value.strip()
                .removeprefix("+")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(" ", "")
            )

            if len(new_phone) == 12:
                format_phone = "+" + new_phone
            else:
                format_phone = "+38" + new_phone

            self.__value = format_phone


class Birthday(Field):
    def __init__(self, birthday) -> None:
        super().__init__()
        self.value = birthday

    @property
    def value(self) -> object:
        return self.__value

    @value.setter
    def value(self, new_value) -> None:
        try:
            birthday = datetime.strptime(new_value, "%d-%m-%Y").date()
            self.__value = birthday
        except ValueError:
            print("Not correct date format. Use next format dd-mm-yyyy.")


if __name__ == "__main__":
    name1 = Name("Bill")
    phone1 = Phone("1234567890")
    birthday1 = Birthday("01-01-1991")
    rec1 = Record(name1, phone1, birthday1)

    name2 = Name("Tom")
    phone2 = Phone("0987654321")
    birthday2 = Birthday("02-02-1992")
    rec2 = Record(name2, phone2, birthday2)

    ab = AddressBook()
    ab.add_record(rec1)
    ab.add_record(rec2)
    ab.save_to_disk("adress_book.txt")
    # ab.load_from_disk("adress_book.txt")

    # assert isinstance(ab["Bill"], Record)
    # assert isinstance(ab["Bill"].name, Name)
    # assert isinstance(ab["Bill"].phones, list)
    # assert isinstance(ab["Bill"].phones[0], Phone)
    # assert isinstance(ab["Bill"].birthday, Birthday)
    # assert ab["Bill"].phones[0].value == "1234567890"

    for i in ab.iterator(1):
        print(i)

    print("All Ok)")
