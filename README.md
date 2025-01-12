# LVC-CC

This project is designed for crosscheck of the MPEG WG/04 Lenslet Video Coding.

## Prerequisites

### Setup Python Env

Run `pip install .`

Besides, LVC-CC also supports `uv sync` via [`uv`](https://docs.astral.sh/uv/).

### Build the Executables

The comments in the following `config.toml` guide you download the source code and build the binaries.

## Configure the Workflow Through `config.toml`

Create a `config.toml` in the project directory. Then follow the comment after each field to configure the workflow.

```toml
frames = 30  # Run 30 frames
views = 5    # Generate 5x5 views

[cases]
vtm_types = ["AI", "RA"]  # Only run the type you specified here
seqs = ["Boys", "OiOiOi"]  # Only run the sequences you specified here

[dir]
input = "/path/to/input"  # We should have yuv files inside this input directory
output = "/path/to/output"  # Anywhere you like

[app]
# Download the binary of [ffmpeg-7.0.2](https://johnvansickle.com/ffmpeg)
ffmpeg = "/path/to/ffmpeg"
# Download the source code of [VTM-11.0](https://vcgit.hhi.fraunhofer.de/jvet/VVCSoftware_VTM/-/tree/VTM-11.0)
# And build the CMake target `EncoderApp`
encoder = "/path/to/EncoderAppStatic"
# Download the source code of [RLC-4.0](WIP)
# And build the CMake target `RLC40`
convertor = "/path/to/tlct"

[QP.anchor]
Boys = [48, 52]  # Mapping from sequence name to the QPs you wanna run
Girls = [42, 44]  # Only run the QPs you specified here
OiOiOi = [42, 44]  # Please place the QPs in ascending order (e.g. 1,2,3,4...)
```

### Configure the `input` Directory

Create an `input` directory at anywhere you like and **put the yuv files into** it.

Once the yuv files are ready, the structure of the `input` directory **should be something like** `${dir.input}/${sequence_name}/as_you_like.yuv`.

e.g. `/path/to/input/Boys/Boys_4080x3068_30fps_8bit.yuv` or `/path/to/input/Fujita/src.yuv`

The file name of the yuv files can be anything you like. But the name of the parent directory **should be the same as** the sequence name!

### Launch the Workflow

Please make sure the `output` directory **is sufficient for** several TeraBytes of data.

```shell
python cc-00-convert-anchor.py
```

### Compute PSNR

```shell
python cc-10-compute.py
```

You can check the draft output in `${dir.output}/summary/tasks`.

### Export to CSV

```shell
python cc-20-export-csv-anchor.py
```

You can check the information of Bitrate and PSNR in the output csv files in `${dir.output}/summary/csv`.

### Draw the RD-Curve

```shell
python cc-30-figure-anchor.py
```

You can check the RD-Curve figures in `${dir.output}/summary/figure`.

## Details of Design

This appendix is for the people who **wants to check** the intermediate output of any `Task`.

The **basic unit of** LVC-CC is `Task`. We compose multiple `Task`s into a forest (a.k.a list of trees) to conduct the crosscheck workflow.

Each `Task` has its own directory under `${dir.output}/tasks`. The name of the directory **involves all crucial informations** of all upstream `Task`s.

Some example of the naming rule of the `Task` directory:

- `copy-Boys-f1-58ea` - copy: copy a slice from the raw sequence / Boys: sequence name / f1: only run 1 frame / 58ea: the auto-generated hash to prevent duplicate name
- `codec-Boys-f1-anchor-RA-QP52-9014` - codec: do VVC codec / anchor: the task chain involves VVC codec but excludes any pre/post process tool (e.g. MCA) / RA: VTM is using the Random Access preset / QP52: the codec QP is 52
- `convert-Boys-f1-anchor-RA-QP52-c637` - convert: convert the lenslet to multi-view
- `convert-Boys-f1-base-2444` - base: the task chain excludes VVC codec and it is the base reference of the multi-view PSNR computation

Each output yuv file uses the same naming rule as the `Task` directory.
