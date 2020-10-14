import tkinter as tk
from bs4 import BeautifulSoup
import requests
import urllib


languageSelected = "default"
language = 0
difficulty = "default"
arraySelected = []
currVerb = "default"
window = tk.Tk()
frame = tk.Frame(window, width = 600, height = 300, bg="grey")
frame2 = tk.Frame(window, width = 600, height = 300, bg="grey")
frame.place(x=0,y=0)
fbut = tk.Button()
dBut = tk.Button()
d1But = tk.Button()
d2But = tk.Button()
d3But = tk.Button()
d4But = tk.Button()
d5But = tk.Button()
d6but = tk.Button()
languageLabel = ""
topVerbs10 = []
topVerbs25 = []
topVerbs50 = []
topVerbs100 = []
topVerbs200 = []
irregulars = []
i = ""
you = ""
heshe = ""
we = ""
youFormal = ""
they = ""

class Language:
    def __init__(self, Language, topverbs10, topVerbs25, topVerbs50, topVerbs100, topVerbs200, irregulars, i, you, heshe, we, youFormal, they):
        self.languageLabel = Language
        self.topverbs10 = topVerbs10
        self.topVerbs25 = topVerbs25
        self.topVerbs50 = topVerbs50
        self.topVerbs100 = topVerbs100
        self.topVerbs200 = topVerbs200
        self.irregulars = irregulars
        self.i = i
        self.you = you
        self.heshe = heshe
        self.we = we
        self.youFormal = youFormal
        self.they = they


    def devUI():
        return

# Create languages before main runs
French = Language("French", ["Etre", "Avoir", "Aller", "Vouloir", "Faire", "Parler", "Demander", "Savoir", "Dire", ""], \
["test"], 0, 0, 0, 0, "je", "tu", "il/elle", "nous", "vous", "ils/elles")

German = Language("German", 0, 0, 0, 0, 0, 0, "ich", "du", "er/sie/es", "wir/sie", "ihr", "Sie")

class User:
    def __init__(self, languageSelected, difficulty):
        self.languageSelected = languageSelected
        self.difficulty = difficulty

    def setLanguageFrench(self):
        language = 1
        self.language = French
        return
    def setLanguageGerman(self):
        language = 1
        self.language = German
        return

    # Difficulty setters
    def setDifficultyA1(self):
        self.difficulty = "A1"
        if (language == 1):
            self.arraySelected = self.languageSelected.topVerbs10
        return
    def setDifficultyA2(self):
        self.difficulty = "A2"
        if (language == 1):
            selfarraySelected = self.languageSelected.topVerbs25
        return
    def setDifficultyB1(self):
        self.difficulty = "B1"
        if (language == 1):
            self.arraySelected = self.languageSelected.topVerbs50
        return
    def setDifficultyB2(self):
        self.difficulty = "B2"
        if (language == 1):
            self.arraySelected = self.languageSelected.topVerbs100
        return
    def setDifficultyC(self):
        self.difficulty = "C"
        if (language == 1):
            self.arraySelected = self.languageSelected.topVerbs200
        return
    def setDifficultyIr(self):
        self.difficulty = "I"
        if (language == 1):
            self.arraySelected = self.languageSelected.irregulars


    def startF(self):
        if self.languageSelected == "default" or self.difficulty == "default":
            print("Error! Select language and difficulty")
            return
        frame.forget()
        frame.destroy()
        frame2.place(x=0, y=0)
        self.frame2Builder()
        currVerb = "devoir"
        website = "http://www.conjugation-fr.com/conjugate.php?verb=" +currVerb + "&x=0&y=0"
        req = requests.get(website)
        soup = str(BeautifulSoup(req.content, 'html5lib'))
        print(soup)
        one = soup.find("je d<span class=\"conjuguaison\">")
        print(one)
        two = soup.find("</span><br/>")
        print(two)
        oneAnswer = soup[(one + 30), two - 1]
        print(oneAnswer)

    def checkAnswers():

        return

    def frame1Builder(self):
        window.title("Conjugation Practice")
        window.geometry("600x300")
        label = tk.Label(frame, text = "Welcome to the Conjugation Practicer!", font=("Arial Bold", 25))
        label.place(x=60,y=0)
        fBut = tk.Button(frame, text = "French", command = lambda : self.setLanguageFrench()).place(x = 212, y =35)
        gBut = tk.Button(frame, text = "German", command = lambda : self.setLanguageGerman()).place(x = 288, y = 35)
        d1But = tk.Button(frame, text = "Beginner (A1)", command = lambda : self.setDifficultyA1()).place(x = 175, y = 70)
        d2But = tk.Button(frame, text = "Improving (A2)", command = lambda : self.setDifficultyA2()).place(x = 285, y = 70)
        d3But = tk.Button(frame, text = "Intermediate (B1)", command = lambda : self.setDifficultyB1()).place(x = 285, y = 95)
        d4But = tk.Button(frame, text = "Intermediate Advanced (B2)", command = lambda : self.setDifficultyB2()).place(x = 85, y = 95)
        d5But = tk.Button(frame, text = "Advanced (C1-2)", command = lambda: self.setDifficultyC()).place(x = 220, y = 120)
        d6but = tk.Button(frame, text = "irregulars only", command = lambda: self.setDifficultyIr()).place(x = 230, y = 150)
        startBut = tk.Button(frame, text = "Start!", command = lambda : self.startF()).place(x = 260, y = 200)

    def frame2Builder(self):
        #build text boxes
        window.title("Selected Language: " + self.languageSelected)
        definition = tk.Entry(frame2)
        definition.place(x=200, y=35)
        je = tk.Entry(frame2)
        je.place(x=200, y=75)
        tu = tk.Entry(frame2)
        tu.place(x=200, y=100)
        il = tk.Entry(frame2)
        il.place(x=200, y=125)
        nous = tk.Entry(frame2)
        nous.place(x=200, y=150)
        vous = tk.Entry(frame2)
        vous.place(x=200, y=175)
        elles = tk.Entry(frame2)
        elles.place(x=200, y=200)
        past = tk.Entry(frame2)
        past.place(x=200, y=225)
        defBox = tk.Label(frame2, text = "Infinitive definition:", bg="grey", fg="white")
        defBox.place(x=60,y=35)
        jeBox = tk.Label(frame2, text = self.language.i, bg="grey", fg = "white")
        jeBox.place(x=175, y=75)
        tuBox = tk.Label(frame2, text = self.language.you, bg="grey", fg = "white")
        tuBox.place(x=175, y=100)
        ilBox = tk.Label(frame2, text = self.language.heshe, bg="grey", fg = "white")
        if self.language.languageLabel == "German":
            ilBox.place(x=132, y = 125)
        else:
            ilBox.place(x=155, y=125)
        nousBox = tk.Label(frame2, text = self.language.we, bg="grey", fg = "white")
        nousBox.place(x=155, y=150)
        vousBox = tk.Label(frame2, text = self.language.youFormal, bg="grey", fg = "white")
        vousBox.place(x=155, y=175)
        ellesBox = tk.Label(frame2, text = self.language.they, bg="grey", fg = "white")
        if self.language.languageLabel == "German":
            ellesBox.place(x=150, y=200)
        else:
            ellesBox.place(x=140, y=200)
        pastBox = tk.Label(frame2, text = "Past participle", bg="grey", fg="white")
        pastBox.place(x=90,y=225)
        tk.Button(frame2, text = "Check answers", command = lambda : checkAnswers()).place(x= 200, y = 270)



if __name__=='__main__':
    user = User("Default", "Default")
    user.frame1Builder()
    window.mainloop()
