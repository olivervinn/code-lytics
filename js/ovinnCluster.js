var ClusterGraphic = function(root) {
	
	var tooltip = d3.select("#cluster")
  		  .append("div")
	      .attr('class', 'd3-tip2')
		  .style("position", "absolute")
		  .style("z-index", "10")
		  .style("color", "white")
		  .style("background", "black")
		  .style("padding", "5px")
		  .style("border-radius", "3px")
		  .style("opacity", "0");
	
	var width = 880, height = 400;
	var radius = width / 2;
	
	var cluster = d3.layout.cluster()
	      .size([360, radius - 120]);
	
	var svgr = d3.select("#cluster").append("svg")
	      .attr("width", radius * 2)
	      .attr("height", radius * 2);
	
	var svg = svgr.append("g")
	      .attr("transform", function(d) {
	    	  return "translate(" + radius + "," + radius + ")";
	    	  });
	
    var data = cluster.nodes(root);
	
    var diagonal = d3.svg.diagonal.radial()
	      .projection(function(d) {
	    	  return [d.y, d.x / 180 * Math.PI];
	    	  });
	
	var link = svg.selectAll("path.link")
	      .data(cluster.links(data))
        .enter().append("path")
        /*.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; })
        */
	      .attr("class", "link")
	      .attr("d", diagonal);
	
	var node = svg.selectAll("g.node")
	      .data(data)
	    .enter().append("g")
	      .attr("class", "node")
	      .on("mousemove", function(d) {
	    	  return tooltip
	    	      .style("opacity", "1").html("<b>" + d.name + "<br/><small>" + d.size + "</small><br/>" + d.warnings + " warnings")
	    		  .style("top",(d3.event.pageY-40)+"px").style("left",(d3.event.pageX+40)+"px");
	    	  })
	      .on("mouseout", function(d) {
	    	  return tooltip.style("opacity", "0");
	    	  })
	      .attr("transform", function(d) {
	    	  return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
	    	  })

    node.append("circle")
	    .attr("r", 4)
	    /*
	     .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })*/
	    .style("fill", function(d) { return d.warnings > 0 ? "red" : "white"; })
	    .style("stroke", function(d) {
	    	  if (!d.parent) { 
	            	return "black"; 
	          }
	    	  else if (d.parent === root) {
	          	return d.warnings > 0 ? "red" : "orange"; 
	          }
	          return "steelblue";
	});
	
	node.append("text")
	      .attr("dy", ".31em")
	      .style("font-size", function(d) { if (d.parent === root ) {  return "1.1em"; } return "0.9em"; })
	      .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
	      .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
	      .text(function(d) { return d.name; });


	d3.select(self.frameElement).style("height", radius * 2 + "px");
};