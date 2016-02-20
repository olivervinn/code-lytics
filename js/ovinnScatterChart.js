
var ScatterCompareGraphic = function(htmlId, data, prop, prop2) {

	var map = {};
	var stats = {};
	
	var margin = {top: 20, right: 40, bottom: 30, left: 200},
	    bwidth = 1060
	    bheight = 600
	    width = bwidth - margin.left - margin.right,
	    height = bheight - margin.top - margin.bottom;
	
	var color = d3.scale.category10();
		
	console.info("Adding char to " + htmlId);
	var svg = d3.select(htmlId).append("svg")
	    .attr("height", bheight)
	    .attr("viewBox", "0 0 " + bwidth + " " + bheight)
	    .attr("preserveAspectRatio", "xMinYMin meet")
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	
  var nextId = 0;
  var data_raw = data;
  var data_show = [];

  data.forEach(function(d) {
    if ('depends-on' in d && Object.keys(d['depends-on']).length > 0) {
      d.datax = Object.keys(d[prop]).length;
      d.datay = Object.keys(d[prop2]).length;
      data_show.push(d);
    }
  });

  var x = d3.scale.linear()
    .range([0, width]);

  var y = d3.scale.linear()
    .range([height, 0]);

  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

  var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

  var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    return "<strong>" + ((d[prop].length === undefined) ? '' : d[prop].length) + "</strong> <span style='color:red'>" + d.path + "</span>";
  })

  svg.call(tip);

  x.domain(d3.extent(data, function(d) { return d.datax; })).nice();
  y.domain(d3.extent(data, function(d) { return d.datay; })).nice();

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text(prop);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);
    

  var radius = 3;
  var band = 0;
  
  svg.selectAll(".dot")
      .data(data_show)
    .enter().append("circle")
      .attr("class", "dot")
      .attr("r", radius)
      .attr("opacity", "0.4")
      .attr("transform", "translate(0, " + band + ")")
      .attr("cx", function(d) { return x(d.datax); })
      .attr("cy", function(d) { return y(d.datay); })      
      .style("fill", function(d) { return color(d.species); })
      .on("mouseover", tip.show)
      .on("mouseout", tip.hide);
	
};

 