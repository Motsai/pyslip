import unittest
import slip
import struct

class ut_Slip(unittest.TestCase):

	def setUp(self):
		self.slip = slip.slip()

	def getTestStream(self, filepath):
		self.testFile = open(filepath, "rb")

		# Decode the slip packets
		testSlipPackets = self.slip.decodePackets(self.testFile)
		self.testFile.close()

		return testSlipPackets

	def testSLIPDecode(self):
		packets = self.getTestStream("testdata.bin")

		# Check that a correct amount of packets have been decoded
		self.assertEqual(len(packets), 4)

		# Check content of first packet
		self.assertEqual(packets[1][0], 10)
		self.assertEqual(packets[1][1], 11)
		self.assertEqual(packets[1][2], 12)
		self.assertEqual(packets[1][3], 13)
		self.assertEqual(packets[1][4], 14)
		self.assertEqual(packets[1][5], 15)
		self.assertEqual(packets[1][6], 14)

		self.assertEqual(packets[2][0], 1)
		self.assertEqual(packets[2][1], 2)
		self.assertEqual(packets[2][2], 3)
		self.assertEqual(packets[2][3], 4)
		self.assertEqual(packets[2][4], 5)
		self.assertEqual(packets[2][5], 6)
		self.assertEqual(packets[2][6], 7)
		self.assertEqual(packets[2][7], 8)
		self.assertEqual(packets[2][8], 9)
		self.assertEqual(packets[2][9], 10)

	# Make sure that decoding and re-encoding SLIP packets works well
	def testSLIPDecodeEncode(self):
		nebSlip = slip.slip()
		testFile = open("testdata.bin", "rb")
		initialPackets = nebSlip.decodePackets(testFile)
		testFile.close()

		testFile = open("encodedPackets.bin", "wb")
		for packet in initialPackets:
			encodedPacket = self.slip.encode(packet)
			testFile.write(encodedPacket)
		testFile.close()

		testFile = open("encodedPackets.bin", "rb")
		newPackets = nebSlip.decodePackets(testFile)
		testFile.close()

		for idx,newPacket in enumerate(newPackets):
			self.assertEqual(newPacket, initialPackets[idx])



if __name__ == "__main__":
	unittest.main() # run all tests
	print (unittest.TextTestResult)
