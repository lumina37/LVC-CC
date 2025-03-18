# LVC-CC

This project is designed for crosscheck of the MPEG WG/04 Lenslet Video Coding.

## Prerequisites

### Setup Python Env

```shell
pip install .
```

DO NOT miss the *dot* (`.`) after `install`!

### Build the Executables

Follow the comments in the `base.toml` to download or build binaries.

### Setup `base.toml`

Create a `base.toml` in the project directory. Then follow the comment after each field to configure the workflow.

```toml
frames = 30  # Run 30 frames
views = 5    # Generate 5x5 views

seqs = [
    "Boxer-IrishMan-Gladiator2",
    "Boys2",
    "HandTools",
    "Matryoshka",
    "MiniGarden2",
    "Motherboard2",
    "Fujita2",
    "Origami",
    "TempleBoatGiantR32",
]  # Specify which sequence to run

[dir]
input = "/path/to/input"    # Put the lenslet yuv files into this directory
output = "/path/to/output"  # Anywhere you like

[app]
# Download the binary of [ffmpeg](https://johnvansickle.com/ffmpeg)
ffmpeg = "/path/to/ffmpeg"
# Download the source code of [VTM-11.0](https://vcgit.hhi.fraunhofer.de/jvet/VVCSoftware_VTM/-/tree/VTM-11.0)
# And build the CMake target `EncoderApp`
encoder = "/path/to/EncoderAppStatic"
# Download the source code of [RLC-4.0](https://gitlab.com/mpeg-dense-light-field/rlc/-/tree/version4.0)
# And build the CMake target `RLC40`
convertor = "/path/to/RLC40"

[anchorQP]          # Specifies QPs for anchor generation
Boys2 = [48, 52]    # Mapping from sequence name to the QPs you wanna run
Fujita2 = [42, 44]  # The QPs will be auto-sorted into ascending order

[proc.any_name]     # Extension for pre/postproc with any content you like
example0 = 1
example1 = 0
```

### About the `input` Directory

Please **put the lenslet yuv files** into this directory. Generally, the yuv files should be downloaded from https://content.mpeg.expert/data/CfP/LVC/Sequences.

Once the lenslet yuv files are ready, the structure of the `input` directory **should be something like** `${dir.input}/${sequence_name}/as_you_like.yuv`.

e.g. `/path/to/input/Boys2/Boys2_3976x2956_30fps_8bit.yuv` or `/path/to/input/Fujita/src.yuv`

The file name of the yuv files can be anything you like. But make sure that the name of the parent directory **is identical to** the sequence name!

### SHA1 Checksum

First of all, check the SHA1 checksum of all input yuvs.

```shell
python scripts/checksum.py
```

## Run it!

### Launch the Workflow

Before launching the workflow, please make sure the `output` directory **is sufficient for** several **T**era**B**ytes of data. BTW, a full pass of workflow may take **upto 7 days or more time** to run.

```shell
python cc-00-run-anchor.py
```

### Compute PSNR

```shell
python cc-10-compute.py
```

You can check the draft result in `${dir.output}/summary/tasks`.

### Export to CSV

```shell
python cc-20-export-csv-anchor.py
```

You can check the bitrate, lenslet PSNR and multi-view PSNR in the output csv files in `${dir.output}/summary/csv`.

### Draw the RD-Curve

```shell
python cc-30-export-figure.py
```

You can check the RD-Curves in `${dir.output}/summary/figure`.

## Details of Design

This appendix is for the people who **wants to check** the intermediate output of `Task`s.

### Task Based Structure

The **basic unit of** LVC-CC is `Task`. We compose multiple `Task`s into a forest (a.k.a list of trees) to conduct the crosscheck workflow.

Each `Task` is associated with an unique directory under `${dir.output}/tasks`. The name of the directory **involves all crucial informations** of all upstream `Task`s.

The naming rule of the `Task` directory:

- `copy-Fujita2-f1-c5d6` - copy: this is a `CopyTask` (copy a slice from the raw sequence) / Fujita2: sequence name / f1: only run 1 frame / c5d6: the auto-generated hash to prevent duplicate names
- `codec-Fujita2-f1-anchor-QP54-ec1c` - codec: this is a `CodecTask` (VVC Codec) / anchor: the task chain involves VVC codec but excludes any pre/post processing tools (e.g. MCA) / QP54: the codec QP is 54
- `convert40-Fujita2-f1-anchor-QP54-8b36` - convert: this is a `Convert40Task` (convert the lenslet into multi-view using `RLC40`)
- `convert40-Fujita2-f1-base-19eb` - base: the task chain excludes VVC codec and it is the base reference of the multi-view PSNR computation

Each output yuv file uses the same naming rule as the `Task` directory.

### Onion-like Configs

You can update the global configuration by `update_config("path/to/config.toml")`. The non-dictionary fields (e.g. `str`, `int`) will be overwrited, while the dictionary-like fields (e.g. `dict`, `OrderedDict`) will be `update`d with the new value. With this design, users can leave the constant per-device configurations in `base.toml` and only overwrite the frequently changing part by sequentially calling `update_config("freq_changing.toml")` and `update_config("even_more_freq_changing.toml")` for different purpose.

As a recommendation, we always define the following fields in `base.toml`:

```toml
# base.toml
[dir]
input = "/dataset/input"

[app]
encoder = "EncoderAppStatic"
processor = "MCA"
convertor = "RLC40"

[anchorQP]  # Following CTC
Boxer-IrishMan-Gladiator2 = [40, 44, 48, 52]
Boys2 = [36, 40, 44, 48]
HandTools = [41, 46, 50, 54]
Matryoshka = [40, 44, 48, 52]
MiniGarden2 = [40, 46, 50, 54]
Motherboard2 = [39, 42, 46, 50]
Fujita2 = [36, 40, 44, 48]
Origami = [36, 40, 44, 48]
TempleBoatGiantR32 = [40, 44, 48, 52]
```

And the mutable fields define in something like `250318-dbg.toml`:

```toml
# 250318-dbg.toml
frames = 1
views = 1

seqs = [
    # "Boxer-IrishMan-Gladiator2",
    # "Boys2",
    # "HandTools",
    # "Matryoshka",
    # "MiniGarden2",
    # "Motherboard2",
    # "Fujita2",
    # "Origami",
    "TempleBoatGiantR32",
]

[dir]
output = "/dataset/250318-dbg"
```
