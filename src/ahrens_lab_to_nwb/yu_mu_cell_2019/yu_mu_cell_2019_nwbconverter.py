"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .yu_mu_cell_2019_imaging_interface import AhrensHdf5ImagingInterface
from .yu_mu_cell_2019_segmentation_interface import YuMu2019SegmentationInterface


class YuMuCell2019NWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Imaging=AhrensHdf5ImagingInterface,
        GliaSegmentation=YuMu2019SegmentationInterface,
        NeuronSegmentation=YuMu2019SegmentationInterface,
    )
