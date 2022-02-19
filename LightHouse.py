#!/usr/bin/env python3

import os
import re
import sys
import pwd
import getopt
import logging
from logging import config
from logging_conf import LOGGING

# TODO: Investigate issues with dbus and notify2
# As for now, such dependencies are circumvented using subprocess
# import notify2
import subprocess


# Load the logging configuration
config.dictConfig(LOGGING)
logger = logging.getLogger("LightHouse")
logger.propagate = False


#   _    _  _____ ______ _____   __      __     _____   _____ 
#  | |  | |/ ____|  ____|  __ \  \ \    / /\   |  __ \ / ____|
#  | |  | | (___ | |__  | |__) |  \ \  / /  \  | |__) | (___  
#  | |  | |\___ \|  __| |  _  /    \ \/ / /\ \ |  _  / \___ \ 
#  | |__| |____) | |____| | \ \     \  / ____ \| | \ \ ____) |
#   \____/|_____/|______|_|  \_\     \/_/    \_\_|  \_\_____/ 
#                                                             


user = pwd.getpwuid(os.getuid())[0]
config_path = "/home/" + user + "/.config/"
localPath = "/home/" + user + "/.local/"
vscode_path = "/home/" + user + "/.config/Code/User/"

# notify2.init('LightHouse')


#   _____  ______ ______   
#  |  __ \|  ____|  ____|  
#  | |  | | |__  | |__ ___ 
#  | |  | |  __| |  __/ __|
#  | |__| | |____| |  \__ \
#  |_____/|______|_|  |___/
#                          

def dbus_notifier(
        app_name: str,
        replaces_id: int,
        app_icon: str,
        summary: str,
        body: str,
        actions: list,
        hints: list,
        timeout: int,
    ) -> None:
    pass


# Check if Global Theme exists
# TODO: check presence of the gtk_theme
def check_args(
        plasma_theme: str,
        gtk_theme: str,
        wallpaper: str,
        konsole_profile: str,
    ) -> None:

    # Check plasma_theme
    if plasma_theme:
        try:
            res = subprocess.run(args=["lookandfeeltool", "-l"], text=True, capture_output=True)
            res = res.stdout.split("\n")
            logger.debug(f"lookandfeeltool output: {res}")
        except subprocess.CalledProcessError:
            logger.error("Cannot check Global Theme presence, is lookandfeeltool installed?")
            # n = notify2.Notification("ERROR", "Cannot check Global Theme presence, is lookandfeeltool installed?")
            # n.show()
            sys.exit("")
        if plasma_theme not in res:
            logger.error(f"Cannot find a Global Theme with the given name, check the arguments: theme_arg: {plasma_theme}, res: {res}]")
            # n = notify2.Notification(f"ERROR", f"Cannot find a Global Theme with the given name, check the arguments. [theme_arg = {plasma_theme} | res = {res}]")
            # n.show()
            sys.exit()
    else:
        # No plasma_theme Provided
        pass

    # Check GTK Theme
    # TODO

    # Check Wallpaper
    if wallpaper:
        found = False
        ## Separate path and filename
        path, filename = os.path.split(wallpaper)

        scandir_iterator = os.scandir(path)  # Reinitialize the generator
        for item in scandir_iterator :
            if os.path.isfile(item.path) and item.name == filename:
                found = True
                break
        if not found:
            logger.error(f"Cannot find a wallpaper with the given filename, check the arguments.")
            # n = notify2.Notification("ERROR", "Cannot find a wallpaper with the given filename, check the arguments.")
            # n.show()
            sys.exit()
    else:
        # No Wallpaper provided
        pass

    # Check Konsole Profile
    if konsole_profile:
        found = False
        scandir_iterator = os.scandir(localPath+"share/konsole/")  # Reinitialize the generator
        for item in scandir_iterator :
            if os.path.isfile(item.path) and item.name == konsole_profile+".profile":
                found = True
                break
        if not found:
            logger.error(f"Cannot find a Konsole profile with the given profile name, check the arguments.")
            # n = notify2.Notification("ERROR", "Cannot find a Konsole profile with the given profile name, check the arguments.")
            # n.show()
            sys.exit()
    else:
        # No Konsole Theme provided
        pass

