import os
import shutil

from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QGroupBox, QListWidgetItem, QDialog, QMessageBox, QIcon, QVBoxLayout, QTreeView, QHeaderView

from data_sources_list import DataSourcesList, USER_DS_PATHS
from ds_edit_dialog import DsEditDialog
from data_sources_model import DSManagerModel

import resources_rc

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'user_services_box.ui'))


class UserServicesBox(QGroupBox, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(UserServicesBox, self).__init__(parent)
        self.setupUi(self)

        self.feel_list()

        self.lstServices.currentItemChanged.connect(self.on_sel_changed)
        self.lstServices.itemDoubleClicked.connect(self.on_edit)
        self.btnEdit.clicked.connect(self.on_edit)
        self.btnAdd.clicked.connect(self.on_add)
        self.btnDelete.clicked.connect(self.on_delete)
        self.btnCopy.clicked.connect(self.on_copy)

        self.btnAdd.setIcon(QIcon(":/plugins/QuickMapServices/icons/plus.svg"))
        self.btnEdit.setIcon(QIcon(":/plugins/QuickMapServices/icons/compose.svg"))
        self.btnDelete.setIcon(QIcon(":/plugins/QuickMapServices/icons/trash.svg"))
        self.btnCopy.setIcon(QIcon(":/plugins/QuickMapServices/icons/copy.svg"))

        self.ds_model = DSManagerModel()

    def feel_list(self):
        self.lstServices.clear()
        ds_list = DataSourcesList(USER_DS_PATHS)
        for ds in ds_list.data_sources.itervalues():
            item = QListWidgetItem(ds.action.icon(), ds.action.text())
            item.setData(Qt.UserRole, ds)
            self.lstServices.addItem(item)

    def on_sel_changed(self, curr, prev):
        has_sel = curr is not None
        self.btnEdit.setEnabled(has_sel)
        self.btnDelete.setEnabled(has_sel)

    def on_add(self):
        edit_dialog = DsEditDialog()
        edit_dialog.setWindowTitle(self.tr('Create service'))
        if edit_dialog.exec_() == QDialog.Accepted:
            self.feel_list()
            self.ds_model.resetModel()

    def on_edit(self):
        item = self.lstServices.currentItem().data(Qt.UserRole)
        edit_dialog = DsEditDialog()
        edit_dialog.setWindowTitle(self.tr('Edit service'))
        edit_dialog.set_ds_info(item)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.feel_list()
            self.ds_model.resetModel()

    def on_delete(self):
        res = QMessageBox.question(None,
                                   self.tr('Delete service'),
                                   self.tr('Delete selected service?'),
                                   QMessageBox.Yes, QMessageBox.No)
        if res == QMessageBox.Yes:
            ds_info = self.lstServices.currentItem().data(Qt.UserRole)
            dir_path = os.path.abspath(os.path.join(ds_info.file_path, os.path.pardir))
            shutil.rmtree(dir_path, True)
            self.feel_list()
            self.ds_model.resetModel()

    def on_copy(self):
        self.ds_model.sort(DSManagerModel.COLUMN_GROUP_DS)

        select_data_sources_dialog = QDialog(self)
        select_data_sources_dialog.setWindowTitle(self.tr("Choose source service"))
        layout = QVBoxLayout(select_data_sources_dialog)
        select_data_sources_dialog.setLayout(layout)

        list_view = QTreeView(self)
        layout.addWidget(list_view)
        list_view.setModel(self.ds_model)
        list_view.setColumnHidden(DSManagerModel.COLUMN_VISIBILITY, True)
        list_view.setAlternatingRowColors(True)
        list_view.header().setResizeMode(DSManagerModel.COLUMN_GROUP_DS, QHeaderView.ResizeToContents)
        list_view.clicked.connect(
            lambda index: select_data_sources_dialog.accept() \
                if not self.ds_model.isGroup(index) and \
                    index.column() == DSManagerModel.COLUMN_GROUP_DS \
                else None
        )

        if select_data_sources_dialog.exec_() == QDialog.Accepted:
            data_source = self.ds_model.data(list_view.currentIndex(), Qt.UserRole)
            data_source.id += "_copy"
            edit_dialog = DsEditDialog()
            edit_dialog.setWindowTitle(self.tr('Create service from existing'))
            edit_dialog.fill_ds_info(data_source)
            if edit_dialog.exec_() == QDialog.Accepted:
                self.feel_list()
                self.ds_model.resetModel()
