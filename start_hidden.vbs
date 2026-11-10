Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = currentDir & "\run_loop.bat"

' Run hidden with window style 0 and do not wait
WshShell.CurrentDirectory = currentDir
WshShell.Run """" & batPath & """", 0, False
