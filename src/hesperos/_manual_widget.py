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
    display_warning_box,
    display_save_message_box,
    display_ok_cancel_question_box,
    display_yes_no_question_box
)
from hesperos.layout.napari_elements import disable_napari_buttons, disable_layer_widgets, reset_dock_widget, disable_dock_widget_buttons, label_colors, disable_napari_change_dim_button
from hesperos.resources._icons import get_icon_path, get_relative_icon_path

import hesperos.annotation.fetus as fetus_data
import hesperos.annotation.shoulder as shoulder_data
import hesperos.annotation.shoulder_bones as shoulder_bones_data
import hesperos.annotation.shoulder_bone_border as shoulder_bone_border_data
import hesperos.annotation.shoulder_deltoid as shoulder_deltoid_data
import hesperos.annotation.mouse_embryon as mouse_embryon_data
import hesperos.annotation.larva as larva_data
import hesperos.annotation.feta as feta_data
from hesperos.annotation.structuresubpanel import StructureSubPanel


# ============ Import python packages ============
import json
import napari
import functools
import numpy as np
import tifffile as tif
import SimpleITK as sitk
from pathlib import Path
from napari._vispy import VispyCanvas

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
        # reset_dock_widget(napari_viewer)

        super().__init__()

        napari.utils.notifications.WarningNotification.blocked = True
        self.viewer = napari_viewer

        disable_napari_buttons(self.viewer)
        self.viewer.dims.events.current_step.connect(self.update_go_to_selected_slice_push_button_check_status)

        self.generate_main_layout()

        napari.DOCK_WIDGETS.append(self)
        disable_dock_widget_buttons(self.viewer)
        # self.generate_help_layout()


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
        self.add_annotation_panel(2)
        self.add_sub_annotation_panel(3)
        self.add_slice_selection_panel(4)
        self.add_reset_export_panel(5)

        # Display status (cannot display progressing bar because napari is freezing)
        self.status_label = add_label(
            text='Ready',
            layout=self.layout,
            row=6,
            column=0,
            visibility=True
            )

        self.toggle_panels(["annotation_panel", "slice_selection_panel", "reset_export_panel"], False)

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
        self.import_panel = QGroupBox("1. IMPORT 3D IMAGE")
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
            tooltip_text="Import DICOM data from a folder containing one serie",
        )

        self.import_file_image_push_button = add_push_button(
            name="Open image file",
            layout=self.import_layout,
            callback_function=functools.partial(self.set_image_with_path, "file"),
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Import image data from one file",
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
            tooltip_text="Zoom the main camera",
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
            tooltip_text="Use a predefined HU contrast",
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
        self.annotation_panel = QGroupBox("2. ANNOTATE")
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
            tooltip_text="Open a segmentation file with the same size of the original image",
        )

        # Annotations tools are created in another layout
        self.tool_annotation_layout = QHBoxLayout()

        self.undo_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('undo')),
            layout=self.tool_annotation_layout,
            callback_function=self.undo_segmentation,
            row=0,
            column=0,
            tooltip_text="Undo the last painting action",
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
            tooltip_text="Select the pre-defined structure to annotate",
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
        self.reset_export_panel = QGroupBox("3. EXPORT ANNOTATION")
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
            tooltip_text="Export only the segmented data",
        )

        self.reset_push_button = add_push_button(
            name="Delete all",
            layout=self.reset_export_layout,
            callback_function=self.reset_segmentation,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Delete all segmentation data",
        )

        self.backup_check_box = add_check_box(
            text="Automatic segmentation backup",
            layout=self.reset_export_layout,
            callback_function=self.activate_backup_segmentation,
            row=1,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            tooltip_text="Activate the automatic backup of the segmentation data when the slice inex is changed",
        )
        self.backup_check_box.setChecked(False)

        self.reset_export_panel.setLayout(self.reset_export_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.reset_export_panel, row, column)

    def add_view_panel(self, row, column):
        """
        Create view panel

        Parameters
        ----------
        row : int
            row position of the panel in the help QGridLayout
        column : int
            column position of the panel in the help QGridLayout

        """

        # === Set panel parameters ===
        self.view_panel = QGroupBox("3D VIEW AXIS")
        self.view_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.view_layout = QGridLayout()
        self.view_layout.setSpacing(5)
        self.view_layout.setContentsMargins(10, 10, 10, 10)

        # === Add Qwidgets to the panel layout ===
        self.view_image_1 = add_image_widget(
            name="view1",
            layout=self.view_layout,
            image_path='',
            row=0,
            column=0,
            visibility=False,
            minimum_width=0
            )

        self.view_image_2 = add_image_widget(
            name="view2",
            layout=self.view_layout,
            image_path='',
            row=0,
            column=1,
            visibility=False,
            minimum_width=0
            )

        self.view_panel.setLayout(self.view_layout)

        # === Add panel to the help layout ===
        self.help_layout.addWidget(self.view_panel, row, column)

    def add_atlas_panel(self, row, column):
        """
        Create atlas panel

        Parameters
        ----------
        row : int
            row position of the panel in the help QGridLayout
        column : int
            column position of the panel in the help QGridLayout

        """

        # === Set panel parameters ===
        self.atlas_panel = QGroupBox("ATLAS")
        self.atlas_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.atlas_layout = QGridLayout()
        self.atlas_layout.setSpacing(5)
        self.atlas_layout.setContentsMargins(10, 10, 10, 10)

        # === Add Qwidgets to the panel layout ===
        self.atlas_label = add_label(
            text='',
            layout=self.atlas_layout,
            row=0,
            column=0)

        self.canvas_ax1 = VispyCanvas(
            keys=None,
            vsync=True,
            parent=self.atlas_label,
        )

        self.atlas_panel.setLayout(self.atlas_layout)

        # === Add panel to the help layout ===
        self.help_layout.addWidget(self.atlas_panel, row, column)

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
        self.slice_selection_panel = QGroupBox("3. SELECT SLICES OF INTEREST")
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
            tooltip_text="Add the currently displayed z-index in the drop-down menu. Click on the map button to go to the selected slice.",
            isHBoxLayout=True,
        )

        self.remove_selected_slice_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('minus')),
            layout=self.tool_slice_selection_layout,
            callback_function=self.remove_selected_slice,
            row=0,
            column=1,
            tooltip_text="Remove the currently displayed z-index in the drop-down menu.",
            isHBoxLayout=True,
        )
        
        self.go_to_selected_slice_push_button = add_icon_push_button(
            icon=QIcon(get_icon_path('map')),
            layout=self.tool_slice_selection_layout,
            callback_function=self.go_to_selected_slice,
            row=0,
            column=2,
            tooltip_text="Go to the z-index selected in the drop-down menu.",
            isHBoxLayout=True,
        )
        self.go_to_selected_slice_push_button.setCheckable(True)
        
        self.slice_selection_text = add_label(
            text='Slice: ',
            layout=self.tool_slice_selection_layout,
            row=0,
            column=2,
            isHBoxLayout=True,
            )

        self.slice_selection_layout.addLayout(self.tool_slice_selection_layout, 0, 0)
        
        self.selected_slice_combo_box = add_combo_box(
            list_items=[" "],
            layout=self.slice_selection_layout,
            callback_function=self.go_to_selected_slice,
            row=0,
            column=1,
            tooltip_text="Select a z-index from the list to work with it more easily.",
        )

        self.slice_selection_panel.setLayout(self.slice_selection_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.slice_selection_panel, row, column)
        

