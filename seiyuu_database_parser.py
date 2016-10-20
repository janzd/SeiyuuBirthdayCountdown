# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import codecs
import romkan

if sys.version_info[0] > 2:
    pass
else:
    def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding,
                    errors=errors, buffering=buffering)

#sys.stdin  = codecs.getreader('utf_8')(sys.stdin)
#sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

url = 'http://lain.gr.jp/voicedb/profile/'

def parse_name(name):
    name = name.split(' ')
    surname = name[0]
    first_name = ''
    if len(name) == 2:
        first_name = name[1]
    if len(name) > 2:
        first_name = " ".join(name[1:])
        print(name)
    return surname, first_name

def parse_yomi_name(db_entry):
    yomi = db_entry.find(text = u'よみ')
    yomi_name = yomi.findNext().getText()
    yomi_surname, yomi_first_name = parse_name(yomi_name)
    print(yomi_surname.encode('utf-8') + ' ' + yomi_first_name.encode('utf-8'))
    return yomi_surname, yomi_first_name, romkan.to_waapuro(yomi_surname).title(), romkan.to_waapuro(yomi_first_name).title()

def parse_kanji_name(db_entry):
	kanji = db_entry.find(text = u'名前')
	kanji_name = kanji.findNext().getText()
	kanji_surname, kanji_first_name = parse_name(kanji_name)
	return kanji_surname, kanji_first_name

def parse_birthdate(db_entry):
    tanjoubi = db_entry.find(text = u'誕生日')
    if tanjoubi is None:
    	return None
    birthdate = tanjoubi.findNext().getText()
    birthdate = birthdate.split(u'年')
    year_of_birth = ''
    month_of_birth = ''
    day_of_birth = ''
    if len(birthdate) == 1:
    	month_day_of_birth = birthdate[0].split(u'月')
    else:
        year_of_birth = birthdate[0]
        month_day_of_birth = birthdate[1].split(u'月')
    month_of_birth = month_day_of_birth[0]
    day_of_birth = month_day_of_birth[1].split(u'日')
    day_of_birth = day_of_birth[0]
    return (year_of_birth, month_of_birth, day_of_birth)

class Seiyuu(object):

	def __init__(self, kanji_surname, kanji_first_name, yomi_surname, yomi_first_name, romaji_surname, romaji_first_name, year_of_birth, month_of_birth, day_of_birth):
		self.kanji_surname = kanji_surname
		self.kanji_first_name = kanji_first_name
		self.yomi_surname = yomi_surname
		self.yomi_first_name = yomi_first_name
		self.romaji_surname = romaji_surname
		self.romaji_first_name = romaji_first_name
		self.year_of_birth = year_of_birth
		self.month_of_birth = month_of_birth
		self.day_of_birth = day_of_birth

index = 1
error404_seq = 0
seiyuu_list = []
while True:
	try:
		response = urllib2.urlopen(url + str(index))
		source = response.read()
		soup = BeautifulSoup(source.decode('utf-8'))
		db_entry = soup.find('div', {'id' : 'db'})
		index += 1
		if error404_seq > 0:
		    error404_seq = 0
		kanji_surname, kanji_first_name = parse_kanji_name(db_entry)
		yomi_surname, yomi_first_name, romaji_surname, romaji_first_name = parse_yomi_name(db_entry)
		print(romaji_surname + ' ' + romaji_first_name)
		birthdate = parse_birthdate(db_entry)
		if birthdate is None:
			continue
		seiyuu = Seiyuu(kanji_surname, kanji_first_name, yomi_surname, yomi_first_name, romaji_surname, romaji_first_name, birthdate[0], birthdate[1], birthdate[2])
		seiyuu_list.append(seiyuu)
		if (index % 100) == 0:
			print(index)
	except urllib2.HTTPError:
		index += 1
		error404_seq += 1
		if error404_seq > 100:
			break
		else:
			continue

seiyuu_list.sort(key=lambda s: (s.yomi_surname, s.yomi_first_name))

with open('database.csv', 'w', encoding='utf-8') as database:
	for seiyuu in seiyuu_list:
		database.write(seiyuu.kanji_surname + ',')
		database.write(seiyuu.kanji_first_name + ',')
		database.write(seiyuu.yomi_surname + ',')
		database.write(seiyuu.yomi_first_name + ',')
		database.write(seiyuu.romaji_surname + ',')
		database.write(seiyuu.romaji_first_name + ',')
		database.write(seiyuu.year_of_birth + ',')
		database.write(seiyuu.month_of_birth + ',')
		database.write(seiyuu.day_of_birth + '\n')
