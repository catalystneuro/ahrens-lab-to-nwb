"""Custom segmentation interface to read the data from Mikael Rubinov corresponding to the Yu Mu 2019 Cell paper."""
from typing import Optional

import numpy as np
from pynwb import NWBFile
from pynwb.ophys import ImageSegmentation, Fluorescence, DfOverF, RoiResponseSeries
from hdmf.backends.hdf5.h5_utils import H5DataIO
from neuroconv.datainterfaces.ophys.basesegmentationextractorinterface import BaseSegmentationExtractorInterface
from neuroconv.tools.hdmf import SliceableDataChunkIterator
from neuroconv.utils import FilePathType

from ..extractors.yu_mu_cell_2019_segmentation_extractor import YuMu2019SegmentationExtractor


class YuMu2019SingleColorSegmentationInterface(BaseSegmentationExtractorInterface):
    """Data Interface for single-color sessions of YuMu2019SegmentationExtractor."""

    Extractor = YuMu2019SegmentationExtractor

    def __init__(self, file_path: FilePathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(file_path=file_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose
        self.segmentation_extractor = YuMu2019SegmentationExtractor(
            file_path=file_path, sampling_frequency=sampling_frequency
        )

    def run_conversion(
        self,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        stub_test: bool = False,
        stub_frames: int = 100,
        iterator_options: Optional[dict] = None,
        compression_options: Optional[dict] = None,
    ):
        if stub_test:
            stub_frames = min([stub_frames, self.segmentation_extractor.get_num_frames()])
            segmentation_extractor = self.segmentation_extractor.frame_slice(start_frame=0, end_frame=stub_frames)
        else:
            segmentation_extractor = self.segmentation_extractor

        # Assume all Imaging-related data has been added already
        iterator_options = iterator_options or dict()
        compression_options = compression_options or dict(compression="gzip")

        ophys_module = nwbfile.create_processing_module(
            name="ophys", description="Processed data for the optical physiology."  # Best Practice name
        )

        image_segmentation = ImageSegmentation(name=metadata["Ophys"]["ImageSegmentation"]["name"])

        plane_segmentation = image_segmentation.create_plane_segmentation(
            name=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][0]["name"],
            description=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][0]["description"],
            imaging_plane=nwbfile.imaging_planes["NeuronVolume"],
            reference_images=nwbfile.acquisition["RawTwoPhotonSeries"],
        )

        for roi in segmentation_extractor.get_roi_ids():
            voxel_mask = np.array(segmentation_extractor.get_roi_pixel_masks(roi_ids=[roi])).squeeze()
            plane_segmentation.add_roi(id=roi, voxel_mask=voxel_mask)

        ophys_module.add(image_segmentation)

        # Add baseline series
        roi_table_region = plane_segmentation.create_roi_table_region(
            description="Region reference to ROI table.",  # With region=None, it should select entire ROI table
        )
        timestamps = segmentation_extractor.frame_to_time(frames=np.arange(segmentation_extractor.get_num_frames()))
        baseline_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["Fluorescence"]["roi_response_series"][0]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(
                    segmentation_extractor.get_traces_dict()["raw"],  # DO NOT USE get_traces() as that loads array
                    **iterator_options,
                ),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )
        ophys_module.add(
            Fluorescence(name=metadata["Ophys"]["Fluorescence"]["name"], roi_response_series=baseline_response_series)
        )

        # Add detrended series
        detrended_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(
                    segmentation_extractor.get_traces_dict()["dff"],  # DO NOT USE get_traces() as that loads array
                    **iterator_options,
                ),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )
        ophys_module.add(
            DfOverF(name=metadata["Ophys"]["DfOverF"]["name"], roi_response_series=detrended_response_series)
        )
