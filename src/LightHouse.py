#!/usr/bin/env python3

import os
import re
import sys
import pwd

# Requires dbus-python installed (possibly from distro's package manager)
import dbus

import getopt
import logging
import subprocess
from logging import config
from logging_conf import LOGGING

# Load the logging configuration
config.dictConfig(LOGGING)
logger = logging.getLogger("LightHouse")

# Create the notifier
notifier = dbus.Interface(
        object=dbus.SessionBus().get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications"),
        dbus_interface="org.freedesktop.Notifications"
    )


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

# Configure the default parameters for notifications
# See https://www.galago-project.org/specs/notification/0.9/x408.html#command-notify
app_name = "LightHouse"
replaces_id = 0
info_app_icon = "system-help.svg"
warning_app_icon = "dialog-warning-symbolic.svg"
critical_app_icon = "dialog-error-symbolic.svg"
summary = ""
body = ""
actions = []
# See https://www.galago-project.org/specs/notification/0.9/x344.html
# For urgency levels etc, move to the previous pages, from the one above
hints = {"urgency" : 1}
expire_timeout = -1



#   _____  ______ ______   
#  |  __ \|  ____|  ____|  
#  | |  | | |__  | |__ ___ 
#  | |  | |  __| |  __/ __|
#  | |__| | |____| |  \__ \
#  |_____/|______|_|  |___/
#                          

# Check if Global Theme exists
# TODO: check presence of the gtk_theme
def check_args(
        plasma_theme: str,
        gtk_theme: str,
        wallpaper: str,
        konsole_profile: str,
    ) -> None:
    """Checks if the given theme names reflect existing themes and profiles.

    Args:
        plasma_theme (str): The name of the Plasma Theme you want to be applied.
        gtk_theme (str): The name of the GTK Theme you want to be applied.
        wallpaper (str): The filename of the wallpaper you want to be applied.
        konsole_profile (str): The name of the Konsole profile you want to be applied.

    Raises:
        RuntimeError: Cannot check Global Theme presence, is lookandfeeltool installed?
        RuntimeError: Cannot find a Global Theme with the given name...
        RuntimeError: Cannot find a wallpaper with the given filename...
        RuntimeError: Cannot find a Konsole profile with the given filename...
    """    
    # Check plasma_theme
    if plasma_theme:
        try:
            res = subprocess.run(args=["lookandfeeltool", "-l"], text=True, capture_output=True)
            res = res.stdout.split("\n")
            logger.debug(f"lookandfeeltool output: {res}")
        except subprocess.CalledProcessError:
            raise RuntimeError("Cannot check Global Theme presence, is lookandfeeltool installed?")
        if plasma_theme not in res:
            raise RuntimeError("Cannot find a Global Theme with the given name...")
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
            raise RuntimeError("Cannot find a wallpaper with the given filename...")
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
            raise RuntimeError("Cannot find a Konsole profile with the given filename...")
    else:
        # No Konsole Theme provided
        pass

def check_config_files(
        path: str,
        filename: str,
        configuration_string:str,
        theme_name: str,
    ) -> bool:
    """Reads a configuration file and checks if a given theme has been correctly applied.

    This can be used to check if writing to a confi file has been done correctly or if a theme has
    already been applied previously.

    Args:
        path (str): The path pointing to the configuration file.
        filename (str): The filename of the configuration file.
        configuration_string (str): The configuration string to look for that prepends the theme name.
        theme_name (str): The theme name string that folows the configuration string.

    Returns:
        bool: False if the theme cannot be found in the configuration file, True otherwise.
    """    
    with open(path + filename, "r") as file:
        string_found = re.findall(configuration_string + "[A-z 0-9 \.\-\,=:_]*", str(file.readlines()))[0]
        #[:-2]
        string_found = str.replace(string_found, "\n", "")
        string_found = str.replace(string_found, "\\n","")
        if (string_found == configuration_string + theme_name):
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
        configuration_string: str,
        string_to_add: str,
    ) -> bool:
    """Updates a configuration file with the given theme name.

    Args:
        path (str): The path pointing to the configuration file.
        filename (str): The filename of the configuration file.
        configuration_string (str): The configuration string to look for that prepends the theme name.
        string_to_add (str): The theme name string that folows the configuration string.

    Returns:
        bool: False if no string mentioning the theme can be found, True if the file has been updated correctly.
    """
    with open(path+filename, "r") as f:
        # [A-z \.-]*
        # [A-z \.\-0-9);]*

        # current_theme contains the entire line found in the file, to be modified
        current_theme = re.findall(configuration_string + "[A-z \.,\-0-9();\"β]*", str(f.readlines()))[0][:-2]
        logger.debug(f"current_theme: {current_theme}")

    with open(path+filename, "r") as f:
        s = f.read()
        if current_theme not in s:
            logger.error(f"Error while looking for a previous valid theme in the DE configs file.")
            return False

    # Safely write the changed content, if found in the file
    with open(path+filename, 'w') as f:
        # Let's define the new line that will entirely substitute current_theme
        s = s.replace(current_theme, configuration_string.replace("\\", "") + string_to_add)
        f.write(s)
    logger.debug(f"updated_theme: " + configuration_string.replace("\\", "") + string_to_add)
    return True

