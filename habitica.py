# -*- coding: utf-8 -*-

import requests
import sys
import os
from datetime import datetime


#Podria traducir un poco
#Y hacerlo multi lenguaje, aunque no se como
import argparse
parser = argparse.ArgumentParser(description=u'Muestra tareas diarias y pendientes (con fecha) de habítica. La información del usuario puede ser introducida en el archivo %s/keys.py, o introducida con las opciones --api-user y --api-key'%(os.path.dirname(os.path.realpath(sys.argv[0]))))
parser.add_argument('-q','--quiet', action='store_true',  help='Sin mensajes de error.')
parser.add_argument('--html', action='store_true',  help='Salida html sin script para listas deplegables.')
parser.add_argument('-hs','--htmls', action='store_true',  help='Salida html con script para listas deplegables.')
parser.add_argument('--script', action='store_true',  help='Solo muestra el script para listas deplegables y sale.')
parser.add_argument('-s','--semanas', default=1, help="Semanas extra a mostrar (default 1)")
#terminar
parser.add_argument('-d','--daily', action='store_true',  help='Solo muestra las tareas \"diarias\"')
#Terminar
parser.add_argument('-t','--to-do', action='store_true',  help='Solo muestra las tareas pendientes')
#Terminar
parser.add_argument('--prefijar-daily', action='store_const',default="",const="(repite)",  help=u'Prefija las tareas diarias con (repite)')
parser.add_argument('--prefijar-to-do', action='store_const',default="",const="(pendiente)",  help=u'Prefija las tareas pendientes con (pendiente)')
parser.add_argument('-pd', action='store_const',default="",const="(R)",  help=u'Prefija las tareas diarias con (R)')
parser.add_argument('-pt', action='store_const',default="",const="(P)",  help=u'Prefija las tareas pendientes con (P)')
parser.add_argument('-au','--api-user', help="Introduce la x-api-user de Habitica (https://habitica.com/#/options/settings/api). Sobreescrive el valor en %s/keys.py"%(os.path.dirname(os.path.realpath(sys.argv[0]))))
parser.add_argument('-ak','--api-key', help="Introduce la x-api-key de Habitica (https://habitica.com/#/options/settings/api). Sobreescrive el valor en %s/keys.py"%(os.path.dirname(os.path.realpath(sys.argv[0]))))

args = parser.parse_args()

if args.script:
        print """
    <script type="text/javascript">
 setTimeout(function(){window.stop()},30000)
 function swap(targetId){
  if (document.getElementById){
        target = document.getElementById(targetId);
            if (target.style.display == "none"){
                target.style.display = "";
            } else{
                target.style.display = "none";
            }
                
  }
}
</script>"""
        exit(0)
        

if args.quiet:
    #import sys
    sys.stderr=open("/dev/null","w")

#Esto no puede estar hard-coded!!!
#Puede introducirse de un archivo a traves de un import (ya está) o con kwallet (en el plasmoide)
import keys
if keys.api_user:
   api_user=keys.api_user
elif args.api_user:
   api_user=args.api_user
else:
   print "Error: Necesita una identificación de usuario.\nVea https://habitica.com/#/options/settings/api"
   exit(1)
   
if keys.api_key:
   api_key=keys.api_key
elif args.api_key:
   api_key=args.api_key
else:
   print "Error: Necesita un token.\nVea https://habitica.com/#/options/settings/api"
   exit(1)
  
payload = {"Content-Type":"application/json",'x-api-user': api_user,'x-api-key': api_key, }


#El domingo es el dia 6, de manera que sumo los dias restantes de la semana.
periodo=7*int(args.semanas)+6-datetime.today().weekday()

semana = ["m","t","w","th","f","s","su"]
semana_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
mes = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

calen = {}

try:
    u=requests.get("https://habitica.com/api/v3/tasks/user", headers=payload,timeout=30)
    U=u.json()
except:
    print "No se pudo conectar"
    exit(1)

for i in U["data"]:
  if not args.to_do:
    if i["type"]== "daily" and i.has_key("everyX"):
#        print i["text"],i["everyX"],i["startDate"],i["repeat"]
        dia = datetime.strptime(i["startDate"], '%Y-%m-%dT%H:%M:%S.%fZ').toordinal()
        diasiguiente = datetime.today().toordinal()+i["everyX"]-(datetime.today().toordinal()- dia)%i["everyX"]
        #Primero hoy
        if not (datetime.today().toordinal()-dia)%i["everyX"]:
	   if i["repeat"][semana[datetime.today().weekday()]]:
              if i["completed"]:
                  calen.setdefault(datetime.today().toordinal(),[]).append(args.pd+args.prefijar_daily+i["text"]+" (listo)")
              else:
                  calen.setdefault(datetime.today().toordinal(),[]).append(args.pd+args.prefijar_daily+i["text"])
        #Los demas dias
        j=0
        #Todo este bloque podría ser escrito mejor, pero meh...
        if diasiguiente <= datetime.today().toordinal()+periodo:
            #print i["text"],diasiguiente,datetime.today().toordinal()+periodo
            while j<periodo:
