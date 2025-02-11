import os
import warnings

import pytest
import pandas as pd
import numpy as np
import h5py

from visual_behavior.ophys.dataset.visual_behavior_ophys_dataset import VisualBehaviorOphysDataset



def safe_makedirs(path):
    # exist_ok is not a thing in Python 2
    try:
        os.makedirs(path)
    except OSError as err:
        pass


    
@pytest.fixture
def ophys_metadata():
    return pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6]
    })



@pytest.fixture
def ophys_timestamps():
    return pd.DataFrame({
        'stimulus_frames': [np.arange(10)],
        'ophys_frames': [np.arange(10)+0.5]
    }, index=['timestamps'])



@pytest.fixture
def ophys_stimulus_table():
    return pd.DataFrame({
        'flash_number': [0, 1, 2], 
        'start_time': [0.0, 0.5, 1.0],
        'end_time': [0.5, 1.0, 1.5], 
        'image_name': ['im01', 'im02', 'im03'],
        'orientation': [np.pi/2.0, np.pi, -np.pi/2.0], 
        'contrast': [10, 20, 30], 
        'image_category': ['a', 'a', 'b'], 
        'start_frame': [0, 1, 2], 
        'end_frame': [1, 2, 3], 
        'duration': [0.5, 0.5, 0.5]
    })
    
    
@pytest.fixture
def stimulus_template():
    return np.arange(250).reshape([10, 5, 5])
    
    
@pytest.fixture
def stimulus_metadata():
    return pd.DataFrame({
        'image_index': [12, 24, 36],
        'image_name': ['im01', 'im02', 'im03'],
        'image_category': ['a', 'a', 'b']
    })


@pytest.fixture
def running_speed():
    return pd.DataFrame({
        'frame': [0, 1, 2],
        'running_speed': [6.1, 5.9, 6.0],
        'time': [0.25, 0.75, 1.25]
    })
    
    
@pytest.fixture
def licks():
    return pd.DataFrame({
        'frame': [1, 2, 3],
        'time': [0.1, 5.2, 1.24]
    })


@pytest.fixture
def rewards():
    return pd.DataFrame({
        'frame': [2, 3],
        'time': [5.2, 1.24]
    })


@pytest.fixture
def task_parameters():
    return pd.DataFrame({
        'blank_duration': [0.5],
        'n_stimulus_frames': [215788],
        'omitted_flash_fraction': [None],
        'response_window': [[0.15, 0.75]],
        'reward_volume': [0.007],
        'stage': ['natural_images_ophys_session_A'],
        'stimulus': ['Natural_Images_Lum_Matched_set_training_2017.07.14.pkl'],
        'stimulus_distribution': ['exponential'],
        'stimulus_duration': [0.25],
        'task': ['DoC_NaturalImages_Ophys_SessionA']
    }, index=['params'])
    
    
@pytest.fixture
def max_projection():
    return np.arange(25).reshape([5, 5])


@pytest.fixture
def motion_correction():
    return pd.DataFrame({
        'x_corr': [0.5, 0.75, 0.9],
        'y_corr': [0.9, 0.4, 1.0]
    })
    

