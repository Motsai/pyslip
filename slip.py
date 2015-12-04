#!/usr/bin/env python
import serial as sc
import binascii

# SLIP decoder
class slip():

	def __init__(self, serialFD = None):
		self.started = False
		self.escaped = False
		self.stream = b''
		self.packet = bytearray()
		self.rejectedPackets = []
		self.SLIP_END = b'\xc0'		# dec: 192
		self.SLIP_ESC = b'\xdb'		# dec: 219
		self.SLIP_ESC_END = b'\xdc'	# dec: 220
		self.SLIP_ESC_ESC = b'\xdd'	# dec: 221
		self.serialComm = serialFD
		
	def attachSerialComm(self, serialFD):
		self.serialComm = serialFD

	def sendPacket(self, packet):
		if self.serialComm == None:
			raise Exception('Missing Serial Comm Object')
		encodedPacket = self.encode(packet)
		for char in encodedPacket:
			sc.sendChar(char)

	def sendPacketToStream(self, packet, stream):
		if stream == None:
			raise Exception('Missing stream Object')
		encodedPacket = self.encode(packet)
		for char in encodedPacket:
			sc.sendChar(char)

	def receivePacketFromStream(self, stream, length=1000):
		if stream == None:
			raise Exception('Missing stream Object')
		packet = b''
		received = 0
		while 1:
			# ii = ii + 1
			# if ii > 50:
			# 	return packet
			serialByte = stream.read(1)
			if serialByte is None:
				raise Exception('Bad character from stream')
			elif serialByte == b'': # EOF reached
				return serialByte
			elif serialByte == self.SLIP_END:
				if len(packet) > 0:
					return packet
			elif serialByte == self.SLIP_ESC:
				serialByte = stream.read(1)
				if serialByte is None:
					return -1
				elif serialByte == self.SLIP_ESC_END:
					packet += self.SLIP_END
				elif serialByte == self.SLIP_ESC_ESC:
					packet += self.SLIP_ESC
				else:
					raise Exception('SLIP Protocol Error')
			elif received < length:
				received = received + 1
				packet += serialByte


	def receivePacketFromComm(self):
		if self.serialComm == None:
			raise Exception('Missing Serial Comm Object')
		packet = []
		while 1:
			serialByte = sc.receiveChar(self.serialComm)
			if serialByte is None:
				raise Exception('Bad character from serial interface')
			elif serialByte == self.SLIP_END:
				if len(packet) > 0:
					return packet
			elif serialByte == self.SLIP_ESC:
				serialByte = sc.receiveChar(self.serialComm)
				if serialByte is None:
					return -1
				elif serialByte == self.SLIP_ESC_END:
					packet.append(self.SLIP_END)
				elif serialByte == self.SLIP_ESC_ESC:
					packet.append(self.SLIP_ESC)
				else:
					raise Exception('SLIP Protocol Error')
			else:
				 packet.append(serialByte)
		return

	def append(self, chunk):
		self.stream += chunk
		# self.stream += chunk.decode('iso-8859-1')

	def decodePackets(self):
		packetlist = []
		packet = self.receivePacketFromStream(self.stream)
		packetlist.append(packet)
		while(packet != b''):
			packet = self.receivePacketFromStream(self.stream)
			packetlist.append(packet)
		return packetlist

	def decode(self):
		packetlist = []
		for byte in self.stream:	
			# SLIP_END
			if byte == self.SLIP_END:
				if self.started:
					packetlist.append(self.packet)
				else:
					self.rejectedPackets.append(self.packet)
					self.started = True
				self.packet = ''
			# SLIP_ESC
			elif byte == self.SLIP_ESC:
				self.escaped = True
			# SLIP_ESC_END
			elif byte == self.SLIP_ESC_END:
				if self.escaped:
					self.packet += self.SLIP_END
					self.escaped = False
				else:
					self.packet += byte
			# SLIP_ESC_ESC
			elif byte == self.SLIP_ESC_ESC:
				if self.escaped:
					self.packet += self.SLIP_ESC
					self.escaped = False
				else:
					self.packet += byte
			# all others
			else:
				if self.escaped:
					raise Exception('SLIP Protocol Error')
					self.packet = ''
					self.escaped = False
				else:
					self.packet += byte
					# self.started = True
		self.stream = ''
		self.started = False
		return (packetlist)
		
	def encode(self, packet):
		# Encode an initial END character to flush out any data that 
		# may have accumulated in the receiver due to line noise
		encoded = b''
		# encoded = self.SLIP_END
		packetBytes = [packet[ii:ii+1] for ii in range(len(packet))]
		for byte in packetBytes:
			# SLIP_END
			if byte == self.SLIP_END:
				encoded +=  self.SLIP_ESC + self.SLIP_ESC_END
			# SLIP_ESC
			elif byte == self.SLIP_ESC:
				encoded += self.SLIP_ESC + self.SLIP_ESC_ESC
			# the rest can simply be appended
			else:
				encoded += byte
		encoded += self.SLIP_END
		return (encoded)

