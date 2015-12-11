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

	def sendPacketToStream(self, stream, packet):
		if stream == None:
			raise Exception('Missing stream Object')
		encodedPacket = self.encode(packet)
		stream.write(encodedPacket)

	def receivePacketFromStream(self, stream, length=1000):
		if stream == None:
			raise Exception('Missing stream Object')
		packet = b''
		received = 0
		while 1:
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

	def append(self, chunk):
		self.stream += chunk

	def decodePackets(self, stream):
		packetlist = []
		packet = self.receivePacketFromStream(stream)
		while(packet != b''):
			packetlist.append(packet)
			packet = self.receivePacketFromStream(stream)
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

