# ============ Import python files ============
from hesperos.layout.gui_elements import (
    add_check_box,
    add_combo_box,
    add_icon_push_button,
    add_icon_text_push_button,
    add_image_widget,
    add_label,
    add_push_button,
    add_slider,
    add_spin_box,
    display_warning_box,
    display_save_message_box,
    display_ok_cancel_question_box,
    display_yes_no_question_box
)
from hesperos.layout.napari_elements import (
    disable_napari_buttons,
    disable_layer_widgets,
    reset_dock_widget,
    disable_dock_widget_buttons,
    label_colors,
    disable_napari_change_dim_button)
from hesperos.annotation.structuresubpanel import StructureSubPanel
from hesperos.resources._icons import get_icon_path, get_relative_icon_path

import hesperos.annotation.feta as feta_data
import hesperos.annotation.larva as larva_data
import hesperos.annotation.fetus as fetus_data
import hesperos.annotation.shoulder as shoulder_data
import hesperos.annotation.mouse_embryon as mouse_embryon_data
import hesperos.annotation.shoulder_bones as shoulder_bones_data
import hesperos.annotation.shoulder_deltoid as shoulder_deltoid_data
import hesperos.annotation.shoulder_bone_border as shoulder_bone_border_data


# ============ Import python packages ============
import json
import napari
import functools
import numpy as np
import pandas as pd
import tifffile as tif
import SimpleITK as sitk
from pathlib import Path

from qtpy import QtCore
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QWidget,
    QFileDialog,
    QHBoxLayout,
)


# ============ Define variables ============
COLUMN_WIDTH = 100
if not hasattr(napari, 'DOCK_WIDGETS'):
    napari.DOCK_WIDGETS = []


# ============ Define QWidget Class ============
class ManualSegmentationWidget(QWidget):
    """
    QWidget class for Manual Segmentation in napari

    """
    def __init__(self, napari_viewer):
        """
        Initilialisation of the widget in the current napari viewer

        Parameters
        ----------
        napari_viewer : napari.Viewer
            active (unique) instance of the napari viewer

        """
        reset_dock_widget(napari_viewer)

        super().__init__()

        napari.utils.notifications.WarningNotification.blocked = True
        self.viewer = napari_viewer

        disable_napari_buttons(self.viewer)

        self.generate_main_layout()

        self.viewer.dims.events.current_step.connect(self.update_go_to_selected_slice_push_button_check_status)
        self.viewer.dims.events.current_step.connect(self.update_go_to_selected_oriented_landmark_push_button_check_status)
        self.viewer.dims.events.order.connect(self.update_slice_positon_after_dims_roll)
        self.viewer.dims.events.ndisplay.connect(self.set_button_interactivity)

        napari.DOCK_WIDGETS.append(self)
        # disable_dock_widget_buttons(self.viewer)


# ============ Define Layout ============
    def generate_main_layout(self):
        """
        Generate the main layout of the widget

        """

        # === Set layout parameters ===
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(5)

        # === Create and add panels to the layout ===
        self.add_import_panel(1)
        self.add_manage_oriented_landmarks_panel(2)
        self.add_annotation_panel(3)
        self.add_sub_annotation_panel(4)
        self.add_slice_selection_panel(5)
        self.add_reset_export_panel(6)

        # Display status (cannot display progressing bar because napari is freezing)
        self.status_label = add_label(
            text='Ready',
            layout=self.layout,
            row=7,
            column=0,
            visibility=True
            )

        self.toggle_panels(["manage_oriented_landmarks_panel", "annotation_panel", "slice_selection_panel", "reset_export_panel"], False)

        self.setLayout(self.layout)

    def add_sub_annotation_panel(self, row):
        """
        Create annotation sub panel with the list of all struture to annotate

        Parameters
        ----------
        row : int
            row position of the sub panel in the main QGridLayout

        """
        self.feta = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=feta_data.LIST_STRUCTURES,
            dict_substructures=feta_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.fetus = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=fetus_data.LIST_STRUCTURES,
            dict_substructures=fetus_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.shoulder = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=shoulder_data.LIST_STRUCTURES,
            dict_substructures=shoulder_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=shoulder_data.DICT_SUB_SUB_STRUCTURES)

        self.shoulder_bones = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=shoulder_bones_data.LIST_STRUCTURES,
            dict_substructures=shoulder_bones_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.shoulder_bone_borders = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=shoulder_bone_border_data.LIST_STRUCTURES,
            dict_substructures=shoulder_bone_border_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.shoulder_deltoid = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=shoulder_deltoid_data.LIST_STRUCTURES,
            dict_substructures=shoulder_deltoid_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.larva = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=larva_data.LIST_STRUCTURES,
            dict_substructures=larva_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.mouse_embryon = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=mouse_embryon_data.LIST_STRUCTURES,
            dict_substructures=mouse_embryon_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

    def add_import_panel(self, row, column=0):
        """
        Create import panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """
        # === Set panel parameters ===
        self.import_panel = QGroupBox("1. IMPORT IMAGE")
        self.import_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.import_layout = QGridLayout()
        self.import_layout.setContentsMargins(10, 10, 10, 10)
        self.import_layout.setSpacing(5)
        self.import_layout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the panel layout ===
        self.import_dicom_image_push_button = add_push_button(
            name="Open DICOM serie",
            layout=self.import_layout,
            callback_function=functools.partial(self.set_image_with_path, "folder"),
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Import DICOM data from a folder containing one serie.",
        )

        self.import_file_image_push_button = add_push_button(
            name="Open image file",
            layout=self.import_layout,
            callback_function=functools.partial(self.set_image_with_path, "file"),
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Import image data from one file.",
        )

        self.file_name_text = add_label(
            text='File/Folder name: ',
            layout=self.import_layout,
            row=1,
            column=0,
            minimum_width=COLUMN_WIDTH,
            )

        self.file_name_label = add_label(
            text='',
            layout=self.import_layout,
            row=1,
            column=1,
            minimum_width=COLUMN_WIDTH,
            )

        self.zoom_slider = add_slider(
            layout=self.import_layout,
            bounds=[50, 500],
            callback_function=self.zoom,
            row=2,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Zoom the main camera.",
        )
        self.zoom_slider.setStyleSheet("""
            QSlider::handle:horizontal {{
                image: url({});
                margin: -30px 0px;
                width: 25px;
                background: transparent;
                }}""".format(get_relative_icon_path('zoom')))

        # Import tools are created in another layout
        self.tool_import_layout = QHBoxLayout()

        self.set_custom_contrast_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('plus')),
            layout=self.tool_import_layout,
            callback_function=self.set_custom_contrast,
            row=0,
            column=0,
            tooltip_text="Add custom contrast limit setting. Open it by selecting the Custom Contrast choice.",
            isHBoxLayout=True,
        )
        self.custom_contrast_limits = None
        self.hu_limits = []

        self.import_custom_contrast_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('import')),
            layout=self.tool_import_layout,
            callback_function=self.import_custom_contrast,
            row=0,
            column=1,
            tooltip_text="Import custom contrast limit setting from a .json file.",
            isHBoxLayout=True,
        )

        self.export_custom_contrast_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('export')),
            layout=self.tool_import_layout,
            callback_function=self.export_custom_contrast,
            row=0,
            column=2,
            tooltip_text="Export custom contrast limit setting as .json file.",
            isHBoxLayout=True,
        )

        self.default_contrast_combo_box = add_combo_box(
            list_items=["Set a default contrast", "CT Bone", "CT Soft", "Custom Contrast"],
            layout=self.tool_import_layout,
            callback_function=self.set_default_contrast,
            row=0,
            column=3,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Use a predefined HU contrast.",
            isHBoxLayout=True,
        )

        self.import_layout.addLayout(self.tool_import_layout, 3, 0, 1, 2)

        self.import_panel.setLayout(self.import_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.import_panel, row, column)

        # === Make widgets visible (after adding to the main layout to preventing them from briefly appearing in a separate window) ===
        self.import_panel.setVisible(True)
        self.import_dicom_image_push_button.setVisible(True)
        self.import_file_image_push_button.setVisible(True)

        self.toggle_import_panel_widget(False)

    def add_manage_oriented_landmarks_panel(self, row, column=0):
        """
        Create manage oriented landmarks panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """
        # === Set panel parameters ===
        self.manage_oriented_landmarks_panel = QGroupBox("2. MANAGE ORIENTED LANDMARKS FOR DIVA")
        self.manage_oriented_landmarks_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.manage_oriented_landmarks_layout = QGridLayout()
        self.manage_oriented_landmarks_layout.setContentsMargins(10, 10, 10, 10)
        self.manage_oriented_landmarks_layout.setSpacing(5)
        self.manage_oriented_landmarks_layout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the panel layout ===
        self.import_oriented_landmarks_push_button = add_push_button(
            name="Open landmarks file",
            layout=self.manage_oriented_landmarks_layout,
            callback_function=self.set_oriented_landmarks_with_path,
            row=0,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Import the oriented landmarks from the DIVA software.",
        )

        # Oriented landmarks tools are created in another layout
        self.tool_oriented_landmarks_layout = QHBoxLayout()

        self.add_oriented_landmark_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('plus')),
            layout=self.tool_oriented_landmarks_layout,
            callback_function=self.update_landmarks_layer_mode,
            row=0,
            column=0,
            tooltip_text="When checked, click on the image to add a landmark, uncheck it to disable.",
            isHBoxLayout=True,
        )
        self.add_oriented_landmark_push_button.setCheckable(True)

        self.remove_oriented_landmark_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('minus')),
            layout=self.tool_oriented_landmarks_layout,
            callback_function=self.remove_oriented_landmark,
            row=0,
            column=1,
            tooltip_text="Remove the currently selected landmark in the drop-down menu.",
            isHBoxLayout=True,
        )

        self.go_to_selected_oriented_landmark_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('map')),
            layout=self.tool_oriented_landmarks_layout,
            callback_function=self.go_to_oriented_landmark,
            row=0,
            column=2,
            tooltip_text="Go to the landmark position selected in the drop-down menu.",
            isHBoxLayout=True,
        )
        self.go_to_selected_oriented_landmark_push_button.setCheckable(True)

        self.landmark_ID_text = add_label(
            text='Landmark ID: ',
            layout=self.tool_oriented_landmarks_layout,
            row=0,
            column=3,
            isHBoxLayout=True,
            isResizingWithTextSize=True,
        )

        self.manage_oriented_landmarks_layout.addLayout(self.tool_oriented_landmarks_layout, 1 , 0)

        self.selected_oriented_landmark_combo_box = add_combo_box(
            list_items=[" "],
            layout=self.manage_oriented_landmarks_layout,
            callback_function=self.go_to_oriented_landmark,
            row=1,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Select a landmark index from the list to visualize it more easily.",
        )
        
        self.export_oriented_landmarks_push_button = add_push_button(
            name="Export landmarks file",
            layout=self.manage_oriented_landmarks_layout,
            callback_function=self.export_oriented_landmarks,
            row=2,
            column=0,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Export the oriented landmarks to be opened in the DIVA sofware.",
        )
        
        self.reset_oriented_landmarks_push_button = add_push_button(
            name="Delete landmarks",
            layout=self.manage_oriented_landmarks_layout,
            callback_function=self.reset_oriented_landmark,
            row=2,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Delete all landmarks.",
        )

        self.manage_oriented_landmarks_panel.setLayout(self.manage_oriented_landmarks_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.manage_oriented_landmarks_panel, row, column)

    def add_annotation_panel(self, row, column=0):
        """
        Create annotation panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """
        # === Set panel parameters ===
        self.annotation_panel = QGroupBox("3. ANNOTATE")
        self.annotation_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.annotation_layout = QGridLayout()
        self.annotation_layout.setContentsMargins(10, 10, 10, 10)
        self.annotation_layout.setSpacing(5)
        self.annotation_layout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the panel layout ===
        self.import_segmentation_push_button = add_push_button(
            name="Open segmentation file",
            layout=self.annotation_layout,
            callback_function=lambda: self.set_segmentation_with_path(None),
            row=0,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Open a segmentation file with the same size of the original image.",
        )

        # Annotations tools are created in another layout
        self.tool_annotation_layout = QHBoxLayout()

        self.undo_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('undo')),
            layout=self.tool_annotation_layout,
            callback_function=self.undo_segmentation,
            row=0,
            column=0,
            tooltip_text="Undo the last painting action.",
            isHBoxLayout=True,
        )

        self.lock_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('unlock')),
            layout=self.tool_annotation_layout,
            callback_function=self.lock_slide,
            row=0,
            column=1,
            tooltip_text="Lock a slice of work. Click on the checked button to go to the locked slice.",
            isHBoxLayout=True,
        )
        self.lock_push_button.setCheckable(True)

        self.annotation_layout.addLayout(self.tool_annotation_layout, 1, 0)

        self.annotation_combo_box = add_combo_box(
            list_items=["Choose a structure", "Feta Challenge", "Fetus", "Larva", "Mouse Embryon", "Shoulder", "Shoulder Bones", "Shoulder Bone Borders", "Shoulder Deltoid"],
            layout=self.annotation_layout,
            callback_function=self.toggle_annotation_sub_panel,
            row=1,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Select the pre-defined structure to annotate.",
        )

        self.annotation_panel.setLayout(self.annotation_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.annotation_panel, row, column)

    def add_reset_export_panel(self, row, column=0):
        """
        Create reset and export panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """
        # === Set panel parameters ===
        self.reset_export_panel = QGroupBox("5. EXPORT ANNOTATION")
        self.reset_export_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.reset_export_layout = QGridLayout()
        self.reset_export_layout.setSpacing(5)

        # === Add Qwidgets to the panel layout ===
        self.export_push_button = add_push_button(
            name="Export",
            layout=self.reset_export_layout,
            callback_function=self.export_segmentation,
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Export only the segmented data.",
        )

        self.reset_push_button = add_push_button(
            name="Delete all",
            layout=self.reset_export_layout,
            callback_function=self.reset_segmentation,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Delete all segmentation data.",
        )

        self.backup_check_box = add_check_box(
            text="Automatic segmentation backup",
            layout=self.reset_export_layout,
            callback_function=self.activate_backup_segmentation,
            row=1,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Activate the automatic backup of the segmentation data when the slice inex is changed.",
        )
        self.backup_check_box.setChecked(False)

        self.reset_export_panel.setLayout(self.reset_export_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.reset_export_panel, row, column)

    def add_slice_selection_panel(self, row, column=0):
        """
        Create slice selection panel (for ShoulderBones, ShoulderDeltoid and Larva categories only)

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """
        # === Set panel parameters ===
        self.slice_selection_panel = QGroupBox("4. SELECT SLICES OF INTEREST")
        self.slice_selection_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.slice_selection_layout = QGridLayout()
        self.slice_selection_layout.setContentsMargins(10, 10, 10, 10)
        self.slice_selection_layout.setSpacing(5)
        self.slice_selection_layout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the panel layout ===

        # Slice selection tools are created in another layout
        self.tool_slice_selection_layout = QHBoxLayout()

        self.add_selected_slice_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('plus')),
            layout=self.tool_slice_selection_layout,
            callback_function=self.add_selected_slice,
            row=0,
            column=0,
            tooltip_text="Add the currently displayed slice index in the drop-down menu. Click on the map button to go to the selected slice.",
            isHBoxLayout=True,
        )

        self.remove_selected_slice_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('minus')),
            layout=self.tool_slice_selection_layout,
            callback_function=self.remove_selected_slice,
            row=0,
            column=1,
            tooltip_text="Remove the currently displayed slice index in the drop-down menu.",
            isHBoxLayout=True,
        )

        self.go_to_selected_slice_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('map')),
            layout=self.tool_slice_selection_layout,
            callback_function=self.go_to_selected_slice,
            row=0,
            column=2,
            tooltip_text="Go to the slice index selected in the drop-down menu.",
            isHBoxLayout=True,
        )
        self.go_to_selected_slice_push_button.setCheckable(True)

        self.slice_selection_text = add_label(
            text='Slice ID: ',
            layout=self.tool_slice_selection_layout,
            row=0,
            column=3,
            isHBoxLayout=True,
            isResizingWithTextSize=True,
            )

        self.slice_selection_layout.addLayout(self.tool_slice_selection_layout, 0, 0)

        self.selected_slice_combo_box = add_combo_box(
            list_items=[" "],
            layout=self.slice_selection_layout,
            callback_function=self.go_to_selected_slice,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Select a slice index from the list to work with it more easily.",
        )

        # Slice selection tools are created in another layout
        self.step_range_text = add_label(
            text='Step slices range: ',
            layout=self.slice_selection_layout,
            row=1,
            column=0,
            isResizingWithTextSize=True,
        )

        self.tool2_slice_selection_layout = QHBoxLayout()

        self.go_left_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('back')),
            layout=self.tool2_slice_selection_layout,
            callback_function=self.go_left_step_slices,
            row=0,
            column=0,
            tooltip_text="Move backward in the displayed axe acording to the step range.",
            isHBoxLayout=True,
        )

        self.step_range_spin_box = add_spin_box(
            layout=self.tool2_slice_selection_layout,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Define the step range.",
            isHBoxLayout=True,
        )

        self.go_right_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('next')),
            layout=self.tool2_slice_selection_layout,
            callback_function=self.go_right_step_slices,
            row=0,
            column=2,
            tooltip_text="Move forward in the displayed axe acording to the step range.",
            isHBoxLayout=True,
        )

        self.slice_selection_layout.addLayout(self.tool2_slice_selection_layout, 1, 1)

        self.slice_selection_panel.setLayout(self.slice_selection_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.slice_selection_panel, row, column)


