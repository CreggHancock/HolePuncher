This fork is compatible with Godot 4. Find the Godot 3 compatible version here: https://github.com/CreggHancock/HolePuncher/tree/godot3

## HolePunch Plugin

The HolePunch plugin can be used in combination with the Server to manage port-forwarding in your game through a method known as hole punching. To get started with the plugin start by importing the addons folder into your Godot game folder and enabling the plugin. Afterwards you can add the HolePunch node to the scene where you utilize matchmaking to begin setting up hole punching for your game.


### Documentation


#### Properties

| Type        | Name            |
| ----------- | --------------- |
|PacketPeerUDP|server_udp       |
|PacketPeerUDP|peer_udp         |
| String      |client_name      |
| String      |rendevouz_address|
| String      |host_address     |
| String      |host_port        |
| int         |rendevouz_port   |
| int         |max_player_count |
| bool        |is_host          |
| bool        |starting_game    |

#### Methods

| Return type | Name                                                                  |
| ----------- | ----------------------------------------------------------------------|
| void        | start_traversal( string key, bool is_player_host, string player_name) |
| void        | finalize_peers( string key)                                           |

#### Signals

-`hole_punched(int my_port, int hosts_port, string hosts_address)`

Emitted when all peers have completed their holepunch and are ready to connect to your game server

#### Property Descriptions

-`PacketPeerUDP server_udp` The server PackPeerUDP used for connecting to the server. Not usually necessary to interact with directly as the node will handle most of this.


-`PacketPeerUDP peer_udp` The peer PackPeerUDP used for connecting to peers. Not usually necessary to interact with directly as the node will handle most of this.

-`string client_name` The name the player or client is using on the local machine.

-`string rendevouz_address` The ip address that is being used for the intermediate or holepunch server.

-`string host_address` The ip address of the confirmed host (will default to "" if the client is the host or before the host information is obtained).

-`string host_port` The port of the confirmed host (will default to 0 if the client is the host or before the host information is obtained).

-`int rendevouz_port` The port that is being used for the intermediate or holepunch server.

-`int max_player_count` The maximum amount of players the holepunch server sessions will account for before automatically connecting peers.

-`bool is_host` If the client running this game is the client hosting the game server or not.


#### Method Descriptions

-`void start_traversal(string key, bool is_player_host, string player_name)` Call this method on the HolePunch node when you are ready to begin the HolePunch process. 

-`void finalize_peers(string key)` Call this method on the HolePunch node when you want to stop waiting for peers to begin the HolePunch process early before the server has reached the *max_player_count* value.

-`void checkout()` Call this method on the HolePunch node when you want to cancel the HolePunch process after you've already started it.


# Server
 A UDP hole punching server in python + Godot Client

The python server is based on https://github.com/stylesuxx/udp-hole-punching/

Server requires Python 3 and Twisted: https://twistedmatrix.com/trac/

`Usage: ./server.py PORT`



This began as a fork of: https://github.com/dalton5000/tyson/blob/master/LICENSE, but has since been reimplemented
and converted to a plugin.

This simple implementation is still a work in progress. All help and contributions are welcome!



