import os
import h5py
import warnings
import numpy as np
import pandas as pd


from allensdk.internal.api import PostgresQueryMixin
from visual_behavior.data_access import utilities as utils
from visual_behavior.data_access import from_lims_utilities as lims_utils
import visual_behavior.database as db


# Accessing Lims Database
try:
    lims_dbname = os.environ["LIMS_DBNAME"]
    lims_user = os.environ["LIMS_USER"]
    lims_host = os.environ["LIMS_HOST"]
    lims_password = os.environ["LIMS_PASSWORD"]
    lims_port = os.environ["LIMS_PORT"]

    lims_engine = PostgresQueryMixin(
        dbname=lims_dbname,
        user=lims_user,
        host=lims_host,
        password=lims_password,
        port=lims_port
    )

    # building querys
    mixin = lims_engine

except Exception as e:
    warn_string = 'failed to set up LIMS/mtrain credentials\n{}\n\n \
        internal AIBS users should set up environment variables \
        appropriately\nfunctions requiring database access will fail'.format(e)
    warnings.warn(warn_string)


### QUERIES USED FOR MULTIPLE FUNCTIONS ###      # noqa: E266
def general_info_for_id_query():
    """the base query used for all the 'get_general_info_for...
    id type' functions. can be used with the following ID types:
    ophys_experiment_id
    ophys_session_id
    behavior_session_id
    container_id
    supercontainer_id

    AND to be used in combination with a query
    selection statment, that specifies the ID type. Example:
    query_selection = '''
    WHERE
    oe.id ={}
    '''.format(ophys_experiment_id)

    Returns
    -------
    string
        a string that can be used in a lims query.
    """

    general_info_for_id_query_string = '''
    SELECT
    oe.id AS ophys_experiment_id,
    oe.ophys_session_id,
    bs.id AS behavior_session_id,
    os.foraging_id,
    vbec.id AS ophys_container_id,
    os.visual_behavior_supercontainer_id AS supercontainer_id,

    oe.workflow_state AS experiment_workflow_state,
    os.workflow_state AS session_workflow_state,
    vbec.workflow_state AS container_workflow_state,

    os.specimen_id,
    specimens.donor_id,
    specimens.name AS specimen_name,

    os.date_of_acquisition,
    os.stimulus_name AS session_type,
    structures.acronym AS targeted_structure,
    imaging_depths.depth,
    equipment.name AS equipment_name,
    projects.code AS project,

    oe.storage_directory AS experiment_storage_directory,
    os.storage_directory AS session_storage_directory,
    vbec.storage_directory AS container_storage_directory

    FROM
    ophys_experiments oe

    JOIN ophys_sessions os
    ON os.id = oe.ophys_session_id

    JOIN behavior_sessions bs
    ON bs.foraging_id = os.foraging_id

    JOIN ophys_experiments_visual_behavior_experiment_containers oevbec
    ON oe.id = oevbec.ophys_experiment_id

    JOIN visual_behavior_experiment_containers vbec
    ON vbec.id = oevbec.visual_behavior_experiment_container_id

    JOIN projects ON projects.id = os.project_id
    JOIN specimens ON specimens.id = os.specimen_id
    JOIN structures ON structures.id = oe.targeted_structure_id
    JOIN imaging_depths ON imaging_depths.id = oe.imaging_depth_id
    JOIN equipment ON equipment.id = os.equipment_id
    '''
    return general_info_for_id_query_string


def all_ids_for_id_query():
    """the base query used for all the 'get_all_ids_for...
    id type' functions. can be used with the following ID types:
    ophys_experiment_id
    ophys_session_id
    behavior_session_id
    ophys_container_id
    supercontainer_id

    AND to be used in combination with a query
    selection statment, that specifies the ID type. Example:
    query_selection = '''
    WHERE
    oe.id ={}
    '''.format(ophys_experiment_id)

    Returns
    -------
    string
        string that can be used for lims queries
    """
    all_ids_query_string = '''
    SELECT
    oe.id AS ophys_experiment_id,
    oe.ophys_session_id,
    bs.id AS behavior_session_id,
    oevbec.visual_behavior_experiment_container_id AS ophys_container_id,
    os.visual_behavior_supercontainer_id AS supercontainer_id

    FROM
    ophys_experiments oe

    JOIN ophys_sessions os
    ON os.id = oe.ophys_session_id

    JOIN behavior_sessions bs
    ON bs.foraging_id = os.foraging_id

    JOIN ophys_experiments_visual_behavior_experiment_containers oevbec
    ON oe.id = oevbec.ophys_experiment_id
    '''
    return all_ids_query_string

### ID TYPES ###      # noqa: E266

# mouse related IDS


def get_donor_id_for_specimen_id(specimen_id):
    specimen_id = int(specimen_id)
    query = '''
    SELECT
    donor_id

    FROM
    specimens

    WHERE
    id = {}
    '''.format(specimen_id)
    donor_ids = mixin.select(query)
    return donor_ids


def get_specimen_id_for_donor_id(donor_id):
    donor_id = int(donor_id)
    query = '''
    SELECT
    id

    FROM
    specimens

    WHERE
    donor_id = {}
    '''.format(donor_id)
    specimen_ids = mixin.select(query)
    return specimen_ids


