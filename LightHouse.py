#!/usr/bin/env python3

import subprocess
import fileinput
import pwd
import os
import re

import dbus
import sys

user = pwd.getpwuid(os.getuid())[0]
path = "/home/" + user + "/.config/"

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
            subprocess.run("notify-send \"Aurora Theme Switcher\" \"Error while looking for a previous valid theme in the DE configs file.")
            return
    # Safely write the changed content, if found in the file
    with open(path+filename, 'w') as f:
        s = s.replace(currentTheme, string+stringToAdd)
        f.write(s)


# Setting Plasma Theme
def plasmaGlobalThemeSet():
    subprocess.run("lookandfeeltool --apply " + plasmaTheme, shell=True)
    # Update "kdeglobals" file
    # Ex: LookAndFeelPackage=Aritim-Dark_DEV
    updateFile(path, "kdeglobals", "LookAndFeelPackage=", plasmaTheme)


# Setting GTK Theme
def GTKThemeSet():
    gtk_path = path+"gtk-3.0/"
    updateFile(gtk_path, "settings.ini", "gtk-theme-name=", GTKTheme)


# Setting the Wallpaper
def wallpaperSet(filepath, plugin = 'org.kde.image'):
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


def konsoleSet():
    filename = "/konsolerc"
    updateFile(path, filename, "DefaultProfile=", plasmaTheme+".profile")


def rstPlasmashell():
    subprocess.run("plasmashell --replace > /dev/null 2>&1 && sleep 5 & ", shell=True)



if __name__ == '__main__':

    if (len(sys.argv) != 4):
        subprocess.run("notify-send \"LightHouse\" \"Cannot start! Have you specified the correct arguments?\"", shell=True)
        sys.exit("ERROR! Usage: python3 LightHouse.py <PLASMA_THEME_NAME> <GTK_THEME> <WALLPAPER_FILENAME>")
        # sys.exit(1)
    else:
        plasmaTheme = sys.argv[1]   # "Aritim-Dark_DEV"
        GTKTheme = sys.argv[2]      # "Aritim-Dark-GTK"
        
        # CHANGE here the path where your wallpapers are located
        wallpaperFilePath = "/home/"+user+"/Pictures/Wallpapers/"+plasmaTheme+"/"
        wallpaperFilename = sys.argv[3]  # "dunes_NIGHT.jpg"

        if (checkConfigFiles(path, "kdeglobals", "LookAndFeelPackage=", plasmaTheme)):
            subprocess.run("notify-send \"LightHouse\" \"There is nothig to do, exiting...\"", shell=True)
            sys.exit()
        else:    
            plasmaGlobalThemeSet()
            GTKThemeSet()
            wallpaperSet(wallpaperFilePath + wallpaperFilename, "org.kde.image")
            konsoleSet()

            # rstPlasmashell()

