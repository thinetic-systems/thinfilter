/*# InlineEditor.js 2007-01-04 18:22:00 mariodebian 
#
#        InlineEditor AJAX, prototype
#  Mario Izquierdo (mariodebian) \at\ gmail
#               8 dic 2006
#
# InlineEditor is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# InlineEditor is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with InlineEditor, if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.
*/

var ajax_timeout;


//algunas variables globales
var fila=0;
var editado=false;
var celdas=new Array();
var celdas_num=0;
var accion="";
var celdamaestra="";

function IEAddEditable (nombre, tipo, extra) {
    // añade al array de celdas editables una nueva celda
    celdas[celdas_num]=new Array();
    celdas[celdas_num]['nombre']=nombre;
    celdas[celdas_num]['tipo']=tipo;
    celdas[celdas_num]['extra']=extra;
    celdas_num++;
}

function IEEditarFila(id){
    //editar fila, activa las celdas editables del numero de fila que se pase
    //IEHideMessage(1);
    
    
    if (fila != 0) {
        if ( ! IECancelar(fila) ) {
            return;
        }
    }
    
    //console.log("IEEditarFila() i="+id);
    for(i=0;i<celdas.length;i++){
        IEMakeEditable(celdas[i]['nombre'] + "-" + id, celdas[i]['tipo'], celdas[i]['extra']);
    }
    IEVerControles("editar-" + id);
    fila=id;
}


function IEMakeEditable(elem, tipo, extras){
    //console.log("IEMakeEditable elem="+elem+" tipo="+tipo+" extras="+extras);
    // añade el codigo html para cada celda
    nombre=$("#" + elem)[0].id;
    defvalue=$("#"+elem)[0].innerHTML;
        
    if(tipo == "text") {
        $("#"+elem)[0].innerHTML=IEMakeInput(nombre, defvalue, extras);
    }
    else if(tipo== "select") {
        $("#"+elem)[0].innerHTML=IEMakeSelect(nombre, extras, defvalue);
    }
    else if(tipo== "checkbox") {
        $("#"+elem)[0].innerHTML=IEMakeCheckbox(nombre, defvalue);
    }
    else if(tipo == "textarea" ) {
        $("#"+elem)[0].innerHTML=IEMakeTextArea(nombre, defvalue, extras);
    }
    else {
        alert("Tipo de campo no soportado: '"+tipo+"' para la celda: '"+elem+"'");
    }
    $("#"+elem)[0].innerHTML+="<input type='hidden' id='old-"+nombre+"' name='old-"+nombre+"' value='"+defvalue+"'>";    
    return;
}

function IEMakeNoEditable(elem){
    // quita el html para dejar solo el valor
    nombre='old-' + elem;
    valor=$("#"+nombre)[0].value;
    $("#"+elem)[0].innerHTML=valor;
}

function IEMakeNoEditableFromNew(elem, obj){
    // quita el html para dejar solo el valor
    nombre='edit-' + elem;
    valor=$("#"+nombre)[0].value;
    if (obj) {
        for(j=0;j<obj.length;j++){
            //console.log("obj["+j+"]=> texto="+obj[j]['texto'] + " valor="+obj[j]['valor']);
            if ( (valor==obj[j]['valor']) || (valor==obj[j]['texto']) ){
                valor=obj[j]['texto'];
                $("#"+elem)[0].innerHTML=obj[j]['texto'];
                return;
            }
        }
    }
    $("#"+elem)[0].innerHTML=valor;
}

function IEMakeInput(name, defvalue, extras) {
    // crea un campo input text
    return "<input type='text' id='edit-"+name+"' name='edit-"+name+"' value='"+defvalue+"' onchange='javascript:IESetEditado(\"edit-"+name+"\")' "+extras+" /><br/>";
}
 
