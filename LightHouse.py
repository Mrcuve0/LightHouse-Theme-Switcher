#!/usr/bin/env python3

import subprocess
import fileinput
import getopt
import pwd
import os
import re

import dbus
import notify2
import sys

#   _    _  _____ ______ _____   __      __     _____   _____ 
#  | |  | |/ ____|  ____|  __ \  \ \    / /\   |  __ \ / ____|
#  | |  | | (___ | |__  | |__) |  \ \  / /  \  | |__) | (___  
#  | |  | |\___ \|  __| |  _  /    \ \/ / /\ \ |  _  / \___ \ 
#  | |__| |____) | |____| | \ \     \  / ____ \| | \ \ ____) |
#   \____/|_____/|______|_|  \_\     \/_/    \_\_|  \_\_____/ 
#                                                             
#                                                             

user = pwd.getpwuid(os.getuid())[0]
configPath = "/home/" + user + "/.config/"
localPath = "/home/" + user + "/.local/"
firefoxPath = "/home/" + user + "/.mozilla/firefox/"
firefoxProfileFolder = "5x01oqmi.default" + "/"     # <-- Change your profile folder here!
vsCodePath = "/home/" + user + "/.config/Code/User/"

notify2.init('LightHouse')

#   _____  ______ ______   
#  |  __ \|  ____|  ____|  
#  | |  | | |__  | |__ ___ 
#  | |  | |  __| |  __/ __|
#  | |__| | |____| |  \__ \
#  |_____/|______|_|  |___/
#                          
#                          

# Check if Global Theme exists
# TODO: check presence of the GTKTheme
def checkArgs(plasmaTheme, GTKTheme, wallpaper, konsoleTheme):
    # Check PlasmaTheme
    if (plasmaTheme != None):
        try:
            res = subprocess.run(args=["lookandfeeltool", "-l"], text=True, capture_output=True)
            res = res.stdout.split("\n")
        except subprocess.CalledProcessError as e:
            return_code = e.returncode
            # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot check Global Theme presence, is lookandfeeltool installed?"])
            n = notify2.Notification("ERROR", "Cannot check Global Theme presence, is lookandfeeltool installed?")
            n.show()
            sys.exit("LightHouse: ERROR: cannot check Global Theme presence, is lookandfeeltool installed?")
        if plasmaTheme not in res:
            # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot find a Global Theme with the given name, check the arguments."])
            n = notify2.Notification(f"ERROR", f"Cannot find a Global Theme with the given name, check the arguments. [theme_arg = {plasmaTheme} | res = {res}]")
            n.show()
            sys.exit(f"LightHouse: ERROR: cannot find a Global Theme with the given name, check the arguments. [theme_arg = {plasmaTheme}]")
    else:
        # No PlasmaTheme Provided
        pass

    # Check Wallpaper
    if (wallpaper != None):
        found = False

        ## Separate path and filename
        path, filename = os.path.split(wallpaper)

        scandir_iterator = os.scandir(path)  # Reinitialize the generator
        for item in scandir_iterator :
            if os.path.isfile(item.path) and item.name == filename:
                found = True
                break
        if not found:
            n = notify2.Notification("ERROR", "Cannot find a wallpaper with the given filename, check the arguments.")
            n.show()
            # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot find a wallpaper with the given filename, check the arguments."])
            sys.exit("LightHouse: ERROR: cannot find a wallpaper with the given filename, check the arguments.")
    else:
        # No Wallpaper provided
        pass

    # Check Konsole Profile
    if (konsoleTheme != None):
        found = False
        scandir_iterator = os.scandir(localPath+"share/konsole/")  # Reinitialize the generator
        for item in scandir_iterator :
            if os.path.isfile(item.path) and item.name == konsoleTheme+".profile":
                found = True
                break
        if not found:
            n = notify2.Notification("ERROR", "Cannot find a Konsole profile with the given profile name, check the arguments.")
            n.show()
            # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot find a wallpaper with the given filename, check the arguments."])
            sys.exit("LightHouse: ERROR: cannot find a Konsole profile with the given profile name, check the arguments.")
    else:
        # No Konsole Theme provided
        pass


# Check if theme is already applied
def checkConfigFiles(path, filename, string, themeName):
    with open(path + filename, "r") as file:
        foundString = re.findall(string + "[A-z 0-9 \.\-\,=:_]*", str(file.readlines()))[0]
        #[:-2]
        foundString = str.replace(foundString, "\n", "")
        foundString = str.replace(foundString, "\\n","")
        if (foundString == string + themeName):
            # The theme has been already applied correctly
            file.close()
            return True
        else:
            # Continue updating with the new theme
            file.close()
            return False