# for ophys_experimnt_id
def get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id):
    """gets the id for the current cell segmentation run for a given experiment.
        Queries LIMS via AllenSDK PostgresQuery function.

    Parameters
    ----------
    ophys_experiment_id : int
        9 digit ophys experiment id

    Returns
    -------
    int
        current cell segmentation run id
    """
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    id

    FROM
    ophys_cell_segmentation_runs

    WHERE
    current = true
    AND ophys_experiment_id = {}
    '''.format(ophys_experiment_id)
    current_run_id = mixin.select(query)
    current_run_id = int(current_run_id["id"][0])
    return current_run_id


def get_ophys_session_id_for_ophys_experiment_id(ophys_experiment_id):
    """uses an sqlite to query lims2 database. Gets the ophys_session_id
       for a given ophys_experiment_id from the ophys_experiments table
       in lims.
    """
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    ophys_session_id

    FROM
    ophys_experiments

    WHERE
    id = {}
    '''.format(ophys_experiment_id)
    ophys_session_id = mixin.select(query)
    ophys_session_id = ophys_session_id["ophys_session_id"][0]
    return ophys_session_id


def get_behavior_session_id_for_ophys_experiment_id(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    behavior.id as behavior_session_id

    FROM
    behavior_sessions behavior

    JOIN
    ophys_experiments oe on oe.ophys_session_id = behavior.ophys_session_id

    WHERE
    oe.id = {}
    '''.format(ophys_experiment_id)
    behavior_session_id = mixin.select(query)
    behavior_session_id = behavior_session_id["behavior_session_id"][0]
    return behavior_session_id


def get_ophys_container_id_for_ophys_experiment_id(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    visual_behavior_experiment_container_id as ophys_container_id

    FROM
    ophys_experiments_visual_behavior_experiment_containers

    WHERE
    ophys_experiment_id = {}
    '''.format(ophys_experiment_id)
    ophys_container_id = mixin.select(query)
    ophys_container_id = ophys_container_id["ophys_container_id"][0]
    return ophys_container_id


def get_supercontainer_id_for_ophys_experiment_id(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    sessions.visual_behavior_supercontainer_id as supercontainer_id

    FROM
    ophys_experiments experiments

    JOIN ophys_sessions sessions
    ON sessions.id = experiments.ophys_session_id

    WHERE
    experiments.id = {}
    '''.format(ophys_experiment_id)
    supercontainer_id = mixin.select(query)
    supercontainer_id = supercontainer_id["supercontainer_id"][0]
    return supercontainer_id


def get_all_ids_for_ophys_experiment_id(ophys_experiment_id):
    """queries LIMS and gets all of the ids for a given ophys
    experiment id

    Parameters
    ----------
    ophys_experiment_id : int
        unique identifier for an ophys experiment
        (single FOV optical physiology session)

    Returns
    -------
    dataframe/table
        table with the following columns:
            ophys_experiment_id,
            ophys_session_id,
            behavior_session_id,
            ophys_container_id,
            supercontainer_id

    """
    ophys_experiment_id = int(ophys_experiment_id)

    all_ids_query = all_ids_for_id_query()
    query_selection = '''
    WHERE oe.id = {} '''.format(ophys_experiment_id)
    query = all_ids_query + query_selection

    all_ids = mixin.select(query)
    return all_ids


def get_general_info_for_ophys_experiment_id(ophys_experiment_id):
    """queries lims to using the general_info_for_id_query() and
    returns general information specific to a given ophys_experiment_id

    Parameters
    ----------
    ophys_experiment_id : int
        unique identifier for an ophys experiment (single FOV)

    Returns
    -------
    dataframe
        dataframe with the following columns:
            ophys_experiment_id
            ophys_session_id
            behavior_session_id
            foraging_id
            ophys_container_id
            supercontainer_id
            experiment_workflow_state
            session_workflow_state
            container_workflow_state
            specimen_id
            donor_id
            specimen_name
            date_of_acquisition
            session_type
            targeted_structure
            depth
            equipment_name
            project
            experiment_storage_directory
            session_storage_directory

    """
    ophys_experiment_id = int(ophys_experiment_id)

    general_info_query = general_info_for_id_query()
    query_selection = '''
    WHERE oe.id ={} '''.format(ophys_experiment_id)
    query = general_info_query + query_selection

    general_info = mixin.select(query)

    # ensure operating system compatible filepaths
    general_info = lims_utils.correct_general_info_filepaths(general_info)

    return general_info


def get_genotype_from_ophys_experiment_id(ophys_experiment_id):
    '''
    gets genotype string for a given ophys_experiment_id
    '''
    qs = '''
        select donors.full_genotype
        from ophys_experiments as oe
        JOIN ophys_sessions os on os.id = oe.ophys_session_id
        JOIN specimens on specimens.id = os.specimen_id
        JOIN donors on donors.id = specimens.donor_id
        where oe.id = {}
    '''
    return db.lims_query(qs.format(ophys_experiment_id))


# for ophys_session_id


def get_ophys_experiment_ids_for_ophys_session_id(ophys_session_id):
    """uses an sqlite to query lims2 database. Gets the ophys_experiment_id
       for a given ophys_session_id from the ophys_experiments table in lims.

       note: number of experiments per session will vary depending on the
       rig it was collected on and the project it was collected for.
    """
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    id

    FROM ophys_experiments

    WHERE
    ophys_session_id = {}
    '''.format(ophys_session_id)
    ophys_experiment_ids = mixin.select(query)
    ophys_experiment_ids = ophys_experiment_ids.rename(columns={"id": "ophys_experiment_id"})
    return ophys_experiment_ids


def get_behavior_session_id_for_ophys_session_id(ophys_session_id):
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    id AS behavior_session_id

    FROM behavior_sessions

    WHERE
    ophys_session_id = {}
    '''.format(ophys_session_id)
    behavior_session_id = mixin.select(query)
    behavior_session_id = behavior_session_id["behavior_session_id"][0]
    return behavior_session_id


def get_ophys_container_ids_for_ophys_session_id(ophys_session_id):
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    container.visual_behavior_experiment_container_id
    AS ophys_container_id

    FROM ophys_experiments_visual_behavior_experiment_containers container
    JOIN ophys_experiments oe ON oe.id = container.ophys_experiment_id

    WHERE
    oe.ophys_session_id = {}
    '''.format(ophys_session_id)
    ophys_container_ids = mixin.select(query)
    return ophys_container_ids


def get_supercontainer_id_for_ophys_session_id(ophys_session_id):
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    visual_behavior_supercontainer_id
    AS supercontainer_id

    FROM
    ophys_sessions

    WHERE id = {}
    '''.format(ophys_session_id)
    supercontainer_id = mixin.select(query)
    supercontainer_id = supercontainer_id["supercontainer_id"][0]
    return supercontainer_id


def get_all_ids_for_ophys_session_id(ophys_session_id):
    """

    Parameters
    ----------
    ophys_session_id : int
        unique identifier for an ophys session

    Returns
    -------
    dataframe/table
        table with the following columns:
            ophys_experiment_id,
            ophys_session_id,
            behavior_session_id,
            ophys_container_id,
            supercontainer_id
    """
    ophys_session_id = int(ophys_session_id)

    all_ids_query = all_ids_for_id_query()
    query_selection = '''
    WHERE oe.ophys_session_id ={} '''.format(ophys_session_id)
    query = all_ids_query + query_selection

    all_ids = mixin.select(query)
    return all_ids


def get_general_info_for_ophys_session_id(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_session_id = int(ophys_session_id)

    general_info_query = general_info_for_id_query()
    query_selection = '''
    WHERE os.id ={} '''.format(ophys_session_id)
    query = general_info_query + query_selection

    general_info = mixin.select(query)

    # ensure operating system compatible filepaths
    general_info = lims_utils.correct_general_info_filepaths(general_info)

    return general_info


# for behavior_session_id


def get_ophys_experiment_ids_for_behavior_session_id(behavior_session_id):
    behavior_session_id = int(behavior_session_id)
    query = '''
    SELECT
    oe.id
    AS ophys_experiment_id

    FROM behavior_sessions behavior

    JOIN ophys_experiments oe
    ON oe.ophys_session_id = behavior.ophys_session_id

    WHERE
    behavior.id = {}
    '''.format(behavior_session_id)
    ophys_experiment_ids = mixin.select(query)
    return ophys_experiment_ids


def get_ophys_session_id_for_behavior_session_id(behavior_session_id):
    """uses an sqlite to query lims2 database. Gets the ophys_session_id
       for a given behavior_session_id from the behavior_sessions table in
       lims.

       note: not all behavior_sessions have associated ophys_sessions. Only
       behavior_sessions where ophys imaging took place will have
       ophys_session_id's
    """
    behavior_session_id = int(behavior_session_id)
    query = '''
    SELECT
    ophys_session_id

    FROM behavior_sessions

    WHERE id = {}'''.format(behavior_session_id)
    ophys_session_id = mixin.select(query)
    ophys_session_id = ophys_session_id["ophys_session_id"][0]
    return ophys_session_id


def get_ophys_container_ids_for_behavior_session_id(behavior_session_id):
    behavior_session_id = int(behavior_session_id)
    query = '''
    SELECT
    container.visual_behavior_experiment_container_id
    AS ophys_container_id

    FROM
    ophys_experiments experiments

    JOIN behavior_sessions behavior
    ON behavior.ophys_session_id = experiments.ophys_session_id

    JOIN ophys_experiments_visual_behavior_experiment_containers container
    ON container.ophys_experiment_id = experiments.id

    JOIN ophys_sessions sessions on sessions.id = experiments.ophys_session_id

    WHERE
    behavior.id = {}
    '''.format(behavior_session_id)
    container_id = mixin.select(query)
    return container_id


def get_supercontainer_id_for_behavior_session_id(behavior_session_id):
    behavior_session_id = int(behavior_session_id)
    query = '''
    SELECT
    sessions.visual_behavior_supercontainer_id AS supercontainer_id

    FROM
    ophys_experiments experiments

    JOIN behavior_sessions behavior
    ON behavior.ophys_session_id = experiments.ophys_session_id

    JOIN ophys_experiments_visual_behavior_experiment_containers container
    ON container.ophys_experiment_id = experiments.id

    JOIN ophys_sessions sessions on sessions.id = experiments.ophys_session_id

    WHERE
    behavior.id = {}
    '''.format(behavior_session_id)
    supercontainer_id = mixin.select(query)
    supercontainer_id = supercontainer_id["supercontainer_id"][0]
    return supercontainer_id


def get_all_ids_for_behavior_session_id(behavior_session_id):
    """queries LIMS and gets all of the ids for a given behavior
    session id

    Parameters
    ----------
    behavior_session_id : int
        unique identifier for a behavior session

    Returns
    -------
    dataframe/table
        table with the following columns:
            ophys_experiment_id,
            ophys_session_id,
            behavior_session_id,
            ophys_container_id,
            supercontainer_id
    """
    behavior_session_id = int(behavior_session_id)

    all_ids_query = all_ids_for_id_query()
    query_selection = '''
    WHERE bs.id ={} '''.format(behavior_session_id)
    query = all_ids_query + query_selection

    all_ids = mixin.select(query)
    return all_ids


def get_general_info_for_behavior_session_id(behavior_session_id):
    """[summary]

    Parameters
    ----------
    behavior_session_id : [type]
        [description]

    Returns
    -------
    dataframe
        dataframe with the following columns:
            ophys_experiment_id
            ophys_session_id
            behavior_session_id
            foraging_id
            ophys_container_id
            supercontainer_id
            experiment_workflow_state
            session_workflow_state
            container_workflow_state
            specimen_id
            donor_id
            specimen_name
            date_of_acquisition
            session_type
            targeted_structure
            depth
            equipment_name
            project
            experiment_storage_directory
            session_storage_directory
    """
    behavior_session_id = int(behavior_session_id)

    general_info_query = general_info_for_id_query()
    query_selection = '''
    WHERE bs.id ={} '''.format(behavior_session_id)
    query = general_info_query + query_selection

    general_info = mixin.select(query)

    # ensure operating system compatible filepaths
    general_info = lims_utils.correct_general_info_filepaths(general_info)

    return general_info


# for ophys_container_id


def get_ophys_experiment_ids_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)
    query = '''
    SELECT
    ophys_experiment_id

    FROM
    ophys_experiments_visual_behavior_experiment_containers

    WHERE
    visual_behavior_experiment_container_id = {}
    '''.format(ophys_container_id)
    ophys_experiment_ids = mixin.select(query)
    return ophys_experiment_ids


def get_ophys_session_ids_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)
    query = '''
    SELECT
    oe.ophys_session_id

    FROM
    ophys_experiments_visual_behavior_experiment_containers oevbec

    JOIN ophys_experiments oe
    ON oe.id = oevbec.ophys_experiment_id

    WHERE
    oevbec.visual_behavior_experiment_container_id = {}
    '''.format(ophys_container_id)
    ophys_session_ids = mixin.select(query)
    return ophys_session_ids


def get_behavior_session_ids_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)
    query = '''
    SELECT
    bs.id
    AS behavior_session_id

    FROM
    ophys_experiments oe

    JOIN behavior_sessions bs
    ON bs.ophys_session_id = oe.ophys_session_id

    JOIN ophys_experiments_visual_behavior_experiment_containers oevbec
    ON oevbec.ophys_experiment_id = oe.id

    JOIN ophys_sessions os
    ON os.id = oe.ophys_session_id

    WHERE
    oevbec.visual_behavior_experiment_container_id = {}
    '''.format(ophys_container_id)
    behavior_session_id = mixin.select(query)
    return behavior_session_id


def get_supercontainer_id_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)
    query = '''
    SELECT
    os.visual_behavior_supercontainer_id AS supercontainer_id

    FROM
    ophys_experiments oe

    JOIN behavior_sessions bs
    ON bs.ophys_session_id = oe.ophys_session_id

    JOIN ophys_experiments_visual_behavior_experiment_containers oevbec
    ON oevbec.ophys_experiment_id = oe.id

    JOIN ophys_sessions os on os.id = oe.ophys_session_id

    WHERE
    oevbec.visual_behavior_experiment_container_id = {}
    '''.format(ophys_container_id)
    supercontainer_id = mixin.select(query)
    supercontainer_id = int(supercontainer_id['supercontainer_id'][0])
    return supercontainer_id


def get_all_ids_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)

    all_ids_query = all_ids_for_id_query()
    query_selection = '''
    WHERE
    oevbec.visual_behavior_experiment_container_id = {}
    '''.format(ophys_container_id)
    query = all_ids_query + query_selection

    all_ids = mixin.select(query)
    return all_ids


def get_general_info_for_ophys_container_id(ophys_container_id):
    ophys_container_id = int(ophys_container_id)

    general_info_query = general_info_for_id_query()
    query_selection = '''
    WHERE vbec.id ={} '''.format(ophys_container_id)
    query = general_info_query + query_selection

    general_info = mixin.select(query)

    # ensure operating system compatible filepaths
    general_info = lims_utils.correct_general_info_filepaths(general_info)
    return general_info


# for supercontainer_id


def get_ophys_experiment_ids_for_supercontainer_id(supercontainer_id):
    supercontainer_id = int(supercontainer_id)
    query = '''
    SELECT
    oe.id AS ophys_experiment_id

    FROM
    ophys_experiments oe

    JOIN ophys_sessions os
    ON os.id = oe.ophys_session_id

    WHERE
    os.visual_behavior_supercontainer_id = {}
    '''.format(supercontainer_id)
    ophys_experiment_ids = mixin.select(query)
    return ophys_experiment_ids


def get_ophys_session_ids_for_supercontainer_id(supercontainer_id):
    supercontainer_id = int(supercontainer_id)
    query = '''
    SELECT
    id AS ophys_session_id

    FROM
    ophys_sessions

    WHERE
    visual_behavior_supercontainer_id = {}
    '''.format(supercontainer_id)
    ophys_session_ids = mixin.select(query)
    return ophys_session_ids


def get_behavior_session_id_for_supercontainer_id(supercontainer_id):
    supercontainer_id = int(supercontainer_id)
    query = '''
    SELECT
    bs.id AS behavior_session_id

    FROM
    ophys_sessions os

    JOIN behavior_sessions bs
    ON bs.ophys_session_id = os.id

    WHERE
    os.visual_behavior_supercontainer_id = {}
    '''.format(supercontainer_id)
    behavior_session_ids = mixin.select(query)
    return behavior_session_ids


def get_ophys_container_ids_for_supercontainer_id(supercontainer_id):
    supercontainer_id = int(supercontainer_id)
    query = '''
    SELECT
    oevbec.visual_behavior_experiment_container_id
    AS ophys_container_id

    FROM
    ophys_experiments oe

    JOIN ophys_experiments_visual_behavior_experiment_containers oevbec
    ON oevbec.ophys_experiment_id = oe.id

    JOIN ophys_sessions os
    ON os.id = oe.ophys_session_id

    WHERE
    os.visual_behavior_supercontainer_id = {}
    '''.format(supercontainer_id)
    ophys_container_ids = mixin.select(query)
    return ophys_container_ids


def get_all_ids_for_supercontainer_id(supercontainer_id):
    """queries LIMS and gets all of the ids for a given
    supercontainer id

    Parameters
    ----------
    supercontainer_id : [type]
        [description]

    Returns
    -------
    dataframe/table
        table with the following columns:
            ophys_experiment_id,
            ophys_session_id,
            behavior_session_id,
            ophys_container_id,
            supercontainer_id
    """
    supercontainer_id = int(supercontainer_id)

    all_ids_query = all_ids_for_id_query()
    query_selection = '''
    WHERE
    os.visual_behavior_supercontainer_id = {}
    '''.format(supercontainer_id)
    query = all_ids_query + query_selection

    all_ids = mixin.select(query)
    return all_ids


def get_general_info_for_supercontainer_id(supercontainer_id):
    """[summary]

    Parameters
    ----------
    supercontainer_id : [type]
        [description]

    Returns
    -------
    dataframe
        dataframe with the following columns:
            ophys_experiment_id
            ophys_session_id
            behavior_session_id
            foraging_id
            ophys_container_id
            supercontainer_id
            experiment_workflow_state
            session_workflow_state
            container_workflow_state
            specimen_id
            donor_id
            specimen_name
            date_of_acquisition
            session_type
            targeted_structure
            depth
            equipment_name
            project
            experiment_storage_directory
            session_storage_directory
    """
    supercontainer_id = int(supercontainer_id)

    general_info_query = general_info_for_id_query()
    query_selection = '''
    WHERE
    os.visual_behavior_supercontainer_id ={} '''.format(supercontainer_id)
    query = general_info_query + query_selection

    general_info = mixin.select(query)

    # ensure operating system compatible filepaths
    general_info = lims_utils.correct_general_info_filepaths(general_info)

    return general_info


### TABLES ###    # noqa: E266


def get_cell_segmentation_runs_table(ophys_experiment_id):
    """Queries LIMS via AllenSDK PostgresQuery function to retrieve
        information on all segmentations run in the
        ophys_cell_segmenatation_runs table for a given experiment

    Arguments:
         ophys_experiment_id {int} -- 9 digit ophys experiment ID

    Returns:
        dataframe --  dataframe with the following columns:
                        id {int}:  9 digit segmentation run id
                        run_number {int}: segmentation run number
                        ophys_experiment_id{int}: 9 digit ophys experiment id
                        current{boolean}: True/False
                                    True: most current segmentation run
                                    False: not the most current segmentation run
                        created_at{timestamp}:
                        updated_at{timestamp}:
    """
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    select
    *

    FROM
    ophys_cell_segmentation_runs

    WHERE
    ophys_experiment_id = {}
    '''.format(ophys_experiment_id)
    return mixin.select(query)


def get_ophys_experiments_table(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)
    query = '''
    SELECT
    oe.id AS ophys_experiment_id,
    oe.workflow_state AS experiment_workflow_state,
    oe.storage_directory AS experiment_storage_directory,
    oe.ophys_session_id,
    structures.acronym AS targeted_structure,
    imaging_depths.depth AS imaging_depth,
    oe.calculated_depth,
    oevbec.visual_behavior_experiment_container_id AS ophys_container_id,
    oe.raw_movie_number_of_frames,
    oe.raw_movie_width,
    oe.raw_movie_height,
    oe.movie_frame_rate_hz,
    oe.ophys_imaging_plane_group_id

    FROM
    ophys_experiments_visual_behavior_experiment_containers oevbec

    JOIN ophys_experiments oe
    ON oe.id = oevbec.ophys_experiment_id

    JOIN structures ON structures.id = oe.targeted_structure_id
    JOIN imaging_depths ON imaging_depths.id = oe.imaging_depth_id

    WHERE
    oe.id = {}
    '''.format(ophys_experiment_id)
    ophys_experiments_table = mixin.select(query)
    return ophys_experiments_table


def get_ophys_sessions_table(ophys_session_id):
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    os.id AS ophys_session_id,
    os.storage_directory AS session_storage_directory,
    os.workflow_state AS session_workflow_state,
    os.specimen_id,
    os.isi_experiment_id,
    os.parent_session_id,
    os.date_of_acquisition,
    equipment.name AS equipment_name,
    projects.code AS project,
    os.stimulus_name AS session_type,
    os.foraging_id,
    os.stim_delay,
    os.visual_behavior_supercontainer_id AS supercontainer_id

    FROM
    ophys_sessions os

    JOIN equipment ON equipment.id = os.equipment_id

    JOIN projects ON projects.id = os.project_id

    WHERE
    os.id = {}
    '''.format(ophys_session_id)
    ophys_sessions_table = mixin.select(query)
    return ophys_sessions_table


def get_behavior_sessions_table(behavior_session_id):
    behavior_session_id = int(behavior_session_id)
    query = '''
    SELECT
    bs.id as behavior_session_id,
    bs.ophys_session_id,
    bs.behavior_training_id,
    bs.foraging_id,
    bs.donor_id,
    equipment.name as equipment_name,
    bs.created_at,
    bs.date_of_acquisition

    FROM
    behavior_sessions bs
    JOIN equipment ON equipment.id = bs.equipment_id

    WHERE
    bs.id = {}
    '''.format(behavior_session_id)
    behavior_sessions_table = mixin.select(query)
    return behavior_sessions_table


def get_visual_behavior_experiment_containers_table(ophys_container_id):
    ophys_container_id = int(ophys_container_id)
    query = '''
    SELECT
    vbec.id AS container_id,
    projects.code AS project,
    vbec.specimen_id,
    vbec.storage_directory AS container_storage_directory,
    vbec.workflow_state AS container_workflow_state

    FROM
    visual_behavior_experiment_containers as vbec
    JOIN projects on projects.id = vbec.project_id
    WHERE
    vbec.id = {}
    '''.format(ophys_container_id)
    visual_behavior_experiment_containers_table = mixin.select(query)
    return visual_behavior_experiment_containers_table


### ROI ###       # noqa: E266


def get_cell_exclusion_labels(ophys_experiment_id):
    query = '''
    SELECT
    oe.id AS ophys_experiment_id,
    cr.id AS cell_roi_id,
    rel.name AS exclusion_label

    FROM ophys_experiments oe

    JOIN ophys_cell_segmentation_runs ocsr
    ON ocsr.ophys_experiment_id=oe.id
    AND ocsr.current = 't'

    JOIN cell_rois cr ON cr.ophys_cell_segmentation_run_id=ocsr.id
    JOIN cell_rois_roi_exclusion_labels crrel ON crrel.cell_roi_id=cr.id
    JOIN roi_exclusion_labels rel ON rel.id=crrel.roi_exclusion_label_id

    WHERE
    oe.id = {}
    '''.format(ophys_experiment_id)
    return mixin.select(query)


### FILEPATHS FOR WELL KNOWN FILES###      # noqa: E266

## for ophys_experiment_id ##              # noqa: E266

def get_BehaviorOphysNWB_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'BehaviorOphysNwb'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_demixed_traces_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'DemixedTracesFile'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_motion_corrected_movie_filepath(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'MotionCorrectedImageStack'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_neuropil_correction_filepath(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'NeuropilCorrection'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_average_intensity_projection_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysAverageIntensityProjectionImage'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_dff_traces_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysDffTraceFile'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_event_trace_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysEventTraceFile'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_extracted_traces_input_filepath(ophys_experiment_id):
    """[summary]

    Parameters
    ----------
    ophys_experiment_id : int
        unique identifier for an ophys experiment

    Returns
    -------
    string for filepath
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysExtractedTracesInputJson'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_motion_preview_filepath(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysMotionPreview'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_motion_xy_offset_filepath(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysMotionXyOffsetData'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_neuropil_traces_filepath(ophys_experiment_id):
    """uses well known file system to query lims and get the directory
    and filename for the neuropil_traces.h5 for a given ophys experiment

    Parameters
    ----------
    ophys_experiment_id : int
        a unique identifier for an ophys experiment

    Returns
    -------
    filepath string
        AI network filepath string for neuropil_traces.h5 for a
        given ophys experiment.
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysNeuropilTraces'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_ophys_registration_summary_image_filepath(ophys_experiment_id):
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysRegistrationSummaryImage'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_roi_traces_filepath(ophys_experiment_id):
    """uses well known file system to query lims and get the directory
    and filename for the roi_traces.h5 for a given ophys experiment

    Parameters
    ----------
    ophys_experiment_id : int
        unique identifier for an ophys experiment

    Returns
    -------
    filepath
        filepath to the roi_traces.h5 for an ophys experiment
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysRoiTraces'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_time_syncronization_filepath(ophys_experiment_id):
    """for scientifica experiments only

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ophys_experiment_id = int(ophys_experiment_id)

    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysTimeSynchronization'
    AND wkf.attachable_id = {}
    '''.format(ophys_experiment_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


## for segmentation_id via ophys_experiment_id ##              # noqa: E266

def get_segmentation_objects_filepath(ophys_experiment_id):
    """use SQL and the LIMS well known file system to get the
       location information for the objectlist.txt file for a
       given cell segmentation run

    Arguments:
        segmentation_run_id {int} -- 9 digit segmentation run id

    Returns:
        list -- list with storage directory and filename
    """
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysSegmentationObjects'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_lo_segmentation_mask_filepath(ophys_experiment_id):
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysLoSegmentationMaskData'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_segmentation_mask_filepath(ophys_experiment_id):
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysSegmentationMaskData'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_segmentation_mask_image_filepath(ophys_experiment_id):
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysSegmentationMaskImage'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_ave_intensity_projection_filepath(ophys_experiment_id):
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysAverageIntensityProjectionImage'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_max_intensity_projection_filepath(ophys_experiment_id):
    current_seg_id = int(get_current_segmentation_run_id_for_ophys_experiment_id(ophys_experiment_id))
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id

    WHERE
    wkft.name = 'OphysMaxIntImage'
    AND wkf.attachable_id = {}
    '''.format(current_seg_id)
    RealDict_object = mixin.select(query)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


## for ophys_session_id ##              # noqa: E266


def get_timeseries_ini_filepath(ophys_session_id):
    """use SQL and the LIMS well known file system to get the
       timeseries_XYT.ini file for a given ophys session.
       Notes: only Scientifca microscopes prodice timeseries.ini files

    Arguments:
        ophys_session_id {int} -- 9 digit ophys session id

    Returns:

    """
    ophys_session_id = int(ophys_session_id)
    query = '''
    SELECT
    wkf.storage_directory || wkf.filename
    AS filepath

    FROM
    well_known_files wkf

    JOIN well_known_file_types wkft ON wkft.id=wkf.well_known_file_type_id
    JOIN specimens sp ON sp.id=wkf.attachable_id
    JOIN ophys_sessions os ON os.specimen_id=sp.id

    WHERE
    wkft.name = 'SciVivoMetadata'
    AND wkf.storage_directory LIKE '%ophys_session_{0}%'
    AND os.id = {0}
    '''.format(ophys_session_id)

    try:
        RealDict_object = mixin.select(query)
        filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
        return filepath
    except KeyError:
        print("Error: Must be collected on a scientifica microscope to have timeseries ini. \n Check that equipment_name = CAM2P.2, CAM2P.3, CAM2P.4, CAM2P.5 or CAM2P.6")


def get_stimulus_pkl_filepath(ophys_session_id):
    """use SQL and the LIMS well known file system to get the
        session pkl file information for a given
        ophys_session_id

    Arguments:
        ophys_session_id {int} -- 9 digit ophys session ID

    Returns:
        [type] -- [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 610487715
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_session_h5_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 610487713
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_behavior_avi_filepath(ophys_session_id):
    """use SQL and the LIMS well known file system to get the network
    video-0.avi (behavior video) filepath for a given ophys_session_id

    Parameters
    ----------
    ophys_session_id : int
        unique identifier for ophys session

    Returns
    -------
    string
        network filepath as a string
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 695808672
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_behavior_h5_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 695808672
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)

    filepath = RealDict_object['filepath'][0]
    filepath = filepath.replace('avi', 'h5')
    filepath = utils.correct_filepath(filepath)

    return filepath


def get_eye_tracking_avi_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 695808172
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_eye_tracking_h5_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 695808172
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)

    filepath = RealDict_object['filepath'][0]
    filepath = filepath.replace('avi', 'h5')
    filepath = utils.correct_filepath(filepath)

    return filepath


def get_ellipse_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM well_known_files

    WHERE
    well_known_file_type_id = 914623492
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_platform_json_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM well_known_files

    WHERE
    well_known_file_type_id = 746251277
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_screen_mapping_h5_filepath(ophys_session_id):
    """[summary]

    Parameters
    ----------
    ophys_session_id : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM well_known_files

    WHERE
    well_known_file_type_id = 916857994
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


def get_deepcut_h5_filepath(ophys_session_id):
    """use SQL and the LIMS well known file system to get the
        screen mapping .h5 file information for a given
        ophys_session_id

    Arguments:
        ophys_session_id {int} -- 9 digit ophys session ID

    Returns:
        [type] -- [description]
    """
    QUERY = '''
    SELECT
    storage_directory || filename
    AS filepath

    FROM
    well_known_files

    WHERE
    well_known_file_type_id = 990460508
    AND attachable_id = {0}
    '''.format(ophys_session_id)
    RealDict_object = mixin.select(QUERY)
    filepath = lims_utils.get_filepath_from_realdict_object(RealDict_object)
    return filepath


### WELL KNOWN FILES ###      # noqa: E303, E266


def load_demixed_traces_array(ophys_experiment_id):
    """use SQL and the LIMS well known file system to find and load
            "demixed_traces.h5" then return the traces as an array

        Arguments:
            ophys_experiment_id {int} -- 9 digit ophys experiment ID

        Returns:
            demixed_traces_array -- mxn array where m = rois and n = time
        """
    filepath = get_demixed_traces_filepath(ophys_experiment_id)
    demix_file = h5py.File(filepath, 'r')
    demixed_traces_array = np.asarray(demix_file['data'])
    demix_file.close()
    return demixed_traces_array


def load_neuropil_traces_array(ophys_experiment_id):
    """use SQL and the LIMS well known file system to find and load
            "neuropil_traces.h5" then return the traces as an array

        Arguments:
            ophys_experiment_id {int} -- 9 digit ophys experiment ID

        Returns:
            neuropil_traces_array -- mxn array where m = rois and n = time
        """
    filepath = get_neuropil_traces_filepath(ophys_experiment_id)
    f = h5py.File(filepath, 'r')
    neuropil_traces_array = np.asarray(f['data'])
    f.close()
    return neuropil_traces_array


def load_motion_corrected_movie(ophys_experiment_id):
    """uses well known file system to get motion_corrected_movie.h5
        filepath and then loads the h5 file with h5py function.
        Gets the motion corrected movie array in the h5 from the only
        datastream/key 'data' and returns it.

    Parameters
    ----------
    ophys_experiment_id : [type]
        [description]

    Returns
    -------
    HDF5 dataset
        3D array-like (z, y, x) dimensions
                        z: timeseries/frame number
                        y: single frame y axis
                        x: single frame x axis
    """
    filepath = get_motion_corrected_movie_filepath(ophys_experiment_id)
    motion_corrected_movie_file = h5py.File(filepath, 'r')
    motion_corrected_movie = motion_corrected_movie_file['data']
    return motion_corrected_movie


def load_rigid_motion_transform(ophys_experiment_id):
    """use SQL and the LIMS well known file system to locate
        and load the rigid_motion_transform.csv file for
        a given ophys_experiment_id

    Arguments:
        ophys_experiment_id {int} -- 9 digit ophys experiment ID

    Returns:
        dataframe -- dataframe with the following columns:
                        "framenumber":
                                  "x":
                                  "y":
                        "correlation":
                           "kalman_x":
                           "kalman_y":
    """
    filepath = get_motion_xy_offset_filepath(ophys_experiment_id)
    rigid_motion_transform_df = pd.read_csv(filepath)
    return rigid_motion_transform_df


def load_objectlist(ophys_experiment_id):
    """loads the objectlist.txt file for the current segmentation run,
       then "cleans" the column names and returns a dataframe

    Arguments:
        experiment_id {[int]} -- 9 digit unique identifier for the experiment

    Returns:
        dataframe -- dataframe with the following columns:
                    (from http://confluence.corp.alleninstitute.org/display/IT/Ophys+Segmentation)
            trace_index:The index to the corresponding trace plot computed
                        (order of the computed traces in file _somaneuropiltraces.h5)
            center_x: The x coordinate of the centroid of the object in image pixels
            center_y:The y coordinate of the centroid of the object in image pixels
            frame_of_max_intensity_masks_file: The frame the object mask is in maxInt_masks2.tif
            frame_of_enhanced_movie: The frame in the movie enhimgseq.tif that best shows the object
            layer_of_max_intensity_file: The layer of the maxInt file where the object can be seen
            bbox_min_x: coordinates delineating a bounding box that
                        contains the object, in image pixels (upper left corner)
            bbox_min_y: coordinates delineating a bounding box that
                        contains the object, in image pixels (upper left corner)
            bbox_max_x: coordinates delineating a bounding box that
                        contains the object, in image pixels (bottom right corner)
            bbox_max_y: coordinates delineating a bounding box that
                        contains the object, in image pixels (bottom right corner)
            area: Total area of the segmented object
            ellipseness: The "ellipticalness" of the object, i.e. length of
                         long axis divided by length of short axis
            compactness: Compactness :  perimeter^2 divided by area
            exclude_code: A non-zero value indicates the object should be excluded from
                         further analysis.  Based on measurements in objectlist.txt
                        0 = not excluded
                        1 = doublet cell
                        2 = boundary cell
                        Others = classified as not complete soma, apical dendrite, ....
            mean_intensity: Correlates with delta F/F.  Mean brightness of the object
            mean_enhanced_intensity: Mean enhanced brightness of the object
            max_intensity: Max brightness of the object
            max_enhanced_intensity: Max enhanced brightness of the object
            intensity_ratio: (max_enhanced_intensity - mean_enhanced_intensity)
                             / mean_enhanced_intensity, for detecting dendrite objects
            soma_minus_np_mean: mean of (soma trace – its neuropil trace)
            soma_minus_np_std: 1-sided stdv of (soma trace – its neuropil trace)
            sig_active_frames_2_5:# frames with significant detected activity (spiking):
                                  Sum ( soma_trace > (np_trace + Snpoffsetmean+ 2.5 * Snpoffsetstdv)
                                  trace_38_soma.png  See example traces attached.
            sig_active_frames_4: # frames with significant detected activity (spiking):
                                 Sum ( soma_trace > (np_trace + Snpoffsetmean+ 4.0 * Snpoffsetstdv)
            overlap_count: 	Number of other objects the object overlaps with
            percent_area_overlap: the percentage of total object area that overlaps with other objects
            overlap_obj0_index: The index of the first object with which this object overlaps
            overlap_obj1_index: The index of the second object with which this object overlaps
            soma_obj0_overlap_trace_corr: trace correlation coefficient
                                          between soma and overlap soma0
                                          (-1.0:  excluded cell,  0.0 : NA)
            soma_obj1_overlap_trace_corr: trace correlation coefficient
                                          between soma and overlap soma1
    """
    filepath = get_segmentation_objects_filepath(ophys_experiment_id)
    objectlist_dataframe = pd.read_csv(filepath)
    objectlist_dataframe = lims_utils.update_objectlist_column_labels(objectlist_dataframe)
    return objectlist_dataframe


def get_well_known_file_path(id, attachable_type, asset_name):
    '''
    returns the filepath for a given well known file asset
    Parameters:
    -----------
    id: int
        the id of the attachable_type
    attachable_type: str
        attachable type (e.g. 'OphysExperiment', 'OphysSession', 'BehaviorSession')
    asset_name: str
        the name of the desired asset (e.g. 'OphysRoiTraces'). Must exist for the given attachable type

    Returns:
    --------
    str
        filepath to asset
    '''
    wkf = db.get_well_known_files(id, attachable_id_type=attachable_type)

    assert asset_name in wkf.index.to_list(), 'only assets {} are available for {}'.format(wkf.index.to_list(), attachable_type)

    return '/' + ''.join([wkf.loc[asset_name]['storage_directory'], wkf.loc[asset_name]['filename']])


def get_ophys_experiment_id_for_cell_roi_id(cell_roi_id):
    '''
    returns the ophys experiment ID from which a given cell_roi_id was recorded
    Parameters:
    -----------
    cell_roi_id: int
        cell_roi_id of interest

    Returns:
    --------
    int
        ophys_experiment_id
    '''
    cell_roi_id = int(cell_roi_id)
    query_string = '''
    select ophys_experiment_id
    from cell_rois
    where id = {}
    '''

    return db.lims_query(query_string.format(cell_roi_id))


def get_id_type(input_id):
    '''
    a function to get the id type for a given input ID

    Examples:

    >> get_id_type(914580664)
    'ophys_experiment_id'

    >> get_id_type(914211263)
    'behavior_session_id'

    >> get_id_type(1086515263)
    'cell_specimen_id'

    >> get_id_type(914161594)
    'ophys_session_id'

    >> get_id_type(1080784881)
    'cell_roi_id'

    >> get_id_type(1234)
    'unknown_id'

    Parameters:
    -----------
    input_id : int
        id to search

    Returns:
    --------
    string
        The ID type, or 'unknown_id' if the ID type cannot be determined
    '''

    found_id_types = []

    # set up a general query string
    query = 'select * from {} where id = {} limit 1'

    # iterate over tables
    for table in ['ophys_experiments', 'ophys_sessions', 'behavior_sessions', 'cell_rois']:

        # check to see if the id is an index in the table
        if len(db.lims_query(query.format(table, input_id))) > 0:
            # add to list of found IDs
            found_id_types.append(table[:-1] + '_id')

    # a special case for cell_specimen_id given that there is no cell_specimens table
    cell_specimen_id_query = 'select * from cell_rois where cell_specimen_id = {} limit 1'
    if len(db.lims_query(cell_specimen_id_query.format(input_id))) > 0:
        # return if id is cell_specimen_id
        found_id_types.append('cell_specimen_id')

    # assert that no more than one ID type was found (they should be unique)
    assert len(found_id_types) <= 1, 'found ID in multiple tables: {}'.format(found_id_types)

    if len(found_id_types) == 1:
        # if only one id type was found, return it
        return found_id_types[0]
    else:
        # return 'unknown_id' if id was not found
        return 'unknown_id'
