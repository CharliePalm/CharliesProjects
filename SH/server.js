
// define global variables and packages
const express = require('express');
const http = require('http');
const path = require('path');
const socketIO = require('socket.io');
const ajax = require('ajax');
const session = require('express-session');
const app = express();
const server = http.Server(app);
const io = socketIO(server);
var connections = [];
var games = {};
var notInGame = {};

io.use((socket, next) => {
  sessionMiddleware(socket.request, {}, next);
})

const sessionMiddleware = session({ secret: 'BungaloBill', cookie: { maxAge: 60000 }});
app.use(sessionMiddleware);
app.set('port', 5000);
//app.use('/static', express.static(__dirname + '/static'));
app.use(express.static(__dirname + '/public'));
// Routing on entry
app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, 'prePlayView.html'));
});

// called when a player enters the game
app.post("/userView.html", function(req, res) {
  var body = "";
  req.on('data', function(char) {
    body += char;
  });
  // parses user's input into id and name
  req.on('end', function () {
    var asdh = getGameID(req.session.id)
    console.log('req says ' + req.session.id)
    var playerName = body.substr(body.indexOf("=") + 1, body.indexOf("&") - 5);
    var id = body.substr(body.indexOf("&") + 4, body.length);
    body = "";
    // if id is blank then the user wants to join a new game
    if (id == '') {
      while (true) {
        id = generateID();
        if (games[id] == null) {
          games[id] = new Game();
          break;
        }
      }

      games[id].addPlayer(playerName, req.session.id);
      games[id].firstID = req.session.id;
      game.id = id;

    } else { // join game with user inputted id
      if (games[id] == null || games[id].players.length == 10) {
        res.sendFile(path.join(__dirname, 'prePlayView.html'));
        return;
      }
      games[id].addPlayer(playerName, req.session.id);
    }

    res.sendFile(path.join(__dirname, 'userView.html'));
  });

});

// starts the game after button push
app.post('/gameview.html', function(req, res) {
  if (Object.keys(game.players).length < 5) {
    console.log('less than 5');
    res.sendFile(path.join(__dirname, '/index.html'));
    return;
  }
  gameStarted = true;
  res.sendFile(path.join(__dirname, '/index.html'));
  //console.log(res.sendFile(path.join(__dirname, '/index.html')));
});

// io inputs: collections of user interaction with server
io.on('connect', function(socket) {

  var playerID = socket.request.session.id;
  playerID.connections++;

  console.log('socket says ' + playerID)
  connections[playerID] = socket.id;

  socket.on('waiting', function() {
    console.log(playerID);
    var id = getGameID(playerID);
    socket.join(id);
    notInGame[playerID] = null;
    io.to(id).emit('newPlayer', games[id], id);
  });

  socket.on('gamestart', function(gameID) {
    if (games[gameID].numPlayers < 5) {
      return;
    }

    gameStarted = true;
    getFascists(games[gameID]);
    io.to(id).('gamestart', games[gameID].players, playerID, game.firstID);
  });

  socket.on('newpres', function(first, gameID) {
    newPres(first);
    io.emit('newpres', game.currPres, first, game);
  });

  socket.on('chance', function(id, gameID) {
    games[gameID].currChance = games[gameID].players[id]
    io.to(gameID).emit('vote', games[gameID]);
    return true;
  });

  socket.on('ja', function(game) {
    game.numJas++;
    game.jas[playerID] = true;
    if (game.numJas / game.numCurrPlayers > .5) {
      jaornein(game);
    }
  });

  socket.on('nein', function(game) {
    game.numNeins++;
    game.jas[playerID] = false;
    if (game.numNeins / game.numCurrPlayers > .5) {
      jaornein(game);
    }
  });

  socket.on('presCards', function(game) {
    draw = game.draw();
    // emit specifically to pres
    io.to(connections[game.currPres.id]).emit('presCards', game, draw);
  });

  socket.on('presPass', function(game, card) {
    // log cards passed by president
    if (card == true) {
      game.passedCards.push(true);
    } else {
      game.passedCards.push(false);
    }
    // send cards after 2 are sent
    if (game.passedCards.length == 2) {
      io.to(game.id).emit('passing', game);
      io.to(connections[game.currChance.id]).emit('chanceCards', game.passedCards, game);
      game.passedCards = [];
    }
  });

  socket.on('cardPlayed', function(card, game) {
    var power = game.playCard(card);
    if (!power) {
      io.emit('cardPlayed', card, game, power);
    }
  });

  socket.on('investigate', function(id) {
    io.to(socket.id).emit('receivedInvestigation', game, id, game.players[id].isFascist);
  });

  socket.on('election', function(id) {
    game.currPres = game.players[id];
    io.emit('newpres', game.currPres, game.players, false, game);
  });

  socket.on('bullet', function(id) {
    if (game.players[id].isHitler) {
      io.emit('end', game, 3)
    }
    var dead = game.players[id];
    game.numCurrPlayres--;
    delete game.players[id];

    io.emit('kill', game, dead);
  });

  socket.on('disconnect', function() {
    var id = getGameID(playerID);
    io.to(games[id]).emit('DC', games[id]);
    for (var key in Object.keys(games[id].players)) {

    }
    delete games[id];

  });

});

