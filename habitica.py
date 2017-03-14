#!/usr/bin/python
# -*- coding: utf-8 -*-
#Podria traducir un poco
#Y hacerlo multi lenguaje, aunque no se como
from __future__ import print_function

class MyError(Exception):
   pass
   #return Error
  
  
def habitica(quiet=False,html=False,htmls=False,script=False,semanas=1,daily=False,to_do=False,prefijar_daily="",prefijar_to_do="",api_user="",api_key=""):    
    """Muestra tareas diarias y pendientes (con fecha) de habítica. La información del usuario puede ser 
       introducida en el archivo keys.py, o introducida con las opciones api_user y api_key
       
       Opciones
       
       quiet[False]       Sin mensajes de error
       html[False]        Salida html sin script para listas deplegables.
       htmls[False]       Salida html con script para listas deplegables
       script[False]      Solo muestra el script para listas deplegables.
       semanas[1]         Semanas extra a mostrar.
       daily[False]       Solo muestra las tareas "diarias"
       to_do[False]       Solo muestra las tareas pendientes
       prefijar_daily[""] Prefija las tareas diarias con la cadena suministrada.
       prefijar_to_do[""] Prefija las tareas pendientes la cadena suministrada.
       api_user[""]       Introduce la x-api-user de Habitica 
                           (https://habitica.com/#/options/settings/api). 
                           Sobreescribe el valor en keys.py
       api_key[""]        Introduce la x-api-key de Habitica 
                           (https://habitica.com/#/options/settings/api).
                           Sobreescribe el valor en keys.py"""

    import requests
    #import sys
    #import os
    from datetime import datetime
    
    salida=""

    
    if script:
            salida+="""
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
    </script>\n"""
            #if verbose:
               #print (salida)
               #sys.exit(0)
            #else:
            return salida
            
    
    if quiet:
        #import sys
        sys.stderr=open("/dev/null","w")
    
    #Esto no puede estar hard-coded!!!
    #Puede introducirse de un archivo a traves de un import (ya está) o con kwallet (en el plasmoide)
    if not api_user:
      try:
        import keys
        api_user=keys.api_user
      except Exception:
        raise MyError('Error: Necesita un token.\nVea https://habitica.com/#/options/settings/api\n')
    if not api_key:
      try:
        import keys
        api_key=keys.api_key
      except Exception:
        raise MyError('Error: Necesita un token.\nVea https://habitica.com/#/options/settings/api\n')        
        
    #print(api_key)
        
        
        
        
        #else:
           #raise MyError('Error: Necesita una identificación de usuario.\nVea https://habitica.com/#/options/settings/api\n')
           
        #if args.api_key and not api_key:
           #api_key=args.api_key
        #elif keys.api_key and not api_key:
           #api_key=keys.api_key
        #else:
             #raise MyError('Error: Necesita un token.\nVea https://habitica.com/#/options/settings/api\n')
    #except Exception:
        #if args.api_user and not api_user:
           #api_user=args.api_user
        #else:
          ##if verbose:
              ##salida+= "Error: Necesita una identificación de usuario.\nVea https://habitica.com/#/options/settings/api\n"
              ##print (salida,file=sys.stderr)
              ##sys.exit(1)
          ##else:
           #raise MyError('Error: Necesita una identificación de usuario.\nVea https://habitica.com/#/options/settings/api\n')
           
        #if args.api_key:
           #api_key=args.api_key
        #else:
           #raise MyError('Error: Necesita un token.\nVea https://habitica.com/#/options/settings/api\n')
