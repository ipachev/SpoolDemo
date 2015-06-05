window.requestAnimFrame = (function(callback) {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame ||
    function(callback) {
        window.setTimeout(callback, 1000 / 60);
    };
})();


function Table(height) {
    this.height = height;
    this.draw = function(context, canvas) {
        context.save();
        context.fillStyle = "#663300";
        context.fillRect(0, this.height, canvas.width, 30);
    }
}

function Spool(x, y, minor, major, mass) {
    this.x = x;
    this.y = y;
    this.initialx = x;
    this.initialy = y;
    this.angle = 0;
    this.minor = minor;
    this.major = major;
    this.vel = 0;
    this.angvel = 0;
    this.mass = mass;
    this.scalefactor = 4;
    this.paused = false;
    this.initialstringlength = 6*this.minor*2*Math.PI;
    this.stringlength = this.initialstringlength;

    this.setMinor = function(minor) {
        this.minor = minor;
        console.log("changed minor axis to " + minor);
    };

    this.setMajor = function(major) {
        this.major = major;
        if(this.table != null) {
            this.setOnTable(this.table);
        }
        console.log("changed major axis to " + major);
    };

    this.setMass = function(mass) {
    	this.mass = mass;
    	console.log("changed mass to " + mass);
    };

    this.setOnTable = function(table) {
        this.table = table;
        this.y = this.initialy = table.height-this.major*this.scalefactor;
    };

    this.incrementAngle = function(increment) {
        this.angle -= increment;
        this.stringlength += increment * this.minor * this.scalefactor;
        if (this.stringlength < 3) {
            this.paused = true;
        }
    };

    this.incrementPosition = function(x, y) {
        this.x += x*this.scalefactor;
        this.y += y*this.scalefactor;
    };

    this.resetPosition = function() {
        this.x = this.initialx;
        this.vel = 0;
        this.angvel = 0;
        this.stringlength = this.initialstringlength;
        this.angle = 0;
    };

    this.pause = function() {
        this.paused = !this.paused;
    };

    this.calc = function(pull) {
        var inertia = 1.0/2.0*(2.0*this.mass/3.0*Math.pow(this.major,2.0)+this.mass/3.0*Math.pow(this.minor,2.0));
        var friction = -1.0*pull*(this.minor+(inertia/(this.major*this.mass)))/(this.major+(inertia/(this.major*this.mass)));
        var mew = .19;
        var mewk = .95*mew;
        var frictionmax = -this.mass*9.81*mew;
        if(Math.abs(friction) > Math.abs(frictionmax))
        {
            friction = -1.0*this.mass*9.81*mewk;
        }
        var a = (pull + friction)/this.mass;
        var alpha = (major * friction + minor*pull)/inertia;
        var dt = 1.0/60;
        var dx = 1.0/2.0*a*Math.pow(dt, 2.0) + this.vel*dt;
        var dtheta = 1.0/2.0*alpha * Math.pow(dt, 2.0)+this.angvel*dt;
        this.incrementPosition(dx, 0);

        this.incrementAngle(dtheta);
        this.vel += a*dt;
        this.angvel += alpha*dt;
    };

    this.draw = function(context) {
        context.save();
        var drawmajor = this.major*this.scalefactor;
        var drawminor = this.minor*this.scalefactor;
        context.fillStyle = "#DEB887";
        context.strokeStyle = "#000000"
        context.translate(this.x, this.y);
        context.rotate(this.angle);

        if(this.minor > this.major)
        {
            context.beginPath();
            context.arc(0, 0, drawminor, 0, 2*Math.PI);
            context.stroke();
            context.fill();
            context.beginPath();
            context.arc(0, 0, drawmajor, 0, 2*Math.PI);
            context.stroke();
            context.fill();
        }
        else
        {
            context.beginPath();
            context.arc(0, 0, drawmajor, 0, 2*Math.PI);
            context.stroke();
            context.fill();
            context.beginPath();
            context.arc(0, 0, drawminor, 0, 2*Math.PI);
            context.stroke();
            context.fill();
        }

        context.strokeStyle = "#000000"
        context.moveTo(-drawminor, 0);
        context.lineTo(drawminor, 0);
        context.stroke();

        context.moveTo(0,-drawminor);
        context.lineTo(0, drawminor);
        context.stroke();

        context.restore();
        context.save();

        context.translate(this.x, this.y + drawminor);
        context.beginPath();
        context.moveTo(0,0);
        context.lineTo(this.stringlength, 0);
        context.stroke();
        context.restore();
    };
}

var pullForce;
var canvas = document.getElementById('myCanvas');
var context = canvas.getContext('2d');

var spool = new Spool(100, 300, 5.0, 10.0, 10.0);
var table = new Table(canvas.height-400);

function animate(canvas, context)
{
    if(!spool.paused)
    {
        spool.calc(pullForce);
    }
    context.clearRect(0,0, canvas.width, canvas.height);
    spool.draw(context);
    table.draw(context, canvas);
    requestAnimFrame(function () {
        animate(canvas, context);
    })
}



function applyValues() {
	var input = document.getElementById("inputs");
	pullForce = parseFloat(input.pullforce.value);
	spool.setMajor(parseFloat(input.majoraxis.value));
	spool.setMinor(parseFloat(input.minoraxis.value));
	spool.setMass(parseFloat(input.mass.value));
	spool.resetPosition();
}

function init() {
	var input = document.getElementById("inputs");
	input.pullforce.value = 20;
	input.majoraxis.value = 10.0;
	input.minoraxis.value = 5.0;
	input.mass.value = 5.0;
	applyValues();
}

init()

spool.setOnTable(table);
spool.draw(context);
table.draw(context, canvas);


animate(canvas, context, spool, table);