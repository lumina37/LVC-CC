## 简介

本项目用于LVC相关的crosscheck

## 安装依赖项

### VTM、RLC、MCA所需的C++环境依赖

1. CMake>=3.15
2. gcc或clang编译工具链，需支持C++20的concepts特性，gcc12实测够用，gcc10应该够用
3. OpenCV>=4.9，必需模块包括imgcodecs、imgproc，还需要额外编译[opencv-contrib](https://github.com/opencv/opencv_contrib)中的quality模块。另，由于SSIM计算使用了大量小Mat运算，推荐关闭OpenCL（-DWITH_OPENCL=OFF）以加快RLC的速度

以下为我们目前使用的Dockerfile指令，仅供参考

```Dockerfile
# OpenCV
ADD opencv-4.10.0.tar.gz opencv_contrib-4.10.0.tar.gz .
RUN NPROC=$(nproc=`cat /proc/cpuinfo | grep processor | grep -v processors | wc -l`; if [ $nproc -gt 24 ]; then nproc=`expr 24 + $nproc / 10`; fi; echo $nproc); \
    cmake -S opencv-4.10.0 -B opencv-4.10.0/build -DBUILD_LIST="imgcodecs,imgproc,quality" -DBUILD_SHARED_LIBS=OFF -DCV_TRACE=OFF -DENABLE_PRECOMPILED_HEADERS=OFF -DCPU_BASELINE=AVX2 -DCPU_DISPATCH=AVX2 -DBUILD_OpenCV_apps=OFF -DWITH_ADE=OFF -DWITH_DSHOW=OFF -DWITH_FFMPEG=OFF -DWITH_FLATBUFFERS=OFF -DWITH_GSTREAMER=OFF -DWITH_IMGCODEC_HDR=OFF -DWITH_IMGCODEC_PFM=OFF -DWITH_IMGCODEC_PXM=OFF -DWITH_IMGCODEC_SUNRASTER=OFF -DWITH_IPP=OFF -DWITH_JASPER=OFF -DWITH_JPEG=OFF -DWITH_LAPACK=OFF -DWITH_MSMF=OFF -DWITH_MSMF_DXVA=OFF -DWITH_OPENCL=OFF -DWITH_OPENEXR=OFF -DWITH_OPENJPEG=OFF -DWITH_PROTOBUF=OFF -DWITH_VTK=OFF -DWITH_WEBP=OFF -DWITH_TIFF=OFF -DOPENCV_EXTRA_MODULES_PATH="opencv_contrib-4.10.0/modules" && \
    make -C opencv-4.10.0/build -j$NPROC && \
    make -C opencv-4.10.0/build install
```

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

### 编译RLC3.1

以下命令行将解压RLC3.1，进入工程文件夹并编译目标

```
unzip rlc-3.1.zip
cmake -S rlc-3.1 -B rlc-3.1/build
cmake --build rlc-3.1/build --config Release --target RLC31
```

编译完成后，可在`rlc-3.1/build/src/bin/...`下找到可执行文件`RLC31`

## 运行脚本

### 配置文件`config.toml`

在当前目录下新建`config.toml`文件，并参考下面的注释填充`config.toml`中对应字段的内容

```toml
frames = 30  # 跑几帧

[cases]
vtm_types = ["RA"]  # 填VTM编码模式，填什么跑什么
seqs = ["Matryoshka", "ExampleSeq"]  # 填序列名称，填什么跑什么

[path]
input = "/path/to/input"  # 修改该路径字段以指向input文件夹。input文件夹下应有下载解压后的yuv文件
output = "/path/to/output"  # 输出位置，随便设

[app]
ffmpeg = "ffmpeg"  # 指向ffmpeg的可执行文件ffmpeg
encoder = "/path/to/EncoderApp"  # 指向VTM-11.0的编码器EncoderApp
rlc = "/path/to/RLC31"  # 指向RLC3.1的可执行文件RLC31

[QP.anchor]
"Matryoshka" = [48, 52]  # 序列名以及对应的需要跑的QP
"ExampleSeq" = [42, 44]  # 填什么跑什么，目前需要升序排序
```

### 配置input文件夹

在任意位置创建一个input文件夹，并将yuv转移进input文件夹

移入yuv后，input文件夹的目录结构应符合`${input}/${sequence_name}/xxx.yuv`的形式

例如：`/path/to/input/Matryoshka/Matryoshka_4080x3068_30fps_8bit.yuv`

yuv的文件名可随意设置

### 启动大全套渲染（含编解码与多视角转换）

**执行前请确保output文件夹有4TB以上的空闲空间**

```shell
python cc-00-render-anchor.py
```

### 计算PSNR指标

```shell
python cc-10-compute.py
```

指标会输出到`${output}/summary/tasks`下

### 导出csv

```shell
python cc-20-export-csv-anchor.py
```

包含Bitrate和PSNR的csv会输出到`${output}/summary/csv`下

### 绘制RD-Curve

```shell
python cc-30-figure-anchor.py
```

RD-Curve会输出到`${output}/summary/figure`下

### 输出格式

LVC-CC是一套以任务（`Task`）为单元的crosscheck框架，通过多个`Task`的串联来组织编码测试。

每个`Task`都有一个目标文件夹。这个目标文件夹位于`${output}/tasks`文件夹下。目标文件夹的名称包含了该任务链路上所有前置任务的重点信息。

以任务文件夹名`compose-Matryoshka-f1-anchor-RA-QP52-8f7e`为例，`compose`是当前任务的类型，`Matryoshka`为测试序列名，`f1`表明帧数量为1，`anchor`表明该任务链路仅包含VTM而不包含额外的编码工具（如MCA等），`RA`表明VVC编码使用random_access相关预设，`QP48`表明编码QP为48，`8f7e`为避免名称重复的hash。

各个yuv也使用了和目标文件夹相同的命名规则。
