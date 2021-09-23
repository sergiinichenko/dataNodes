Welcome to DataNodes 
==========================

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/datanodes.png
    :width: 150
    :alt: Screenshot of Simple Data Node

.. contents:: Outline


About
=====

This package is created with the goal of simplifying data processing and analysis. 
https://github.com/sergiinichenko/dataNodes

Features
--------

- a set of nodes for loading and reading data
- data processing node for cleaning and removing NaN data
- separate and combine data for convenience of work
- plot the data
- show data in a table format

Requirements
------------

- Python 3.x
- PyQt5 or PySide2 (using wrapper QtPy)
- matplotlib>=3.4.0
- pandas>=1.2.0

Installation
------------
.. code-block:: bash

    pip install -i https://test.pypi.org/simple/ datanodes



Or download the source code from gitlab

.. code-block:: bash

    git clone https://github.com/sergiinichenko/dataNodes


Or download the source code from gitlab

.. code-block:: bash

    git clone https://github.com/sergiinichenko/dataNodes


How to run
------------

To be able to run the DataNodes you have to create a minimal python script and run it, e.g. datanodes.py file

.. code-block:: python

    # the datanodes.py file 
    import sys, os
    from PyQt5.QtWidgets import *
    from datanodes.core.main_window import MainWindow

    if __name__ == '__main__':
        app = QApplication(sys.argv)
        wnd = MainWindow()
        sys.exit(app.exec_())

Then you can use any python IDE to run the script (VSCode, Spyder3, etc.) or run it from the console by running:

.. code-block:: bash

    python3 datanodes.py

This script will start the DataNodes. 


Basic Tutorial
--------------

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/EmptyDataNodes.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/NewDataNodes.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddInputFile.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddTableOutput.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/ConnectInputToTable.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddCleanNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/CleanNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/DropCleanNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/SetupCleanNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddSeparateNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/ConnectSeparateNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/SeparateNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddCombineNode.png
    :width: 500
    :alt: Screenshot of Simple Data Node

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/tutorial-basic/AddPlot.png
    :width: 500
    :alt: Screenshot of Simple Data Node



Screenshots
-----------

.. image:: https://github.com/sergiinichenko/dataNodes/blob/master/media/img/DataNodes.png
  :alt: Screenshot of Simple Data Node

Other links
-----------
