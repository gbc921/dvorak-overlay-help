#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Bruno F. Casella

import os
import time
import sys
import signal
import pygtk
import gtk
import ConfigParser
from uuid import getnode
from PyQt4 import QtCore, QtGui
import sys

#TODO 
#janela de escolha de browser (its there! proximo passo: botoes com icones(ta la!\o), janela com viadagem(ok tb))
#escolher se quer abrir em nova janela/janela anonima
#escolher se sempre quer que abra a janela de escolha de browsers instalados
#os dois de cima significam ARQUIVO DE CONFIGURACAO. Sera com configparser (FEITO) ou optparser (NOPE)
#menuzinho para configurar o arquivo de configuracao
#quando clicar num link de email, mandar escolher em qual browser abrir o gmail ia ser uma opcao interessante de se colocar : chromium-browser "https://mail.google.com/mail?view=cm&tf=0&to=`echo $1 | sed 's/mailto://'`"  (FEITO)
#opcao de escolher, quando se der ctrl+c num link, de abrir essa janela (para isso a aplicacao ia ter que ficar num daemon - "You shall delay this!"- Gandalf, about this feature)
#arquivos de log
#instalador legaal (serve um instalador gambiarra?)
#versao pyqt (ta indo... )
#retirar as pogs

#README
#Its a know "bug" (actually, its a feature) of Evince - the pdf reader from gnome - to get you as answer a "permission denied" when trying to open a url through this script. It's documented there (https://bugs.launchpad.net/ubuntu/+source/evince/+bug/632599) that sic" Evince is protected by an AppArmor profile which is intended to confine Evince to a known set of executables in an effort to reduce the attack surface for an attacker if there is a flaw in evince or (much more likely) the underlying libraries ", and to fix it, you should have to edit /etc/apparmor.d/usr.bin.evince to have in the "/usr/bin/evince" stanza:  /home/yourusername/whateverfolder/choooser.sh PUxr,    (be aware thata the comma is part of it)
# and then running: $ sudo apparmor_parser -r -T -W /etc/apparmor.d/usr.bin.evince
#I hope to add some install script to fix this automatically, and also to get de depencies too; It will be there, I just dont know when ;)

pid = os.getpid() #this process pid
theFolder="{0}/Dropbox/Projects".format(os.getenv("HOME"))


def verifyWinManager():
    winManager = os.getenv("GDMSESSION")
    return winManager

def installChoooser(path = None, browser = 'opera', force = False):
    #POG
    #quer um instalador legal ? faça! (e depois me mande)
    if path is not None:
        try:
            if not force:
                FILE = open("{0}{1}2".format(path, browser),"r")
        except:
            try:
                os.rename("{0}{1}".format(path,browser), "{0}{1}2".format(path,browser))
            except:
                print "Erro ao renomear {0} para {1}2".format(browser)
            try:
                os.system("ln -s {0}/choooser.py {1}{2}".format(theFolder,path, browser))
                os.system("chmod +x {0}{1}".format(path, browser))
            except:
                print "Erro ao criar o soft link"
            print "Instalado com sucesso (I hope so!)"
            return True
        return False
    else:
        print "Path to the desired browser is required"
        return False


class ChoooserConfig(ConfigParser.ConfigParser):
    
    def __init__(self):
        self.filename = "{0}/choooser.cfg".format(theFolder)
        ConfigParser.ConfigParser.__init__(self)
        self.saida=None
        
        if not os.path.exists(self.filename):
            #se nao existir, cria os arquivos e as secoes
            self.add_section("Choooser")
            self.set("Choooser", "winmanager","qt")
            self.set("Choooser", "notify","No")
            self.set("Choooser", "pog", "No")
            self.save()
        self.load()

    def load(self):
        self.readfp(open(self.filename))

    def save(self):
        saida=open(self.filename, 'wb')
        with saida as configfile:
            self.write(configfile)
        saida.close()
    
    def getWinManager(self):
        return self.get("Choooser", "winmanager")

    def setWinManager(self, valor):
        self.set("Choooser", "winmanager", valor)
        
    def getNotify(self):
        return self.getboolean("Choooser", "notify")
        
    def setNotify(self,valor="No"):
        self.set("Choooser","notify",valor)

    def getPog(self):
        return self.get("Choooser", "pog")
        
    def setPog(self,valor="firefox"):
        self.set("Choooser","pog",valor)

    def commit(self):
        self.save()


