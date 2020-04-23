#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#                         
#============================================================(C) JPL 2019=======

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import mmap

import settings

#-------------------------------------------------------------------------------
# Const
#-------------------------------------------------------------------------------
NONPRINTABLE = (0, 7, 8, 9, 10, 13)

HEADER_CSS = '''
::section {
    border: 0px;
    padding: 1px;
    text-align: center;
    font: Consolas;
    }
::section:checked {
    color: white;
    font-weight: normal;
    background-color: blue;
    }
::section:hover {
    color: blue;
    }
'''

TABLE_CSS = '''
::item {
    gridline-color: white;
    }
::item:focus {
    border: 0px;
    color: red;
    gridline-color: white;
    }
::item:hover {
    color: blue;
    }
'''

#-------------------------------------------------------------------------------
# Class Dataview
#-------------------------------------------------------------------------------
class DataView:
    """
    Data view object: wrapper over raw binary data, files etc.

    :param data: The raw data (bytes or bytearray).
    :param filename: The file name containing the data.
    """
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, data=None, filename=None, readonly=True):
        if not (data or filename):
            raise ValueError('Raw data or a filename must be provided!')
        if data and not readonly and type(data) is bytes:
            data = bytearray(data)
        self.rawdata = data
        self.filename = filename
        self.readonly = readonly
        self._data = None


    @property
#-------------------------------------------------------------------------------
# data()
#-------------------------------------------------------------------------------
    def data(self):
        """
        This is the actual data. The file view is created automagically as needed and can be closed with .close().
        """
        if self._data is not None:
            return self._data
        if self.filename:
            mode, access  = 'r+', mmap.ACCESS_READ
            if not self.readonly:
                mode = 'w'
                access |= mmap.ACCESS_WRITE
            # TODO : manage Windows & Unix OS case
            # TODO : manage empty files
            # TODO : manage readonly=False
            self.fh = open(self.filename, mode)
            self.mm = mmap.mmap(self.fh.fileno(), 0, access=access)
            self._data = self.mm
        else:
            self._data = self.rawdata
        return self._data


#-------------------------------------------------------------------------------
# close()
#-------------------------------------------------------------------------------
    def close(self):
        """
        Close the file (if open).
        """
        if self._data is not None:
            self.mm.close()
            self.fh.close()
            self._data = None

#-------------------------------------------------------------------------------
# __setitem__()
#-------------------------------------------------------------------------------
    def __setitem__(self, item, value):
        if self.readonly:
            raise ValueError('Readonly flag set!')
        self.data[item] = value

#-------------------------------------------------------------------------------
# __getitem__()
#-------------------------------------------------------------------------------
    def __getitem__(self, item):
        return self.data[item]

#-------------------------------------------------------------------------------
# __len__()
#-------------------------------------------------------------------------------
    def __len__(self):
        return len(self.data)


#-------------------------------------------------------------------------------
# Class QHexEditor
#-------------------------------------------------------------------------------
class QHexEditor(QtWidgets.QWidget):
    """
    Hex editor widget.

    :param data: The raw data (bytes or bytearray).
    :param filename: The file name containing the data.
    """
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, data=None, filename=None, readonly=True, columns=16):
        super().__init__()
        self.filename = filename
        self.font = QtGui.QFont('Consolas', 10)
        self.metrics = QtGui.QFontMetrics(self.font)
        self.row_height = self.metrics.height() + 4
        self.columns = columns
        self.rows = 1
        self.perpage = self.columns * self.rows
        self.dm = None
        self.hexview = QtWidgets.QTableView(font=self.font, showGrid=1, styleSheet=TABLE_CSS)
        self.hexview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.hexview.horizontalHeader().setHighlightSections(1)
        self.hexview.verticalHeader().setHighlightSections(1)
        self.scroll = QtWidgets.QScrollBar(Qt.Vertical)
        self.scroll.setPageStep(1)
        self.scroll.valueChanged[int].connect(self.jump_to_row)
        self.l1 = QtWidgets.QVBoxLayout()
        self.l2 = QtWidgets.QHBoxLayout()
        self.l3 = QtWidgets.QHBoxLayout()
        self.l2.addWidget(self.hexview)
        self.l2.addWidget(self.scroll)
        self.l1.addLayout(self.l2)

        self.status = {}
        self.lbl_offset = QtWidgets.QLabel('Offset:')
        self.status['offset'] = QtWidgets.QLabel('-')
        hSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.l3.addWidget(self.lbl_offset)
        self.l3.addWidget(self.status['offset'])        
        self.l3.addItem(hSpacer)        
        
        self.l1.addLayout(self.l3)
        self.setLayout(self.l1)
        self.setMinimumWidth(800)
        # self.connect(QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self), SIGNAL('activated()'), sys.exit)
        self._data = None
        self.dm = QtGui.QStandardItemModel(self.rows, self.columns)
        self.hexview.setModel(self.dm)
        self.hexview.horizontalHeader().setStretchLastSection(0)
        self.hexview.selectionModel().selectionChanged.connect(self.sel_changed)
        self.open(data, filename, readonly)
        self.jump()