# ============ Toggle widgets and panel ============
    def toggle_annotation_sub_panel(self):
        """
            Toggle sub panel of the structure to annotate and toggle SliceSelection panel if "Shoulder Bones" or "Shoulder Deltoid" or "Feta" is visible

        """
        structure_name = self.annotation_combo_box.currentText()

        if structure_name == "Fetus":
            toggle_feta = False
            toggle_fetus = True
            toggle_shoulder = False
            toggle_larva = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = True
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder Bones":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = True
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder Bone Borders":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = True
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder Deltoid":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = True
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Feta Challenge":
            toggle_feta = True
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Larva":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = True
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        elif structure_name == "Mouse Embryon":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = True

        else:
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_mouse_embryon = False

        # === Toggle sub panels ===
        self.feta.toggle_sub_panel(toggle_feta)
        self.larva.toggle_sub_panel(toggle_larva)
        self.fetus.toggle_sub_panel(toggle_fetus)
        self.shoulder.toggle_sub_panel(toggle_shoulder)
        self.mouse_embryon.toggle_sub_panel(toggle_mouse_embryon)
        self.shoulder_bones.toggle_sub_panel(toggle_shoulder_bones)
        self.shoulder_deltoid.toggle_sub_panel(toggle_shoulder_deltoid)
        self.shoulder_bone_borders.toggle_sub_panel(toggle_shoulder_bone_borders)

        # === Reset widgets ===
        self.reset_annotation_radio_button_checked_id()
        self.reset_annotation_layer_selected_label()

    def toggle_import_panel_widget(self, isVisible, file_type=None):
        """
        Toggle widget or the import panel (default contrast option only for DICOM image (use housfield value))

        Parameters
        ----------
        isVisible : bool
            visible status of the widgets
        file_type : str
            type of image loaded : "file" for .tiff, .tif, .nii and .nii.gz and "folder" for DICOM folder

        """
        self.file_name_text.setVisible(isVisible)
        self.file_name_label.setVisible(isVisible)
        self.zoom_slider.setVisible(isVisible)

        if file_type == "file":
            self.set_custom_contrast_push_button.setVisible(False)
            self.import_custom_contrast_push_button.setVisible(False)
            self.export_custom_contrast_push_button.setVisible(False)
            self.default_contrast_combo_box.setVisible(False)

        elif file_type == 'folder':
            self.set_custom_contrast_push_button.setVisible(True)
            self.import_custom_contrast_push_button.setVisible(True)
            self.export_custom_contrast_push_button.setVisible(True)
            self.default_contrast_combo_box.setVisible(True)

        else:
            self.set_custom_contrast_push_button.setVisible(isVisible)
            self.import_custom_contrast_push_button.setVisible(isVisible)
            self.export_custom_contrast_push_button.setVisible(isVisible)
            self.default_contrast_combo_box.setVisible(isVisible)

    def toggle_panels(self, list_panel_names, isVisible):
        """
        Make visible panels

        Parameters
        ----------
        list_panel_names : List[str]
            list of the name of the panels to enable
        isVisible : bool
            visible status of the panels

        """
        for panel_name in list_panel_names:
            if panel_name == "annotation_panel":
                self.annotation_panel.setVisible(isVisible)
                self.import_segmentation_push_button.setVisible(isVisible)
                self.undo_push_button.setVisible(isVisible)
                self.lock_push_button.setVisible(isVisible)
                self.annotation_combo_box.setVisible(isVisible)

            elif panel_name == "manage_oriented_landmarks_panel":
                self.manage_oriented_landmarks_panel.setVisible(isVisible)
                self.import_oriented_landmarks_push_button.setVisible(isVisible)
                self.add_oriented_landmark_push_button.setVisible(isVisible)
                self.remove_oriented_landmark_push_button.setVisible(isVisible)
                self.go_to_selected_oriented_landmark_push_button.setVisible(isVisible)
                self.landmark_ID_text.setVisible(isVisible)
                self.selected_oriented_landmark_combo_box.setVisible(isVisible)
                self.export_oriented_landmarks_push_button.setVisible(isVisible)
                self.reset_oriented_landmarks_push_button.setVisible(isVisible)

            elif panel_name == "slice_selection_panel":
                self.slice_selection_panel.setVisible(isVisible)
                self.add_selected_slice_push_button.setVisible(isVisible)
                self.remove_selected_slice_push_button.setVisible(isVisible)
                self.go_to_selected_slice_push_button.setVisible(isVisible)
                self.slice_selection_text.setVisible(isVisible)
                self.selected_slice_combo_box.setVisible(isVisible)
                self.step_range_text.setVisible(isVisible)
                self.go_left_push_button.setVisible(isVisible)
                self.step_range_spin_box.setVisible(isVisible)
                self.go_right_push_button.setVisible(isVisible)

            elif panel_name == "reset_export_panel":
                self.reset_export_panel.setVisible(isVisible)
                self.reset_push_button.setVisible(isVisible)
                self.export_push_button.setVisible(isVisible)
                self.backup_check_box.setVisible(isVisible)

    def enable_widgets(self, isEnable):
        """
        Enable widgets which interact with the 2D view

        Parameters
        ----------
         isEnable : bool
            enable status of the widgets

        """
        self.import_oriented_landmarks_push_button.setEnabled(isEnable)
        self.add_oriented_landmark_push_button.setEnabled(isEnable)
        self.remove_oriented_landmark_push_button.setEnabled(isEnable)
        self.go_to_selected_oriented_landmark_push_button.setEnabled(isEnable)
        self.selected_oriented_landmark_combo_box.setEnabled(isEnable)

        self.add_selected_slice_push_button.setEnabled(isEnable)
        self.remove_selected_slice_push_button.setEnabled(isEnable)
        self.go_to_selected_slice_push_button.setEnabled(isEnable)
        self.selected_slice_combo_box.setEnabled(isEnable)
        self.go_left_push_button.setEnabled(isEnable)
        self.step_range_spin_box.setEnabled(isEnable)
        self.go_right_push_button.setEnabled(isEnable)


