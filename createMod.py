
import os
import xml.etree.ElementTree as ET
import shutil
import subprocess

XRCatToolPath = "F:\SteamLibrary\steamapps\common\X Tools"           # Path where X Tools is installed.
InputPath =     "F:\SteamLibrary\steamapps\common\X Tools\Extracted" # Path where the extraced cat files are located.
OutputPath =    "F:\SteamLibrary\steamapps\common\X Tools\Mods"      # Path where the modded cat files will be written to.


# Example XML of input file to read returning someValue:
#
#<?xml version="1.0" encoding="utf-8"?>
#<!--Exported by: nick (192.168.3.59) at 14.10.2021_11-17-47-->
#<macros>
# <macro name="storage_par_l_trans_container_03_a_macro" class="storage">
#    <component ref="generic_storage" />
#    <properties>
#      <identification makerrace="paranid" />
#      <cargo max="someValue" tags="container" />
#      <hull integrated="1" />
#    </properties>
#  </macro>
#</macros>
def getCargo(fileName):
    # Parse the XML file
    tree = ET.parse(fileName)
    root = tree.getroot()
    
    # Navigate through the XML structure to find the 'cargo' element
    cargo_element = root.find(".//properties/cargo")
    
    if cargo_element is not None:
        # Get the value of the 'max' attribute
        return int(cargo_element.get('max'))
    else:
        raise(ValueError(f"Did not find a max value for {fileName}"))
    
def incrementVersion(fileName):
    tree = ET.parse(fileName)
    root = tree.getroot()
    currentVersion = int(root.get('version'))
    newVersion = currentVersion + 10
    root.set('version', str(newVersion))    
    tree.write(fileName, encoding='utf-8', xml_declaration=True)
    print(f"Updating to version {newVersion}")


# Example XML of patch file to write:
#
#<?xml version='1.0' encoding='utf-8'?>
#<diff><replace sel="//cargo/@max"><someValue * X></replace></diff>
def writeModFile(path, newMax):
    print(f"Writing to {path}, new cargo {newMax}")
    diff = ET.Element("diff")
    replace = ET.SubElement(diff, "replace", sel="//cargo/@max")
    replace.text = str(newMax)

    output_dir = os.path.dirname(path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create the tree and write to the output file
    tree = ET.ElementTree(diff)
    tree.write(path, encoding='utf-8', xml_declaration=True)

# recursively extract cat files from a directory
def modFiles(inputDir, outputDir, factor):
    for root, dirs, files in os.walk(inputDir):
        for file in files:
            inFilePath = os.path.join(root, file)
            isCargo = getCargo(inFilePath)
            relPath = os.path.relpath(root, inputDir)
            outPath = outputDir
            if relPath != ".":
                outPath = os.path.join(outputDir, relPath)
            outPath= os.path.join(outPath, file)
            writeModFile(outPath, isCargo * factor)

# copy the content.xml file to the mod folder to prepare upload
def copyContentXml(outPath, factor):
    contentFileName = os.path.join(outPath, "content.xml")
    incrementVersion(f"content_{factor}.xml")
    shutil.copy(f"content_{factor}.xml", contentFileName)

# Call XRCatTools to put all the files into ext01.cat file
def zipToCat(outPath):
    outCatFilePath = os.path.join(outPath, "ext_01.cat")
    command = f'"{XRCatToolPath}\XRCatTool.exe" -in "{outPath}" -out "{outCatFilePath}"'
    print(f"Calling {command}")
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)

# Delete all directories in outPath to prepare for upload
def cleanupDirs(outPath):
    for root, dirs, files in os.walk(outPath):
        for dir in dirs:
            path = os.path.join(root, dir)
            if os.path.exists(path):
                print(f"Cleanup of {path}")
                shutil.rmtree(path)

def uploadMod(outpath, factor, changeNote):
    print(f"Uploading mod for factor {factor} from {outpath}")
    command = f'WorkshopTool update -path "{outpath}" -changenote "{changeNote}"'
    print(f"Calling {command}")
    subprocess.call(command, shell=True)

def cleanup(path):
    shutil.rmtree(path)
            
def main():
    changeNote = "Update for TimeLines"
    cleanup(OutputPath)
    for factor in [2,3,5,10]:
        outPath = os.path.join(OutputPath , f"lf_cargo_extension_{factor}")
        if os.path.exists(outPath):
            shutil.rmtree(outPath)
        modFiles(InputPath, outPath, factor)
        copyContentXml(outPath, factor)
        zipToCat(outPath)
        cleanupDirs(outPath)
        #uploadMod(outPath, factor, changeNote)

if __name__ == "__main__":
    main()