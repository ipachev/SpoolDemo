
var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use(express.static('public'));

app.get('/', function(req, res){
  res.sendFile('public/SpoolDemo.html');
});

io.on('connection', function(socket){
  console.log('a user connected');
  socket.on("callMethod", function(data) {
    if(data["methodName"] == "swag") {
        console.log("swag");
    }
});
});

http.listen(80, function(){
  console.log('listening on *:80');
});