# ============ Toggle widgets and panel ============
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
                self.annotation_combo_box.setVisible(isVisible)
                self.import_segmentation_push_button.setVisible(isVisible)
                self.undo_push_button.setVisible(isVisible)
                self.lock_push_button.setVisible(isVisible)
            
            elif panel_name == "slice_selection_panel":
                self.slice_selection_panel.setVisible(isVisible)
                self.add_selected_slice_push_button.setVisible(isVisible)
                self.remove_selected_slice_push_button.setVisible(isVisible)
                self.go_to_selected_slice_push_button.setVisible(isVisible)
                self.slice_selection_text.setVisible(isVisible)
                self.selected_slice_combo_box.setVisible(isVisible)

            elif panel_name == "reset_export_panel":
                self.reset_export_panel.setVisible(isVisible)
                self.backup_check_box.setVisible(isVisible)
                self.reset_push_button.setVisible(isVisible)
                self.export_push_button.setVisible(isVisible)

            elif panel_name == "view_panel":
                self.view_panel.setVisible(isVisible)
                self.view_image_1.setVisible(isVisible)
                self.view_image_2.setVisible(isVisible)

            elif panel_name == "atlas_panel":
                self.atlas_panel.setVisible(isVisible)
                self.atlas_label.setVisible(isVisible)

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
            toggle_slice_selection_panel = False
            toggle_napari_dim_button = True
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = True
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = False
            toggle_napari_dim_button = True
            toggle_mouse_embryon = False

        elif structure_name == "Shoulder Bones":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = True
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = True
            toggle_napari_dim_button = False
            toggle_mouse_embryon = False
        
        elif structure_name == "Shoulder Bone Borders":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = True
            toggle_slice_selection_panel = True
            toggle_napari_dim_button = False
            toggle_mouse_embryon = False
        
        elif structure_name == "Shoulder Deltoid":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = True
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = True
            toggle_napari_dim_button = False
            toggle_mouse_embryon = False

        elif structure_name == "Feta Challenge":
            toggle_feta = True
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = False
            toggle_napari_dim_button = True
            toggle_mouse_embryon = False
            
        elif structure_name == "Larva":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = True
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = True
            toggle_napari_dim_button = True
            toggle_mouse_embryon = False
        
        elif structure_name == "Mouse Embryon":
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = True
            toggle_napari_dim_button = True
            toggle_mouse_embryon = True
            
        else:
            toggle_feta = False
            toggle_fetus = False
            toggle_larva = False
            toggle_shoulder = False
            toggle_shoulder_bones = False
            toggle_shoulder_deltoid = False
            toggle_shoulder_bone_borders = False
            toggle_slice_selection_panel = False
            toggle_napari_dim_button = False
            toggle_mouse_embryon = False
            
        # == toggle sub panels ==
        self.feta.toggle_sub_panel(toggle_feta)
        self.fetus.toggle_sub_panel(toggle_fetus)
        self.shoulder.toggle_sub_panel(toggle_shoulder)
        self.shoulder_bones.toggle_sub_panel(toggle_shoulder_bones)
        self.shoulder_bone_borders.toggle_sub_panel(toggle_shoulder_bone_borders)
        self.shoulder_deltoid.toggle_sub_panel(toggle_shoulder_deltoid)
        self.mouse_embryon.toggle_sub_panel(toggle_mouse_embryon)
        self.larva.toggle_sub_panel(toggle_larva)
        self.toggle_panels(["slice_selection_panel"], toggle_slice_selection_panel)
        
        # == reset widgets ==
        self.reset_annotation_radio_button_checked_id()
        self.reset_annotation_layer_selected_label()
        
        # == Update dimension button and panel name ==
        self.update_reset_export_panel_title(toggle_slice_selection_panel)
        disable_napari_change_dim_button(self.viewer, toggle_napari_dim_button)

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


