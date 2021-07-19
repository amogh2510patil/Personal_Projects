# PROGRAMMING CLUB PROJECT
# Program to detect any sort of plagirism between one source code file with another set of test files
#Team members:
# Abdul Hadi - ME19B068
# Amogh Patil - EE19B134
# Sharang Borde - MM19B058
# Vivek - 



import mysql.connector
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = ""  #Enter your sql password
)
mycursor = mydb.cursor()  #Used to establish connection with sql server

#Creating database and table
mycursor.execute("CREATE DATABASE IF NOT EXISTS plagirismcheck") 
mycursor.execute("USE plagirismcheck")
mycursor.execute("CREATE TABLE IF NOT EXISTS DATAS (FILENAME VARCHAR(255), SIMILARITY FLOAT(10))")
mycursor.execute("DELETE FROM DATAS")

from threading import *
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        #print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation
import threading 
def EditDistDP(str1, str2):
    
    len1 = len(str1); 
    len2 = len(str2);
    
    #To fill the DP array with 0
    
    DP = [[0 for i in range(len1 + 1)] for j in range(2)]
    #Base condition when second string is empty then we remove all characters
    
    for i in range(len1 + 1):
        DP[0][i] = i
    #Start filling the DP This loop run for every character in second string
        
    for i in range(1,len2 + 1):

    #This loop compares the char from second string with first string characters 
        
        for j in range(len1 + 1):

    #if first string is empty then we have to perform add character operation to get second string
			
            if(j == 0):
                DP[i % 2][j] = i

    #if character from both string is same then we do not perform any operation . here i % 2 is for bound the row number. 
                
            elif(str1[j-1] == str2[i-1]):
                DP[i % 2][j] = DP[(i - 1) % 2][j - 1]

    #if character from both string is not same then we take the minimum from three specified operation 
                
            else:
                DP[i % 2][j] = 1 + min(DP[(i - 1) % 2][j], min(DP[i % 2][j - 1], DP[(i - 1) % 2][j - 1]))
	
    #after complete fill the DP array if the len2 is even then we end up in the 0th row else we end up 
    #in the 1th row so we take len2 % 2 to get row
    S = (1 - (DP[len2 % 2][len1])/(max(len1,len2)))*100
    return(S)

def Sentencing(sent1,sent2):
    #Extracting words from the sentences
    words1 = [w.lower() for w in word_tokenize(sent1) if w not in punctuation] 
    words2 = [w.lower() for w in word_tokenize(sent2) if w not in punctuation]

    #Common words giving zero edit distance
    words = set(words1) & set(words2)
    common_words = [w for w in words]
    common_words.sort()
    sen = " ".join(common_words)

    #Sentence 1 with alphabetically arranged words excluding common words
    sen1 = [w for w in words1 if w not in words]
    sen1.sort()
    sent1 = " ".join(sen1)

    #Similarly sentence 2
    sen2 = [w for w in words2 if w not in words]
    sen2.sort()
    sent2 = " ".join(sen2) 

    #Sentences with common words at the beginning followed by alphabetically arranged words
    sent1 = sen + ' ' + sent1
    sent2 = sen + ' ' + sent2
    return(EditDistDP(sent1,sent2))


#Opening the query doc that needs to checked(User enter in *.txt form)
f1 = input("Enter the name of the file to be inspected: ")
with open (f1) as f:
    lines1 = [line.split('#')[0] for line in f.readlines()]
    f.close()
sent1 = ' '.join(lines1)

num = int(input("Enter the Number of files needed to be checked with: "))  #Number of files to be checked with query doc
files =[]     #To store file contents in the list
filename=[]   #To store file names in the list
sqlcmd = "INSERT INTO DATAS (FILENAME, SIMILARITY) VALUES (%s,%s)"

#Opening the files
for i in range(num):
    print("Enter the name of the ",i+1,"th file: ")
    f2 = input()
    inp = (f2,0)
    mycursor.execute(sqlcmd, inp)     #Entering the names of files into the database
    filename.append(f2)               #Store the file contents
    with open (f2) as f:
        lines2 = [line.split('#')[0] for line in f.readlines()]
        sent2 = ' '.join(lines2)
        files.append(sent2)
        f.close()

print()
mydb.commit()

#Creating threads for simultaneous checking of various documents
Tobj=[]     #To store the returned percentages
for fil in files:
    a = ThreadWithReturnValue(target=Sentencing, args=(sent1,fil))
    a.start()
    Tobj.append(a)

#Entering the returned %ofsimilarity into the database
for (val,fname) in zip(Tobj,filename):
    perc=val.join()
    sql = "UPDATE DATAS SET SIMILARITY = "+str(perc)+" WHERE FILENAME = '"+fname+"'"
    mycursor.execute(sql)
    mydb.commit()

#Retrieving data from database to be displayed to user
mycursor.execute("SELECT * FROM DATAS")
data = mycursor.fetchall()
for row in data:
    print(row)

#mycursor.execute() - used to execute SQL commands 
#mydb.commit()  - Used to save changes made to the database