class Choooser():

    runningBrowsers = []
    installedBrowsers = []
    browsers=["chromium-browser-bin","chromium-browser","chromium","opera",
    "firefox","firefox-bin", "firefox-trunk-bin" , "google-chrome","chrome", "epiphany"]
	
    def __init__(self):
        self.__theChosenOne = None
		
    def getTheChosenOne(self):
        return self.__theChosenOne
	
    def setTheChosenOne(self,browser):
        self.__theChosenOne=browser
	
    def verifyRunningBrowsers(self):
        browsers=["chromium-browser-bin","chromium-browser","chromium","opera",
        "firefox","firefox-bin", "firefox-trunk-bin", "google-chrome","chrome", "epiphany"]
        config=ChoooserConfig()
        pog = config.getPog()        
        for aux in browsers:
            brow=os.system("pidof {0}".format(aux))
            if brow!=256:
                if aux.count("firefox-trunk-bin")>=1:
                    aux="firefox-trunk"
                elif aux.count("firefox") >=1:
                    if verifyWinManager()=="gnome-shell":
                        if pog=="firefox":
                            aux="firefox2"
                        else:
                            aux="firefox"
                    else:
                        aux="firefox"
                elif aux.count("chrome") >=1 :
        	        aux="google-chrome"
        	        
                elif aux.count("opera") >=1 :
                    if verifyWinManager()=="gnome-shell":
                        if pog=="opera":
                            aux="opera2"
                        else:
                            aux="opera"
                    else:
                        aux="opera"
        	        
                self.runningBrowsers.append(aux)

    def verifyInstalledBrowsers(self):
        config=ChoooserConfig()
        pog = config.getPog()
        if verifyWinManager()=="gnome-shell":
            if pog=="No":
                brAux="firefox"
                brAux2="opera"
            if pog=="opera":
                brAux="firefox"
                brAux2="opera2"
            if pog=="firefox":
                brAux="firefox2"
                brAux2="opera"                
        else:
            brAux="firefox"
            brAux="opera"
        browsers = ["/usr/bin/epiphany","/usr/bin/chromium-browser", 
        "/usr/bin/{0}".format(brAux), "/usr/bin/firefox-trunk",
        "/usr/bin/{0}".format(brAux2), "/usr/bin/google-chrome", 
        "/usr/local/bin/opera"]
        cont=0
        for filename in browsers:
            try:
                FILE = open(filename,"r")
                self.installedBrowsers.append(filename)
            except:
                print "O browser {0} nao esta instalado".format(filename)
            cont+=1            
                        
    def launchLink(self, link,browser):
        if "mailto" in link:
            #open links in gmail, in the chosen browser
            link= "https://mail.google.com/mail?view=cm&tf=0&to={0}".format(link[7:])
        os.system(browser+' "'+link+'" &')
        os.kill(pid, signal.SIGTERM)