def set_plasma_global_theme(plasma_theme: str) -> bool:
    """Sets the Plasma's Global Theme.

    Args:
        plasma_theme (str): The name of the Plasma GLobal Theme to be applied.

    Raises:
        RuntimeError: Error when applying the theme, is 'lookandfeeltool' installed in the system?

    Returns:
        bool: False if the 'kdeglobals' file cannot be updated: the theme is applied but the system
            is not anymore aware of the changes. True otherwise.
    """
    try:
        subprocess.run(args=["lookandfeeltool", "--apply", plasma_theme], text=True, capture_output=True)
    except subprocess.CalledProcessError: raise
    
    # Update "kdeglobals" file
    # Example: LookAndFeelPackage=Aritim-Dark_DEV
    if update_file(config_path, "kdeglobals", "LookAndFeelPackage=", plasma_theme) is False:
        logger.error(f"Something went wrong when setting Plasma Global theme...")
        return False
    else:
        return True

def set_gtk_theme(gtk_theme: str) -> None:
    """Set the GTK theme.

    Args:
        gtk_theme (str): The name of the GTK theme to be set.

    Raises:
        RuntimeError: If unable to set GTK theme.
    """    
    # See https://old.reddit.com/r/kde/comments/slizni/changing_gnomegtk_application_style_theme_from/
    # dbus-send --session --dest=org.kde.GtkConfig --type=method_call /GtkConfig org.kde.GtkConfig.setGtkTheme 'string:themes_name_goes_here'
    try:
        interface = dbus.Interface(
                dbus.SessionBus().get_object("org.kde.GtkConfig", "/GtkConfig"),
                dbus_interface="org.kde.GtkConfig"
            )
        interface.setGtkTheme(gtk_theme)
    except:
        raise RuntimeError(f"Unable to set GTK theme! gtk_theme: {gtk_theme}")

def set_wallpaper(wallpaper: str) -> None:
    """Set the wallpaper.

    Args:
        wallpaper (str): The filename of the wallpaper to be set.

    Raises:
        RuntimeError: If unable to set wallpaper.
    """    
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
        interface = dbus.Interface(
            dbus.SessionBus().get_object("org.kde.plasmashell", "/PlasmaShell"),
            dbus_interface="org.kde.PlasmaShell"
        )
        interface.evaluateScript(jscript)
    except:
        raise RuntimeError(f"Unable to set wallpaper! wallpaper: {wallpaper}")

