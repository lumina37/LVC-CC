# LVC-CC

This project is designed for crosscheck of the MPEG WG/04 Lenslet Video Coding.

## Prerequisites

### Setup Python Env

```shell
pip install .
```

### Build the Executables

Follow the comments in the `config.toml` to download or build binaries.

### Setup `config.toml`

Create a `config.toml` in the project directory. Then follow the comment after each field to configure the workflow.

```toml
frames = 30  # Run 30 frames
views = 5    # Generate 5x5 views

seqs = ["Boys2", "OiOiOi"]  # Specify which sequence to run

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

[anchorQP]         # Specifies QPs for anchor generation
Boys2 = [48, 52]   # Mapping from sequence name to the QPs you wanna run
OiOiOi = [42, 44]  # The QPs will be auto-sorted into ascending order

[proc.QP]          # Specifies QPs for pre/postproc
Boys2 = [44, 48]
OiOiOi = [39, 42]

[proc.any_name]    # Extension for pre/postproc with any content you like
example0 = 1
example1 = 0
```

### About the `input` Directory

Please **put the lenslet yuv files** into this directory.

Once the lenslet yuv files are ready, the structure of the `input` directory **should be something like** `${dir.input}/${sequence_name}/as_you_like.yuv`.

e.g. `/path/to/input/Boys2/Boys2_3976x2956_30fps_8bit.yuv` or `/path/to/input/Fujita/src.yuv`

The file name of the yuv files can be anything you like. But make sure that the name of the parent directory **is identical to** the sequence name!

### Launch the Workflow

Please make sure the `output` directory **is sufficient for** several **T**era**B**ytes of data.

```shell
python cc-00-convert-anchor.py
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
python cc-30-figure-anchor.py
```

You can check the RD-Curves in `${dir.output}/summary/figure`.

## Details of Design

This appendix is for the people who **wants to check** the intermediate output of any `Task`.

The **basic unit of** LVC-CC is `Task`. We compose multiple `Task`s into a forest (a.k.a list of trees) to conduct the crosscheck workflow.

Each `Task` is associated with an unique directory under `${dir.output}/tasks`. The name of the directory **involves all crucial informations** of all upstream `Task`s.

The naming rule of the `Task` directory:

- `copy-Boys2-f1-58ea` - copy: this is a `CopyTask` (copy a slice from the raw sequence) / Boys2: sequence name / f1: only run 1 frame / 58ea: the auto-generated hash to prevent duplicate names
- `codec-Boys2-f1-anchor-RA-QP52-9014` - codec: this is a `CodecTask` (VVC Codec) / anchor: the task chain involves VVC codec but excludes any pre/post processing tools (e.g. MCA) / RA: VTM is using the Random Access preset / QP52: the codec QP is 52
- `convert40-Boys2-f1-anchor-RA-QP52-c637` - convert: this is a `Convert40Task` (convert the lenslet into multi-view using `RLC40`)
- `convert40-Boys2-f1-base-2444` - base: the task chain excludes VVC codec and it is the base reference of the multi-view PSNR computation

Each output yuv file uses the same naming rule as the `Task` directory.
