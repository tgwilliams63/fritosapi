function line_graph(bt, data, ht){
	var chart = c3.generate({
		bindto: bt,
	    data: {
	        columns: [data],
	        names: {
	        	bpm:'Number of Times Item Bought Per Minute'
	        },
	        type: 'spline',
	    },
	    legend:{
	    	hide: true
	    },
	    axis:{
	    	y:{
	    		min: 0,
	    		padding:{
	    			top: 10,
	    			bottom: 0
	    		}
	    	}

	    },
	    size:{
	    	height: ht
	    },
        tooltip: {
	        format: {
	            title: function (d) { return 'Minute ' + d; },
	            value: function (value, ratio, id) {
	                var format = id === 'data' ? d3.format(',') : d3.format('');
	                return format(value);
	            }
				//value: d3.format(',') // apply this format to both y and y2
	        }
	    }

	});
}