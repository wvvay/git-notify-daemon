
import os
import atexit
import signal
import subprocess
import time
import sys
import logging
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

# Настройка логирования
logging.basicConfig(
    filename='/tmp/git_commit_notifier.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

class MyDaemon(Daemon):
    def run(self):
        os.chdir(r'/mnt/c/Users/user/Desktop/Алмаз/КГЭУ/DEVOPS/Python для DevOps/lab44/git-notify-daemon/')
        while True:
            time.sleep(5)
            check_new_commits()

def check_new_commits():
    try:
        # Загружаем обновления из удаленного репозитория
        subprocess.run(['git', 'fetch'], check=True)
        logging.debug("Fetched updates from remote repository.")

        # Выполняем команду git log для получения новых коммитов
        result = subprocess.run(
            [
                'git', 'log', '--graph',
                '--pretty=format:%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr)%Creset',
                '--abbrev-commit', '--date=relative', 'main..origin/main'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )

        # Логируем результат выполнения команды
        logging.debug("git log output:\n" + result.stdout.strip())

        # Если есть новые коммиты, отправляем уведомление
        if result.stdout.strip():
            logging.info("New commits detected.")
            notify_user(result.stdout.strip())
        else:
            logging.debug("No new commits.")

    except subprocess.CalledProcessError as e:
        logging.error("Error in check_new_commits: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)

def notify_user(message):
    Notify.init("Git Commit Notifier")
    notification = Notify.Notification.new("New commits detected!", message, "dialog-information")
    notification.show()
    logging.info("Notification sent with message: %s", message)

def main():
    daemon = MyDaemon('/tmp/daemon-example.pid')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command. Use 'start', 'stop', or 'restart'.")
            sys.exit(1)
    else:
        print("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(1)

if __name__ == "__main__":
    main()
