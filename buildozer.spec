[app]

# (str) Title of your application
title = XFC 보충 어플

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,json,ttf,otf

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,gspread,google-auth,google-auth-httplib2,google-auth-oauthlib,requests,requests-oauthlib,oauthlib,charset_normalizer,cryptography,pyasn1,urllib3,certifi,idna,pyparsing,six

# (list) Supported orientations
orientation = portrait

# Kivy version to use
osx.kivy_version = 2.2.0

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,POST_NOTIFICATIONS,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,BLUETOOTH_ADMIN

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use.
android.ndk_api = 24

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# Python for android (p4a) specific
p4a.branch = release-2024.01.21

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.12.2
ios.codesign.allowed = false

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