class TheChosenWindowGtk:

    chose=Choooser()
    
    def callback(self, widget, l,b):
        #print "Hello again - %s was pressed" % data
        chose.launchLink(l,b)
    # another callback
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def label_box(self, parent, xpm_filename, label_text):
        # Create box for xpm and label
        box = gtk.HBox(False, 0)
        box.set_border_width(2)
     
        # Now on to the image stuff
        image = gtk.Image()
        image.set_from_file(xpm_filename)
     
        # Create a label for the button
        label = gtk.Label(label_text)

        # Pack the pixmap and label into the box 
        box.pack_start(image, False, False, 3)
        box.pack_start(label, False, False, 3)
        image.show()
        label.show()
        return box

    def __init__(self,b,l):
    
        self.cont=-1
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_decorated(False) #no borders
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)#its the border around the buttons
        self.window.set_skip_taskbar_hint(False) #do not appears in the system taskbar
        self.window.set_opacity(0.9)
        self.window.set_default_icon_from_file("{0}/icons/choooser2.png".format(theFolder))
        self.window.stick()#show it up all workspaces
        self.window.set_keep_above(True)#stay above all other windows
        self.statusIcon = gtk.StatusIcon()#faz pastel
        self.statusIcon.set_from_file("{0}/icons/choooser2.png".format(theFolder))
        self.statusIcon.set_visible(True)
        
        print "IMPRIMEEEEE {0}".format(b)
        self.box1 = gtk.HBox(False, 0)
        self.window.add(self.box1)
        
        for aux in b:
            self.cont+=1
            self.button = gtk.Button()
            if "chrome" in b[self.cont]:
                self.box = self.label_box(self.window,
                 "{0}/icons/chrome128.png".format(theFolder), "")
            elif "opera" in b[self.cont]:
                self.box = self.label_box(self.window,
                 "{0}/icons/opera128.png".format(theFolder), "")
            elif "chromium" in b[self.cont]:                
                self.box = self.label_box(self.window, 
                "{0}/icons/chromium128.png".format(theFolder), "")
            elif "firefox-trunk" in b[self.cont]:
                self.box = self.label_box(self.window, 
                "{0}/icons/firefox-ni128.png".format(theFolder), "")
            elif "firefox" in b[self.cont]:
                self.box = self.label_box(self.window, 
                "{0}/icons/firefox128.png".format(theFolder), "")
            else:
                self.box = self.label_box(self.window, 
                "{0}icons/whatahell128.png".format(theFolder), b[self.cont])
            self.button.add(self.box)
            self.box.show()
                #self.button = gtk.Button(b[self.cont])
            self.button.connect("clicked", self.callback, l, b[self.cont])
            self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
            self.box1.pack_start(self.button, True, True, 0)
            self.button.show()
  
        self.box1.show()
        self.window.show()
    def main(self):
        gtk.main()

class TheChosenWindowQT(QtGui.QWidget):

    chose=Choooser()
    
    def vai(self,b):
        chose.launchLink(self.l,b)

    def __init__(self,b,l,parent=None):
        super(TheChosenWindowQT,self).__init__(parent)
        cont=-1
        self.l=l
        mainLayout = QtGui.QGridLayout()
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        #center of screen (that IS kinda pog. #TODO: fix it)
        self.move((screen.width())/2-160, (screen.height())/2-100)
        # no window borders
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) 
        #self.setWindowFlags(QtCore.Qt.WA_TranslucentBackground)
        for aux in b:
            self.b=aux
            cont+=1
            button =  QtGui.QPushButton()
            if "chrome" in aux:
                button.setIcon(QtGui.QIcon("{0}/icons/chrome128.png".format(theFolder)))
            elif "opera" in aux:
                button.setIcon(QtGui.QIcon("{0}/icons/opera128.png".format(theFolder)))
            elif "firefox-trunk" in aux:
                button.setIcon(QtGui.QIcon("{0}/icons/firefox-ni128.png".format(theFolder)))                
            elif "firefox" in aux:
                button.setIcon(QtGui.QIcon("{0}/icons/firefox128.png".format(theFolder)))
            elif "chromium" in aux:
                button.setIcon(QtGui.QIcon("{0}/icons/chromium128.png".format(theFolder)))
            else:
                #browsers whatevers que eu nao dou a minima
                button.setIcon(QtGui.QIcon("{0}/icons/whatahell128.png".format(theFolder)))                
                
            button.setIconSize(QtCore.QSize(100,100))
            
            #funcao de conectar do capeta que nao lembro pq tem que ser assim
            #...mas tem que ser assim!
            self.connect(button, QtCore.SIGNAL('clicked()'),lambda te=aux: self.vai(te))
             
            mainLayout.addWidget(button,0,cont)          

        self.setLayout(mainLayout)
        self.setWindowTitle("Choooser")


