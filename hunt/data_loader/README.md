# 2022 Hunt Data Loader
> Note: this repository used to be split across multiple packages, and so the data loader abstraction was important. It's less important now.

Package for loading from [`hunt.data`](/hunt/data/) reliably.

[Python packaging](https://packaging.python.org/discussions/wheel-vs-egg/) is weird and things aren't always filesystems. Sometimes they're eggs, sometimes they're wheels, and sometimes they're sdists. Who knows what they'll be in the future :)

So we need to use some tooling to load data safely. Unfortunately the situation there is also muddled. Notice how [the two top-voted answers](https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package) contradict themselves in this popular Stack Overflow question.

This package provides some wrappers for safely loading hunt data. They require Python 3.9+ as they use the new `importlibs.resources.files(...)` API.
