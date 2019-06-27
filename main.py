import xlrd
import json
from django.core.management import BaseCommand
from django.db.models import F
from bs4 import BeautifulSoup;
import requests;
from univerlist_app.models import Department, Language, University, Teogs, Province


class Command(BaseCommand):

    def handle(self, *args, **options):
        #self.createJson()
        Teogs.objects.all().delete()
        self.readPdf2019tablo4()

    def createJson(self,):
        class School(object):

            def __init__(self, okul_adi, province, ilce, okul_turu, alan_adi, ogrenim_sure, ogrenim_sekli, yabanci_dili,
                         kont, taban1, taban2):
                self.okul_adi = okul_adi
                self.province = province
                self.ilce = ilce
                self.okul_turu = okul_turu
                self.alan_adi = alan_adi
                self.ogrenim_sure = ogrenim_sure
                self.ogrenim_sekli = ogrenim_sekli
                self.yabanci_dili = yabanci_dili
                self.kont = kont
                self.taban1 = taban1
                self.taban2 = taban2

        province = Province.objects.all()

        #burdaki methodlar constructırın içine gidiyor bu methodlarda tablonun 8'lik mi 9'luk bu olduğu kontrol ediliyor
        #çünkü illerdeki bazı tablolar 8'lik ona göre shifting yapıyor bu shiftingten etkilenenlerin paramlarında
        #nine var ona göre checkliyor

        def okul_adi_controll(schoolInfo):
            if schoolInfo.split('\n')[1].split('/')[1] == '':
                return None
            else:
                return schoolInfo.split('\n')[1].split('/')[1]

        def ilce_controll(schoolInfo):
            if schoolInfo.split('\n')[1].split('/')[0] == '':
                return None
            else:
                return schoolInfo.split('\n')[1].split('/')[0]

        def okul_turu_controll(schoolInfo):
            if schoolInfo.split('\n')[2] == '':
                return None
            else:
                return schoolInfo.split('\n')[2]

        def alan_adi_controll(schoolInfo, nine):
            if nine == 0:
                return None
            else:
                if schoolInfo.split('\n')[3] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[3]

        def ogrenim_sure_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[3] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[3]
            else:
                if schoolInfo.split('\n')[4] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[4]

        def ogrenim_sekli_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[4] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[4]
            else:
                if schoolInfo.split('\n')[5] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[5]

        def yabanci_dili_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[5] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[5]
            else:
                if schoolInfo.split('\n')[6] == '':
                    return None
                else:
                    return schoolInfo.split('\n')[6]

        def kont_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[6] == '':
                    return None
                else:
                    return int(schoolInfo.split('\n')[6])
            else:
                if schoolInfo.split('\n')[7] == '':
                    return None
                else:
                    return int(schoolInfo.split('\n')[7])

        def taban1_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[7] == '':
                    return None
                else:
                    return float(schoolInfo.split('\n')[7].replace(',', '.'))
            else:
                if schoolInfo.split('\n')[8] == '':
                    return None
                else:
                    return float(schoolInfo.split('\n')[8].replace(',', '.'))

        def taban2_controll(schoolInfo, nine):
            if nine == 0:
                if schoolInfo.split('\n')[8] == '':
                    return None
                else:
                    return float(schoolInfo.split('\n')[8].replace(',', '.'))
            else:
                if schoolInfo.split('\n')[9] == '':
                    return None
                else:
                    return float(schoolInfo.split('\n')[9].replace(',', '.'))

        def province_controll(soup):
            province_title = soup.find("h1", {"class": "title"}).getText().split(' Liseleri')[0]
            for pro in province:
                if pro.name == province_title:
                    return pro.id
            return None

        def getNotNullMark(dataObj):
            if dataObj.taban1 != 0:
                return dataObj.taban1
            elif dataObj.taban2:
                return dataObj.taban2
            else:
                return 0

        myobj = School("", "", "", "", "", "", "", "", "", "", "")
        url = 'https://www.basarisiralamalari.com/lise-taban-puanlari-ve-yuzdelik-dilimleri-lgs-meb/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table') #websitesindeki table'ı buldu ve ortaki tüm a taglerini aldı
        href_tags = table.find_all('a')
        links = []


        for tag in href_tags:
            links.append(tag.attrs['href']) #href taglerinin içindeki linkleri arraye koydu.
        dataObjs = []  #okul obje arrayi
        wrongProvinces = []

        for link in links:  #tüm illeri gezmeyi saglıyor.
            print('LINK :', link)
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')[-1] #bazı yerlerde birden fazla veya yeni tablo olduğu için en sonuncu yani
            rows = tables.find_all('tr')    #istediğimiz tabloyu aldı.
            is_new_table = tables.find('tr') #aldığımızın yeni olup olmadığına baktı.Bazılarında sadece bir tane var
                                  #o yüzden aynı zamanda sonuncuda olur bunun kontrolü olucak onun için var bu kısım.
            schoolsInfos = []
            main_table_avaiable = 1  #9'luk mu 8'lik mi kontrolü için kullanılacak
            is_table_nine = 1
            if 'Alan Adı' not in rows[0].getText():  #tablo 9'luk mu 8'lik mi kontrolü
                is_table_nine = 0
            else:
                is_table_nine = 1
            for row in rows:
                if 'Tercih Kodu' not in is_new_table.getText(): #yeni tablo mu değil mi

                    schoolsInfos.append(row.getText())
                    main_table_avaiable = 1
                else:
                    main_table_avaiable = 0
                    # wrongProvinces.append(link.split('-liseleri')[0].split('.com/')[1])

            if main_table_avaiable == 1:
                schoolsInfos.pop(0)  #iki kere pop var çünkü ilk ikisi her zaman okul adı okul ismi gibi verilerin satırı
                schoolsInfos.pop(0)

                for schoolInfo in schoolsInfos: #tüm okulları obje olarak yaratıp array'e atıyor
                    dataObjs.append(
                        School(okul_adi_controll(schoolInfo), province_controll(soup), ilce_controll(schoolInfo),
                               okul_turu_controll(schoolInfo),
                               alan_adi_controll(schoolInfo, is_table_nine),
                               ogrenim_sure_controll(schoolInfo, is_table_nine),
                               ogrenim_sekli_controll(schoolInfo, is_table_nine),
                               yabanci_dili_controll(schoolInfo, is_table_nine),
                               kont_controll(schoolInfo, is_table_nine), taban1_controll(schoolInfo, is_table_nine),
                               taban2_controll(schoolInfo, is_table_nine)))

        data_teog = {}
        data_teog['lise'] = []
        for obj in dataObjs:    #json'a çevrilme kısmı

            data_teog['lise'].append({
                'is_active':True,
                'name': obj.okul_adi.strip(),
                'region': obj.ilce,
                'school_type': obj.okul_turu,
                'dom': obj.alan_adi,
                'type': obj.ogrenim_sure,
                'condition': obj.ogrenim_sekli,
                'sec_language': obj.yabanci_dili,
                'quota': obj.kont,
                'mark': getNotNullMark(obj),
                'province':obj.province,

            })
        with open('teogData2019.json', 'w', encoding='utf-8') as outfile:
                json.dump(data_teog, outfile, ensure_ascii=False)









    def readPdf2019tablo4(self):

        with open('teogData2019.json', encoding="utf-8") as f:
            data = json.load(f)
            for i, a in enumerate(data['lise']):
                teog = Teogs()
                teog.is_active = True
                teog.name = ' '+a.get('name')
                teog.region = a.get('region')
                teog.school_type = a.get('school_type')
                teog.dom = a.get('dom')
                teog.type = a.get('type')
                teog.condition = a.get('condition')
                teog.sec_language = a.get('sec_language')
                teog.quota = a.get('quota')
                teog.mark = a.get('mark')
                teog.province_id = a.get('province')
                teog.save()



        # for wrongProvince in wrongProvinces:
        #   print(wrongProvince)

        # bu for sadece tablosu olmayan şehirleri gösteriyor şu anlık sadece istanbul
