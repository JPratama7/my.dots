#!/usr/bin/env bash
#
# usage: kb-layout.sh [--status|-s] [--next|-n]
#

if [[ "$1" == "--status" || "$1" == "-s" ]]; then
  # just print the two-letter code of the current main keyboard
  hyprctl devices -j \
    | jq -r '
      .keyboards[]
      | select(.main == true).active_keymap
      | {
          "English (US)": "EN",  "Russian": "RU",   "French": "FR",
          "German": "DE",        "Spanish": "ES",   "Italian": "IT",
          "Portuguese": "PT",    "Dutch": "NL",     "Swedish": "SV",
          "Norwegian": "NO",     "Danish": "DA",    "Finnish": "FI",
          "Polish": "PL",        "Czech": "CS",     "Hungarian": "HU",
          "Greek": "EL",         "Turkish": "TR",   "Hebrew": "HE",
          "Arabic": "AR",        "Thai": "TH",      "Chinese (Simplified)": "ZH-CN",
          "Chinese (Traditional)": "ZH-TW", "Japanese": "JA", "Korean": "KO"
        }[.]'
  exit 0

elif [[ "$1" == "--next" || "$1" == "-n" ]]; then
  # just print the name(s) of your main keyboard(s)
  main_keyboards=($(hyprctl devices -j | jq -r '.keyboards[] | select(.main == true) | .name'))
  echo "Main keyboard(s): ${main_keyboards[@]}"
  for kb in "${main_keyboards[@]}"; do
    # set the new layout
    hyprctl switchxkblayout "$kb" next
  done
  exit 0
fi