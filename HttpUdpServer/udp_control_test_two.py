#!/usr/bin/env python

# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------

'''
  This solution relying on UDP is simple, light-weight and reactive.
  Only one socket is sufficient to handle the simultaneous dialogs
    with the multiple robots (taking advantage of broadcast).
  UDP is very light-weight for the ESP8266; it can easily support many
    requests per second.
  Furthermore, the dialog is bidirectionnal; this enables the delivery
    of events from the robots.

  This solution should be prefered to the one relying on HTTP which
    is complicated and slow.
'''
import sys
import socket
import traceback
import time
import select
import threading
import struct
import json

if 0:
  ROBOT_BROADCAST='10.0.255.255' # RoboCanes
elif 0:
  ROBOT_BROADCAST='192.168.1.255' # BrainCooker
elif 1:
  ROBOT_BROADCAST='10.3.141.255' # RaspBerryPDL
else:
  ROBOT_BROADCAST='192.168.4.255' # Amirobot
ROBOT_PORT=9876

ROBOT_COLORS=['red', 'green', 'blue', 'white']
ROBOT_SCAN_PERIOD=5.
ROBOT_COMMAND_PERIOD=100.0
ROBOT_SCAN_DISPLAY=1.

SERVER_PORT=8051

(MSG_IDENT, MSG_COMMAND, MSG_EVENT)=(0, 1, 2)

class Record:
  def __init__(self, **kw):
    self.update(**kw)
  #
  def update(self, **kw):
    self.__dict__.update(**kw)
  #
  def get(self, attr_name, default=None):
    return getattr(self, attr_name, default)

#-----------------------------------------------------------------------------

def handle_ident(app, from_addr, ident):
  if ident<0 or ident>=len(app.robots):
    sys.stderr.write('!!! unknown robot identifier: %d !!!\n'%ident)
    return
  r=app.robots[ident]
  with r.lock:
    r.last_seen=app.now
    ip_addr=from_addr[0]
    if r.ip_addr!=ip_addr:
      if r.ip_addr:
        sys.stderr.write('!!! robot %d/%s changed from %s to %s !!!\n'
                         %(ident, r.color, r.ip_addr, ip_addr))
      else:
        sys.stderr.write('robot %d/%s found at %s\n'
                         %(ident, r.color, ip_addr))
      r.ip_addr=ip_addr
    else:
      # sys.stderr.write('robot %d/%s still at %s\n'%(ident, r.color, ip_addr))
      pass

def handle_event(app, from_addr, ident, event):
  if ident<0 or ident>=len(app.robots):
    sys.stderr.write('!!! unknown robot identifier: %d !!!\n'%ident)
    return
  r=app.robots[ident]
  ip_addr=from_addr[0]
  with r.lock:
    if r.ip_addr==ip_addr:
      r.last_seen=app.now
      sys.stderr.write('event %d from robot %d/%s\n'
                       %(event, ident, r.color))

def handle_incoming(app, from_addr, msg):
  if(len(msg)==0):
    print("INCOMING EMPTY MESSAGE FROM", from_addr)
    return
  print("INCOMING from ", from_addr, "with msg[0] : ", msg[0])
  if bytes==str: # python 2
    msg=[ord(b) for b in msg]
  if len(msg)<1:
    return
  if msg[0]==MSG_IDENT:
    if len(msg)>=2:
      handle_ident(app, from_addr, msg[1])
    return
  if msg[0]==MSG_EVENT:
    if len(msg)>=3:
      handle_event(app, from_addr, msg[1], msg[2])
    return

def scan_robots(app):
  print("**** SCAN ROBOTS **** ")
  msg=bytearray(1)
  msg[0]=MSG_IDENT
  app.udp_socket.sendto(msg, (ROBOT_BROADCAST, ROBOT_PORT))

def scan_display(app):
  print("*SCAN DISPLAY*"),

