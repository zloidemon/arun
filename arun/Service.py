from abc import ABCMeta, abstractmethod


class ARunService(metaclass=ABCMeta):
    @abstractmethod
    def signals(self):
        """ define signals """

    @abstractmethod
    def run(self):
        """ run application """
