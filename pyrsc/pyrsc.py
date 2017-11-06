import os
import os.path
import shutil
import sys
import re
from optparse import OptionParser
from xml.etree import ElementTree

__all__ = []
__version__ = 1.0
__date__ = '2017-11-03'
__updated__ = '2017-11-03'
program_long_desc = 'This program generates cleans ROM sets from undesired ROMs'

# Default log level
LOG_LEVEL = 1

# Dry run mode
IS_DRY_RUN = False

# Required Python version
REQUIRED_PYTHON_VERSION = 3


# Just show log message on STDERR, if log level is enough
def log(level, message):

    if LOG_LEVEL >= level:
        sys.stdout.flush()
        sys.stderr.write(message + '\n')
        sys.stderr.flush()


def make_flat(path_to_roms_dir):

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        if os.path.basename(dirname) != os.path.basename(path_to_roms_dir):
            for filename in filenames:
                full_path = os.path.join(dirname, filename)
                if IS_DRY_RUN:
                    log(2, "Would move up file: " + full_path)
                else:
                    log(2, "Moving up file: " + full_path)
                    shutil.move(full_path, path_to_roms_dir)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        if os.path.basename(dirname) != os.path.basename(path_to_roms_dir):
            if IS_DRY_RUN:
                log(1, "Would remove directory: " + dirname)
            else:
                print("Removing directory: " + dirname)
                shutil.rmtree(dirname, ignore_errors=True)

    return 0


def check_and_get_list(list_string):

    list = []

    matches = re.search(r"^(\*[^\*]+\*\s*)+$", list_string)
    if not matches:
        log(1, "ERROR: badly formatted input list of patterns; shall be like \"*pattern1* *pattern2*\"")
    else:
        matches = re.findall(r"\*[^\*]+\*", list_string)
        if not matches:
            log(1, "ERROR: badly formatted input list of patterns; shall be like \"*pattern1* *pattern2*\"")
        else:
            for match in matches:
                pattern = match.replace("*", "")
                log(2, "Adding pattern: '" + pattern + "'")
                list.append(pattern)

    return list


def get_bioses_from_roms_and_dat(path_to_roms_dir, path_to_dat_file):

    bios_list = []

    file = open(path_to_dat_file, 'r')
    tree = ElementTree.parse(file)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            rom = filename.split(".")[0]
            nodes = tree.findall('.//game[@name="' + rom + '"]')
            if len(nodes) != 0:
                is_bios = nodes[0].attrib.get("isbios")
                if is_bios:
                    log(2, "Found BIOS ROM: " + rom)
                    bios_list.append(rom)

    return bios_list


def del_files_without(path_to_roms_dir, inclusion_list_string):

    log(0, "\nRemoving files with name NOT matching all of input patterns...\n")

    inclusion_list = check_and_get_list(inclusion_list_string)

    if not inclusion_list:
        return 2

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            for pattern in inclusion_list:
                if not pattern.lower() in filename.lower():
                    full_name = os.path.join(dirname, filename)
                    if IS_DRY_RUN:
                        log(1, "Would delete: " + filename)
                    else:
                        log(1, "Deleting: " + filename)
                        os.remove(full_name)
                    break;

    return 0


def del_files_with(path_to_roms_dir, exclusion_list_string):

    log(0, "\nRemoving files with name matching any of input patterns...\n")

    exclusion_list = check_and_get_list(exclusion_list_string)

    if not exclusion_list:
        return 2

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            for pattern in exclusion_list:
                if pattern.lower() in filename.lower():
                    full_name = os.path.join(dirname, filename)
                    if IS_DRY_RUN:
                        log(1, "Would delete: " + filename)
                    else:
                        log(1, "Deleting: " + filename)
                        os.remove(full_name)
                    break;

    return 0


