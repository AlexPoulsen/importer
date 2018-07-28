#Importer
Preventing insanity when dealing with local imports

Subdirectory `Importer` is to allow for pushing to interpreter packages directory with `Importer("Importer", copy_packages=True)`

```python
import Importer
Im = Importer.Importer("moduleone", "moduletwo")
Im.moduleone.myfunc("foo", 1, 2)
Im.moduletwo.anotherfunc(3, 4, "bar")
Im.modulethree.func("foo", "bar", "bat")  # yes this works, assuming all three packages are in the directory
Im.moduleone.__file__  # './moduleone/__init__.py'
Im.path("moduleone")  # '/Users/you/folders/moduleone/__init__.py/'
```