#-------------------------------------------------------------------------------
# sel_changed()
#-------------------------------------------------------------------------------
    def sel_changed(self, new, old):
        """
        Selection changing is monitored to allow highlighting matching selected bytes between the hex dump and the text.
        """
        new, old = ([(e.row(), (e.column() + self.columns) % (2 * self.columns)) for e in lst.indexes()] \
                for lst in (new, old))
        for e in old:
            if e in new:
                continue
            self.dm.item(*e).setBackground(QtGui.QColor('#FFFFFF'))
        for e in new:
            if e in old:
                continue
            self.dm.item(*e).setBackground(QtGui.QColor('#53868B'))
        idx = self.hexview.selectionModel().currentIndex()
        offs = self.offs + idx.row() * self.columns + idx.column()
        self.status['offset'].setText('<b>0x%X</b> (%d)' % (offs, offs))


#-------------------------------------------------------------------------------
# wheelEvent()
#-------------------------------------------------------------------------------
    def wheelEvent(self, evt):
        """
        Hooked to implement scrolling by mouse wheel.
        """
        self.jump_rows(1 if evt.angleDelta().y() > 0 else -1)
        evt.accept()

#-------------------------------------------------------------------------------
# keyPressEvent()
#-------------------------------------------------------------------------------
    def keyPressEvent(self, evt):
        """
        Hooked to implement scrolling by up/down/pgup/pgdn.

        Note: only events which aren't caught by self.hexview end up here.
        """
        key = evt.key()
        if key in (Qt.Key_PageUp, Qt.Key_PageDown):
            self.jump_pages(1 if key == Qt.Key_PageUp else -1)
            evt.accept()
        elif key in (Qt.Key_Up, Qt.Key_Down):
            self.jump_rows(1 if key == Qt.Key_Up else -1)
            evt.accept()

#-------------------------------------------------------------------------------
# resizeEvent()
#-------------------------------------------------------------------------------
    def resizeEvent(self, evt):
        """
        This keeps self.rows/columns/perpage updated and regenerates the self.hexdump content.
        """
        self.rows = (self.hexview.height() - self.hexview.horizontalHeader().height() - 6) // self.row_height
        self.perpage = self.columns * self.rows
        self.dm.setRowCount(self.rows)
        self.jump(self.offs)
        super().resizeEvent(evt)

