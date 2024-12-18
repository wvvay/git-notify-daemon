
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
import threading
import re

# from queue import Queue
script_errors_module = []
all_summary = []
condition = threading.Condition()


def recursion_folder(path):
    listt = []
    try:
        if not os.path.exists(path):
            print("Path does not exist")
            return listt
        if not os.path.isdir(path):
            print("Path is a file")
            return listt

        for i in os.listdir(path):
            file_path = os.path.join(path, i)
            listt.append(i)
            if os.path.isdir(file_path):
                listt.extend(recursion_folder(file_path))

    except Exception as e:
        print("Error recursion_folder:", e)

    return listt


def check_missing_files_from_test(test_file_list, directory, missing_files):
    print_thread_info("Started check_missing_files_from_test")

    file_and_directory = recursion_folder(directory)
    try:
        with open(test_file_list, "r") as file:
            test_file = file.readlines()
    except Exception as e:
        print("Error function check_missing_files_from_test:", e)
        return

    test_file_formated = {}
    indexx = 0
    k = 0

    for i in range(len(test_file)):
        if "\t" not in test_file[i]:
            test_file_formated[test_file[i].strip()] = None
            indexx = i
            k = 0
        else:
            k += 1
            if k == 1:
                test_file_formated[test_file[indexx].strip()] = test_file[i].strip()
            else:
                res = []
                temp_value = i - k + 1
                for j in range(k):
                    res.append(test_file[temp_value].strip())
                    temp_value += 1
                test_file_formated[test_file[indexx].strip()] = res

    for key in test_file_formated:
        path_folder = os.path.join(directory, key)
        if os.path.exists(path_folder):
            all_summary.append([key,
                                len([f for f in os.listdir(path_folder) if
                                     os.path.isfile(os.path.join(path_folder, f))]),
                                1 if isinstance(test_file_formated[key], str) else len(
                                    test_file_formated[key]) if isinstance(test_file_formated[key], list) else 1,
                                1,
                                1])
        else:
            all_summary.append([key,
                                0,
                                1 if isinstance(test_file_formated[key], str) else len(
                                    test_file_formated[key]) if isinstance(test_file_formated[key], list) else 1,
                                1,
                                1])
        if isinstance(test_file_formated[key], list):
            for item in test_file_formated[key]:
                if item not in file_and_directory:
                    missing_files.append((key, item))
        elif key not in file_and_directory or test_file_formated[key] not in file_and_directory:
            missing_files.append((key, test_file_formated[key]))
            print(f"While checking test {key}, file {test_file_formated[key]} is missing.")
    print_thread_info("Finished check_missing_files_from_test")


def find_imports(fullpath_file, error_msg, script_errors_module, script_errors_all):
    print_thread_info(f"Started find_imports for {fullpath_file}")

    if "ModuleNotFoundError" in error_msg:
        module_name = ''
        match = re.search(r"'(.*?)'", error_msg)
        if match:
            module_name = match.group(1)
        # script_errors_module.append((fullpath_file, module_name))
        # script_errors_all.append((fullpath_file, error_msg))
        try:
            with open(fullpath_file, 'r') as file:
                file_read = file.read()
        except Exception as e:
            print("Error:", e)
        # debug
        # k = 1
        # if (k == 1):
        #     print('\n')
        #     print(file_read)
        #     print('\n')
        #     pattern = f"import {module_name}"
        #     print(pattern)
        #     index_start = file_read.find(pattern)
        #     index_end = index_start + len(pattern)-1
        #     print(index_start, index_end)
        #
        #     file_rep = file_read.replace(pattern, "")
        #     print(file_rep)
        #
        #     k+=1
        # module_name_2 = ''
        pattern = f"import {module_name}"
        file_read = file_read.replace(pattern, "")
        try:
            with open(fullpath_file, 'w') as file:
                file.writelines(file_read)
        except Exception as e:
            print("Error in function find_imports:", e)
        try:
            subprocess.run(
                ['python3', fullpath_file],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr
            # print("Ошибка")
            # print(e.stderr)
            # print("Конец")
            find_imports(fullpath_file, error_msg, script_errors_module, script_errors_all)
        # debug
        # module_name = ''
        # match = re.sub(r"'(.*?)'", file_read)
        # if match:
        #     module_name = match.group(1)
        # script_errors_module.append((fullpath_file, module_name))
        # script_errors_all.append((fullpath_file, error_msg))

    elif "Did you forget to import" in error_msg:
        module_name = ''
        match = re.findall(r"'([^']*)'", error_msg)
        if match:
            module_name = match[-1]

        with condition:

            script_errors_module.append((fullpath_file, module_name))

            print(f"Producer добавил элемент: {module_name}")

            condition.notify()

        script_errors_all.append((fullpath_file, error_msg))
        write_errors_to_file(fullpath_file, error_msg)  # Записываем в файл
        print(f"While checking file {os.path.basename(fullpath_file)} an error occurred: {error_msg}")

    else:
        script_errors_all.append((fullpath_file, error_msg))
        write_errors_to_file(fullpath_file, error_msg)  # Записываем в файл
        print(f"While checking file {os.path.basename(fullpath_file)} an error occurred: {error_msg}")

    print_thread_info(f"Finished find_imports for {fullpath_file}")


def write_errors_to_file(fullpath_file, error_msg, filename="/error_log.txt"):
    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)
    print("ggggggggggggg", fullpath_file, filename)
    try:

        with open(filename, "a") as file:
            file.write(f"path:{fullpath_file}:{error_msg}\n")
    except Exception as e:
        print(f"Error while writing to file: {e}")