def check_config_files(
        path: str,
        filename: str,
        string:str,
        theme_name: str,
    ) -> bool:

    with open(path + filename, "r") as file:
        string_found = re.findall(string + "[A-z 0-9 \.\-\,=:_]*", str(file.readlines()))[0]
        #[:-2]
        string_found = str.replace(string_found, "\n", "")
        string_found = str.replace(string_found, "\\n","")
        if (string_found == string + theme_name):
            # The theme has been already applied correctly
            file.close()
            return True
        else:
            # Continue updating with the new theme
            file.close()
            return False

def update_file(
        path: str,
        filename: str,
        string: str,
        string_to_add: str,
    ) -> bool:
    with open(path+filename, "r") as f:
        # [A-z \.-]*
        # [A-z \.\-0-9);]*

        # current_theme contains the entire line found in the file, to be modified
        current_theme = re.findall(string + "[A-z \.,\-0-9();\"β]*", str(f.readlines()))[0][:-2]
        logger.debug(f"current_theme: {current_theme}")

    
    with open(path+filename, "r") as f:
        s = f.read()
        if current_theme not in s:
            logger.error(f"Error while looking for a previous valid theme in the DE configs file.")
            # subprocess.run(args=["notify-send", "LightHouse:", "Error while looking for a previous valid theme in the DE configs file."])
            # n = notify2.Notification("ERROR", "Cannot find a valid theme entry in the DE config file.")
            # n.show()
            return False

    # Safely write the changed content, if found in the file
    with open(path+filename, 'w') as f:
        # Let's define the new line that will entirely substitute current_theme
        s = s.replace(current_theme, string.replace("\\", "") + string_to_add)
        f.write(s)
    return True

