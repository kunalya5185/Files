Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "pythonw.exe """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\fileserver.py""", 0, False
Set WshShell = Nothing
