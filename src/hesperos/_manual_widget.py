# ============ Import python files ============
from hesperos.layout.gui_elements import (
    add_push_button,
    add_icon_push_button,
    add_label,
    add_slider,
    add_combobox,
    add_image_widget,
    display_warning_box,
    display_save_message_box,
    display_ok_cancel_question_box
)
from hesperos.layout.napari_elements import disable_napari_buttons, disable_layer_widgets
from hesperos.resources._icons import get_icon_path, get_relative_icon_path

import hesperos.annotation.fetus as fetus_data
import hesperos.annotation.shoulder as shoulder_data
import hesperos.annotation.feta as feta_data
from hesperos.annotation.structuresubpanel import StructureSubPanel

# ============ Import python packages ============
import os
import napari
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
SEGM_METHODS_PANEL_ALIGN = (
    "center"  # Alignment of text in pushbuttons in methods chooser panel
)


# ============ Define QWidget Class ============
class ManualSegmentationWidget(QWidget):
    """
    QWidget class for Manual Segmentation in NAPARI

    """
    def __init__(self, napari_viewer):
        """ Initilialisation of the widget in the current napari viewer

        Parameters
        ----------
        napari_viewer : napari.Viewer
            active (unique) instance of the napari viewer

        """
        super().__init__()

        napari.utils.notifications.WarningNotification.blocked = True
        self.viewer = napari_viewer

        disable_napari_buttons(self.viewer)

        self.generate_main_layout()
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
        self.add_loading_panel(1)

        self.add_annotation_panel(2)
        self.add_sub_annotation_panel(3)

        self.add_reset_save_panel(4)

        self.enable_panels(["annotation_panel", "reset_save_panel"], False)

        self.setLayout(self.layout)

    def add_sub_annotation_panel(self, row):
        """
        Create annotation sub panel with the list of all struture to annotate

        Parameters
        ----------
        row : int
            row position of the sub panel in the main QGridLayout

        """
        self.fetus = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=fetus_data.LIST_STRUCTURES,
            dict_substructures=fetus_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.feta = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=feta_data.LIST_STRUCTURES,
            dict_substructures=feta_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])

        self.shoulder = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=shoulder_data.LIST_STRUCTURES,
            dict_substructures=shoulder_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=shoulder_data.DICT_SUB_SUB_STRUCTURES)

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


    def add_loading_panel(self, row, column=0):
        """
        Create loading panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """

        # === Set panel parameters ===
        self.loading_panel = QGroupBox("1. LOAD IMAGE")
        self.loading_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.loading_layout = QGridLayout()
        self.loading_layout.setSpacing(5)
        self.loading_layout.setContentsMargins(10, 10, 10, 10)

        # === Add Qwidgets to the panel layout ===
        self.load_dicom_image_push_button = add_push_button(
            name="Open DICOM folder",
            layout=self.loading_layout,
            callback_function=self.load_dicom_image,
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.load_file_image_push_button = add_push_button(
            name="Open image file",
            layout=self.loading_layout,
            callback_function=self.load_image,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.file_name_text = add_label(
            text='File/Folder name: ',
            layout=self.loading_layout,
            row=1,
            column=0,
            column_span=1,
            )

        self.file_name = add_label(
            text='',
            layout=self.loading_layout,
            row=1,
            column=1,
            column_span=1,
            )

        self.loading_panel.setLayout(self.loading_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.loading_panel, row, column)

        # === Make widgets visible (after adding to the main layout to preventing them from briefly appearing in a separate window) ===
        self.loading_panel.setVisible(True)
        self.load_dicom_image_push_button.setVisible(True)
        self.load_file_image_push_button.setVisible(True)
        self.file_name_text.setVisible(True)
        self.file_name.setVisible(True)

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
        self.annotation_text = add_label(
            text="Choose a type of structure:",
            layout=self.annotation_layout,
            row=0,
            column=0,
        )

        self.annotation_combo_box = add_combobox(
            layout=self.annotation_layout,
            items=["", "Fetus", "Shoulder", "Feta Challenge"],
            callback_function=self.toggle_annotation_sub_panel,
            row=0,
            column=1,
        )
        # self.annotation_combo_box.setStyleSheet("QComboBox::disabled{background-color: black; color: darkgray;}")

        self.load_label_push_button = add_push_button(
            name="Open segmentation file",
            layout=self.annotation_layout,
            callback_function=self.load_label,
            row=1,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )
        # self.load_label_push_button.setStyleSheet("QPushButton::disabled{background-color: black; color: darkgray;}")

        # Annotations tools are created in another layout
        self.tool_annotation_layout = QHBoxLayout()

        self.undo_push_button = add_icon_push_button(
            name="",
            icon=QIcon(get_icon_path('undo')),
            layout=self.tool_annotation_layout,
            callback_function=self.undo_label,
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
            isBoxLayout=True,
        )
        # self.undo_push_button.setStyleSheet("QPushButton::disabled{background-color: black; color: darkgray;}")

        self.lock_push_button = add_icon_push_button(
            name="",
            icon=QIcon(get_icon_path('unlock')),
            layout=self.tool_annotation_layout,
            callback_function=self.lock_slide,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
            isBoxLayout=True,
        )
        self.lock_push_button.setCheckable(True)
        # self.lock_push_button.setStyleSheet("QPushButton::disabled{background-color: black; color: darkgray;}")

        self.zoom_slider = add_slider(
            layout=self.tool_annotation_layout,
            bounds=[50, 500],
            callback_function=self.zoom,
            row=0,
            column=2,
            isBoxLayout=True
        )
        self.zoom_slider.setStyleSheet("""
            QSlider::handle:horizontal {{
                image: url({});
                margin: -30px 0px;
                width: 25px;
                background: transparent;
                }}""".format(get_relative_icon_path('zoom')))

        self.annotation_layout.addLayout(self.tool_annotation_layout, 2, 0, 1, 2)
        self.annotation_panel.setLayout(self.annotation_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.annotation_panel, row, column)

    def add_reset_save_panel(self, row, column=0):
        """
        Create reset and save panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """

        # === Set panel parameters ===
        self.reset_save_panel = QGroupBox("3. SAVE ANNOTATION")
        self.reset_save_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.reset_save_layout = QGridLayout()
        self.reset_save_layout.setSpacing(15)

        # === Add Qwidgets to the panel layout ===
        self.backup_push_button = add_icon_push_button(
            name="",
            icon=QIcon(get_icon_path('backup')),
            layout=self.reset_save_layout,
            callback_function=self.activate_backup_label,
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )
        self.backup_push_button.setCheckable(True)

        self.save_push_button = add_push_button(
            name="Save",
            layout=self.reset_save_layout,
            callback_function=self.save_label,
            row=0,
            column=1,
            column_span=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.reset_push_button = add_push_button(
            name="Delete all",
            layout=self.reset_save_layout,
            callback_function=self.reset_label,
            row=0,
            column=2,
            column_span=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.reset_save_panel.setLayout(self.reset_save_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.reset_save_panel, row, column)

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

    def enable_panels(self, list_panel_names, isVisible):
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
                self.annotation_text.setVisible(isVisible)
                self.annotation_combo_box.setVisible(isVisible)
                self.load_label_push_button.setVisible(isVisible)
                self.zoom_slider.setVisible(isVisible)
                self.undo_push_button.setVisible(isVisible)
                self.lock_push_button.setVisible(isVisible)

            elif panel_name == "reset_save_panel":
                self.reset_save_panel.setVisible(isVisible)
                self.backup_push_button.setVisible(isVisible)
                self.reset_push_button.setVisible(isVisible)
                self.save_push_button.setVisible(isVisible)

            elif panel_name == "view_panel":
                self.view_panel.setVisible(isVisible)
                self.view_image_1.setVisible(isVisible)
                self.view_image_2.setVisible(isVisible)
            
            elif panel_name == "atlas_panel":
                self.atlas_panel.setVisible(isVisible)
                self.atlas_label.setVisible(isVisible)

    def toggle_annotation_sub_panel(self):
        """
            Toggle sub panel of the structure to annotate
        """
        structure_name = self.annotation_combo_box.currentText()

        isFetus = self.fetus.subpanel.isVisible()
        isShoulder = self.shoulder.subpanel.isVisible()
        isFeta = self.feta.subpanel.isVisible()

        if (isFetus and structure_name != "Fetus") or (isShoulder and structure_name != "Shoulder") or (isFeta and structure_name != "Feta Challenge"):
            canRemoveLabel = self.can_remove_label_data()
        elif (isFetus and structure_name == "Fetus") or (isShoulder and structure_name == "Shoulder") or (isFeta and structure_name == "Feta Challenge"):
            return
        else:
            canRemoveLabel = True

        if canRemoveLabel:
            if structure_name == "Fetus":
                toggle_fetus = True
                toggle_shoulder = False
                toggle_feta = False

            elif structure_name == "Shoulder":
                toggle_fetus = False
                toggle_shoulder = True
                toggle_feta = False

            elif structure_name == "Feta Challenge":
                toggle_fetus = False
                toggle_shoulder = False
                toggle_feta = True

            else:
                toggle_fetus = False
                toggle_shoulder = False
                toggle_feta = False

            self.fetus.toggle_sub_panel(toggle_fetus)
            self.shoulder.toggle_sub_panel(toggle_shoulder)
            self.feta.toggle_sub_panel(toggle_feta)

            # Reset label data
            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()

        else:
            if isFetus:
                self.annotation_combo_box.setCurrentText("Fetus")
            elif isShoulder:
                self.annotation_combo_box.setCurrentText("Shoulder")
            elif isFeta:
                self.annotation_combo_box.setCurrentText("Feta Challenge")
            else:
                self.annotation_combo_box.setCurrentText("")

# ============ Define callbacks ============
    def load_dicom_image(self):
        """
        Load a complete DICOM serie and convert it in a .nii file to be directly open in Napari.
        The created .nii file will be deleted when saving the segmentation (see save_segmentation function).
        """

        dicom_path = QFileDialog.getExistingDirectory(self, 'Choose a DICOM serie directory')
        self.img_dir = dicom_path

        if dicom_path == "":
            return
        # if not glob.glob('*.dcm'):
        #     display_warning_box(self, "Error", "No DICOM files in the directory")
        #     return


        reader = sitk.ImageSeriesReader()
        img_names = reader.GetGDCMSeriesFileNames(dicom_path)
        reader.SetFileNames(img_names)
        self.image_sitk = reader.Execute()

        image = sitk.GetArrayFromImage(self.image_sitk) # z, y, x
        #ITK's Image class does not have a bracket operator. It has a GetPixel which takes an ITK Index object as an argument, which is an array ordered as (x,y,z). This is the convention that SimpleITK's Image class uses for the GetPixel method as well.
        # While in numpy, an array is indexed in the opposite order (z,y,x).

        canRemove = self.can_remove_all()

        if canRemove:
            self.remove_image()
            self.viewer.add_image(image, name='image')

            disable_layer_widgets(self.viewer, 'image')

            self.enable_panels(["annotation_panel", "reset_save_panel"], True)
            self.reset_zoom_slider()

            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()

            self.fetus.toggle_sub_panel(False)
            self.shoulder.toggle_sub_panel(False)
            self.feta.toggle_sub_panel(False)
            self.annotation_combo_box.setCurrentText("")

            self.file_name.setText(Path(dicom_path).stem)

        else:
            return

    def load_image(self):
        """
            Load an image file of type .tiff, .tif, .nii.gz
        """

        files_types = "TIF (*.tif);;TIFF (*.tiff);;NIFTI compressed (*.nii.gz)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a image file", "" , files_types )

        if file_path == "":
            return

        extensions = Path(file_path).suffixes
        self.img_dir = Path(file_path).parents[0]

        if len(extensions) == 1:
            if (extensions[0] == ".tif") or (extensions[0] == ".tiff"):           
                image = tif.imread(file_path)
                self.image_sitk = sitk.Image(image.shape[2], image.shape[1], image.shape[0], sitk.sitkInt16)
       
        elif len(extensions) == 2:
            if (extensions[0] == ".nii") and (extensions[1] == ".gz"):               
                self.image_sitk = sitk.ReadImage(file_path)
                image = sitk.GetArrayFromImage(self.image_sitk)
        else:
            return

        canRemove = self.can_remove_all()

        if canRemove:
            self.remove_image()
            self.viewer.add_image(image, name='image')

            disable_layer_widgets(self.viewer, 'image')

            self.enable_panels(["annotation_panel", "reset_save_panel"], True)
            self.reset_zoom_slider()

            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()

            self.fetus.toggle_sub_panel(False)
            self.shoulder.toggle_sub_panel(False)
            self.feta.toggle_sub_panel(False)
            self.annotation_combo_box.setCurrentText("")

            self.file_name.setText(Path(file_path).stem)

        else:
            return

    def load_label(self):
        """
            Load label image file of type .tiff, .tif or .nii.gz
        """

        files_types = "TIF (*.tif);;TIFF (*.tiff);;NIFTI compressed (*.nii.gz)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a segmentation file", "" , files_types )

        if file_path == "":
            return

        canRemoveLabel = self.can_remove_label_data()

        if canRemoveLabel:
            self.remove_label()

            extensions = Path(file_path).suffixes

            if len(extensions) == 1:
                if (extensions[0] == ".tif") or (extensions[0] == ".tiff"): 
                    label = tif.imread(file_path)
                    self.add_label_layers(label_data=label)

            elif len(extensions) == 2:
                if (extensions[0] == ".nii") and (extensions[1] == ".gz"):
                    label_sitk = sitk.ReadImage(file_path)
                    label = sitk.GetArrayFromImage(label_sitk)
                    label = label.astype(np.uint8)
                    # self.originalType = label.dtype

                    if any(n < 0 for n in np.unique(label)):
                        display_warning_box(self, "Error", "Incorrect NIFTI format : negative value")
                        return
                    self.add_label_layers(label_data=label)
            else:
                return

            self.reset_annotation_radio_buttons()

            # self.fetus.toggle_sub_panel(False)
            # self.shoulder.toggle_sub_panel(False)
            # self.feta.toggle_sub_panel(False)
            # self.annotation_combo_box.setCurrentText("")

        else:
            return

    def add_label_layers(self, label_data=[]):
        """
        Add a new layer to the NAPARI viewer for annotation.
        New layer can be empty for initialisation.

        Parameters
        ----------
        label_data : 3Darray
            labelled data with the same size than the raw image (display in the 'image' layer)

        """
        if hasattr(self.viewer, 'layers'):
            if 'image' in self.viewer.layers:
                source_img = self.viewer.layers['image'].data

                if label_data == []:
                    label_img = np.zeros(source_img.shape, dtype=np.int8)
                else:
                    label_img = label_data
                    if label_img.shape != source_img.shape:
                        display_warning_box(self, "Error", "Size of the segmentation file doesn't correspond to the size of the source image")
                        return


                labels_layer = self.viewer.add_labels(label_img, name='annotations')

                if self.annotation_combo_box.currentText() == "Fetus":
                    self.viewer.layers['annotations'].selected_label = self.fetus.nbr_buttons
                elif self.annotation_combo_box.currentText() == "Shoulder":
                    self.viewer.layers['annotations'].selected_label = self.shoulder.nbr_buttons
                elif self.annotation_combo_box.currentText() == "Feta Challenge":
                    self.viewer.layers['annotations'].selected_label = self.feta.nbr_buttons
                else:
                    self.viewer.layers['annotations'].selected_label = 0

                self.viewer.layers['annotations'].mode = "PAINT"

                disable_layer_widgets(self.viewer, 'annotations')

                # qctrl = self.viewer.window._qt_viewer.controls.widgets[self.viewer.layers['annotations']]
                # qctrl.opacitySlider.setMaximum(0.8)
            else:
                display_warning_box(self, "Error", "Load first a image")

        else:
            display_warning_box(self, "Error", "Load first a image")

    def zoom(self):
        """
            Zoom the camera view of the main canvas of NAPARI
        """
        # TODO check value slider
        self.viewer.camera.zoom = self.zoom_slider.value() / 100

    def undo_label(self):
        """
            Undo last operation of annotation
        """
        if hasattr(self.viewer, 'layers'):
            if 'annotations' in self.viewer.layers:
                label_layer = self.viewer.layers['annotations']
                label_layer.undo()

    def lock_slide(self):
        """
            TODO
        """

        if self.lock_push_button.isChecked() == True:
            self.lock_push_button.setIcon(QIcon(get_icon_path('lock')))
        else:
            self.lock_push_button.setIcon(QIcon(get_icon_path('unlock')))

    def save_label(self):
        """
            Save the labelled data as a unique 3D image, or multiple 3D images (one by label)
        """
        files_types = "TIFF (*.tiff);;TIF (*.tif);;NIFTI compressed (*.nii.gz)"

        default_filepath = Path(self.img_dir).joinpath("segmentation.tif")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Segmentation", str(default_filepath), files_types)

        # If choose "Cancel"
        if file_path == "":
            return

        if hasattr(self.viewer, 'layers'):
            if "annotations" in self.viewer.layers:

                saving_mode = display_save_message_box(
                    "Saving Mode",
                    "Do you want to save all label in once file, or independently ?",
                )

                label_img = self.viewer.layers['annotations'].data

                extensions = Path(file_path).suffixes

                if saving_mode: # if All
                    if len(extensions) == 1:
                        if (extensions[0] == ".tif") or (extensions[0] == ".tiff"): 
                            tif.imsave(file_path, label_img)
                    elif len(extensions) == 2:
                        if (extensions[0] == ".nii") and (extensions[1] == ".gz"):
                            result_image_sitk = sitk.GetImageFromArray(label_img.astype(np.uint16))
                            # result_image_sitk = sitk.GetImageFromArray(label_img)
                            result_image_sitk.CopyInformation(self.image_sitk)
                            sitk.WriteImage(result_image_sitk, file_path)

                else: # If independently
                    structure_name = self.annotation_combo_box.currentText()
                    if structure_name == "Fetus":
                        structure_list = self.fetus.list_structure_name
                    elif structure_name == "Shoulder":
                        structure_list = self.shoulder.list_structure_name
                    elif structure_name == "Feta Challenge":
                        structure_list = self.feta.list_structure_name
                    else:
                        structure_list=[]

                    for idx, struc in enumerate(structure_list):
                        label_struc = np.zeros(label_img.shape, dtype=np.uint16)
                        label_struc[label_img == (idx + 1)] = 255

                        if len(extensions) == 1:
                            if (extensions[0] == ".tif") or (extensions[0] == ".tiff"):
                                file_name = Path(file_path).stem 
                                new_file_name = file_name + '_' + struc + extensions[0]
                                new_file_path = Path(Path(file_path).parent).joinpath(new_file_name)
                                tif.imsave(str(new_file_path), label_struc)
                        elif len(extensions) == 2:
                            if (extensions[0] == ".nii") and (extensions[1] == ".gz"):
                                file_name = Path(Path(file_path).stem).stem
                                new_file_name = file_name + '_' + struc + extensions[0] + extensions[1]
                                new_file_path = Path(Path(file_path).parent).joinpath(new_file_name)
                                result_image_sitk = sitk.GetImageFromArray(label_struc)
                                result_image_sitk.CopyInformation(self.image_sitk)
                                sitk.WriteImage(result_image_sitk, str(new_file_path))

                self.remove_backup_label_file()

            else:
                display_warning_box(self, "Error", "No segmentation data find")
                return

    def backup_save_label(self):
        """
            Save a backup of the 3D segmentation data as a .tif file
        """

        if hasattr(self.viewer, 'layers'):
            if "annotations" in self.viewer.layers:
                label_img = self.viewer.layers['annotations'].data

                #TIF OPTION
                temp_label_data_file_path = Path(self.img_dir).joinpath("TEMP_segmentation.tif")
                
                tif.imsave(str(temp_label_data_file_path), label_img)       

                # NII GZ OPTION

                # temp_label_data_file_path = Path(self.img_dir).joinpath("TEMP_segmentation.nii.gz")
                # result_image_sitk = sitk.GetImageFromArray(label_img.astype(np.uint16))
                # # result_image_sitk = sitk.GetImageFromArray(label_img)
                # result_image_sitk.CopyInformation(self.image_sitk)
                # sitk.WriteImage(result_image_sitk, str(temp_label_data_file_path))

    def activate_backup_label(self):
        """
        TODO
        """
        if self.backup_push_button.isChecked() == True:
            self.viewer.dims.events.emitters['current_step'].connect(self.backup_save_label)
        else:
            self.viewer.dims.events.emitters['current_step'].disconnect(self.backup_save_label)
            


# ============ Display warning/question message box ============
    def can_remove_image_data(self):
        """
            Display a question box to remove image data
        """
        if "image" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will reset image data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

    def can_remove_label_data(self):
        """
            Display a question box to remove segmentation data
        """
        if "annotations" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will reset segmentation data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

    def can_remove_all(self):
        """
            Display a question box to remove all data
        """
        if "image" in self.viewer.layers or "annotations" in self.viewer.layers:
            choice = display_ok_cancel_question_box(
                "Warning",
                "This will reset all data. Do you want to continue ?",
            )
        else:
            choice = True

        return choice

# ============ Remove or reset data ============
    def remove_image(self):
        """
            Remove image data
        """
        if "image" in self.viewer.layers:
            self.viewer.layers.remove('image')

    def remove_label(self):
        """
            Remove segmentation data
        """
        if "annotations" in self.viewer.layers:
            self.viewer.layers.remove('annotations')

    def remove_backup_label_file(self):
        """
            Delete the backup segmentation file
        """

        temp_label_data_file_path = Path(self.img_dir).joinpath("TEMP_segmentation.tif")
        if os.path.exists(str(temp_label_data_file_path)):
            os.remove(str(temp_label_data_file_path))

    def reset_label(self):
        """
            Reset segmentation data
        """
        canRemoveLabel = self.can_remove_label_data()

        if canRemoveLabel:
            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()
            self.remove_backup_label_file()
        else:
            return

    def reset_annotation_radio_buttons(self):
        structure_name = self.annotation_combo_box.currentText()
        if structure_name == "Fetus":
            radio_button_to_check = self.fetus.group_radio_button.button(self.fetus.nbr_buttons)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Shoulder":
            radio_button_to_check = self.shoulder.group_radio_button.button(self.shoulder.nbr_buttons)
            radio_button_to_check.setChecked(True)

        elif structure_name == "Feta Challenge":
            radio_button_to_check = self.feta.group_radio_button.button(self.feta.nbr_buttons)
            radio_button_to_check.setChecked(True)

    def reset_zoom_slider(self):
        median = round( (self.zoom_slider.maximum() - self.zoom_slider.minimum()) / 2)
        self.zoom_slider.setValue(median)

    # def slicer_change(self):
    #     index = self.viewer.dims.current_step
    #     print(index)

    #     # image_to_display = self.image[index, :, :]

    #     if 'image' in self.viewer.layers:
    #             source_img = self.viewer.layers['image'].data


    #     pixmap = QPixmap(image_path)
    #     view_image_1.setPixmap(pixmap)