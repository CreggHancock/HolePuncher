if not recieved_peer_greet:
			if packet_string.begins_with(PEER_GREET):
				print("peer greet!")
				var m = packet_string.split(":")
				_handle_greet_message(m[1], int(m[2]), int(m[3]))

		if not recieved_peer_confirm:
			if packet_string.begins_with(PEER_CONFIRM):
				print("peer confirm!")
				var m = packet_string.split(":")
				_handle_confirm_message(m[2], m[1], m[4], m[3])

		elif not recieved_peer_go:
			if packet_string.begins_with(PEER_GO):
				print("peer go!")
				var m = packet_string.split(":")
				_handle_go_message(m[1])

#handle peer greet; reconfigure ports
func _handle_greet_message(peer_name, peer_port, my_port):
	if own_port != my_port:
		own_port = my_port
		peer_udp.close()
		peer_udp.listen(own_port, "*")
	recieved_peer_greet = true #see messages at top

#handle confirm
func _handle_confirm_message(peer_name, peer_port, my_port, peer_is_host):
	if peer[peer_name].port != peer_port:
		peer[peer_name].port = peer_port

	peer[peer_name].is_host = peer_is_host
	if peer_is_host:
		host_address = peer[peer_name].address
		host_port = peer[peer_name].port
	peer_udp.close()
	peer_udp.listen(own_port, "*")
	recieved_peer_confirm = true #see messages at top

#handle go; send signal to start game connection
func _handle_go_message(peer_name):
	recieved_peer_go = true #see messages at top
	emit_signal("hole_punched", int(own_port), int(host_port), host_address) #sends signal to game to start
	peer_udp.close()
	p_timer.stop()
	set_process(false) #stop _process

#search for better ports, send greetings accordingly
func _cascade_peer(peer_address, peer_port):
	for i in range(peer_port - port_cascade_range, peer_port + port_cascade_range):
		peer_udp.set_dest_address(peer_address, i)
		var buffer = PoolByteArray()
		buffer.append_array((PEER_GREET+client_name+":"+str(own_port)+":"+str(i)).to_utf8()) #tell peers about new port
		peer_udp.put_packet(buffer)
		ports_tried += 1



	if not recieved_peer_confirm and greets_sent < response_window:
		print("send greet!")
		for p in peer.keys():
			peer_udp.set_dest_address(peer[p].address, int(peer[p].port))
			var buffer = PoolByteArray()
			buffer.append_array((PEER_GREET+client_name+":"+str(own_port)+":"+peer[p].port).to_utf8())
			peer_udp.put_packet(buffer)
			greets_sent+=1
				
	#if the other player hasn't responded we should try more ports
	if not recieved_peer_confirm and greets_sent == response_window:
		print("Receiving no confirm. Starting port cascade")
		for p in peer.keys():
			_cascade_peer(peer[p].address, int(peer[p].port))
		greets_sent += 1

	#send confirm to other peers
	if recieved_peer_greet and not recieved_peer_go:
		print("send confirm!")
		for p in peer.keys():
			peer_udp.set_dest_address(peer[p].address, int(peer[p].port))
			var buffer = PoolByteArray()
			buffer.append_array((PEER_CONFIRM+str(own_port)+":"+client_name+":"+str(is_host)+":"+peer[p].port).to_utf8())
			peer_udp.put_packet(buffer)

	#send gos, and finalize hole punch
	if  recieved_peer_confirm:
		print("send go!")
		for p in peer.keys():
			peer_udp.set_dest_address(peer[p].address, int(peer[p].port))
			var buffer = PoolByteArray()
			buffer.append_array((PEER_GO+client_name).to_utf8())
			peer_udp.put_packet(buffer)
		gos_sent += 1

		if gos_sent >= response_window: #the other player has confirmed and is probably waiting
			emit_signal("hole_punched", int(own_port), int(host_port), host_address)
			p_timer.stop()
			set_process(false)