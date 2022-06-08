# ============ Import python files ============
from hesperos.layout.gui_elements import add_sub_subgroup_radio_button


# ============ Import python packages ============
from qtpy.QtWidgets import QGridLayout, QGroupBox
from qtpy import QtCore

COLUMN_WIDTH_SUB = 40



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
        row : int
            row position of the sub panel in the layout of the parent (QGridLayout)
        column : int
            column position of the sub panel in the layout of the parent (QGridLayout)
        list_structures : list[str]
            list of the main groups of radio buttons
        dict_subgroups : dict[str, str]
            dictionnary of subgroups of main groups (name of radio buttons)
        dict_sub_subgroups : dict[str, str]
            dictionnary of sub-subgroups of subgroups (name of radio buttons)

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
        list_structures : list[str]
            list of the main groups of radio buttons
        dict_subgroups : dict[str, str]
            dictionnary of subgroups of main groups (name of radio buttons)
        dict_sub_subgroups : dict[str, str]
            dictionnary of sub-subgroups of subgroups (name of radio buttons)

        """

        # === Set sub panel parameters ===
        self.subpanel = QGroupBox("")
        self.subpanel.setObjectName("SubPanel")
        self.subpanel.setStyleSheet("""
                QGroupBox#SubPanel{
                    border: 0px;
                    border-radius: 0px;
                    padding: 0px 0px 0px 0px;
                },
                QGroupBox::title#SubPanel{
                    border: 0px;
                    border-radius: 0px;
                    padding: 0px 0px 0px 0px;
                    margin = 0px 0px 0px 0px
                }""")

        # === Set sub panel layout parameters ===
        sublayout = QGridLayout()
        sublayout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the sub panel layout ===
        self.group_radio_button, self.list_structure_name, self.list_button_in_subgroups = add_sub_subgroup_radio_button(
            list_items=list_structures,
            layout=sublayout,
            callback_function=self.change_structure_type,
            column=0,
            minimum_width=COLUMN_WIDTH_SUB,
            dict_subgroups=dict_substructures,
            dict_sub_subgroups=dict_sub_substructures
        )

        # sublayout.setColumnMinimumWidth(0, COLUMN_WIDTH_SUB)
        self.subpanel.setLayout(sublayout)

        # === Add sub panel to the main layout (QGridLayout) of the parent widget ===
        self.parent.layout.addWidget(self.subpanel, row, column)

        # === Disable sub panel ===
        self.subpanel.setVisible(False)

    def toggle_sub_panel(self, toggle_bool):
        """
        Toggle the annotation sub panel and corresponding group radio button (except button in a subgroup)

        Parameters
        ----------
        toggle_bool : bool
            toggle status

        """
        self.subpanel.setVisible(toggle_bool)
        for btn in self.group_radio_button.buttons():
            if btn not in self.list_button_in_subgroups:
                btn.setVisible(toggle_bool)   

    def change_structure_type(self, object):
        """
        Change the selected structure to annotate according to the choice of a group radio button

        Parameters
        ----------
        object : QAbstractButton
            selected button of a QButtonGroup

        """
        structure_id = self.group_radio_button.id(object)
        if hasattr(self.parent.viewer, 'layers'):
            if 'annotations' in self.parent.viewer.layers:
                self.parent.viewer.layers['annotations'].selected_label = structure_id
                self.parent.viewer.layers['annotations'].mode = "PAINT"