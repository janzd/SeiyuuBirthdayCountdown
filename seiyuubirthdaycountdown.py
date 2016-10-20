from datetime import *
import time
try:
    import thread as _thread
except:
    import _thread
import os
try:
    import cPickle as pickle
except:
    import pickle
import sys

if sys.version_info[0] > 2:
    pass
else:
    import codecs
    def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding,
                    errors=errors, buffering=buffering)

try:
    from msvcrt import getch
except ImportError:
    def getch():
        """Listens to keyboard."""
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
 
char = None
 
def keypress():
    """Retrieves any pressed key and stores the character in a global variable."""
    global char
    char = getch()

class Seiyuu(object):
    """Class representing individual seiyuu instances.

    It is used to work with the data from the database and find the seiyuu
    whose birthdays are approaching.

    Attributes:
        surname_k: A string containing the surname of a seiyuu in kanji.
        fname_k: A string containing the first name of a seiyuu in kanji.
        surname_y: A string containing the surname of a seiyuu in kana.
        fname_y: A string containing the first name of a seiyuu in kana.
        surname_r: A string containing the surname of a seiyuu in romaji.
        fname_r: A string containing the name of a seiyuu in romaji.
        y: An integer representing the year of birth of a seiyuu.
        m: An integer representing the month of birth of a seiyuu.
        d: An integer representing the day of birth of a seiyuu.
        birthdate: A datetime object representing the date of birth of a seiyuu.
        age: An integer representing the age of a seiyuu.
        remaining_days: An integer representing the number of days left until the birthday of a seiyuu.
    """

    def __init__(self,surname_k,fname_k,surname_y,fname_y,surname_r,fname_r,y,m,d):
        """Instantiates an object of the Seiyuu class."""
        self.surname_k = surname_k
        self.fname_k = fname_k
        self.surname_y = surname_y
        self.fname_y = fname_y
        self.surname_r = surname_r
        self.fname_r = fname_r
        self.y = y
        self.m = m
        self.d = d
        if self.y is not None:
            self.birthdate = datetime(self.y,self.m,self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        else:
            self.birthdate = datetime(year=1000,month=self.m,day=self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        if self.y is not None:
            self.is_age = 1
        else:
            self.is_age = 0
        
    def get_remaining_days(self):
        """Counts the number of days left until the birthday."""
        now = datetime.now()
        date_now = date(now.year, now.month, now.day)
        if now.month < self.birthdate.month or (now.month == self.birthdate.month and now.day < self.birthdate.day):
            date_birthday = date(now.year, self.birthdate.month, self.birthdate.day)
        else:
            date_birthday = date(now.year + 1, self.birthdate.month, self.birthdate.day)
        difference = date_birthday - date_now
        return difference.days

    def get_age(self):
        """Counts the age of the seiyuu."""
        now = datetime.now()
        if now.month < self.birthdate.month or (now.month == self.birthdate.month and now.day < self.birthdate.day):
            return now.year - self.birthdate.year
        else:
            return now.year - self.birthdate.year + 1
        
    def __str__(self):
        """Default print method of the Seiyuu class."""
        if self.is_age == 1:
            return str(str(self.get_remaining_days()) + " days left until " + self.surname_r + " " + self.fname_r + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + " turning " + str(self.get_age()) + " years old.")
        else:
            return str(str(self.get_remaining_days()) + " days left until " + self.surname_r + " " + self.fname_r + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + ".")

class Sorter(object):
    """Class used for sorting seiyuu objects by the days remaining until their birthdays in ascending order
    and printing the names of those whose birthdays are approaching.

    Attributes:
       seiyuu: A list of Seiyuu objects.
    """

    def __init__(self, seiyuu_objects, days_left_threshold):
        """Instantiates an object of the Sorter class, sorts the seiyuu, and prints those
        whose birthdays are to be reminded of based on the number of days left until their birthdays.

        Args:
            seiyuu: A list of Seiyuu objects.
            days_left_threshold: An integer indicating the threshold of number of days left until
                the birthday of a seiyuu from which to remind of it.
        """
        self.seiyuu_objects = seiyuu_objects
        self.sort_by_remaining_days()
        self.print_seiyuu_whose_birthday_is_within_x_days(days_left_threshold)

    def sort_by_remaining_days(self):
        """Sorts the list of seiyuu by the number of days remaining until their birthdays in ascending order."""
        self.seiyuu_objects.sort(key=lambda x: x.get_remaining_days(), reverse=False)  

    def print_seiyuu_whose_birthday_is_within_x_days(self, days_left_threshold):
        """Prints the Seiyuu objects of seiyuu whose birthdays are closer than the defined threshold."""
        printed_any = 0
        for s in self.seiyuu_objects:
            if s.get_remaining_days() > days_left_threshold:
                break
            else:
                print(s)
                printed_any = 1
        if printed_any == 0:
            print("There is not any seiyuu in your selection who celebrates his/her birthday within " + str(days_left_threshold) + " days.")

def read_database():
    """Reads the database file and stores all entries in a dictionary."""
    database = open("database.csv", mode='r', encoding='utf-8')
    seiyuu_database = {};
    for line in database:
        seiyuu = line.strip().split(",")
        seiyuu_database[seiyuu[0] + " " + seiyuu[1]] = seiyuu
        seiyuu_database[seiyuu[4] + " " + seiyuu[5]] = seiyuu
    database.close()
    return seiyuu_database

def read_own_list(seiyuu_database):
    """Reads the list of seiyuu the user is interested in and stores their corresponding
    dictionary entries in a list.

    Args:
        seiyuu_database: A dictionary with seiyuu entries from the database.
    """
    own_list = open("seiyuu_list.txt", mode='r', encoding='utf-8')
    seiyuu_list = []
    for line in own_list :
        name = line.strip().split()
        try:
            seiyuu = seiyuu_database[name[0] + " " + name[1]]
            seiyuu_list.append(seiyuu)
        except KeyError:
            try:
                seiyuu = seiyuu_database[name[0] + " " + name[1]]
                seiyuu_list.append(seiyuu)
            except KeyError:
                pass
    own_list.close()
    return seiyuu_list

def instantiate_seiyuu_objects(seiyuu_list):
    """Goes through the list of seiyuu and creates an object of Seiyuu class for each of them.
    
    Args:
        seiyuu_list: A list of seiyuu the user is interested in.
    """
    seiyuu_objects = []
    for seiyuu in seiyuu_list:
        if seiyuu[6] is not '':
            s = Seiyuu(seiyuu[0], seiyuu[1], seiyuu[2], seiyuu[3], seiyuu[4], seiyuu[5], int(seiyuu[6]), int(seiyuu[7]), int(seiyuu[8]))
            seiyuu_objects.append(s)
        else:
            s = Seiyuu(seiyuu[0], seiyuu[1], seiyuu[2], seiyuu[3], seiyuu[4], seiyuu[5], None, int(seiyuu[7]), int(seiyuu[8]))
            seiyuu_objects.append(s)
    return seiyuu_objects

def hash_seiyuu_names():
    """Returns a hashcode of the text in the user's list of seiyuu"""
    with open("seiyuu_list.txt", mode='r', encoding='utf-8') as own_list:
        list_content = own_list.read()
    return hash(list_content)

def main():      
    """Tries to open generated serialized object file and the hashcode file of user's list.
    If the files are not available or the stored hashcode does not match the current hashcode
    of user's list, it calls methods to read the database and the user file with a list of seiyuu,
    and calls a method to create the objects of Seiyuu class for each seiyuu, and then serializes
    the objects in a file and saves the new hashcode.
    Then, it creates an object of the Sorter class to sort the seiyuu by the days remaining
    until their birthdays and print those whose birthdays are close, and tells
    the user to exit by pressing any key."""
    no_generated_data = 0
    if os.path.isfile('seiyuu_o.pkl') and os.path.isfile('sl_hsh'):
        with open('seiyuu_o.pkl', 'rb') as obj_file:
            seiyuu_objects = pickle.load(obj_file)
        idhash = 0
        with open('sl_hsh', 'r', encoding='utf-8') as hash_file:
            content = hash_file.read().splitlines()
            idhash = content[0]
    else:
        no_generated_data = 1
    if no_generated_data == 1 or idhash != str(hash_seiyuu_names()):
        seiyuu_database = read_database()
        seiyuu_list = read_own_list(seiyuu_database)
        seiyuu_objects = instantiate_seiyuu_objects(seiyuu_list)
        idhash = hash_seiyuu_names()
        with open('sl_hsh', 'w', encoding='utf-8') as hash_file:
            hash_file.write(str(idhash))
        with open('seiyuu_o.pkl', 'wb') as obj_file:
            pickle.dump(seiyuu_objects, obj_file)
    # Variable defining the threshold of number of days left until the birthday 
    # from which to remind of the approaching birthday.
    days_left_threshold = 15
    sorter = Sorter(seiyuu_objects, days_left_threshold)
    print("Close by pressing any key...")
    _thread.start_new_thread(keypress, ())
    while True:
        if char is not None:
            break
        time.sleep(0.1)


if __name__ == '__main__':
    main()
