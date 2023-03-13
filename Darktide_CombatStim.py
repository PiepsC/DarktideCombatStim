from pynput import keyboard, mouse
from threading import Thread, Event, Lock, current_thread
from inspect import signature
from typing import Callable
import configparser
import argparse

# MIT License

# Copyright (c) 2023 Lars Willemsen

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class SequenceLock(object):
	def __init__(self) -> None:
		self.lock = Lock()
		self.open = True
		self.cident = 0
		self.listeners = []
		self._pause = False
		self._active = True

	def acquire(self) -> bool:
		self.lock.acquire()
		if(not self.open):
			self.lock.release()
			return False
		else:
			self.open = False
			self.lock.release()
			return True
	
	def release(self) -> None:
		self.lock.acquire()
		self.open = True
		self.lock.release()

	def register(self, obj : object) -> None:
		self.lock.acquire()
		self.listeners.append(obj)
		self.lock.release()

	@property
	def pause(self) -> bool:
		return self._pause
	
	# Do NOT call this from within anything but the termination thread as it is not thread safe
	@pause.setter
	def pause(self, val) -> None:
		if(current_thread().ident != self.cident):
			raise Exception("Calling pause setter outside control thread")

		self._pause = val

	@property
	def active(self) -> bool:
		return self._active

	def terminate(self) -> None:
		if(current_thread().ident != self.cident):
			raise Exception("Trying to terminate listeners from outside control thread")

		self._active = False
		for listener in self.listeners:
			listener.stop()

controller_k = keyboard.Controller()
controller_m = mouse.Controller()
mutex = SequenceLock()

# Helper
def TryPress(key, release=True) -> None:
	if(type(key) is str or isinstance(key, keyboard.Key)):
		controller_k.press(key)
		if(release):
			controller_k.release(key)
	else:
		controller_m.press(key)
		if(release):
			controller_m.release(key)

def EmulateKeyRepeated(key : keyboard.Key | mouse.Button, delay: float, count : int, event : Event) -> None:
	for _ in range(count):
		TryPress(key)
		event.wait(timeout=delay)

def EmulateKeyOnce(key: keyboard.Key | mouse.Button) -> None:
	TryPress(key)

def EmulateKeyOncePress(key: keyboard.Key | mouse.Button) -> None:
	TryPress(key, False)

_ACTIONS = {
	2 : EmulateKeyOnce,
	3 : EmulateKeyRepeated,
	4 : EmulateKeyOncePress
}
_PARAMS = [0,0] + [len(signature(p).parameters) for p in _ACTIONS.values()]
# -----

# Core
def KeySequence(inputs : list, event : Event, lock : SequenceLock, args=[]) -> None:
	c = 0
	for i in inputs:
		if(event.is_set()):
			return # Terminated
		if(i == 0): # Then it's a wait
			event.wait(timeout=args[c])
			c += 1
		elif(i == 1): # Then it's the ending of the sequence
			if(lock):
				lock.release()
			return
		else:
			_ACTIONS[i](*args[c:c+_PARAMS[i]])
			c += _PARAMS[i]

def KeySequenceHotkeyTrigger(keystroke : str, inputs : list, lock : SequenceLock, args=[]) -> None:
	event = Event()
	event.clear()
	def Check() -> None:
		if(lock.pause or not lock.acquire()):
			return
		inner = Thread(target=KeySequence, args=[inputs, event, lock, args])
		inner.run()

	def Normalize(f) -> Callable:
		return lambda k: f(k) if isinstance(k, keyboard.Key) else f(poller.canonical(k))

	hotkey = keyboard.HotKey(
		keyboard.HotKey.parse(keystroke),
		Check
	)
	poller = keyboard.Listener(
		on_press=Normalize(hotkey.press),
		on_release=Normalize(hotkey.release)
	)
	lock.register(poller)
	poller.run()
	print("Listener thread terminated")

def ControlThread(pause : str, stop : str, lock : SequenceLock) -> None:
	event = Event()
	event.clear()
	def TogglePause():
		print("Pausing" if not lock.pause else "Resuming")
		lock.cident = current_thread().ident # Assume control over lock
		lock.pause = not lock.pause

	def Terminate():
		print("Terminating")
		lock.cident = current_thread().ident # Assume control over lock
		lock.terminate()
		event.set()

	def Normalize(f) -> Callable:
		return lambda k: f(k) if isinstance(k, keyboard.Key) else f(poller.canonical(k))

	pauseKey = keyboard.HotKey(
		keyboard.HotKey.parse(pause),
		TogglePause
	)
	stopKey = keyboard.HotKey(
		keyboard.HotKey.parse(stop),
		Terminate
	)

	poller = keyboard.Listener(
		on_press=Normalize(pauseKey.press),
		on_release=Normalize(pauseKey.release)
	)
	poller2 = keyboard.Listener(
		on_press=Normalize(stopKey.press),
		on_release=Normalize(stopKey.release)
	)

	poller.start()
	poller2.start()
	event.wait()
	print("Terminated control thread")
	poller.stop()
	poller2.stop()

# -----

def SpawnListeners(delay=0, terminate='', chat='', crouch='', dodge='', dodgemask='', prefix='',
		   left='', back='', right='') -> None:
	
	print("Started Darktide CombatStim!")
	ct = Thread(target=ControlThread, args=[chat, terminate, mutex])
	t1 = Thread(target=KeySequenceHotkeyTrigger, args=[f"{prefix}{left}", [2, 2, 2, 0, 2, 1], mutex, [dodgemask, crouch, dodge, delay, crouch]])
	t2 = Thread(target=KeySequenceHotkeyTrigger, args=[f"{prefix}{right}", [2, 2, 2, 0, 2, 1], mutex, [dodgemask, crouch, dodge, delay, crouch]])
	t3 = Thread(target=KeySequenceHotkeyTrigger, args=[f"{prefix}{back}", [2, 2, 2, 0, 2, 1], mutex, [dodgemask, crouch, dodge, delay, crouch]])
	
	ct.start()
	t1.start()
	t2.start()
	t3.start()

# Parser for individual keys. Reduces it to a single value
def parse(key):
	val = keyboard.HotKey.parse(key)[0]
	return val.char if isinstance(val, keyboard.KeyCode) else val

# SpawnListeners()
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Darktide CombatStim is a macro-like script that allows you to move more erratically without having to break your fingers')
	parser.add_argument('classname', metavar='name', type=str,
						help='the name of the class in the ini file')
	parser.add_argument('-f', '--filename', metavar='file', type=str, nargs=1, required=False, default="combatstim.ini",
						help='the name of the ini file in this folder')
	args = parser.parse_args()

	config = configparser.ConfigParser()
	config.read(args.filename)
	delay = float(config[args.classname]['delay'])
	prefix = config['controls.special']['prefix']
	terminate = config['controls.special']['terminate']
	chat = config['controls.special']['chat']
	keysec = config['controls.keys']
	keys = {}
	for i in keysec.keys():
		keys[i] = parse(keysec[i])

	SpawnListeners(prefix=prefix, delay=delay, terminate=terminate, chat=chat, **keys)