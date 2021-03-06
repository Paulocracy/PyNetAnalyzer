"""The PyNetAnalyzer metabolite list"""
import cobra
from cnapy.cnadata import CnaData
from cnapy.utils import *
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (QAction, QHBoxLayout, QHeaderView, QLabel,
                            QLineEdit, QMenu, QMessageBox, QPushButton,
                            QSplitter, QTableWidget, QTableWidgetItem,
                            QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)


class MetaboliteList(QWidget):
    """A list of metabolites"""

    def __init__(self, appdata: CnaData):
        QWidget.__init__(self)
        self.appdata = appdata
        self.last_selected = None

        self.metabolite_list = QTreeWidget()
        self.metabolite_list.setHeaderLabels(["Id", "Name"])
        self.metabolite_list.setSortingEnabled(True)

        for m in self.appdata.project.cobra_py_model.metabolites:
            self.add_metabolite(m)
        self.metabolite_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.metabolite_list.customContextMenuRequested.connect(self.on_context_menu)

        # create context menu
        self.popMenu = QMenu(self.metabolite_list)
        in_out_fluxes_action = QAction('compute in/out fluxes for this metabolite', self.metabolite_list)
        self.popMenu.addAction(in_out_fluxes_action)
        in_out_fluxes_action.triggered.connect(self.emit_in_out_fluxes_action)

        self.metabolites_mask = MetabolitesMask(appdata)
        self.metabolites_mask.hide()

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.metabolite_list)
        self.splitter.addWidget(self.metabolites_mask)
        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

        self.metabolite_list.currentItemChanged.connect(
            self.metabolites_selected)
        self.metabolites_mask.changedMetaboliteList.connect(
            self.emit_changedModel)
        self.metabolites_mask.jumpToReaction.connect(
            self.emit_jump_to_reaction)

    def clear(self):
        self.metabolite_list.clear()
        self.metabolites_mask.hide()

    def add_metabolite(self, metabolite):
        item = QTreeWidgetItem(self.metabolite_list)
        item.setText(0, metabolite.id)
        item.setText(1, metabolite.name)
        item.setData(2, 0, metabolite)

    def on_context_menu(self, point):
        if len(self.appdata.project.cobra_py_model.metabolites)>0:
            self.popMenu.exec_(self.mapToGlobal(point))

    def update_annotations(self, annotation):

        self.metabolites_mask.annotation.itemChanged.disconnect(
            self.metabolites_mask.metabolites_data_changed)
        c = self.metabolites_mask.annotation.rowCount()
        for i in range(0, c):
            self.metabolites_mask.annotation.removeRow(0)
        i = 0
        for key in annotation:
            self.metabolites_mask.annotation.insertRow(i)
            keyl = QTableWidgetItem(key)
            iteml = QTableWidgetItem(str(annotation[key]))
            self.metabolites_mask.annotation.setItem(i, 0, keyl)
            self.metabolites_mask.annotation.setItem(i, 1, iteml)
            i += 1

        self.metabolites_mask.annotation.itemChanged.connect(
            self.metabolites_mask.metabolites_data_changed)

    def emit_changedModel(self):
        self.last_selected = self.metabolites_mask.id.text()
        self.changedModel.emit()

    def update_selected(self, string):
        print("metabolite_list:update_selected", string)
        root = self.metabolite_list.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            item.setHidden(True)

        for item in self.metabolite_list.findItems(string, Qt.MatchContains, 0):
            item.setHidden(False)
        for item in self.metabolite_list.findItems(string, Qt.MatchContains, 1):
            item.setHidden(False)

    def metabolites_selected(self, item, _column):
        # print("metabolites_selected")
        if item is None:
            self.metabolites_mask.hide()
        else:
            self.metabolites_mask.show()
            metabolites: cobra.Metabolite = item.data(2, 0)
            self.metabolites_mask.id.setText(metabolites.id)
            self.metabolites_mask.name.setText(metabolites.name)
            self.metabolites_mask.formula.setText(metabolites.formula)
            self.metabolites_mask.charge.setText(str(metabolites.charge))
            self.metabolites_mask.compartment.setText(metabolites.compartment)
            self.update_annotations(metabolites.annotation)
            self.metabolites_mask.old = metabolites
            self.metabolites_mask.changed = False

            turn_white(self.metabolites_mask.id)
            turn_white(self.metabolites_mask.name)
            turn_white(self.metabolites_mask.formula)
            turn_white(self.metabolites_mask.charge)
            turn_white(self.metabolites_mask.compartment)
            self.metabolites_mask.is_valid = True
            self.metabolites_mask.update_state()

    def update(self):
        self.metabolite_list.clear()
        for m in self.appdata.project.cobra_py_model.metabolites:
            self.add_metabolite(m)

        if self.last_selected is None:
            pass
        else:
            # print("something was previosly selected")
            items = self.metabolite_list.findItems(
                self.last_selected, Qt.MatchExactly)

            for i in items:
                self.metabolite_list.setCurrentItem(i)
                print(i.text(0))
                break

    def setCurrentItem(self, key):
        self.last_selected = key
        self.update()

    def emit_jump_to_reaction(self, reaction):
        self.jumpToReaction.emit(reaction)
        
    def emit_in_out_fluxes_action (self):
        self.computeInOutFlux.emit(self.metabolite_list.currentItem().text(0))

    itemActivated = Signal(str)
    changedModel = Signal()
    jumpToReaction = Signal(str)
    computeInOutFlux = Signal(str)


