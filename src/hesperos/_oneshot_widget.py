# ============ Import python files ============
# === GUI elements ===
from hesperos.layout.gui_elements import (
    add_push_button, 
    add_icon_push_button,
    add_label, 
    add_slider, 
    display_warning_box, 
    display_ok_cancel_question_box
)
from hesperos.layout.napari_elements import disable_napari_buttons, disable_layer_widgets
from hesperos.resources._icons import get_icon_path, get_relative_icon_path

import hesperos.annotation.oneshot as oneshot_data
from hesperos.annotation.structuresubpanel import StructureSubPanel

# === One Shot learning computation
from hesperos.one_shot_learning.features3d import Features3D
from hesperos.one_shot_learning.utilities import run_one_shot_learning

# ============ Import python packages ============
import os
import napari
import numpy as np
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
    QHBoxLayout
)


# ============ Define variables ============
COLUMN_WIDTH = 100
SEGM_METHODS_PANEL_ALIGN = (
    "center"  # Alignment of text in pushbuttons in methods chooser panel
)


# ============ Define QWidget Class ============
class OneShotWidget(QWidget):
    """
    QWidget class for One Shot Learning Segmentation in NAPARI

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

        napari.features_3d = Features3D()

        self.generate_main_layout()

# ============ Define Layout ============
    def generate_main_layout(self):
        """
        Generate the main layout of widget
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

        self.add_segmentation_panel(4)

        self.add_reset_save_panel(5)

        self.enable_panels(["annotation_panel", "segmentation_panel", "reset_save_panel"], False)

        self.setLayout(self.layout)

    def add_sub_annotation_panel(self, row):
        """
        Create annotation sub panel with the list of all struture to annotate

        Parameters
        ----------
        row : int
            row position of the sub panel in the main QGridLayout

        """
        self.oneshot = StructureSubPanel(
            parent=self,
            row=row,
            column=0,
            list_structures=oneshot_data.LIST_STRUCTURES,
            dict_substructures=oneshot_data.DICT_SUB_STRUCTURES,
            dict_sub_substructures=[])


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
        self.loading_layout.setContentsMargins(10, 10, 10, 10)
        self.loading_layout.setSpacing(5)
        self.loading_layout.setAlignment(QtCore.Qt.AlignTop)

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
            column=0,
            column_span=2,
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

    def add_segmentation_panel(self, row, column=0):
        """
        Create segmentation panel

        Parameters
        ----------
        row : int
            row position of the panel in the main QGridLayout
        column : int
            column position of the panel in the main QGridLayout

        """

        # === Set panel parameters ===
        self.segmentation_panel = QGroupBox("3. SEGMENT")
        self.segmentation_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.segmentation_layout = QGridLayout()
        self.segmentation_layout.setContentsMargins(10, 10, 10, 10)
        self.segmentation_layout.setSpacing(5)
        self.segmentation_layout.setAlignment(QtCore.Qt.AlignTop)

        # === Add Qwidgets to the panel layout ===
        self.run_segmentation_push_button = add_push_button(
            name="Run segmentation",
            layout=self.segmentation_layout,
            callback_function=self.run_segmentation,
            row=0,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.threshold_label = add_label(
            text="Probability threshold:",
            layout=self.segmentation_layout,
            row=1,
            column=0,
            minimum_width=COLUMN_WIDTH,
        )

        self.threshold_slider = add_slider(
            layout=self.segmentation_layout,
            bounds=[0, 255],
            callback_function=self.change_threshold,
            row=1,
            column=1,
            minimum_width=COLUMN_WIDTH,
        )

        self.segmentation_panel.setLayout(self.segmentation_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.segmentation_panel, row, column)       

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
        self.reset_save_panel = QGroupBox("4. SAVE ANNOTATION")
        self.reset_save_panel.setStyleSheet("margin-top : 5px;")

        # === Set panel layout parameters ===
        self.reset_save_layout = QGridLayout()
        self.reset_save_layout.setSpacing(5)

        # === Add Qwidgets to the panel layout ===
        self.save_seg_push_button = add_push_button(
            name="Save segmentation",
            layout=self.reset_save_layout,
            callback_function=self.save_segmentation,
            row=0,
            column=0,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.save_proba_push_button = add_push_button(
            name="Save probabilities",
            layout=self.reset_save_layout,
            callback_function=self.save_probabilities,
            row=0,
            column=1,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.reset_push_button = add_push_button(
            name="Delete all",
            layout=self.reset_save_layout,
            callback_function=self.reset_label,
            row=1,
            column=0,
            column_span=2,
            minimum_width=COLUMN_WIDTH,
            alignment=SEGM_METHODS_PANEL_ALIGN,
        )

        self.reset_save_panel.setLayout(self.reset_save_layout)

        # === Add panel to the main layout ===
        self.layout.addWidget(self.reset_save_panel, row, column)

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
                self.load_label_push_button.setVisible(isVisible)
                self.zoom_slider.setVisible(isVisible)
                self.undo_push_button.setVisible(isVisible)
            
            elif panel_name == "segmentation_panel":
                self.segmentation_panel.setVisible(isVisible)
                self.run_segmentation_push_button.setVisible(isVisible)
                self.threshold_label.setVisible(isVisible)
                self.threshold_slider.setVisible(isVisible)

            elif panel_name == "reset_save_panel":
                self.reset_save_panel.setVisible(isVisible)
                self.save_seg_push_button.setVisible(isVisible)
                self.reset_push_button.setVisible(isVisible)
                self.save_proba_push_button.setVisible(isVisible)

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
            self.viewer.add_image(rearranged_image, name='image')

            disable_layer_widgets(self.viewer, 'image')

            self.enable_panels(["annotation_panel", "segmentation_panel", "reset_save_panel"], True)
            self.reset_zoom_slider()

            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()

            self.remove_segmentation()
            self.remove_proba()

            self.oneshot.toggle_sub_panel(True)
            napari.features_3d = Features3D()
        else:
            return

    def load_image(self):
        """
            Load an image file of type .tiff, .tif, .nii.gz
        """

        files_types = "TIFF (*.tiff);;TIF (*.tif);;NIFTI compressed (*.nii.gz)"
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

            self.enable_panels(["annotation_panel", "segmentation_panel", "reset_save_panel"], True)
            self.reset_zoom_slider()

            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()

            self.remove_segmentation()
            self.remove_proba()

            self.oneshot.toggle_sub_panel(True)
            napari.features_3d = Features3D()

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
                self.viewer.layers['annotations'].selected_label = self.oneshot.nbr_buttons
                self.viewer.layers['annotations'].mode = "PAINT"

                disable_layer_widgets(self.viewer, 'annotations')

                # qctrl = self.viewer.window._qt_viewer.controls.widgets[self.viewer.layers['annotations']]
                # qctrl.opacitySlider.setMaximum(0.8)
            else:
                display_warning_box(self, "Error", "Load first a DICOM serie")

        else:
            display_warning_box(self, "Error", "Load first a DICOM serie")

    def run_segmentation(self):
        """
            Run One shot learning : training and inference steps
        """

        # === Load data ===
        if hasattr(self.viewer, 'layers'):
            if 'image' in self.viewer.layers:
                source_img = self.viewer.layers['image'].data
            else:
                return
            if 'annotations' in self.viewer.layers:
                label = self.viewer.layers['annotations'].data
            else:
                return

        output_proba = run_one_shot_learning(source_img, label)

        self.remove_segmentation()
        self.remove_proba()

        self.viewer.add_image(output_proba, name="probabilities")
        disable_layer_widgets(self.viewer, 'probabilities')
        self.viewer.layers['probabilities'].visible = False

        output_threshold = np.where(output_proba > self.threshold_slider.value(), 255, 0)
        self.viewer.add_image(output_threshold, name="segmentation", colormap="red", opacity=0.5)
        disable_layer_widgets(self.viewer, 'segmentation')

    def change_threshold(self):
        """
        TODO
        """
        value = self.threshold_slider.value()

        if hasattr(self.viewer, 'layers'):
            if 'probabilities' in self.viewer.layers:
                output_proba = self.viewer.layers["probabilities"].data
                threshold_img = np.where(output_proba > value, 255, 0)
                if 'segmentation' in self.viewer.layers:
                    self.viewer.layers["segmentation"].data = threshold_img
    
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



    def save_segmentation(self):
        """
            Save the segmented data as a unique 3D image, or multiple 3D images (one by label)
        """

        files_types = "TIFF (*.tiff);;TIF (*.tif);;NIFTI compressed (*.nii.gz)"

        default_filename = os.path.join(self.img_dir, "segmentation.tif")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Segmentation", default_filename , files_types)

        # If choose "Cancel"
        if file_path == "":
            return

        #TODO ADD CHOIVE TO SAVE SEPERATELYR

        if hasattr(self.viewer, 'layers'):
            if "segmentation" in self.viewer.layers:
                seg_img = self.viewer.layers['segmentation'].data

                extensions = Path(file_path).suffixes

                if len(extensions) == 1:
                    if (extensions[0] == ".tif") or (extensions[0] == ".tiff"): 
                        tif.imsave(file_path, seg_img)
                elif len(extensions) == 2:
                        if (extensions[0] == ".nii") and (extensions[1] == ".gz"):
                            result_image_sitk = sitk.GetImageFromArray(seg_img.astype(np.uint16))
                            result_image_sitk.CopyInformation(self.image_sitk)
                            sitk.WriteImage(result_image_sitk, file_path)
            else:
                display_warning_box(self, "Error", "No segmentation data find")
                return

    def save_probabilities(self):
        """
            Save the probabilities data as a unique 3D image, or multiple 3D images (one by label)
        """

        files_types = "TIFF (*.tiff);;TIF (*.tif);;NIFTI compressed (*.nii.gz)"

        default_filename = os.path.join(self.img_dir, "probabilities.tif")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Probabilities", default_filename , files_types)

        # If choose "Cancel"
        if file_path == "":
            return

        #TODO ADD CHOIVE TO SAVE SEPERATELYR

        if hasattr(self.viewer, 'layers'):
            if "probabilities" in self.viewer.layers:
                proba_img = self.viewer.layers['probabilities'].data
                proba_img = proba_img * 255
                proba_img = proba_img.astype(np.uint16)

                extensions = Path(file_path).suffixes

                if len(extensions) == 1:
                    if (extensions[0] == ".tif") or (extensions[0] == ".tiff"): 
                        tif.imsave(file_path, proba_img)
                elif len(extensions) == 2:
                    if (extensions[0] == ".nii") and (extensions[1] == ".gz"):
                        result_image_sitk = sitk.GetImageFromArray(proba_img)
                        result_image_sitk.CopyInformation(self.image_sitk)
                        sitk.WriteImage(result_image_sitk, file_path)
            else:
                display_warning_box(self, "Error", "No probabilities data find")
                return

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
            Remove label data
        """
        if "annotations" in self.viewer.layers:
            self.viewer.layers.remove('annotations')

    def remove_segmentation(self):
        """
            Remove segmentation data
        """
        if "segmentation" in self.viewer.layers:
            self.viewer.layers.remove('segmentation')

    def remove_proba(self):
        """
            Remove probabilities data
        """
        if "probabilities" in self.viewer.layers:
            self.viewer.layers.remove('probabilities')

    def reset_label(self):
        """
            Reset label data
        """
        canRemoveLabel = self.can_remove_label_data()

        if canRemoveLabel:
            self.remove_label()
            self.add_label_layers(label_data=[])
            self.reset_annotation_radio_buttons()
        else:
            return

    def reset_annotation_radio_buttons(self):
        radio_button_to_check = self.oneshot.group_radio_button.button(self.oneshot.nbr_buttons)
        radio_button_to_check.setChecked(True)

    def reset_zoom_slider(self):
        median = round( (self.zoom_slider.maximum() - self.zoom_slider.minimum()) / 2)
        self.zoom_slider.setValue(median)
        
# ============ For testing ============
    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")