def set_konsole(konsole_profile: str) -> None:
    """Set Konsole profile.

    Args:
        konsole_profile (str): The name of the Konsole profile to be set.

    Raises:
        RuntimeError: Unable to get the sessions for the given PID.
        RuntimeError: No sessions found.
        RuntimeError: Unable to set Konsole profile for this session.
        RuntimeError: Something went wrong when setting Konsole profile.
    """
    # Get the PIDs of all Konsole's processes running
    try:
        res = subprocess.run(args=["pidof", "konsole"], capture_output=True)
    except subprocess.CalledProcessError: raise

    pids = str(res.stdout, "UTF-8").replace("\n", "").split()
    logger.debug(f"PIDs: {pids}")
    # Now, for each Konsole qindow (i.e. PID), get how many sessions there are and their unique number
    session_extractor = re.compile("<node name=\"([0-9]*)\"\/>")
    for pid in pids:
        output_string = ""
        try:
            interface = dbus.Interface(
                dbus.SessionBus().get_object(f"org.kde.konsole-{pid}", "/Sessions"),
                dbus_interface="org.freedesktop.DBus.Introspectable"
            )
            output_string = interface.Introspect()
        except:
            raise RuntimeError(f"Unable to get the sessions for the given PID! PID: {pid}")
        # try:
        #     res = subprocess.run(
        #         args=[
        #             "dbus-send",
        #             "--session",
        #             f"--dest=org.kde.konsole-{pid}",
        #             "--type=method_call",
        #             "--print-reply",
        #             f"/Sessions",
        #             "org.freedesktop.DBus.Introspectable.Introspect",
        #         ],
        #         capture_output=True
        #     )
        # except subprocess.CalledProcessError: raise

        # output_lines = str(res.stdout, "UTF-8").split("\n")
        # output_string = str(res.stdout, "UTF-8")
        if output_string:
            session_list = re.findall(session_extractor, output_string)
        else:
            # No sessions found, this is impossilble!
            logger.error(f"output_string: {output_string}")
            raise RuntimeError("No sessions found!")

        logger.debug(f"session_list: {session_list}")
        # For each Konsole process, change its profile.
        # This applies the theme to all Konsole windows and sessions currently opened
        for session in session_list:
            logger.debug(f"Konsole PID: {pid}")
            logger.debug(f"Konsole session: {session}")

            output_string = ""
            try:
                interface = dbus.Interface(
                    dbus.SessionBus().get_object(f"org.kde.konsole-{pid}", f"/Sessions/{session}"),
                    dbus_interface="org.kde.konsole.Session"
                )
                interface.setProfile(konsole_profile)
            except:
                raise RuntimeError(f"Unable to set Konsole profile for this session! konsole_profile: {konsole_profile}, session: {session}")
            # try:
            #     subprocess.run(
            #         args=[
            #             "dbus-send",
            #             "--session",
            #             f"--dest=org.kde.konsole-{pid}",
            #             "--type=method_call",
            #             f"/Sessions/{session}",
            #             "org.kde.konsole.Session.setProfile",
            #             f"string:{konsole_profile}",
            #         ]
            #     )
            # except subprocess.CalledProcessError: raise

    # Now, change the default Konsole profile (this will be applied to all freshly spawned windows)
    filename = "/konsolerc"
    if update_file(config_path, filename, "DefaultProfile=", konsole_profile + ".profile") is False:
        logger.error(f"Something went wrong when setting Konsole profile...")
        raise RuntimeError("Something went wrong when setting Konsole profile...")

