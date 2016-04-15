# -*- coding: utf-8 -*-

import os
import readTags
import subprocess


def createDicom(tempFolder, fileStamp, tagFile, DICOM, TAGS_SINGLE):
    jpegPath = '{}/{}/'.format(tempFolder, fileStamp)
    firstPage = True
    files = next(os.walk(jpegPath))[2]
    if files:
        print('JPEG dosyalar bulundu: '),
        for file in files:
            if file.endswith('jpg'):
                print file
                tagData = readTags.readTagFile(tagFile)
                patName = readTags.getPatName(tagData[TAGS_SINGLE['PatName']])
                patID = readTags.getPatID(tagData[TAGS_SINGLE['PatID']])
                patSex = readTags.getPatSex(tagData[TAGS_SINGLE['PatSex']])
                patAge = readTags.getPatAge(tagData[TAGS_SINGLE['PatAge']], ' ')
                procedure = readTags.getProcedure(tagData[TAGS_SINGLE['Procedure']],TAGS_SINGLE['ProcExamSplitter'])
                examDate, examTime = readTags.getDicomDateTime(tagData[TAGS_SINGLE['ExamDate']],TAGS_SINGLE['ProcExamSplitter'])

                img2dcmCommand = \
'"Util/dcmtk/bin/img2dcm" -i JPEG -l1 --do-checks +i1 +i2 -ll info {}{} {}{}.dcm -k 0010,0010="{}" \
-k 0010,1010="{}" -k 0008,0060="{}" -k 0008,0021="{}" -k 0008,0022="{}" -k 0008,0023="{}" \
-k 0010,0020="{}" -k 0010,0040="{}" -k 0008,0016="{}" -k 0008,0020="{}" -k 0008,0030="{}"  \
-k 0008,1030="{}" -k 0008,103E="{}" -k 0008,0005="{}" -k 0008,0031="{}" -k 0008,0032="{}" \
-k 0008,0033="{}" -k 0008,0070="{}" -k 0008,1090="{}" -k 0008,0080="{}" -k 0008,0081="{}" \
-k 0008,1040="{}" -k 0018,1000="{}" -k 0018,1016="{}" -k 0018,1018="{}" -k 0018,1019="{}"'.format(\
                    jpegPath, file, jpegPath, file, patName, patAge, DICOM['Modality'], examDate, examDate, examDate, patID, patSex, \
                    DICOM['SOPClassUID'], examDate, examTime, procedure, DICOM['SeriesDescription'], DICOM['CharacterSet'], \
                    examTime, examTime, examTime, DICOM['Manufacturer'], DICOM['ManufacturersModelName'], DICOM['InstitutionName'],\
                    DICOM['InstitutionAddress'], DICOM['DepartmentName'], DICOM['DeviceSerialNumber'],\
                    DICOM['SecondaryCaptureDeviceManufacturer'], DICOM['SecondaryCaptureDeviceModel'], \
                    DICOM['SecondaryCaptureDeviceSoftwareVersion'])

                print img2dcmCommand
                process = subprocess.Popen(img2dcmCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                print ('output: %s', output)
                print ('error: %s', error)
                return error

def decompressJpegs(dcmtk, tempFolder, fileStamp):
    # dcmdjpeg -f Temp/c255e9d518c1896b26115e696a6354bda163d486/Page00.jpg.dcm Temp/c255e9d518c1896b26115e696a6354bda163d486/dumpPage00.dcm
    dicomPath = '{}/{}/'.format(tempFolder, fileStamp)
    firstPage = True
    files = next(os.walk(dicomPath))[2]
    if files:
        print('Sıkıştırılmış dicom dosyaları bulundu: '),
        for file in files:
            if file.endswith('jpg.dcm'):
                print file
                dcmdjpgcommand = '"{}/dcmdjpeg.exe" -f {}{} {}dump{}'.format(dcmtk, dicomPath, file, dicomPath, file)
                print (dcmdjpgcommand)
                process = subprocess.Popen(dcmdjpgcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                print ('output: %s', output)
                print ('error: %s', error)
                return error

def sendtopacs(root, dcmtk, tempFolder, fileStamp, PACS, TAGS_SINGLE):
    storescucommand = '"{}/storescu.exe" -aet {} {} -aec {} {} +sd "{}/{}/*.dcm" +sp "dump*.jpg.dcm" {}'\
    .format(dcmtk, PACS['AET'], PACS['Address'], PACS['AEC'], PACS['Port'], tempFolder, fileStamp, PACS['ScuParams'])
    print storescucommand
    # storescucommand.replace('/', '\\')
    process = subprocess.Popen(storescucommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    print ('output: %s', output)
    print ('error: %s', error)
    return error