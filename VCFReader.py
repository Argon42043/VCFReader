import os
import re
import vobject
from fpdf import FPDF

def fileName():
    """Asking for the filename which should be read.
    Returns:
        String: Filename with whole path
        String: Only filename
    """
    print('Which file?')
    filename = input()
    dir = os.getcwd()
    return str(os.path.join(dir, filename)), filename

def checkFile(path):
    """Checking if filename or path is correct.
    Args:
        path (string): path with file name 
    Returns:
        Bool: if everything is correct or not
    """
    print('Is this the correct name of the file? Yes -> Y/y')
    answer = input()
    if not os.path.isfile(path):
        print('Filename wrong or file does not exist!')
        return True
    if (answer == 'y' or answer == 'Y'):
        return False
    else:
        print("You entered that the file name is not correct!")
        return True

def removeSymbols(String):
    """Remove unnecessary ASCII from string

    Args:
        String (string): get string of the vcf file

    Returns:
        string: get the new finished and clean string
    """
    if "TEL" in String:
        String = String.replace("TEL", "")
    if "FN" in String:
        String = String.replace("FN", "")
    if "EMAIL" in String:
        String = String.replace("EMAIL", "")
    if "BDAY" in String:
        String = String.replace("BDAY", "")
    if "ADR" in String:
        String = String.replace("ADR", "")
        String = String.replace("\\n", "")
    if "CHARSET" in String:
        String = String.replace("CHARSET", "")
    if "UTF-8" in String:
        String = String.replace("UTF-8", "")
    String = re.sub(r'[\[<\{\'\'\:\}>\]]', r'', String)
    String = String.lstrip()
    return String

def checkLineStart(element):
    element = str(element).split("\n")
    count = 0
    arrDelete = []
    for line in element:
        if str(line).startswith("(") or ";;;;" == str(line):
            arrDelete.append(count)
            count = count - 1
        count = count + 1
    for line in arrDelete:
        element.pop(line)
    element = "\n".join(element)
    return element

def readVCFFile(file):
    """Reading the VCF File and format it.
    Args:
        file (string): name of the file
    Returns:
        informationArray (nested list): all contacts with information (Tel, Mail, Bday)
    """
    with open (file, 'r') as fileSource:
        fileText = fileSource.read()
    
    fileText = re.sub(r'(END:VCARD)', r'\1~', fileText)

    listText = fileText.split('~')

    informationArray = []
    countInformationArray = 0

    for elements in listText:
        if 'BEGIN:VCARD' in elements:
            if "ADR;X-CUSTOM" in elements:
                elements = elements.split("\n")
                count = 0
                for line in elements:
                    if "ADR;X-CUSTOM" in line:
                        elements.pop(count)
                        print(elements[count + 1])
                        if elements[count + 1] != 'FN' or elements[count + 1] != 'TEL' or elements[count + 1] != 'EMAIL' or elements[count + 1] != 'N' or elements[count + 1] != 'X-SAMSUNGADR' or elements[count + 1] != 'BDAY' or elements[count + 1] != 'END' or elements[count + 1] != 'ADR' or elements[count + 1] != 'URL' or elements[count + 1] != 'NOTE':
                            elements.pop(count)
                    count = count + 1    
                elements = "\n".join(elements)
            if "TEL;X-CUSTOM" in elements:
                elements = re.sub("TEL;X-CUSTOM\([a-z, A-Z, 0-9, \=, \-, \,, \;, \), \:, \\\n]*\):", "TEL;CELL:", elements)
            elements = checkLineStart(elements)
            print(elements)
            read = vobject.readOne(elements, allowQP=True)
            count = 1
            readArray = []
            if 'FN' in str(read):
                FN = str(read.contents['fn'])
                FN = removeSymbols(FN)
                readArray.insert(0, FN)
            if 'TEL' in str(read):
                TEL = str(read.contents['tel'])
                TEL = removeSymbols(TEL)
                readArray.insert(count, TEL)
                count = count + 1
            if 'EMAIL' in str(read):
                EMAIL = str(read.contents['email'])
                EMAIL = removeSymbols(EMAIL)
                readArray.insert(count, EMAIL)
                count = count + 1
            if 'BDAY' in str(read):
                BDAY = str(read.contents['bday'])
                BDAY = removeSymbols(BDAY)
                readArray.insert(count, BDAY)
                count = count + 1
            if 'ADR' in str(read) and not 'X-SAMSUNGADR' in str(read):
                ADR = str(read.contents['adr'])
                ADR = removeSymbols(ADR)
                readArray.insert(count, ADR)
                count = count + 1

            print(readArray)
            countInformationArray = countInformationArray + 1
            informationArray.insert(countInformationArray, readArray)
    return informationArray

def sort(list):
    """Sort list

    Args:
        list (list): unsorted list

    Returns:
        list: sorted list
    """
    sortedList = sorted(list)
    return sortedList

def writeTextFile(list):
    """Write to file

    Args:
        list (list): get list to write in file

    Returns:
        txtFileName: String of filename
    """
    txtFileName = "Contacts.txt"
    with open(txtFileName, "w") as txtFile:
        txtFile.write("Name:\t\t\t\tTel:\t\t\t\tBDay/EMail/Adress:\n")
        for contacts in list:
            for item in contacts:
                txtFile.write("%s\t\t\t\t" % item)
            txtFile.write("\n")
    return txtFileName

def writePDFFile(txtFile):
    """Write txt file to pdf

    Args:
        txtFile (string): name of txt file
    """
    pdf = FPDF(orientation = 'L')
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    if os.path.exists(txtFile):
        with open(txtFile, "r") as txtFile:
            for lines in txtFile:
                lines = lines.replace("\t", " ")
                pdf.cell(50, 10, txt = lines, border=30, ln = 2, align = 'L')
        pdf.output("Contacts.pdf")
    else:
        print("Text file, which is needed for copying to pdf, was not found!")

def deleteTxtFile(txtFileName):
    """deleting text file

    Args:
        txtFileName (string): name of textfile
    """
    if os.path.exists(txtFileName):
        os.remove(txtFileName)
    else:
        print("File not exist, can not delete!")

def main():
    """Main of VCFReader"""
    print("Put the contact file in the same directory as the python script!")

    loopCondition = True
    try:
        while loopCondition:
            path, filename = fileName()
            loopCondition = checkFile(path)
    except:
       print("Error during user input or finding file.") 
    
    print("Read VCF file!")
    #try:
    contactList = readVCFFile(filename)
    #except:
    #    print("Error during reading VCF file, have you installed the needed packages?")
    print("Sort contacts on list")
    try:
        contactList = sort(contactList)
    except:
        print("Error during sorting elements.")

    print("Do you want to write result also in an pdf file? Yes -> Y/y")
    try:
        answer = input()
    except:
        print("Error during user input.")

    print("Write to text file.")
    try:
        txtFileName = writeTextFile(contactList)
    except:
        print("Error during writing on file.")
    
    if answer == "y" or answer == "Y":
        loopCondition = False
        print("Write to pdf file.")
        try:
            writePDFFile(txtFileName)
        except:
            print("Error during writing pdf file")

        print("Delete text file")
        try:
            deleteTxtFile(txtFileName)
        except:
            print("Error during deleting txt file.")
        
    print("Done!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping programm!")