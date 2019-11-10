# -*- coding: utf-8 -*-

from tinydb import TinyDB, where, Query

def createStudyTable():
    db = TinyDB('database/db.json')
    tableStudy = db.table('Study')

    tableStudy.insert({'patName': 'Hasta adı', 'patID': '3333', 'patSex':'Cinsiyet', 'patAge':'Yaş',
                   'patBirthdate':'Doğum Tarihi', 'procedure':'Protokol', 'examDate':'Çekim Tarihi', 'origFile':'',
                   'importDatetime':'Yakalama zamanı', 'studyID':'tetkikNo', 'fileSHA':'1234567890', 'modality':'OT',
                   'operatorName':'Teknisyen', 'refPhys':'Gönderen Doktor', 'importTime':'11/04/2016 11:21:00',
                   'sentToPacs':'False', 'senTime':'', 'retries':'0'})
    db.close()

def exist(SHA):
    db = TinyDB('database/db.json')
    tableStudy = db.table('Study')
    study = Query()
    result = tableStudy.contains(study.fileSHA == SHA)
    db.close()
    return result


def testQuery():
    db = TinyDB('database/db.json')
    tableStudy = db.table('Study')
    study = Query()
    pat = tableStudy.search(study.fileSHA == '12345')
    res = pat[0]
    print(res['examDate'])
    db.close()


createStudyTable()
#print exist('123456789') db boşşa hata veriyor, yakala
#testQuery()

#createStudyTable()