function IEMakeSelect(name, values, defvalue) {
    // crea un campo desplegable, las opciones se pasan como array['texto'] array['valor']
    txt="<select id='edit-"+name+"' name='edit-"+name+"' onchange='javascript:IESetEditado(\"edit-"+name+"\")'>";
    for(j=0;j<values.length;j++){
        deftxt='';
        if( (defvalue == values[j]['valor']) || (defvalue == values[j]['texto']) ) {
            deftxt=' selected';
        }
        txt+='<option value="'+values[j]['valor']+'" '+deftxt+'>'+values[j]['texto']+'</option>';
    }         
    txt+="</select>";
    return txt;
}

function IEMakeCheckbox(name, selected) {
    // crea un campo activable
    checktxt="";
    if( defvalue == "1" ){
        checktxt=" checked";
    }
    return '<input type="checkbox" id="edit-'+name+'" onchange="javascript:IESetEditado(\'edit-'+name+'\');" '+checktxt+'>';
}

function IEMakeTextArea(name, defvalue, extras){
    txt="<textarea id='edit-"+name+"' name='edit-"+name+"' ";
    txt+="onchange='javascript:IESetEditado(\"edit-"+name+"\")' "+extras+" />"+defvalue+"</textarea><br/>";
    return txt;
}

function IEVerControles(elem){
    // muestra en la columna de ediccion las imágenes 
    $("#"+elem)[0].innerHTML="<a href='javascript:void(IECancelar(fila));' title='Cancelar'><img src='"+baseimg+"/iecancel.png' title='Cancelar'></a>&nbsp;&nbsp;";
    $("#"+elem)[0].innerHTML+="<a href='javascript:void(IEGuardar(fila));' title='Guardar'><img src='"+baseimg+"/iesave.png' title='Guardar'></a>&nbsp;&nbsp;";
    $("#"+elem)[0].innerHTML+="<a href='javascript:void(IEBorrar(fila));' title='Borrar'><img src='"+baseimg+"/iedelete.png' title='Borrar'></a>";
}
    
function IEOcultarControles(elem, id) {
    // pone la imagen de editar
    //console.log("IEOcultarControles() elem="+elem);
    $("#"+elem)[0].innerHTML="<a href='javascript:IEEditarFila("+id+");' title='Editar'><img src='"+baseimg+"/ieedit.png' alt='Editar'></a>";
    return;
}
    
function IESetEditado(elem){
    // se activa cada vez que cambia un valor en los editables
    // así se puede avisar para no perder cambios
    editado=true;
}

function __IEGetNextPunto(){
    var lists = document.getElementsByClassName(celdamaestra);
    var puntos=new Array();
    for (var i = 0; i < lists.length; i++) {
        puntos[i]=lists[i].id.split('-')[1];
    }
    var max=parseInt(puntos.max());
    return max+1;
}

function __IEGetLastClassName(fila){
    classname=$('#' + celdamaestra + '-'+fila)[0].className;
    if(classname == celdamaestra + " odd"){
        return "even";
    }
    else if(classname == celdamaestra + " even" ) {
        return "odd";
    }
}


/*************************************************
*
*      Funciones que hacen cosas (que original)
*
**************************************************/

function IECancelar(id){
        // si añadimos una nueva línea y no la editamos
        // cancelar la borra
        for(i=0;i<celdas.length;i++){
            if ( $('edit-' + celdas[i]['nombre'] + "-" + id).value == "editame" ) {
                if ( confirm("¿Desea cancelar una nueva celda?") ){
                    Element.remove(celdamaestra + "-" + fila);
                    editado=false;
                    fila=0;
                    return;
                }
            }
        }
        
        if (editado) {
            if( ! confirm("Ha editado algún campo, ¿Desea perder los cambios?") ) {
                return false;
            }
        }
        
        editado=false;
        for(i=0;i<celdas.length;i++){
            IEMakeNoEditable(celdas[i]['nombre'] + "-" + id);
        }
        IEOcultarControles("editar-" + id, id);
        fila=0;
        return true;
}

