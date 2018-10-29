# -*- coding: utf-8 -*-
# LambdaScrapers Cleanup Service

import os
import re

import xbmc
import xbmcvfs
import xbmcaddon

from lib.lambdascrapers import getAllHosters

'''
Temporary service to TRY to make some file changes, and then prevent itself from running again.
'''

ADDON = xbmcaddon.Addon()

# 1) Do the actual file changes:
try:
    profileFolderPath = xbmc.translatePath(ADDON.getAddonInfo('profile')).decode('utf-8')
    settingsPath = os.path.join(profileFolderPath, 'settings.xml')

    # Rewrite the user settings file, ignoring all lines with obsolete providers.
    if xbmcvfs.exists(settingsPath):
        currentProviders = set(getAllHosters())
        with open(settingsPath, 'r+') as settingsFile:
            originalLines = settingsFile.readlines()
            settingsFile.seek(0)
            for line in originalLines:
                if 'provider.' in line:
                    if line.split('.', 1)[1] in currentProviders:
                        settingsFile.write(line) # Keep this valid provider.
                    else:
                        pass # Ignore this obsolete provider.
                else:
                    settingsFile.write(line) # Keep all other settings lines.
            settingsFile.truncate()
except:
    pass


# 2) Disable the service in the 'addon.xml' file.
try:
    addonFolderPath = xbmc.translatePath(ADDON.getAddonInfo('path')).decode('utf-8')
    addonXMLPath = os.path.join(addonFolderPath, 'addon.xml')

    # Disabling is done by commenting out the XML line with the service extension.
    with open(addonXMLPath, 'r+') as addonXMLFile:
        xml = addonXMLFile.read()
        serviceFilename = 'CleanupService\.py'
        pattern = r'(<\s*?extension.*?' + serviceFilename + '.*?\s*?/\s*?>)'
        updatedXML = re.sub(pattern, r'<!--\1-->', xml, count=1, flags=re.IGNORECASE)
        addonXMLFile.seek(0)
        addonXMLFile.write(updatedXML)
except:
    pass
