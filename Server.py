"""UDP hole punching server."""
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from time import sleep

import sys

autostart = False

def address_to_string(address):
	ip, port = address
	return ':'.join([ip, str(port)])

class ServerFail(Exception): #used to catch errors and invalid registering, and relay to client
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return(repr(self.value))

class ServerProtocol(DatagramProtocol):

	def __init__(self):
		self.active_sessions = {}
		self.registered_clients = {}

	def name_is_registered(self, name):
		return name in self.registered_clients

	def create_session(self, s_id, client_list):
		if s_id in self.active_sessions:
			print("Tried to create existing session")
			raise(ServerFail("Tried to create existing session"))

		self.active_sessions[s_id] = Session(s_id, client_list, self)

	def remove_session(self, s_id):
		try:
			del self.active_sessions[s_id]
		except KeyError:
			print("Tried to terminate non-existing session")


	def register_client(self, c_name, c_session, c_ip, c_port, c_nickname):
		if self.name_is_registered(c_name):
			print("Client %s is already registered." % [c_name])
			raise(ServerFail("Client already registered"))
			#this case should probably disconnect the old one
		if not c_session in self.active_sessions:
			print("Client registered for non-existing session")
			raise(ServerFail("Client registered for non-existing session"))
		elif len(self.active_sessions[c_session].registered_clients) >= int(self.active_sessions[c_session].client_max):
			print("Session full")
			raise(ServerFail("Session full"))
		else:
			new_client = Client(c_name, c_session, c_ip, c_port, c_nickname)
			self.registered_clients[c_name] = new_client
			self.active_sessions[c_session].client_registered(new_client)

	def exchange_info(self, c_session):
		if not c_session in self.active_sessions:
			return
		self.active_sessions[c_session].exchange_peer_info()

	def client_checkout(self, name):
		try:
			c = self.registered_clients[name]
			for s in self.active_sessions:
				if c in self.active_sessions[s].registered_clients:
					self.active_sessions[s].registered_clients.remove(c)
					self.active_sessions[s].update_lobby()
			del self.registered_clients[name] #deleting c would not delete the index
		except Exception as e:
			print("Error unregistering client", e)

	def datagramReceived(self, datagram, address):
		"""Handle incoming datagram messages."""
		print(datagram)
		data_string = datagram.decode("utf-8")
		msg_type = data_string[:2]

		if msg_type == "rs":
			# register session
			c_ip, c_port = address
			self.transport.write(bytes('ok:'+str(c_port),"utf-8"), address)
			split = data_string.split(":")
			session = split[1]
			max_clients = split[2]
			try:
				self.create_session(session, max_clients)
			except ServerFail as e:
				self.transport.write(bytes('close:'+str(e),"utf-8"), address)

		elif msg_type == "rc":
			# register client
			split = data_string.split(":")
			c_name = split[1]
			c_session = split[2]
			c_nickname = split[3]
			c_ip, c_port = address
			self.transport.write(bytes('ok:'+str(c_port),"utf-8"), address)
			try:
				self.register_client(c_name, c_session, c_ip, c_port, c_nickname)
			except ServerFail as e:
				self.transport.write(bytes('close:'+str(e),"utf-8"), address)

		elif msg_type == "ep":
			# exchange peers
			split = data_string.split(":")
			c_session = split[1]
			self.exchange_info(c_session)

		elif msg_type == "cc":
			# checkout client
			split = data_string.split(":")
			c_name = split[1]
			self.client_checkout(c_name)

		elif msg_type == "cs":
			# close session
			split = data_string.split(":")
			c_session = split[1]
			c_reason = split[2]
			c_ip, c_port = address
			try:
				self.active_sessions[c_session].close(c_ip,c_reason)
			except KeyError:
				print("Host tried to close non-existing session")
				


class Session:

	def __init__(self, session_id, max_clients, server):
		self.id = session_id
		self.client_max = max_clients
		self.server = server
		self.registered_clients = []

	def update_lobby(self):
		nicknames = []
		for client in self.registered_clients:
			nicknames.append(client.nickname)
		for client in self.registered_clients:
			message = bytes("lobby:"+(",".join(nicknames))+":"+self.client_max, "utf-8")
			self.server.transport.write(message, (client.ip, client.port))

	def client_registered(self, client):
		if client in self.registered_clients: return
		# print("Client %c registered for Session %s" % client.name, self.id)
		self.registered_clients.append(client)
		if autostart and len(self.registered_clients) == int(self.client_max):
			sleep(5)
			print("waited for OK message to send, sending out info to peers")
			self.exchange_peer_info()
		self.update_lobby()

	def exchange_peer_info(self):
		for addressed_client in self.registered_clients:
			address_list = []
			for client in self.registered_clients:
				if not client.name == addressed_client.name:
					address_list.append(client.name + ":" + address_to_string((client.ip, client.port)))
			address_string = ",".join(address_list)
			message = bytes( "peers:" + address_string, "utf-8")
			self.server.transport.write(message, (addressed_client.ip, addressed_client.port))

		print("Peer info has been sent. Terminating Session")
		for client in self.registered_clients:
			self.server.client_checkout(client.name)
		self.server.remove_session(self.id)

	def close(self, host_ip, reason):
		if len(self.registered_clients) == 0 or self.registered_clients[0].ip != host_ip:
			return #just a bit of security, non hosts can't close session
		for client in self.registered_clients:
			message = bytes("close:"+reason, "utf-8")
			self.server.transport.write(message, (client.ip, client.port))
			del self.server.registered_clients[client.name]
		print("Closing session due to: "+reason)
		self.server.remove_session(self.id)

class Client:

	def confirmation_received(self):
		self.received_peer_info = True

	def __init__(self, c_name, c_session, c_ip, c_port, c_nickname):
		self.name = c_name
		self.session_id = c_session
		self.ip = c_ip
		self.port = c_port
		self.nickname = c_nickname
		self.received_peer_info = False

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: ./server.py PORT AUTOSTART(y/n)")
		sys.exit(1)
	port = int(sys.argv[1])
	autostart = sys.argv[2]=="y"
	reactor.listenUDP(port, ServerProtocol())
	print('Listening on *:%d' % (port))
	reactor.run()
