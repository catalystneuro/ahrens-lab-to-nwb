"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from dateutil import tz

# from neuroconv.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019 import YuMuCell2019NWBConverter

# Manually specify everything here as it changes
# ----------------------------------------------
timezone = "US/Eastern"

global_metadata_path = Path(__file__) / "yu_mu_cell_2019_metadata.yaml"

imaging_folder_path = Path(
    "E:/Ahrens/Imaging/20170228/fish4/20170228_4_1_gfaprgeco_hucgc_6dpf_shorttrials_20170228_185002/raw"
)

ephys_folder_path = Path(
    "E:/Ahrens/Imaging/20170228/fish4/20170228_4_1_gfaprgeco_hucgc_6dpf_shorttrials_20170228_185002/ephys"
)
raw_behavior_file_path = ephys_folder_path / "rawdata.mat"
raw_behavior_series_descriptions = Path(__file__) / "yu_mu_cell_2019_behavior_descriptions.yaml"
processed_behavior_file_path = ephys_folder_path / "data.mat"
trial_table_file_path = ephys_folder_path / "trial_info.mat"
states_folder_path = ephys_folder_path

nwbfile_path = Path("E:/Ahrens/NWB/testing.nwb")
# ----------------------------------------------
# Below here is automated


example_session_id = imaging_folder_path.parent.stem
session_start_time_string = "".join(example_session_id.split("_")[-2:])
session_start_time = datetime.strptime(session_start_time_string, "%Y%m%d%H%M%S")
session_start_time.replace(tzinfo=tz.gettz(timezone))

# The rate is estimated from the mean number of frames between TTL onset (ch3) for frame
# captures divided by average reported volume sampling speed
imaging_rate = 1.56
behavior_rate = 2431.6
source_data = dict(
    Imaging=dict(folder_path=str(imaging_folder_path), sampling_frequency=imaging_rate),
    RawBehavior=dict(
        data_file_path=str(raw_behavior_file_path),
        metadata_file_path=raw_behavior_series_descriptions,
        sampling_frequency=behavior_rate,
    ),
    ProcessedBehavior=dict(file_path=str(processed_behavior_file_path), sampling_frequency=behavior_rate),
    Trials=dict(file_path=trial_table_file_path, sampling_frequency=behavior_rate),
    SwimIntervals=dict(file_path=processed_behavior_file_path, sampling_frequency=behavior_rate),
    ActivityStates=dict(folder_path=states_folder_path),
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
