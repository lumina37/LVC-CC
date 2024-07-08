## 简介

以下教程将执行大全套crosscheck并输出RD-Curve

## 安装依赖项

### VTM、RLC、MCA所需的C++环境依赖

1. CMake>=3.15
2. gcc或clang编译工具链，需支持C++20的concepts特性，gcc12实测够用，gcc10应该够用
3. OpenCV>=4.0，必需模块包括core、imgcodecs、imgproc、highgui，还需要额外编译[opencv-contrib](https://github.com/opencv/opencv_contrib)中的quality模块。另，由于SSIM计算使用了大量小Mat运算，推荐关闭OpenCL（-DWITH_OPENCL=OFF）以加快RLC的速度

### 该脚本所需的Python环境依赖

Python版本需大于等于3.10，推荐3.12

使用

```shell
pip install .
```

安装该脚本所需的Python环境依赖

### 编译VTM-11.0

项目链接：https://vcgit.hhi.fraunhofer.de/jvet/VVCSoftware_VTM/-/tree/VTM-11.0

参考官方文档编译`EncoderApp`

### 编译MCA

以下命令行将解压MCA，进入工程文件夹并编译目标

```
unzip MCA.zip
cd MCA
cmake -S . -B ./build
cmake --build ./build --config Release
```

编译完成后，可在`./build/src/bin/...`下找到可执行文件`mca-preproc`和`mca-postproc`

### 编译RLC3.0

以下命令行将解压RLC3.0，进入工程文件夹并编译目标

```
unzip rlc.zip
cd rlc/Program
cmake -S . -B ./build
cmake --build ./build --config Release
```

编译完成后，可在`./build/...`下找到可执行文件`RLC30`

## 运行脚本

### 修改配置文件`config.toml`

参考下面的注释修改`config.toml`中对应字段的内容

```toml
[path]
input = "D:/MPEG/MPEG144/dataset/input"
output = "E:/output"  # 修改该路径字段以指向解压出的output文件夹。output文件夹下应有包含中间yuv文件的playground文件夹

...

[app]
ffmpeg = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"  # 指向ffmpeg的可执行文件ffmpeg
encoder = "D:/MPEG/MPEG144/code/VVCSoftware_VTM/bin/ninja/msvc-19.37/x86_64/release/EncoderApp.exe"  # 指向VTM-11.0的编码器EncoderApp
preproc = "D:/MPEG/MPEG143/code/MCA/cmake-build-release/src/bin/mca-preproc.exe"  # 指向MCA预处理的可执行文件mca-preproc
postproc = "D:/MPEG/MPEG143/code/MCA/cmake-build-release/src/bin/mca-postproc.exe"  # 指向MCA逆处理的可执行文件mca-postproc
rlc = "D:/MPEG/MPEG146/code/rlc/Program/cmake-build-release/RLC30.exe"  # 指向RLC3.0的可执行文件RLC30
```

### 迁移先前的编码结果

上周我把QP点设错了，需要部分调整。ChessPieces序列我也搞错了（草台Orz）。需要以新上传的output.zip为准。

新output文件夹可直接合并进旧output文件夹。对于重名旧文件可跳过。

后续脚本会自动复用已完成的编码结果。

### 启动大全套渲染（含编解码、多视角转换、MCA等）

**执行前请确保output文件夹有4TB以上的空闲空间**

```shell
python crosscheck-0-render.py
```

### 计算PSNR指标

```shell
python crosscheck-1-compute.py
```

指标会输出到`${output}/summary/compute/*.json`中

### 绘制RD-Curve

```shell
python crosscheck-2-visualize.py
```

RD-Curve会输出到`${output}/summary/figs/*.svg`中
