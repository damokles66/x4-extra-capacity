# This script will unpack a number of cat files using the command
# lineTool -in <fullPathToCatFile> -out <fullPathToOutputDirectory> -include <pattern>
# The cat files are located in multiple directories like:
# data/a1.cat
# data/a2.cat
# data/extensions/<extensionName>/a1.cat
# data/<someDir>/a1.cat
# data/<someDir2>/<someDir3>/a1.cat
# and so on
#
# And they should be extracted keeping the same directory structure.

import os
import subprocess
import shutil
import xml.etree.ElementTree as ET


def hasCargo(fileName):
    # Parse the XML file
    tree = ET.parse(fileName)
    root = tree.getroot()
    
    # Navigate through the XML structure to find the 'cargo' element
    cargo_element = root.find(".//properties/cargo")    
    return cargo_element is not None

# Example XML of patch file to write:
#
#<?xml version='1.0' encoding='utf-8'?>
#<diff><replace sel="//cargo/@max"><someValue * X></replace></diff>
def writeModFile(path, newMax):
    print(f"Writing to {path}, new cargo {newMax}")
    diff = ET.Element("diff")
    replace = ET.SubElement(diff, "replace", sel="//cargo/@max")
    replace.text = str(newMax)

    # Create the tree and write to the output file
    tree = ET.ElementTree(diff)
    tree.write(path, encoding='utf-8', xml_declaration=True)

# recursively delete all files without cargo value
def clearFiles(inputDir):
    for root, dirs, files in os.walk(inputDir):
        for file in files:
            inFilePath = os.path.join(root, file)
            if not hasCargo(inFilePath):
                print(f"Removed {inFilePath} as no cargo value is found!")
                os.remove(inFilePath)

# recursively extract cat files from a directory
def extractCatFiles(inputDir, outputDir):
    for root, dirs, files in os.walk(inputDir):
        for file in files:
            if file.endswith('.cat') and not file.endswith('sig.cat'):
                extractCatFile(inputDir, root, file, outputDir)

def extractCatFile(inputDir, root, catFile, outputDir):
    relPath = os.path.relpath(root, inputDir)
    catFilePath = os.path.join(root, catFile)
    outPath = outputDir
    if relPath != ".":
        outPath = os.path.join(outputDir, relPath)
        
    print(f"Extracting {catFilePath} to {outPath}")
    if not os.path.exists(outPath):
        os.makedirs(outPath)
    command = f'XRCatTool.exe -in "{catFilePath}" -out "{outPath}" -include storage_.*_l_.*macro.xml -exclude .*_l_liquid.* .*_l_container.* .*_l_solid.*'
    print(f"Calling {command}")
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)

def remove_empty_dirs(path):
    # Walk the directory tree from the bottom up
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # Check if the directory is empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Removed empty directory: {dir_path}")

def main():

    inputPath = "D:\Spiele\Steam\steamapps\common\X4 Foundations"
    outputPath = "F:\SteamLibrary\steamapps\common\X Tools\Extracted"
    if os.path.exists(outputPath):
        shutil.rmtree(outputPath)

    extractCatFiles(inputPath, outputPath)
    clearFiles(outputPath)
    remove_empty_dirs(outputPath)

if __name__ == "__main__":
    main()