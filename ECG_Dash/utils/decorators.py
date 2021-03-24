'''
Created on Oct 17, 2020

@author: shanti
'''

''' Using class-based decorator to implement singleton pattern '''
class Singleton:

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self, **kwargs):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls(**kwargs)
            return self._instance
        #raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)

