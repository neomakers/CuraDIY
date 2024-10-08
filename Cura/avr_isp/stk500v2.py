import os, struct, sys, time

from serial import Serial
from serial import SerialException

import ispBase, intelHex

class Stk500v2(ispBase.IspBase):
	def __init__(self):
		self.serial = None
		self.seq = 1
		self.lastAddr = -1
	
	def connect(self, port = 'COM3', speed = 115200):
		if self.serial != None:
			self.close()
		try:
			self.serial = Serial(port, speed, timeout=1)
		except SerialException as e:
			raise ispBase.IspError("Failed to open serial port")
		except:
			raise ispBase.IspError("Unexpected error while connecting to serial port:" + port + ":" + str(sys.exc_info()[0]))
		self.seq = 1
		
		#Reset the controller
		self.serial.setDTR(1)
		self.serial.setDTR(0)
		time.sleep(0.2)
		
		self.sendMessage([1])
		if self.sendMessage([0x10, 0xc8, 0x64, 0x19, 0x20, 0x00, 0x53, 0x03, 0xac, 0x53, 0x00, 0x00]) != [0x10, 0x00]:
			self.close()
			raise ispBase.IspError("Failed to enter programming mode")

	def close(self):
		if self.serial != None:
			self.serial.close()
			self.serial = None
	
	def isConnected(self):
		return self.serial != None
	
	def sendISP(self, data):
		recv = self.sendMessage([0x1D, 4, 4, 0, data[0], data[1], data[2], data[3]])
		return recv[2:6]
	
	def writeFlash(self, flashData):
		#Set load addr to 0, in case we have more then 64k flash we need to enable the address extension
		flashSize = self.chip['pageSize'] * 2 * self.chip['pageCount']
		if flashSize > 0xFFFF:
			self.sendMessage([0x06, 0x80, 0x00, 0x00, 0x00])
		else:
			self.sendMessage([0x06, 0x00, 0x00, 0x00, 0x00])
		
		loadCount = (len(flashData) + 0xFF) / 0x100
		for i in xrange(0, loadCount):
			recv = self.sendMessage([0x13, 0x01, 0x00, 0xc1, 0x0a, 0x40, 0x4c, 0x20, 0x00, 0x00] + flashData[(i * 0x100):(i * 0x100 + 0x100)])
			if self.progressCallback != None:
				self.progressCallback(i + 1, loadCount*2)
	
	def verifyFlash(self, flashData):
		#Set load addr to 0, in case we have more then 64k flash we need to enable the address extension
		flashSize = self.chip['pageSize'] * 2 * self.chip['pageCount']
		if flashSize > 0xFFFF:
			self.sendMessage([0x06, 0x80, 0x00, 0x00, 0x00])
		else:
			self.sendMessage([0x06, 0x00, 0x00, 0x00, 0x00])
		
		loadCount = (len(flashData) + 0xFF) / 0x100
		for i in xrange(0, loadCount):
			recv = self.sendMessage([0x14, 0x01, 0x00, 0x20])[2:0x102]
			if self.progressCallback != None:
				self.progressCallback(loadCount + i + 1, loadCount*2)
			for j in xrange(0, 0x100):
				if i * 0x100 + j < len(flashData) and flashData[i * 0x100 + j] != recv[j]:
					raise ispBase.IspError('Verify error at: 0x%x' % (i * 0x100 + j))

	def sendMessage(self, data):
		message = struct.pack(">BBHB", 0x1B, self.seq, len(data), 0x0E)
		for c in data:
			message += struct.pack(">B", c)
		checksum = 0
		for c in message:
			checksum ^= ord(c)
		message += struct.pack(">B", checksum)
		try:
			self.serial.write(message)
			self.serial.flush()
		except SerialTimeoutException:
			raise ispBase.IspError('Serial send timeout')
		self.seq = (self.seq + 1) & 0xFF
		return self.recvMessage()
	
	def recvMessage(self):
		state = 'Start'
		checksum = 0
		while True:
			s = self.serial.read()
			if len(s) < 1:
				raise ispBase.IspError("Timeout")
			b = struct.unpack(">B", s)[0]
			checksum ^= b
			#print hex(b)
			if state == 'Start':
				if b == 0x1B:
					state = 'GetSeq'
					checksum = 0x1B
			elif state == 'GetSeq':
				state = 'MsgSize1'
			elif state == 'MsgSize1':
				msgSize = b << 8
				state = 'MsgSize2'
			elif state == 'MsgSize2':
				msgSize |= b
				state = 'Token'
			elif state == 'Token':
				if b != 0x0E:
					state = 'Start'
				else:
					state = 'Data'
					data = []
			elif state == 'Data':
				data.append(b)
				if len(data) == msgSize:
					state = 'Checksum'
			elif state == 'Checksum':
				if checksum != 0:
					state = 'Start'
				else:
					return data


def main():
	programmer = Stk500v2()
	programmer.connect()
	programmer.programChip(intelHex.readHex("cfg_4f55234def059.hex"))
	sys.exit(1)

if __name__ == '__main__':
	main()
