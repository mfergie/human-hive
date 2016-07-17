# human-hive

How to run:
- Go to project root
- Add current directory to python path:

```
$ export PYTHONPATH=.
```

Then run the following:
```
python scripts/humanhive_run.py --n-channels 6 --swarm-samples-dir humanhive/tests/audio/ --recorded-samples-dir /tmp/
```

- `--swarm-samples-dir` should point to a folder which contains the sample you want to play. Currently it just picks the first file out of the directory.

- `--recorded-samples-dir` does nothing at this point. 