@pytest.fixture
def roi_metrics():
    return pd.DataFrame({'index': {3: 4, 6: 7, 8: 9},
         ' traceindex': {3: 2, 6: 5, 8: 7},
         ' tempIndex': {3: 17, 6: 12, 8: 2},
         ' cx': {3: 127, 6: 234, 8: 299},
         ' cy': {3: 36, 6: 152, 8: 171},
         ' mask2Frame': {3: 0, 6: 0, 8: 0},
         ' frame': {3: 345, 6: 21, 8: 332},
         ' object': {3: 2, 6: 2, 8: 2},
         ' minx': {3: 118, 6: 225, 8: 290},
         ' miny': {3: 29, 6: 141, 8: 160},
         ' maxx': {3: 134, 6: 246, 8: 308},
         ' maxy': {3: 43, 6: 162, 8: 183},
         ' area': {3: 139, 6: 298, 8: 302},
         ' shape0': {3: 0.326, 6: 0.484, 8: 0.435},
         ' shape1': {3: 15, 6: 12, 8: 12},
         ' eXcluded': {3: 0, 6: 0, 8: 0},
         ' meanInt0': {3: 33, 6: 34, 8: 37},
         ' maxInt0': {3: 52, 6: 56, 8: 64},
         ' meanInt1': {3: 15, 6: 15, 8: 17},
         ' maxInt1': {3: 30, 6: 33, 8: 40},
         ' maxMeanRatio': {3: 1.0, 6: 1.2, 8: 1.3529},
         ' snpoffsetmean': {3: 12.225381, 6: 7.040238, 8: 9.801933},
         ' snpoffsetstdv': {3: 14.154276000000001, 6: 9.789852999999999, 8: 9.318489},
         ' act2': {3: 5282, 6: 12630, 8: 6275},
         ' act3': {3: 1055, 6: 9851, 8: 3166},
         ' OvlpCount': {3: 0, 6: 0, 8: 0},
         ' OvlpAreaPer': {3: 0, 6: 0, 8: 0},
         ' OvlpObj0': {3: 0, 6: 0, 8: 0},
         ' corcoef0': {3: 0.0, 6: 0.0, 8: 0.0},
         ' OvlpObj1': {3: 0, 6: 0, 8: 0},
         ' corcoef1': {3: 0.0, 6: 0.0, 8: 0.0},
         'roi_id': {3: 798485141, 6: 798485135, 8: 798485144},
         'id': {3: 815268274, 6: 815266942, 8: 815267016},
            'x': {3: 118, 6: 225, 8: 290},
            'y': {3: 29, 6: 141, 8: 160},
            'width': {3: 17, 6: 22, 8: 19},
            'height': {3: 15, 6: 22, 8: 24},
            'valid': {3: True, 6: True, 8: True},
            'mask': {3: [[True, False], [True, False]],
                     6: [[True, False], [True, False]],
                     8: [[True, False], [True, False]]},
            'unfiltered_cell_index': {3: 20, 6: 17, 8: 21},
            'cell_index': {3: 5, 6: 4, 8: 6},
            'cell_specimen_id': {3: 815268274, 6: 815266942, 8: 815267016}}
    )
    
@pytest.fixture
def ophys_data_dir(tmpdir_factory, 
    ophys_metadata, ophys_timestamps, ophys_stimulus_table, stimulus_template, stimulus_metadata, running_speed,
    licks, rewards, task_parameters, max_projection, motion_correction, roi_metrics
):
    warnings.simplefilter("ignore") # pandas yells about hdf object columns - it IS a problem for cross-version compatibility
    
    eid = 12345678
    tmp_dir = str(tmpdir_factory.mktemp('ophys_dataset_01'))
    
    # analysis folder
    analysis_folder_name = '{}_analysis'.format(eid)
    analysis_folder_path = os.path.join(tmp_dir, analysis_folder_name)
    safe_makedirs(analysis_folder_path)
    
    # metadata
    md_path = os.path.join(analysis_folder_path, 'metadata.h5')
    ophys_metadata.to_hdf(md_path, key='df', format='fixed')
    
    # timestamps
    ts_path = os.path.join(analysis_folder_path,  'timestamps.h5')
    ophys_timestamps.to_hdf(ts_path, key='df', format='fixed')
    
    # stim table
    stimulus_table_path = os.path.join(analysis_folder_path, 'stimulus_table.h5')
    ophys_stimulus_table.to_hdf(stimulus_table_path, key='df', format='fixed')
    
    # stim template
    stimulus_template_path = os.path.join(analysis_folder_path, 'stimulus_template.h5')
    with h5py.File(stimulus_template_path, 'w') as stimulus_template_file:
        stimulus_template_file.create_dataset('data', data=stimulus_template)
        
    # stim metadata
    stimulus_metadata_path = os.path.join(analysis_folder_path, 'stimulus_metadata.h5')
    stimulus_metadata.to_hdf(stimulus_metadata_path, key='df', format='fixed')
    
    # run speed
    running_speed_path = os.path.join(analysis_folder_path, 'running_speed.h5')
    running_speed.to_hdf(running_speed_path, key='df', format='fixed')
    
    # licks
    licks_path = os.path.join(analysis_folder_path, 'licks.h5')
    licks.to_hdf(licks_path, key='df', format='fixed')
    
    # rewards
    rewards_path = os.path.join(analysis_folder_path, 'rewards.h5')
    rewards.to_hdf(rewards_path, key='df', format='fixed')
    
    # task parameters
    task_parameters_path = os.path.join(analysis_folder_path, 'task_parameters.h5')
    task_parameters.to_hdf(task_parameters_path, key='df', format='fixed')
    
    # max projection
    max_projection_path = os.path.join(analysis_folder_path, 'max_projection.h5')
    with h5py.File(max_projection_path, 'w') as max_projection_file:
        max_projection_file.create_dataset('data', data=max_projection)
        
    # motion correction
    motion_correction_path = os.path.join(analysis_folder_path, 'motion_correction.h5')
    motion_correction.to_hdf(motion_correction_path, key='df', format='fixed')

    # roi metrics
    roi_metrics_path = os.path.join(analysis_folder_path, 'roi_metrics.h5')
    roi_metrics.to_hdf(roi_metrics_path, key='df', format='fixed')
    
    return tmp_dir


