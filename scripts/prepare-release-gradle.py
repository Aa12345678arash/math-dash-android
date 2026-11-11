#!/usr/bin/env python3
"""Configure a freshly generated Capacitor Android project for signed MATH DASH release."""
from pathlib import Path
import re

gradle = Path("android/app/build.gradle")
if not gradle.exists():
    raise SystemExit("android/app/build.gradle was not generated")

source = gradle.read_text(encoding="utf-8")
pattern = re.compile(r"(?m)^(\s*)buildTypes\s*\{\s*\n(\s*)release\s*\{")
match = pattern.search(source)
if not match:
    raise SystemExit("Could not find the expected Android release buildTypes block")

outer_indent, inner_indent = match.group(1), match.group(2)
signing = (
    f"{outer_indent}signingConfigs {{\n"
    f"{inner_indent}release {{\n"
    f"{inner_indent}    storeFile file(System.getenv('ANDROID_KEYSTORE_PATH'))\n"
    f"{inner_indent}    storePassword System.getenv('ANDROID_KEYSTORE_PASSWORD')\n"
    f"{inner_indent}    keyAlias System.getenv('ANDROID_KEY_ALIAS')\n"
    f"{inner_indent}    keyPassword System.getenv('ANDROID_KEY_PASSWORD')\n"
    f"{inner_indent}}}\n"
    f"{outer_indent}}}\n\n"
)
source = source[:match.start()] + signing + source[match.start():]
replacement = (
    f"{outer_indent}buildTypes {{\n"
    f"{inner_indent}release {{\n"
    f"{inner_indent}    signingConfig signingConfigs.release"
)
source, changed = pattern.subn(replacement, source, count=1)
if changed != 1:
    raise SystemExit("Could not attach the release signing configuration")

source, code_count = re.subn(r"(?m)^(\s*versionCode\s+)\d+\s*$", r"\g<1>3", source, count=1)
source, name_count = re.subn(r"(?m)^(\s*versionName\s+)[\"'][^\"']+[\"']\s*$", r'\g<1>"0.1.3"', source, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not set versionCode/versionName; refusing to build a mis-versioned APK")

gradle.write_text(source, encoding="utf-8")
print("Configured signed release: versionCode=3, versionName=0.1.3")
