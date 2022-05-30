# ============ Import python packages ============
from qtpy.QtWidgets import (
    QPushButton,
    QCheckBox,
    QLabel,
    QComboBox,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QSlider,
    QGroupBox,
    QGridLayout,
)

from qtpy.QtGui import QPixmap, QFont
from qtpy import QtCore


# ============ Functions to add custom QWidgets ============
def add_push_button(name, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0, alignment="center"):
    """
    Create a QPushButton and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget in the grid
    column : int
        column  of the widget in the grid
    column_span : int
        column span of the widget
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    alignment : Qt.Alignment
        alignement inside the widget

    Returns
    ----------
    out : QPushButton

    """

    button = QPushButton(name)
    button.setVisible(visibility)

    if alignment == "center":
        pass
    elif alignment == "left":
        button.setStyleSheet("QPushButton { text-align: left; }")
    elif alignment == "right":
        button.setStyleSheet("QPushButton { text-align: right; }")


    button.setMinimumWidth(minimum_width)
    layout.addWidget(button, row, column, 1, column_span)
    button.clicked.connect(callback_function)

    return button

def add_icon_push_button(name, icon, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0, alignment="center", isBoxLayout=False):
    """
    Create a QPushButton with only a icon image (no text) and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    icon : QIcon
        icon of the widget
    layout : QGridLayout or QVBox TODO : check if use of vertical layout
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget in the grid (used if the layout is a QGridLayout)
    column : int
        column  of the widget in the grid
    column_span : int
        column span of the widget (used if the layout is a QGridLayout)
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    alignment : Qt.Alignment
        alignement inside the widget
    isBoxLayout : bool
        status of the layout : true if the layout is a QGridLayout, false if not

    Returns
    ----------
    out : QPushButton

    """

    button = QPushButton(icon, name)
    button.setVisible(visibility)

    button.setFixedSize(25, 25)
    button.setIconSize(QtCore.QSize(20,20))
    button.setStyleSheet("text-align: center;")

    if isBoxLayout:
        layout.addWidget(button, column)
    else:
        layout.addWidget(button, row, column, 1, column_span)
    button.clicked.connect(callback_function)

    return button

def add_radio_button(name, layout, callback_function, row, column, visibility=False, minimum_width=0, alignment="center"):
    """
    Create a QRadioButton and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget in the grid
    column : int
        column  of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    alignment : Qt.Alignment
        alignement inside the widget

    Returns
    ----------
    out : QRadioButton

    """

    button = QRadioButton(name)
    button.setVisible(visibility)

    if alignment == "center":
        pass
    elif alignment == "left":
        button.setStyleSheet(
            "QRadioButton { text-align: left; padding: 0; spacing: 30px;}"
        )
    elif alignment == "right":
        button.setStyleSheet(
            "QRadioButton { text-align: right; padding: 0; spacing: 30px;}"
        )

    button.setMinimumWidth(minimum_width)
    layout.addWidget(button, row, column)
    button.clicked.connect(callback_function)

    return button

def add_image_widget(name, layout, image_path, row, column, visibility=False, minimum_width=0):
    """
    Create a QLabel with an image and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    layout : QGridLayout
        layout containing the widget
    image_path : str
        file path of the 2D image to display
    row : int
        row of the widget in the grid
    column : int
        column  of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget

    Returns
    ----------
    out : QLabel

    """
    label = QLabel(name)
    pixmap = QPixmap(image_path)
    label.setPixmap(pixmap)

    label.setVisible(visibility)
    label.setMinimumWidth(minimum_width)
    layout.addWidget(label, row, column)

    return label

def add_group_radio_button(name, items, layout, callback_function, column=0, visibility=False, minimum_width=0, alignment="center"):
    """
    Create a QButtonGroup of QRadioButton and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    items :TODO

    layout : QVBoxLayout TODO TOCHECK
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    column : int
        column  of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    alignment : Qt.Alignment
        alignement inside the widget

    Returns
    ----------
    button : QButtonGroup

    nbr_buttons: int
        number of QRadioButtons in the QButtonGroup

    """
    
    group_button = QButtonGroup()

    for label, item in enumerate(items):
        button = QRadioButton(item)
        button.setVisible(visibility)

        button.setMinimumWidth(minimum_width)

        group_button.addButton(button, label + 1)
        layout.addWidget(button, label, column)

    radio_button_to_check = group_button.button(label + 1)
    radio_button_to_check.setChecked(True)

    nbr_buttons = label + 1

    group_button.buttonClicked.connect(callback_function)

    return group_button, nbr_buttons

