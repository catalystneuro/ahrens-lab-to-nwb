"""Primary NWBConverter class for this dataset."""
from nwb_conversion_tools import (
    NWBConverter,
    Suite2PSegmentationInterface,
)

from ahrens_lab_to_nwb.yu_mu_cell_2019 import YuMuCell2019BehaviorInterface


class YuMuCell2019NWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Segmentation=Suite2PSegmentationInterface,
    )
