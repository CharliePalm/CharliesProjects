var express = require('express');
var http = require('http');
var path = require('path');
var socketIO = require('socket.io');
var players = {};
var app = express();
var server = http.Server(app);
var io = socketIO(server);
var body = "";
var playerName = "";
var gameStarted = false;
var fascistCardsPlayed = 0;
var liberalCardsPlayed = 0;
var deck = [];
var first = true;
var firstID;
var jas = {};
app.set('port', 5000);
app.use('/static', express.static(__dirname + '/static'));
// Routing
app.get('/', function(request, response) {
  response.sendFile(path.join(__dirname, 'index.html'));
});

// called when a player enters the game
app.post("/PrePlayView.html", function(req, res) {
  if (gameStarted) {
    res.sendFile(path.join(__dirname, 'index.html'));
    return;
  }
  req.on('data', function (chunk) {
    body += chunk;
  });

  req.on('end', function () {
    playerName = body.substr(body.indexOf("=") + 1, body.length);
    body = "";
    res.sendFile(path.join(__dirname, 'PrePlayView.html'));
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


io.on('connection', function(socket) {

  socket.on('newPlayer', function() {
    if (first) {
      first = false;
      firstID = socket.id;
    }
    game.addPlayer(new Player(playerName, socket.id));
    playerName = "";
    io.emit('newPlayer', game.players);
  });

  socket.on('gamestart', function() {
    if (game.numPlayers < 5) {
      return;
    }
    gameStarted = true;
    getFascists(game);
    io.emit('gamestart', game.players, socket.id, firstID);
    io.emit("shtime");
  });

  socket.on('newpres', function(first) {
    newPres(first);
    io.emit('newpres', game.currPres, game.players, first, game);
  });

  socket.on('chance', function(id) {
    game.currChance = game.players[id]
    io.emit('vote', game.players[id], game);
    return true;
  });

  socket.on('ja', function(id) {
    game.numJas++;
    game.jas[socket.id] = true;
    if (game.numJas / game.numCurrPlayers > .5) {
      jaornein(id);
    }
  });

  socket.on('nein', function() {
    game.numNeins++;
    game.jas[socket.id] = false;
    if (game.numNeins / game.numCurrPlayers > .5) {
      jaornein(0);
    }
  });

  socket.on('presCards', function() {
    draw = game.draw();
    socket.emit('presCards', draw);
  });

  socket.on('presPass', function(card) {
    if (card == true) {
      game.passedCards.push(true);
    } else {
      game.passedCards.push(false);
    }
    if (game.passedCards.length == 2) {
      io.emit('passing', game.currChance.id);
      io.to(game.currChance.id).emit('chanceCards', game.passedCards);
      game.passedCards = [];
    }
  });

  socket.on('cardPlayed', function(card) {
    var power = game.playCard(card);
    if (!power) {
      io.emit('cardPlayed', card, game, power);
    }
  });

  socket.on('disconnect', function() {
    io.emit('gameover', 'none');
    game = new Game();
    first = true;
    gameStarted = false;
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
    for (var i in Object.keys(game.players)) {
      console.log(i);
    }
    io.emit('kill', game, dead);
  });

});


function jaornein(id) {
  if (game.numJas > game.numNeins) {
    game.numJas = 0;
    game.numNeins = 0;
    game.anarchy = 0;
    game.prevChance = game.currChance;
    game.currChance = game.players[id];
    if (game.currChance.isHitler && game.numFCards >=3) {
      io.emit('end', game, 2);
      return;
    }
    io.emit('voteTally', game.jas, game.currPres, game.players, true);
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

function newPres(first) {
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

class Game {
  constructor() {
    console.log('initializing game');
    this.players = {};
    this.currPres;
    this.currChance;
    this.prevPres;
    this.prevChance;
    this.vicLib;
    this.vicFasc;
    this.anarchy = 0;
    this.discards = [];
    this.numFCards = 0;
    this.numLCards = 0;
    this.cards = this.createDeck();
    this.shuffle();
    console.log(this.cards);
    this.index = 0;
    this.numPlayers = 0;
    this.passedCards = [];
    this.numCurrPlayers = 0;
    this.jas = {};
    this.numJas = 0;
    this.numNeins = 0;
  }
  addPlayer(player) {
    this.numPlayers++;
    this.numCurrPlayers++;
    this.players[player.id] = player;
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
      io.emit('end', 0);
    }
    if (this.numFCards == 6) {
      io.emit('end', 1);
    }
  }

  getPower(card) {
    if (this.numFCards == 4 || this.numFCards == 5) {
      io.emit('bullet', this);
      return true;
    }
    if (this.numPlayers == 5 || this.numPlayers == 6) {
      if (this.numFCards == 3) {
        io.emit('invetigation', this);
        return true;
      }
    } else if (this.numPlayers == 7 || this.numPlayers == 8) {
      if (this.numFCards == 2) {
        io.emit('investigation', this);
        return true;
      } else if (this.numFCards == 3) {
        io.emit('election', this);
        return true;
      }
    } else if (this.numPlayers == 9 || this.numPlayers == 10) {
      if (this.numFCards == 1 || this.numFCards == 2) {
        io.emit('investigation', this);
        return true;
      } else if (this.numFCards == 3) {
        io.emit('specialElection', this);
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
    console.log(toPlayer);
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
var game = new Game();
