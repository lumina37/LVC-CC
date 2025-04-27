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

e.g. `/path/to/input/Boys2/Boys2_3976x2956_30fps_8bit.yuv` or `/path/to/input/Origami/src.yuv`

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

### Task

The **basic unit of** LVC-CC is `Task`. Each `Task` represents a signle operation, e.g. the VVC codec or the multi-view conversion.

### Task Based Pipeline

We compose multiple `Task`s into a **pipeline**. Then compose several **pipeline**s into a **forest** (a.k.a list of trees) to conduct the overall crosscheck.

As for now, there are three acknowledged **pipeline**s:

1. **base**: copy->convert40. Straight-forward multi-view conversion. Provides the **base** for PSNR computation.
2. **anchor**: copy->codec->convert40. Pipeline appends with VVC codec. Provides the **anchor** to estimate the performance of pre/postprocess tools.
3. **proc**: copy->preproc->codec->postproc->convert40. Pipeline appends with pre/postprocess procedure.

### Naming Rules and Directory Structure

Each `Task` is associated with an unique directory under `${dir.output}/tasks`. The name of the directory **involves all crucial informations** of all upstream `Task`s.

There are six pre-defined `Task`s:

#### copy

Copy a certain range of the source yuv file to ensure a uniform input.

Directory name `copy-Boys2-f300-e979` can be spilt into:

- **copy**: This is a `CopyTask`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **e979**: Hash for deduplication.

Directory structure:

```
./copy-Boys2-f300-e979
├── Boys2-f300-3976x2956.yuv  # copied yuv
└── task.json  # metadata
```

#### preproc

Preprocess with the MCA.

Directory name `preproc-Boys2-f300-proc-d45a` can be spilt into:

- **preproc**: This is a `PreprocTask`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **proc**: The pipeline is tagged by **proc** (both VVC and MCA).
- **d45a**: Hash for deduplication.

Directory structure:

```
./preproc-Boys2-f300-proc-d45a
├── Boys2-f300-proc-3250x2100.yuv  # preprocessed yuv
├── cfg  # configs required by the MCA
│   ├── calib.xml
│   └── codec.cfg
├── proc.log  # MCA log 
└── task.json  # metadata
```

#### codec

VVC codec.

For the **anchor** pipeline variant:

Directory name `codec-Boys2-f300-anchor-QP36-c445` can be spilt into:

- **codec**: This is a `CodecTask`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **anchor**: The pipeline is tagged by **anchor** (only VVC, no MCA).
- **QP36**: Encoded by QP=36.
- **c445**: Hash for deduplication.

Directory structure:

```
./codec-Boys2-f300-anchor-QP36-c445
├── Boys2-f300-anchor-QP36-3976x2956.yuv  # decoded yuv
├── Boys2-f300-anchor-QP36.bin  # encoded binary
├── Boys2-f300-anchor-QP36.log  # encoder log
├── cfg  # configs required by the VVC encoder
│   ├── seq.cfg
│   └── vtm.cfg
└── task.json  # metadata
```

**Notice that all the output files use the same naming rule as the task directory!!!**

For the **proc** pipeline variant:

Directory name `codec-Boys2-f300-proc-QP33-2776` can be spilt into:

- **codec**: This is a `CodecTask`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **proc**: The pipeline is tagged by **anchor** (only VVC, no MCA).
- **QP33**: Encoded by QP=33.
- **2776**: Hash for deduplication.

Directory structure: similiar to the **anchor** pipeline variant.

#### postproc

Postprocess with the MCA

Directory name `postproc-Boys2-f300-proc-QP33-3b24` can be spilt into:

- **postproc**: This is a `PostprocTask`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **proc**: The pipeline is tagged by **proc** (both VVC and MCA).
- **QP33**: The QP of the upstream `CodecTask` is 33.
- **3b24**: Hash for deduplication.

Directory structure:

```
./postproc-Boys2-f300-proc-QP33-3b24
├── Boys2-f300-proc-QP33-3976x2956.yuv  # postprocessed yuv
├── cfg  # configs required by the MCA
│   └── proc.log
└── task.json  # metadata
```

#### convert40

Convert lenslet yuv into multi-view yuv using the RLC4.0.

For the **base** pipeline variant:

Directory name `convert40-Boys2-f300-base-5982` can be spilt into:

- **convert40**: This is a `Convert40Task`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **base**: The pipeline is tagged by **base** (no VVC, no MCA).
- **5982**: Hash for deduplication.

Directory structure:

```
./convert40-Boys2-f300-base-5982
├── cfg  # configs required by the RLC40
│   ├── calib.xml
│   └── param.cfg
├── img  # temporary image input/output
│   ├── dst  # multi-view png output
│   │   ├── frame001  # each frame
│   │   │   ├── image_001.png  # each view
│   │   │   ├── ...
│   │   │   └── image_025.png
│   │   ├── ...
│   │   └── frame300
│   │       ├── image_001.png
│   │       ├── ...
│   │       └── image_025.png
│   └── src  # lenslet png input
│       ├── frame001.png  # each frame
│       ├── ...
│       └── frame300.png
├── task.json  # metadata
└── yuv  # multi-view yuv output
    ├── Boys2-f300-base-v000-1098x800.yuv  # each view
    ├── ...
    └── Boys2-f300-base-v024-1098x800.yuv
```

For the **anchor** pipeline variant:

Directory name `convert40-Boys2-f300-anchor-QP36-fc31` can be spilt into:

- **convert40**: This is a `Convert40Task`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **anchor**: The pipeline is tagged by **anchor** (only VVC, no MCA).
- **QP36**: The QP of the upstream `CodecTask` is 36.
- **fc31**: Hash for deduplication.

Directory structure: similiar to the **base** pipeline variant.

For the **proc** pipeline variant:

Directory name `convert40-Boys2-f300-proc-QP33-294f` can be spilt into:

- **convert40**: This is a `Convert40Task`.
- **Boys2**: The sequence name is Boys2.
- **f300**: The pipeline involves 300 frames.
- **proc**: The pipeline is tagged by **proc** (both VVC and MCA).
- **QP33**: The QP of the upstream `CodecTask` is 33.
- **294f**: Hash for deduplication.

Directory structure: similiar to the **base** pipeline variant.

#### posetrace

Generate posetrace video for subjective quality assessment.

TODO

### Onion-like Configs

You can update the global configuration by `update_config("path/to/config.toml")`. The non-dictionary fields (e.g. `str`, `int`, `list`) will be overwritten, while the dictionary-like fields (e.g. `dict`, `OrderedDict`) will be `update`d with the new value. By that design, users can store the invariant per-device configurations in `base.toml` and overwrite the frequently changing part by sequentially calling `update_config("freq_changing.toml")` and `update_config("even_more_freq_changing.toml")` for different purpose.

As a recommendation, we define the following fields in `base.toml`:

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

And the mutable fields define in something like `dbg-250318.toml`:

```toml
# dbg-250318.toml
frames = 1
views = 1

seqs = [  # Only enable 2 sequences
    # "Boxer-IrishMan-Gladiator2",
    "Boys2",
    # "HandTools",
    # "Matryoshka",
    # "MiniGarden2",
    # "Motherboard2",
    "Fujita2",
    # "Origami",
    # "TempleBoatGiantR32",
]

[dir]
output = "/dataset/250318-dbg"
```