# ============ Update widget status or panel title ============
    def update_reset_export_panel_title(self, isSelectionSlicePanelVisible):
        """
        Update the number in the ResetExport panel title to match the actual number of panels displayed (based on the SelectionSlice panel display)
        
        Parameters
        ----------
        isSelectionSlicePanelVisible : bool
            visible status of the SelectionSlice panel
            
        """
        if isSelectionSlicePanelVisible:
            self.reset_export_panel.setTitle("4. EXPORT ANNOTATION")
        else:
            self.reset_export_panel.setTitle("3. EXPORT ANNOTATION")
                
    def update_go_to_selected_slice_push_button_check_status(self, event):
        """
        Update the checked status of the go_to_selected_slice push button according to the currently selected slice and the currently displayed slice
        
        Parameters
        ----------
        event : event
            event with the index of the current slice displayed in value as (x, y, z)      
        
        """       
        if len(event.value) == 3:
            if (self.go_to_selected_slice_push_button.isChecked() == True) and (self.selected_slice_combo_box.currentText() != " "):
                current_slice_z = self.viewer.dims.current_step[0]
                selected_slice_z = int(self.selected_slice_combo_box.currentText())
                if current_slice_z != selected_slice_z:
                    self.go_to_selected_slice_push_button.setChecked(False)
                    
            elif (self.go_to_selected_slice_push_button.isChecked() == False) and (self.selected_slice_combo_box.currentText() != " "):
                current_slice_z = self.viewer.dims.current_step[0]
                selected_slice_z = int(self.selected_slice_combo_box.currentText())
                if current_slice_z == selected_slice_z:
                    self.go_to_selected_slice_push_button.setChecked(True)
                
        
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
            display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image")
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

        # if (extensions[-1] == ".tif") or (extensions[-1] == ".tiff"):
        #     image_arr = tif.imread(file_path)
        #     self.image_sitk = sitk.Image(image_arr.shape[2], image_arr.shape[1], image_arr.shape[0], sitk.sitkInt16)
        #     self.file_name_label.setText(Path(file_path).stem)
        
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
            display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image")
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
                return None

        else:
            file_path = str(default_file_path)

        extensions = Path(file_path).suffixes

        # if (extensions[-1] == ".tif") or (extensions[-1] == ".tiff"):
        #     segmentation_arr = tif.imread(file_path)
        
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
                display_warning_box(self, "Error", "Incorrect NIFTI format : negative value")
                return
            
        else:
            return None
            
        if len(segmentation_arr.shape) != 3:
            display_warning_box(self, "Error", "Incorrect file size. Need to be a 3D image")
            return None

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
        Import metadata containing in the 'ImageDescription'/'Hesperos_SelectedSlices' as a list. (works only for tiff file TOIMPROVE)   
        
        Parameters
        ----------
        segmentation_sitk : SimpleITK image
            segmentation data in sitk format
        
        """        
        try:
            description = json.loads(segmentation_sitk.GetMetaData('ImageDescription'))
            loaded_selected_slice_list = json.loads(description['Hesperos_SelectedSlices'])
        except:
            return

        if loaded_selected_slice_list != []:
            self.selected_slice_list = loaded_selected_slice_list

            # if len(self.selected_slice_list) >= 30:
            #     display_warning_box(self, "Error", "More than 30 selected slices are not allowed. Please remove some selected slices to add new ones.")
            #     return
        
            self.selected_slice_list.sort()

            for slice_index in self.selected_slice_list:
                new_text = str(slice_index)
                self.selected_slice_combo_box.addItem(new_text)


# ============ Export data ============
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
                        description = {"Hesperos_SelectedSlices" : json.dumps(self.selected_slice_list)}
                        # tif.imsave(file_path, segmentation_arr, description=json.dumps(self.selected_slice_list))
                        tif.imsave(file_path, segmentation_arr, description=json.dumps(description))
                        
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
                display_warning_box(self, "Error", "No segmentation data find")
                return

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

            self.reset_zoom_slider()
            self.reset_lock_push_button()
            self.go_to_selected_slice_push_button.setChecked(False)
            self.backup_check_box.setChecked(False)
            self.default_contrast_combo_box.setCurrentText("")

            self.toggle_import_panel_widget(True, file_type)
            self.toggle_panels(["annotation_panel", "reset_export_panel"], True)

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
                    self.reset_selected_slice()

            else:
                segmentation_arr = np.zeros(image_arr.shape, dtype=np.int8)
                self.set_segmentation_layer(segmentation_arr)
                self.reset_lock_push_button()
                self.go_to_selected_slice_push_button.setChecked(False)
                self.reset_selected_slice()

            self.annotation_combo_box.setCurrentText("Choose a structure")  
            self.status_label.setText("Ready")

        else:
            return

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
                        display_warning_box(self, "Error", "Size of the segmentation file doesn't correspond to the size of the source image")
                        self.status_label.setText("Ready")
                        return

                self.set_segmentation_layer(segmentation_arr)
                self.reset_lock_push_button()
                self.go_to_selected_slice_push_button.setChecked(False)
                self.reset_selected_slice()
                self.import_selected_slice(segmentation_sitk)

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
        self.viewer.add_image(array, name='image')
        self.viewer.layers['image'].contrast_limits = (np.min(array), np.max(array))
        disable_layer_widgets(self.viewer, layer_name='image', layer_type='image')
        self.viewer.layers['image'].events.contrast_limits.connect(self.reset_default_contrast_combo_box)

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


# ============ Custom widget callbacks ============
    def add_selected_slice(self):
        """
        Add the z index of the actual slice display in the selected_slice_combo_box

        """
        selected_slice_z = self.viewer.dims.current_step[0]
        
        # if len(self.selected_slice_list) >= 30:
        #     display_warning_box(self, "Error", "More than 30 selected slices are not allowed. Please remove some selected slices to add new ones.")
        #     return

        if selected_slice_z in self.selected_slice_list:
            return

        else:
            self.selected_slice_list.append(selected_slice_z)
            self.selected_slice_list.sort()
            
            list_index = self.selected_slice_list.index(selected_slice_z)
            self.selected_slice_combo_box.insertItem(list_index + 1, str(selected_slice_z))
            self.selected_slice_combo_box.setCurrentText(str(selected_slice_z))

    def go_to_selected_slice(self):
        """
        Change the currently displayed slice according to the slice index selected in the selected_slice_combo_box

        """
        if self.go_to_selected_slice_push_button.isChecked() == True:
            if self.selected_slice_combo_box.currentText() != " ":
                # json to tuple
                # selected_slice = eval(self.selected_slice_combo_box.currentText())
                selected_slice_z = int(self.selected_slice_combo_box.currentText())
                _, y, x = self.viewer.layers['image'].data.shape
                self.viewer.dims.current_step = (selected_slice_z, y, x)  
            else:
                self.go_to_selected_slice_push_button.setChecked(False) 
                   
        else:
            if self.selected_slice_combo_box.currentText() != " ":  
                current_slice_z = self.viewer.dims.current_step[0]
                selected_slice_z = int(self.selected_slice_combo_box.currentText())
                if current_slice_z != selected_slice_z:
                    _, y, x = self.viewer.layers['image'].data.shape
                    self.viewer.dims.current_step = (selected_slice_z, y, x)  
                else:                      
                    self.go_to_selected_slice_push_button.setChecked(True)
            
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

    def reset_zoom_slider(self):
        """
        Reset the zoom slider to 100 (no zoom)

        """
        self.zoom_slider.setValue(int(self.viewer.camera.zoom * 100))

    def reset_selected_slice(self):
        """
        Reset the selected slice list to empty, set the combo box to the default value " " and remove all other item of the combo box
        
        """
        self.selected_slice_list = []

        if self.selected_slice_combo_box.currentText() != " ":
            self.selected_slice_combo_box.setCurrentText(" ")

        while self.selected_slice_combo_box.count() != 1:
            index = self.selected_slice_combo_box.count() - 1 
            self.selected_slice_combo_box.removeItem(index)


# ============ Remove or Reset data ============
    def remove_image_layer(self):
        """
            Remove image layer from napari viewer

        """
        if "image" in self.viewer.layers:
            self.viewer.layers.remove('image')

    def remove_segmentation_layer(self):
        """
            Remove segmentation layer from napari viewer

        """
        if "annotations" in self.viewer.layers:
            self.viewer.layers.remove('annotations')

    def remove_backup_segmentation_file(self):
        """
            Delete the backup segmentation file

        """
        temp_segmentation_data_file_path = Path(self.image_dir).joinpath("TEMP_" + self.file_name_label.text() + "_segmentation.tif")
        if temp_segmentation_data_file_path.exists():
            temp_segmentation_data_file_path.unlink()

        self.backup_check_box.setChecked(False)

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
        else:
            return

    def remove_selected_slice(self):
        """
        Remove the current z index displayed in the selected_slice_combo_box and set the combo box to the default value " "
        
        """
        if len(self.selected_slice_list) == 0:
            return
        
        current_slice_z = self.viewer.dims.current_step[0]

        if current_slice_z in self.selected_slice_list:
            list_index = self.selected_slice_list.index(current_slice_z) 
            self.selected_slice_combo_box.removeItem(list_index + 1)   
            self.selected_slice_list.remove(current_slice_z)
            self.selected_slice_combo_box.setCurrentText(" ")
            

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
        if "image" in self.viewer.layers or "annotations" in self.viewer.layers:
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


# ============ Comments ============
    # def slicer_change(self):
    #     index = self.viewer.dims.current_step
    #     print(index)

    #     # image_to_display = self.image[index, :, :]

    #     if 'image' in self.viewer.layers:
    #             image_arr = self.viewer.layers['image'].data


    #     pixmap = QPixmap(image_path)
    #     view_image_1.setPixmap(pixmap)
    
    

    # def generate_help_layout(self):

    #     self.help_layout = QGridLayout()
    #     self.help_layout.setContentsMargins(10, 10, 10, 10)
    #     # self.help_layout.setAlignment(QtCore.Qt.AlignTop)
    #     self.help_layout.setSpacing(4)

    #     self.add_view_panel(row=0, column=0)
    #     self.add_atlas_panel(row=0, column=1)

    #     self.help_container = QWidget()

    #     self.help_container.setLayout(self.help_layout)

    #     self.help_dock = self.viewer.window.add_dock_widget(widget=self.help_container, area='bottom')  
    
    
    # def import_selected_slice_metadata_from_nifti(self, img_sitk):
    #     """
    #     TODO

    #     """
    #     try:
    #         return img_sitk.GetMetaData("Hesperos_SelectedSlices")
    #     except:
    #         return []