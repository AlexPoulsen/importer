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


def copy_in(path: str, sub: str, *ignore: str):
	return shutil.copytree(path, f"{path}/{sub}/", ignore=(lambda x, y: [sub, *ignore]))


invalid_chars = {
	"~":  "_",
	"`":  "_",
	"!":  "i",
	"@":  "a",
	"#":  "H",
	"$":  "S",
	"%":  "X",
	"^":  "v",
	"&":  "A",
	"*":  "x",
	"(":  "_",
	")":  "_",
	"-":  "_",
	"+":  "_",
	"=":  "_",
	"{":  "_",
	"}":  "_",
	"[":  "_",
	"]":  "_",
	"|":  "I",
	"\\": "_",
	":":  "i",
	";":  "j",
	"\"": "_",
	"'":  "_",
	"<":  "v",
	">":  "v",
	",":  "_",
	".":  "_",
	"?":  "Q",
	"/":  "_"
}


def char_range(c1, c2):
	"""Generates the characters from `c1` to `c2`, inclusive."""
	return [chr(c) for c in range(ord(c1), ord(c2) + 1)]


valid_chars = [*char_range("a", "z"), *char_range("A", "Z"), *char_range("0", "9")]


def name_check(name: str, fallback_char: str = None, reduce_replaced: bool = False):
	if fallback_char is None:
		replace_known_invalid = "".join([invalid_chars[L] if L in invalid_chars else L for L in name])
		valid = "".join([L if L in valid_chars else "_" for L in replace_known_invalid])
	else:
		replace_known_invalid = "".join([fallback_char if L in invalid_chars else L for L in name])
		valid = "".join([L if L in valid_chars else fallback_char for L in replace_known_invalid])
	if reduce_replaced:
		temp_valid = []
		last = ""
		for O, L in zip(name, valid):
			if (L == last) and (L != O):
				pass
			else:
				temp_valid += [L]
		return "".join(temp_valid)
	else:
		return valid


class Importer:

	def __init__(self, *paths: str, copy_packages: bool = False, del_packages=False, replace_invalid_with_similar: bool = False, reduce_replaced_chars: bool = False):
		self.paths: typing.List[str] = list(paths)
		self.copy_packages = copy_packages
		self.package_location = site.getsitepackages()[0]
		self.packages = {}
		self.replace_visually = replace_invalid_with_similar
		self.reduce_replaced_chars = reduce_replaced_chars
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
				p_valid_name = name_check(p.split(os.sep)[-1], "_" if not self.replace_visually else None, self.reduce_replaced_chars)
				if p.startswith("~/"):
					p_full = str(pathlib.Path.home()) + p[1:]
				elif "/" not in p:
					p_full = f"{str(pathlib.Path(p).resolve())}/"
				else:
					p_full = p
				if os.path.isdir(f"{self.package_location}/{p}"):
					shutil.rmtree(f"{self.package_location}/{p}")
				shutil.copytree(p_full, f"{self.package_location}/{p}")
				self.packages[p_valid_name] = __import__(p)
		else:
			sys.path.insert(0, '.')
			for p in paths:
				p_valid_name = name_check(p.split(os.sep)[-1], "_" if not self.replace_visually else None, self.reduce_replaced_chars)
				self.packages[p_valid_name] = __import__(p)
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

