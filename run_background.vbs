Set oShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory of the current script
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

strPythonW = "pythonw"
strFallback = oShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\AppData\Local\Programs\Python\Python311\pythonw.exe"

If fso.FileExists(strFallback) Then
    strPythonW = """" & strFallback & """"
End If

' We also use taskkill first to make sure no other instance is running
oShell.Run "taskkill /F /IM pythonw.exe /T", 0, True

On Error Resume Next
oShell.Run strPythonW & " """ & strPath & "\server.py""", 0, False
If Err.Number <> 0 Then
    MsgBox "Python not found. Please run install.bat to set up YT Downloader.", 16, "YT Downloader Error"
End If
On Error GoTo 0
