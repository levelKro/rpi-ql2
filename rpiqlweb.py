#!/usr/bin/python3
import urllib.parse as urlparse
import http.server
import socketserver
import os
import subprocess
import configparser
import json
import datetime
import time
from threading import Timer
from urllib.parse import parse_qs
from os import path
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join, isdir
from subprocess import Popen

print("Starting Web Server script")
scriptpath=os.path.dirname(os.path.realpath(__file__))+"/"
print(" * Loading configuration file: "+scriptpath+"config.ini")
config = configparser.ConfigParser()
config.read(scriptpath+"config.ini", encoding='utf-8')
print("Setting web directory")
WEBPATH=scriptpath + config["web"]["path"]
#os.chdir(WEBPATH)

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    update = False
    def do_GET(self):
        if self.path == '/':
            self.path = "/index.html"
        pathSplit = self.path.split("?")
        try:
            self.runPage(pathSplit[0],pathSplit[1])
        except:
            self.runPage(pathSplit[0])
            pass
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        postDatas = post_data.decode("utf-8")
        if self.path == '/':
            self.path = "/index.html"
        pathSplit = self.path.split("?")
        try:
            self.runPage(pathSplit[0],pathSplit[1],postDatas)
        except:
            self.runPage(pathSplit[0],"",postDatas)
            pass

    def runPage(self,page,getDatas="",postDatas=""):
        pathSection = page.split("/")
        print("** URL: "+page)
        print("** _GET: "+getDatas)
        print("** _POST: "+postDatas)
        
        try:
            getDatas = urlparse.parse_qs(getDatas.replace('"',"''"))
        except:
            getDatas=""
            pass
        try:
            postDatas = urlparse.parse_qs(postDatas.replace('"',"''"))
        except:
            postDatas=""
            pass
        
        if path.exists(WEBPATH+page) is True:
            self.path = page
            try:
                f = open(WEBPATH+self.path, 'rb')
            except OSError:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes('Document requested is not found.', "utf-8"))
                return None

            ctype = self.guess_type(self.path)
            fs = os.fstat(f.fileno())

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified",
                self.date_time_string(fs.st_mtime))
            self.end_headers()            

            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()
            ##return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif pathSection[1] == "api":
            outputJson={"result":"error","reason":"Invalid action"}
            values=""
            if pathSection[2] == "images":
                imgs=[]
                for x in os.listdir("images"):
                    if x.endswith(".jpg") or x.endswith(".png") or x.endswith(".ico"):
                        imgs.append(x)
                        
                outputJson={"result":"success","reason":"Get images","images":imgs}
            elif pathSection[2] == "image":
                try:
                    f = open("images/"+pathSection[3], 'rb')
                except OSError:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes('Document requested is not found.', "utf-8"))
                    return None

                ctype = self.guess_type("images/"+pathSection[3])
                fs = os.fstat(f.fileno())

                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-type", ctype)
                self.send_header("Content-Length", str(fs[6]))
                self.send_header("Last-Modified",
                    self.date_time_string(fs.st_mtime))
                self.end_headers()            

                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
                return
            elif pathSection[2] == "templates":
                templates=[]
                for x in os.listdir("templates"):
                    if x.endswith(".rpiql"):
                        templates.append(x)
                    
                outputJson={"result":"success","reason":"Get templates","templates":templates}
            
            elif pathSection[2] == "template":
                result="{"
                template = configparser.ConfigParser()
                template.read("templates/" + pathSection[3] + ".rpiql", encoding='utf-8')
                for s in template.sections():
                    result=result+'"'+str(s)+'":{'
                    for o,v in template.items(s):
                        result=result+'"'+str(o)+'":"'+str(v)+'",'
                    result=result+'},'
                    
                result=result+"}"
                result=result.replace(",}","}")

                outputJson={"result":"success","reason":"Reading template.","datas":json.loads(result)}

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "print":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outputJson={"result":"error","reason":"Invalid action"}
            values=""
            try:
                if(int(postDatas['copie'])<=0):
                    copie=1
                else:
                    copie=int(postDatas['copie'])
            except:
                copie=1
               
            try:
                if pathSection[2] == "exemple":
                    if(postDatas.get('text') is not None):
                        values=values+' -a text -k "'+str(copie)+'" -t "'+str(postDatas['text'])+'"'
                        outputJson={"result":"success","reason":"Printing text label."}
                        self.goPrint(str(values))
                    else:
                        outputJson={"result":"error","reason":"Text is missing."}
                        
                elif pathSection[2] == "cli":
                    print("CLI")
                    if(postDatas.get('data') is not None):
                        params=str(postDatas['data']).replace('["',"").replace('"]',"").replace("''",'"')
                        outputJson={"result":"success","reason":"Send to printer script the parameters."}
                        self.goPrint(" "+params)
                    else:
                        print("NO PARAMS")
                        outputJson={"result":"error","reason":"No parameter to send to printer script."}
            except:
                outputJson={"result":"error","reason":"Error when processing the request."}
                pass
                    
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "manage":
            print(" * Loading configuration file: "+scriptpath+"config.ini")
            config = configparser.ConfigParser()
            config.read(scriptpath+"config.ini", encoding='utf-8')
            outputJson={"result":"error","reason":"Invalid action"}
            if(postDatas.get('password') is not None):
                if(str(postDatas.get('password')).replace("['","").replace("']","")==str(config['web']['adminpass'])):
                    try:
                        if pathSection[2] == "reboot":
                            outputJson={"result":"success","reason":"Rebooting system..."}
                            tmp=subprocess.Popen(['./cli-reboot.sh'])
                        elif pathSection[2] == "poweroff":
                            outputJson={"result":"success","reason":"Poweroff system..."}
                            tmp=subprocess.Popen(['./cli-poweroff.sh'])
                        elif pathSection[2] == "config":
                            if pathSection[3] == "load":
                                result="{"
                                readconfig = configparser.ConfigParser()
                                readconfig.read('config.ini', encoding='utf-8')
                                for s in readconfig.sections():
                                    result=result+'"'+str(s)+'":{'
                                    for o,v in readconfig.items(s):
                                        if(str(o)!="adminpass"):
                                            result=result+'"'+str(o)+'":"'+str(v)+'",'
                                    result=result+'},'
                                    
                                result=result+"}"
                                result=result.replace(",}","}")

                                outputJson={"result":"success","reason":"Reading configuration.","datas":json.loads(result)}
                                
                            elif pathSection[3] == "save":
                                saveconfig = configparser.ConfigParser()
                                saveconfig.read('config.ini', encoding='utf-8')
                                
                                if(postDatas.get('model') is not None):
                                    saveconfig['printer']['model']=str(postDatas['model']).replace("['","").replace("']","")
                                if(postDatas.get('usb') is not None):
                                    saveconfig['printer']['usb']=str(postDatas['usb']).replace("['","").replace("']","")
                                if(postDatas.get('serial') is not None):
                                    saveconfig['printer']['serial']=str(postDatas['serial']).replace("['","").replace("']","")
                                    
                                with open('config.ini', 'w', encoding='utf-8') as configfile:    # save
                                    saveconfig.write(configfile)
                                
                                result="{"
                                saveconfig = configparser.ConfigParser()
                                saveconfig.read('config.ini', encoding='utf-8')
                                for s in saveconfig.sections():
                                    result=result+'"'+str(s)+'":{'
                                    for o,v in saveconfig.items(s):
                                        if(str(o)!="adminpass"):
                                            result=result+'"'+str(o)+'":"'+str(v)+'",'
                                    result=result+'},'
                                    
                                result=result+"}"
                                result=result.replace(",}","}")

                                outputJson={"result":"success","reason":"Saving configuration.","datas":json.loads(result)}                                    
                            else:
                                print("Error in config")
                                outputJson={"result":"error","reason":"This action is not valid."}
                        else:
                           outputJson={"result":"error","reason":"Request is not valid."} 
                    except Exception as e:
                        print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
                        outputJson={"result":"error","reason":"Error when processing the request."}
                        pass
                else:    
                    outputJson={"result":"error","reason":"Password is incorrect."}
            else:
                outputJson={"result":"error","reason":"No password or not in POST method."}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()                
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes('Document requested is not found.', "utf-8"))
        return
        
    def goPrint(self,values):
        strclean=str(values).replace("['","").replace("']","")
        print("Send to printer : "+strclean)
        try:
            os.system('python3 rpiql.py'+strclean)
        except:
            ##tmp=subprocess.Popen('python3 core.py'+str(values).replace("['","").replace("']",""), shell=True)
            print("Can't run the command.")
 
def start():
    pcStats = MyHttpRequestHandler
    pcStatsServer = socketserver.TCPServer(("0.0.0.0", int(config['web']['port'])), pcStats)
    print("*** RUNNING WEB SERVER AT PORT "+str(config['web']['port'])+" ***")
    pcStatsServer.serve_forever()

            
start()            
            