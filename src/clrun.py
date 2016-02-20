
import clrunner

__name__ == "__main__":

    J_URL    = 'https://jenkins/jenkins/job/'
    J_JOB    = 'Test'
    C_URL    = 'http://coverity:8080'
    C_PROJ   = 'TEST'
    C_STREAM = 'NIGHTLY'
    C_MAP    = 'MAP'
    C_USER   = 'USER'
    C_PASS   = 'PASSWORD'
    M_SEARCH_PATH = 'build\\output'
    M_FILE_EXT = '.qac.log'
    
    # Run from correct relative path
    pass
    # Build model
    model = clrunner.get_model_desc(J_URL, J_JOB, 
                                    C_URL, C_PROJ, C_STREAM, C_MAP, C_USER, C_PASS,
                                    M_SEARCH_PATH, M_FILE_EXT,
                                    PATH_STRIP,
                                    include_jenkins=True,
                                    include_coveritry=True)
    # Convert
    json_data = clrunner.model_to_jsonable(model)
    # Export
    print(json.dumps(json_data))