# Update config file
def updateFile(path, filename, string, stringToAdd):
    with open(path+filename, "r") as f:
        # [A-z \.-]*
        # [A-z \.\-0-9);]*

        # currentTheme contains the entire line found in the file, to be modified
        currentTheme = re.findall(string + "[A-z \.,\-0-9();\"β]*", str(f.readlines()))[0][:-2]
    
    with open(path+filename, "r") as f:
        s = f.read()
        if currentTheme not in s:
            # subprocess.run(args=["notify-send", "LightHouse:", "Error while looking for a previous valid theme in the DE configs file."])
            n = notify2.Notification("ERROR", "Cannot find a valid theme entry in the DE config file.")
            n.show()
            return -1

    # Safely write the changed content, if found in the file
    with open(path+filename, 'w') as f:
        # Let's define the new line that will entirely substitute currentTheme
        s = s.replace(currentTheme, string.replace("\\", "") +stringToAdd)
        f.write(s)


# Setting Plasma Theme
def setPlasmaGlobalTheme():
    try:
        res = subprocess.run(args=["lookandfeeltool", "--apply", plasmaTheme], text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot apply Global Theme, is lookandfeeltool installed?"])
        n = notify2.Notification("ERROR", "Cannot apply Global Theme, is lookandfeeltool installed?")
        n.show()
        sys.exit("LightHouse: ERROR: cannot apply Global Theme, is lookandfeeltool installed?")
    
    # Update "kdeglobals" file
    # Ex: LookAndFeelPackage=Aritim-Dark_DEV
    if (updateFile(configPath, "kdeglobals", "LookAndFeelPackage=", plasmaTheme) == -1):
        n = notify2.Notification("ERROR", "Something has gone wrong when setting the Plasma Global theme...")
        n.show()


# Setting GTK Theme
def setGTKTheme(GTKTheme):
    GTKTheme_lower = GTKTheme.lower()
    nameComponents = GTKTheme_lower.split("-")

    for version in ["3.0", "4.0"]:
        # Set Theme
        gtk_path = configPath + f"gtk-{version}/"
        if (updateFile(gtk_path, "settings.ini", "gtk-theme-name=", GTKTheme) == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting the GTK theme...")
            n.show()
        # Set theme preference
        if ("dark" in nameComponents):
            if (updateFile(gtk_path, "settings.ini", "gtk-application-prefer-dark-theme=", "true") == -1):
                n = notify2.Notification("ERROR", "Something has gone wrong when setting the \"prefer-dark-theme\"...")
                n.show()
        elif ("light" in nameComponents):
            if (updateFile(gtk_path, "settings.ini", "gtk-application-prefer-dark-theme=", "false") == -1):
                n = notify2.Notification("ERROR", "Something has gone wrong when setting the \"prefer-dark-theme\"...")
                n.show()
    # FIXME: Does not work 
    # try:
    #     res = subprocess.run(args=["/usr/bin/gsettings", " set", " org.gnome.desktop.interface", " gtk-theme", GTKTheme], text=True, capture_output=True)
    # except subprocess.CalledProcessError as e:
    #     return_code = e.returncode
    #     n = notify2.Notification("ERROR", "Something has gone wrong when setting the \"gtk-theme\"...")
    #     n.show()
    #     sys.exit("ERROR", "Something has gone wrong when setting the \"gtk-theme\"...")


# Setting the Wallpaper
def setWallpaper(wallpaper, plugin = 'org.kde.image'):
    jscript = """
    var allDesktops = desktops();
    print (allDesktops);
    for (i=0;i<allDesktops.length;i++) {
        d = allDesktops[i];
        d.wallpaperPlugin = "%s";
        d.currentConfigGroup = Array("Wallpaper", "%s", "General");
        d.writeConfig("Image", "file://%s")
    }
    """
    bus = dbus.SessionBus()
    plasma = dbus.Interface(bus.get_object('org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
    plasma.evaluateScript(jscript % (plugin, plugin, wallpaper))


# Setting the Konsole profile
def setKonsole(konsoleTheme):
    filename = "/konsolerc"
    if (updateFile(configPath, filename, "DefaultProfile=", konsoleTheme + ".profile") == -1):
        n = notify2.Notification("ERROR", "Something has gone wrong when setting the Konsole profile...")
        n.show()


# Setting the Firefox theme preference (will be used by websites w/ dark mode (Twitter, Youtube,
# GitHub etc...))
def setFirefox(firefoxTheme):
    # user_pref(\"ui.systemUsesDarkTheme\", 1);
    filename = "prefs.js"
    if (str.lower(firefoxTheme) == "dark"):
        if (updateFile(firefoxPath+firefoxProfileFolder, filename, "user_pref\(\"ui.systemUsesDarkTheme\",", " 1);") == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting the Firefox profile...")
            n.show()
    elif (str.lower(firefoxTheme) == "light"):
        if (updateFile(firefoxPath+firefoxProfileFolder, filename, "user_pref\(\"ui.systemUsesDarkTheme\",", " 0);") == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting the Firefox profile...")
            n.show()
    else:
        n = notify2.Notification("ERROR", "Firefox profile error: please set either \"dark\" or \"light\"...")
        n.show()


def setVSCode(vscodeTheme):
    # "workbench.colorTheme": "GitHub Plus",
    filename = "settings.json"
    if (updateFile(vsCodePath, filename, "\"workbench.colorTheme\":", " \""+vscodeTheme+"\",") == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting VSCode theme...")
            n.show()
    if (checkConfigFiles(vsCodePath, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") is True):
        # n = notify2.Notification("1 --> 0")
        # n.show()
        if (updateFile(vsCodePath, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(0)},") == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting VSCode PDF_preview theme...")
            n.show()
    else:
        # n = notify2.Notification("0 --> 1")
        # n.show()
        if (updateFile(vsCodePath, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") == -1):
            n = notify2.Notification("ERROR", "Something has gone wrong when setting VSCode PDF_preview theme...")
            n.show()


# Resetting Plasmashell to solve icon issues
def rstPlasmashell():
    try:
        res = subprocess.run(args=["plasmashell", "--replace > ", "/dev/null", "2>&1", "&&", "sleep 5 &"], text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        # subprocess.run(args=["notify-send", "LightHouse", "CRITICAL ERROR: cannot restart plasmashell, WTF?"])
        n = notify2.Notification("CRITICAL ERROR", "Cannot restart plasmashell, WTF?")
        n.show()
        sys.exit("LightHouse: CRITICAL ERROR: cannot restart plasmashell, WTF?") 


#   __  __          _____ _   _ 
#  |  \/  |   /\   |_   _| \ | |
#  | \  / |  /  \    | | |  \| |
#  | |\/| | / /\ \   | | | . ` |
#  | |  | |/ ____ \ _| |_| |\  |
#  |_|  |_/_/    \_\_____|_| \_|
#                               
#                               

if __name__ == '__main__':

    plasmaTheme = None
    GTKTheme = None
    wallpaper = None
    konsoleTheme = None
    firefoxTheme = None
    vsCodeTheme = None

    shortOpts = "hp:g:w:k:f:c:"
    longOpts = ["help", "plasma=", "gtk=", "wallpaper=", "konsole=", "firefox=", "vscode="]
    argList = sys.argv[1:]

    try:
        args, vals = getopt.getopt(argList, shortOpts, longOpts);
    except getopt.error as err:
        n = notify2.Notification("ERROR", "Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
        n.show()
        print("--- LightHouse Help Page ---")
        print("")
        print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
        print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
        print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply GTKTheme")
        print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
        print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
        print("\t-f=,\t--firefox = FIREFOX_THEME:\t\tApply Firefox Theme Preference")
        print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
        print("")
        print("--- LightHouse Help Page ---")
        sys.exit()

    # Evaluate given options
    for currArg, currVal in args:
        if currArg in ("-h", "--help"):
            n = notify2.Notification("LightHouse Help", "Visit https://bit.ly/32UK20A or launch the script from terminal for full help/man page")
            n.show()
            print("--- LightHouse Help Page ---")
            print("")
            print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
            print("\t-p,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
            print("\t-g,\t--gtk = GTK_THEME:\t\t\tApply GTKTheme")
            print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
            print("\t-k,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
            print("\t-f=,\t--firefox = FIREFOX_THEME:\t\tApply Firefox Theme Preference")
            print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
            print("")
            print("--- LightHouse Help Page ---")
            sys.exit()
        elif currArg in ("-p", "--plasma"):
            plasmaTheme = currVal
        elif currArg in ("-g", "--gtk"):
            GTKTheme = currVal
        elif currArg in ("-w", "--wallpaper"):
            wallpaper = currVal
        elif currArg in ("-k", "--konsole"):
            konsoleTheme = currVal
        elif currArg in ("-f", "--firefox"):
            firefoxTheme = currVal
        elif currArg in ("-c", "--vscode"):
            vsCodeTheme = currVal
        else:
            pass
    if len(args) == 0:
            n = notify2.Notification("ERROR", "Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
            n.show()
            print("--- LightHouse Help Page ---")
            print("")
            print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
            print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
            print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply GTKTheme")
            print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
            print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
            print("\t-f=,\t--firefox = FIREFOX_THEME:\t\tApply Firefox Theme Preference")
            print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
            print("")
            print("--- LightHouse Help Page ---")
            print("")
            sys.exit("ERROR! No arguments specified!")

    checkArgs(plasmaTheme, GTKTheme, wallpaper, konsoleTheme)

    if (plasmaTheme != None and checkConfigFiles(configPath, "kdeglobals", "LookAndFeelPackage=", plasmaTheme)):
        # Next notification is disabled as can be too distracting, especially if cron launches the script quite often
        # subprocess.run("notify-send \"LightHouse\" \"There is nothig to do, exiting...\"", shell=True)
        # n = notify2.Notification("ERROR", "There is nothig to do, exiting...")
        # n.show()
        sys.exit("LightHouse: There is nothig to do, exiting...")
    else:
        if (plasmaTheme != None):
            setPlasmaGlobalTheme()
        if (GTKTheme != None):
            setGTKTheme(GTKTheme)
        if (wallpaper != None):
            setWallpaper(wallpaper, "org.kde.image")
        if (konsoleTheme != None):
            setKonsole(konsoleTheme)
        # if (firefoxTheme != None):
            # setFirefox(firefoxTheme)
        if (vsCodeTheme != None):
            setVSCode(vsCodeTheme)

        # rstPlasmashell()

