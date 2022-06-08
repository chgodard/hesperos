# ============ Import python packages ============
import functools
from qtpy import QtCore
from qtpy.QtTest import QTest
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
    QTextEdit
)
from qtpy.QtGui import QPixmap, QFont
from pathlib import Path, PurePath


from hesperos.layout.napari_elements import label_colors


# ============ Functions to add custom QWidgets ============
def add_combo_box(list_items, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0):
    """
    Create a QComboBox and add it to the corresponding layout

    Parameters
    ----------
    list_items : List[str]
        list of item to display
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when changing selected item in the combobox
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
    out : QComboBox

    """
    
    combo_box = QComboBox()
    # combo_box.setVisible(visibility)
    combo_box.addItems(list_items)
    combo_box.setCurrentIndex(0)

    combo_box.setMinimumWidth(minimum_width)
    layout.addWidget(combo_box, row, column, 1, column_span)
    combo_box.currentIndexChanged.connect(callback_function)
    # combo_box.activated[str].connect(callback_function)

    return combo_box

def add_check_box(text, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0):
    """
    Create a QCheckBox and add it to the corresponding layout

    Parameters
    ----------
    text : str
        text to be displayed
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when changing the state of the box
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
    out : QCheckBox

    """

    check_box = QCheckBox(text)
    check_box.setVisible(visibility)

    check_box.setMinimumWidth(minimum_width)
    layout.addWidget(check_box, row, column, 1, column_span)
    check_box.stateChanged.connect(callback_function)

    return check_box

def add_icon_push_button(icon, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0, isHBoxLayout=False):
    """
    Create a QPushButton with only a icon image (no text) and add it to the corresponding layout

    Parameters
    ----------
    icon : QIcon
        icon of the widget
    layout : QGridLayout or QHBoxLayout
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget (used if the layout is a QGridLayout)
    column : int
        column of the widget in the layout
    column_span : int
        column span of the widget (used if the layout is a QGridLayout)
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    isHBoxLayout : bool
        status of the layout : true if the layout is a QHBoxLayout, false if not

    Returns
    ----------
    out : QPushButton

    """

    button = QPushButton(icon, "")
    button.setVisible(visibility)

    button.setFixedSize(25, 25)
    button.setIconSize(QtCore.QSize(20,20))
    button.setStyleSheet("QPushButton {text-align: center;}")

    if isHBoxLayout:
        layout.addWidget(button, column)
    else:
        layout.addWidget(button, row, column, 1, column_span)
    button.clicked.connect(callback_function)

    return button

def add_icon_text_push_button(icon, text, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0, isHBoxLayout=False):
    """
    Create a QPushButton with only a icon image (no text) and add it to the corresponding layout

    Parameters
    ----------
    icon : QIcon
        icon of the widget
    text : str
        text to be displayed
    layout : QGridLayout or QHBoxLayout
        layout containing the widget
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget (used if the layout is a QGridLayout)
    column : int
        column of the widget in the layout
    column_span : int
        column span of the widget (used if the layout is a QGridLayout)
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    isHBoxLayout : bool
        status of the layout : true if the layout is a QHBoxLayout, false if not

    Returns
    ----------
    out : QPushButton

    """

    button = QPushButton(icon, text)
    button.setVisible(visibility)

    button.setIconSize(QtCore.QSize(20,20))
    button.setStyleSheet("QPushButton {text-align: center;}")

    if isHBoxLayout:
        layout.addWidget(button, column)
    else:
        layout.addWidget(button, row, column, 1, column_span)
    button.clicked.connect(callback_function)

    return button

def add_image_widget(name, layout, image_path, row, column, column_span=1, visibility=False, minimum_width=0):
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
    label = QLabel(name)
    pixmap = QPixmap(image_path)
    label.setPixmap(pixmap)

    label.setVisible(visibility)
    label.setMinimumWidth(minimum_width)
    layout.addWidget(label, row, column, 1, column_span)

    return label

