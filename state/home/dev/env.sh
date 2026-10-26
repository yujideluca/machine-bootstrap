# shellcheck shell=bash
JAVA_HOME="$(ls -d "$HOME"/dev/jdk-21* | head -1)"
export ANDROID_HOME="$HOME/dev/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$(ls -d "$HOME"/dev/gradle-* | head -1)/bin:$PATH"
export JAVA_HOME PATH
