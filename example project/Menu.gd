extends Node2D

var room_code
var max_connect_time = 20 #if this time is exceeded when joining a game, a fail message is displayed

func _ready():
	get_tree().connect("network_peer_connected", self, "_player_connected")

func _on_ButtonHost_pressed():
	if $RoomCode.text != "":
		room_code = $RoomCode.text
		$HolePunch.start_traversal(room_code, true, Globals.client_name) #Attempt to connect to server as host
		prepare_lobby("ROOM CODE:" + room_code)

func _on_ButtonJoin_pressed():
	if $RoomCode.text != "":
		room_code = $RoomCode.text
		$HolePunch.start_traversal(room_code, false, Globals.client_name) #Attempt to connect to server as client
		prepare_lobby("Connecting to game...")
		$FailTimer.start(max_connect_time)
		
func prepare_lobby(lobby_message):
	var lobby = preload("res://Lobby.tscn").instance()
	get_tree().get_root().add_child(lobby)
	lobby.get_node("CurrentLobby").text = lobby_message
	hide()

func _player_connected(id): #When player connects, load game scene
	Globals.player2id = id
	var game = preload("res://Game.tscn").instance()
	get_tree().get_root().add_child(game)
	queue_free()

func _on_Node_hole_punched(my_port, hosts_port, hosts_address): #When signal recieved that server punched holes to each client
	yield(get_tree(), "idle_frame")
	if $HolePunch.is_host:
		$ConnectTimer.start(2) #Waiting for port to become unused to start game
	else:
		$ConnectTimer.start(10) #Waiting for host to start game

func _on_ConnectTimer_timeout():
	if $HolePunch.is_host:
		var net = NetworkedMultiplayerENet.new() #Create regular godot peer to peer server
		net.create_server($HolePunch.own_port, 2) #You can follow regular godot networking tutorials to extend this
		get_tree().set_network_peer(net)
	else:
		var net = NetworkedMultiplayerENet.new() #Connect to host
		net.create_client(str($HolePunch.host_address), int($HolePunch.host_port), 0, 0, int($HolePunch.own_port))
		get_tree().set_network_peer(net)


func _on_FailTimer_timeout():
	get_tree().root.get_node("Lobby").get_node("CurrentLobby").text = "Failed to connect"
