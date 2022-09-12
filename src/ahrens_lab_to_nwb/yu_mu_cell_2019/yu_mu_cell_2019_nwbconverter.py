"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .yu_mu_cell_2019_imaging_interface import AhrensHdf5ImagingInterface
from .yu_mu_cell_2019_raw_behavior_interface import YuMu2019RawBehaviorInterface
from .yu_mu_cell_2019_processsed_behavior_interface import YuMu2019ProcessedBehaviorInterface


class YuMuCell2019NWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Imaging=AhrensHdf5ImagingInterface,
        RawBehavior=YuMu2019RawBehaviorInterface,
        Trials=YuMu2019TrialsInterface,
    )
