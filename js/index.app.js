
var Application = function (json_data_source) {

	function humanFileSize(bytes, si) {
		var thresh = si ? 1000 : 1024;
		if (Math.abs(bytes) < thresh) {
			return bytes + ' B';
		}
		var units = si
			 ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
			 : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
		var u = -1;
		do {
			bytes /= thresh;
			++u;
		} while (Math.abs(bytes) >= thresh && u < units.length - 1);
		return bytes.toFixed(1) + ' ' + units[u];
	}

	function formatSize(x) {
		if (x.hasOwnProperty('label')) {
			return x.label + ": " + humanFileSize(x.value);
		} else {
			return humanFileSize(x);
		}
	}

	function emptyIf0(x) {
		return x > 0 ? x : '';
	}

	function buildFileInfo(compobj) {
		var max_shown = 20;
		var st = '<div style="margin-left:20px" class="panel">';
		if (compobj !== undefined) {
			if (compobj.coverity_issues.length > 0) {
				st += "<h3>Coverity</h3>";
				st += '<table class="table table-responsive"><thead><td>CID</td><td>CHECKER</td><td>FUNCTION</td><thead>';
				for (s in compobj.coverity_issues) {

					var c = compobj.coverity_issues[s];
					st += "<tr><td>" + c.cid + " </td><td><a href=\"" + c.url + "\"> " + c.checker + "</a></td><td>" + c.function  + "</td></tr>";
			}
			if (compobj.coverity_issues.length >= max_shown) {
				st += "<tr><td></td><td colspan=\"2\"> TOO MANY ISSUES TO DISPLAY </td>";
			}
			st += '</table>';
		}

		if (compobj.compiler_issues.length > 0) {
			st += "<h3>Compiler Warnings</h3>";
			st += '<table class="table table-responsive"><thead><td>LINE</td><td>MESSAGE</td><thead>';
			for (i = 0; i < compobj.compiler_issues.length && i < max_shown; i++) {
				var c = compobj.compiler_issues[i];
				st += "<tr><td>" + c.line + "</td><td><a href=\"" + c.url + "\">" + c.message + "</a><br/>";
			}
			if (compobj.compiler_issues.length >= max_shown) {
				st += "<tr><td></td><td> TOO MANY ISSUES TO DISPLAY </td>";
			}
			st += '</table>';
		}

		if (Object.keys(compobj.misra_issues).length > 0) {
			st += "<h3>MISRA Warnings</h3>";
			st += '<table class="table table-responsive"><thead><td>LEVEL</td><td>LINE</td><td>DETAIL</td><thead>';

			var limit_cnt = 0;
			for (s_ in compobj.misra_issues) {
				for (s in compobj.misra_issues[s_]) {
					var c = compobj.misra_issues[s_][s];
					st += "<tr><td>" + s_ + "</td><td>" + c.line + "</td><td>" + c.detail + "</td></tr>";
					limit_cnt++;
					if (limit_cnt >= max_shown) {
						st += "<tr><td></td><td colspan=\"2\"> TOO MANY ISSUES TO DISPLAY </td>";
						break;
					}
				}
			}

			st += '</table>';
		}
		return st + "</div>";
	}
	return "";
};

	function processFile(groupObj) {
		
	}

	$.getJSON(json_data_source)
	.then(function (model) {
		
		var data = model.data;
		var rules = model.groups;
		var stats = model.stats;
		var overview = { 'groups' : {}, 'totals' : {} };

		for (var j = 0; j < data.length; j++) {
			
			var group = data[j];
			var name = group.name;
			var files = group.files;			
			overview[name] = {
				'compiler': 0,
				'misra_7' : 0,
				'misra_8' : 0,
				'coverity': 0,
				'files'   : 0,
				'size'    : 0
			};

			var html_group = "";
			for (var i = 0; i < files.length; i++) {				
				var file = files[i];
				
				if (file.compiler_issues.length > 0 ||
					file.coverity_issues.length > 0 ||
					Object.keys(file.misra_issues) > 0) {
						
					html_group +=
					'<tr data-group-index="' + j + '" data-file-index="' + i + '" class="issuerow">' +
					'<td></td>' +
					'<td><div style="margin-right:10px"> </div>' + file.path      + '</td>' +
					'<td align="center">' + emptyIf0(file.compiler_issues.length) + '</td>' +
					'<td align="center">' + emptyIf0(file.coverity_issues.length) + '</td>';

					if (file.misra_issues[7] !== undefined) {
						html_group += '<td align="center">' + emptyIf0(file.misra_issues[7].length) + '</td>';
						overview[name].misra_7 += file.misra_issues[7].length;
					} else {
						html_group += '<td></td>';
					}
					
					if (file.misra_issues[8] !== undefined) {
						html_group += '<td align="center">' + emptyIf0(file.misra_issues[8].length) + '</td>';
						overview[name].misra_8 += file.misra_issues[8].length;
					} else {
						html_group += '<td></td>';
					}
					
					html_group += '</tr>';
					
					overview[name].compiler += file.compiler_issues.length;
					overview[name].coverity += file.coverity_issues.length;
				}
				overview[name].size += file.size;
				overview[name].files++;
			}
			
			var html_total =
			'<td align="center">' + emptyIf0(overview[name].compiler) + '</td>' +
			'<td align="center">' + emptyIf0(overview[name].coverity) + '</td>' +
			'<td align="center">' + emptyIf0(overview[name].misra_7)  + '</td>' +
			'<td align="center">' + emptyIf0(overview[name].misra_8)  + '</td>' +
			'<td align="center">' + (overview[name].compiler + 
			                         overview[name].coverity + 
			                         overview[name].misra_8) + '</td></tr>';
			
			$("#comps")
			.append('<tr class="issuegroupexpander" style="background-color:#eeeeee" data-group-index="' + j + '">' +
				'<td colspan="2"><div class="glyphicon glyphicon-chevron-right" style="margin-right:10px"> </div>' +
				name + html_total + html_group);
		}

		$('.issuegroupexpander').on('click', '', function (event) {
			$curRow = $(this).closest('tr');
			if (!$curRow[0].hasAttribute('expanded')) {
				$curRow.attr('expanded', true);

				$g = Number($curRow.attr("data-group-index"));
				$ma = $('.issuerow[data-group-index="' + $g + '"]');
				$ma.show();
				$curRow.find('td div').removeClass(" glyphicon-chevron-right");
				$curRow.find('td div').addClass(" glyphicon-chevron-down");

			} else {
				$curRow.removeAttr('expanded');
				$g = Number($curRow.attr("data-group-index"));
				$ma = $('.issuerow[data-group-index="' + $g + '"]');
				$ma.hide();
				$curRow.find('td div').addClass(" glyphicon-chevron-right");
				$curRow.find('td div').removeClass(" glyphicon-chevron-down");
			}
		});

		$('.issuerow').on('click', '', function (event) {
			$curRow = $(this).closest('tr');
			if (!$curRow.next('tr').hasClass('issuerowdetail')) {
				$g = Number($curRow.attr("data-group-index"));
				$i = Number($curRow.attr("data-file-index"));
				$file = $curRow.find("td:nth-child(2)").text();

				$f = data[$g].files[$i];
				$curRow.after('<tr class="issuerowdetail"><td></td><td colspan="4">' + buildFileInfo($f) + '</td></tr>');
				$curRow.find('td div').removeClass("glyphicon-chevron-right");
				$curRow.find('td div').addClass("glyphicon-chevron-down");
			} else if ($curRow.next('tr').hasClass('issuerowdetail')) {
				$curRow.next().remove();
				$curRow.find('td div').removeClass("glyphicon-chevron-down");
				$curRow.find('td div').addClass("glyphicon-chevron-right");
			}
		});

		$(document).ready(function () {
			$(".dropdown-menu").append('<li><a ref="#">[ALL]</a></li>');
			$(".dropdown-menu").append('<li><a ref="#">[OVERVIEW]</a></li>');
			for (i = 0; i < data.length; i++) {
				$(".dropdown-menu").append('<li><a ref="#">' + data[i].name + '</a></li>');
			};

			$(".dropdown-menu li").on("click", function (event) {
				var x = event.target.innerText;
				if (x === '[ALL]' || x === undefined) {
					$('.issuerow').show();
				} else if (x === '[OVERVIEW]' || x === undefined) {
					$('.issuerow').hide();
				} else {
					for (var j = 0; j < data.length; j++) {
						if (data[j].name === x) {
							x = j;
						}
					}

					$('.issuerow').hide();
					$(".issuerow[data-group-index='" + x + "']").show();
				}
			});

			$('.issuerow').hide();
		});

		var scheme = new ColorScheme;
		scheme.from_hue(50)
		.scheme('contrast')
		.variation('pastel')

		var c_colors = scheme.colors();
		var index = 0;
		Object.keys(overview).forEach(function (o) {
			overview[o].color = "#" + c_colors[index++];
		});

		var data_comp = [];
		var comp_sum_cnt = 0;
		var data_cov = [];
		var cov_sum_cnt = 0;
		var data_misra = [];
		var misra_sum_cnt = 0;
		var data_size = [];
		var size_cnt = 0;
		var data_files = [];
		var files_cnt = 0;
		var linesofcode = [];
		var linesofcode_cnt = 0;

		Object.keys(overview).forEach(function (o) {
			data_comp.push({
				'label' : o,
				'value' : overview[o].compiler,
				'color' : overview[o].color,
				'labelFontSize' : '10',
				'labelColor' : 'white',
				'labedl' : '',
				'highlights' : overview[o].color
			});
			comp_sum_cnt += overview[o].compiler;
			data_cov.push({
				'label' : o,
				'value' : overview[o].coverity,
				'color' : overview[o].color,
				'highlights' : overview[o].color
			});
			cov_sum_cnt += overview[o].coverity;
			data_misra.push({
				'label' : o,
				'value' : overview[o].misra_8,
				'color' : overview[o].color,
				'highlights' : overview[o].color
			});
			misra_sum_cnt += overview[o].misra_8;
			data_size.push({
				'label' : o,
				'value' : overview[o].size,
				'color' : overview[o].color,
				'highlights' : overview[o].color
			});
			size_cnt += overview[o].size;
			data_files.push({
				'label' : o,
				'value' : overview[o].files,
				'color' : overview[o].color,
				'highlights' : overview[o].color
			});
			files_cnt += overview[o].files;
			if (stats[o] !== undefined) {
				linesofcode.push({
					'label' : o,
					'value' : stats[o],
					'color' : overview[o].color,
					'highlights' : overview[o].color
				});
				linesofcode_cnt += stats[o];
			}
		});
		data_comp.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});
		data_cov.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});
		data_misra.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});
		data_size.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});
		data_files.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});
		linesofcode.sort(function (a, b) {
			if (a.value < b.value)
				return -1;
			else if (a.value > b.value)
				return 1;
			else
				return 0;
		});

		Chart.types.Doughnut.extend({
			// Passing in a name registers this chart in the Chart namespace in the same way
			name : "DoughnutNumber",
			draw : function () {
				Chart.types.Doughnut.prototype.draw.apply(this, arguments);
				//if (this.done) {
				{ //this.chart.ctx.fillText("Hello", this.txtPosx, this.textPos);
					this.chart.ctx.textBaseline = "middle";
					this.chart.ctx.fillStyle = '#aaaaaa';
					this.chart.ctx.font = "50px Helvetica";
					this.chart.ctx.textAlign = "center";
					this.chart.ctx.fillText(this.options.titelvalue, 175, 200);
					this.chart.ctx.font = "14px Helvetica";
					this.chart.ctx.fillText(this.options.titlename, 175, 230);
				}
			}
		});

		Chart.types.Doughnut.extend({
			// Passing in a name registers this chart in the Chart namespace in the same way
			name : "DoughnutNumberSmall",
			draw : function () {
				Chart.types.Doughnut.prototype.draw.apply(this, arguments);
				//if (this.done) {
				{ //this.chart.ctx.fillText("Hello", this.txtPosx, this.textPos);
					this.chart.ctx.textBaseline = "middle";
					this.chart.ctx.fillStyle = '#aaaaaa';
					this.chart.ctx.font = "15px Helvetica";
					this.chart.ctx.textAlign = "center";
					this.chart.ctx.fillText(this.options.titelvalue, 150, 100);
					this.chart.ctx.font = "10px Helvetica";
					this.chart.ctx.fillText(this.options.titlename, 150, 120);
				}
			}
		});

		function commaSeparateNumber(val) {
			while (/(\d+)(\d{3})/.test(val.toString())) {
				val = val.toString().replace(/(\d+)(\d{3})/, '$1' + ',' + '$2');
			}
			return val;
		}

		var ctx1 = $("#chart_cov").get(0).getContext("2d");
		var myDoughnutChart1 = new Chart(ctx1).DoughnutNumber(data_cov);
		myDoughnutChart1.options['titlename'] = 'Coverity';
		myDoughnutChart1.options['titelvalue'] = cov_sum_cnt;
		myDoughnutChart1.options.percentageInnerCutout = 60;

		var ctx2 = $("#chart_comp").get(0).getContext("2d");
		var myDoughnutChart2 = new Chart(ctx2).DoughnutNumber(data_comp);
		myDoughnutChart2.options['titlename'] = 'Compiler';
		myDoughnutChart2.options['titelvalue'] = comp_sum_cnt;
		myDoughnutChart2.options.percentageInnerCutout = 60;

		var ctx = document.getElementById("chart_misra").getContext("2d");
		var myDoughnutChart3 = new Chart(ctx).DoughnutNumber(data_misra);
		myDoughnutChart3.options['titlename'] = 'MISRA L8';
		myDoughnutChart3.options['titelvalue'] = misra_sum_cnt;
		myDoughnutChart3.options.percentageInnerCutout = 60;

		var ctx = document.getElementById("chart_stats").getContext("2d");
		var myDoughnutChart3 = new Chart(ctx).DoughnutNumberSmall(linesofcode);
		myDoughnutChart3.options['titlename'] = 'LOC';
		myDoughnutChart3.options['titelvalue'] = commaSeparateNumber(linesofcode_cnt);
		myDoughnutChart3.options.percentageInnerCutout = 60;
	});
};
