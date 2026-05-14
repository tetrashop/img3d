import subprocess
import os
import sys

def run_cmd(cmd, allow_fail=False):
    """اجرای یک دستور shell و بررسی خطا"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print("STDOUT:", result.stdout)
    if result.stderr and not allow_fail:
        print("STDERR:", result.stderr)
    if result.returncode != 0 and not allow_fail:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result

# Get ANDROID_HOME
android_home = os.environ.get('ANDROID_HOME', '/usr/local/lib/android/sdk')
android_jar = os.path.join(android_home, 'platforms', 'android-34', 'android.jar')
build_tools = os.path.join(android_home, 'build-tools', '34.0.0')

print(f"ANDROID_HOME: {android_home}")
print(f"Android JAR: {android_jar}")
print(f"Build tools: {build_tools}")

# Ensure build tools are installed
run_cmd(f'yes | {android_home}/cmdline-tools/latest/bin/sdkmanager "build-tools;34.0.0" "platforms;android-34"', allow_fail=True)

# Create directories
os.makedirs('android-app/gen', exist_ok=True)
os.makedirs('android-app/obj', exist_ok=True)

# Generate R.java (may fail if no resources - that's OK)
run_cmd(f'aapt package -f -m -J android-app/gen -M android-app/AndroidManifest.xml -S android-app/res -I {android_jar}', allow_fail=True)

# If R.java not generated, create minimal one
r_file = 'android-app/gen/com/img3d/app/R.java'
if not os.path.exists(r_file):
    os.makedirs(os.path.dirname(r_file), exist_ok=True)
    with open(r_file, 'w') as f:
        f.write('package com.img3d.app;\npublic final class R {}\n')
    print("Created minimal R.java")

# Compile Java
run_cmd(f'javac -source 1.8 -target 1.8 -bootclasspath {android_jar} -d android-app/obj android-app/src/com/img3d/app/MainActivity.java android-app/gen/com/img3d/app/R.java', allow_fail=True)

# If compilation failed, try without R.java
if not os.path.exists('android-app/obj/com/img3d/app/MainActivity.class'):
    print("Trying compilation without R.java...")
    run_cmd(f'javac -source 1.8 -target 1.8 -bootclasspath {android_jar} -d android-app/obj android-app/src/com/img3d/app/MainActivity.java', allow_fail=True)

# Create DEX
run_cmd(f'{build_tools}/dx --dex --output=android-app/classes.dex android-app/obj/')

# Package APK
run_cmd(f'cd android-app && aapt package -f -M AndroidManifest.xml -S res -I {android_jar} -F app-unsigned.apk')

# Add DEX to APK
run_cmd(f'cd android-app && aapt add app-unsigned.apk classes.dex')

# Sign APK
run_cmd('cd android-app && keytool -genkey -v -keystore debug.keystore -alias debug -keyalg RSA -keysize 2048 -validity 10000 -storepass android -keypass android -dname "CN=Debug, OU=Debug, O=Debug, L=Debug, ST=Debug, C=US"', allow_fail=True)
run_cmd(f'cd android-app && {build_tools}/apksigner sign --ks debug.keystore --ks-pass pass:android --key-pass pass:android app-unsigned.apk')

# Move final APK
if os.path.exists('android-app/app-unsigned.apk'):
    os.rename('android-app/app-unsigned.apk', 'img3d.apk')
    print("SUCCESS: APK created at img3d.apk")
else:
    print("ERROR: APK not created!")
    sys.exit(1)
