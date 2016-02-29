"""
# Copyright Oliver Vinn 2015
# github.com/ovinn/code-lytics
"""
import json
import clrunner

if __name__ == "__main__":
    # Settings
    J_URL = 'https://jenkins/jenkins/job/'
    J_JOB = 'Test'
    C_URL = 'http://coverity:8080'
    C_PROJ = 'TEST'
    C_STREAM = 'NIGHTLY'
    C_MAP = 'MAP'
    C_USER = 'USER'
    C_PASS = 'PASSWORD'
    M_SEARCH_PATH = 'build\\output'
    M_FILE_EXT = '.qac.log'
    PATH_STRIP = ['foo/bar', 'other/bar']

    # Run from correct relative path
    # os.chdir('..')

    # Build model
    METRIC_MODEL = clrunner.get_model_desc(J_URL, J_JOB,
                                           C_URL, C_PROJ, C_STREAM, C_MAP, C_USER, C_PASS,
                                           M_SEARCH_PATH, M_FILE_EXT,
                                           PATH_STRIP,
                                           include_jenkins=True,
                                           include_coveritry=True)
    # Convert
    METRIC_DATA_JSON = clrunner.model_to_jsonable(METRIC_MODEL)

    # Export
    print(json.dumps(METRIC_DATA_JSON))
