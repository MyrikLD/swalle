from __future__ import print_function

import binascii
import logging
import time

from bluepy import btle


# Author:
#   Siarhei Yorsh (MyrikLD)
# Source:
#    https://github.com/MyrikLD/swalle
# Free to modify and use as you wish, so long as my name remains in this file.
# Special thanks to IanHarvey for bluepy


def find(mac=None):
	cnt = 0

	if mac != None:
		mac = mac.upper()
		while True:
			for i in btle.Scanner(0).scan(1):
				if i.addr.upper() == mac:
					return mac
			cnt += 1
			logging.info('Try #' + str(cnt))
	while True:
		for i in btle.Scanner(0).scan(1):
			for j in i.getScanData():
				if j[0] == 9 and j[2].startswith('SW'):
					return str(i.addr).upper()
		cnt += 1
		logging.info('Try #' + str(cnt))


class Connection(btle.Peripheral):
	def __init__(self, mac):
		btle.Peripheral.__init__(self, mac)

	def info(self):
		out = dict()

		services = self.getServices()

		for i in services:
			sname = binascii.b2a_hex(i.binVal).decode('utf-8')[4:8]
			print(str(sname))

			ch = services[i].getCharacteristics()

			dat = dict()
			for c in ch:
				name = binascii.b2a_hex(c.uuid.binVal).decode('utf-8')[4:8]
				if c.supportsRead() and name != 'fff5':
					try:
						b = bytearray(c.read())
					except Exception:
						b = ''
					try:
						if name in ('2a50', 'fff6'):
							b = list(b)
						if name in ('fff2', 'fff1'):
							b = b[0]
						logging.info('\t%s: %s' % (name, b))
						dat.update({name: b})
					except Exception:
						logging.info('\t%s: %s' % (name, list(b)))
						dat.update({name: list(b)})
				else:
					logging.info('\t%s: %s' % (name, c.props))
					dat.update({name: c})
			out.update({sname: dat})
		return out


class Ball(object):
	sock = None
	name = None
	mac = None
	_property = 12
	_ledStyle = 0
	_ledRGB = [255, 255, 255]
	_moto_dir = [0, 0]
	_moto_pwm = [0, 0]
	_lastCmd = ''
	autosync = True
	interface = 'hci0'

	NOTIFY = btle.UUID("0000fff6-0000-1000-8000-00805f9b34fb")
	SERVICE = btle.UUID("0000fff0-0000-1000-8000-00805f9b34fb")

	def __init__(self, **kwargs):
		if 'sock' in kwargs:
			logging.info('Connecting by sock')
			self.sock = kwargs['sock']
		elif 'mac' in kwargs:
			logging.info('Connecting by mac')
			self.mac = find()
			self.sock = self._connect(self.mac)
		elif 'name' in kwargs:
			logging.info('Connecting by name')
			self.name = kwargs['name']
			self.mac = find()
			self.sock = self._connect(self.mac)
		else:
			raise IOError("No arguments")
		

	def _connect(self, mac):
		logging.info("Create sock")
		self.dev = Connection(mac)

		service = self.dev.getServiceByUUID(self.SERVICE)
		sock = service.getCharacteristics(self.NOTIFY)[0]

		return sock

	def setRGB(self, red=0, green=0, blue=0, style=0):
		self._ledStyle = int(style)
		self._ledRGB = [int(red), int(green), int(blue)]
		if self.autosync:
			self.sync()

	def red(self, val=255):
		self.setRGB(val, 0, 0)

	def green(self, val=255):
		self.setRGB(val, 0, 0)

	def blue(self, val=255):
		self.setRGB(0, 0, val)

	def white(self, val=255):
		self.setRGB(val, val, val)

	def lights(self):
		self._ledStyle = 4
		if self.autosync:
			self.sync()

	def setMoto(self, dir1, speed1, dir2, speed2):
		self._moto_dir = [int(dir1), int(dir2)]
		self._moto_pwm = [int(min(speed1 * 3.1373, 800)), int(min(speed2 * 3.1373, 800))]
		if self.autosync:
			self.sync()

	def forward(self, speed=255):
		if speed < 0:
			return self.back(abs(speed))
		else:
			self.setMoto(1, speed, 1, speed)

	def left(self, speed=255):
		speed = abs(speed)
		self.setMoto(1, speed, 2, speed)

	def right(self, speed=255):
		speed = abs(speed)
		self.setMoto(2, speed, 1, speed)

	def back(self, speed=255):
		if speed < 0:
			return self.forward(abs(speed))
		else:
			self.setMoto(2, speed, 2, speed)

	def stop(self):
		self.setMoto(0, 0, 0, 0)
		if self.autosync:
			self.sync()

	def _reset(self):
		self.prop = 0
		if self.autosync:
			self.sync()

	def _get_pwm(self):
		ret = list()
		ret.append((self._moto_pwm[0] >> 8) & 255)
		ret.append(self._moto_pwm[0] & 255)
		ret.append((self._moto_pwm[1] >> 8) & 255)
		ret.append(self._moto_pwm[1] & 255)

		return ret

	def _data(self):
		bs = bytearray([65, 66, 112, self._property, 100, self._ledStyle])
		bs += bytearray(self._ledRGB)
		bs += bytearray(self._moto_dir)
		bs += bytearray(self._get_pwm())
		bs += bytearray([66, 65])

		return str(bs)

	def sync(self, s=None):
		if s is None:
			s = self._data()
		# send only new commands
		if self._lastCmd != s:
			self._lastCmd = s
			try:
				self.sock.write(s)
			except btle.BTLEException:
				logging.info("Ball lost, reconnecting")
				mac = find(mac=self.mac)
				self.sock = self._connect(mac)
				self.lights()
				self.sync()


if __name__ == '__main__':
	ball = Ball(name='SW21T025766')

	ball.white()
	time.sleep(1)
	ball.red()
	time.sleep(1)
	ball.green()
	time.sleep(1)
	ball.blue()
	time.sleep(1)

	ball.white()
	ball.lights()
	time.sleep(1)

	ball.forward()
	time.sleep(1)
	ball.left()
	time.sleep(1)
	ball.right()
	time.sleep(1)
	ball.back()
	time.sleep(1)
