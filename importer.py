import sys
import inspect
import os
import pathlib
import site
import shutil
import typing


class NoPackagesError(Exception):
	__slots__ = ["message"]

	def __init__(self, message):
		self.message = message

	def __repr__(self):
		if self.message:
			return "NoPackagesError: " + self.message
		else:
			return "NoPackagesError"


def called_from(depth):
	out = []
	for x in range(0, depth):
		try:
			out.append(inspect.stack()[x + 2][3])
		except IndexError:
			return out
	return out


def debug(*values, stack_size=4, mini=False):
	typedvals = list(map(lambda x: str(x) + " is " + str(type(x)) + ",", values))
	caller = inspect.getframeinfo(inspect.stack()[1][0])
	if not mini:
		print("<!>", *called_from(stack_size), "IN:" + str(caller.filename) + ":" + str(caller.lineno), ":|:", *typedvals, flush=True)
	elif mini:
		print("<!>", *called_from(stack_size), "line:" + str(caller.lineno), ":|:", *typedvals, flush=True)


def copy_in(path: str, sub: str, *ignore: str):
	return shutil.copytree(path, f"{path}/{sub}/", ignore=(lambda x, y: [sub, *ignore]))


class Importer:
	# __slots__ = ["paths", "copy_packages", "package_location", "packages", "del_packages"]

	def __init__(self, *paths: str, copy_packages: bool = False, del_packages=False):
		self.paths: typing.List[str] = list(paths)
		self.copy_packages = copy_packages
		self.package_location = site.getsitepackages()[0]
		self.packages = {}
		if not copy_packages:
			self.del_packages = False
		else:
			self.del_packages = del_packages
		self.import_package(paths)

	def import_package(self, paths: typing.Union[typing.List[str], typing.Tuple[str]]):
		self.paths = list(set(self.paths + list(paths)))
		if paths.__class__ == str:
			paths = [paths]
		if self.copy_packages:
			for p in paths:
				p = str(p)
				if p.startswith("~/"):
					p_full = str(pathlib.Path.home()) + p[1:]
				elif "/" not in p:
					p_full = f"{str(pathlib.Path(p).resolve())}/"
				else:
					p_full = p
				if os.path.isdir(f"{self.package_location}/{p}"):
					shutil.rmtree(f"{self.package_location}/{p}")
				shutil.copytree(p_full, f"{self.package_location}/{p}")
				self.packages[p] = __import__(p)
		else:
			sys.path.insert(0, '.')
			for p in paths:
				p = str(p)
				self.packages[p] = __import__(p)
		for name, package in self.packages.items():
			self.__dict__[name] = package
		if len(paths) == 1:
			return self.packages[paths[0]]
		else:
			return [self.packages[v] for v in paths]

	def __getattr__(self, item):
		return self.import_package(item)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type:
			print(f"Code resulted in {exc_type.__name__}: {exc_val}")
		if self.copy_packages and self.del_packages:
			for name, package in self.packages.items():
				shutil.rmtree(f"{self.package_location}/{name}")
				print(f"deleted package {name}")

	def path(self, package):
		if package in self.packages:
			return f"{str(pathlib.Path(self.packages[package].__file__).resolve())}/"
		else:
			raise NoPackagesError("No matching packages found")


def push_importer_to_interpreter_path():
	copy_in(".", "Importer", ".git", ".gitattributes")
	Importer("Importer", copy_packages=True)
	shutil.rmtree("Importer")

