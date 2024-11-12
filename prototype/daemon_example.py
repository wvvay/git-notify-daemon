# daemon_example.py
from daemon import Daemon
import subprocess
import time
import sys
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify


class MyDaemon(Daemon):
	def run(self):
		while True:
			time.sleep(5)
			check_new_commits()

def check_new_commits():
	try:
		# Загружаем обновления из удаленного репозитория
		subprocess.run(['git', 'fetch'], check=True)

		# Выполняем команду git log для получения новых коммитов
		result = subprocess.run(
			[
				'git', 'log', '--graph',
				'--pretty=format:%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr)%Creset',
				'--abbrev-commit', '--date=relative', 'master..origin/master'
			],
			capture_output=True,
			text=True,
			check=True
		)

		# Если есть новые коммиты, отправляем уведомление
		if result.stdout.strip():
			notify_user(result.stdout.strip())

	except subprocess.CalledProcessError as e:
		print("Error in check_new_commits:", e)
	except Exception as e:
		print("Unexpected error:", e)

def notify_user(message):
	Notify.init("Git Commit Notifier")
	notification = Notify.Notification.new("New commits detected!", message, "dialog-information")
	notification.show()

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
