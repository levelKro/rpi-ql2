function printerAPI(id) {
	
	if(document.getElementById("templateOutCopie").value>=1){
		copie=document.getElementById("templateOutCopie").value;
	}
	else{
		copie=1;
	}
	var params="-f "+document.getElementById("templatesList").value+" -c "+copie+" -v '";
	for( var i=0; i<document.getElementById("templateForm").elements.length; i++ ){
		var fieldName = document.getElementById("templateForm").elements[i].name;
		var fieldValue = document.getElementById("templateForm").elements[i].value;
		if(fieldName!=""){
			params += fieldName + '="' + fieldValue + '";';
		}
	}	
	params += "'";
	/*
	for( var i=0; i<document.getElementById("printerForm").elements.length; i++ )
	{
	   var fieldName = document.getElementById("printerForm").elements[i].name;
	   var fieldValue = document.getElementById("printerForm").elements[i].value;

	   params += fieldName + '=' + fieldValue + '&';
	}	
	if (action == "expire") {
		ed=document.getElementById("dateoutday").value();
		em=document.getElementById("dateoutmonth").value().split(" ")[0];
		ey=document.getElementById("dateoutyear").value();
		pd=document.getElementById("dateinday").value().split(" ")[0];
		pm=document.getElementById("dateinmonth").value();
		py=document.getElementById("dateinyear").value();
		params+="packed="+pd+"-"+pm+"-"+py;
		if (document.getElementById("expireVisible").checked()) {
			params+="&expired="+ed+"-"+em+"-"+ey;
		}
	}
	*/
	if (window.XMLHttpRequest) { printerAPICall=new XMLHttpRequest(); }
	else { printerAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	printerAPICall.onreadystatechange=function() {
		if (printerAPICall.readyState==4 && printerAPICall.status==200) {
			var result=printerAPICall.responseText;		
			var values=JSON.parse(result);	
			if(values.result=="success"){	
				document.getElementById("templateOutputForm").innerText=values.reason;
			}
			else{
				document.getElementById("templateOutputForm").innerText=values.reason;
			}
		}
	}
	printerAPICall.open("POST","/print/cli?r="+Math.random(),true);
	printerAPICall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	printerAPICall.send("data="+params);	
	return false;
}
function manageAPI(id,action) {
	var params="";
	if (action == "config/save") {
		for( var i=0; i<document.getElementById("configForm").elements.length; i++ )
		{
		   var fieldName = document.getElementById("configForm").elements[i].name;
		   var fieldValue = document.getElementById("configForm").elements[i].value;
		   params += fieldName + '=' + fieldValue + '&';
		}	
	}
	for( var i=0; i<document.getElementById("manageForm").elements.length; i++ )
	{
	   var fieldName = document.getElementById("manageForm").elements[i].name;
	   var fieldValue = document.getElementById("manageForm").elements[i].value;
	   params += fieldName + '=' + fieldValue + '&';
	}	
	if (window.XMLHttpRequest) { manageAPICall=new XMLHttpRequest(); }
	else { manageAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	manageAPICall.onreadystatechange=function() {
		if (manageAPICall.readyState==4 && manageAPICall.status==200) {
			var result=manageAPICall.responseText;		
			var values=JSON.parse(result);	
			if(values.result=="success"){	
				document.getElementById("manageOutput").innerText=values.reason;
				if(values.datas) {
					document.getElementById("configModel").value=values.datas['printer']['model'];
					document.getElementById("configUSB").value=values.datas['printer']['usb'];
					document.getElementById("configSerial").value=values.datas['printer']['serial'];
				}
			}
			else{
				document.getElementById("manageOutput").innerText=values.reason;
			}
		}
	}
	document.getElementById("manageOutput").innerText="Request the action to system..."
	manageAPICall.open("POST","/manage/"+action+"?r="+Math.random(),true);
	manageAPICall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	manageAPICall.send(params);	
	if (action=="update") {
		setTimeout("updateAPI('updateOutput')",2000);
	}
	return false;
}
function loadImages(id) {
	if (window.XMLHttpRequest) { loadImagesAPICall=new XMLHttpRequest(); }
	else { loadImagesAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	loadImagesAPICall.onreadystatechange=function() {
		if (loadImagesAPICall.readyState==4 && loadImagesAPICall.status==200) {
			var result=loadImagesAPICall.responseText;	
			var values=JSON.parse(result);	
			document.getElementById(id).innerHTML="";
			for (var i=0; i<values.images.length; i++){
				document.getElementById(id).innerHTML+='<option value="images/'+values.images[i]+'">'+values.images[i]+'</option>';
			}
		}
	}
	loadImagesAPICall.open("GET","/api/images?r="+Math.random(),true);
	loadImagesAPICall.send();	
	return false;
}
function changeImage(imglist,imgview) {
	document.getElementById(imgview).src=document.getElementById(imglist).value.replace("images/","api/image/");
}
function loadTemplates(id) {
	if (window.XMLHttpRequest) { loadTemplatesAPICall=new XMLHttpRequest(); }
	else { loadTemplatesAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	loadTemplatesAPICall.onreadystatechange=function() {
		if (loadTemplatesAPICall.readyState==4 && loadTemplatesAPICall.status==200) {
			var result=loadTemplatesAPICall.responseText;	
			var values=JSON.parse(result);	
			document.getElementById(id).innerHTML="<option>- Sélectionner un template -</option>";
			for (var i=0; i<values.templates.length; i++){
				document.getElementById(id).innerHTML+='<option value="'+values.templates[i]+'">'+values.templates[i].replace(".rpiql","")+'</option>';
			}
		}
	}
	loadTemplatesAPICall.open("GET","/api/templates?r="+Math.random(),true);
	loadTemplatesAPICall.send();	
	return false;
}
function changeTemplate(id) {
	document.getElementById("templateFormPrint").disabled=true;
	if (window.XMLHttpRequest) { loadTemplateAPICall=new XMLHttpRequest(); }
	else { loadTemplateAPICall=new ActiveXObject("Microsoft.XMLHTTP"); }
	loadTemplateAPICall.onreadystatechange=function() {
		if (loadTemplateAPICall.readyState==4 && loadTemplateAPICall.status==200) {
			var result=loadTemplateAPICall.responseText;	
			var values=JSON.parse(result);	
			document.getElementById(id).innerHTML='<table width="100%">'+
			'	<tr>'+
			'		<td rowspan="2" class="left"><h3>'+values.datas["paper"]["name"]+'</h3><p>'+values.datas["paper"]["desc"]+'</p></td>'+
			'		<th class="right">Dimension:</th><td class="left">'+values.datas["paper"]["width"]+'x'+values.datas["paper"]["height"]+'px</td>'+			
			'	</tr><tr>'+
			'		<th class="right">Rotate:</th><td class="left">'+values.datas["paper"]["rotate"]+'</td>'+			
			'	</tr>'+
			'</table><hr/>';
			for (const [key, value] of Object.entries(values.datas)) {
				out='';
				if( key != "paper" ){
					if(value.edit=="1"){
						out+='<table width="100%"><tr>';
						if(value.type == "text"){
							out+='<th rowspan="3" class="left">'+key+' (texte):</th><td rowspan="3" class="left"><input name="'+key+'" type="text" value="'+value.value+'"/>'+
							'<th class="right" width="10%">Aligment:</th><td class="left" width="10%">'+value.align+'</td>'+
							'<th class="right" width="10%">Overflow:</th><td class="left" width="10%">'+value.overflow+'</td>';
						}
						else if(value.type == "image"){
							out+='<th rowspan="3" class="left">'+key+' (texte):</th><td rowspan="3" class="left"><select id="imagesList_'+key+'" name="'+key+'" onchange="changeImage(\'imagesList_'+key+'\',\'imagesPreview_'+key+'\')"><option>Chargement...</option></select></td>'+
							'<td class="Left"><img src="" class="imagesPreview" id="imagesPreview_'+key+'"/></td>';
							setTimeout('loadImages("imagesList_'+key+'")',1000);
						}
						else if(value.type == "barcode"){
							out+='<th rowspan="3" class="left">Code :</th><td rowspan="3" class="left"><input name="'+key+'" type="text" value="'+value.value+'"/>';
						}
						out+='</tr><tr>';
						if(value.params!=""){
							out+='<th class="right" width="10%">Paramètre(s):</th><td class="left" width="10%" colspan="3">'+value.params+'</td></tr><tr>';
						}
						out+='<th class="right" width="10%">Position:</th><td class="left" width="10%">'+value.posx+'x'+value.posy+'px</td>'+
						'<th class="right" width="10%">Dimension:</th><td class="left" width="10%">'+value.width+'x'+value.height+'px</td>';
						document.getElementById(id).innerHTML+=out+'</tr></table><hr/>';
					}
					document.getElementById("templateFormPrint").disabled=false;
				}		
			}
			
		}
	}
	loadTemplateAPICall.open("GET","/api/template/"+document.getElementById("templatesList").value.replace(".rpiql","")+"?r="+Math.random(),true);
	loadTemplateAPICall.send();	
	return false;
}