# ============ Update widget status or panel title ============
    def update_go_to_selected_slice_push_button_check_status(self, event):
        """
        Update the checked status of the go_to_selected_slice push button according to the currently selected slice and the currently displayed slice

        Parameters
        ----------
        event : event
            event with the index of the current slice displayed in value as (x, y, z)

        """
        if len(event.value) == 3:
            axis_order = ['z', 'y', 'x']

            if (self.go_to_selected_slice_push_button.isChecked() == True) and (self.selected_slice_combo_box.currentText() != " "):
                current_axis_index = self.viewer.dims.not_displayed[0]
                current_slice = self.viewer.dims.current_step[current_axis_index]
                selected_slice = int(self.selected_slice_combo_box.currentText()[:-1])
                selected_axis_index = axis_order.index(self.selected_slice_combo_box.currentText()[-1])

                if (current_slice != selected_slice) or (current_axis_index != selected_axis_index):
                    self.go_to_selected_slice_push_button.setChecked(False)

            elif (self.go_to_selected_slice_push_button.isChecked() == False) and (self.selected_slice_combo_box.currentText() != " "):
                current_axis_index = self.viewer.dims.not_displayed[0]
                current_slice = self.viewer.dims.current_step[current_axis_index]
                selected_slice = int(self.selected_slice_combo_box.currentText()[:-1])
                selected_axis_index = axis_order.index(self.selected_slice_combo_box.currentText()[-1])

                if (current_slice == selected_slice) and (current_axis_index == selected_axis_index):
                    self.go_to_selected_slice_push_button.setChecked(True)

    def update_go_to_selected_oriented_landmark_push_button_check_status(self, event):
        """
        Update the checked status of the go_to_selected_oriented_landmark push button according to the currently selected slice and the currently displayed slice

        Parameters
        ----------
        event : event
            event with the index of the current slice displayed in value as (x, y, z)

        """
        if len(event.value) == 3:
            current_axis_index = self.viewer.dims.not_displayed[0]

            if (self.go_to_selected_oriented_landmark_push_button.isChecked() == True) and (self.selected_oriented_landmark_combo_box.currentText() != " "):
                current_slice = self.viewer.dims.current_step[current_axis_index]
                landmark_slice = self.oriented_landmarks_positions_array[int(self.selected_oriented_landmark_combo_box.currentText()) - 1][current_axis_index]

                if current_slice != landmark_slice:
                    self.go_to_selected_oriented_landmark_push_button.setChecked(False)

            elif (self.go_to_selected_oriented_landmark_push_button.isChecked() == False) and (self.selected_oriented_landmark_combo_box.currentText() != " "):
                current_slice = self.viewer.dims.current_step[current_axis_index]
                landmark_slice = self.oriented_landmarks_positions_array[int(self.selected_oriented_landmark_combo_box.currentText()) - 1][current_axis_index]

                if current_slice == landmark_slice:
                    self.go_to_selected_oriented_landmark_push_button.setChecked(True)

    def update_panel_titles(self):
        """
        Update the number in the panel title to match the actual number of panels displayed (based on the OrientedLandmarks and SelectionSlice panels display status)

        """
        isOrientedLandmarksPanelVisible = self.manage_oriented_landmarks_panel.isVisible()
        isSelectionSlicePanelVisible = self.slice_selection_panel.isVisible()

        if isOrientedLandmarksPanelVisible and isSelectionSlicePanelVisible:
            self.annotation_panel.setTitle("3. ANNOTATE")
            self.slice_selection_panel.setTitle("4. SELECT SLICES OF INTEREST")
            self.reset_export_panel.setTitle("5. EXPORT ANNOTATION")

        elif isOrientedLandmarksPanelVisible and (not isSelectionSlicePanelVisible):
            self.annotation_panel.setTitle("3. ANNOTATE")
            self.reset_export_panel.setTitle("4. EXPORT ANNOTATION")

        elif (not isOrientedLandmarksPanelVisible) and isSelectionSlicePanelVisible:
            self.annotation_panel.setTitle("2. ANNOTATE")
            self.slice_selection_panel.setTitle("3. SELECT SLICES OF INTEREST")
            self.reset_export_panel.setTitle("4. EXPORT ANNOTATION")

        elif (not isOrientedLandmarksPanelVisible) and (not isSelectionSlicePanelVisible):
            self.annotation_panel.setTitle("2. ANNOTATE")
            self.reset_export_panel.setTitle("3. EXPORT ANNOTATION")

    def update_reset_export_panel_title(self, isSelectionSlicePanelVisible):
        """
        Update the number in the ResetExport panel title to match the actual number of panels displayed (based on the SelectionSlice panel display)

        Parameters
        ----------
        isSelectionSlicePanelVisible : bool
            visible status of the SelectionSlice panel

        """
        if isSelectionSlicePanelVisible:
            self.reset_export_panel.setTitle("5. EXPORT ANNOTATION")
        else:
            self.reset_export_panel.setTitle("4. EXPORT ANNOTATION")

    def update_selected_oriented_landmark_combo_box(self):
        """
        Fill the selected_oriented_landmark Combo Box with the oriented landmark indexes.

        """
        self.reset_oriented_landmark_combo_box()

        for landmark_index in range(len(self.oriented_landmarks_positions_array)):
            new_text = str(landmark_index + 1)
            self.selected_oriented_landmark_combo_box.addItem(new_text)

    def set_button_interactivity(self, event):
        """
        Change interactivity of some buttons according to the mode of display (2D or 3D view)
        
        """
        if event.value == 3:
            # to prevent bug with 3D visualisation of the "orientations" and "landmarks" layers (i.e. point and vector layers)
            while self.viewer.dims.displayed != (0, 1, 2):
                self.viewer.dims._roll()
            self.enable_widgets(False)
        else:
            self.enable_widgets(True)


# ============ Import image data ============
    def import_dicom_folder(self):
        """
        Import a complete DICOM serie from a folder

        Returns
        ----------
        image_arr : ndarray
            3D image as a 3D array. None if importation failed.

        """
        dicom_path = QFileDialog.getExistingDirectory(self, 'Choose a DICOM serie directory')

        if dicom_path == "":
            return None

        if (Path(dicom_path).name == 'Raw') or (Path(dicom_path).name == 'ST0'):
            self.image_dir = Path(dicom_path).parents[1]
            file_name = Path(dicom_path).parents[0].name
        else:
            self.image_dir = Path(dicom_path).parents[0]
            file_name = Path(dicom_path).name

        reader = sitk.ImageSeriesReader()

        series_found = reader.GetGDCMSeriesIDs(dicom_path)
        if len(series_found) > 1:
            display_warning_box(self, "Error", "More than 1 DICOM serie in the folder. Select a folder containing a single DICOM series.")
            return None

        img_names = reader.GetGDCMSeriesFileNames(dicom_path)
        reader.SetFileNames(img_names)
        try:
            self.image_sitk = reader.Execute()
        except:
            display_warning_box(self, "Error", "NO DICOM data in the folder.")
            return None

        image_arr = sitk.GetArrayFromImage(self.image_sitk) # z, y, x
        #ITK's Image class does not have a bracket operator. It has a GetPixel which takes an ITK Index object as an argument, which is an array ordered as (x,y,z). This is the convention that SimpleITK's Image class uses for the GetPixel method as well.
        # While in numpy, an array is indexed in the opposite order (z,y,x).

        if len(image_arr.shape) != 3:
            display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image.")
            return None

        self.file_name_label.setText(file_name)

        return image_arr

    def import_image_file(self):
        """
        Import a 3D image file of type .tiff, .tif, .nii or .nii.gz

        Returns
        ----------
        image_arr : ndarray
            3D image as a 3D array. None if importation failed.

        """
        files_types = "Image File (*.tif *.tiff *.nii.gz *.nii)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a 3D image file", "" , files_types)

        if file_path == "":
            return None

        extensions = Path(file_path).suffixes
        self.image_dir = Path(file_path).parents[0]

        if (extensions[-1] in [".tif", ".tiff", ".nii"]) or (extensions == [".nii", ".gz"]):
            try:
                self.image_sitk = sitk.ReadImage(file_path)
                image_arr = sitk.GetArrayFromImage(self.image_sitk)
                if len(image_arr.shape) == 2:
                    image_arr = np.expand_dims(image_arr, 0)
            # SimpleITK can not handle images with 64-bits images
            except:
                image_arr = tif.imread(file_path)
                if len(image_arr.shape) == 2:
                    image_arr = np.expand_dims(image_arr, 0)
                self.image_sitk = sitk.Image(image_arr.shape[2], image_arr.shape[1], image_arr.shape[0], sitk.sitkInt16)

            if len(extensions) == 2:
                self.file_name_label.setText(Path(Path(file_path).stem).stem)
            else:
                self.file_name_label.setText(Path(file_path).stem)

        else:
            return None

        if len(image_arr.shape) != 3:
            
            return None

        return image_arr

    def import_segmentation_file(self, default_file_path=None):
        """
        Import segmentation image file of type .tiff, .tif, .nii or .nii.gz

        Parameters
        ----------
        default_file_path : Pathlib.Path
            path of the segmentation image to import. If None, a QFileDialog is open to aks a path.

        Returns
        ----------
        segmentation_arr : ndarray
            segmentation image as a 3D array. None if importation failed.
        segmentation_sitk : SimpleITK image
            segmentation image as SimpleITK image

        """
        if default_file_path is None:
            files_types = "Image File (*.tif *.tiff *.nii.gz *.nii)"
            file_path, _ = QFileDialog.getOpenFileName(self, "Choose a segmentation file", "" , files_types)
            if file_path == "":
                return None, None
        else:
            file_path = str(default_file_path)

        extensions = Path(file_path).suffixes
        if (extensions[-1] in [".tif", ".tiff", ".nii"]) or (extensions == [".nii", ".gz"]):
            try:
                segmentation_sitk = sitk.ReadImage(file_path)
                segmentation_arr = sitk.GetArrayFromImage(segmentation_sitk)
                segmentation_arr = segmentation_arr.astype(np.uint8)
                if len(segmentation_arr.shape) == 2:
                    segmentation_arr = np.expand_dims(segmentation_arr, 0)

            # SimpleITK can not handle images with 64-bits images
            except:
                segmentation_arr = tif.imread(file_path)
                segmentation_arr = segmentation_arr.astype(np.uint8)
                if len(segmentation_arr.shape) == 2:
                    segmentation_arr = np.expand_dims(segmentation_arr, 0)
                segmentation_sitk = sitk.Image(segmentation_arr.shape[2], segmentation_arr.shape[1], segmentation_arr.shape[0], sitk.sitkInt8)

            if any(n < 0 for n in np.unique(segmentation_arr)):
                display_warning_box(self, "Error", "Incorrect NIFTI format : negative value.")
                return None, None

        else:
            return None, None

        if len(segmentation_arr.shape) != 3:
            display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image.")
            return None, None

        if not isinstance(segmentation_arr.flat[0], np.integer):
            segmentation_arr = segmentation_arr.astype(np.int)

        return segmentation_arr, segmentation_sitk

    def has_corresponding_segmentation_file(self):
        """
        Check is there exist a segmentation file (.tiff, .tif, .nii, .nii.gz) matching the name of the open image file.
        The segmentation file name has to be : image_file_name + "_segmentation".

        Returns
        ----------
        hasCorrespondingSegmentation : bool
            True if there exist a segmentation file, False if not.
        segmentation_file_path : Pathlib.Path
            path of the segmentation image to import if there exist a segmentation file, None if not.

        """
        for type_extensions in (".tiff", ".tif", ".nii", ".nii.gz"):
            segmentation_file_path = Path(self.image_dir).joinpath(self.file_name_label.text() + "_segmentation" + type_extensions)
            if segmentation_file_path.exists():
                return True, segmentation_file_path

        return False, ""