def add_sub_subgroup_radio_button(name, list_items, layout, callback_function, column=0, visibility=False, minimum_width=0, dict_subgroups={}, dict_sub_subgroups={}):
    """
    Create a QButtonGroup of QRadioButton and add it to the corresponding layout

    Parameters
    ----------
    name : str
        name of the push button to be displayed
    list_items: list[str]
    TODO

    layout : QVBoxLayout TODO TOCHECK
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    column : int
        column  of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    dict_subgroups : dict[str, str]
    TODO

    dict_sub_subgroups : dict[str, str]
    TODO


    Returns
    ----------
    button : QButtonGroup

    nbr_buttons : int
        number of QRadioButtons in the QButtonGroup

    list_structure_name : List[str]
        list of all structure to annotate

    """
    
    group_button = QButtonGroup()

    list_structure_name = []
    label = 0
    for column_grp, item in enumerate(list_items):
        if item in dict_subgroups:
            main_panel = QGroupBox(item)

            main_panel.setObjectName('MainPanel')
            main_panel.setStyleSheet("""
                QGroupBox#MainPanel{
                    margin-top : 5px;
                    border : 1px solid rgb(90, 98, 108);
                    font-weight: bold;
                },
                QGroupBox::title#MainPanel{
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                    background-color: transparent;
                }""")


            layout_main_panel = QGridLayout()

            for subindex, subitem in enumerate(dict_subgroups[item]):
                if subitem in dict_sub_subgroups:
                    sub_panel = QGroupBox(subitem)
                    layout_sub_panel = QGridLayout()

                    sub_panel.setObjectName("SubPanel")

                    font = QFont()
                    font.setItalic(True)
                    sub_panel.setFont(font)

                    sub_panel.setStyleSheet("""
                    QGroupBox#SubPanel {
                        border: 1px solid rgb(90, 98, 108);
                        margin-top: 0.5em;
                        color: rgb(90, 98, 108);
                        font-weight: normal;
                    },
                    QGroupBox::title#SubPanel {
                        top: -6px;
                        left: 10px;
                    }""")


                    for sub_subindex, sub_subitem in enumerate(dict_sub_subgroups[subitem]):
                        button = QRadioButton(sub_subitem)
                        button.setVisible(visibility)
                        button.setMinimumWidth(minimum_width)

                        font = QFont()
                        font.setItalic(False)
                        button.setFont(font)

                        button.setStyleSheet("color: rgb(240, 241, 242);")

                        # button.setStyleSheet(
                        #     """QRadioButton::indicator{
                        #         background-color: yellow;
                        #     }""")

                        group_button.addButton(button, label + 1)
                        layout_sub_panel.addWidget(button, sub_subindex, 0)

                        list_structure_name.append(sub_subitem)

                        label = label + 1

                    sub_panel.setLayout(layout_sub_panel)

                    layout_main_panel.addWidget(sub_panel, subindex, 0)

                else:
                    button = QRadioButton(subitem)
                    button.setVisible(visibility)
                    button.setMinimumWidth(minimum_width)
                    button.setStyleSheet("font-weight: normal;")

                    group_button.addButton(button, label + 1)
                    layout_main_panel.addWidget(button, subindex, 0)

                    list_structure_name.append(subitem)

                    label = label + 1

            main_panel.setLayout(layout_main_panel)
            layout.addWidget(main_panel, 0, column + column_grp)

    nbr_buttons = label
    radio_button_to_check = group_button.button(nbr_buttons)
    radio_button_to_check.setChecked(True)

    group_button.buttonClicked.connect(callback_function)

    return group_button, nbr_buttons, list_structure_name

