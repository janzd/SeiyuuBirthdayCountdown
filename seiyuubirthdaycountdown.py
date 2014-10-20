from datetime import *
import time
import _thread

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
        name: A string containing the name of a seiyuu.
        y: An integer representing the year of birth of a seiyuu.
        m: An integer representing the month of birth of a seiyuu.
        d: An integer representing the day of birth of a seiyuu.
        birthdate: A datetime object representing the date of birth of a seiyuu.
        age: An integer representing the age of a seiyuu.
        remaining_days: An integer representing the number of days left until the birthday of a seiyuu.
    """

    def __init__(self,name,y,m,d):
        """Instantiates an object of the Seiyuu class."""
        self.name = name
        self.y = y
        self.m = m
        self.d = d
        if self.y is not None:
            self.birthdate = datetime(self.y,self.m,self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        else:
            self.birthdate = datetime(year=1000,month=self.m,day=self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        self.count_remaining_days()
        if self.y is not None:
            self.count_age()
        else:
            self.age = None
        
    def count_remaining_days(self):
        """Counts the number of days left until the birthday."""
        now = datetime.now()
        self.remaining_days = self.birthdate.day - now.day 

    def count_age(self):
        """Counts the age of the seiyuu."""
        now = datetime.now()
        if now.month < self.birthdate.month or (now.month == self.birthdate.month and now.day < self.birthdate.day):
            self.age = now.year - self.birthdate.year
        else:
            self.age = now.year - self.birthdate.year + 1
        
    def __str__(self):
        """Default print method of the Seiyuu class."""
        if self.age is not None:
            return str(str(self.remaining_days) + " days left until " + self.name + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + " turning " + str(self.age) + " years old.")
        else:
            return str(str(self.remaining_days) + " days left until " + self.name + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + ".")

class Sorter(object):
    """Class used for sorting seiyuu objects by the days remaining until their birthdays in ascending order.

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
        self.seiyuu_objects.sort(key=lambda x: x.remaining_days, reverse=False)  

    def print_seiyuu_whose_birthday_is_within_x_days(self, days_left_threshold):
        """Prints the Seiyuu objects of seiyuu whose birthdays are closer than the defined threshold."""
        for s in self.seiyuu_objects:
            if s.remaining_days > days_left_threshold:
                break
            else:
                print(s)

def read_database():
    """Reads the database file and stores all entries in a dictionary."""
    database = open("seiyuu_database.csv", mode='r', encoding='utf-8')
    seiyuu_database = {};
    for line in database:
        seiyuu = line.strip().split(",")
        seiyuu_database[seiyuu[0] + " " + seiyuu[1]] = seiyuu
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
        if seiyuu[2] is not '':
            s = Seiyuu(seiyuu[0] + " " + seiyuu[1], int(seiyuu[2]), int(seiyuu[3]), int(seiyuu[4]))
            seiyuu_objects.append(s)
        else:
            s = Seiyuu(seiyuu[0] + " " + seiyuu[1], None, int(seiyuu[3]), int(seiyuu[4]))
            seiyuu_objects.append(s)
    return seiyuu_objects

def main():      
    """Calls methods to read the database and the user file with a list of seiyuu,
    calls a method to create the objects of Seiyuu class for each seiyuu,
    creates an object of the Sorter class to sort the seiyuu by the days remaining
    until their birthdays and print those whose birthdays are close, and tells
    the user to exit by pressing any key."""
    seiyuu_database = read_database()
    seiyuu_list = read_own_list(seiyuu_database)
    seiyuu_objects = instantiate_seiyuu_objects(seiyuu_list)
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