function getGameID(playerID) {
  var ids = Object.keys(games);
  for (var i = 0; i < ids.length; i++) {
    if (games[ids[i]].players[playerID]) {
      return ids[i];
    }
  }
  return null;
}


function generateID() {
  return Math.random().toString(36).substr(2, 7);
}

function jaornein(game) {
  if (game.numJas > game.numNeins) {
    game.numJas = 0;
    game.numNeins = 0;
    game.anarchy = 0;
    game.prevChance = game.currChance;
    game.currChance = game.players[id];
    if (game.currChance.isHitler && game.numFCards >=3) {
      io.to(game.id).emit('end', game, 2);
      return;
    }
    io.to(game.id).emit('voteTally', game, true);
    game.jas = {};
  } else {
    game.numJas = 0;
    game.numNeins = 0;
    game.anarchy++;
    if (game.anarchy == 3) {
      var card = game.cards[game.index];
      game.index++;
      game.playCard(card);
      io.emit('anarchy', card);
    }
    io.emit('voteTally', game.jas, game.currPres, game.players, false);
    newPres(false);
    io.emit('newpres', game.currPres, game.players, false, game);
  }
}


function getFascists() {
  var numFascists = 0;
  if (game.numPlayers == 5 || game.numPlayers == 6) {
    numFascists = 1
  } else if (game.numPlayers == 7 || game.numPlayers == 8) {
    numFascists = 2;
  } else {
    numFascists = 3;
  }
  var hitler = 1;
  var ids = Object.keys(game.players);
  for (i = 0; i < numFascists + 1; i++) {
    var playerIndex = Math.floor(Math.random() * ids.length);
    while (true) {
      if (game.players[ids[playerIndex]].isFascist) {
        playerIndex = Math.floor(Math.random() * ids.length);
        continue;
      } else {
        game.players[ids[playerIndex]].isFascist = true;
        if (hitler == 1) {
          game.players[ids[playerIndex]].isHitler = true;
          hitler = 0;
        }
        break;
      }
    }
  }
}

function newPres(first, id) {
  var chance = null;
  var playersOnly = Object.values(game.players);
  game.prevPres = game.currPres;
  if (first) {
    // if first is true randomly select first president.
    var playerExc = [];
    for (var key in game.players) {
      playerExc.push(game.players[key]);
    }
    var index = Math.floor(Math.random() * playerExc.length);
    game.currPres = playerExc[index];
    // otherwise increment by single step to get next president
  } else if (game.currPres == playersOnly[playersOnly.length - 1]) {
    game.currPres.isPresident = false;
    playersOnly[0].isPresident = true;
    game.prevPres = game.currPres;
    game.currPres = playersOnly[0];
  } else {
    for (var i = 0; i < Object.keys(game.players).length; i++) {
      if (playersOnly[i] == game.currPres) {
        game.currPres.isPresident = false;
        game.prevPres = game.currPres;
        game.currPres = playersOnly[i+1];
        playersOnly[i+1].isPresident = true;
        break;
      }
    }
  }
}


// Starts the server.
server.listen(5000, function() {
  console.log('Starting server on port 5000');
});

