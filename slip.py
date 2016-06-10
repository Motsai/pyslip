#!/usr/bin/env python
import serial as sc
import binascii
import io


class slip():
    """
        SLIP decoder
    """
    SLIP_END = b'\xc0' # dec: 192
    SLIP_ESC = b'\xdb' # dec: 219
    SLIP_ESC_END = b'\xdc' # dec: 220
    SLIP_ESC_ESC = b'\xdd' # dec: 221

    def sendPacketToStream(self, stream, packet):
        if stream == None:
            raise Exception('Missing stream Object')
        encodedPacket = self.encode(packet)
        stream.write(encodedPacket)

    def receivePacketFromStream(self, stream, length=1000):
        if stream == None:
            raise Exception('Missing stream Object')
        fileStream = (type(stream) == io.BufferedReader)
        packet = b''
        received = 0
        stream._timeout = 0.01
        while 1:
            serialByte = stream.read(1)
            if serialByte is None:
                raise Exception('Bad character from stream')
            elif len(serialByte) == 0:
                if fileStream: # EOF reached
                    return serialByte
                else:
                    # raise TimeoutError('Read timed out')
                    break
            elif serialByte == self.SLIP_END:
                if len(packet) > 0:
                    return packet
            elif serialByte == self.SLIP_ESC:
                serialByte = stream.read(1)
                if serialByte is None:
                    return -1
                elif len(serialByte) == 0:
                    if fileStream: # EOF reached
                        return serialByte
                    else:
                        # raise TimeoutError('Read timed out')
                        break
                elif serialByte == self.SLIP_ESC_END:
                    packet += self.SLIP_END
                elif serialByte == self.SLIP_ESC_ESC:
                    packet += self.SLIP_ESC
                else:
                    raise Exception('SLIP Protocol Error')
            elif received < length:
                received = received + 1
                packet += serialByte

    def decodePackets(self, stream):
        packetlist = []
        packet = self.receivePacketFromStream(stream)
        while(packet != b''):
            packetlist.append(packet)
            packet = self.receivePacketFromStream(stream)
        return packetlist

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