def command_robots(app, robot=None):
  print("**** COMMAND ROBOTS ****")
  robots=app.robots if robot is None else [robot]
  delay=3.0*ROBOT_SCAN_PERIOD;
  for r in robots:
    with r.lock:
      if r.last_seen is not None and r.last_seen+delay<app.now:
        sys.stderr.write('!!! lost robot %d/%s at %s !!!\n'
                         %(r.ident, r.color, r.ip_addr))
        r.last_seen=None
        r.ip_addr=None
      if r.ip_addr:
        msg=bytearray(3)
        msg[0]=MSG_COMMAND
        msg[1]=r.left
        msg[2]=r.right
        print("Sending Robot command : "),
        print("r.ip : ", r.ip_addr),
        print(" r.color :", r.color),
        print(" r.left : ", r.left),
        print(" r.right : ", r.right)
        try:
          app.udp_socket.sendto(msg, (r.ip_addr, ROBOT_PORT))
        except:
          traceback.print_exc()
          pass

#-----------------------------------------------------------------------------

def handle_control(app, control):

  zone_direction=app.zone_direction

  #print("////////////////////////////////////////////////////////////////////"+zone_direction)

  print('TEST',zone_direction)

  # sys.stderr.write('--> %s\n'%cmd)
  try:
    control=control.split()

    if zone_direction==b'STOP':
      r=app.robots[2]
      with r.lock:
        r.left=90
        r.right=90
      command_robots(app, r)

    if zone_direction==b'AVANT':
      r=app.robots[2]
      with r.lock:
        r.left=180
        r.right=0
      command_robots(app, r)


    if zone_direction==b'ARRIERE':
      r=app.robots[2]
      with r.lock:
        r.left=0
        r.right=180
      command_robots(app, r)


    if zone_direction==b'AVANT DROIT':
      r=app.robots[2]
      with r.lock:
        r.left=180
        r.right=45
      command_robots(app, r)


    if zone_direction==b'AVANT GAUCHE':
      r=app.robots[2]
      with r.lock:
        r.left=45
        r.right=0
      command_robots(app, r)

    if zone_direction==b'ARRIERE GAUCHE':
      r=app.robots[2]
      with r.lock:
        r.left=0
        r.right=45
      command_robots(app, r)

    if zone_direction==b'ARRIERE DROIT':
      r=app.robots[2]
      with r.lock:
        r.left=45
        r.right=180
      command_robots(app, r)

    if zone_direction==b'DROITE':
      r=app.robots[2]
      with r.lock:
        r.left=180
        r.right=180
      command_robots(app, r)

    if zone_direction==b'GAUCHE':
      r=app.robots[2]
      with r.lock:
        r.left=0
        r.right=0
      command_robots(app, r)

  except:
    traceback.print_exc()
    pass
  return b''

