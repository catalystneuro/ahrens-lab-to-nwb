"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from dateutil import tz

# from neuroconv.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019 import YuMuCell2019NWBConverter

imaging_folder_path = Path(
    "E:/Ahrens/Imaging/20170228/fish4/20170228_4_1_gfaprgeco_hucgc_6dpf_shorttrials_20170228_185002/raw"
)
glia_segmentation_file_path = Path("E:/Ahrens/Segmentation/cells0_adjusted.mat")
neuron_segmentation_file_path = Path("E:/Ahrens/Segmentation/cells1_adjusted.mat")

example_session_id = imaging_folder_path.parent.stem
session_start_time_string = "".join(example_session_id.split("_")[-2:])
session_start_time = datetime.strptime(session_start_time_string, "%Y%m%d%H%M%S")
session_start_time.replace(tzinfo=tz.gettz("US/Eastern"))

nwbfile_path = Path("E:/Ahrens/NWB/testing.nwb")

metadata_path = Path(__file__) / "yu_mu_cell_2019_metadata.yaml"

source_data = dict(
    # Imaging=dict(folder_path=str(imaging_folder_path), sampling_frequency=1.56),
    GliaSegmentation=dict(file_path=str(glia_segmentation_file_path), sampling_frequency=1.56),
    #    NeuronSegmentation=dict(file_path=str(neuron_segmentation_file_path), sampling_frequency=1.56),
)
conversion_options = dict(Imaging=dict(stub_test=True, stub_frames=3))

converter = YuMuCell2019NWBConverter(source_data=source_data)

metadata = converter.get_metadata()
metadata["NWBFile"].update(session_start_time=session_start_time)
# metadata_from_yaml = load_dict_from_file(metadata_path)
# metadata = dict_deep_update(metadata, metadata_from_yaml)

converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options, overwrite=True
)