def set_plasma_global_theme(plasma_theme: str) -> None:
    try:
        subprocess.run(args=["lookandfeeltool", "--apply", plasma_theme], text=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error(f"Cannot apply Global Theme, is lookandfeeltool installed?")
        # n = notify2.Notification("ERROR", "Cannot apply Global Theme, is lookandfeeltool installed?")
        # n.show()
        sys.exit()
    
    # Update "kdeglobals" file
    # Example: LookAndFeelPackage=Aritim-Dark_DEV
    if update_file(config_path, "kdeglobals", "LookAndFeelPackage=", plasma_theme) is False:
        logger.error(f"Something went wrong when setting Plasma Global theme...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting Plasma Global theme...")
        # n.show()

def set_gtk_theme(gtk_theme: str) -> None:
    # See https://old.reddit.com/r/kde/comments/slizni/changing_gnomegtk_application_style_theme_from/
    # dbus-send --session --dest=org.kde.GtkConfig --type=method_call /GtkConfig org.kde.GtkConfig.setGtkTheme 'string:themes_name_goes_here'
    try:
        subprocess.run(
            args=[
                "dbus-send",
                "--session",
                "--dest=org.kde.GtkConfig",
                "--type=method_call",
                "/GtkConfig",
                "org.kde.GtkConfig.setGtkTheme",
                f"string:{gtk_theme}",
            ]
        )
    except subprocess.CalledProcessError:
        logger.error(f"Something went wrong when setting \"gtk-theme\"...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting \"gtk-theme\"...")
        # n.show()
        sys.exit()

def set_wallpaper(wallpaper: str) -> None:
    # See https://old.reddit.com/r/kde/comments/65pmhj/change_wallpaper_from_terminal/
    jscript = f"""
        var allDesktops = desktops();
        print (allDesktops);
        for (i=0;i<allDesktops.length;i++) {{
            d = allDesktops[i];
            d.wallpaperPlugin = "org.kde.image";
            d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
            d.writeConfig("Image", "{wallpaper}")
        }}
    """
    try:
        subprocess.run(
            args=[
                "dbus-send",
                "--session",
                "--dest=org.kde.plasmashell",
                "--type=method_call",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                f"string:{jscript}",
            ]
        )
    except subprocess.CalledProcessError:
        logger.error(f"Something went wrong when setting \"wallpaper\"...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting \"wallpaper\"...")
        # n.show()
        sys.exit()

def set_konsole(konsole_profile: str) -> None:
    # Get the PIDs of all Konsole's processes running
    try:
        res = subprocess.run(args=["pidof", "konsole"], capture_output=True)
    except subprocess.CalledProcessError:
        logger.error(f"Something went wrong when setting \"konsole profile\"...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting \"konsole profile\"...")
        # n.show()
        sys.exit()
    pids = str(res.stdout, "UTF-8").replace("\n", "").split()
    logger.debug(f"PIDs: {pids}")

    # Now, for each Konsole qindow (i.e. PID), get how many sessions there are and their unique number
    session_extractor = re.compile("<node name=\"([0-9]*)\"\/>")
    for pid in pids:
        try:
            res = subprocess.run(
                args=[
                    "dbus-send",
                    "--session",
                    f"--dest=org.kde.konsole-{pid}",
                    "--type=method_call",
                    "--print-reply",
                    f"/Sessions",
                    "org.freedesktop.DBus.Introspectable.Introspect",
                ],
                capture_output=True
            )
        except subprocess.CalledProcessError:
            logger.error(f"Something went wrong when setting \"konsole profile\"...")
            # n = notify2.Notification("ERROR", "Something went wrong when setting \"konsole profile\"...")
            # n.show()
            sys.exit()
        # output_lines = str(res.stdout, "UTF-8").split("\n")
        output_string = str(res.stdout, "UTF-8")
        session_list = re.findall(session_extractor, output_string)
        logger.debug(f"session_list: {session_list}")

        # For each Konsole process, change its profile.
        # This applies the theme to all Konsole windows and sessions currently opened
        for session in session_list:
            logger.debug(f"Konsole PID: {pid}")
            logger.debug(f"Konsole session: {session}")
            try:
                subprocess.run(
                    args=[
                        "dbus-send",
                        "--session",
                        f"--dest=org.kde.konsole-{pid}",
                        "--type=method_call",
                        f"/Sessions/{session}",
                        "org.kde.konsole.Session.setProfile",
                        f"string:{konsole_profile}",
                    ]
                )
            except subprocess.CalledProcessError:
                logger.error(f"Something went wrong when setting \"konsole profile\"...")
                # n = notify2.Notification("ERROR", "Something went wrong when setting \"konsole profile\"...")
                # n.show()
                sys.exit()

    # Now, change the default Konsole profile (this will be applied to all freshly spawned windows)
    filename = "/konsolerc"
    if update_file(config_path, filename, "DefaultProfile=", konsole_profile + ".profile") is False:
        logger.error(f"Something went wrong when setting Konsole profile...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting Konsole profile...")
        # n.show()

def set_vscode(vscode_theme):
    # "workbench.colorTheme": "GitHub Plus",
    filename = "settings.json"
    if update_file(vscode_path, filename, "\"workbench.colorTheme\":", " \""+vscode_theme+"\",") is False:
        logger.error(f"Something went wrong when setting VSCode theme...")
        # n = notify2.Notification("ERROR", "Something went wrong when setting VSCode theme...")
        # n.show()
    if check_config_files(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") is True:
        logger.debug(f"1 --> 0")
        # n = notify2.Notification("1 --> 0")
        # n.show()
        if update_file(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(0)},") is False:
            logger.error(f"Something went wrong when setting VSCode PDF_preview theme...")
            # n = notify2.Notification("ERROR", "Something went wrong when setting VSCode PDF_preview theme...")
            # n.show()
    else:
        logger.debug(f"0 --> 1")
        # n = notify2.Notification("0 --> 1")
        # n.show()
        if update_file(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") is False:
            logger.error(f"Something went wrong when setting VSCode PDF_preview theme...")
            # n = notify2.Notification("ERROR", "Something went wrong when setting VSCode PDF_preview theme...")

            # n.show()
def rstPlasmashell():
    try:
        subprocess.run(args=["plasmashell", "--replace > ", "/dev/null", "2>&1", "&&", "sleep 5 &"], text=True)
    except subprocess.CalledProcessError:
        logger.critical(f"Cannot restart plasmashell, WTF?")
        # n = notify2.Notification("CRITICAL ERROR", "Cannot restart plasmashell, WTF?")
        # n.show()
        sys.exit() 


#   __  __          _____ _   _ 
#  |  \/  |   /\   |_   _| \ | |
#  | \  / |  /  \    | | |  \| |
#  | |\/| | / /\ \   | | | . ` |
#  | |  | |/ ____ \ _| |_| |\  |
#  |_|  |_/_/    \_\_____|_| \_|
#                               


if __name__ == '__main__':

    plasma_theme : str = ""
    gtk_theme : str = ""
    wallpaper : str = ""
    konsole_profile : str = ""
    vscode_theme : str = ""

    logger.handlers[0].setLevel(logging.INFO)

    short_opts : str = "hp:g:w:k:f:c:v"
    long_opts : list = ["help", "plasma=", "gtk=", "wallpaper=", "konsole=", "vscode=", "verbose"]
    arg_list : list = sys.argv[1:]

    try:
        args, vals = getopt.getopt(arg_list, short_opts, long_opts);
    except getopt.error:
        logger.error(f"Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
        # n = notify2.Notification("ERROR", "Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
        # n.show()
        print("--- LightHouse Help Page ---")
        print("")
        print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
        print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
        print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
        print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
        print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
        print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
        print("")
        print("--- LightHouse Help Page ---")
        sys.exit()

    # Evaluate the given options
    for curr_arg, curr_val in args:
        if curr_arg in ("-h", "--help"):
            logger.info("Visit https://bit.ly/32UK20A or launch the script from terminal for full help/man page")
            # n = notify2.Notification("LightHouse Help", "Visit https://bit.ly/32UK20A or launch the script from terminal for full help/man page")
            # n.show()
            print("--- LightHouse Help Page ---")
            print("")
            print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
            print("\t-p,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
            print("\t-g,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
            print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
            print("\t-k,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
            print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
            print("")
            print("--- LightHouse Help Page ---")
            sys.exit()
        elif curr_arg in ("-p", "--plasma"):
            plasma_theme = curr_val
        elif curr_arg in ("-g", "--gtk"):
            gtk_theme = curr_val
        elif curr_arg in ("-w", "--wallpaper"):
            wallpaper = curr_val
        elif curr_arg in ("-k", "--konsole"):
            konsole_profile = curr_val
        elif curr_arg in ("-c", "--vscode"):
            vscode_theme = curr_val
        elif curr_arg in ("-v", "--verbose"):
            logger.handlers[0].setLevel(logging.DEBUG)
        else:
            pass

    logger.debug(f"[setup] Plasma_theme: {plasma_theme}")
    logger.debug(f"[setup] gtk_theme: {gtk_theme}")
    logger.debug(f"[setup] wallpaper: {wallpaper}")
    logger.debug(f"[setup] konsole_profile: {konsole_profile}")
    logger.debug(f"[setup] vscode_theme: {vscode_theme}")

    if len(args) == 0:
        logger.error("Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
        # n = notify2.Notification("ERROR", "Cannot start LightHouse! Error while specifying arguments, see wiki or --help")
        # n.show()
        print("--- LightHouse Help Page ---")
        print("")
        print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
        print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
        print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
        print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
        print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
        print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
        print("")
        print("--- LightHouse Help Page ---")
        print("")
        sys.exit("ERROR! No arguments specified!")

    # Check if the specified themes exist in system
    check_args(plasma_theme, gtk_theme, wallpaper, konsole_profile)

    if (plasma_theme and check_config_files(config_path, "kdeglobals", "LookAndFeelPackage=", plasma_theme)):
        # Next notification is disabled as can be too distracting, especially if cron launches the script quite often
        # subprocess.run(
        #     args=[
        #         "notify-send",
        #         "LightHouse",
        #         "There is nothing to do, exiting..."
        #     ]
        # )
        logger.info("There is nothig to do, exiting...")
        # n = notify2.Notification("ERROR", "There is nothig to do, exiting...")
        # n.show()
        sys.exit()
    else:
        if plasma_theme:
            set_plasma_global_theme(plasma_theme)
        if gtk_theme:
            set_gtk_theme(gtk_theme)
        if wallpaper:
            set_wallpaper(wallpaper)
        if konsole_profile:
            set_konsole(konsole_profile)
        if vscode_theme:
            set_vscode(vscode_theme)

        # Some issues may disappear by forcing a plasmashell restart
        # rstPlasmashell()