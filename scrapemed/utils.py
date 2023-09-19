"""
ScrapeMed's Utility Module
============================

The `utils` module contains various utilities necessary for PMC data parsing and
cleaning, where the utilities are not directly related to text cleaning (`_clean`),
recursive text processing (`_text`), or parsing (`_parse`).

At the moment, the module contains a helper function for cleaning up docstrings,
and a class, basicBiMap, which is a two-way map similar to python's dict class,
used for efficient storage of data reference maps used throughout ScrapeMed.

Note: Data reference maps are used to pull citations, tables, and figures out of
text for parsing elsewhere while retaining placeholders in the original text.

.warnings::
    - :class:`reversedBiMapComparisonWarning` - Warned when comparing
        basicBiMaps which are exactly the same but reversed.
"""

import warnings
from inspect import cleandoc


class reversedBiMapComparisonWarning(Warning):
    """
    Warned when comparing basicBiMaps which are exactly the same but reversed.
    """

    pass


# --------- general helper funcs ---------------
def cleanerdoc(s):
    """
    Wrapper for inspect.cleandoc which also removes newlines.

    :param str s: The string to clean and remove newlines from.

    :return: The cleaned and newline-removed string.
    :rtype: str
    """
    return cleandoc(s).replace("\n", "")


# --------- end general helper funcs


class basicBiMap(dict):
    """
    BiMap class which extends Python's dict class to also store
    a reverse of itself for efficiency.

    This class allows for bidirectional mapping between keys and values.
    When a key-value pair is added, it can be accessed both by key and by value.

    Methods are inherited from the dict class, and additional methods
    specific to bidirectional mapping are provided.

    :param *args: Positional arguments passed to the dict constructor.
    :param **kwargs: Keyword arguments passed to the dict constructor.

    Example:
    ```
    bi_map = basicBiMap({'apple': 'red', 'banana': 'yellow'})
    print(bi_map['apple'])  # Output: 'red'
    print(bi_map.reverse['red'])  # Output: 'apple'
    ```

    :ivar reverse: A reverse mapping from values to keys.
    :vartype reverse: dict
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the BiMap.

        :param *args: Positional arguments passed to the dict constructor.
        :param **kwargs: Keyword arguments passed to the dict constructor.
        """
        super().__init__(*args, **kwargs)
        self.reverse = {value: key for key, value in self.items()}

    def __str__(self):
        """
        Return a string representation of the BiMap.

        :return: A string representation of the BiMap.
        :rtype: str
        """
        return "BiMap: " + super().__str__()

    def __setitem__(self, key, value):
        """
        Set a key-value pair in the BiMap.

        :param key: The key to set.
        :param value: The value to set.
        """
        super().__setitem__(key, value)  # call the original __setitem__ method
        self.reverse[value] = key  # update the reverse dict

    # Pass to super for methods necessary to be considered a Mapping class
    def __getitem__(self, key):
        return super().__getitem__(key)

    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        return super().__next__()

    def __len__(self):
        return super().__len__()

    def __eq__(self, other):
        """
        Compare the BiMap to another object for equality.

        :param other: The object to compare to.
        :type other: dict or basicBiMap

        :return: True if the BiMap is equal to the other object, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, basicBiMap) and not issubclass(type(other), dict):
            return False
        if not super().__eq__(other):
            if isinstance(other, basicBiMap) and other.reverse == dict(self):
                warnings.warn(
                    (
                        "Warning: Comparing basicBiMaps which are not equal, "
                        "but would be with keys and values swapped."
                    ),
                    reversedBiMapComparisonWarning,
                )
            return False
        return True