if __name__== '__main__':
        #in args[1] will be the URL, and THAT is what we want my son!
        args = sys.argv 
        config=ChoooserConfig()
        try:
            mac = getnode()
            print "MAC {0} ".format(hex(mac))  #why? Because I want!
        except:
            print "Fail to get mac"
       	try:
			systemOS = os.uname()
			print systemOS #it's linux \o/ (or macos, but I dont give a fuck)
			systemOS="linux"
        except:
            #meh (TODO: it will work there ? Maybe when I made a Qt version... maybe...)
            #eh, saporra soh vai funfar soh no linux mesmo....!
		    systemOS = "windows" 
        cont=0
        for aux in args:
            cont+=1
        if cont < 2:
           print "Humnnn, that's an error! Not enough arguments. Exiting!"
           if verifyWinManager()=="gnome-shell":
               pog = config.getPog()
               #se nao tem argumento e esta no gnome-shell
               #provavelmente eh devido a gambi mega-boga do programa
               #e por isso tem que abrir o browser[2]
               #e eh isso ae
               if pog=="No":
                   pass
               elif pog=="firefox":
                   os.system("firefox2")
               elif pog=="opera":
                   os.system("opera2")         
               #caralho, pog com arquivo de configuracao!!!          
           else:
               pass
               #nem lembro mais pq do pass. Acho que é pra tratar o unity depois
               
           os.kill(pid, signal.SIGTERM)
           
        if args[1].lower() == "--install":
            if cont >= 3:
                if "-f" in args[2].lower():
                #-f tem que vir depois de --install mesmo, e fodase
                #depois vou usar um argparser. depois!
                
                #Força a bagaça. Obviamente pode dar merda (tipo f*der o browser)
                    installChoooser("/usr/local/bin/", "opera", True)
    	    else:
                installChoooser("/usr/local/bin/", "opera", False)
            os.kill(pid, signal.SIGTERM)
           
        if systemOS=="linux":
            chose = Choooser()
            chose.verifyRunningBrowsers()
            chose.verifyInstalledBrowsers()
            run = chose.runningBrowsers
            installed = chose.installedBrowsers
 
            cont=0
            print args[1]
            for aux in run:
                  cont+=1
            if cont==0: #nenhum browser aberto; ver os instalados, perguntar em qual abrir
                    if config.getWinManager()=="qt":
                        app = QtGui.QApplication(sys.path)
                        pbarwin = TheChosenWindowQT(installed,args[1])
                        pbarwin.show()
                        sys.exit(app.exec_())
                        
                    #elif config.getWinManager()=="gtk":
                    else: #gtk
                        theWindow = TheChosenWindowGtk(installed,args[1])
                        theWindow.main()                        
                        
            elif cont==1: 
                    #um soh browser aberto, abre o link nele
                    chose.launchLink(args[1],run[0])

            elif cont>1: #mais de um browser aberto
                    if config.getNotify():
                        os.system("notify-send 'Escolha o browser'")
                    
                    if config.getWinManager()=="gtk":
                        app = QtGui.QApplication(sys.path)
                        pbarwin = TheChosenWindowQT(run,args[1])
                        pbarwin.show()
                        sys.exit(app.exec_())                    
                    #elif config.getWinManager()=="gtk":                        
                    else: #gtk
                        theWindow = TheChosenWindowGtk(run,args[1])
                        theWindow.main()

            else:
                    print "F#c$ this sh$t, I'm getting the bazooka!"  
        else:
            #others systems
            print "Error number 42: BIOS problem. Please contact your neighbour. Exiting!"
            os.kill(pid, signal.SIGTERM)

        #filename="/home/bfc/Dropbox/Projects/testelegal.txt"
        #FILE = open(filename,"")
