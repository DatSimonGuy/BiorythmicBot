import telebot
import math
import datetime
import pickle
import os
from threading import Thread
import schedule
from time import sleep
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("TOKEN")

bot = telebot.TeleBot(token,parse_mode= None)


class Person:
    def __init__(self, name, day, month, year):
        self.name = name
        self.day = day
        self.month = month
        self.year = year
    def __str__(self):
        if len(str(self.day)) < 2:
            day = '0' + str(self.day)
        else:
            day = str(self.day)
        if len(str(self.month)) < 2:
            month = '0' + str(self.month)
        else:
            month = str(self.month)
        return f'{self.name} {day}.{month}.{self.year}\n'
    
class Biorythm:
    def __init__(self, int, emo, phys, tendencyi, tendencye, tendencyp):
        self.int = int
        self.emo = emo
        self.phys = phys
        self.tendencyp = tendencyp
        self.tendencye = tendencye
        self.tendencyi = tendencyi
    def __str__(self):
        return f'physical: {self.phys}% {self.tendencyp}\nemotional: {self.emo}% {self.tendencye}\nintellectual: {self.int}% {self.tendencyi}\n'

if os.path.isfile("people.pkl"):
    with open("people.pkl", 'rb') as f:
        people = pickle.load(f)
else:
    people = []

if os.path.isfile("id.pkl"):
    with open("id.pkl", 'rb') as f:
        id = pickle.load(f)
else:
    id = []

def GenerateBiorythm(user, chatid):
    n = 0
    for i in id:
        if i == chatid:
            break
        n+=1
    for person in people[n]:
        if person.name == user:
            current_date = datetime.datetime.now().date()
            date = datetime.date(person.year,person.month,person.day)
            datediff = current_date - date
            if math.sin(2 * math.pi * datediff.days/33) > math.sin(2 * math.pi * (datediff.days+1)/33):
                tendencyi = "decreasing"
            else:
                tendencyi = "increasing"
            if math.sin(2 * math.pi * datediff.days/28) > math.sin(2 * math.pi * (datediff.days+1)/28):
                tendencye = "decreasing"
            else:
                tendencye = "increasing"
            if math.sin(2 * math.pi * datediff.days/23) > math.sin(2 * math.pi * (datediff.days+1)/23):
                tendencyp = "decreasing"
            else:
                tendencyp = "increasing"
            biorythm = Biorythm(round(math.sin(2 * math.pi * datediff.days/33) * 100),round(math.sin(2 * math.pi * datediff.days/28) * 100),round(math.sin(2 * math.pi * datediff.days/23) * 100), tendencyi, tendencye, tendencyp)
            return biorythm
    return 0

def TimeChecker():
    while True:
        schedule.run_pending()
        sleep(1)
        
def DailyCheck():
    print("am aliv")
    n = 0
    for i in id:
        if len(people[n]) > 0:
            message = "Today's biorythms:\n"
            for person in people[n]:
                biorythm = GenerateBiorythm(person.name, i) 
                message = message + str(person.name) + "\n" + str(biorythm) + "\n"
            bot.send_message(text=message, chat_id=i)
        n+=1
    n=0
    for group in people:
        for person in group:
            if datetime.datetime.now().day == person.day and datetime.datetime.now().month == person.month:
                bot.send_message(chat_id=id[n],text=f"Happy birthday @{person.name}")
        n+=1
        
schedule.every().day.at("00:00").do(DailyCheck)
Thread(target=TimeChecker).start()

@bot.message_handler(commands=['start'])
def Answer(message):
    bot.reply_to(message, "Hey! Welcome to BiorythmBot. I will provide you with biorythms at daily basis at 00:00.\nTo start please type /Add (day) (month) (year) please make sure they are all integers.")
    chat_id = message.chat.id
    data = []
    id.append(chat_id)
    with open("id.pkl", "wb") as f:
        pickle.dump(id, f)
    people.append(data)
    with open("people.pkl", "wb") as f:
        pickle.dump(people, f)

@bot.message_handler(commands=['Add','add'])
def AddPerson(message):
    if message.chat.id not in id:
        data = []
        id.append(message.chat.id)
        with open("id.pkl", "wb") as f:
            pickle.dump(id, f)
        people.append(data)
        with open("people.pkl", "wb") as f:
            pickle.dump(people, f)
    text = message.text.split(' ')
    n=0
    for i in id:
        if i == message.chat.id:
            break
        n+=1
    exists = False
    for person in people[n]:
        if person.name == message.from_user.username:
            exists = True
    if exists == False:
        if text[1].isdigit() and text[2].isdigit() and text[3].isdigit(): 
            people[n].append(Person(message.from_user.username, int(text[1]), int(text[2]), int(text[3])))
            bot.reply_to(message, "Added!")
            bot.reply_to(message, people[n][len(people[n])-1])
            with open("people.pkl", 'wb') as f:
                pickle.dump(people, f)
        else:
            bot.reply_to(message, "You did something wrong. Check if you didn't add whitespaces somewhere")
    else:
        bot.reply_to(message, "Bro you arleady did that")
        
    
     
@bot.message_handler(commands=['Gib','gib'])
def Gib(message):
    user = message.from_user.username
    if GenerateBiorythm(user, message.chat.id) != 0:
        bot.reply_to(message, GenerateBiorythm(user, message.chat.id))
    else:
        bot.reply_to(message, "I don't have you in my system! Please provide your birthdate using /add")

@bot.message_handler(commands=['Delete','delete'])
def Delete(message):
    user = message.from_user.username
    chat = message.chat.id
    n = 0
    for i in id:
        if i == chat:
            break
        n-=-1
    for person in people[n]:
        if person.name == user:
            people[n].remove(person)
            break
    bot.reply_to(message, "Deleted!")
    with open("people.pkl",'wb') as f:
        pickle.dump(people, f)

@bot.message_handler(commands=['check','Check'])
def Check(message):
    user = message.from_user.username
    chat = message.chat.id
    n = 0
    for i in id:
        if i == chat:
            break
        n-=-1
    for person in people[n]:
        if person.name == user:
            bot.reply_to(message, "Yes, you exist")
            return
    bot.reply_to(message, "Who are you?")

@bot.message_handler(commands=['Everyone','everyone'])
def Everyone(message):
    chat = message.chat.id
    n = 0
    for i in id:
        if i == chat:
            break
        n-=-1
    text = ""
    for person in people[n]:
        text = text + str(person) 
    bot.reply_to(message, text)   
bot.infinity_polling()