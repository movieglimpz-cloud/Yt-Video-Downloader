Set oShell = CreateObject("WScript.Shell")
' Get the directory of the current script
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Run the python server using pythonw (no window)
' We also use taskkill first to make sure no other instance is running
oShell.Run "taskkill /F /IM pythonw.exe /T", 0, True
oShell.Run "pythonw """ & strPath & "\server.py""", 0, False