# ============ Import metadata ============
    def import_custom_contrast(self):
        """
        Import custom contrast limits from a .json file and apply it

        """
        files_types = "JSON File (*.json)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a JSON image", "" , files_types)

        if file_path == "":
            return None

        self.default_contrast_combo_box.setCurrentText("Set a default contrast")

        with open(file_path) as f:
            import_contrast = json.load(f)

        if (np.max(import_contrast) <= self.viewer.layers['image'].contrast_limits_range[1]) and (np.min(import_contrast) >= self.viewer.layers['image'].contrast_limits_range[0]):
            self.custom_contrast_limits = import_contrast
        else:
            display_warning_box(self, "Error", "The imported contrast limits is outside of the image contrast range.")
            return

        self.default_contrast_combo_box.setCurrentText("Custom Contrast")

    def import_selected_slice(self, segmentation_sitk=None):
        """
        Import metadata containing in the 'ImageDescription'/'Hesperos_SelectedSlices' as a list. (works only for tiff file TODO TOIMPROVE)

        Parameters
        ----------
        segmentation_sitk : SimpleITK image
            segmentation data in sitk format

        """
        try:
            description = json.loads(segmentation_sitk.GetMetaData('ImageDescription'))
            loaded_selected_slice_list = description['Hesperos_SelectedSlices']
            # loaded_selected_slice_list = json.load(description['Hesperos_SelectedSlices'])
        except:
            return
        if loaded_selected_slice_list != []:
            if loaded_selected_slice_list != "[]":
                self.selected_slice_list = loaded_selected_slice_list
                self.selected_slice_list.sort(key=lambda text: int(text[:-1]))

                for slice_index in self.selected_slice_list:
                    new_text = str(slice_index)
                    self.selected_slice_combo_box.addItem(new_text)


# ============ Import data from DIVA ============
    def import_oriented_landmarks_json(self):
        """
        Import landmarks positions and orientations (added in DIVA using Virtual Reality) from a .json file.

        Returns
        ----------
        status : bool
            True if the importation succeed, False if not

        """        
        files_types = "JSON File (*.json)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a oriented landmarks file from DIVA", "" , files_types)

        if file_path == "":
            return False
        

        with open(file_path, 'r') as f:
            oriented_landmarks_data = json.loads(f.read())
        oriented_landmarks_positions_df = pd.json_normalize(oriented_landmarks_data['_oriented_landmarks_parameters'], record_path=['_volume_positions'])
        oriented_landmarks_orientations_df = pd.json_normalize(oriented_landmarks_data['_oriented_landmarks_parameters'], record_path=['_local_rotations'])        
        
        nbr_landmarks = len(oriented_landmarks_positions_df)
        # if nbr_landmarks > 10:
        #     display_warning_box(self, "Error", "More than 10 oriented landmarks are not allowed. Please remove some landmarks in your file.")
        #     return False

        # DIVA volume is ordered as (x, y, z) and z axis is inverted
        # Numpy array is ordered as (z, y, x)
        shape = self.viewer.layers['image'].data.shape # as (x, y, z)

        oriented_landmarks_positions_array = [[] * len(shape) for i in range(nbr_landmarks)]
        oriented_landmarks_orientations_array = [[] * len(shape) for i in range(nbr_landmarks)]
        oriented_landmarks_quaternions_array = [[] * 4 for i in range(nbr_landmarks)]

        if ("x" and "y" and "z" and "w") in oriented_landmarks_orientations_df.columns.values.tolist():
            for i in range(nbr_landmarks):
                diva_x, diva_y, diva_z = round(oriented_landmarks_positions_df['x'][i]), round(oriented_landmarks_positions_df['y'][i]), round(oriented_landmarks_positions_df['z'][i])
                oriented_landmarks_positions_array[i] = [shape[0] - diva_z, diva_y, diva_x]
                oriented_landmarks_quaternions_array[i] = [oriented_landmarks_orientations_df['x'][i], oriented_landmarks_orientations_df['y'][i], oriented_landmarks_orientations_df['z'][i], oriented_landmarks_orientations_df['w'][i]]
                special_variable_list = [[0.0, 1.0, 0.0, 0.0], [0.0, 1.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0]]
                if oriented_landmarks_quaternions_array[i] in special_variable_list:
                    # landmark in z
                    if oriented_landmarks_quaternions_array[i] == [0.0, 1.0, 0.0, 0.0]:
                        oriented_landmarks_orientations_array[i] = [0.0, 0.0, 1.0]
                    # landmark in y
                    elif oriented_landmarks_quaternions_array[i] == [0.0, 1.0, 1.0, 0.0]:
                        oriented_landmarks_orientations_array[i] = [0.0, 1.0, 0.0]
                    # landmark in x
                    elif oriented_landmarks_quaternions_array[i] == [0.0, 1.0, 0.0, 1.0]:
                        oriented_landmarks_orientations_array[i] = [1.0, 0.0, 0.0]
                        
                else:
                    forward = np.array([0.0, 0.0, 1.0])
                    oriented_landmarks_orientations_array[i] = self.quaternion_multiply_old(oriented_landmarks_quaternions_array[i], forward)
                    oriented_landmarks_orientations_array[i][-1] = - oriented_landmarks_orientations_array[i][-1]
        else:
            display_warning_box(self, "Error", "Incorrect orientations format: need to have quaternions as x, y, z and w in the file.")
            return False

        # Check if landmark position is valid
        for i in range(nbr_landmarks):
            if (oriented_landmarks_positions_array[i][0] > shape[0]) or (oriented_landmarks_positions_array[i][1] > shape[1]) or (oriented_landmarks_positions_array[i][2] > shape[2]) or any(x < 0 for x in oriented_landmarks_positions_array[i]):
                display_warning_box(self, "Error", "Incorrect landmark positions: outside of the image size.")
                return False
            
        self.oriented_landmarks_positions_array = np.array(oriented_landmarks_positions_array)
        self.oriented_landmarks_orientations_array = np.array(oriented_landmarks_orientations_array)
        self.oriented_landmarks_quaternions_array = np.array(oriented_landmarks_quaternions_array)

        return True
    
    def quaternion_multiply(self, quaternion, vector3):
        """
        Rotate a vector by a quaternion : same as (quaternion * Vector3.forward) in Unity 
        (inspired from https://answers.unity.com/questions/372371/multiply-quaternion-by-vector3-how-is-done.html)
        
        Parameters
        ----------
        quaternion : float[4]
            array of (x, y, z, w) coordinates represented a Quaternion
        vector3 : float[3]
            array of (x, y, z)
            
        Returns
        ----------
        output : float[3]
            array of (x, y, z)
                    
        """
        q0 = quaternion[0]
        q1 = quaternion[1]
        q2 = quaternion[2]
        q3 = quaternion[3]
        m00 = 1.0 - 2.0 * q1 * q1 - 2.0 * q2 * q2
        m01 = 2.0 * q0 * q1 - 2.0 * q2 * q3
        m02 = 2.0 * q0 * q2 + 2.0 * q1 * q3
        m10 = 2.0 * q0 * q1 + 2.0 * q2 * q3
        m11 = 1.0 - 2.0 * q0 * q0 - 2.0 * q2 * q2
        m12 = 2.0 * q1 * q2 - 2.0 * q0 * q3
        m20 = 2.0 * q0 * q2 - 2.0 * q1 * q3
        m21 = 2.0 * q1 * q2 + 2.0 * q0 * q3
        m22 = 1.0 - 2.0 * q0 * q0 - 2.0 * q1 * q1
        
        x = m00 * vector3[0] + m01 * vector3[1] + m02 * vector3[2]
        y = m10 * vector3[0] + m11 * vector3[1] + m12 * vector3[2]
        z = m20 * vector3[0] + m21 * vector3[1] + m22 * vector3[2]
        
        return [x, y, z]
    
    def quaternion_multiply_old(self, quaternion, vector3):
        
        num = quaternion[0] * 2.0
        num2 = quaternion[1] * 2.0
        num3 = quaternion[2] * 2.0
        num4 = quaternion[0] * num
        num5 = quaternion[1] * num2
        num6 = quaternion[2] * num3
        num7 = quaternion[0] * num2
        num8 = quaternion[0] * num3
        num9 = quaternion[1] * num3
        num10 = quaternion[3] * num
        num11 = quaternion[3] * num2
        num12 = quaternion[3] * num3
        x = (1.0 - (num5 + num6)) * vector3[0] + (num7 - num12) * vector3[1] + (num8 + num11) * vector3[2]
        y = (num7 + num12) * vector3[0] + (1.0 - (num4 + num6)) * vector3[1] + (num9 - num10) * vector3[2]
        z = (num8 - num11) * vector3[0]+ (num9 + num10) * vector3[1] + (1.0 - (num4 + num5)) * vector3[2]
        
        return [x, y, z]

    def local_to_volume_position(self, local_position):
        """
        Convert local position to volume position according to the volume open in the "image" layer.

        Parameters
        ----------
        local_position : array
            local position in the volume (z, y, x) : between 0-1.

        Returns
        ----------
        volume_position : array
            world position in the volume (z, y, x) : in pixels.

        """
        if "image" in self.viewer.layers:
            image_arr = self.viewer.layers['image'].data

            volume_position = np.array(local_position.shape)
            volume_position[0] = (local_position[0]) * (float)(image_arr.shape[0])
            volume_position[1] = (local_position[1]) * (float)(image_arr.shape[1])
            if len(image_arr.shape) == 3:
                volume_position[2] = (local_position[2]) * (float)(image_arr.shape[2])

            return volume_position

    def volume_to_local_position(self, volume_position):
        """
        Convert volume position to local position according to the volume open in the "image" layer.

        Parameters
        ----------
        volume_position : array
            world position in the volume (z, y, x) : in pixels.

        Returns
        ----------
        local_position : array
            local position in the volume (z, y, x) : between 0-1.

        """
        if "image" in self.viewer.layers:
            image_arr = self.viewer.layers['image'].data

            local_position = np.zeros(len(volume_position), dtype=np.float32)
            local_position[0] = volume_position[0] / (float)(image_arr.shape[0])
            local_position[1] = volume_position[1] / (float)(image_arr.shape[1])
            if len(image_arr.shape) == 3:
                local_position[2] = volume_position[2] / (float)(image_arr.shape[2])

            return local_position


