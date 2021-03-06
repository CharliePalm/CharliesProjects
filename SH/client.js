import io from 'socket.io-client';

const socket = io.connect();
let playerID;
console.log("test");
// back and forth between the server upon connection to log client's id
socket.on('playerID', function(id) {
  playerID = id
});
// let the server know there's someone in the waiting room
socket.emit('waiting');
// adds a player to the screen
socket.on('newPlayer', function(game, id) {
  var out = "";
  for (var key in game.players) {
      out += game.players[key].name + '<br>';
  }
  document.getElementById('names').innerHTML = out;
  document.getElementById('idCode').innerHTML = id;

  });
  // initializes the primary game view
  socket.on('gamestart', function(game, firstID) {
    document.getElementById('f').innerHTML = 'Fascists played:<br>';
    document.getElementById('l').innerHTML = 'Liberals played:';
    var elem = document.getElementById('everyone');
    elem.parentNode.removeChild(elem);
    var bool = false;
    var callID;
    for (var key in game.players) {
      callID = key;
      break;
    }
    document.getElement
    document.getElementById('top').innerHTML = "Your super secret role is:\n";
    document.getElementById('nameLabel').innerHTML = 'current players:';

    if (game.players[playerID].isHitler) {
      // when there's only 5 or 6 game.players hitler know his fascists
      if (Object.keys(game.players).length == 5 || Object.keys(game.players).length == 6) {
        var otherFasc = "";
        for (var key in game.players) {
          if (game.players[key].isFascist) {
              otherFasc = game.players[key].name;
              break;
            }
          }
        document.getElementById('sub').innerHTML += "HITLER. Your other fascist is " + otherFasc;
      } else {
        document.getElementById('sub').innerHTML = "HITLER";
      }
      // otherwise he doesn't
    } else if (game.players[playerID].isFascist) {
      var otherFascists = "";
      var moreFasc = false;

      for (var key in game.players) {
        var hitler;
        if (game.players[key].isFascist) {
          if (game.players[key].isHitler) {
            hitler = game.players[key].name;
          } else if (playerID != key) {
            moreFasc = true;
            otherFascists += game.players[key].name + " and ";
          }
        }
      }
      if (!moreFasc) {
        document.getElementById('sub').innerHTML = "FASCIST. Your only ally is HITLER who is " + hitler + "";
      } else {
        document.getElementById('sub').innerHTML = "FASCIST. Your other Fascists are " + otherFascists + "HITLER is " + hitler + "";
      }
    } else {
      document.getElementById('sub').innerHTML = "LIBERAL";
    }
    if (playerID == game.firstID) {
      socket.emit('newpres', true, game);
    }
  });

  socket.on('newpres', function(game, first) {
    destroyChoice();
    destroyPostChoice();
    destroyCards();

    if (playerID == game.currPres.id) {
      if (first) {
        document.getElementById('pres').innerHTML = "You have been selected to be the first president";
      } else {
        document.getElementById('pres').innerHTML = "You are the new president<br>";
      }
      document.getElementById('choice').innerHTML = 'Pick your chanecellor:<br>';

      var ids = Object.keys(game.players);
      // create buttons to pick chancellor:
      ids.forEach(function(key) {
        const id = key;
        if (first) {
          if (key != playerID) {
            var x = document.createElement("BUTTON");
            var t = document.createTextNode(game.players[key].name);
            x.append(t);
            x.addEventListener('click', function() {
              chancellor(id, game);
            });
            var element = document.getElementById('choice');
            element.append(x);
          }
      } else {
        if (key != playerID && key != game.prevChance.id && key != game.prevPres.id) {
          var x = document.createElement("BUTTON");
          var t = document.createTextNode(game.players[key].name);
          x.append(t);
          x.addEventListener('click', function() {
            chancellor(id, game);
          });
          var element = document.getElementById('choice');
          element.append(x);
        }
      }
    });
  } else {
      if (first) {
        document.getElementById('pres').innerHTML = "The first president is " + game.currPres.name + ". They are currently deciding on their Chancellor.";
      } else {
        document.getElementById('pres').innerHTML = "The new president is " + game.currPres.name + ". They are currently deciding on their Chancellor.";
      }
    }
  });

  socket.on('vote', function(game) {
    destroyI();
    destroyPostChoice();
    if (!(playerID in game.players)) {
      return;
    }
    document.getElementById('pres').innerHTML = game.currPres.name + ' has chosen ' + game.prospectChance.name + ' to be Chancellor. ja or nein?<br>';
    document.getElementById('pres').innerHTML += "Remember: this vote is final!";

    var x = document.createElement("BUTTON");
    var t = document.createTextNode("nein!");
    x.append(t);
    x.addEventListener('click', function() {
      destroyChoice();
      document.getElementById('choice').innerHTML = 'your vote has been cast...';
      socket.emit('nein', game);
    });
    var element = document.getElementById('choice');
    element.append(x);

    var x = document.createElement("BUTTON");
    var t = document.createTextNode("ja!");
    x.append(t);
    x.addEventListener('click', function() {
      destroyChoice();
      document.getElementById('choice').innerHTML = 'your vote has been cast...';
      socket.emit('ja', game);
    })

    var element = document.getElementById('choice');
    element.append(x);
  });

  socket.on('kill', function(game, dead) {
    destroyPostChoice();
    document.getElementById('powerAction').innerHTML = game.currPres.name + ' has killed ' + dead.name + ". They were a ";
    if (dead.isFascist) {
      document.getElementById('powerAction').innerHTML += "FILTHY FASCIST!";
    } else {
      document.getElementById('powerAction').innerHTML += "A BIG LIB!";
    }
    socket.emit('newpres', false);
  });

  // game is over as someone disconnected
  socket.on('dc', function(game) {
    document.getElementById('top').innerHTML = "Nobody wins! Woohoo!";
    listPlayerRoles(game);
  });

  // game is over
  socket.on('end', function(game, fasc) {
    if (fasc == 2) {
      document.getElementById('top').innerHTML = game.currChance.name + " is hitler! FASCISTS WIN!";
    } else if (fasc == 1) {
      document.getElementById('top').innerHTML = "FASCISTS WIN!";
    } else if (fasc == 0) {
      document.getElementById('top').innerHTML = "LIBERALS WIN!";
    } else {
      document.getElementById('top').innerHTML = 'The bullet found Hitler! LIBERALS WIN';
    }
    listPlayerRoles(game);
  });

  //helper method for the two end games
  function listPlayerRoles(game) {
    destroyAll();
    document.getElementById('names').innerHTML = "";
    document.getElementById('nameLabel').innerHTML = "";
    var liberals = "";
    var fascists = "";
    for (var i in Object.keys(game.players)) {
      if (game.players[i].isFascist) {
        fascists += game.players[i].name + "<br>";
      } else {
        liberals += game.players[i].name + "<br>";
      }
    }
    document.getElementById('sub').innerHTML = "Fascists: " + fascists + "<br>";
    document.getElementById('sub').innerHTML += 'liberals: ' + liberals + '<br><br><br>';
    document.getElementById('sub').innerHTML += 'please close out this tab and rejoin to start a new game';
  }


  socket.on('voteTally', function(game, pass) {
    var ja = '';
    var nein = '';
    var i = 0;
    for (var key in game.jas) {
      if (game.jas[key]) {
        ja += game.players[key].name + " ";
      } else {
        nein += game.players[key].name + " ";
      }
      i++;
    }
    if (pass) {
      document.getElementById('postChoice').innerHTML = 'VOTE PASSED!<br>Sending cards to ' + game.currPres.name + '<br><br>';
      destroyChoice();
      destroyPres();
      if (playerID == game.currPres.id) {
        socket.emit('presCards', game);
      }
    } else {
      document.getElementById('postChoice').innerHTML = 'VOTE FAILED!<br>';
    }
    document.getElementById('postChoice').innerHTML += "In favor: " + ja + '<br>Opposed: ' + nein + '<br>';
  });

  socket.on('presCards', function(game, cards) {
    for (var i = 1; i < cards.length + 1; i++) {
      var x = document.createElement("BUTTON");
      const cardButton = cards[i - 1];
      const htIndex = i;
      if (!cards[i - 1]) {
        var t = document.createElement("Button");
        t.setAttribute('id', "FASCIST")
        x.addEventListener('click', function() {
          destroySingleCard(htIndex);
          socket.emit('presPass', game, false);
        });
      } else {
        var t = document.createElement("Button");
        t.setAttribute('id', "LIBERAL");
        x.addEventListener('click', function() {
          destroySingleCard(htIndex);
          socket.emit('presPass', game, true);
        });
      }
      x.append(t);
      var element = document.getElementById('card' + i);
      element.append(x);
    }
  });

  socket.on('passing', function(game) {
    destroyPostChoice();
    if (playerID == game.currChance.id) {
      document.getElementById('postChoice').innerHTML = 'The president just passed you:';
    } else {
      document.getElementById('postChoice').innerHTML = 'Chancellor is deciding on cards';
    }
    destroyCards();
  });

  socket.on('chanceCards', function(cards, game) {
    console.log(cards);
    for (var i = 1; i < cards.length + 1; i++) {
      var x = document.createElement("BUTTON");
      const cardButton = cards[i-1];
      if (!cards[i - 1]) {
        const htIndex = i;
        var t = document.createElement("Button");
        // set id to fascist to get image from css file
        t.setAttribute('id', 'FASCIST');
        x.addEventListener('click', function() {
          console.log('fasc clicked');
          if (socket.emit('cardPlayed', game, false)) {
            destroyCards();
          }
        });
      } else {
        const htIndex = i;
        var t = document.createElement("Button");
        // set id to Liberal to get image from css file
        t.setAttribute('id', 'LIBERAL');
        x.addEventListener('click', function() {
          if (socket.emit('cardPlayed', game, true)) {
            destroyCards();
          }
        });
      }
      x.append(t);
      var element = document.getElementById('card' + i);
      element.append(x);
    }
  });

  socket.on('cardPlayed', function(card, game, power) {
    destroyAll();
    document.getElementById('cards').innerHTML = game.currPres.name + " and " + game.currChance.name + " played a ";
    if (card) {
      document.getElementById('cards').innerHTML += 'Liberal card!';
      document.getElementById('l').innerHTML += ' L';
    } else {
      document.getElementById('cards').innerHTML += 'Fascist card!';
      document.getElementById('f').innerHTML += ' F';
    }
    if (playerID == game.currPres.id) {
      socket.emit('newpres', false, game);
    }
  });

  socket.on('investigation', function(game) {
    destroyI();
    destroyPostChoice();
    var test = game.currChance.name
    var test2 = game.currPres.name
    document.getElementById('cards').innerHTML = game.currPres.name + " and " + game.currChance.name + " played a ";
    document.getElementById('cards').innerHTML += 'Fascist card!';
    document.getElementById('f').innerHTML += ' F';
    document.getElementById('cards').innerHTML += '<br>' + game.currPres.name + ' now gets an investigation.';
    if (playerID == game.currPres.id) {
      for (key in game.players) {
        let i = key;
        const id = key;
        if (key != playerID) {
          var x = document.createElement("BUTTON");
          var t = document.createTextNode(game.players[key].name);
          x.append(t);
          x.addEventListener('click', function() {
            investigate(id, game);
          })
          var element = document.getElementById('powerAction');
          element.append(x);
        }
      }
    }
  });

  socket.on('specialElection', function(game) {
    destroyCards();
    destroyPostChoice();
    document.getElementById('cards').innerHTML = game.currPres.name + " and " + game.currChance.name + " played a ";
    document.getElementById('cards').innerHTML += 'Fascist card!';
    document.getElementById('f').innerHTML += ' F';
    document.getElementById('cards').innerHTML += '<br>' + game.currPres.name + ' gets a special election!';
    if (playerID == game.currPres.id) {
      document.getElementById('choice').innerHTML += '<br>Pick the next president:<br>';
      for (key in game.players) {
        let i = key;
        const id = key;
        if (key != playerID) {
          var x = document.createElement("BUTTON");
          var t = document.createTextNode(game.players[key].name);
          x.append(t);
          x.addEventListener('click', function() {
            elect(id, game);
          });
          var element = document.getElementById('choice');
          element.append(x);
        }
      }
    }
  });

  socket.on('bullet', function(game) {
    destroyPostChoice();
    destroyCards();
    document.getElementById('cards').innerHTML = game.currPres.name + " and " + game.currChance.name + " played a ";
    document.getElementById('cards').innerHTML += 'Fascist card!';
    document.getElementById('f').innerHTML += ' F';
    document.getElementById('choice').innerHTML += '<br>' + game.currPres.name + ' has a bullet...<br>'
    if (playerID == game.currPres.id) {
      document.getElementById('choice').innerHTML += "Who dies?<br>"
      for (key in game.players) {
        let i = key;
        const id = key;
        if (key == playerID) {
          continue;
        } else {
          var x = document.createElement("BUTTON");
          var t = document.createTextNode(game.players[key].name);
          x.append(t);
          x.addEventListener('click', function() {
            bullet(id, game);
          })
          var element = document.getElementById('choice');
          element.append(x);
        }
      }
    }
  });

  function bullet(id, game) {
    socket.emit('bullet', id, game);
  }

  function elect(id, game) {
    socket.emit('election', game);
  }

  function chancellor(id, game) {
    if (game.prospectChance != null && (id == game.prospectChance.id || id == game.prevPres.id)) {
      return;
    }
    socket.emit("chance", id, game)
    destroyChoice();
  }

  function investigate(id, game) {
    destroyI();
    if (game.players[id].isFascist) {
      document.getElementById('cards').innerHTML = game.players[id].name + " is FASCIST!";
    } else {
      document.getElementById('cards').innerHTML = game.players[id].name + " is LIBERAL!";
    }
    // create continue button
    var x = document.createElement("BUTTON");
    var t = document.createTextNode("continue");
    x.append(t);
    x.addEventListener('click', function() {
      destroyPowerAction();
      socket.emit('newpres', false, game);
    })
    var element = document.getElementById('powerAction');
    element.append(x);

  }

  function destroySingleCard(i) {
    var parent = document.getElementById('card' + i).parentNode;
    parent.removeChild(document.getElementById('card' + i));
    var newNode = document.createElement('p');
    newNode.setAttribute('id', 'card' + i);
    parent.appendChild(newNode);
  }

  function destroyAll() {
    destroyPostChoice();
    destroyChoice();
    destroyPres();
    destroyCards();
    destroyPowerAction();
  }
  // for getting rid of old buttons and texts that are now unimportant
  function destroyPowerAction() {
    var node = document.getElementById('powerAction');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('h');
    newNode.setAttribute('id', 'powerAction');
    parent.appendChild(newNode);
    return newNode;
  }

  function destroyPostChoice() {
    var node = document.getElementById('postChoice');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('p');
    newNode.setAttribute('id', 'postChoice');
    parent.appendChild(newNode);
    return newNode;
  }

  function destroyChoice() {
    var node = document.getElementById('choice');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('p');
    newNode.setAttribute('id', 'choice');
    parent.appendChild(newNode);
    return newNode;
  }

  function destroyPres() {
    var node = document.getElementById('pres');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('p');
    newNode.setAttribute('id', 'pres');
    parent.appendChild(newNode);
  }

  function destroyCards() {
    var node = document.getElementById('cards');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('h');
    newNode.setAttribute('id', 'cards');
    parent.appendChild(newNode);
    for (var i = 1; i <=3; i++) {
      const index = i;
      var node = document.getElementById('card' + index);
      var parent = node.parentNode;
      parent.removeChild(node);
      var newNode = document.createElement('p');
      newNode.setAttribute('id', 'card' + index);
      parent.appendChild(newNode);
    }
  }

  function destroyI() {
    var node = document.getElementById('powerAction');
    var parent = node.parentNode;
    parent.removeChild(node);
    var newNode = document.createElement('p');
    newNode.setAttribute('id', 'powerAction');
    parent.appendChild(newNode);
  }

  function gameStart() {
    socket.emit('gamestart', document.getElementById('idCode').innerHTML);
  }
