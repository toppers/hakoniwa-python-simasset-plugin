#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class HakoAplOps(ABC):
    @abstractmethod
    def initialize():
        pass
    @abstractmethod
    def step():
        pass
    @abstractmethod
    def reset():
        pass