# ============ Export data ============
    def export_backup_segmentation(self):
        """
            Export a backup of the 3D segmentation data as a .tif file.

        """
        if hasattr(self.viewer, 'layers'):
            if "annotations" in self.viewer.layers:
                segmentation_arr = self.viewer.layers['annotations'].data
                temp_segmentation_data_file_path = Path(self.image_dir).joinpath("TEMP_" + self.file_name_label.text() + "_segmentation.tif")
                tif.imsave(str(temp_segmentation_data_file_path), segmentation_arr)

    def export_custom_contrast(self):
        """
        Export custom contrast limits as a .json file that can be re-open in the plugin

        """
        if self.custom_contrast_limits is not None:

            files_types = "JSON File (*.json)"

            default_filepath = Path(self.image_dir).joinpath(self.file_name_label.text() + "_custom_contrast.json")
            file_path, _ = QFileDialog.getSaveFileName(self, "Export contrast limit parameters", str(default_filepath), files_types)

            # If choose "Cancel"
            if file_path == "":
                return

            with open(file_path, 'w') as f:
                json.dump(self.custom_contrast_limits, f)

        else:
            display_warning_box(self, "Error", "No custom contrast limits saved. Click on + button to add one (it will take the value of the current contrast limits used).")

    def export_segmentation(self):
        """
            Export the labelled data as a unique 3D image, or multiple 3D images (one by label)

        """
        files_types = "Image File (*.tif *.tiff *.nii.gz *.nii)"

        default_filepath = Path(self.image_dir).joinpath(self.file_name_label.text() + "_segmentation.tif")
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Segmentation", str(default_filepath), files_types)

        # If choose "Cancel"
        if file_path == "":
            return

        if hasattr(self.viewer, 'layers'):
            if "annotations" in self.viewer.layers:

                self.status_label.setText("Saving...")

                saving_mode = display_save_message_box(
                    "Saving Mode",
                    """How do you want to export the segmentation data ? \n\n _Unique_ : as a unique 3D image with corresponding label ids (can be re-open for correction in the application). \n\n _Several_ : as several binary 3D images (0 or 255), one for each label id.""",
                )

                segmentation_arr = self.viewer.layers['annotations'].data

                extensions = Path(file_path).suffixes

                if saving_mode: # "Unique" choice
                    if extensions[-1] in [".tif", ".tiff"]:
                        description = {"Hesperos_SelectedSlices" : self.selected_slice_list}
                        # tif.imsave(file_path, segmentation_arr, description=json.dumps(self.selected_slice_list))
                        tif.imsave(file_path, segmentation_arr, description=json.dumps(description))
                        # tif.imsave(file_path, segmentation_arr, description=description)

                    elif (extensions[-1] == ".nii") or (extensions == [".nii", ".gz"]):
                        result_image_sitk = sitk.GetImageFromArray(segmentation_arr.astype(np.uint8))
                        result_image_sitk.CopyInformation(self.image_sitk)
                        sitk.WriteImage(result_image_sitk, file_path)

                        # ====== Test Metadata writing with SimpleITK ======
                        # result_image_sitk.SetMetaData(key="Hesperos_SelectedSlices", value=str(self.selected_slice_list))
                        # result_image_sitk.GetMetaData("Hesperos_SelectedSlices")
                        # for k in result_image_sitk.GetMetaDataKeys():
                        #     v = result_image_sitk.GetMetaData(k)
                        #     print("({0}) = = \"{1}\"".format(k,v))

                        # writer = sitk.ImageFileWriter()
                        # writer.KeepOriginalImageUIDOn()
                        # writer.SetFileName(file_path)
                        # writer.Execute(result_image_sitk)
                        # ==================================================================

                else: # "Several" choice
                    structure_name = self.annotation_combo_box.currentText()
                    if structure_name == "Fetus":
                        structure_list = self.fetus.list_structure_name
                    elif structure_name == "Shoulder":
                        structure_list = self.shoulder.list_structure_name
                    elif structure_name == "Shoulder Bones":
                        structure_list = self.shoulder_bones.list_structure_name
                    elif structure_name == "Shoulder Bone Borders":
                        structure_list = self.shoulder_bone_borders.list_structure_name
                    elif structure_name == "Shoulder Deltoid":
                        structure_list = self.shoulder_deltoid.list_structure_name
                    elif structure_name == "Feta Challenge":
                        structure_list = self.feta.list_structure_name
                    elif structure_name == "Larva":
                        structure_list = self.larva.list_structure_name
                    elif structure_name == "Mouse Embryon":
                        structure_list = self.mouse_embryon.list_structure_name
                    else:
                        structure_list=[]

                    for idx, struc in enumerate(structure_list):
                        label_struc = np.zeros(segmentation_arr.shape, dtype=np.uint8)
                        label_struc[segmentation_arr == (idx + 1)] = 255

                        #export only if the labelled data is not empty
                        if np.any(label_struc):
                            if extensions[-1] in [".tif", ".tiff"]:
                                file_name = Path(file_path).stem
                                new_file_name = file_name + '_' + struc + extensions[0]
                                new_file_path = Path(Path(file_path).parent).joinpath(new_file_name)
                                tif.imsave(str(new_file_path), label_struc)

                            elif (extensions[-1] == ".nii") or (extensions == [".nii", ".gz"]):
                                file_name = Path(Path(file_path).stem).stem
                                try:
                                    new_file_name = file_name + '_' + struc + extensions[0] + extensions[1]
                                except:
                                    new_file_name = file_name + '_' + struc + extensions[0]
                                new_file_path = Path(Path(file_path).parent).joinpath(new_file_name)
                                result_image_sitk = sitk.GetImageFromArray(label_struc)
                                result_image_sitk.CopyInformation(self.image_sitk)
                                sitk.WriteImage(result_image_sitk, str(new_file_path))

                            else:
                                return

                self.remove_backup_segmentation_file()
                self.status_label.setText("Ready")

            else:
                display_warning_box(self, "Error", "No segmentation data find.")
                return

    def export_oriented_landmarks(self):
        """
        Export oriented landmark parameters as a .json file for reopening in DIVA software.
        
        """        
        files_types = "JSON File (*.json)"
        default_filepath = Path(self.image_dir).joinpath(self.file_name_label.text() + "_oriented_landmarks_for_DIVA.json")
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Oriented Landmarks", str(default_filepath), files_types)

        # If choose "Cancel"
        if file_path == "":
            return

        oriented_landmarks = {}
        oriented_landmarks_parameters = {}
        
        shape = self.viewer.layers['image'].data.shape # as (x, y, z)
        
        if len(shape) != 3:
            display_warning_box(self, "Error", "Incorrect image size. Need to be a 3D image to use oriented landmarks.")
            return
        
        volume_positions = pd.DataFrame(self.oriented_landmarks_positions_array, columns = ["z","y","x"])
        volume_positions = volume_positions[["x","y","z"]]
        volume_positions["z"] = shape[0] - volume_positions["z"]
        
        local_rotations = pd.DataFrame(self.oriented_landmarks_quaternions_array, columns = ["x","y","z","w"])

        oriented_landmarks["_volume_positions"] = volume_positions.to_dict('records')
        oriented_landmarks["_local_rotations"] = local_rotations.to_dict('records')
        
        oriented_landmarks_parameters["_oriented_landmarks_parameters"] = oriented_landmarks
            
        with open(file_path, 'w') as f:
            json.dump(oriented_landmarks_parameters, f, separators=(',', ':'))
    

# ============ Set data ============
    def set_image_with_path(self, file_type):
        """
        Set image data by asking file path to the user.
        Import image data, add it to napari, toggle panels, check if a corresponding segmentation data file exist (if so, import it and add it to napari).

        Parameters
        ----------
        file_type : str
            type of image loaded : "file" for .tiff, .tif, .nii and .nii.gz and "folder" for DICOM folder

        """
        canRemove = self.can_remove_all()

        if canRemove:
            self.status_label.setText("Loading...")

            if file_type == "file":
                image_arr = self.import_image_file()
            elif file_type == 'folder':
                image_arr = self.import_dicom_folder()

            if image_arr is None:
                self.status_label.setText("Ready")
                return

            self.set_image_layer(image_arr)
            self.remove_oriented_landmarks_layers()

            self.reset_zoom_slider()
            self.reset_lock_push_button()
            self.go_to_selected_slice_push_button.setChecked(False)
            self.go_to_selected_oriented_landmark_push_button.setChecked(False)
            self.backup_check_box.setChecked(False)
            self.default_contrast_combo_box.setCurrentText("")

            self.toggle_import_panel_widget(True, file_type)
            self.toggle_panels(["manage_oriented_landmarks_panel", "annotation_panel", "slice_selection_panel", "reset_export_panel"], True)
            # if image_arr.shape[0] > 1:
            #     self.toggle_panels(["manage_oriented_landmarks_panel"], True)
            # else :
            #     self.toggle_panels(["manage_oriented_landmarks_panel"], False)
            self.update_panel_titles()

            self.step_range_spin_box.setMaximum(image_arr.shape[0])

            hasCorrespondingSegmentation, segmentation_file_path = self.has_corresponding_segmentation_file()

            if hasCorrespondingSegmentation:
                choice = display_yes_no_question_box(
                "Warning",
                "A corresponding segmentation file has been found. Do you want to open it ?",
                )

                if choice: #Yes
                    self.set_segmentation_with_path(segmentation_file_path)
                else:
                    segmentation_arr = np.zeros(image_arr.shape, dtype=np.int8)
                    self.set_segmentation_layer(segmentation_arr)
                    self.reset_lock_push_button()
                    self.go_to_selected_slice_push_button.setChecked(False)
                    self.reset_selected_slice_combo_box()
                    self.go_to_selected_oriented_landmark_push_button.setChecked(False)
                    self.reset_oriented_landmark()

            else:
                segmentation_arr = np.zeros(image_arr.shape, dtype=np.int8)
                self.set_segmentation_layer(segmentation_arr)
                self.reset_lock_push_button()
                self.go_to_selected_slice_push_button.setChecked(False)
                self.reset_selected_slice_combo_box()
                self.go_to_selected_oriented_landmark_push_button.setChecked(False)
                self.reset_oriented_landmark()

            self.update_panel_titles()
            self.annotation_combo_box.setCurrentText("Choose a structure")
            self.status_label.setText("Ready")

        else:
            return

    def set_oriented_landmarks_from_points_layer_action(self):
        """
        Set oriented landmarks data if a point was added or removed from the point layer button.
        Update oriented_landmarks_positions_array and oriented_landmarks_orientations_array, add it to napari, toggle panels.

        """
        if "landmarks" in self.viewer.layers:
            shape = self.viewer.layers['image'].data.shape
            if len(shape) != 3:
                return
            current_points_layer_data = self.viewer.layers["landmarks"].data

            new_nbr_landmarks = len(current_points_layer_data)
            oriented_landmarks_positions_array = [[] * len(shape) for i in range(new_nbr_landmarks)]
            oriented_landmarks_orientations_array = [[0.0] * len(shape) for i in range(new_nbr_landmarks)]
            oriented_landmarks_quaternions_array = [[0.0] * 4 for i in range(new_nbr_landmarks)]

            # == When a point was added (always at the last position in the list) ===
            if new_nbr_landmarks > len(self.oriented_landmarks_positions_array):
                # # Check if landmark position is valid
                new_point_position_array = current_points_layer_data[-1].astype(np.int16)
                if (new_point_position_array[0] > shape[0]) or (new_point_position_array[1] > shape[1]) or (new_point_position_array[2] > shape[2]) or any(x < 0 for x in new_point_position_array):
                    display_warning_box(self, "Error", "Incorrect landmark positions: outside of the image size.")
                    self.remove_oriented_landmark(isRemoveLast = True)
                    self.add_oriented_landmark_push_button.setChecked(False)
                    return 
                                
                is_added = True
                for i in range(new_nbr_landmarks):
                    oriented_landmarks_positions_array[i] = current_points_layer_data[i].astype(np.int16)
                    # for the last point (the new one) define orientations as the current axes
                    if i == new_nbr_landmarks - 1:
                        # test if new point in image size 
                        # 2D view
                        if len(self.viewer.dims.displayed) == 2:
                            current_axis_index = self.viewer.dims.not_displayed[0]
                            # Order of rotation Rx, Ry, Rz different of the axis order z y x
                            if len(shape) == 3:
                                rotation_order = [2, 1, 0]
                            else : 
                                rotation_order = [1, 0]
                            
                            oriented_landmarks_orientations_array[i][rotation_order[current_axis_index]] = 1.0
                            
                            # for landmark added in z as current axis => q = 0 1 0 0
                            if rotation_order[current_axis_index] == 2:
                                oriented_landmarks_quaternions_array[i][1] = 1.0
                            # for landmark added in y as current axis => q = 0 1 1 0
                            elif rotation_order[current_axis_index] == 1:
                                oriented_landmarks_quaternions_array[i][1] = 1.0
                                oriented_landmarks_quaternions_array[i][2] = 1.0
                            # for landmark added in x as current axis => q = 0 1 0 1
                            elif rotation_order[current_axis_index] == 0:
                                oriented_landmarks_quaternions_array[i][1] = 1.0
                                oriented_landmarks_quaternions_array[i][3] = 1.0
                        # 3D view (keep orientation to 0)
                    else:
                        oriented_landmarks_orientations_array[i] = self.oriented_landmarks_orientations_array[i]
                        oriented_landmarks_quaternions_array[i] = self.oriented_landmarks_quaternions_array[i]

            # == When a point was deleted (always at the last position in the list) ===
            elif new_nbr_landmarks < len(self.oriented_landmarks_positions_array):
                is_added = False
                oriented_landmarks_positions_array = current_points_layer_data.astype(np.int16)
                oriented_landmarks_orientations_array = self.oriented_landmarks_orientations_array[:-1]
                oriented_landmarks_quaternions_array = self.oriented_landmarks_quaternions_array[:-1]

            else:
                return

            self.oriented_landmarks_positions_array = np.array(oriented_landmarks_positions_array)
            self.oriented_landmarks_orientations_array = np.array(oriented_landmarks_orientations_array)
            self.oriented_landmarks_quaternions_array = np.array(oriented_landmarks_quaternions_array)

            self.set_oriented_landmark_layers()
            self.update_selected_oriented_landmark_combo_box()

            # == When a point was added ===
            if is_added:
                self.selected_oriented_landmark_combo_box.setCurrentText(str(new_nbr_landmarks))
                self.add_oriented_landmark_push_button.setChecked(False)
                self.update_landmarks_layer_mode()

    def set_oriented_landmarks_with_path(self):
        """
        Set oriented landmarks data by asking file path to the user.
        Import data, add it to napari, toggle panels.

        """
        if "image" in self.viewer.layers:
            if len(self.viewer.layers['image'].data.shape) != 3:
                display_warning_box(self, "Error", "Incorrect image size. Need to be a 3D image to use oriented landmarks.")
                return
            
        canRemove = self.can_remove_oriented_landmarks_data()

        if canRemove:
            self.status_label.setText("Loading...")

            import_status = self.import_oriented_landmarks_json()

            if import_status is False:
                self.status_label.setText("Ready")
                return

            if "image" in self.viewer.layers:
                self.set_oriented_landmark_layers()
                self.update_selected_oriented_landmark_combo_box()
                self.status_label.setText("Ready")

    def set_segmentation_with_path(self, segmentation_path=None):
        """
        Set segmentation data from a file path : import data and add it to napari.

        Parameters
        ----------
        segmentation_path : str
            path of the segmentation file

        """
        # not from a corresponding segmentation file found for the image
        if segmentation_path is None:
            canRemove = self.can_remove_segmentation_data()
        # from a corresponding segmentation file found for the image (not ask for remove because all ready done)
        else:
            canRemove = True

        if canRemove:
            self.status_label.setText("Loading...")

            segmentation_arr, segmentation_sitk = self.import_segmentation_file(segmentation_path)

            if segmentation_arr is None:
                self.status_label.setText("Ready")
                return

            if "image" in self.viewer.layers:
                image_arr = self.viewer.layers['image'].data

                if segmentation_arr.shape != image_arr.shape:
                    image_arr_viewer = np.transpose(image_arr, self.viewer.dims.order)

                    if segmentation_arr.shape == image_arr_viewer.shape:
                        if self.viewer.dims.order == (2, 0, 1):
                            segmentation_arr = np.transpose(segmentation_arr, (1, 2, 0))
                        elif self.viewer.dims.order == (1, 2, 0):
                            segmentation_arr = np.transpose(segmentation_arr, (2, 0, 1))

                    else:
                        display_warning_box(self, "Error", "Size of the segmentation file doesn't correspond to the size of the source image.")
                        self.status_label.setText("Ready")
                        return

                self.set_segmentation_layer(segmentation_arr)
                self.update_napari_layers_order()
                self.reset_lock_push_button()
                self.go_to_selected_slice_push_button.setChecked(False)
                self.reset_selected_slice_combo_box()
                self.import_selected_slice(segmentation_sitk)
                # self.go_to_selected_oriented_landmark_push_button.setChecked(False)
                # self.reset_oriented_landmark_data()
                # self.reset_oriented_landmark_combo_box()
                self.status_label.setText("Ready")


