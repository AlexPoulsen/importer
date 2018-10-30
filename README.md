# importer

Preventing insanity when dealing with local imports

Pushing Importer to the interpreter package directory with `push_importer_to_interpreter_path()`

The command copies the folder into itself ignoring git files and preventing infinite looping, initializes Importer with the copied version of itself and pushes it to the interpreter package directory, and deletes the created copy.

```python
import importer
Im = importer.Importer("moduleone", "moduletwo")
Im.moduleone.myfunc("foo", 1, 2)
Im.moduletwo.anotherfunc(3, 4, "bar")
Im.modulethree.func("foo", "bar", "bat")  # yes this works, assuming all three packages are in the directory
Im.moduleone.__file__  # './moduleone/__init__.py'
Im.path("moduleone")  # '/Users/you/folders/moduleone/__init__.py/'
```

Packages with invalid characters in the name (-, /, $, +, etc) are now edited to remove them, and they are replaced with underscores. Even though this should work fine, you should still edit the package's name, if possible, to a valid name. Names starting with a number have it replaced with a _ by default.

Tested on py3.7, but should work on py3.6 as that is when f-strings were added. Importer could be backported further easily.
