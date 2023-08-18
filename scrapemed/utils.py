"""
Various utilities for markup language and text processing. Classes for text sections, paragraphs, figure/xref/table reference BiMaps.
"""
import warnings

class reversedBiMapComparisonWarning(Warning):
    """
    Raised when comparing basicBiMaps which are exactly the same but reversed.
    """
    pass

class basicBiMap(dict):
    """
    BiMap class which extends python's dict class to also store a reverse of itself for efficiency.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reverse = {value: key for key, value in self.items()}
        
    def __str__(self):
        return "BiMap: " + super().__str__()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)  # call the original __setitem__ method
        self.reverse[value] = key  # update the reverse dict

    #Pass to super for methods necessary to be considered a Mapping class
    def __getitem__(self, key):
        return super().__getitem__(key)
    def __iter__(self):
        return super().__iter__()
    def __next__(self):
        return super().__next__()
    def __len__(self):
        return super().__len__()

    def __eq__(self, other):
        if not isinstance(other, basicBiMap) and not issubclass(type(other), dict):
            return False
        if not super().__eq__(other):
            if isinstance(other, basicBiMap) and other.reverse == dict(self):
                warnings.warn("Warning: Comparing basicBiMaps which are not equal, but would be with keys and values swapped.",
                                reversedBiMapComparisonWarning)   
            return False
        return True

