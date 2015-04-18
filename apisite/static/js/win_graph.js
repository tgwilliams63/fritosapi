function win_graph(bt, data, ht){
	var chart = c3.generate({
		bindto: bt,
	    data: {
	        columns: [data],
	        names: {
	        	wrbm:'Winrate at Minute Bought'
	        },
	        type: 'line',
	    },
	    legend: {
	    	hide: true
	    },
	    axis:{
	    	y:{
	    		min: 0,
	    		max: 100,
	    		padding:{
	    			top: 2,
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
	                var format = id === 'data' ? d3.format(',') : d3.format('%');
	                return value +"%";
	            }
				//value: d3.format(',') // apply this format to both y and y2
	        }
	    }
	});
}