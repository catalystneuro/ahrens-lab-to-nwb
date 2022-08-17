"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .yu_mu_cell_2019_imaging_interface import AhrensHdf5ImagingInterface


class YuMuCell2019NWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(Imaging=AhrensHdf5ImagingInterface)
