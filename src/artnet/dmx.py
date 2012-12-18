import time, sys, socket, logging, threading

from artnet import packet

log = logging.getLogger(__name__)

def create_multifade(frames, secs=5.0, fps=40):
	result = []
	total_frames = len(frames)
	for index in range(total_frames):
		if(index < len(frames) - 1):
			result.extend(create_fade(frames[index], frames[index+1], secs/(total_frames-1), fps))
	return result

def create_fade(start, end, secs=5.0, fps=40):
	result = []
	for position in range(int(secs * fps)):
		frame = [0] * 512
		for channel in range(len(start)):
			a = start[channel] or 0
			b = end[channel] or 0
			frame[channel] = int(a + (((b - a) / (secs * fps)) * position))
		result.append(frame)
	return result

def get_channels(fixtures):
	fixtures = fixtures if isinstance(fixtures, list) else [fixtures]
	channels = [0] * 512
	for f in fixtures:
		for offset, value in f.getState():
			if(offset is None):
				continue
			channels[(f.address - 1) + offset] = value
	return channels

class Controller(threading.Thread):
	def __init__(self, address, fps=40.0, nodaemon=False):
		super(Controller, self).__init__()
		self.address = address
		self.fps = fps
		self.last_frame = [0] * 512
		self.queue = []
		self.access_lock = threading.Lock()
		self.nodaemon = nodaemon
		self.daemon = not nodaemon
		self.running = True
	
	def stop(self):
		try:
			self.access_lock.acquire()
			if(self.running):
				self.running = False
		finally:
			self.access_lock.release()
	
	def enqueue(self, frames):
		try:
			self.access_lock.acquire()
			self.queue.extend(frames)
		finally:
			self.access_lock.release()
	
	def dequeue(self):
		try:
			self.access_lock.acquire()
			return self.queue.pop(0)
		finally:
			self.access_lock.release()
	
	def run(self):
		now = time.time()
		while(self.queue if self.nodaemon else self.running):
			drift = now - time.time()
			self.last_frame = self.dequeue() if self.is_busy() else self.last_frame
			self.send_dmx(self.last_frame)
			elapsed = time.time() - now
			excess = (1 / self.fps) - elapsed
			if(excess > 0):
				time.sleep(excess - drift)
			now = time.time()
	
	def is_busy(self):
		return bool(self.queue)
	
	def send_dmx(self, channels):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.bind(('', packet.ARTNET_PORT))
		
		p = packet.DmxPacket()
		for index in range(len(channels)):
			p[index] = channels[index]
		
		#log.info(p)
		
		sock.sendto(p.encode(), (self.address, packet.ARTNET_PORT))
		sock.close()

	