@pytest.fixture
def ophys_dataset(ophys_data_dir):
    return VisualBehaviorOphysDataset(12345678, ophys_data_dir)
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.analysis_folder,
    lambda ds: ds.get_analysis_folder()
])
def test_analysis_folder(fn, ophys_dataset):

    obtained = fn(ophys_dataset)
    assert obtained == '12345678_analysis'
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.analysis_dir,
    lambda ds: ds.get_analysis_dir()
])
def test_analysis_dir(fn, ophys_dataset, ophys_data_dir):
    
    obtained = fn(ophys_dataset)
    assert obtained == os.path.join(ophys_data_dir, '12345678_analysis')
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.metadata,
    lambda ds: ds.get_metadata()
])
def test_get_metadata(fn, ophys_dataset, ophys_metadata):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, ophys_metadata, check_like=True)
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.timestamps,
    lambda ds: ds.get_timestamps()
])
def test_get_timestamps(fn, ophys_dataset, ophys_timestamps):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, ophys_timestamps, check_like=True)
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.stimulus_timestamps,
    lambda ds: ds.get_stimulus_timestamps()
])
def test_get_stimulus_timestamps(fn, ophys_dataset, ophys_timestamps):
    
    obtained = fn(ophys_dataset)
    assert np.allclose(obtained, ophys_timestamps['stimulus_frames']['timestamps'])
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.ophys_timestamps,
    lambda ds: ds.get_ophys_timestamps()
])
def test_get_ophys_timestamps(fn, ophys_dataset, ophys_timestamps):
    
    obtained = fn(ophys_dataset)
    assert np.allclose(obtained, ophys_timestamps['ophys_frames']['timestamps'])
    

@pytest.mark.parametrize('fn', [
    lambda ds: ds.stimulus_table,
    lambda ds: ds.get_stimulus_table()
])
def test_get_stimulus_table(fn, ophys_dataset, ophys_stimulus_table):
    
    obtained = fn(ophys_dataset)
    ophys_stimulus_table = ophys_stimulus_table.loc[:, ('contrast', 'flash_number',
                                                        'start_time', 'end_time',
                                                        'image_name', 'orientation',
                                                        'image_category', 'duration')]
    pd.testing.assert_frame_equal(obtained, ophys_stimulus_table, check_like=True)
        
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.stimulus_template,
    lambda ds: ds.get_stimulus_template()
])
def test_get_ophys_timestamps(fn, ophys_dataset, stimulus_template):
    
    obtained = fn(ophys_dataset)
    assert np.allclose(obtained, stimulus_template)
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.stimulus_metadata,
    lambda ds: ds.get_stimulus_metadata()
])
def test_get_stimulus_metadata(fn, ophys_dataset, stimulus_metadata):
    
    obtained = fn(ophys_dataset)
    stimulus_metadata = stimulus_metadata.loc[:, ('image_index', 'image_name')]
    pd.testing.assert_frame_equal(obtained.query('image_name != "omitted"'), stimulus_metadata, check_like=True) 
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.running_speed,
    lambda ds: ds.get_running_speed()
])
def test_get_running_speed(fn, ophys_dataset, running_speed):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, running_speed, check_like=True) 
    

@pytest.mark.parametrize('fn', [
    lambda ds: ds.licks,
    lambda ds: ds.get_licks()
])
def test_ge_licks(fn, ophys_dataset, licks):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, licks, check_like=True) 
    

@pytest.mark.parametrize('fn', [
    lambda ds: ds.rewards,
    lambda ds: ds.get_rewards()
])
def test_get_rewards(fn, ophys_dataset, rewards):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, rewards, check_like=True) 
    

@pytest.mark.parametrize('fn', [
    lambda ds: ds.task_parameters,
    lambda ds: ds.get_task_parameters()
])
def test_get_task_parameters(fn, ophys_dataset, task_parameters):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, task_parameters, check_like=True) 
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.motion_correction,
    lambda ds: ds.get_motion_correction()
])
def test_get_motion_correction(fn, ophys_dataset, motion_correction):
    
    obtained = fn(ophys_dataset)
    pd.testing.assert_frame_equal(obtained, motion_correction, check_like=True) 
    
    
@pytest.mark.parametrize('fn', [
    lambda ds: ds.max_projection,
    lambda ds: ds.get_max_projection()
])
def test_get_max_projection(fn, ophys_dataset, max_projection):
    
    obtained = fn(ophys_dataset)
    assert np.allclose(obtained, max_projection) 
