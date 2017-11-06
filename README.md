# pyrsc
Python-based ROMs Set Cleaner, to help and clean large ROM sets from undesired ROMs.

The point with this project is to help those who wish to clean their romsets but don't want to bother with learning advanced/complex tools (yet excellent, for most of them), like clrmamepro.

This Python tool tries and provides a lighter/easier way to remove clones, bootlegs and other unwanted ROMs from any large romsets.

Finally note that, though it uses the regular database XML .dat files in input, this tool can also operate on romsets provided wihtout this file, trying to clean based on filenames only. 

## Prerequisites

This project requires to have Python 3 installed on your computer. 

This tool shall be use with non-merged romsets. Dependencies in merged and split romsets are not considered. 

## Getting Started

### Linux

If not already available, you will be likely to install Python like this:
```
$ sudo apt-get update
$ sudo apt-get install python3.6
```

Then simply call pyrsc/pyrsc.py from the command line and start playing with options:
```
python3 pyrsc.py --help
```

### Windows

You will have to download and install the latest Python 3 package from [python.org](https://www.python.org/downloads/windows/)

Then, locate where python.exe was installed, e.g. under: C:\Users\JohnDoe\AppData\Local\Programs\Python\Python36-32, open a command prompt, get there and call pyrsc/pyrsc.py via python.exe:
```
C:\Users\JohnDoe>`
C:\Users\JohnDoe>cd AppData\Local\Programs\Python\Python36-32
C:\Users\JohnDoe\AppData\Local\Programs\Python\Python36-32>python.exe C:\Users\JohnDoe\pyrsc\pyrsc.py --help
```

## How-to?

### Use common options

* --help will display the online help.
* --dry-run will execute a dry-run, nothing will be changed, no file will be deleted.
* --roms-dir is a mandatory option, that is our entry point: the directory holding ROMs to be cleared, with or without subdirectories.
* --dat-file is a an option, that is the regular XML .dat file, related to --roms-dir input directory including ROMs.
* --verbose will let you have more or less information being displaying, to possibly help and understand what is done. 

### Delete files matching patterns

Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --del-files-with="*(PD)* *[o1]* *[o2]* *Prototype*" 
```
Any file in ~/myRoms having "(PD)", "[o1]", etc. in its name will be removed.

### Delete files not matching patterns

Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --del-files-without="*[!]* *.zip*" 
```
Any file in ~/myRoms NOT having "[!]" and ".zip", etc. in its name will be removed.

### Delete fist variants of all ROMs
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --del-first-variants 
```
Consider this case, having the following ROMs under ~/myRoms:
```
...
Balloon Fight (Europe).zip
Balloon Fight (Japan).zip
Balloon Fight (USA).zip
...
```
Applying --del-first-variants will remove the fist 2 variants of this ROM, that is Europe and Japan variants, keeping USA variant.

### Delete last variants of all ROMs
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --del-last-variants 
```
Consider this case, having the following ROMs under ~/myRoms:
```
...
Annals Of Rome (1987)(Magic).zip
Annals Of Rome (1987)(Magic)[a].zip
Annals Of Rome (1987)(Magic)[a2].zip
...
```
Applying --del-last-variants will remove last 2 variants of this ROM, that is [a] and [a2] variants.

### Delete PAL or NTSC variants of all ROMs
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --del-ntsc-versions
```
Consider this case, having the following ROMs under ~/myRoms:
```
...
3-D Tic-Tac-Toe (1978) (Atari) (PAL) [!].a26
3-D Tic-Tac-Toe (1978) (Atari) [!].a26
...
```
Applying --del-ntsc-variants will remove that ROM not having (PAL) pattern, assuming it is an NTSC variant.

Applying --del-pal-variants will remove that ROM having (PAL) pattern and keep the other one, assuming it is NTSC.

### Delete clones of all ROMs
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=mame.dat --del-clones
```
From the input .dat file analysis, this will delete all ROMs being 'romof', 'cloneof' or 'sampleof' other ROMs (except if the parent ROM is a BIOS!).

Consider this MAME database file extract:
```
<game name="1944">
...
</game>
<game name="1944j" cloneof="1944" romof="1944">
...
</game>
<game name="aof" romof="neogeo">
</game>
```
Applying --del-clones will remove 1944j, but will keep 1944, and will also keep aof, as neogeo is a BIOS ROM, not a game ROM. 

### Delete all ROMs having sound samples

Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=mame.dat --del-roms-with-samples
```
From the input .dat file analysis, this will delete all ROMs requiring sample files to get their sound working.

This option will also remove any folder named samples found under ~/myRoms.

### Delete all ROMs older than a given year

Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=mame.dat --del-roms-older-than 1996
```
From the input .dat file analysis, this will delete all ROMs tagged with a date prior 1996.

### Delete all ROMs with description/manufacturer matching patterns 

Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=mame.dat --del-if-description-has "*broken* *bootleg* *hack* *demo* *prototype*"
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=mame.dat --del-if-manufacturer-has "*hack* *bootleg*"
```
From the input .dat file analysis, this will delete all ROMs which description/manufacturer attributes matches the any the input patterns.

Consider this MAME database file extract:
```
<game name="asteroid">
    <description>Asteroids</description>
    ...
</game>
<game name="asteroib" cloneof="asteroid" romof="asteroid">
    <description>Asteroids (bootleg on Lunar Lander hardware)</description>
    ...
</game>
<game name="boggy84">
    <description>Boggy</description>
    <manufacturer>bootleg</manufacturer>
    ...
</game>
```
Applying both --del-if-description-has and  --del-if-manufacturer-has with *bootleg* pattern will remove both asteroib and boggy84.

### Delete all ROMs having given parent BIOS(es)
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=fba.dat --del-if-bios-is "nmk004 ym2608"
```
From the input .dat file analysis, all ROMs which are found having a parent NMK004 or YM2608 BIOS will be removed.

### Delete all ROMs not having given parent BIOS(es)
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/myRoms --dat-file=fba.dat --del-if-bios-isnt "neogeo"
```
From the input .dat file analysis, all ROMs which are found not having a parent NEOGEO BIOS, e.g. having a NMK004 or YM2608 BIOS, will be removed.

### Delete all duplicate ROMs amongst 2 different ROM directories
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/fbaRoms --dat-file=fba.dat --ref-roms-dir=~/mameRoms --del-duplicates
```
From comparing file names and files sizes (but not checksums...), any file in ~/fbaRoms that would be found identical in ~/mameRoms will be removed from ~/fbaRoms.

The input fba.dat is used to identify BIOS files in ~/fbaRoms, to avoid removing them. 

### Flatten a tree-like ROM directory structure
Call pyrsc like this:
```
python3 pyrsc.py --roms-dir=~/fbaRoms --make-flat
```
This will move all files found in ~/fbaRoms subdirectories directly under ~/fbaRoms, then remove all subdirectories.

In case of duplicate names in the tree structure, we do not overwritte files under ~/fbaRoms. When a potential conflict is detected, the file is not moved, subdirectories possibly remain with unmoved/conflictual files inside. 