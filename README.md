# Fast-Audioset-Download
Download audioset data super fastly with youtube-dl and parmap

```shell
foo@bar:/path/to/this/repo $ rm -rf temps/* #if temps folder exist
foo@bar:/path/to/this/repo $ python download.py
```
** Resume supported in case of crash or keyboard interrupt: Only acquire video meta-information(for creating final metadata.json) without downloading actual audio. 

required packages : youtube-dl, parmap, tqdm
