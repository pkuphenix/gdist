## Introduction
"gdist" means "game distribution". This util is created for easily distribute multi-depth resource files
 into a single directory with changed file names which contains a digest of the file content itself. **Incremental
 update** is supported based on the digests. It's useful for manage and distribute resources for C/S online games.
 
This small utility will recursively traverse a directory, compute MD5 digest for all containing files
 and then copy them to an single output directory. The mappings from the original file pathes (relative)
 to the new pathes are outputed in JSON format.
 
For example, if you have following files in the input directory:
`
indir/image/a.png
indir/image/b.png
indir/index.html
indir/style/test.css
`

With the "gdist.py", you can get a output directory copied into these files with new names:
`
outdir/a.433dfdc7ad50d2241c46b60eb6c70c2b.png
outdir/b.a06966b0fecb07d863b8fa06c177d23d.png
outdir/index.eacf331f0ffc35d4b482f1d15a887d3b.html
outdir/test.3116a8e065cf41f2912d91e81283abf2.css
`

And you can get a mapping JSON:
`
{
"indir/image/a.png":"a.433dfdc7ad50d2241c46b60eb6c70c2b.png",
...
}
`

## Usage
**gdist.py** \[ -v \] \[ -i _indir_ \] \[ -o _outdir_ \] \[ -f _file_ \] \[ -r _reference_ \]

* **-v**   Verbose mode
* **-i**   Assign the input directory (default ./)
* **-o**   Assign the output directory (default ./gdist)
* **-f**   Assign the output file for mapping JSON (default ./gdist.json)
* **-r**   Assign the reference mapping JSON for incremental update. Only files 
 with digests different from the reference JSON are copied.

## License
*MIT license*: <http://lqian.mit-license.org>
