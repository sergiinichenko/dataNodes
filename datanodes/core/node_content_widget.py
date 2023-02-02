# -*- encoding:utf8 -*-
"""Module docs"""
from datanodes.core.node_serializer import Serializer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
#from PyQt5.QtCore import *
from collections import OrderedDict

DEBUG = False

class NodeContentWidget(QWidget, Serializer):
    """Class docs"""

    def __init__(self, node:'Node', parent:'QWidget'=None):
        """default constructor"""
        self.node = node
        
        super().__init__(parent)
        self.initUI()


    def initUI(self):
        """Setting up default layout"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.layout.addWidget(QTextEdit("foo"))


    def serialize(self) -> OrderedDict:
        """
        :return:
        """
        return OrderedDict([
            ('id' , self.id),
            ('content', "")
        ])
        
    def deserialize(self, data:dict, hashmap:dict=[]) -> bool:
        """The default deserialize method. Has to be overwritten in the inherited class
        Returns ``True`` if the element has been successfuly deserialized

        :param data: input data to be deserialized
        :type data: ``dict``
        :param hashmap: the [optional] hashmap of the data, stores id of the elements in the scene
        :type hashmap: ``list``
        :return: ``True`` if deserialized
        :rtype: ``boot``
        """
        return True