#-------------------------------------------------------------------------------
# open()
#-------------------------------------------------------------------------------
    def open(self, data=None, filename=None, readonly=True):
        """
        Open a file (or a data buffer).
        """
        self.offs = 0
        if self._data is not None:
            self._data.close()
        self._data = DataView(data=data, filename=filename, readonly=readonly)
        self.size = len(self._data)
        self.scroll.setRange(0, self.size // self.columns)

#-------------------------------------------------------------------------------
# jump_pages()
#-------------------------------------------------------------------------------
    def jump_pages(self, pages=1):
        """
        Jump a number of pages up / down.

        :param pages: Number of pages to jump; negative values jump down.
        """
        self.jump(self.offs - pages * self.perpage)

#-------------------------------------------------------------------------------
# jump_rows()
#-------------------------------------------------------------------------------
    def jump_rows(self, rows=1):
        """
        Jump a number of rows up / down.

        :param rows: Number of rows to jump; negative values jump down.
        """
        self.jump(self.offs - rows * self.columns)

#-------------------------------------------------------------------------------
# jump_to_row()
#-------------------------------------------------------------------------------
    def jump_to_row(self, row):
        """
        Jump to the given row id.
        """
        self.jump(row * self.columns)


#-------------------------------------------------------------------------------
# jump()
#-------------------------------------------------------------------------------
    def jump(self, offs=0):
        """
        Jump to the given offset (this is the main workhorse which updates the self.hexview contents).
        """
        brushes = [QtGui.QBrush(QtGui.QColor(x)) for x in ('#506080', '#8D431F')]
        hv = self.hexview
        crt = hv.selectionModel().currentIndex()
        vh = hv.verticalHeader()
        hh = hv.horizontalHeader()
        ### get data window
        self.offs = max(0, min(offs, self.size - self.perpage))
        data = self._data[self.offs:self.offs + self.perpage]
        ### generate & set labels
        addrlabels = [' %08X ' % i for i in range(self.offs, self.offs + self.perpage, self.columns)]
        self.dm.setVerticalHeaderLabels(addrlabels)
        self.dm.setHorizontalHeaderLabels([("%02X" % x) for x in range(self.columns)] + [("%X" % x) for x in range(self.columns)])
        ### generate data for datamodel (actual hexview contents)
        idx = 0   # offset inside the data window (index in `data`)
        for row in range(self.rows):
            for col in range(self.columns):
                if idx < len(data):
                    c = data[idx]
                    # HEXA VIEW
                    hitem = QtGui.QStandardItem("%02X" % c)
                    hitem.setTextAlignment(Qt.AlignCenter)
                    hitem.setForeground(brushes[col % 2])
                    hitem.setBackground(QtGui.QBrush(QtGui.QColor(settings.db['HEXEDITOR_HEXA_BACKGROUND'])))
                    # ASCII TEXT VIEW
                    titem = QtGui.QStandardItem(bytes([46 if c in NONPRINTABLE else c]).decode('cp437'))
                    titem.setTextAlignment(Qt.AlignCenter)
                    titem.setForeground(brushes[col % 2])
                    titem.setBackground(QtGui.QBrush(QtGui.QColor(settings.db['HEXEDITOR_TEXT_BACKGROUND'])))
                else:
                    hitem = titem = None
                self.dm.setItem(row, col, hitem)
                self.dm.setItem(row, col + self.columns, titem)
                idx += 1
        ### format view
        hh.setDefaultSectionSize(hv.fontMetrics().width('AAA') + 2)
        hh.setMaximumSectionSize(hv.fontMetrics().width('AAA') + 2)
        # hh.setMaximumSectionSize(hv.fontMetrics().width('AAAAA'))
        for i in range(16):
            hh.resizeSection(i, hv.fontMetrics().width('AAA') + 2)
            hh.resizeSection(i + self.columns, hv.fontMetrics().width('AA') + 2)
            # hh.resizeSection(i + self.columns, hv.fontMetrics().width('I'))
        vh.setDefaultSectionSize(self.row_height)
        vh.setDefaultAlignment(Qt.AlignCenter)
        vh.setStyleSheet(HEADER_CSS)
        hh.setStyleSheet(HEADER_CSS)
        ### restore pre-scroll selection
        hv.setCurrentIndex(crt)


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    # import random
    import sys
    # data = bytes(random.randint(0, 255) for i in range(1024))
    fn = sys.argv[-1]   # filename given as parameter or the script itself
    data = open(fn, 'rb').read()
    app = QtWidgets.QApplication()
    he = QHexEditor(data=data)
    he.show()
    sys.exit(app.exec_())
