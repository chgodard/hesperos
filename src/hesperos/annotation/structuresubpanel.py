# ============ Import python files ============
from hesperos.layout.gui_elements import add_sub_subgroup_radio_button


# ============ Import python packages ============
from qtpy.QtWidgets import QGridLayout, QGroupBox
from qtpy import QtCore


# ============ Define variables ============
SEGM_METHODS_PANEL_ALIGN = (
    "left"  # Alignment of text in pushbuttons in methods chooser panel
)


# ============ Define class ============
class StructureSubPanel(QGroupBox):
    """
        QGroupBox class for segmentation data with a QRadioButton for each structure to annotate
    """

    def __init__(self, parent, row, column, list_structures, dict_substructures=[], dict_sub_substructures=[]):
        """ Initilialisation of the subwidget in the main widget of the plugin

        Parameters
        ----------
        parent : QWidget
            parent widget

        """
        super().__init__()

        self.parent = parent
        self.add_sub_panel(row, column, list_structures, dict_substructures, dict_sub_substructures)

    def add_sub_panel(self, row, column, list_structures, dict_substructures, dict_sub_substructures):
        """
        Create a disabled sub panel in the layout of the parent widget

        Parameters
        ----------
        row : int
            row position of the sub panel in the layout of the parent (QGridLayout)
        column : int
            column position of the panel in the layout of the parent (QGridLayout)

        """

        # === Set sub panel parameters ===
        self.subpanel = QGroupBox("")
        self.subpanel.setObjectName("SubPanel")
        self.subpanel.setStyleSheet("QGroupBox#SubPanel{border: 0px;}")

        # === Set sub panel layout parameters ===
        sublayout = QGridLayout()
        sublayout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the sub panel layout ===
        self.group_radio_button, self.nbr_buttons, self.list_structure_name = add_sub_subgroup_radio_button(
            name="",
            list_items=list_structures,
            layout=sublayout,
            callback_function=self.change_structure_type,
            column=0,
            minimum_width=30,
            dict_subgroups=dict_substructures,
            dict_sub_subgroups=dict_sub_substructures
        )

        sublayout.setColumnMinimumWidth(0, 30)
        self.subpanel.setLayout(sublayout)

        # === Add sub panel to the main layout (QGridLayout) of the parent widget ===
        self.parent.layout.addWidget(self.subpanel, row, column)

        # === Disable sub panel ===
        self.subpanel.setVisible(False)

    def toggle_sub_panel(self, toggle_bool):
        """
        Toggle the annotation sub panel and corresponding group radio button

        Parameters
        ----------
        toggle_bool : bool
            toggle status

        """
        self.subpanel.setVisible(toggle_bool)
        for btn in self.group_radio_button.buttons():
            btn.setVisible(toggle_bool)

    def change_structure_type(self, object):
        """
        Change the selected structure to annotate according to the choice of a group radio button

        Parameters
        ----------
        object : ??
            ??

        """
        structure_id = self.group_radio_button.id(object)
        if hasattr(self.parent.viewer, 'layers'):
            if 'annotations' in self.parent.viewer.layers:
                self.parent.viewer.layers['annotations'].selected_label = structure_id
                self.parent.viewer.layers['annotations'].mode = "PAINT"