def main_page(app):
  content=br'''
<!DOCTYPE html>
<html>
<head>
<script>
window.APPLI={};


APPLI.log=function(msg)
{
  var log_area=document.getElementById('log_area');

  // Make an instance of two and place it on the page.
   var visu_area= document.getElementById('visu_area');
   //visu_area.innerHTML = "TEST";


   //APPLI.two.clear()
   //APPLI.two.appendTo(visu_area);

  //alert(app.coords[0])
  //alert(app.coords[0])
  //var circle = APPLI.two.makeCircle(Math.floor(55+Math.random() * Math.floor(390)), 55+Math.floor(Math.random() * Math.floor(390)), 30);

   //var circle = APPLI.two.makeCircle(Math.floor(55+med_x), 55+Math.floor(med_y), 30);
   //circle.fill = "#ffffff";
   //circle.noStroke();
   //circle.fill = '#FF8000';
   //circle.stroke = 'orangered';
   //APPLI.two.update();

    //APPLI.zone_direction=zone_direction;
    //APPLI.send_direction(zone_direction);

};

APPLI.addRobots = function(coords){
  APPLI.two.clear();

  var rect = APPLI.two.makeRectangle(250, 250, 500, 500);

  rect.fill = "#efefef";
  //rect.noStroke();
  rect.stroke = "#a8a8a8";
  rect.linewidth = 50;

   var visu_area = document.getElementById('visu_area');
   APPLI.two.appendTo(visu_area);

   for(var i=0; i<coords.length/2; i++){
       if (typeof coords[i] !== 'undefined' && typeof coords[i+1] !== 'undefined'){
            console.log(coords[i])
            console.log(coords[i+1]+'\n\n')

            var circle = APPLI.two.makeCircle(Math.floor(55+parseInt(coords[i])), 55+Math.floor(parseInt(coords[i+1])), 30);
            circle.fill = "#ffffff";
            circle.noStroke();
       }
   }
   APPLI.two.update();


};


// Ask a poll regularly
APPLI.requestScan=function()
{
  //alert('SCANNING')
  APPLI.reqScan.open('GET', '/scan', true);
  APPLI.reqScan.send();
  window.setTimeout(function()
  {
   APPLI.requestScan();
  }, 300);
};

var k = 0;
APPLI.send_direction=function()
{
    if(! (directionOnBreak && k>0) ){
       k++;
       APPLI.reqDirection.open('POST', '/zone_direction', true);
       APPLI.reqDirection.send(zone_direction);
  }

  window.setTimeout(function()
  {
   APPLI.send_direction();
  }, 300);
};

APPLI.recvDirection=function()
{
  //alert('DIRECTION RECEIVED!')
}

APPLI.recvScan=function()
{
  //alert('SCAN RECEIVED!')
  coords = APPLI.reqScan.responseText.split(" ")

  console.log("*******************")
  console.log(coords.length)

  APPLI.addRobots(coords)
};

APPLI.initVisu = function(){
  APPLI.two = new Two({ width: 500, height: 500 });
  //APPLI.two = new Two({ fullscreen: true }).appendTo(elem);

  var visu_area= document.getElementById('visu_area');
  APPLI.two.appendTo(visu_area);

  var rect = APPLI.two.makeRectangle(250, 250, 500, 500);
  rect.fill = "#efefef";
  //rect.noStroke();
  rect.stroke = "#a8a8a8";
  rect.linewidth = 50;

  APPLI.two.update();
}

window.onload=function(evt)
{
APPLI.initVisu()
init();


  APPLI.robots=[];  for(var i=0; i<%d; ++i)
  {
  var r={};
   r.state=true;
   r.lbl=document.getElementById('robot_'+i);
   console.log(r.lbl);
   r.btns=[];
   btns=['switch'];

   APPLI.robots.push(r);
   console.log(r.btns);

  }

  APPLI.reqDirection=new XMLHttpRequest();
  APPLI.reqDirection.onload=APPLI.recvDirection;

  APPLI.reqScan=new XMLHttpRequest();
  APPLI.reqScan.onload=APPLI.recvScan;

  APPLI.requestScan();
  APPLI.send_direction();

};
</script>



</head>


<body>
<div id="main"></div>

<!--<script src="https://cdnjs.cloudflare.com/ajax/libs/two.js/0.6.0/two.min.js"></script>-->
<script src="./js/two.min.js"></script>

<div class="outer-div">
	<div class="inner-div">



<h2> Robocup 2020 </h2>


<div id="container"></div>
<div id="container"> <div id="visu_area"></div>
<div class="container space-top">
  <!--<h1 class="center blue-text thin">Joystick</h1>-->
  <div class="center-align">
  <canvas id="joystick" height="300" width="300"></canvas> </div>
  <br><br><br><br><br><br><br><br><br><br><br>
<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
<br><br><br><br><br><br><br><br><br><br><br>
Robot(s) disponible(s) :<br><br><br><br>


'''%(len(app.robots))
  for r in app.robots:
    with r.lock:
      ident=r.ident
      color=r.color.upper()
    if bytes!=str: # python 3
      color=color.encode()
    content+=br'''

<label class="switch_%s">
  <input type="checkbox" id=""switch_%s">
  <span class="slider round"></span>
</label><br><br>


<!--
<br><br>
<label class="switch_green">
  <input type="checkbox" id="green">
  <span class="slider round"></span>
</label>

<br><br>
<label class="switch_blue">
  <input type="checkbox" id="blue">
  <span class="slider round"></span>
</label>

<br><br>
<label class="switch_white">
  <input type="checkbox" id="white">
  <span class="slider round"></span>
</label>

-->
'''%(color,color)
  content+=br'''







  <!--
  <div id="xVal" class="light">X : </div>
  <div id="yVal" class="light">Y : </div>
  <div id="zVal" class="light">Orientation : </div>-->
</div>
<!--
<div>
<h2>Control</h2>
<p>[<a href="/">home</a>]</p>
<hr>

<hr>


</div>-->



</div>
</div>







<!--
<script src='http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.3/js/materialize.js'></script>
<script src='https://hammerjs.github.io/dist/hammer.js'></script>
<script src='https://code.createjs.com/createjs-2015.11.26.combined.js'></script>
-->



<body>
<script src="./js/jquery.js"></script>
<script src="./js/materialize.js"></script>
<script src="./js/hammer.js"></script>
<script src="./js/createjs-2015.11.26.combined.js"></script>


<script  src="./js/index.js"></script>

<link rel="stylesheet" type="text/css" href="./css/style.css" />
</body>



<!--<p><b>LOG</b>&nbsp;
#<button onclick="APPLI.log(null);">&nbsp;clear&nbsp;</button></p>
#<p><pre id="log_area"></pre></p>
#</body>-->











</html>
'''

  return content

