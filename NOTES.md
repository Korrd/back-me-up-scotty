# Notes & thoughts

This is the native python module for compressing stuff. We don't use it as it is single-threaded, as far as we know.
```python
# import tarfile
# tarfile.open(destination, "w:gz").add(source)
```

Some notes on split(), rsplit() & partition()
```python
# rsplit = split on last occurence
# split = split on first occurence
# partition = splits into three elements, containing left, separator and right sides
```