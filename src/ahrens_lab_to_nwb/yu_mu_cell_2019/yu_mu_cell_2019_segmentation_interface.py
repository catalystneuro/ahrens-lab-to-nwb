"""Custom segmentation interface to read the data from Mikael Rubinov corresponding to the Yu Mu 2019 Cell paper."""
from neuroconv.datainterfaces.ophys.basesegmentationextractorinterface import BaseSegmentationExtractorInterface
from neuroconv.utils import FilePathType

from .yu_mu_cell_2019_segmentation_extractor import YuMu2019SegmentationExtractor


class YuMu2019SegmentationInterface(BaseSegmentationExtractorInterface):
    """Data Interface for YuMu2019SegmentationExtractor."""

    Extractor = YuMu2019SegmentationExtractor

    def __init__(self, file_path: FilePathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(file_path=file_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose
        self.segmentation_extractor = YuMu2019SegmentationExtractor(
            file_path=file_path, sampling_frequency=sampling_frequency
        )
