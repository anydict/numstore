<h1 align="center">
<img src="https://raw.githubusercontent.com/anydict/numstore/main/logo/numstorelogo.svg" width="300">
</h1><br>

Source code: https://github.com/anydict/numstore

Numstore - fast and easy key-value storage in RAM. It only works with numbers keys and numbers values.

This is an ideal solution if you need to store a small integer value for a huge number of integer keys.
It is high performance.
For example: if you fill the dictionary with 999999999 keys, it will take about 500 megabytes in memory

Limits on use:

- keys can only be positive integer values;
- the values must be in the range from 0 to 15 (None values cannot be used);
- All keys initially have a value of 0 (A value equal to 0 is considered a non-existent value);
- the size of the dictionary is set during initialization and cannot change during operation;

Otherwise, the dictionary has similar functionality to a regular dictionary

Usage
-----

`pip install numstore`

```python 
import numstore

buffer = numstore.Dict(length=6)

buffer[100] = 1
buffer[200] = 2
buffer[300] = 3
del buffer[100]

print('get_method      ', buffer.get(200))
print("check_contains  ", 100 in buffer)
print("check_bool      ", True if buffer else False)
print("len(buffer)     ", len(buffer))
print("buffer.pop(200) ", buffer.pop(200))
print("all keys        ", list(buffer.keys()))
print("all values      ", list(buffer.values()))
print("all items       ", list(buffer.items()))
buffer.clear()
print("len(buffer)     ", len(buffer))

buffer.save("test.pkl")  # save dictionary in file
buffer.load("test.pkl")  # load dictionary from file

# keys and values can be specified as a string
buffer["400"] = "4"

buffer = numstore.Dict(length=3, raise_index_error=False)
# but these strings must contain numbers
buffer["a"] = "1"  # NOT WORKING (key is not number) (show UserWarning in stdout)
buffer["1"] = "a"  # NOT WORKING (value is not number) (show UserWarning in stdout)
buffer["-1"] = 1  # NOT WORKING (negative key) (show UserWarning in stdout)
buffer[1] = -11  # NOT WORKING (not allowed value) (show UserWarning in stdout)
buffer[123456789] = 1  # NOT WORKING (max length=3) (show UserWarning in stdout)

```

Performance
-----------

### One million records

| module   | Speed writes     | Speed random reads | Memory for one million records |
|----------|------------------|--------------------|--------------------------------|
| numstore | 666988 / second  | 962239 / second    | 17 Mb                          |
| numpy    | 5446387 / second | 8103369 / second   | 25 Mb                          |
| dict     | 6604781 / second | 2196775 / second   | 100 Mb                         |
| pysos    | 86963 / second   | 204624 / second    | 972 Mb                         |

### Ten million records

| module   | Speed writes     | Speed random reads | Memory for ten million records |
|----------|------------------|--------------------|--------------------------------|
| numstore | 663046 / second  | 900838 / second    | 104 Mb                         |
| numpy    | 5425987 / second | 6841141 / second   | 809 Mb                         |
| dict     | 5757307 / second | 1680141 / second   | 8600 Mb                        |
| pysos    | 82755 / second   | 206848 / second    | 11700 Mb                       |

F.A.Q.
------

### Is it thread safe?

No. It's not thread safe.
In practice, synchronization mechanisms are typically desired on a higher level anyway.