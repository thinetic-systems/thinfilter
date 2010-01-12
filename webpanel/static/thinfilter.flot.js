

function plot_hdd(dev, data) {

//        var data = {
//					items: [{label: 'September posts', data: 12015},
//						   {label: 'October posts', data: 23834},
//						   {label: 'November posts', data: 24689}]
//					};

		  // FLOT
		  jQuery(function () {
		    jQuery.plot(jQuery(dev), data.items, {
				pie: { 
					show: true, 
					pieStrokeLineWidth: 1, 
					pieStrokeColor: '#FFF', 
					//pieChartRadius: 100, 			// by default it calculated by 
					//centerOffsetTop:30,
					//centerOffsetLeft:30, 			// if 'auto' and legend position is "nw" then centerOffsetLeft is equal a width of legend.
					showLabel: true,				//use ".pieLabel div" to format looks of labels
					labelOffsetFactor: 4/6, 		// part of radius (default 5/6)
					//labelOffset: 0        		// offset in pixels if > 0 then labelOffsetFactor is ignored
					labelBackgroundOpacity: 0.55, 	// default is 0.85
					labelFormatter: function(serie){// default formatter is "serie.label"
					return serie.label+'<br/>'+Math.round(serie.percent)+'%';
					}
				},
				legend: {
					show: true, 
					position: "ne", 
					backgroundOpacity: 0
				}
			})
		  });



}