###########################
    
      
    payload = {"Content-Type":"application/json",'x-api-user': api_user,'x-api-key': api_key, }
    
    
    #El domingo es el dia 6, de manera que sumo los dias restantes de la semana.

    periodo=7*int(semanas)+6-datetime.today().weekday()
    
    semana = ["m","t","w","th","f","s","su"]
    semana_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    mes = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
    
    calen = {}
    
    
    #Los dos siguientes no son considerados mensajes de error, sino información de la data recibida (o no recibida)
    try:
        u=requests.get("https://habitica.com/api/v3/tasks/user", headers=payload,timeout=30)
        U=u.json()
    except Exception:
        salida+="No se pudo conectar\n"
        #if verbose:
           #print (salida)
           #sys.exit(1)
        #else:
        return salida
    try:
      if U["data"]:
          pass
    except Exception:
          salida+="No se pudo obtener la data\n"
          #if verbose:
             #print (salida)
             #sys.exit(1)
          #else:
          return salida
    
    for i in U["data"]:
      if not to_do:
        if i["type"]== "daily" and i.has_key("everyX"):
    #        print i["text"],i["everyX"],i["startDate"],i["repeat"]
            dia = datetime.strptime(i["startDate"], '%Y-%m-%dT%H:%M:%S.%fZ').toordinal()
            diasiguiente = datetime.today().toordinal()+i["everyX"]-(datetime.today().toordinal()- dia)%i["everyX"]
            #Primero hoy
            if not (datetime.today().toordinal()-dia)%i["everyX"]:
               if i["repeat"][semana[datetime.today().weekday()]]:
                  if i["completed"]:
                      calen.setdefault(datetime.today().toordinal(),[]).append(prefijar_daily+i["text"]+" (listo)")
                  else:
                      calen.setdefault(datetime.today().toordinal(),[]).append(prefijar_daily+i["text"])
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
                        calen.setdefault(diasiguiente.toordinal(),[]).append(prefijar_daily+i["text"])
                    j+=i["everyX"]
                    
      if not daily:
         if i["type"]== "todo" and i.has_key("date"):
            if i["date"]:
               diasiguiente = datetime.strptime(i["date"], '%Y-%m-%dT%H:%M:%S.%fZ').toordinal()
               if diasiguiente <= datetime.today().toordinal()+periodo:
                   calen.setdefault(diasiguiente,[]).append(prefijar_to_do+i["text"])
                    
    claves=calen.keys()
    Firstclose=False
    claves.sort()
    
    if html or htmls:
        if htmls:
            salida+= """
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
    </script>\n"""
        #print "<ul>"
        salida+= '<meta charset="utf-8"/>\n'
        cuentasemana = -1
        for j in claves:
            if j == datetime.today().toordinal():
               salida+="<ul>\n  <li><dl  onclick=\"swap('today');return false;\"><a style=\"text-decoration: underline;\"><b>Hoy:</b></a></dl><ul id='today' style='display: ;'>\n"
            else:
                if cuentasemana != datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]:
                    cuentasemana = datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]
                    if not j == datetime.today().toordinal() and Firstclose:
                        salida+= "</div>\n"
                        salida+= "</li>\n </ul>\n"
                    if cuentasemana:
                        salida+= "<ul>\n  <li><dl  onclick=\"swap('semana%d');return false;\"><a style=\"text-decoration: underline;\"><b>Dentro de %d semana%s:</b></a></dl>"%(cuentasemana,cuentasemana,"s" if cuentasemana > 1 else "")+"\n"
                        salida+= "   <div id='semana%d' style='display:none ;'>\n"%(cuentasemana)+"\n"
                    else:
                        salida+= "<ul>\n  <li><dl  onclick=\"swap('estasemana');return false;\"><a style=\"text-decoration: underline;\"><b>En esta semana:</b></a></dl>\n"
                        salida+= "   <div id='estasemana' style='display: ;'>\n"
        #            cambiasemana = False
                    Firstclose=True
                salida+= "   <ul>\n     <li><a>     <i>"+datetime.fromordinal(j).strftime("%s %%d de %s de %%Y"%(semana_es[datetime.fromordinal(j).weekday()],mes[datetime.fromordinal(j).month-1]))+":</i></a>\n"
                salida+= "       <ul>\n"
            for k in calen[j]:
                salida+= "        <li><a>          "+k.encode("utf8")+"</a></li>\n"
            salida+= "       </ul>\n     </li>\n   </ul>\n"
        salida+= "  </div></li>\n </ul>\n"
    #print "</ul>"
    else:
        cuentasemana = -1
        for j in claves:
            if j == datetime.today().toordinal():
                salida+= "Hoy:\n"
            else:
                if cuentasemana != datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]:
                    cuentasemana = datetime.fromordinal(j).isocalendar()[1]-datetime.today().isocalendar()[1]
                    if cuentasemana:
                        salida+= "Dentro de %d semana%s:"%(cuentasemana,"s" if cuentasemana > 1 else "")+"\n"
                    else:
                        salida+= "En esta semana:\n"
        #            cambiasemana = False
                salida+= "     "+datetime.fromordinal(j).strftime("%s %%d de %s de %%Y"%(semana_es[datetime.fromordinal(j).weekday()],mes[datetime.fromordinal(j).month-1]))+":\n"
            for k in calen[j]:
                salida+= "          "+k.encode("utf8")+"\n"
    
    return salida
    
if __name__=="__main__":
       import argparse
       import sys
       import os
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
       parser.add_argument('-au','--api-user', help="Introduce la x-api-user de Habitica (https://habitica.com/#/options/settings/api). Sobreescribe el valor en %s/keys.py"%(os.path.dirname(os.path.realpath(sys.argv[0]))))
       parser.add_argument('-ak','--api-key', help="Introduce la x-api-key de Habitica (https://habitica.com/#/options/settings/api). Sobreescribe el valor en %s/keys.py"%(os.path.dirname(os.path.realpath(sys.argv[0]))))
       
       args = parser.parse_args()
       
       #if __name__ != "__main__" and not args.verbose:
       #if __name__ != "__main__":
           #verbose=False
           #Si no es ejecutado directamente tomo el valor dado a la función
           #args.script = script
           #args.to_do = to_do
           #args.daily = daily
           #args.semanas=semanas
           #args.prefijar_daily=prefijar_daily
           #args.prefijar_to_do=prefijar_to_do
           #args.quiet = quiet
           #args.html = html
           #args.htmls = htmls
       #else:
       #verbose=True
       print(habitica(quiet=args.quiet,html=args.html,htmls=args.htmls,script=args.script,semanas=args.semanas,daily=args.daily,to_do=args.to_do,\
         prefijar_daily=args.pd+args.prefijar_daily,prefijar_to_do=args.pt+args.prefijar_to_do,api_user=args.api_user,api_key=args.api_key))
       #print (args.api_user+"")
                
                