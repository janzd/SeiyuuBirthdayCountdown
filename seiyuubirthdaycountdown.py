from datetime import *
import time
import _thread

try:
    from msvcrt import getch
except ImportError:
    def getch():
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
    global char
    char = getch()

class Seiyuu:    
    def __init__(self,name,y,m,d):
        self.name = name
        self.y = y
        self.m = m
        self.d = d
        if self.y is not None:
            self.birthdate = datetime(self.y,self.m,self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        else:
            self.birthdate = datetime(year=1000,month=self.m,day=self.d,hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        self.countRemainingDays()
        if self.y is not None:
            self.countAge()
        else:
            self.age = None
        
    def countRemainingDays(self):
        now = datetime.now()
        self.remainingDays = self.birthdate.day - now.day 

    def countAge(self):
        now = datetime.now()
        if now.month < self.birthdate.month or (now.month == self.birthdate.month and now.day < self.birthdate.day):
            self.age = now.year - self.birthdate.year
        else:
            self.age = now.year - self.birthdate.year + 1
        
    def __str__(self):
        if self.age is not None:
            return str(str(self.remainingDays) + " days left until " + self.name + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + " turning " + str(self.age) + " years old.")
        else:
            return str(str(self.remainingDays) + " days left until " + self.name + "'s birthday! " + self.birthdate.strftime("%B") + " " + str(self.birthdate.day) + ".")

class Sorter:
    def __init__(self, seiyuu, daysLeftThreshold):
        self.seiyuu = seiyuu
        self.sortByRemainingDays()
        self.printSeiyuuWhoseBirthdayIsWithinXDays(daysLeftThreshold)

    def sortByRemainingDays(self):
        self.seiyuu.sort(key=lambda x: x.remainingDays, reverse=False)  

    def printSeiyuuWhoseBirthdayIsWithinXDays(self, daysLeftThreshold):
        for s in self.seiyuu:
            if s.remainingDays > daysLeftThreshold:
                break
            else:
                print(s)

def readDatabase():
    database = open("seiyuu_database.csv", mode='r', encoding='utf-8')
    seiyuu_database = {};
    for line in database:
        seiyuu = line.strip().split(",")
        seiyuu_database[seiyuu[0] + " " + seiyuu[1]] = seiyuu
    database.close()
    return seiyuu_database

def readOwnList(seiyuu_database):
    ownList = open("seiyuu_list.txt", mode='r', encoding='utf-8')
    seiyuu_list = []
    for line in ownList :
        name = line.strip().split()
        seiyuu = seiyuu_database[name[0] + " " + name[1]]
        seiyuu_list.append(seiyuu)
    ownList.close()
    return seiyuu_list

def instantiateSeiyuuObjects(seiyuu_list):
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
    seiyuu_database = readDatabase()
    seiyuu_list = readOwnList(seiyuu_database)
    seiyuu_objects = instantiateSeiyuuObjects(seiyuu_list)
    daysLeftThreshold = 15
    sorter = Sorter(seiyuu_objects, daysLeftThreshold)
    print("Close by pressing any key...")
    _thread.start_new_thread(keypress, ())
    while True:
        if char is not None:
            break
        time.sleep(0.1)


if __name__ == '__main__':
    main()