def del_pal_or_ntsc_files(path_to_roms_dir, del_ntsc_versions):

    if del_ntsc_versions:
        log(0, "\nRemoving NTSC versions of ROMs...\n")
    else:
        log(0, "\nRemoving PAL versions of ROMs...\n")

    files_list = []

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            file_attributes = {}
            file_attributes['parent_dir'] = dirname
            file_attributes['name'] = filename
            file_attributes['rom'] = filename.split("(")[0].strip().lower()
            file_attributes['full_name'] = os.path.join(dirname, filename)
            file_attributes['to_be_deleted'] = False
            if '(PAL' in filename:
                file_attributes['is_pal'] = True
            elif '(NTSC' in filename:
                file_attributes['is_pal'] = False
            # In case nor PAL and NTSC is showing up, assume the ROM is NTSC
            else:
                file_attributes['is_pal'] = False
            files_list.append(file_attributes)

    for file in files_list:
        for file2 in files_list:
            if file['parent_dir'] == file2['parent_dir']:
                if file['name'] == file2['name']:
                    break
                else:
                    if file['rom'] == file2['rom']:
                        if file['is_pal'] and not file2['is_pal']:
                            if del_ntsc_versions:
                                file2['to_be_deleted'] = True
                            else:
                                file['to_be_deleted'] = True
                            break

    for file in files_list:
        if file['to_be_deleted']:
            if IS_DRY_RUN:
                log(1, "Would delete: " + file['name'])
            else:
                log(1, "Deleting: " + file['name'])
                os.remove(file['full_name'])

    return 0


def del_variant_files(path_to_roms_dir, del_first_variants):

    if del_first_variants:
        log(0, "\nRemoving first variants of ROMs...\n")
    else:
        log(0, "\nRemoving last variants of ROMs...\n")

    files_list = []

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            file_attributes = {}
            file_attributes['parent_dir'] = dirname
            file_attributes['name'] = filename
            file_attributes['rom'] = filename.split("(")[0].strip().lower()
            file_attributes['full_name'] = os.path.join(dirname, filename)
            file_attributes['to_be_deleted'] = False
            files_list.append(file_attributes)

    for file in files_list:
        for file2 in files_list:
            if file['parent_dir'] == file2['parent_dir']:
                if file['name'] == file2['name']:
                    break
                else:
                    if file['rom'] == file2['rom'] and not file2['to_be_deleted']:
                        if del_first_variants:
                            file2['to_be_deleted'] = True
                        else:
                            file['to_be_deleted'] = True
                        break

    for file in files_list:
        if file['to_be_deleted']:
            if IS_DRY_RUN:
                log(1, "Would delete: " + file['name'])
            else:
                log(1, "Deleting: " + file['name'])
                os.remove(file['full_name'])

    return 0


def del_duplicates(path_to_roms_dir, path_to_dat_file, path_to_reference_roms_dir):

    log(0, "\nRemoving duplicates in alternate ROMs directory...\n")

    # Get any BIOS ROM found in the input ROMs directory, to prevent removing them
    bios_list = get_bioses_from_roms_and_dat(path_to_roms_dir, path_to_dat_file)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            for dirname2, dirnames2, filenames2 in os.walk(path_to_reference_roms_dir):
                for filename2 in filenames2:
                    if filename == filename2:
                        full_name = os.path.join(dirname, filename)
                        size = os.path.getsize(full_name)
                        full_name2 = os.path.join(dirname2, filename2)
                        size2 = os.path.getsize(full_name2)
                        if filename.split(".")[0] in bios_list:
                            if IS_DRY_RUN:
                                log(2, "Would keep BIOS: " + full_name2)
                            else:
                                log(2, "Keeping BIOS: " + full_name2)
                        elif size == size2:
                            if IS_DRY_RUN:
                                log(1, "Would remove " + full_name + ", duplicate of " + full_name2)
                            else:
                                log(1, "Removing " + full_name + ", duplicate of " + full_name2)
                                os.remove(full_name)

    return 0