// class for organizing players
class Player {
  constructor(name, id) {
    this.name = name,
    this.id = id,
    this.isHitler = false,
    this.isFascist = false,
    this.isChancellor = false,
    this.isPresident = false;
    this.wasInPrevious = false;
  }
}

// class for organizing game actions and variables
class Game {
  constructor() {
    console.log('initializing game');
    this.ID;
    this.players = {};
    this.currPres;
    this.currChance;
    this.prevPres;
    this.prevChance;
    this.vicLib;
    this.vicFasc;
    this.firstID;
    this.anarchy = 0;
    this.discards = [];
    this.numFCards = 0;
    this.numLCards = 0;
    this.cards = this.createDeck();
    this.shuffle();
    this.index = 0;
    this.numPlayers = 0;
    this.passedCards = [];
    this.numCurrPlayers = 0;
    this.jas = {};
    this.numJas = 0;
    this.numNeins = 0;
  }

  addPlayer(name, id) {
    var toAdd = new Player(name, id);
    this.numPlayers++;
    this.numCurrPlayers++;
    this.players[toAdd.id] = toAdd;
  }

  createDeck() {
    var numLib = 0;
    for (var i = 0; i < 17; i++) {
      if (numLib < 6) {
        this.discards.push(true);
        numLib++;
      } else {
        this.discards.push(false);
      }
    }
    return this.discards;
  }

  playCard(card) {
    if (card) {
      this.numLCards += 1;
    } else {
      this.numFCards += 1;
      return this.getPower();
    }
    if (this.numLCard == 5) {
      io.to(this.id).emit('end', 0);
    }
    if (this.numFCards == 6) {
      io.to(this.id).emit('end', 1);
    }
  }

  getPower(card) {
    if (this.numFCards == 4 || this.numFCards == 5) {
      io.to(this.id).emit('bullet', this);
      return true;
    }
    if (this.numPlayers == 5 || this.numPlayers == 6) {
      if (this.numFCards == 3) {
        io.to(this.id).emit('invetigation', this);
        return true;
      }
    } else if (this.numPlayers == 7 || this.numPlayers == 8) {
      if (this.numFCards == 2) {
        io.to(this.id).emit('investigation', this);
        return true;
      } else if (this.numFCards == 3) {
        io.to(this.id).emit('election', this);
        return true;
      }
    } else if (this.numPlayers == 9 || this.numPlayers == 10) {
      if (this.numFCards == 1 || this.numFCards == 2) {
        io.to(this.id).emit('investigation', this);
        return true;
      } else if (this.numFCards == 3) {
        io.to(this.id).emit('specialElection', this);
        return true;
      }
      return false;
    }
  }

  draw() {
    var toPlayer = [];
    const index = this.index;
    if (this.index == this.cards.length) {

      this.shuffle;
      for (this.index; this.index < index + 3; this.index++) {
        this.discards.push(this.cards[index]);
        toPlayer.push(this.cards[index]);
      }

    } else if (this.index == this.cards.length - 1) {

        this.discards.push(this.cards[index]);
        this.toPlayer.push(this.cards[index])
        this.shuffle;
        for (this.index; this.index < index + 2; this.index++) {
          this.discards.push(this.cards[index]);
          toPlayer.push(this.cards[index]);
        }

    } else if (this.index == this.cards.length - 2) {
      for (this.index; this.index < index + 2; this.index++) {
        this.discards.push(this.cards[index]);
        toPlayer.push(this.cards[index]);
      }
      this.shuffle;
      this.discards.push(this.cards[index]);
      toPlayer.push(this.cards[index]);
      this.index++;
    } else {
      for (this.index; this.index < index + 3; this.index++) {
        this.discards.push(this.cards[this.index]);
        toPlayer.push(this.cards[this.index]);
      }
    }
    return toPlayer;
  }

  shuffle() {
    var j, x, i;
    for (var i = this.discards.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = this.cards[i];
        this.discards[i] = this.discards[j];
        this.discards[j] = x;
    }
    for (var i = 0; i < this.discards.length; i++) {
      this.cards[i] = this.discards[i];
    }
    this.index = 0;
    this.discards = [];
  }
}