class MetabolitesMask(QWidget):
    """The input mask for a metabolites"""

    def __init__(self, appdata):
        QWidget.__init__(self)
        self.appdata = appdata
        self.old = None
        self.is_valid = True
        self.changed = False
        layout = QVBoxLayout()
        l = QHBoxLayout()
        label = QLabel("Id:")
        self.id = QLineEdit()
        l.addWidget(label)
        l.addWidget(self.id)
        layout.addItem(l)

        l = QHBoxLayout()
        label = QLabel("Name:")
        self.name = QLineEdit()
        l.addWidget(label)
        l.addWidget(self.name)
        layout.addItem(l)

        l = QHBoxLayout()
        label = QLabel("Formula:")
        self.formula = QLineEdit()
        l.addWidget(label)
        l.addWidget(self.formula)
        layout.addItem(l)

        l = QHBoxLayout()
        label = QLabel("Charge:")
        self.charge = QLineEdit()
        l.addWidget(label)
        l.addWidget(self.charge)
        layout.addItem(l)

        l = QHBoxLayout()
        label = QLabel("Compartment:")
        self.compartment = QLineEdit()
        l.addWidget(label)
        l.addWidget(self.compartment)
        layout.addItem(l)

        l = QVBoxLayout()
        label = QLabel("Annotations:")
        l.addWidget(label)
        l2 = QHBoxLayout()
        self.annotation = QTableWidget(0, 2)
        self.annotation.setHorizontalHeaderLabels(
            ["key", "value"])
        self.annotation.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l2.addWidget(self.annotation)

        self.add_anno = QPushButton("+")
        self.add_anno.clicked.connect(self.add_anno_row)
        l2.addWidget(self.add_anno)
        l.addItem(l2)
        layout.addItem(l)

        l = QVBoxLayout()
        label = QLabel("Reactions using this metabolite:")
        l.addWidget(label)
        l2 = QHBoxLayout()
        self.reactions = QTreeWidget()
        self.reactions.setHeaderLabels(["Id"])
        self.reactions.setSortingEnabled(True)
        l2.addWidget(self.reactions)
        l.addItem(l2)
        self.reactions.itemDoubleClicked.connect(self.emit_jump_to_reaction)
        layout.addItem(l)

        l = QHBoxLayout()
        self.apply_button = QPushButton("apply changes")

        l.addWidget(self.apply_button)
        layout.addItem(l)

        self.setLayout(layout)

        self.id.textEdited.connect(self.metabolites_data_changed)
        self.name.textEdited.connect(self.metabolites_data_changed)
        self.formula.textEdited.connect(self.metabolites_data_changed)
        self.charge.textEdited.connect(self.metabolites_data_changed)
        self.compartment.textEdited.connect(self.metabolites_data_changed)
        self.annotation.itemChanged.connect(self.metabolites_data_changed)
        self.apply_button.clicked.connect(self.apply)
        self.validate_mask()

    def add_anno_row(self):
        i = self.annotation.rowCount()
        self.annotation.insertRow(i)
        self.changed = True

    def apply(self):
        if self.old is None:
            self.old = cobra.metabolites(
                id=self.id.text())
            self.appdata.project.cobra_py_model.add_metabolite(self.old)
        try:
            self.old.id = self.id.text()
        except:
            msgBox = QMessageBox()
            msgBox.setText("Could not apply changes identifier already used.")
            msgBox.exec()
            pass
        else:
            self.old.name = self.name.text()
            self.old.formula = self.formula.text()
            self.old.charge = int(self.charge.text())
            self.old.compartment = self.compartment.text()
            self.old.annotation = {}
            rows = self.annotation.rowCount()
            for i in range(0, rows):
                key = self.annotation.item(i, 0).text()
                value = self.annotation.item(i, 1).text()
                print(key, value)
                self.old.annotation[key] = value

            self.changed = False
            self.changedMetaboliteList.emit()

    def validate_id(self):
        import sys
        import traceback
        with self.appdata.project.cobra_py_model as model:
            text = self.id.text()
            if text == "":
                turn_red(self.id)
                return False
            if ' ' in text:
                turn_red(self.id)
                return False
            try:
                m = cobra.Metabolite(id=self.id.text())
                model.add_metabolite([m])
            except Exception:

                traceback.print_exception(*sys.exc_info())
                turn_red(self.id)
                return False
            else:
                turn_white(self.id)
                return True

    def validate_name(self):
        with self.appdata.project.cobra_py_model as model:
            try:
                m = cobra.Metabolite(id="test_id", name=self.name.text())
                model.add_metabolite([m])
            except:
                turn_red(self.name)
                return False
            else:
                turn_white(self.name)
                return True

    def validate_formula(self):
        return True

    def validate_charge(self):
        try:
            x = int(self.charge.text())
        except:
            turn_red(self.charge)
            return False
        else:
            turn_white(self.charge)
            return True

    def validate_compartment(self):
        try:
            m = cobra.Metabolite(id="test_id", name=self.compartment.text())
        except:
            turn_red(self.compartment)
            return False
        else:
            turn_white(self.compartment)
            return True

    def validate_mask(self):
        valid_id = self.validate_id()
        valid_name = self.validate_name()
        valid_formula = self.validate_formula()
        valid_charge = self.validate_charge()
        valid_compartment = self.validate_compartment()
        if valid_id & valid_name & valid_formula & valid_charge & valid_compartment:
            self.is_valid = True
        else:
            self.is_valid = False

        self.update_state()

    def metabolites_data_changed(self):
        self.changed = True
        self.validate_mask()

    def update_state(self):
        if self.old is None:
            pass
        else:
            if self.is_valid & self.changed:
                self.apply_button.setEnabled(True)
            else:
                self.apply_button.setEnabled(False)

        self.reactions.clear()
        if self.appdata.project.cobra_py_model.metabolites.has_id(self.id.text()):
            metabolite = self.appdata.project.cobra_py_model.metabolites.get_by_id(
                self.id.text())
            for r in metabolite.reactions:
                item = QTreeWidgetItem(self.reactions)
                item.setText(0, r.id)
                item.setText(1, r.name)
                item.setData(2, 0, r)
                text = "Id: " + r.id + "\nName: " + r.name
                item.setToolTip(1, text)

    def emit_jump_to_reaction(self, reaction):
        self.jumpToReaction.emit(reaction.data(2, 0).id)

    jumpToReaction = Signal(str)
    changedMetaboliteList = Signal()
