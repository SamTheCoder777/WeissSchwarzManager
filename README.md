# Weiss Schwarz Manager

## Description

Simple tool for quickly getting Japanese deck prices / playset prices from yuyutei\
Also works for single card

## Getting Started

### Dependencies

* Windows

### Installing

* Download latest release and unzip it

### Executing program

* shift + right click 
* Select open powershell here
* You can also choose to manually open cmd and cd into the folder

```
-h, --help            show this help message and exit
-i {codes,encore}, --import_type {codes,encore}
                    card list format (code or blake) Codes: file with card codes separated by new lines\encore:
                    Card deck txt file exported and saved from encoredecks.com
-f FILE, --file FILE  card list file path
-c CODE, --code CODE  Set code
-sc SINGLECARD, --singlecard SINGLECARD
                    Single card code
-s SCALE, --scale SCALE
                    set scale to the price
-p, --playset         calculate playset price
```

## Help

In these examples, I am using nik (Nikke)

search single price
```
.\WeissSchwarzManager.exe -sc NIK/S117-020 -c nik
```

txt file where card codes separated by newline 
```
.\WeissSchwarzManager.exe -f '.\codes.txt' -c nik -i codes
```

txt file exported from encoredecks.com
```
.\WeissSchwarzManager.exe -f '..\BCS 2026 Mouvaux Nikke 4 door_4 standby.txt' -c nik -i encore
```

playset
```
.\WeissSchwarzManager.exe -c nik -p
```

you can also choose to set scale for prices
```
.\WeissSchwarzManager.exe -f '.\codes.txt' -c nik -i codes -s 0.7

.\WeissSchwarzManager.exe -f '..\BCS 2026 Mouvaux Nikke 4 door_4 standby.txt' -c nik -i encore -s 0.7

.\WeissSchwarzManager.exe -c nik -p -s 0.7
```

## FAQ
I keep getting this error: **AttributeError: 'NoneType' object has no attribute 'replace'**:\
Please double check if your file path is correct

## License

This project is licensed under the Apache-2.0 License - see the LICENSE.md file for details