def set_vscode(vscode_theme: str) -> bool:
    """Set the VSCode theme and set the PDF webview light or dark.

    Args:
        vscode_theme (str): The name of the VSCode theme.

    Returns:
        bool: False if unable to set the VSCode theme or the PDF webview, True is everything completed successfully.
    """    
    # "workbench.colorTheme": "GitHub Plus",
    filename = "settings.json"
    if update_file(vscode_path, filename, "\"workbench.colorTheme\":", " \""+vscode_theme+"\",") is False:
        logger.error(f"Something went wrong when setting VSCode theme...")
        return False

    if check_config_files(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") is True:
        logger.debug(f"1 --> 0")
        if update_file(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(0)},") is False:
            logger.error(f"Something went wrong when setting VSCode PDF webview theme...")
            return False
        else:
            return  True
    else:
        logger.debug(f"0 --> 1")
        if update_file(vscode_path, filename, "\"latex-workshop.view.pdf.invert\":", f" {str(1)},") is False:
            logger.error(f"Something went wrong when setting VSCode PDF webview theme...")
            return False
        else:
            return True

def rstPlasmashell() -> None:
    """Resets 'plasmashell'. This may come handy in case of cache issues or themes not completely be applied.

    Raises:
        RuntimeError: If unable to restart 'plasmashell'.

    """    
    try:
        subprocess.run(args=["plasmashell", "--replace > ", "/dev/null", "2>&1", "&&", "sleep 5 &"], text=True)
    except subprocess.CalledProcessError: raise


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
        notifier.Notify(
            app_name,
            replaces_id,
            critical_app_icon,
            "ERROR",
            "Cannot start LightHouse! Error while specifying arguments, see wiki or --help",
            actions,
            {"urgency" : 3},
            expire_timeout,
        )
        print("--- LightHouse Help Page ---")
        print("")
        print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
        print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
        print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
        print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
        print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
        print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
        print("\t-v=,\t--verbose:\t\tVerbose mode: enable DEBUG logging")
        print("")
        print("--- LightHouse Help Page ---")
        sys.exit()

    # Evaluate the given options
    for curr_arg, curr_val in args:
        if curr_arg in ("-h", "--help"):
            logger.info("Visit https://bit.ly/32UK20A or launch the script from terminal for full help/man page")
            notifier.Notify(
                app_name,
                replaces_id,
                info_app_icon,
                "Help page",
                "Visit https://bit.ly/32UK20A or launch the script from terminal for full help/man page",
                actions,
                {"urgency" : 0},
                expire_timeout,
            )

            print("--- LightHouse Help Page ---")
            print("")
            print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
            print("\t-p,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
            print("\t-g,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
            print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
            print("\t-k,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
            print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
            print("\t-v=,\t--verbose:\t\tVerbose mode: enable DEBUG logging")
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
        notifier.Notify(
                app_name,
                replaces_id,
                warning_app_icon,
                "Warning",
                "Cannot start LightHouse! Error while specifying arguments, see wiki or --help",
                actions,
                {"urgency" : 1},
                expire_timeout,
            )

        print("--- LightHouse Help Page ---")
        print("")
        print("\t-h,\t--help:\t\t\t\t\tOpen this help page")
        print("\t-p=,\t--plasma = PLASMA_GLOBAL_THEME:\t\tApply Plasma Global Theme")
        print("\t-g=,\t--gtk = GTK_THEME:\t\t\tApply gtk_theme")
        print("\t-w=,\t--wallpaper = WALLPAPER:\t\tApply Wallpaper (indicate /path/to/file)")
        print("\t-k=,\t--konsole = KONSOLE_PROFILE:\t\tApply Konsole Profile")
        print("\t-c=,\t--vscode = VSCODE_THEME:\t\tApply VSCode Theme")
        print("\t-v=,\t--verbose:\t\tVerbose mode: enable DEBUG logging")
        print("")
        print("--- LightHouse Help Page ---")
        print("")
        sys.exit()

    # Check if the specified themes exist in system
    try:
        check_args(plasma_theme, gtk_theme, wallpaper, konsole_profile)
    except:
        logger.error("One of the items specified as argument cannot be found in system!")
        notifier.Notify(
            app_name,
            replaces_id,
            critical_app_icon,
            "ERROR",
            "One of the items specified as argument cannot be found in system!",
            actions,
            {"urgency" : 2},
            expire_timeout,
        )

    if (plasma_theme and check_config_files(config_path, "kdeglobals", "LookAndFeelPackage=", plasma_theme)):
        # Next notification is disabled as can be too distracting, especially if cron launches the script quite often
        notifier.Notify(
            app_name,
            replaces_id,
            info_app_icon,
            "Info",
            "There is nothig to do, exiting...",
            actions,
            {"urgency" : 0},
            expire_timeout,
        )
        logger.info("There is nothig to do, exiting...")
        sys.exit()
    else:
        if plasma_theme:
            try:
                if set_plasma_global_theme(plasma_theme) is False:
                    logger.error("")
                    notifier.Notify(
                        app_name,
                        replaces_id,
                        warning_app_icon,
                        "Warning",
                        "Plasma's Global Theme applied, but configuration not updated!",
                        actions,
                        {"urgency" : 1},
                        expire_timeout,
                    )
            except:
                logger.error("Error when applying Plasma's Global Theme, is 'lookandfeeltool' installed?")
                notifier.Notify(
                    app_name,
                    replaces_id,
                    critical_app_icon,
                    "ERROR",
                    "Error when applying Plasma's Global Theme, is 'lookandfeeltool' installed?",
                    actions,
                    {"urgency" : 2},
                    expire_timeout,
                )
        if gtk_theme:
            try:
                set_gtk_theme(gtk_theme)
            except:
                logger.error("Error when applying GTK theme...")
                notifier.Notify(
                    app_name,
                    replaces_id,
                    critical_app_icon,
                    "ERROR",
                    "Error when applying GTK theme...",
                    actions,
                    {"urgency" : 2},
                    expire_timeout,
                )
        if wallpaper:
            try:
                set_wallpaper(wallpaper)
            except:
                logger.error("Error when applying wallpaper...")
                notifier.Notify(
                    app_name,
                    replaces_id,
                    critical_app_icon,
                    "ERROR",
                    "Error when applying wallpaper...",
                    actions,
                    {"urgency" : 2},
                    expire_timeout,
                )
        if konsole_profile:
            try:
                set_konsole(konsole_profile)
            except:
                logger.error("Error when applying Konsole Profile...")
                notifier.Notify(
                    app_name,
                    replaces_id,
                    critical_app_icon,
                    "ERROR",
                    "Error when applying Konsole Profile...",
                    actions,
                    {"urgency" : 2},
                    expire_timeout,
                )
        if vscode_theme:
            if set_vscode(vscode_theme) is False:
                logger.error("Unable to set VSCode theme or PDF preview...")
                notifier.Notify(
                    app_name,
                    replaces_id,
                    critical_app_icon,
                    "ERROR",
                    "Unable to set VSCode theme or PDF preview...",
                    actions,
                    {"urgency" : 2},
                    expire_timeout,
                )

        # Some issues may disappear by forcing a plasmashell restart
        # try:
        #     rstPlasmashell()
        # except:
        #     logger.error("Unable to restart 'plasmashell'")
        #     notifier.Notify(
        #         app_name,
        #         replaces_id,
        #         app_icon,
        #         "ERROR",
        #         "Unable to restart 'plasmashell'",
        #         actions,
        #         {"urgency" : 2},
        #         expire_timeout,
        #     )