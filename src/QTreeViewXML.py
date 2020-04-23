from PyQt5 import QtCore, QtGui, QtXml

class XmlHandler(QtXml.QXmlDefaultHandler):
    def __init__(self, root):
        QtXml.QXmlDefaultHandler.__init__(self)
        self._root = root
        self._item = None
        self._text = ''
        self._error = ''

    def startElement(self, namespace, name, qname, attributes):
        if qname == 'folder' or qname == 'item':
            if self._item is not None:
                self._item = QtGui.QTreeWidgetItem(self._item)
            else:
                self._item = QtGui.QTreeWidgetItem(self._root)
            self._item.setData(0, QtCore.Qt.UserRole, qname)
            self._item.setText(0, 'Unknown Title')
            if qname == 'folder':
                self._item.setExpanded(True)
            elif qname == 'item':
                self._item.setText(1, attributes.value('type'))
        self._text = ''
        return True

    def endElement(self, namespace, name, qname):
        if qname == 'title':
            if self._item is not None:
                self._item.setText(0, self._text)
        elif qname == 'folder' or qname == 'item':
            self._item = self._item.parent()
        return True

    def characters(self, text):
        self._text += text
        return True

    def fatalError(self, exception):
        print('Parse Error: line %d, column %d:\n  %s' % (
              exception.lineNumber(),
              exception.columnNumber(),
              exception.message(),
              ))
        return False

    def errorString(self):
        return self._error