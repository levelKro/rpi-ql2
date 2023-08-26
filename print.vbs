sDataFolder = CreateObject("Scripting.FileSystemObject").GetAbsolutePathName(".") & "\"
sLabelImagePath = sDataFolder & sLabelImage
Set args = Wscript.Arguments
  '*******************************************************************
	'	Print Module
	'   Writted by Mathieu Légaré
	'   Universal template printing module
	'
	'   Note : use var1, var2, var3, etc.. in template for replacement
	'          when you exec command line add each attributes into "
	'          like : print_to_ql.vbs "var1" "var2" "var3" 
	'*******************************************************************
  Sub DoPrint(vars)
		Set ObjDoc = CreateObject("bpac.Document")
		bRet = ObjDoc.Open(vars(0))
		
		Call ObjDoc.SetMediaByName(ObjDoc.Printer.GetMediaName(), True)
		
		If (bRet <> False) Then
			valindex=0
			Dim item
			For Each item In vars
				If valindex <> 0 Then
					itemname = "var" & valindex
					If Mid(item,1,1) = "@" Then
						Call ObjDoc.GetObject(itemname).SetData(0, Mid(item,2), 4)
					Else
						Wscript.Echo  "Replace " & itemname & " by " & item
						ObjDoc.GetObject(itemname).Text = item
					End If
				End If
				valindex = valindex + 1
			Next
			
			Call ObjDoc.SetMediaByName(ObjDoc.Printer.GetMediaName(), True)
			retval=ObjDoc.StartPrint("Label " & vars(0), 0)
			retval=ObjDoc.PrintOut(0, 0)
			ObjDoc.EndPrint
			ObjDoc.Close
		End If
		Set ObjDoc = Nothing
	End Sub
	
	DoPrint(args)