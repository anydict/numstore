"""
Numstore - fast and easy key-value storage in RAM. It only works with numbers keys and numbers values.

This is an ideal solution if you need to store a small integer value for a huge number of integer keys.
It is high performance.
For example: if you fill the dictionary with 999999999 keys, it will take about 500 megabytes in memory


Limits on use:
- keys can only be positive integer values;
- the values must be in the range from 0 to 15 (None values cannot be used);
- All keys initially have a value of 0 (A value equal to 0 is considered a non-existent value);
- the size of the dictionary is set during initialization and cannot change during operation;

Otherwise, the dictionary has similar functionality to a regular dictionary:

import numstore

buffer = Dict(length=6)

buffer[100] = 1
buffer[200] = 2
buffer[300] = 3
del buffer[100]

print("get by index    ", buffer[200])
print("get method      ", buffer.get(300))
print("check contains  ", 100 in buffer)
print("check bool      ", True if buffer else False)
print("len(buffer)     ", len(buffer))
print("buffer.pop(200) ", buffer.pop(200))
print("all keys        ", list(buffer.keys()))
print("all values      ", list(buffer.values()))
print("all items       ", list(buffer.items()))
print("clear           ", buffer.clear())
print("len(buffer)     ", len(buffer))

buffer.save("test.pkl")  # save dictionary in file
buffer.load("test.pkl")  # load dictionary from file

# keys and values can be specified as a string (but these strings must contain numbers)
buffer["400"] = "4"

# # Examples of misuse
# buffer = Dict(length=3, raise_index_error=False)
# buffer["a"] = "1"  # NOT WORKING (key is not number) (show UserWarning in stdout)
# buffer["1"] = "a"  # NOT WORKING (value is not number) (show UserWarning in stdout)
# buffer["-1"] = 1  # NOT WORKING (negative key) (show UserWarning in stdout)
# buffer[1] = -11  # NOT WORKING (not allowed value) (show UserWarning in stdout)
# buffer[123456789] = 1  # NOT WORKING (max length=3) (show UserWarning in stdout)

"""

import os
import pickle
import warnings
from collections.abc import Iterator


