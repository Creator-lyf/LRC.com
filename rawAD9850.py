#!/usr/local/bin/python
# Run an eBay AD9850 on the RPi GPIO
#
# translated from nr8o's Arduino sketch
# at http://nr8o.dhlpilotcentral.com/?p=83
# 
# m0xpd
# shack.nasties 'at Gee Male dot com'
import RPi.GPIO as GPIO


def output(frequency):
	# 必要函数的定义
	def pulseHigh(pin):  # Function to send a pulse
		GPIO.output(pin, True)  # do it a few times to increase pulse width
		GPIO.output(pin, True)  # (easier than writing a delay loop!)
		GPIO.output(pin, True)
		GPIO.output(pin, False)  # end of the pulse
		return

	def tfr_byte(data):  # Function to send a byte by serial "bit-banging"
		for i in range(0, 8):
			GPIO.output(DATA, data & 0x01)  # Mask out LSB and put on GPIO pin "DATA"
			pulseHigh(W_CLK)  # pulse the clock line
			data = data >> 1  # Rotate right to get next bit
		return

	def sendFrequency(frequency):  # Function to send frequency (assumes 125MHz xtal)
		freq = int(frequency * 4294967296 / 125000000)
		for b in range(0, 4):
			tfr_byte(freq & 0xFF)
			freq = freq >> 8
		tfr_byte(0x00)
		pulseHigh(FQ_UD)
		return

	# setup GPIO options...
	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)

	W_CLK = 12              			# Define GPIO pins
	FQ_UD = 16
	DATA = 18
	RESET = 22

	GPIO.setup(W_CLK, GPIO.OUT)       		# setup IO bits...
	GPIO.setup(FQ_UD, GPIO.OUT)       		#
	GPIO.setup(DATA, GPIO.OUT)        		#
	GPIO.setup(RESET, GPIO.OUT)       		#

	for i in range(1):
		GPIO.output(W_CLK, False)         		# initialize everything to zero...
		GPIO.output(FQ_UD, False)
		GPIO.output(DATA, False)
		GPIO.output(RESET, False)

		pulseHigh(RESET)                  		# start-up sequence...
		pulseHigh(W_CLK)
		pulseHigh(FQ_UD)

		#	frequency = 32500               		# choose frequency and
		sendFrequency(frequency)          		# start the oscillator
		pass