def del_roms_clones(path_to_roms_dir, path_to_dat_file):

    log(0, "\nRemoving clones of ROMs...\n")

    # Get any BIOS ROM found in the input ROMs directory, to prevent removing them
    bios_list = get_bioses_from_roms_and_dat(path_to_roms_dir, path_to_dat_file)

    file = open(path_to_dat_file, 'r')
    tree = ElementTree.parse(file)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            rom = filename.split(".")[0]
            nodes = tree.findall('.//game[@name="' + rom + '"]')
            if len(nodes) != 0:
                rom_of = nodes[0].attrib.get("romof")
                clone_of = nodes[0].attrib.get("cloneof")
                sample_of = nodes[0].attrib.get("sampleof")
                if (rom_of and rom_of not in bios_list) or clone_of or sample_of:
                    full_name = os.path.join(dirname, filename)
                    if IS_DRY_RUN:
                        log(1, "Would remove " + full_name)
                    else:
                        log(1, "Removing " + full_name)
                        os.remove(full_name)

    return 0


def del_roms_with_samples(path_to_roms_dir, path_to_dat_file):

    log(0, "\nRemoving ROMs with samples...\n")

    file = open(path_to_dat_file, 'r')
    tree = ElementTree.parse(file)

    roms_with_samples = []

    for sample in tree.findall('game/sample/..'):
        rom = sample.attrib.get("name")
        roms_with_samples.append(rom)

    log(2, "ROMs with samples: " + str(roms_with_samples))

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            rom = filename.split(".")[0]
            if rom in roms_with_samples:
                full_name = os.path.join(dirname, filename)
                if IS_DRY_RUN:
                    log(1, "Would remove " + full_name)
                else:
                    log(1, "Removing " + full_name)
                    os.remove(full_name)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        if os.path.basename(dirname) == "samples":
            if IS_DRY_RUN:
                log(1, "Would remove samples directory: " + dirname)
            else:
                log(1, "Removing samples directory: " + dirname)
                shutil.rmtree(dirname, ignore_errors=True)

    return 0


def del_if_description_has(path_to_roms_dir, path_to_dat_file, exclusion_list_string):

    log(0, "\nRemoving files with description matching any of input patterns...\n")

    exclusion_list = check_and_get_list(exclusion_list_string)

    if not exclusion_list:
        return 2

    file = open(path_to_dat_file, 'r')
    tree = ElementTree.parse(file)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            rom = filename.split(".")[0]
            element = tree.findall('.//game[@name="' + rom + '"]/description')
            if element:
                description = element[0].text
                for pattern in exclusion_list:
                    if pattern.lower() in description.lower():
                        full_name = os.path.join(dirname, filename)
                        if IS_DRY_RUN:
                            log(1, "Would delete: " + filename + " (\"" + description + "\")")
                        else:
                            log(1, "Deleting: " + filename + " (\"" + description + "\")")
                            os.remove(full_name)
                        break

    return 0


def del_if_manufacturer_has(path_to_roms_dir, path_to_dat_file, exclusion_list_string):

    log(0, "\nRemoving files with manufacturer matching any of input patterns...\n")

    exclusion_list = check_and_get_list(exclusion_list_string)

    if not exclusion_list:
        return 2

    file = open(path_to_dat_file, 'r')
    tree = ElementTree.parse(file)

    for dirname, dirnames, filenames in os.walk(path_to_roms_dir):
        for filename in filenames:
            rom = filename.split(".")[0]
            element = tree.findall('.//game[@name="' + rom + '"]/manufacturer')
            if element:
                manufacturer = element[0].text
                for pattern in exclusion_list:
                    if pattern.lower() in manufacturer.lower():
                        full_name = os.path.join(dirname, filename)
                        if IS_DRY_RUN:
                            log(1, "Would delete: " + filename + " (\"" + manufacturer + "\")")
                        else:
                            log(1, "Deleting: " + filename + " (\"" + manufacturer + "\")")
                            os.remove(full_name)
                        break

    return 0


