var zone_direction;
var directionOnBreak = true;

function sleep(millis) {
  var start = new Date().getTime();
  for(var i = 0; i < 1e7; i++){
    if( (new Date().getTime()-start) > millis){
      break;
    }
  }
}

function init() {
  // easal stuff goes hur
  var xCenter = 0;
  var yCenter = 0;
  var stage = new createjs.Stage('joystick');

  var psp = new createjs.Shape();
  psp.graphics.beginFill('#333333').drawCircle(xCenter+150, yCenter+150, 50);

  psp.alpha = 0.25;

  var vertical = new createjs.Shape();
  var horizontal = new createjs.Shape();

  stage.addChild(psp);
  stage.addChild(vertical);
  stage.addChild(horizontal);
  createjs.Ticker.framerate = 60;
  createjs.Ticker.addEventListener('tick', stage);

  $('#xVal').text('X : 0');
  $('#yVal').text('Y : 0');
  $('#zVal').text('Orientation : STOP');
  stage.update();

  var myElement = $('#joystick')[0];

  // by default, it only adds horizontal recognizers
  var mc = new Hammer(myElement);

  mc.on("panstart", function(ev) {
    console.log('on start'+k);
    k = 0;
    directionOnBreak = false;
    var pos = $('#joystick').position();
    xCenter = psp.x;
    yCenter = psp.y;

    psp.alpha = 0.5;

    stage.update();
  });

  // listen to events...
  mc.on("panmove", function(ev) {
    directionOnBreak = false;
    console.log('on move'+ directionOnBreak+ " k:"+k);

    var pos = $('#joystick').position();

    var x = Math.round((ev.center.x - pos.left - 150));
    var y = Math.round((ev.center.y - pos.top - 150));

    var coords = calculateCoords(ev.angle, ev.distance);

    psp.x = coords.x;
    psp.y = coords.y;

    x = Math.round(psp.x);
    y = Math.round(psp.y);

    var direction = 'STOP';

    if (x >= 35)
    {
      if (-y >= 35){direction = 'AVANT DROIT';}
      if (-y <= -35){direction = 'ARRIERE DROIT';}
      if ((-y < 35) && (-y > -35)) {direction = 'DROITE';}
    }
    if (x <= -35)
    {
      if (-y >= 35){direction = 'AVANT GAUCHE';}
      if (-y <= -35){direction = 'ARRIERE GAUCHE';}
      if ((-y < 35) && (-y > -35)) {direction = 'GAUCHE';}
    }
    if ((x > -35) && (x < 35))
    {
      if (-y >= 35){direction = 'AVANT';}
      if (-y <= -35){direction = 'ARRIERE';}
      if ((-y < 35) && (-y > -35)) {direction = 'STOP';}
    }

    console.log(zone_direction);

    zone_direction = direction;

    $('#xVal').text('X : ' + x);
    $('#yVal').text('Y : ' + (-1 * y));
    $('#zVal').text('Orientation : ' + direction);

    psp.alpha = 0.5;

    stage.update();
  });

  mc.on("panend", function(ev) {
    k = 0;
    
    console.log('on break'+ directionOnBreak);
    psp.alpha = 0.25;

    createjs.Tween.get(psp).to({x:0,y:0},750,createjs.Ease.elasticOut);

    $('#xVal').text('X : 0');
    $('#yVal').text('Y : 0');
    $('#zVal').text('Orientation : STOP');

    console.log(zone_direction + " " + directionOnBreak);
    console.log("************************");

    if(zone_direction != 'STOP' && !directionOnBreak){
      directionOnBreak = true;
    }
    console.log(zone_direction + " " + directionOnBreak);
    zone_direction = 'STOP';

    stage.update();
  });
}

function calculateCoords(angle, distance) {
  var coords = {};
  distance = Math.min(distance, 100);
  var rads = (angle * Math.PI) / 180.0;

  coords.x = distance * Math.cos(rads);
  coords.y = distance * Math.sin(rads);

  return coords;
}
