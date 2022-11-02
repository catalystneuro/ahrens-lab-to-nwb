"""Custom segmentation interface to read the data from Mikael Rubinov corresponding to the Yu Mu 2019 Cell paper."""
from typing import Optional
from pathlib import Path

import numpy as np
from pynwb import NWBFile
from pynwb.ophys import ImageSegmentation, Fluorescence, DfOverF, RoiResponseSeries
from hdmf.backends.hdf5.h5_utils import H5DataIO
from neuroconv.datainterfaces.ophys.basesegmentationextractorinterface import BaseSegmentationExtractorInterface
from neuroconv.tools.hdmf import SliceableDataChunkIterator
from neuroconv.utils import FilePathType, load_dict_from_file

from ..extractors.yu_mu_cell_2019_segmentation_extractor import YuMu2019SegmentationExtractor


class YuMu2019DualColorSegmentationInterface(BaseSegmentationExtractorInterface):
    """Data Interface for single-color sessions of YuMu2019SegmentationExtractor."""

    Extractor = YuMu2019SegmentationExtractor

    def __init__(
        self,
        neuron_file_path: FilePathType,
        glia_file_path: FilePathType,
        sampling_frequency: float,
        verbose: bool = True,
    ):
        self.source_data = dict(
            neuron_file_path=neuron_file_path,
            glia_file_path=glia_file_path,
            sampling_frequency=sampling_frequency,
            verbose=verbose,
        )
        self.verbose = verbose
        self.neuron_segmentation_extractor = YuMu2019SegmentationExtractor(
            file_path=neuron_file_path, sampling_frequency=sampling_frequency
        )
        self.glia_segmentation_extractor = YuMu2019SegmentationExtractor(
            file_path=glia_file_path, sampling_frequency=sampling_frequency
        )

    def get_metadata(self):
        metadata_folder = (
            Path(__file__).parent.parent / "metadata"
        )  # The pre-built one in the repository; can also use a local copy

        ophys_metadata_path = metadata_folder / "yu_mu_cell_2019_dual_color_neuron_metadata.yml"
        return load_dict_from_file(file_path=ophys_metadata_path)

    def run_conversion(
        self,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        stub_test: bool = False,
        stub_frames: int = 100,
        iterator_options: Optional[dict] = None,
        compression_options: Optional[dict] = None,
    ):
        # Assume all Imaging-related data has been added already
        iterator_options = iterator_options or dict()
        compression_options = compression_options or dict(compression="gzip")

        # Neuron segmentation
        if stub_test:
            stub_frames = min([stub_frames, self.neuron_segmentation_extractor.get_num_frames()])
            segmentation_extractor = self.neuron_segmentation_extractor.frame_slice(
                start_frame=0, end_frame=stub_frames
            )
        else:
            segmentation_extractor = self.neuron_segmentation_extractor

        image_segmentation = ImageSegmentation(name=metadata["Ophys"]["ImageSegmentation"]["name"])

        neuron_plane_segmentation = image_segmentation.create_plane_segmentation(
            name=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][0]["name"],
            description=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][0]["description"],
            imaging_plane=nwbfile.imaging_planes["NeuronVolume"],
            reference_images=nwbfile.acquisition["NeuronTwoPhotonSeries"],
        )

        for roi in segmentation_extractor.get_roi_ids():
            voxel_mask = np.array(segmentation_extractor.get_roi_pixel_masks(roi_ids=[roi])).squeeze()
            neuron_plane_segmentation.add_roi(id=roi, voxel_mask=voxel_mask)

        # Make baseline series
        roi_table_region = neuron_plane_segmentation.create_roi_table_region(
            region=segmentation_extractor.get_roi_ids(), description="Region reference to ROI table."
        )
        timestamps = segmentation_extractor.frame_to_time(frames=np.arange(segmentation_extractor.get_num_frames()))
        neuron_baseline_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["Fluorescence"]["roi_response_series"][0]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(segmentation_extractor.get_traces(name="raw"), **iterator_options),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )

        # Make detrended series
        neuron_detrended_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][0]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(segmentation_extractor.get_traces(name="dff"), **iterator_options),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )

        # -------------------------------------------------------------------------------------------------------------
        # Glia Segmentation
        if stub_test:
            stub_frames = min([stub_frames, self.glia_segmentation_extractor.get_num_frames()])
            segmentation_extractor = self.glia_segmentation_extractor.frame_slice(start_frame=0, end_frame=stub_frames)
        else:
            segmentation_extractor = self.glia_segmentation_extractor

        glia_plane_segmentation = image_segmentation.create_plane_segmentation(
            name=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][1]["name"],
            description=metadata["Ophys"]["ImageSegmentation"]["plane_segmentations"][1]["description"],
            imaging_plane=nwbfile.imaging_planes["GliaVolume"],
            reference_images=nwbfile.acquisition["GliaTwoPhotonSeries"],
        )

        for roi in segmentation_extractor.get_roi_ids():
            voxel_mask = np.array(segmentation_extractor.get_roi_pixel_masks(roi_ids=[roi])).squeeze()
            glia_plane_segmentation.add_roi(id=roi, voxel_mask=voxel_mask)

        # Make baseline series
        roi_table_region = glia_plane_segmentation.create_roi_table_region(
            region=segmentation_extractor.get_roi_ids(), description="Region reference to ROI table."
        )
        timestamps = segmentation_extractor.frame_to_time(frames=np.arange(segmentation_extractor.get_num_frames()))
        glia_baseline_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["Fluorescence"]["roi_response_series"][1]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][1]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(segmentation_extractor.get_traces(name="raw"), **iterator_options),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )

        # Make detrended series
        glia_detrended_response_series = RoiResponseSeries(
            name=metadata["Ophys"]["DfOverF"]["roi_response_series"][1]["name"],
            description=metadata["Ophys"]["DfOverF"]["roi_response_series"][1]["description"],
            data=H5DataIO(
                SliceableDataChunkIterator(segmentation_extractor.get_traces(name="dff"), **iterator_options),
                **compression_options,
            ),
            rois=roi_table_region,
            unit="a.u.",
            timestamps=timestamps,
        )

        # Add everything to the ophys module
        ophys_module = nwbfile.create_processing_module(name="ophys", description="optical physiology processed data")
        ophys_module.add(image_segmentation)
        ophys_module.add(
            Fluorescence(
                name=metadata["Ophys"]["Fluorescence"]["name"],
                roi_response_series=[neuron_baseline_response_series, glia_baseline_response_series],
            )
        )
        ophys_module.add(
            DfOverF(
                name=metadata["Ophys"]["DfOverF"]["name"],
                roi_response_series=[neuron_detrended_response_series, glia_detrended_response_series],
            )
        )
