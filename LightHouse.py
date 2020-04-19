#!/usr/bin/env python3

import subprocess
import fileinput
import pwd
import os
import re

import dbus
import notify2
import sys

user = pwd.getpwuid(os.getuid())[0]
path = "/home/" + user + "/.config/"
notify2.init('LightHouse')

# Check if Global Theme exists
# TODO: check presence of the GTKTheme
def checkArgs(plasmaTheme, GTKTheme, wallpaperFilePath, wallpaperFilename):
    # Check PlasmaTheme
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
        # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot find a Global Theme with the given name, check your arguments."])
        n = notify2.Notification("ERROR", "Cannot find a Global Theme with the given name, check your arguments.")
        n.show()
        sys.exit("LightHouse: ERROR: cannot find a Global Theme with the given name, check your arguments.")

    # Check Wallpaper
    found = False
    scandir_iterator = os.scandir(wallpaperFilePath)  # Reinitialize the generator
    for item in scandir_iterator :
        if os.path.isfile(item.path) and item.name == wallpaperFilename:
            found = True
            break
    if not found:
        n = notify2.Notification("ERROR", "Cannot find a wallpaper with the given filename, check your arguments.")
        n.show()
        # subprocess.run(args=["notify-send", "LightHouse", "ERROR: cannot find a wallpaper with the given filename, check your arguments."])
        sys.exit("LightHouse: ERROR: cannot find a wallpaper with the given filename, check your arguments.")
        

# Check if theme is already applied
def checkConfigFiles(path, filename, string, themeName):
    with open(path + filename, "r") as file:
        foundString = re.findall(string + "[A-z \.-]*", str(file.readlines()))[0][:-2]
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
        currentTheme = re.findall(string + "[A-z \.-]*", str(f.readlines()))[0][:-2]
    
    with open(path+filename, "r") as f:
        s = f.read()
        if currentTheme not in s:
            # subprocess.run(args=["notify-send", "LightHouse:", "Error while looking for a previous valid theme in the DE configs file."])
            n = notify2.Notification("ERROR", "Cannot find a valid theme entry in the DE config file.")
            n.show()
            return
    # Safely write the changed content, if found in the file
    with open(path+filename, 'w') as f:
        s = s.replace(currentTheme, string+stringToAdd)
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
    updateFile(path, "kdeglobals", "LookAndFeelPackage=", plasmaTheme)


# Setting GTK Theme
def setGTKTheme():
    gtk_path = path+"gtk-3.0/"
    updateFile(gtk_path, "settings.ini", "gtk-theme-name=", GTKTheme)


# Setting the Wallpaper
def setWallpaper(filepath, plugin = 'org.kde.image'):
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
    plasma.evaluateScript(jscript % (plugin, plugin, filepath))


# Setting the Konsole profile
def setKonsole():
    filename = "/konsolerc"
    updateFile(path, filename, "DefaultProfile=", plasmaTheme+".profile")


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



if __name__ == '__main__':
    if (len(sys.argv) != 4):
        # subprocess.run(args=["notify-send", "LightHouse", "ERROR: Cannot start! Have you specified the correct arguments?"])
        n = notify2.Notification("ERROR", "Cannot start LightHouse! Have you specified the correct arguments?")
        n.show()
        sys.exit("ERROR! Usage: python3 LightHouse.py <PLASMA_THEME_NAME> <GTK_THEME> <WALLPAPER_FILENAME>")
        # sys.exit(1)
    else:
        
        plasmaTheme = sys.argv[1]   # "Aritim-Dark_DEV"
        GTKTheme = sys.argv[2]  # "Aritim-Dark-GTK"

        # CHANGE here the path where your wallpapers are located
        wallpaperFilePath = "/home/"+user+"/Pictures/Wallpapers/"+plasmaTheme+"/"
        wallpaperFilename = sys.argv[3]  # "dunes_NIGHT.jpg"

        checkArgs(plasmaTheme, GTKTheme, wallpaperFilePath, wallpaperFilename)

        if (checkConfigFiles(path, "kdeglobals", "LookAndFeelPackage=", plasmaTheme)):
            # Next notification is disabled as can be too distracting, especially if cron launches the script quite often
            # subprocess.run("notify-send \"LightHouse\" \"There is nothig to do, exiting...\"", shell=True)
            # n = notify2.Notification("ERROR", "There is nothig to do, exiting...")
            # n.show()
            sys.exit()
        else:    
            setPlasmaGlobalTheme()
            setGTKTheme()
            setWallpaper(wallpaperFilePath + wallpaperFilename, "org.kde.image")
            setKonsole()

            # rstPlasmashell()