def error_page(method, uri):
  content=br'''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
</head><body>
<h2>404 - Not Found</h2>
<p>[<a href="/">home</a>]</p>
<hr>
<p><i>method:</i> <b>%s</b></p>
<p><i>uri:</i> <b>%s</b></p>
<hr>
</body></html>
'''%(method, uri)
  return content

def http_reply(stream, status, connection, content_type, content):
  header=(b'HTTP/1.1 %s\r\n'+
          b'Connection: %s\r\n'+
          b'Content-Type: %s\r\n'+
          b'Content-Length: %d\r\n'+
          b'\r\n')%(status, connection, content_type, len(content))
  stream.write(header)
  stream.write(content)
  stream.flush()
  return connection==b'keep-alive'

def http_dialog(app, dialog_socket):
  try:
    stream=dialog_socket.makefile('rwb')
    #
    #---- reuse connection as much as possible ----
    while True:
      #
      #---- receive and analyse HTTP request ----
      (method, uri, conn, length)=(b'', b'', b'', b'')
      while True:
        l=stream.readline()
        # sys.stderr.write('%s\n'%l)
        if not l or l==b'\r\n' or l==b'\n':
          break
        if not method: # first line
          (method, uri)=l.split()[0:2]
        elif l.startswith(b'Connection:'):
          conn=l.split(None, 1)[1].strip()
        elif l.startswith(b'Content-Length:'):
          length=l.split(None, 1)[1].strip()
      if not method: break
      # sys.stderr.write('request: %s %s %s %s\n'%(method, uri, conn, length))
      conn=b'close' if conn.find(b'close')!=-1 else b'keep-alive'
      length=int(length) if length else 0
      length_a = length

      post_content=b''
      while length:
        r=stream.read(length)
        if not r: break
        post_content+=r
        length-=len(r)
      #
      #---- handle main page ----
      if method==b'GET':
        content = None;
        content_type = None;
        status_code = None;
        print('uri = ', uri)

        if uri==b'/':
            content=main_page(app)
            content_type = b'text/html'
            status_code = b'200 OK';

        elif uri==b'/js/two.min.js':
            with open('./js/two.min.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/js/hammer.js':
            with open('./js/hammer.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/js/jquery.js':
            with open('./js/jquery.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/js/materialize.js':
            with open('./js/materialize.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/js/createjs-2015.11.26.combined.js':
            with open('./js/createjs-2015.11.26.combined.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/js/index.js':
            with open('./js/index.js', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'application/javascript'
                status_code = b'200 OK';
        elif uri==b'/css/style.css':
            with open('./css/style.css', 'rb') as content_file:
                content = (content_file.read())
                content_type = b'text/css'
                status_code = b'200 OK';
        elif uri==b'/faveicon.ico':
            content = '';
            content_type = b'x-application/'
            status_code = b'200 OK';

        elif uri==b'/scan':
            content = bytes(app.coords, 'utf-8');
            content_type = b'text/plain'
            status_code = b'200 OK';
        else:
            content=error_page(method, uri)
            content_type = b'text/html';
            status_code = b'404 Not Found';

        print(content)
        print(" ((((((((((((((((((((())))))))))))))))))))) ")
        if http_reply(stream, status_code, conn, content_type, content):
          continue # keep-alive
        break # close
      #
      #---- handle control ----
      if method==b'POST' and uri==b'/zone_direction':

        print(" ######################################################################### ")
        print(" ######################################################################### ")

        #continue
        #if app.zone_direction == post_content:
        #    continue

        app.zone_direction=post_content
        content=handle_control(app, post_content)

        if http_reply(stream, b'200 OK', conn, b'text/plain', b''):
          continue # keep-alive
        break # close

      if method==b'POST' and uri==b'/scan':
        print("Receive a POST : ", post_content, " send it to handle_control ")

        json_data=json.loads(post_content.decode('utf-8'))

        print(" ######################################################################### ")
        #print(json_data)

        #array = struct.unpack('f'*8, post_content)

        app.coords = ''
        for robot in json_data:
            med_x = str(int( (robot['corner1']['x'] + robot['corner2']['x'] + robot['corner3']['x'] + robot['corner4']['x'])/4) )
            med_y = str(int( (robot['corner1']['y'] + robot['corner2']['y'] + robot['corner3']['y'] + robot['corner4']['y'])/4) )
            app.coords += med_x+' '+med_y+' '

        app.coords = app.coords[:-1]

        print(app.coords[:-1])

        print(" ######################################################################### ")

        #content=handle_control(app, post_content)
        print("Content returned by handle_control : ", b'')
        if http_reply(stream, b'200 OK', conn, b'text/plain', post_content):
          continue # keep-alive
        break # close
      #
      #---- any other unhandled case ----
      if True: # the last resort!
        content=error_page(method, uri)
        if http_reply(stream, b'404 Not Found', conn, b'text/html', content):
          continue # keep-alive
        break # close
  except:
    traceback.print_exc()
    pass
  dialog_socket.close()

#-----------------------------------------------------------------------------

def init_application():
  app=Record(coords='')
  app.zone_direction=b'STOP'
  app.robots=[Record(ident=ident,
                     color=color,
                     lock=threading.Lock(),
                     last_seen=None,
                     ip_addr=None,
                     left=90,
                     right=90)
              for (ident, color) in enumerate(ROBOT_COLORS)]
  app.udp_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
  app.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  app.listen_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
  app.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  app.listen_socket.bind(('', SERVER_PORT))
  app.listen_socket.listen(10)
  app.now=time.time()
  app.next_scan=app.now
  app.next_scan_display=app.now
  app.next_command=app.now
  return app

def application_step(app, timeout):
  app.now=time.time()
  if app.now>=app.next_scan:
    app.next_scan=app.now+ROBOT_SCAN_PERIOD
    scan_robots(app)
  if app.now>=app.next_scan_display:
    app.next_scan_display=app.now+ROBOT_SCAN_DISPLAY
    scan_display(app)

  if app.now>=app.next_command:
    app.next_command=app.now+ROBOT_COMMAND_PERIOD
    command_robots(app)
  r=select.select([app.udp_socket, app.listen_socket] , [], [], timeout)[0]
  if app.udp_socket in r:
    (msg, from_addr)=app.udp_socket.recvfrom(3)
    handle_incoming(app, from_addr, msg)
  if app.listen_socket in r:
    (dialog_socket, from_addr)=app.listen_socket.accept()
    th=threading.Thread(target=http_dialog,
                        args=(app, dialog_socket))
    th.setDaemon(True)
    th.start()

import random
def dummy_animation(app):
  if not random.randint(0, 4):
    for r in app.robots:
      with r.lock:
        if r.ip_addr is not None:
          r.left=(r.left+random.randint(179, 181))%180
          r.right=(r.right+random.randint(179, 181))%180

def main():
  app=init_application()
  while True:
    application_step(app, 0.1)
    #dummy_animation(app) # FIXME: replace with something useful...

if __name__=='__main__':
  main()

#-----------------------------------------------------------------------------
