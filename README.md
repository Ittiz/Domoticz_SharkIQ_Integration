# Domoticz_SharkIQ_Integration
Python Scripts I created to integrate the Shark IQ Vacuum with the Domoticz Home Automation system.

General information:
I use a Shark ION vacuum, I can't guarantee this will work for all Shark vacuums. If this script breaks your vacuum it's not my fault! USE AT YOUR OWN RISK!

Shark contracted out a company called Alya Networks to do their integration. Although their vacuums only seem to work through the app, Alya has a web portal you can control your vacuum through. My scripts interface with this portal to control the vacuum. If you log in there be EXTREMELY careful it doesn't have any protections to prevent you from breaking your vacuum.

The timer script creates all the needed devices and variables automatically. An important note is these scripts only work with one vacuum. If you have more than one that it will automatically grab the 1st one you registered with Shark. The others will be ignored. Another note is the scripts aren't totally complete. I'd like to add things like uploading your Domoticz room map to the vacuum without it having to learn your house. Possibly some other functions/switches I didn't need that urgently.

Requirements:
1: A working Domoticz HomeAutomation Server
2: Shark Vacuum
3: Shark account with email and password
4: Python 3 enabled on your server
5: Curl enabled on your server
6: None passworded, open access from localhost (127.0.0.1)

Instructions:
1: Place the scripts in your /domoticz/scripts/python folder.
2: Wait at least a minute for the 1st script to kick in and create all your variables and devices.
3: Goto the user variable section in Domoticz, Update the AylaMail and AylaPass variables with the ones you used to sign up with in the Shark App.
4: That's it! You can go into your switches and Utility sections in Domoticz to view the new hardware. Due to limitations to the way the integration by Shark was done I split out the devices that provide info (placed into the Utility section) and buttons to activate and control the vacuum (in the Switches section).
5: Now you can use Domoticz timers and scripts to control your vacuum.