# ============ Set Napari layers ============
    def set_image_layer(self, array):
        """
        Remove the image layer from Napari and add a new image layer (faster than changing the data of an existing layer)

        Parameters
        ----------
        array : ndarray
            3D image data to add

        """
        self.remove_image_layer()
        # self.viewer.add_image(array, name='image', contrast_limits=(np.min(array), np.max(array)))
        if array.shape[0] == 1:
            self.viewer.add_image(array[0, :, :], name='image')
        else:
            self.viewer.add_image(array, name='image')
        self.viewer.layers['image'].contrast_limits = (np.min(array), np.max(array))

        # === Enable axes view ===
        self.viewer.dims.axis_labels = ('z', 'y', 'x') # same than ('0', '1', '2')
        self.viewer.axes.arrows = True
        self.viewer.axes.colored = False
        self.viewer.axes.dashed = False
        self.viewer.axes.labels = True
        self.viewer.axes.visible = True

        disable_layer_widgets(self.viewer, layer_name='image', layer_type='image')
        self.viewer.layers['image'].events.contrast_limits.connect(self.reset_default_contrast_combo_box)
        # self.viewer.window._qt_viewer.viewerButtons.ndisplayButton.clicked.disconnect()
        # self.viewer.window._qt_viewer.viewerButtons.rollDimsButton.clicked.connect(self.overwrite_roll_axes)
        # self.viewer.window._qt_viewer.viewerButtons.rollDimsButton.clicked.connect(self.update_slice_index_after_rollDims)
        # self.viewer.window._qt_viewer.viewerButtons.rollDimsButton.clicked.disconnect()
        # self.viewer.window._qt_viewer.viewerButtons.rollDimsButton.clicked.connect(self.overwrite_roll_axes)
        # self.viewer.window._qt_viewer.viewerButtons.rollDimsButton.clicked.connect(self.update_slice_index_after_rollDims)
        # self.viewer.window._qt_viewer.viewerButtons.transposeDimsButton.clicked.disconnect()
        # self.viewer.window._qt_viewer.viewerButtons.transposeDimsButton.clicked.connect(self.overwrite_transpose_dim)
        # self.rotation_applied = 0

    def set_segmentation_layer(self, array):
        """
        Remove the segmentation layer from Napari and add a new segmentation layer (faster than changing the data of an existing layer)
        New layer can be empty for initialisation.

        Parameters
        ----------
        array : ndarray
            3D segmentation data with the same size than the raw image (display in the 'image' layer)

        """
        self.remove_segmentation_layer()
        self.viewer.add_labels(array, name='annotations', color=label_colors)
        self.reset_annotation_layer_selected_label()
        disable_layer_widgets(self.viewer, layer_name='annotations', layer_type='label')
        self.remove_backup_segmentation_file()

        self.viewer.layers['annotations'].mouse_double_click_callbacks.append(self.automatic_fill)
        self.viewer.layers['annotations'].bind_key('O', self.enable_opacity_annotation_layer)

    def set_oriented_landmark_layers(self):
        """
        Remove the points layer from Napari and add a new points layer and a new vectors layer

        """
        self.remove_oriented_landmarks_layers()

        # === Add positions of the oriented landmarks as points in a point layer ===
        shape_max = max(self.viewer.layers['image'].data.shape)
        points_size = int(shape_max / 64)
        vectors_length = points_size * 2
        vector_edge_width = points_size / 2
        self.viewer.add_points(
            self.oriented_landmarks_positions_array,
            name="landmarks",
            size=points_size,
            symbol='disc',
            edge_color="white",
            face_color="white",
            blending='additive',
            out_of_slice_display=True,
            opacity=1,
            ndim=3)
        disable_layer_widgets(self.viewer, layer_name='landmarks', layer_type='points')
        self.viewer.layers['landmarks'].events.data.connect(self.set_oriented_landmarks_from_points_layer_action)
        # self.viewer.layers['landmarks'].events.mode.connect(self.update_add_oriented_landmark_push_button_check_status)

        # === Add orientations of the oriented landmarks as vectors in a vector layer ===
        nbr_vectors = len(self.oriented_landmarks_orientations_array)
        vectors = np.zeros((nbr_vectors, 2, 3), dtype=np.float32)
        for i in range(nbr_vectors) :
            # assign x-y-z projection
            vectors[i, 1, 0] = self.oriented_landmarks_orientations_array[i][2]
            vectors[i, 1, 1] = self.oriented_landmarks_orientations_array[i][1]
            vectors[i, 1, 2] = self.oriented_landmarks_orientations_array[i][0]

            # assign x-y-z position
            vectors[i, 0, 0] = self.oriented_landmarks_positions_array[i][0]
            vectors[i, 0, 1] = self.oriented_landmarks_positions_array[i][1]
            vectors[i, 0, 2] = self.oriented_landmarks_positions_array[i][2]

        self.viewer.add_vectors(
            vectors,
            name='orientations',
            edge_width=vector_edge_width,
            edge_color='yellow',
            length=vectors_length,
            blending='additive',
            out_of_slice_display=True,
            opacity=1,
            ndim=3)
        disable_layer_widgets(self.viewer, layer_name='orientations', layer_type='vectors')

    def update_napari_layers_order(self):
        """
        Change the order of the napari layers 
        
        """          
        if all(layer_name in self.viewer.layers for layer_name in ["annotations", "landmarks", "orientations"]):
            annotations_layer_index = self.viewer.layers._list.index(self.viewer.layers["annotations"])
            self.viewer.layers.move(annotations_layer_index, 1)


# ============ Napari events callbacks ============
    def activate_backup_segmentation(self):
        """
            Activate backup of the segmentation data when the image slice is changed.

        """
        if self.backup_check_box.isChecked() == True:
            choice = display_ok_cancel_question_box(
                "Warning",
                "Automatically saving the segmentation data when the image slice is changed can slow down the display. Do you want to continue ?",
            )
            if choice: #Ok
                self.viewer.dims.events.emitters['current_step'].connect(self.export_backup_segmentation)
            else: #Cancel
                self.backup_check_box.setChecked(False)
        else:
            self.viewer.dims.events.emitters['current_step'].disconnect(self.export_backup_segmentation)

    def automatic_fill(self, layer, event):
        """
        Quick switch between label modes (paint and fill) by double clicking.

        """
        if layer.mode in ["paint"]:
            layer.mode = "fill"

        elif layer.mode in ["fill"]:
            layer.mode = "paint"

    def enable_opacity_annotation_layer(self, viewer):
        """
        Enable keyboard shortcut to switch between positive opacity and zero opacity.

        """
        if "annotations" in self.viewer.layers:
            if self.viewer.layers['annotations'].opacity != 0:
                self.annotation_opacity = self.viewer.layers['annotations'].opacity
                self.viewer.layers['annotations'].opacity = 0
            else:
                try:
                    self.viewer.layers['annotations'].opacity = self.annotation_opacity
                except:
                    self.viewer.layers['annotations'].opacity = 0.6

    def overwrite_transpose_dim(self, event):
        """
        TODO
        Overwrite napari code for dims._trans)
        """
        # b = 5

        # # basic function : "Transpose order of the last two visible axes, e.g. [0, 1] -> [1, 0]."
        # # napari code for dims._transpose()
        # order = list(self.viewer.dims.order)
        # order[-2], order[-1] = order[-1], order[-2]
        # self.viewer.dims.order = order

        # NAPARI CODE FOR dims._roll
        # order = np.array(self.viewer.dims.order)
        # nsteps = np.array(self.viewer.dims.nsteps)
        # order[nsteps > 1] = np.roll(order[nsteps > 1], 1)
        # self.viewer.dims.order = order.tolist()

        ## test

        # self.rotation_applied = self.rotation_applied + 90
        # if self.rotation_applied > 360:
        #     self.rotation_applied = 0
        # translation = self.viewer.layers['image'].translate
        # indx_1, indx_2 = self.viewer.dims.displayed[0], self.viewer.dims.displayed[1]
        # translation[indx_1] = self.viewer.dims.current_step[indx_1] / 2
        # translation[indx_2] = self.viewer.dims.current_step[indx_2] / 2
        # self.viewer.layers['image'].translate = - translation
        # self.viewer.layers['image'].rotate = self.rotation_applied
        # self.viewer.layers['image'].translate = + translation
        # self.viewer.layers['image'].translate = - 2*translation

    def update_slice_positon_after_dims_roll(self, event):
        """
        Linked to dims._roll() to update the slice position of the new displayed dimension if a oriented landmark or slice has been selected.

        """
        if self.viewer.dims.ndisplay == 2:
            if (self.go_to_selected_oriented_landmark_push_button.isChecked() == True) and (self.selected_oriented_landmark_combo_box.currentText() != " "):
                self.go_to_oriented_landmark()

            elif self.go_to_selected_slice_push_button.isChecked() == True:
                self.go_to_selected_slice()


