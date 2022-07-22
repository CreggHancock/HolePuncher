extends Node

var player2id = -1
var client_name = ""

func _ready():
	randomize()
	client_name = "client" + str(randi())
