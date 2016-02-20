var TreemapGraphic = function(htmlId, data) {
	
	var sizeof_fmt = function(num) {
		return num;
	};

	var w = 1000,
	    h = 600,
	    x = d3.scale.linear().range([0, w]),
	    y = d3.scale.linear().range([0, h]),
	    color = d3.scale.category20c(),
	    root,
	    node;
	
	var treemap = d3.layout.treemap()
	    .round(true)
	    .size([w, h])
	    .sticky(false)
	    .value(function(d) { return d.size; });
		
	var svg = d3.select(htmlId)
	    .attr("class", "chart")
	    .attr("id", "treemapChart")
	    .style("width", w + "px")
	    .style("height", h + "px")
	  .append("svg:svg")
	    .attr("width", w - 5)
	    .attr("height", h - 4)
	  .append("svg:g")
	  .attr("transform", "translate(.5,.5)");
		
	node = root = data;
	
	var tooltip = d3.select("#treemap")
	  .append("div")
	  .attr('class', 'd3-tip')
	  .style("position", "absolute")
	  .style("z-index", "10")
	  .style("color", "white")
	  .style("background", "black")
	  .style("padding", "5px")
	  .style("border-radius", "3px")
	  .style("opacity", "0");
	
	var nodes = treemap
		.nodes(root)
	    .filter(function(d) { return !d.children; });
	
	var cell = svg.selectAll("g")
	      .data(nodes)
	      .enter()
	      .append("svg:g")
	      	.attr("class", "cell")
	      	.style("pointer-events", "none")
	      	.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
	      	;//.on("click", function(d) { return zoom(node == d.parent ? root : d.parent); });
	
	cell.append("svg:rect")
		  .on("mousemove", function(d){return tooltip.style("opacity", "1")
			  .html("<b>" + d.parent.name + "</b><br/>" 
					  + d.name + "<br/><small>" + sizeof_fmt(d.size) + "</small><br/>" + d.warnings + " warnings" +
					  "<br/>" + d.conditions + " conditionals")
					  .style("top",(d3.event.pageY-40)+"px").style("left",(d3.event.pageX+40)+"px");})
		  .on("mouseout", function(d){return tooltip.style("opacity", "0");})
	      .attr("width", function(d) { return Math.max(0, d.dx ); })
	      .attr("height", function(d) { return Math.max(0, d.dy); })
	      
	      .attr("stroke", "white")
	      .style("fill", function(d) { return color(d.parent.name); });
	
	cell.append("svg:text")
	      .attr("x", function(d) { return d.dx / 2; })
	      .attr("y", function(d) { return d.dy / 2; })
	      .style("pointer-events", "none")
	      .attr("dy", ".35em")
	      .attr("text-anchor", "middle")
	      .text(function(d) { return d.name; })
	      .style("opacity", function(d) { d.w = this.getComputedTextLength(); return d.dx > d.w ? (d.dy > 4) ? 1 : 0 : 0; });

	
	var _updateSelection = function(value) {
		if (value == "warnings") {
			treemap.value(function(d) { return d.warnings; } );
		} else if (value === "count") {
			treemap.value(function(d) { return 1; });
		} else if (value === "conditionals") {
			treemap.value(function(d) { return d.conditions; });
		} else {
			treemap.value(function(d) { return d.size; });
		}
		treemap.nodes(root);
	    zoom(root);
	};
	
	var _update = function(data) {
		var s_ = svg.select("").duration(750);
	};
		
	function zoom(d) {
	  var kx = (w / d.dx), ky = (h / d.dy);
	  x.domain([d.x, d.x + d.dx]);
	  y.domain([d.y, d.y + d.dy]);
	
	  var t = svg.selectAll("g.cell").transition()
	      .duration(600)
	      .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });
	
	  t.select("rect")
	      .attr("width", function(d) { return kx * d.dx; })
	      .attr("height", function(d) { return ky * d.dy; })
	
	  t.select("text")
	      .attr("x", function(d) { return (kx * d.dx / 2) ; })
	      .attr("y", function(d) { return (ky * d.dy / 2) ; })
	      .style("opacity", function(d) { return (kx * d.dx > d.w) ? (ky * d.dy > 4) ? 1 : 0 : 0; });
	
	  node = d;
	  if (d3.event) {
		  d3.event.stopPropagation();
	  }
	}	
	
	return {
		update: _update,
		updateSelection: _updateSelection
	}
};