# daemon.py
import os
import sys
import atexit
import signal

class Daemon:
	#Constructor
	def __init__(self, pidfile):
		self.pidfile = pidfile

	def daemonize(self):
		"""Deamonize class. UNIX double fork mechanism."""
		try:
			pid = os.fork()
			if pid > 0:
				# exit first parent
				sys.exit(0)
		except OSError as err:
			sys.stderr.write('fork #1 failed: {0}\n'.format(err))
			sys.exit(1)

		# decouple from parent environment
		os.chdir('/')
		os.setsid()
		os.umask(0)

		# do second fork
		try:
			pid = os.fork()
			if pid > 0:
				# exit from second parent
				sys.exit(0)
		except OSError as err:
			sys.stderr.write('fork #2 failed: {0}\n'.format(err))
			sys.exit(1)

		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(os.devnull, 'r')
		so = open(os.devnull, 'a+')
		se = open(os.devnull, 'a+')

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

		# write pidfile
		atexit.register(self.delpid)

		pid = str(os.getpid())
		with open(self.pidfile,'w+') as f:
			f.write(pid + '\n')


	def delpid(self):
		os.remove(self.pidfile)

	def start(self):

		try:
			with open(self.pidfile, 'r') as pf:
				pid = int(pf.read().strip())
		except FileNotFoundError:
			pid = None

		if pid and os.path.exists("/proc/" + str(pid)):
			print("Warning: The daemon is already running with PID = " + str(pid))
			sys.exit(1)

		self.daemonize()
		self.run()

	def stop(self):
		try:
			with open(self.pidfile, 'r') as pf:
				pid = int(pf.read().strip())
		except FileNotFoundError:
			print("Daemon is not runnig")
			pid = None

		if pid:
			try:
				os.kill(pid, signal.SIGTERM)
				self.delpid()
			except ProcessLookupError:
				print("PS not find")

	def restart(self):
		"""Restart the daemon."""
		self.stop()
		self.start()


	def run(self):
		"""You should override this method when you subclass Daemon.

		It will be called after the process has been daemonized by
		start() or restart()."""
		pass