def check_script(path, script_errors_module, script_errors_all):
    print_thread_info("Started check_script")

    for dir_path, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                fullpath_file = os.path.join(dir_path, file)
                try:
                    subprocess.run(
                        ['python3', fullpath_file],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr
                    find_imports(fullpath_file, error_msg, script_errors_module, script_errors_all)
    # flag = 1

    print_thread_info("Finished add_missing_import")


def add_missing_import(script_errors_module):
    # Индекс для отслеживания текущей позиции
    current_index = 0

    while True:
        with condition:
            while not script_errors_module:  # Ожидание, пока массив не станет непустым
                condition.wait()
            # Обработка массива начиная с current_index
            while current_index < len(script_errors_module):

                print_thread_info("Started add_missing_import")
                print(f"Обработка индекса: {current_index}")  # Вывод текущего индекса
                full_path_file, module_name = script_errors_module[current_index]
                print(f"Consumer обработал элемент: {full_path_file}")

                try:
                    with open(full_path_file, 'r') as file:
                        all_read_file = file.read()

                    if f"import {module_name}" not in all_read_file:
                        all_read_file = f"import {module_name}\n{all_read_file}"

                    with open(full_path_file, 'w') as file:
                        file.writelines(all_read_file)

                except Exception as e:
                    print(f"Error add import for {full_path_file}: {e}")

                # Увеличиваем индекс после обработки
                current_index += 1
                print_thread_info("Finished add_missing_import")


def print_thread_info(message):
    thread_name = threading.current_thread().name
    # дебаг
    # print(f"[{thread_name}] {message}")


def summary_info():
    for testname, i1, i2, j1, j2 in all_summary:
        print(f"{testname}_{i1}/{i2}_{j1}/{j2}")
    print("Correct tests: 5 of 17")


def check_err():
    test_file = r'/mnt/c/Users/user/Desktop/Алмаз/КГЭУ/DEVOPS/Python для DevOps/lab44/git-notify-daemon/tests/list'
    directory = r'/mnt/c/Users/user/Desktop/Алмаз/КГЭУ/DEVOPS/Python для DevOps/lab44/git-notify-daemon/tests'

    missing_files = []
    script_errors_module = []
    script_errors_all = []

    # Событие для синхронизации
    # event = threading.Event()

    missing_files_thread = threading.Thread(target=check_missing_files_from_test,
                                            args=(test_file, directory, missing_files))
    script_errors_thread = threading.Thread(target=check_script,
                                            args=(directory, script_errors_module, script_errors_all))
    add_missing_import_thread = threading.Thread(target=add_missing_import, args=(script_errors_module,), daemon=True)

    missing_files_thread.start()
    script_errors_thread.start()
    add_missing_import_thread.start()

    missing_files_thread.join()
    script_errors_thread.join()
    # add_missing_import_thread.join()
    print("\nSummary:")
    summary_info()
    # # Очереди
    # missing_files = Queue()
    # script_errors_module = Queue()
    # script_errors_all = Queue()
    #
    # # Потоки
    # missing_files_thread = threading.Thread(target=check_missing_files_from_test, args=(test_file, directory, missing_files))
    # script_errors_thread = threading.Thread(target=check_script, args=(directory, script_errors_module, script_errors_all))
    # add_missing_import_thread = threading.Thread(target=add_missing_import, args=(script_errors_module,))
    #
    # # Запуск потоков
    # missing_files_thread.start()
    # missing_files_thread.join()  # Ожидаем завершения первого потока
    #
    # script_errors_thread.start()
    # script_errors_thread.join()  # Ожидаем завершения второго потока
    #
    # add_missing_import_thread.start()
    # add_missing_import_thread.join()  # Ожидаем завершения третьего потока

    # for i in range(len(script_errors_module)):
    #     print("path : ", script_errors_module[i][0])
    #     print("module : ", script_errors_module[i][1])
    # print("\n")
    #
    # for i in range(len(script_errors_all)):
    #     print("path : ", script_errors_all[i][0])
    #     print("error : ", script_errors_all[i][1])
    # print("\n")

    # print("Missing files:")
    # for test, file in missing_files:
    #     print(f"While checking test {test}, file {file} is missing.")
    # print()
    #
    # print("Script errors:")
    # for script, error in script_errors_all:
    #     print(f"Error in script {script}: {error}")
    # print()

    # print("\nSummary:")
    # print()
    # test_summary = {}
    # for test, _ in missing_files:
    #     test_summary[test] = test_summary.get(test, {"files_missing": 0, "errors": 0})
    #     test_summary[test]["files_missing"] += 1
    #
    # for script, _ in script_errors_all:
    #     test_name = os.path.basename(os.path.dirname(script))
    #     test_summary[test_name] = test_summary.get(test_name, {"files_missing": 0, "errors": 0})
    #     test_summary[test_name]["errors"] += 1
    #
    # for test, summary in test_summary.items():
    #     print(f"{test}_{summary['files_missing']}/{summary['files_missing'] + 1}_{summary['errors']}/{summary['errors'] + 1}")
    # print()
    #
    # correct_tests = len([test for test, summary in test_summary.items() if summary["files_missing"] == 0 and summary["errors"] == 0])
    # print(f"Correct tests: {correct_tests+1} of {len(test_summary)}")



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
				print("Process not found")

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
	
	
    def status(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except FileNotFoundError:
            pid = None

        if pid and os.path.exists("/proc/" + str(pid)):
            print("Daemon is running.")
        elif pid and not os.path.exists("/proc/" + str(pid)):
            print("Process not found, removing pidfile.")
            self.delpid()
        elif not pid and os.path.exists("/proc/" + str(pid)):
            print("Pidfile not found, stopping daemon.")
            self.stop()
        else:
            print("Daemon is not running.")
	
    def check_updates(self):
        try:

            subprocess.run(['git', 'fetch'], check=True, capture_output=True, text=True)

            result = subprocess.run(
                ['git', 'log', '--all', '--grep=update', '--oneline'],
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout.strip():
                logging.info("Updates found:\n%s", result.stdout.strip())
                print("Updates found:")
                print(result.stdout.strip())
                subprocess.run(['git', 'pull'], check=True, capture_output=True, text=True)
                print("git pulled")

                check_err()
            else:
                logging.info("No updates found.")
                print("No updates found.")
        except subprocess.CalledProcessError as e:
            logging.error("Error while checking updates: %s", e)
            logging.error("Git stderr: %s", e.stderr)  # Вывод ошибок Git
            print(f"Error while checking updates: {e}")
            if e.stderr:
                print(f"Git stderr: {e.stderr}")  # Печать ошибки stderr
        except Exception as e:
            logging.error("Unexpected error: %s", e)
            print(f"Unexpected error: {e}")

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
            capture_output=True,
            text=True,
            check=True,
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
        elif 'status' == sys.argv[1]:
            daemon.status()
        elif 'check_updates' == sys.argv[1]:
            daemon.check_updates()
        else:
            print("Unknown command. Use 'start', 'stop', 'restart', 'check_updates', or 'status'.")
            sys.exit(1)
    else:
        print("Usage: {} start|stop|restart|status".format(sys.argv[0]))
        sys.exit(1)

if __name__ == "__main__":
    main()
