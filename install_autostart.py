import os
import sys
import subprocess

def install_autostart():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vbs_path = os.path.join(base_dir, "start_hidden.vbs")
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("[-] APPDATA environment variable not found.")
        return False
        
    startup_dir = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_dir, "ZeblaskiOfficialBot.lnk")
    
    # PowerShell command to create shortcut cleanly
    ps_cmd = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut_path}')
$s.TargetPath = 'wscript.exe'
$s.Arguments = '\"{vbs_path}\"'
$s.WorkingDirectory = '{base_dir}'
$s.Description = 'Zeblaski Official Bot 24/7 Background Runner'
$s.Save()
"""
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
        print(f"[+] Successfully installed to Windows Startup:")
        print(f"    {shortcut_path}")
    except Exception as e:
        print(f"[-] Failed to create shortcut: {e}")
        return False
        
    # Start the bot right now via wscript
    try:
        subprocess.Popen(["wscript.exe", vbs_path], cwd=base_dir)
        print(f"[+] Bot has been launched in the background!")
        print(f"[+] It will now run 24/7 and automatically start every time Windows turns on.")
        return True
    except Exception as e:
        print(f"[-] Failed to launch bot: {e}")
        return False

if __name__ == "__main__":
    install_autostart()