# ============ Custom widget callbacks ============
    def add_selected_slice(self):
        """
        Add the slice index of the actual slice displayed in the selected_slice_combo_box

        """
        current_axis_index = self.viewer.dims.not_displayed[0]
        selected_slice = self.viewer.dims.current_step[current_axis_index]
        axis_order = ['z', 'y', 'x']

        # if len(self.selected_slice_list) >= 30:
        #     display_warning_box(self, "Error", "More than 30 selected slices are not allowed. Please remove some selected slices to add new ones.")
        #     return
        selected_info = str(str(selected_slice) + axis_order[current_axis_index] )
        if selected_info in self.selected_slice_list:
            return

        else:
            self.selected_slice_list.append(selected_info)
            self.selected_slice_list.sort(key=lambda text: int(text[:-1]))

            list_index = self.selected_slice_list.index(selected_info)
            self.selected_slice_combo_box.insertItem(list_index + 1, selected_info)
            self.selected_slice_combo_box.setCurrentText(selected_info)

    def go_left_step_slices(self):
        """
        Change the currently displayed slice according to the slice index selected in the step_range_spin_box

        """
        # === Check axis not displayed (so use for current step) ===
        current_axis_index = self.viewer.dims.not_displayed[0]

        # === Update current step along this axis ===
        new_step_index = self.viewer.dims.current_step[current_axis_index] - self.step_range_spin_box.value()
        new_current_step_list = list(self.viewer.dims.current_step)
        if new_step_index >= 0 :
            new_current_step_list[current_axis_index] = new_step_index
            self.viewer.dims.current_step = tuple(new_current_step_list)
        else:
            new_current_step_list[current_axis_index] = 0
            self.viewer.dims.current_step = tuple(new_current_step_list)

    def go_right_step_slices(self):
        """
        Change the currently displayed slice according to the slice index selected in the step_range_spin_box

        """
        # === Check axis not displayed (so use for current step) ===
        current_axis_index = self.viewer.dims.not_displayed[0]

        # === Update current step along this axis ===
        new_step_index = self.viewer.dims.current_step[current_axis_index] + self.step_range_spin_box.value()
        new_current_step_list = list(self.viewer.dims.current_step)
        if new_step_index <= self.viewer.layers['image'].data.shape[current_axis_index]:
            new_current_step_list[current_axis_index] = new_step_index
            self.viewer.dims.current_step = tuple(new_current_step_list)
        else:
            new_current_step_list[current_axis_index] = self.viewer.layers['image'].data.shape[current_axis_index] - 1
            self.viewer.dims.current_step = tuple(new_current_step_list)

    def go_to_selected_slice(self):
        """
        Change the currently displayed slice according to the slice index selected in the selected_slice_combo_box

        """
        axis_order = ['z', 'y', 'x']

        if self.go_to_selected_slice_push_button.isChecked() == True:
            if self.selected_slice_combo_box.currentText() != " ":
                current_axis_index = self.viewer.dims.not_displayed[0]
                selected_slice = int(self.selected_slice_combo_box.currentText()[:-1])
                selected_axis_index =  axis_order.index(self.selected_slice_combo_box.currentText()[-1])
                if current_axis_index == selected_axis_index:
                    new_current_step_list = list(self.viewer.dims.current_step)
                    new_current_step_list[selected_axis_index] = selected_slice
                    self.viewer.dims.current_step = tuple(new_current_step_list)
                else:
                    self.go_to_selected_slice_push_button.setChecked(False)
            else:
                self.go_to_selected_slice_push_button.setChecked(False)

        else:
            if self.selected_slice_combo_box.currentText() != " ":
                current_axis_index = self.viewer.dims.not_displayed[0]
                selected_slice = int(self.selected_slice_combo_box.currentText()[:-1])
                selected_axis_index = axis_order.index(self.selected_slice_combo_box.currentText()[-1])
                current_slice = self.viewer.dims.current_step[current_axis_index]
                if current_slice != selected_slice and current_axis_index == selected_axis_index:
                    new_current_step_list = list(self.viewer.dims.current_step)
                    new_current_step_list[selected_axis_index] = selected_slice
                    self.viewer.dims.current_step = tuple(new_current_step_list)
                elif current_slice == selected_slice and current_axis_index == selected_axis_index:
                    self.go_to_selected_slice_push_button.setChecked(True)
                else:
                    self.go_to_selected_slice_push_button.setChecked(False)

    def go_to_oriented_landmark(self):
        """
        Change the currently displayed slice according to the landmark selected in the selected_oriented_landmark_combo_box

        """
        if self.go_to_selected_oriented_landmark_push_button.isChecked() == True:
            if self.selected_oriented_landmark_combo_box.currentText() != " ":
                # === Check axis not displayed (so use for current step) ===
                current_axis_index = self.viewer.dims.not_displayed[0]
                # === Update current step along this axis ===
                landmark_slice = self.oriented_landmarks_positions_array[int(self.selected_oriented_landmark_combo_box.currentText()) - 1][current_axis_index]
                new_current_step_list = list(self.viewer.dims.current_step)
                new_current_step_list[current_axis_index] = landmark_slice
                self.viewer.dims.current_step = tuple(new_current_step_list)
            else:
                self.go_to_selected_oriented_landmark_push_button.setChecked(False)

        else:
            if self.selected_oriented_landmark_combo_box.currentText() != " ":
                # === Check axis not displayed (so use for current step) ===
                current_axis_index = self.viewer.dims.not_displayed[0]
                # === Update current step along this axis ===
                current_displayed_slice = self.viewer.dims.current_step[current_axis_index]
                landmark_slice = self.oriented_landmarks_positions_array[int(self.selected_oriented_landmark_combo_box.currentText()) - 1][current_axis_index]
                if current_displayed_slice != landmark_slice:
                    new_current_step_list = list(self.viewer.dims.current_step)
                    new_current_step_list[current_axis_index] = landmark_slice
                    self.viewer.dims.current_step = tuple(new_current_step_list)
                else:
                    self.go_to_selected_oriented_landmark_push_button.setChecked(True)

    def lock_slide(self):
        """
        Lock a slice of work. Clicking on the checked QPushButton put the viewer to the locked slice location.
        Allow user to explore data and return to a specific slice quickly.

        """
        if self.lock_push_button.isChecked() == True:
            if self.locked_slice_index is None:
                self.lock_push_button.setIcon(QIcon(get_icon_path('lock')))
                self.locked_slice_index = self.viewer.dims.current_step

        else:
            if self.locked_slice_index == self.viewer.dims.current_step:
                self.lock_push_button.setIcon(QIcon(get_icon_path('unlock')))
                self.locked_slice_index = None

            elif self.locked_slice_index is None:
                self.lock_push_button.setIcon(QIcon(get_icon_path('unlock')))

            else:
                self.lock_push_button.setChecked(True)
                self.viewer.dims.current_step = self.locked_slice_index

    def remove_selected_slice(self):
        """
        Remove the current slice index displayed in the selected_slice_combo_box and set the combo box to the default value " "

        """
        if len(self.selected_slice_list) == 0:
            return

        axis_order = ['z', 'y', 'x']
        current_axis_index = self.viewer.dims.not_displayed[0]

        current_slice = self.viewer.dims.current_step[current_axis_index]
        current_info = str(str(current_slice) + axis_order[current_axis_index] )

        if current_info in self.selected_slice_list:
            list_index = self.selected_slice_list.index(current_info)
            self.selected_slice_combo_box.setCurrentText(" ")
            self.selected_slice_combo_box.removeItem(list_index + 1)
            self.selected_slice_list.remove(current_info)

    def remove_oriented_landmark(self, isRemoveLast=False):
        """
        Remove the last oriented landmark of the list (data is automatically updated)
        
        Parameters
        ----------
        isRemoveLast : bool
            if True the last landmark will be removed. If False, the index of the landmark to remove is defined by selected_oriented_landmark_combo_box.

        """
        if "landmarks" in self.viewer.layers:
            if len(self.viewer.layers["landmarks"].data) != 0:
                if isRemoveLast: 
                    nbr_landmarks = len(self.viewer.layers["landmarks"].data)
                    index_to_remove = nbr_landmarks - 1
                    if index_to_remove < 0 : index_to_remove = 0
                    self.viewer.layers["landmarks"].mode = "SELECT"
                    self.viewer.layers["landmarks"].selected_data={index_to_remove}
                    self.viewer.layers["landmarks"].remove_selected()
                    self.viewer.layers["landmarks"].mode = "PAN_ZOOM"
                
                else:
                    if self.selected_oriented_landmark_combo_box.currentText() != ' ':
                        index_to_remove = int(self.selected_oriented_landmark_combo_box.currentText()) - 1
                        if index_to_remove < 0 : index_to_remove = 0
                        self.viewer.layers["landmarks"].mode = "SELECT"
                        self.viewer.layers["landmarks"].selected_data={index_to_remove}
                        self.viewer.layers["landmarks"].remove_selected()
                        self.viewer.layers["landmarks"].mode = "PAN_ZOOM"

    def reset_segmentation(self):
        """
            Reset segmentation data

        """
        canRemoveSegmentation = self.can_remove_segmentation_data()

        if canRemoveSegmentation:
            if "image" in self.viewer.layers:
                image_arr = self.viewer.layers['image'].data
                segmentation_arr = np.zeros(image_arr.shape, dtype=np.int8)
                self.set_segmentation_layer(segmentation_arr)
                self.update_napari_layers_order()
        else:
            return

    def set_custom_contrast(self):
        """
        Save the current contrast limits as a "Custom Contrast" to be re-used and apply it.

        """
        if "image" in self.viewer.layers:
            self.custom_contrast_limits = self.viewer.layers['image'].contrast_limits
            self.default_contrast_combo_box.setCurrentText("Custom Contrast")

    def set_default_contrast(self):
        """
        Change the image contrast limits according to a predefined contrast window ("CT Bone" or "CT Soft").
        Can only be apply to a DICOM image, because windows are defined using the Hounsfiled units.

        """
        if "image" in self.viewer.layers:
            # rescale_intercept = - self.viewer.layers['image'].contrast_limits_range[0]
            if self.default_contrast_combo_box.currentText() == "CT Bone":
                self.hu_limits = (-450, 1050)
                # hu = pixel_value * slope + intercept
                self.viewer.layers['image'].contrast_limits = self.hu_limits
                # self.viewer.layers['image'].contrast_limits_range = (self.viewer.layers['image'].data.min(), self.viewer.layers['image'].data.max())

            elif self.default_contrast_combo_box.currentText() == "CT Soft":
                self.hu_limits = (-160, 240)
                self.viewer.layers['image'].contrast_limits = self.hu_limits

            elif self.default_contrast_combo_box.currentText() == "Custom Contrast":
                if self.custom_contrast_limits is not None:
                    self.viewer.layers['image'].contrast_limits = self.custom_contrast_limits
                else:
                    display_warning_box(self, "Error", "No custom contrast limits saved. Click on + button to add one (it will take the value of the current contrast limits used).")

            else:
                return
        else:
            self.default_contrast_combo_box.setCurrentText("Set a default contrast")

    def undo_segmentation(self):
        """
            Undo last operation of annotation

        """
        if hasattr(self.viewer, 'layers'):
            if 'annotations' in self.viewer.layers:
                segmentation_layer = self.viewer.layers['annotations']
                segmentation_layer.undo()

    def update_landmarks_layer_mode(self):
        """
        Update the mode of the 'landmarks' layer to allow points addition according to the checked status of the add_oriented_landmark_push_button push button.
        When a point is added, the set_oriented_landmarks_from_points_layer_action function is automatically called.

        """
        if "image" in self.viewer.layers:
            if len(self.viewer.layers["image"].data.shape) != 3:
                display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image to use oriented landmarks.")
                self.add_oriented_landmark_push_button.setChecked(False)
                return
            
        if self.add_oriented_landmark_push_button.isChecked() == False:
            if "landmarks" in self.viewer.layers:
                self.viewer.layers["landmarks"].mode = 'PAN_ZOOM'

        else:
            if "landmarks" in self.viewer.layers:
                self.viewer.layers["landmarks"].mode = 'ADD'
                self.viewer.layers.selected = self.viewer.layers["landmarks"]
                self.viewer.layers.selection.add(self.viewer.layers["landmarks"])
                self.viewer.layers.selection.active = self.viewer.layers["landmarks"]

            else:
                self.oriented_landmarks_positions_array = []
                self.oriented_landmarks_orientations_array = []
                self.oriented_landmarks_quaternions_array = []
                self.set_oriented_landmark_layers()
                self.update_selected_oriented_landmark_combo_box()
                self.update_landmarks_layer_mode()

    def zoom(self):
        """
            Zoom the camera view of the main canvas of napari

        """
        self.viewer.camera.zoom = self.zoom_slider.value() / 100


