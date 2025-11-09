Option Explicit
Dim WShell, FSO, TempFolder, HTAPath, HTAContent
Dim MsgText, TextColor, BGColor, FontType, FontSize, ImageURL, ImageWidth, ImageHeight

' === CONFIGURATION ===
MsgText     = "Who Is This Black Boy ? Isn't He Asit Diwedi ? Am I Right  Aniket, Kartik, Adyant and Deeeeeeptanshu Shukla ?"       ' Text to display
TextColor   = "Black"                           ' Text color
BGColor     = "White"                         ' Background color
FontType    = "Segoe UI"                        ' Font family
FontSize    = "64px"                            ' Font size

ImageURL    = "https://raw.githubusercontent.com/rohan6379/Server/refs/heads/main/Diwedi.jpg"  ' Leave "" for no image
ImageWidth  = "300px"                           ' Image width
ImageHeight = "auto"                            ' Image height (use "auto" to keep proportions)
' ======================

Set WShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

TempFolder = FSO.GetSpecialFolder(2)
HTAPath = TempFolder & "\CustomGreeting.hta"

Dim ImageHTML
If ImageURL <> "" Then
    ImageHTML = "<img src='" & ImageURL & "' width='" & ImageWidth & "' height='" & ImageHeight & "' style='display:block; margin:0 auto 20px auto;' />"
Else
    ImageHTML = ""
End If

HTAContent = "<html>" & vbCrLf & _
"<head>" & vbCrLf & _
"<hta:application id='Greeting' applicationname='Greeting' border='none' caption='no' showintaskbar='no' singleinstance='yes' windowstate='maximize' scroll='no' />" & vbCrLf & _
"<title>Greeting</title>" & vbCrLf & _
"<script language='VBScript'>" & vbCrLf & _
"Sub Window_OnLoad()" & vbCrLf & _
"    window.resizeTo screen.availWidth, screen.availHeight" & vbCrLf & _
"    window.moveTo 0, 0" & vbCrLf & _
"End Sub" & vbCrLf & _
"Sub CloseWindow()" & vbCrLf & _
"    window.close" & vbCrLf & _
"End Sub" & vbCrLf & _
"</script>" & vbCrLf & _
"</head>" & vbCrLf & _
"<body style='margin:0; padding:0; height:100vh; width:100vw; background-color:" & BGColor & "; display:flex; align-items:center; justify-content:center; font-family:" & FontType & "; flex-direction:column;' onclick='CloseWindow' onkeypress='CloseWindow'>" & vbCrLf & _
"    <div style='text-align:center;'>" & vbCrLf & _
"        " & ImageHTML & vbCrLf & _
"        <div style='color:" & TextColor & "; font-size:" & FontSize & ";'>" & MsgText & "</div>" & vbCrLf & _
"    </div>" & vbCrLf & _
"</body>" & vbCrLf & _
"</html>"

With FSO.CreateTextFile(HTAPath, True)
    .Write HTAContent
    .Close
End With

WShell.Run "mshta.exe """ & HTAPath & """", 1, True

If FSO.FileExists(HTAPath) Then
    FSO.DeleteFile HTAPath
End If

Set WShell = Nothing
Set FSO = Nothing
