var OvinnJenkinsAPI = function(baseUrl) {
	
	var apiUrl = baseUrl;
	
	var _getProjectStatus = function(projectJobName, onComplete) {
		var _result = {
			"error" : null,
			"number" : -1,
			"status" : "unknown",
			"newWarnings" : -1,
			"url" : null,
			"building" : false
		};
		
		//$.getJSON(apiUrl + projectJobName + "/lastBuild/warningsResult/api/json?depth=0"))
		$.getJSON(apiUrl + projectJobName + "/lastBuild/api/json?depth=0")
			.fail(function(data) {
				_result.error = "failed";
				onComplete(_result);
			})
			.done(function(pStatus) {
				if (pStatus) {
					_result.number = pStatus.number;
					_result.status = pStatus.result;
					_result.building = pStatus.building;
					_result.url = pStatus.url;
				}
				onComplete(_result);
			});		
	};
	
	var _getProjectWarnings = function(projectJobName, onComplete) {
		var _result = {
			"error" : null,
			"newWarnings" : -1,
			"url" : null,
		};
		
		$.getJSON(apiUrl + projectJobName + "/lastBuild/warningsResult/api/json?depth=0")
			.fail(function(data) {
				_result.error = "failed";
				onComplete(_result);
			})
			.done(function(data) {
				if (data) {
		    		_result.newWarnings = data.numberOfNewWarnings;
				} 
				onComplete(_result);
			});		
	};


	return {
		projectStatus: _getProjectStatus,
		projectWarnings: _getProjectWarnings
	}
};
