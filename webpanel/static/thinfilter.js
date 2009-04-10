

$(document).ready(function() {
   if ( $("input#username") ){
     if ( $("input#username").text() != "")
        $("input#password").focus();
    
     else
        $("input#username").focus();
   }
});


function addtoselect(select1, select2){
    $('#'+select1+' option:selected').remove().appendTo('#'+select2);
}
function removefromselect(select1, select2){
    $('#'+select2+' option:selected').remove().appendTo('#'+select1);
}

/* dropdown menu */
$(document).ready(function(){
 $("ul.dropdown li").hover(function(){
   $(this).addClass("hover");
   $('> .dir',this).addClass("open");
   $('ul:first',this).css('visibility', 'visible');
 },function(){
   $(this).removeClass("hover");
   $('.open',this).removeClass("open");
   $('ul:first',this).css('visibility', 'hidden');
 });
});