#                print i["text"]
                diasiguiente = datetime.fromordinal(datetime.today().toordinal()+i["everyX"]-(datetime.today().toordinal()- dia)%i["everyX"]+j)
                #print i["text"],diasiguiente,i["repeat"],j,diasiguiente.toordinal()
                #La segunda parte del if es un sanity check necesario.
                if i["repeat"][semana[diasiguiente.weekday()]] and diasiguiente.toordinal() <= datetime.today().toordinal()+periodo:
#                    print i["text"]+u" se repetirá el día "+diasiguiente.strftime("%%d de %s de %%Y"%(mes[diasiguiente.month-1]))
                    calen.setdefault(diasiguiente.toordinal(),[]).append(args.pd+args.prefijar_daily+i["text"])
                j+=i["everyX"]
                
  if not args.daily:
     if i["type"]== "todo" and i.has_key("date"):
        if i["date"]:
	   diasiguiente = datetime.strptime(i["date"], '%Y-%m-%dT%H:%M:%S.%fZ').toordinal()
	   if diasiguiente <= datetime.today().toordinal()+periodo:
	       calen.setdefault(diasiguiente,[]).append(args.pt+args.prefijar_to_do+i["text"])
                
#import pprint
#pprint.pprint(calen)
#dia = datetime.strptime('2016-10-30T04:00:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
claves=calen.keys()
Firstclose=False
claves.sort()

if args.html or args.htmls:
    if args.htmls:
        print """
    <script type="text/javascript">
 setTimeout(function(){window.stop()},30000)
 function swap(targetId){
  if (document.getElementById){
        target = document.getElementById(targetId);
            if (target.style.display == "none"){
                target.style.display = "";
            } else{
                target.style.display = "none";
            }
                
  }
}
</script>"""
    #print "<ul>"
    print '<meta charset="utf-8"/>'
    cuentasemana = -1
    for j in claves:
	if j == datetime.today().toordinal():
	    print "<ul>\n  <li><dl  onclick=\"swap('today');return false;\"><a style=\"text-decoration: underline;\"><b>Hoy:</b></a></dl><ul id='today' style='display: ;'>"
	else:
	    if cuentasemana != datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]:
		cuentasemana = datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]
		if not j == datetime.today().toordinal() and Firstclose:
		    print "</div>"
		    print "</li>\n </ul>"
		if cuentasemana:
		    print "<ul>\n  <li><dl  onclick=\"swap('semana%d');return false;\"><a style=\"text-decoration: underline;\"><b>Dentro de %d semana%s:</b></a></dl>"%(cuentasemana,cuentasemana,"s" if cuentasemana > 1 else "")
		    print "   <div id='semana%d' style='display:none ;'>\n"%(cuentasemana)
		else:
		    print "<ul>\n  <li><dl  onclick=\"swap('estasemana');return false;\"><a style=\"text-decoration: underline;\"><b>En esta semana:</b></a></dl>"
		    print "   <div id='estasemana' style='display: ;'>\n"
    #            cambiasemana = False
                Firstclose=True
	    print "   <ul>\n     <li><a>     <i>"+datetime.fromordinal(j).strftime("%s %%d de %s de %%Y"%(semana_es[datetime.fromordinal(j).weekday()],mes[datetime.fromordinal(j).month-1]))+":</i></a>"
	    print "       <ul>"
	for k in calen[j]:
	    print "        <li><a>          "+k.encode("utf8")+"</a></li>\n"
	print "       </ul>\n     </li>\n   </ul>\n"
    print "  </div></li>\n </ul>"
	#print "</ul>"
else:
    cuentasemana = -1
    for j in claves:
	if j == datetime.today().toordinal():
	    print "Hoy:"
	else:
	    if cuentasemana != datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]:
		cuentasemana = datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]
		if cuentasemana:
		    print "Dentro de %d semana%s:"%(cuentasemana,"s" if cuentasemana > 1 else "")
		else:
		    print "En esta semana:"
    #            cambiasemana = False
	    print "     "+datetime.fromordinal(j).strftime("%s %%d de %s de %%Y"%(semana_es[datetime.fromordinal(j).weekday()],mes[datetime.fromordinal(j).month-1]))+":"
	for k in calen[j]:
	    print "          "+k.encode("utf8")+""
	
  
                
                