def add_label(text, layout, row, column, column_span=1, visibility=False, minimum_width=0):
    """
    Create a QLabel and add it to the corresponding layout

    Parameters
    ----------
    text : str
        text to display in the widget
    layout : QVBoxLayout TODO TOCHECK
        layout containing the widget
    row : int
        row of the widget in the grid
    column : int
        column of the widget in the grid
    column_span : int
        column span of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget

    Returns
    ----------
    out : QLabel

    """
    label = QLabel(text)
    label.setVisible(visibility)
    label.setMinimumWidth(minimum_width)
    layout.addWidget(label, row, column, 1, column_span)

    return label

def add_combobox(layout, items, callback_function, row, column, column_span=1, visibility=False):
    """
    Create a QComboBox and add it to the corresponding layout

    Parameters
    ----------
    layout : QVBoxLayout TODO TOCHECK
        layout containing the widget
    items : List[str]
        TODO
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget in the grid
    column : int
        column of the widget in the grid
    column_span : int
        column span of the widget in the grid
    visibility : bool
        visibility status of the widget

    Returns
    ----------
    out : QComboBox

    """
    
    combobox = QComboBox()
    # combobox.setVisible(visibility)
    combobox.addItems(items)
    combobox.setCurrentIndex(0)
    combobox.currentIndexChanged.connect(callback_function)
    # combobox.activated[str].connect(callback_function)

    layout.addWidget(combobox, row, column, 1, column_span)
    return combobox

def add_slider(layout, bounds , callback_function, row, column, column_span=1, visibility=False, minimum_width=0, isBoxLayout=False):
    """
    Create a QSlider and add it to the corresponding layout

    Parameters
    ----------
    layout : QVBoxLayout TODO TOCHECK
        layout containing the widget
    bounds : Tuple[int, int]
        lower and upped bounds of the slider
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget in the grid
    column : int
        column of the widget in the grid
    column_span : int
        column span of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    isBoxLayout : bool
        status of the layout : true if the layout is a QGridLayout, false if not

    Returns
    ----------
    out : QSlider

    """
    slider = QSlider(orientation=QtCore.Qt.Horizontal)
    slider.setVisible(visibility)
    slider.setMinimum(bounds[0])
    slider.setMaximum(bounds[1])
    slider.setSingleStep(1)
    slider.setValue(round((bounds[1] - bounds[0])/2))

    # slider.setMinimumWidth(minimum_width)

    if isBoxLayout:
        layout.addWidget(slider, column)
    else:
        layout.addWidget(slider, row, column, 1, column_span)

    slider.valueChanged[int].connect(callback_function)

    return slider


# ============ Display warning box ============
def display_warning_box(widget, title, message):
    """
    Display a warning message in a pop up window

    Parameters
    ----------
    widget : QWidget
        parent widget
    title : str
        title of the pop up window
    message : str
        text to display
    """
    QMessageBox.warning(
        widget,
        title,
        message,
    )

def display_save_message_box(title, message):
    """
    Display a message in a pop up window and ask the user about the different saving mode (all or independently)

    Parameters
    ----------
    title : str
        title of the pop up window
    message : str
        text to display

    Returns
    ----------
    choice : bool
        answer to the question. True if "all", False if "Independently"
    """

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Question)

    all_button = msg_box.addButton('All', QMessageBox.YesRole)
    independent_button = msg_box.addButton('Independently', QMessageBox.NoRole)

    msg_box.exec_()

    if msg_box.clickedButton() == all_button:
        return True
    elif msg_box.clickedButton() == independent_button:
        return False

def display_ok_cancel_question_box(title, message):
    """
    Display a message in a pop up window to confirm or cancel an action

    Parameters
    ----------
    title : str
        title of the pop up window
    message : str
        text to display

    Returns
    ----------
    choice : bool
        answer to the question
    """

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    msg_box.addButton(QMessageBox.Ok)
    msg_box.addButton(QMessageBox.Cancel)

    message_reply = msg_box.exec_()

    if message_reply == QMessageBox.Ok:
        return True
    else:
        return False