# ============ Reset widget options ============
    def reset_annotation_radio_button_checked_id(self):
        """
        Reset selected radio button (i.e. the element to annotate) to the first item of the list.

        """
        structure_name = self.annotation_combo_box.currentText()
        if structure_name == "Fetus":
            radio_button_to_check = self.fetus.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Shoulder":
            radio_button_to_check = self.shoulder.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Shoulder Bones":
            radio_button_to_check = self.shoulder_bones.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Shoulder Bone Borders":
            radio_button_to_check = self.shoulder_bone_borders.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Shoulder Deltoid":
            radio_button_to_check = self.shoulder_deltoid.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Feta Challenge":
            radio_button_to_check = self.feta.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Larva":
            radio_button_to_check = self.larva.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Mouse Embryon":
            radio_button_to_check = self.mouse_embryon.group_radio_button.button(1)
            radio_button_to_check.setChecked(True)

    def reset_annotation_layer_selected_label(self):
        """
        Reset the selected structure to annotate.

        """
        if "annotations" in self.viewer.layers:
            if self.annotation_combo_box.currentText() == "Choose a structure":
                self.viewer.layers['annotations'].selected_label = 0
            else:
                self.viewer.layers['annotations'].selected_label = 1

            self.viewer.layers['annotations'].mode = "PAINT"
            self.viewer.layers['annotations'].opacity = 0.6

    def reset_default_contrast_combo_box(self):
        """
        Reset the selected structure to annotate.

        """
        if "image" in self.viewer.layers:
            if self.default_contrast_combo_box.currentText() != "Set a default contrast":
                if (self.viewer.layers['image'].contrast_limits == list(self.hu_limits)) or (self.viewer.layers['image'].contrast_limits == self.custom_contrast_limits):
                    return
                else:
                    self.default_contrast_combo_box.setCurrentText("Set a default contrast")

    def reset_lock_push_button(self):
        """
        Reset the selected slice of work to None and uncheck button.

        """
        self.locked_slice_index = None
        self.lock_push_button.setChecked(False)

    def reset_oriented_landmark(self):
        """
        Reset oriented landmarks (reset arrays, delete layers and reset combo box)
        
        """
        self.reset_oriented_landmark_data()
        self.remove_oriented_landmarks_layers()
        self.reset_oriented_landmark_combo_box()

    def reset_oriented_landmark_combo_box(self):
        """
        Set the combo box to the default value " " and remove all other item of the combo box

        """
        if self.selected_oriented_landmark_combo_box.currentText() != " ":
            self.selected_oriented_landmark_combo_box.setCurrentText(" ")

        while self.selected_oriented_landmark_combo_box.count() != 1:
            index = self.selected_oriented_landmark_combo_box.count() - 1
            self.selected_oriented_landmark_combo_box.removeItem(index)

    def reset_oriented_landmark_data(self):
        """
        Reset the oriented landmarks arrays to empty

        """
        self.oriented_landmarks_positions_array = []
        self.oriented_landmarks_orientations_array = []
        self.oriented_landmarks_quaternions_array = []

    def reset_selected_slice_combo_box(self):
        """
        Reset the selected slice list to empty, set the combo box to the default value " " and remove all other item of the combo box

        """
        self.selected_slice_list = []

        if self.selected_slice_combo_box.currentText() != " ":
            self.selected_slice_combo_box.setCurrentText(" ")

        while self.selected_slice_combo_box.count() != 1:
            index = self.selected_slice_combo_box.count() - 1
            self.selected_slice_combo_box.removeItem(index)

    def reset_zoom_slider(self):
        """
        Reset the zoom slider to 100 (no zoom)

        """
        self.zoom_slider.setValue(int(self.viewer.camera.zoom * 100))

        
# ============ Remove layer ============
    def remove_image_layer(self):
        """
            Remove image layer from napari viewer

        """
        if "image" in self.viewer.layers:
            self.viewer.layers.remove('image')

    def remove_oriented_landmarks_layers(self):
        """
            Remove points layer and vectors layer from napari viewer

        """
        if "landmarks" in self.viewer.layers:
            self.viewer.layers.remove('landmarks')
        if "orientations" in self.viewer.layers:
            self.viewer.layers.remove('orientations')

    def remove_segmentation_layer(self):
        """
            Remove segmentation layer from napari viewer

        """
        if "annotations" in self.viewer.layers:
            self.viewer.layers.remove('annotations')


# ============ Reset data ============
    def remove_backup_segmentation_file(self):
        """
        Delete the backup segmentation file

        """
        temp_segmentation_data_file_path = Path(self.image_dir).joinpath("TEMP_" + self.file_name_label.text() + "_segmentation.tif")
        if temp_segmentation_data_file_path.exists():
            temp_segmentation_data_file_path.unlink()

        self.backup_check_box.setChecked(False)


# ============ Display warning/question message box ============
    def can_remove_image_data(self):
        """
        Display a question box to remove image data

        Returns
        ----------
        choice : bool
            answer to the question : True if Ok, False if Cancel (default=True)

        """
        if "image" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will delete image data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

    def can_remove_oriented_landmarks_data(self):
        """
        Display a question box to remove oriented landmarks data (from DIVA)

        Returns
        ----------
        choice : bool
            answer to the question : True if Ok, False if Cancel (default=True)

        """
        if "landmarks" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will delete oriented landmarks data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

    def can_remove_segmentation_data(self):
        """
        Display a question box to remove segmentation data

        Returns
        ----------
        choice : bool
            answer to the question : True if Ok, False if Cancel (default=True)

        """
        if "annotations" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will delete segmentation data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

    def can_remove_all(self):
        """
        Display a question box to remove all data

        Returns
        ----------
        choice : bool
            answer to the question : True if Ok, False if Cancel (default=True)

        """
        if all(layer_name in self.viewer.layers for layer_name in ["image", "annotations", "landmarks", "orientations"]):
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will delete all data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice


# ============ For testing ============
    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")



    # def find_current_axis_index(self):
    #     """
    #     If the original image dimension is 3, find the axis not displayed in the Napari viewer.

    #     Returns
    #     ----------
    #     current_axis_index : int
    #         axis index

    #     """
    #     # if axis labels named as ['z', 'y', 'x'] - used to displayed axis on image
    #     if 'x', 'y', 'z' in self.viewer.dims.axis_labels:

    #     # if axis labels named as ['0', '1', '2'] - used to displayed axis on image
    #     else:
    #         axis_labels = [eval(i) for i in self.viewer.dims.axis_labels]
    #         displayed_axes = list(self.viewer.dims.displayed)


    #     current_axis_index = list(set(axis_labels).difference(displayed_axes))
    #     if len(current_axis_index) > 0:
    #         return current_axis_index[0]
    #     else:
    #         return 0
    
    # def normalize(self, v):
    #     """
    #     Normalize a vector (x, y, z)
        
    #     Parameters
    #     ----------
    #     v : float[3]
    #         vector to normalize
        
    #     Returns
    #     ----------
    #     out : float[3]
    #         normalized vector
            
    #     """
    #     norm = np.linalg.norm(v)
    #     if norm == 0:
    #         return v
    #     return v / norm
    
# ================== TEST ==================
    # left = np.array([-1.0, 0.0, 0.0])
    # up = np.array([0.0, 1.0, 0.0])
    # forward = np.array([0.0, 0.0, 1.0])
    # test = np.array([self.oriented_landmarks_orientations_array[0][0], self.oriented_landmarks_orientations_array[0][1], self.oriented_landmarks_orientations_array[0][2]])
    
    # i = 0
    # print(self.oriented_landmarks_quaternions_array[i])
    # print(self.quaternion_from_forward_and_up_vectors(self.oriented_landmarks_orientations_array[i], left))
    
    # input_quat = np.array([0.0, 0.0, 0.0, 1.0])
    # output_forward = self.quaternion_multiply(input_quat, forward)
    
    # input_forward = np.array([0.0, 0.0, 1.0])
    # output_quat = self.quaternion_from_forward_and_up_vectors(input_forward, left)
    # print(input_forward, output_quat)
 # =============================================
 
    # def quaternion_from_forward_and_up_vectors(self, forward, up):
    #     """
    #     Transform 2 orthogonal vectors as a Quaternion (inspired by https://gist.github.com/awesomebytes/7ccbd396511db71d0a51341569fa95fa )
    #     (same as LookRotation Quaternion function in Unity)
        
    #     Parameters
    #     ----------
    #     forward : float[3]
    #         vector
    #     up : float[3]
    #         vector
        
    #     Returns
    #     ----------
    #     x, y, z, w : float[3]
    #        output quaternion 
        
    #     """
    #     v0 = self.normalize(forward)
    #     v1 = self.normalize(np.cross(self.normalize(up), v0))
    #     v2 = np.cross(v0, v1)
    #     m00, m01, m02 = v1
    #     m10, m11, m12 = v2
    #     m20, m21, m22 = v0

    #     num8 = (m00 + m11) + m22

    #     if num8 > 0.0:
    #         num = sqrt(num8 + 1.0)
    #         w = num * 0.5
    #         num = 0.5 / num
    #         x = (m12 - m21) * num
    #         y = (m20 - m02) * num
    #         z = (m01 - m10) * num
    #         return x, y, z, w

    #     if (m00 >= m11) and (m00 >= m22):
    #         num7 = sqrt(((1.0 + m00) - m11) - m22)
    #         num4 = 0.5 / num7
    #         x = 0.5 * num7
    #         y = (m01 + m10) * num4
    #         z = (m02 + m20) * num4
    #         w = (m12 - m21) * num4
    #         return x, y, z, w

    #     if m11 > m22:
    #         num6 = sqrt(((1.0 + m11) - m00) - m22)
    #         num3 = 0.5 / num6
    #         x = (m10 + m01) * num3
    #         y = 0.5 * num6
    #         z = (m21 + m12) * num3
    #         w = (m20 - m02) * num3
    #         return x, y, z, w

    #     num5 = sqrt(((1.0 + m22) - m00) - m11)
    #     num2 = 0.5 / num5
    #     x = (m20 + m02) * num2
    #     y = (m21 + m12) * num2
    #     z = 0.5 * num5
    #     w = (m01 - m10) * num2
        
    #     return x, y, z, w