def main(argv=None):

    global LOG_LEVEL
    global IS_DRY_RUN
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%1.1f" % __version__
    program_build_date = "%s" % __updated__
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_usage = 'usage: %prog [-h] [--verbose=INT] [--dry-run] --roms-dir=STRING [--dat-file=STRING]\n' \
                    '       *** Cleaning based on file names\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-files-with=STRING] [--del-files-without=STRING]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-first-variants] [--del-last-variants]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-ntsc-versions] [--del-pal-versions]\n' \
                    '       *** Cleaning based on .dat file analysis\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-roms-clones]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-roms-with-samples]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-if-description-with=STRING]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-if-manufacturer-with=STRING]\n' \
                    '       *** Other utilities\n' \
                    '       ' + len(program_name) * ' ' + ' [--make-flat]\n' \
                    '       ' + len(program_name) * ' ' + ' [--del-duplicates --ref-roms-dir=STRING]\n'

    # Check python version is the minimum expected one
    if sys.version_info[0] < REQUIRED_PYTHON_VERSION:
        log(1, "ERROR: this tool requires at least Python version " + REQUIRED_PYTHON_VERSION)
        sys.exit(2)

    # Setup options
    if argv is None:
        argv = sys.argv[1:]

    try:
        # Setup options parser
        parser = OptionParser(usage=program_usage,
                              version=program_version_string,
                              epilog=program_long_desc)
        parser.add_option("-v",
                          "--verbose",
                          action="store",
                          dest="verbose",
                          help="set verbose level [default: %default]",
                          metavar="INT")
        parser.add_option("-y",
                          "--dry-run",
                          action="store_true",
                          dest="is_dry_run",
                          help="execute dry-run, no file will be deleted")
        parser.add_option("-r",
                          "--roms-dir",
                          action="store",
                          dest="roms_dir",
                          help="input directory, including ROM files to be cleaned",
                          metavar="STRING")
        parser.add_option("-d",
                          "--dat-file",
                          action="store",
                          dest="dat_file",
                          help="Optional XML .dat file, related to the input directory including ROMs",
                          metavar="STRING")
        parser.add_option("-m",
                          "--make-flat",
                          action="store_true",
                          dest="make_flat",
                          help="remove any intermediate directory; move all files to the ROMs base directory")
        parser.add_option("-w",
                          "--del-files-with",
                          action="store",
                          dest="del_files_with_string",
                          help="delete files matching any of the provided string patterns",
                          metavar="STRING")
        parser.add_option("-o",
                          "--del-files-without",
                          action="store",
                          dest="del_files_without_string",
                          help="delete files NOT matching all of the provided string patterns",
                          metavar="STRING")
        parser.add_option("-f",
                          "--del-first-variants",
                          action="store_true",
                          dest="del_first_variants",
                          help="in case variants of a ROM are found, delete first variants & keep last")
        parser.add_option("-l",
                          "--del-last-variants",
                          action="store_true",
                          dest="del_last_variants",
                          help="in case variants of a ROM are found, delete last variants & keep first")
        parser.add_option("-n",
                          "--del-ntsc-versions",
                          action="store_true",
                          dest="del_ntsc_versions",
                          help="in case NTSC version of a PAL ROM is found, delete this NTSC last version & keep PAL one")
        parser.add_option("-p",
                          "--del-pal-versions",
                          action="store_true",
                          dest="del_pal_versions",
                          help="in case PAL version of a NTSC ROM is found, delete this PAL last version & keep NTSC one")
        parser.add_option("-u",
                          "--del-duplicates",
                          action="store_true",
                          dest="del_duplicates",
                          help="in case duplicates of ROMs in input directory are found in a reference directory, delete those duplicates")
        parser.add_option("-e",
                          "--ref-roms-dir",
                          action="store",
                          dest="reference_roms_dir",
                          help="reference input directory, including ROM files",
                          metavar="STRING")
        parser.add_option("-c",
                          "--del-roms-clones",
                          action="store_true",
                          dest="del_roms_clones",
                          help="from input .dat file analysis, delete all ROMs being 'romof', 'cloneof' or 'sampleof' other ROMs")
        parser.add_option("-s",
                          "--del-roms-with-samples",
                          action="store_true",
                          dest="del_roms_with_samples",
                          help="from input .dat file analysis, delete all ROMs using sound samples; also delete all samples directories")
        parser.add_option("-i",
                          "--del-if-description-has",
                          action="store",
                          dest="del_if_description_has_string",
                          help="from input .dat file analysis, delete all ROMs with description field matching any of the provided string patterns",
                          metavar="STRING")
        parser.add_option("-j",
                          "--del-if-manufacturer-has",
                          action="store",
                          dest="del_if_manufacturer_has_string",
                          help="from input .dat file analysis, delete all ROMs with manufacturer field matching any of the provided string patterns",
                          metavar="STRING")

        # Set defaults
        parser.set_defaults(verbose=str(LOG_LEVEL))

        # Process options
        (opts, args) = parser.parse_args(argv)

        LOG_LEVEL = int(opts.verbose)
        log(2, "Verbosity level = %s" % opts.verbose)

        if opts.is_dry_run:
            IS_DRY_RUN = True
        else:
            IS_DRY_RUN = False
        log(2, "Dry-run mode    = %s" % str(IS_DRY_RUN))

        # Check some of the options
        if not opts.roms_dir:
            log(1, "ERROR: missing input path to ROMs directory. Try --help")
            return 2

        if not os.path.isdir(opts.roms_dir):
            log(1, "ERROR: " + opts.roms_dir + " directory not found")
            return 2

        if opts.dat_file and not os.path.isfile(opts.dat_file):
            log(1, "ERROR: " + opts.dat_file + " file not found")
            return 2

        if opts.del_duplicates and not opts.reference_roms_dir:
            log(1, "ERROR: setting --del-duplicates requires --ref-roms-dir to be also set")
            return 2

        if opts.reference_roms_dir and not os.path.isdir(opts.reference_roms_dir):
            log(1, "ERROR: " + opts.reference_roms_dir + " directory not found")
            return 2

        if opts.del_duplicates and not opts.dat_file:
            log(1, "ERROR: setting --del-duplicates requires --dat-file to be also set")
            return 2

        if opts.del_roms_clones and not opts.dat_file:
            log(1, "ERROR: setting --del-roms-clones requires --dat-file to be also set")
            return 2

        if opts.del_if_description_has_string and not opts.dat_file:
            log(1, "ERROR: setting --del-if-description-has requires --dat-file to be also set")
            return 2

        if opts.del_if_manufacturer_has_string and not opts.dat_file:
            log(1, "ERROR: setting --del-if-manufacturer-has requires --dat-file to be also set")
            return 2

        if opts.dat_file and not os.path.isfile(opts.dat_file):
            log(1, "ERROR: " + opts.dat_file + " file not found")
            return 2

    except Exception as error:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(error) + "\n")
        sys.stderr.write(indent + " for help use --help\n")
        return 2

    if opts.make_flat:
        status = make_flat(opts.roms_dir)
        if status != 0:
            return status

    if opts.del_files_without_string:
        status = del_files_without(opts.roms_dir, opts.del_files_without_string)
        if status != 0:
            return status

    if opts.del_files_with_string:
        status = del_files_with(opts.roms_dir, opts.del_files_with_string)
        if status !=0:
            return status

    if opts.del_ntsc_versions:
        status = del_pal_or_ntsc_files(opts.roms_dir, True)
        if status !=0:
            return status

    if opts.del_pal_versions:
        status = del_pal_or_ntsc_files(opts.roms_dir, False)
        if status !=0:
            return status

    if opts.del_first_variants:
        status = del_variant_files(opts.roms_dir, True)
        if status !=0:
            return status

    if opts.del_last_variants:
        status = del_variant_files(opts.roms_dir, False)
        if status != 0:
            return status

    if opts.del_duplicates:
        status = del_duplicates(opts.roms_dir, opts.dat_file, opts.reference_roms_dir)
        if status != 0:
            return status

    if opts.del_roms_clones:
        status = del_roms_clones(opts.roms_dir, opts.dat_file)
        if status != 0:
            return status

    if opts.del_roms_with_samples:
        status = del_roms_with_samples(opts.roms_dir, opts.dat_file)
        if status != 0:
            return status

    if opts.del_if_description_has_string:
        status = del_if_description_has(opts.roms_dir, opts.dat_file, opts.del_if_description_has_string)
        if status != 0:
            return status

    if opts.del_if_manufacturer_has_string:
        status = del_if_manufacturer_has(opts.roms_dir, opts.dat_file, opts.del_if_manufacturer_has_string)
        if status != 0:
            return status

# Module run in main mode
if __name__ == "__main__":
    sys.exit(main())