function IEGuardar(id){
        $('#hideshow')[0].style.visibility = 'visible';
        
        if(accion == "" ) {
            accion="guardar";
            var params='accion=guardar';
        }
        else {
            var params='accion='+accion;
        }
        
        for(i=0;i<celdas.length;i++){
            // parsear valor de los checkboxes a 0 o 1
            if ( celdas[i]['tipo'] == "checkbox" ) {
                if ( $("edit-" + celdas[i]['nombre'] + "-" + id).checked ) {
                    $("edit-" + celdas[i]['nombre'] + "-" + id).value="1";
                }
                else {
                    $("edit-" + celdas[i]['nombre'] + "-" + id).value = "0";
                }
            }
            
            params+="&" + celdas[i]['nombre'] + "=" + $("#edit-" + celdas[i]['nombre'] + "-" + id)[0].value;
            newvalue=$("#edit-" + celdas[i]['nombre'] + "-" + id)[0].value
            $(celdas[i]['nombre'] + '-' + fila).innerHTML=newvalue;
        }
        params+='&id=' + id;
        
        
        $.post(
            "/stop/admin/edit",
            params,
            function(data){
                IECompleteAjax(data);
            },
            "html"
            );
        
        /*
        var ajax = new Ajax.Updater(
        {success: 'ajax-message'},
        url_guardar,
        {method: 'post', parameters: params, onFailure: reportError, onComplete: IECompleteAjax});
        */
}

function IEBorrar(id){
        if( ! confirm("¿Realmente desea borrar este registro?") ) {
            return false;
        }
        
        $('#hideshow')[0].style.visibility = 'visible';
        
        accion="borrar";
        var params='accion=borrar';
        for(i=0;i<celdas.length;i++){
            params+="&" + celdas[i]['nombre'] + "=" + $("edit-" + celdas[i]['nombre'] + "-" + id).value;
        }
        params+='&id=' + id;
        
        
        $.post(
            "/stop/admin/edit",
            params,
            function(data){
                IECompleteAjax(data);
            },
            "html"
            );
        /*
        var ajax = new Ajax.Updater(
        {success: 'ajax-message'},
        url_borrar,
        {method: 'post', parameters: params, onFailure: reportError, onComplete: IECompleteAjax});
        */
}
    
function isdefined(variable)
{
return eval('(typeof('+variable+') != "undefined");');
}

                
function IECompleteAjax(response){
        //console.log("IECompleteAjax() response="+response);
        editado=false;
        IEOcultarControles("editar-" + fila, fila);
        
        //console.log("IECompleteAjax() response="+response);
        if (response != "ok") {
            IECancelar(fila);
            alert("Error guardando regla:\n"+response);
        }
        else {
            if(accion == "borrar"){
                //Element.remove(celdamaestra + "-" + fila);
                $("#"+ celdamaestra + "-" + fila).remove();
                $("#"+ celdamaestra + "-" + fila + "-line").remove();
            }
            else {
                // poner valores nuevos en el html
                for(i=0;i<celdas.length;i++){
                    var obj=false;
                    //console.log(celdas[i]['nombre'] + "-" + fila);
                    if ( isdefined(celdas[i]['nombre']) ) {
                        //console.log(eval(celdas[i]['nombre']));
                        obj=eval(celdas[i]['nombre']);
                    }
                    IEMakeNoEditableFromNew(celdas[i]['nombre'] + "-" + fila, obj);
                }
            }
        }
        $('#hideshow')[0].style.visibility = 'hidden';
        
        fila=0;
        accion="";
}

Array.prototype.max = function() {
    var max = this[0];
    var len = this.length;
    for (var i = 1; i < len; i++) if (this[i] > max) max = this[i];
    return max;
}
Array.prototype.min = function() {
    var min = this[0];
    var len = this.length;
    for (var i = 1; i < len; i++) if (this[i] < min) min = this[i];
    return min;
}