def add_label(text, layout, row, column, column_span=1, visibility=False, minimum_width=0):
    """
    Create a QLabel and add it to the corresponding layout

    Parameters
    ----------
    text : str
        text to display in the widget
    layout : QGridLayout
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

def add_push_button(name, layout, callback_function, row, column, column_span=1, visibility=False, minimum_width=0):
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
        column of the widget in the grid
    column_span : int
        column span of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget

    Returns
    ----------
    out : QPushButton

    """

    button = QPushButton(name)
    button.setVisible(visibility)

    button.setMinimumWidth(minimum_width)
    layout.addWidget(button, row, column, 1, column_span)
    button.clicked.connect(callback_function)

    return button

def add_text_edit(text, layout, row, column, column_span=1, visibility=False, minimum_width=0):
    """
    Create a QTextEdit and add it to the corresponding layout

    Parameters
    ----------
    text : str
        text to display in the widget
    layout : QGridLayout
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
    out : QTextEdit

    """
    text_edit = QTextEdit(text)
    text_edit.setVisible(visibility)
    text_edit.setMinimumWidth(minimum_width)
    layout.addWidget(text_edit, row, column, 1, column_span)

    return text_edit

def add_slider(layout, bounds , callback_function, row, column, column_span=1, visibility=False, minimum_width=0, isHBoxLayout=False):
    """
    Create a QSlider and add it to the corresponding layout

    Parameters
    ----------
    layout : QGridLayout or QHBoxLayout
        layout containing the widget
    bounds : Tuple[int, int]
        lower and upped bounds of the slider
    callback_function : func
        function to call when clicking on the push button
    row : int
        row of the widget (used if the layout is a QGridLayout)
    column : int
        column of the widget in the layout
    column_span : int
        column span of the widget (used if the layout is a QGridLayout)
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    isHBoxLayout : bool
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

    # slider.setMinimumWidth(minimum_width)

    if isHBoxLayout:
        layout.addWidget(slider, column)
    else:
        layout.addWidget(slider, row, column, 1, column_span)

    slider.valueChanged[int].connect(callback_function)

    return slider


# ============ Functions to add custom radio buttons subgroups ============
def add_group_radio_button(list_items, layout, callback_function, row=0, column=0, visibility=False, minimum_width=0):
    """
    Create a QButtonGroup of QRadioButton and add it to the corresponding layout

    Parameters
    ----------
    list_items : list[str]
        list of name of radio buttons to create
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when selecting a radio button
    row : int
        row of the widget in the grid
    column : int
        column of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget

    Returns
    ----------
    button : QButtonGroup

    """
    
    group_button = QButtonGroup()

    for label, item in enumerate(list_items):
        button = QRadioButton(item)
        button.setVisible(visibility)

        button.setMinimumWidth(minimum_width)

        group_button.addButton(button, label + 1)
        layout.addWidget(button, label, column)

    radio_button_to_check = group_button.button(label + 1)
    radio_button_to_check.setChecked(True)

    nbr_buttons = label + 1

    group_button.buttonClicked.connect(callback_function)

    return group_button

def add_sub_subgroup_radio_button(list_items, layout, callback_function, row=0, column=0, visibility=False, minimum_width=0, dict_subgroups={}, dict_sub_subgroups={}):
    """
    Create a QButtonGroup with sub groups of QRadioButton and add it to the corresponding layout

    Parameters
    ----------
    list_items: list[str]
        list of the main groups of radio buttons
    layout : QGridLayout
        layout containing the widget
    callback_function : func
        function to call when selecting a radio button
    row : int
        row of the widget in the grid
    column : int
        column of the widget in the grid
    visibility : bool
        visibility status of the widget
    minimum_width : int
        minimum width of the widget
    dict_subgroups : dict[str, str]
        dictionnary of subgroups of main groups (name of radio buttons)
    dict_sub_subgroups : dict[str, str]
        dictionnary of sub-subgroups of subgroups (name of radio buttons)

    Returns
    ----------
    button : QButtonGroup
        widget created
    list_button_name : List[str]
        list of name of all QRadioButtons in the QButtonGroup
    list_button_in_subgroups : list[QRadioButtons]
        list of QRadioButtons in subgroup

    """    
    group_button = QButtonGroup()

    list_button_name = []
    list_button_in_subgroups = []
    list_sub_panel = []
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
            layout_main_panel.setAlignment(QtCore.Qt.AlignTop)
           
            for subindex, subitem in enumerate(dict_subgroups[item]):
                if subitem in dict_sub_subgroups:
                    sub_panel = QGroupBox(subitem)
                    sub_panel.setCheckable(True)
                    layout_sub_panel = QGridLayout()
                    layout_sub_panel.setAlignment(QtCore.Qt.AlignTop)

                    sub_panel.setObjectName("SubPanel")

                    font = QFont()
                    font.setItalic(True)
                    sub_panel.setFont(font)

                    style_sheet_path = Path(__file__).parent.parent.joinpath('resources', 'group_box_stylesheet.qss')
                    sub_panel.setStyleSheet(open(str(style_sheet_path)).read())

                    for sub_subindex, sub_subitem in enumerate(dict_sub_subgroups[subitem]):
                        button = QRadioButton(sub_subitem)
                        button.setMinimumWidth(minimum_width)

                        font = QFont()
                        font.setItalic(False)
                        button.setFont(font)

                        # button.setStyleSheet("color: rgb(240, 241, 242);")

                        # button.setStyleSheet(
                            # """QRadioButton::indicator{{
                            #     background-color: {};
                            # }}""".format(label_colors))

                        group_button.addButton(button, label + 1)
                        layout_sub_panel.addWidget(button, sub_subindex, 0)

                        list_button_name.append(sub_subitem)
                        list_button_in_subgroups.append(button)

                        label = label + 1

                    sub_panel.setLayout(layout_sub_panel)

                    layout_main_panel.addWidget(sub_panel, subindex, 0)

                    list_sub_panel.append(sub_panel)
                   
                else:
                    button = QRadioButton(subitem)
                    button.setVisible(visibility)
                    button.setMinimumWidth(minimum_width)
                    button.setStyleSheet("font-weight: normal;")

                    group_button.addButton(button, label + 1)
                    layout_main_panel.addWidget(button, subindex, 0)

                    list_button_name.append(subitem)

                    label = label + 1

            main_panel.setLayout(layout_main_panel)
            layout.addWidget(main_panel, row, column + column_grp)

    nbr_buttons = label
    radio_button_to_check = group_button.button(nbr_buttons)
    radio_button_to_check.setChecked(True)

    group_button.buttonClicked.connect(callback_function)

    for index, group_box in enumerate(list_sub_panel):
        group_box.toggled.connect(functools.partial(toggle_group_box, list_sub_panel, index))  
        group_box.setChecked(False) 

    return group_button, list_button_name, list_button_in_subgroups

def toggle_group_box(list_sub_panel, index):
    """
    Toggle widgets in a QGroupBox if the GroupBox is clicked 

    Parameters
    ----------
    list_sub_panel : list[QGroupBox]
        list of QGroupBox in the sub panel
    index : int
        index of the clicked QGroupBox

    """
    group_box = list_sub_panel[index]

    state = group_box.isChecked()
    for widget in group_box.children():
        if widget.isWidgetType():
            widget.setVisible(state) 


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
    Display a message in a pop up window and ask the user about the different saving mode (Unique or Several)

    Parameters
    ----------
    title : str
        title of the pop up window
    message : str
        text to display

    Returns
    ----------
    choice : bool
        answer to the question. True if "Unique", False if "Several"
    """

    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Question)

    unique_button = msg_box.addButton('Unique', QMessageBox.YesRole)
    several_button = msg_box.addButton('Several', QMessageBox.NoRole)
    msg_box.setDefaultButton(unique_button)

    msg_box.exec_()

    if msg_box.clickedButton() == unique_button:
        return True
    elif msg_box.clickedButton() == several_button:
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

def display_yes_no_question_box(title, message):
    """
    Display a message in a pop up window to confirm or not an action

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

    msg_box.addButton(QMessageBox.Yes)
    msg_box.addButton(QMessageBox.No)

    message_reply = msg_box.exec_()

    if message_reply == QMessageBox.Yes:
        return True
    else:
        return False