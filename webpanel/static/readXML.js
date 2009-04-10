// File: readXML.js

var runloop=1;

function reloadPhones(){
	// emty div
	$("#ContentArea").empty();
	
	// put loading image
	$("#ContentArea").append('<img class="center" src="/data/loading.gif" alt="loading..."/>');
	
	// Open the students.xml file
	$.get("/phones.xml",{},function(xml){
		
		// Build an HTML string
		myHTMLOutput = '';
		myHTMLOutput += '<table width="70%" id="phones">';
		myHTMLOutput += '<thead class="ttitle"> <tr> <td>MAC</td> <td>Estado</td> <td>Encontrado</td> <td>Enviado</td> </tr> </thead>';
		
		var number=0;
		// Run the function for each student tag in the XML file
		$('phone',xml).each(function(i) {
			phoneMAC = $(this).find("address").text();
			phoneStatus = $(this).find("status").text();
			phoneSearch = $(this).find("date_search").text();
			phoneSend = $(this).find("date_send").text();
			
			// Build row HTML data and store in string
			mydata = BuildPhonesHTML(phoneMAC,phoneStatus,phoneSearch,phoneSend);
			myHTMLOutput = myHTMLOutput + mydata;
			number++;
		});
		if (number > 15) {
			// append table titles if phones > 15
			myHTMLOutput += '<tr class="ttitle"> <td>MAC</td> <td>Estado</td> <td>Encontrado</td> <td>Enviado</td> </tr>';
		}
		myHTMLOutput += '</table>';
		
		// Update the DIV called Content Area with the HTML string
		$("#ContentArea").empty();
		$("#ContentArea").append(myHTMLOutput);
		// scroll to bottom
		$("#ContentArea").attr({ scrollTop: $("#ContentArea").attr("scrollHeight") });
	});
}


function BuildPhonesHTML(phoneMAC,phoneStatus,phoneSearch,phoneSend){
	
	// Build HTML string and return
	output = '';
	output += '<tr>';
	output += '<td>'+ phoneMAC + '</td>';
	output += '<td>'+ phoneStatus +'</td>';
	output += '<td>'+ phoneSearch +'</td>';
	output += '<td>'+ phoneSend +'</td>';
	output += '</tr>';
	return output;
}

function phoneLoop() {
	if( runloop == 1 ) {
		reloadPhones();
		$("#status").html("recargando cada 5 segs");
	}
	else {
		$("#status").html("parado");
	}
}

function phoneReload() {
	$("#status").html("cargando...");
	runloop=1;
}

function phoneStop() {
	$("#status").html("parando...");
	runloop=0;
}


$(document).ready( reloadPhones );
window.setInterval( phoneLoop ,5000); 