class Dict(object):
    def __init__(self, length: int = 9, raise_index_error: bool = True, skip_key_validation: bool = False):
        """
        Method for setting dictionary parameters

        :param length: maximum dictionary length (example: set 4 if your keys from 0 to 9999)
        :param raise_index_error: to raise or not to raise an exception in case of exceeding the key values
        :param skip_key_validation: skip key validation (faster, but not safe)
        """
        self.length: int = length
        self.raise_index_error: bool = raise_index_error
        self.skip_key_validation: bool = skip_key_validation
        self.__len_value = 2  # the higher the number, the less memory is required, but the speed drops
        self.end_range: int = int("1" + "0" * (length - self.__len_value))
        self.buffer: list[int] = [0 for _ in range(0, self.end_range)]
        self.__allows_value: list[str] = [str(x) for x in range(0, 16)]

    @staticmethod
    def replace_str_index(text, index=0, replacement="") -> str:
        """
        A useful method for replacing a character at a specified position with another text

        :param text: the text in which we want to replace the character
        :param index: the position of the symbol to replace
        :param replacement: replacement text
        :return: new text after replacement
        """
        return f"{text[:index]}{replacement}{text[index + 1:]}"

    def checking_key(self, key: str | int) -> bool:
        """
        Checking the key for validity

        :param key: the key being checked
        :return: bool - successfully/unsuccessfully
        """
        if self.skip_key_validation:
            return True

        try:
            key = str(int(key))
            if len(key) > self.length and self.raise_index_error is True:
                raise IndexError(f"index={key} out of range")
            elif len(key) > self.length and self.raise_index_error is False:
                warnings.warn(f"index={key} out of range")
                return False
        except (ValueError, TypeError):
            warnings.warn(f"key={key} has invalid type or value")
            return False

    def get_positions(self, key: str) -> tuple[int, int]:
        """
        Get buffer and hex positions by key

        :param key: key
        :return: tuple[buffer_position, hex_position]
        """

        buffer_position = int(key[0:-self.__len_value] or "0")
        hex_position = int(key[-self.__len_value:])

        return buffer_position, hex_position

    def __getitem__(self, key: int | str) -> int:
        """
        Get the value from the dictionary by key

        :param key: the key for the search
        :return: the value from the dictionary obtained by the key
        """

        if self.checking_key(key) is False:
            return 0

        key = str(key)
        buffer_position, hex_position = self.get_positions(key=key)

        hex_sequence = hex(self.buffer[buffer_position])[2:].zfill(int("1" + "0" * self.__len_value))

        return int(hex_sequence[hex_position], 16)

    def __setitem__(self, key: int | str, value: int | str) -> None:
        """
        Set the value in the dictionary by key

        :param key: key to set
        :param value: value to set
        :return: None
        """

        if self.checking_key(key) is False:
            return

        if str(value) not in self.__allows_value:
            warnings.warn(f"value={value} with type={type(value)} has invalid type or value")
            return

        key = str(key)
        hex_value = hex(int(value))[2:]
        buffer_position, hex_position = self.get_positions(key=key)

        hex_sequence = hex(self.buffer[buffer_position])[2:].zfill(int("1" + "0" * self.__len_value))

        new_hex_sequence = self.replace_str_index(hex_sequence, hex_position, hex_value)
        self.buffer[buffer_position] = int(new_hex_sequence, 16)

    def __delitem__(self, key: int | str) -> None:
        """
        Delete a value in the dictionary by the specified key

        :param key: the key to find the value
        :return: None
        """

        if self.checking_key(key) is False:
            return

        self.__setitem__(key=key, value=0)

    def __len__(self) -> int:
        """
        Get the number of non-zero values

        :return: number of non-zero values
        """

        counter = 0
        for buffer_value in self.buffer:
            if buffer_value == 0:
                continue
            hex_sequence = hex(buffer_value)[2:]
            counter += len(hex_sequence) - hex_sequence.count("0")

        return counter

    def __bool__(self) -> bool:
        """
        Check for at least one non-zero value

        :return: bool - exist or not exist at least one non-zero value
        """

        return bool(len(self))

    def __contains__(self, key: str | int) -> bool:
        """
        Is there a non-zero value for the specified key

        :param key: the key to find the value
        :return: bool - exist or not exist non-zero value by key
        """

        if self.checking_key(key) is False:
            return False

        return self[key] > 0

    def pop(self, key) -> int:
        """
        Delete and return the value by key

        :param key: the key to find the value
        :return: the found value for the specified key
        """

        if self.checking_key(key) is False:
            return 0

        value = self[key]
        del self[key]

        return value

    def get(self, key) -> int:
        """
        return the value by key

        :param key: the key to find the value
        :return: the found value for the specified key
        """

        if self.checking_key(key) is False:
            return 0

        return self[key]

    def clear(self) -> None:
        """
        Clear the entire dictionary

        :return: None
        """

        self.buffer: list[int] = [0 for _ in range(0, self.end_range)]

    def keys(self) -> Iterator[int]:
        """
        Generator for get keys for which there is a non-zero value in the dictionary

        :return: Iterator[int] - key with non-zero value in the dictionary
        """

        buffer_position = -1
        for buffer_value in self.buffer:
            buffer_position += 1
            if buffer_value == 0:
                continue
            hex_sequence = hex(buffer_value)[2:].zfill(int("1" + "0" * self.__len_value))
            for hex_position, char in enumerate(hex_sequence):
                if char != "0":
                    last_part_key = str(hex_position).zfill(self.__len_value)
                    first_part_key = str(buffer_position).zfill(self.length - len(last_part_key))
                    yield int(first_part_key + last_part_key)

    def values(self) -> Iterator[int]:
        """
        Generator for get keys for which there is a non-zero value in the dictionary

        :return: Iterator[int] - key with non-zero value in the dictionary
        """

        for key in self.keys():
            yield self[key]

    def items(self) -> Iterator[int, int]:
        """
        Generator for get keys and values for which there is a non-zero value in the dictionary

        :return: Iterator[int, int] - key and value with non-zero value in the dictionary
        """

        for key in self.keys():
            yield key, self[key]

    def save(self, path: str = "dump.pkl") -> bool:
        """
        Save a copy of the dictionary to a file

        :param path: the path to save
        :return: bool - successfully/unsuccessfully
        """

        try:
            with open(f"{path}.new", "wb") as f:
                pickle.dump(self.buffer, f)
            os.replace(f"{path}.new", f"{path}")
            return True
        except Exception as e:
            warnings.warn(f"something went wrong: {type(e)} => {e}")
            return False

    def load(self, path: str = "dump.pkl", fix_incorrect_length: bool = False) -> bool:
        """
        Load a dictionary from a file into memory

        :param path: the path to load
        :param fix_incorrect_length: fix incorrect dictionary length in memory if it differs from the length in the file
        :return: bool - successfully/unsuccessfully
        """

        try:
            with open(path, "rb") as f:
                new_buffer: list = pickle.load(f)
                range_buffer = len(new_buffer)
                range_value = int("1" + "0" * self.__len_value)
                length = len(str(range_buffer - 1) + str(range_value - 1))

                if length != self.length and fix_incorrect_length is False:
                    warnings.warn(f"different lengths: in file {length}, and in current object {self.length}")
                    return False
                elif length != self.length and fix_incorrect_length is True:
                    self.length: int = length
                    self.end_range: int = int("1" + "0" * (length - self.__len_value))
                self.buffer = new_buffer
            return True
        except Exception as e:
            warnings.warn(f"something went wrong: {type(e)} => {e}")
            return False


if __name__ == "__main__":
    # Simple examples:
    buffer = Dict(length=6)

    buffer[100] = 1
    buffer[200] = 2
    buffer[300] = 3
    del buffer[100]

    print("get by index    ", buffer[200])
    print("get method      ", buffer.get(300))
    print("check contains  ", 100 in buffer)
    print("check bool      ", True if buffer else False)
    print("len(buffer)     ", len(buffer))
    print("buffer.pop(200) ", buffer.pop(200))
    print("all keys        ", list(buffer.keys()))
    print("all values      ", list(buffer.values()))
    print("all items       ", list(buffer.items()))
    print("clear           ", buffer.clear())
    print("len(buffer)     ", len(buffer))

    buffer.save("test.pkl")  # save dictionary in file
    buffer.load("test.pkl")  # load dictionary from file

    # keys and values can be specified as a string (but these strings must contain numbers)
    buffer["400"] = "4"

    # # Examples of misuse
    # buffer = Dict(length=3, raise_index_error=False)
    # buffer["a"] = "1"  # NOT WORKING (key is not number) (show UserWarning in stdout)
    # buffer["1"] = "a"  # NOT WORKING (value is not number) (show UserWarning in stdout)
    # buffer["-1"] = 1  # NOT WORKING (negative key) (show UserWarning in stdout)
    # buffer[1] = -11  # NOT WORKING (not allowed value) (show UserWarning in stdout)
    # buffer[123456789] = 1  # NOT WORKING (max length=3) (show UserWarning in stdout)
