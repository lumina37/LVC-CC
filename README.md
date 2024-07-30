## 简介

本项目用于LVC相关的crosscheck

## 安装依赖项

### VTM、RLC、MCA所需的C++环境依赖

1. CMake>=3.15
2. gcc或clang编译工具链，需支持C++20的concepts特性，gcc12实测够用，gcc10应该够用
3. OpenCV>=4.0，必需模块包括imgcodecs、imgproc、highgui，还需要额外编译[opencv-contrib](https://github.com/opencv/opencv_contrib)中的quality模块。另，由于SSIM计算使用了大量小Mat运算，推荐关闭OpenCL（-DWITH_OPENCL=OFF）以加快RLC的速度

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
cd rlc-3.1
cmake -S . -B ./build
cmake --build ./build --config Release --target RLC31
```

编译完成后，可在`./build/src/bin/...`下找到可执行文件`RLC31`

## 运行脚本

### 修改配置文件`config.toml`

参考下面的注释修改`config.toml`中对应字段的内容

```toml
[path]
input = "/path/to/input"  # 修改该路径字段以指向input文件夹。input文件夹下应有下载解压后的yuv文件
output = "/path/to/output"  # 任意指定输出位置

...

[app]
ffmpeg = "ffmpeg"  # 指向ffmpeg的可执行文件ffmpeg
encoder = "/path/to/EncoderApp"  # 指向VTM-11.0的编码器EncoderApp
rlc = "/path/to/RLC31"  # 指向RLC3.1的可执行文件RLC31
```

### 将yuv复制到input文件夹

input文件夹的目录结构应符合`${input}/${sequence_name}/xxx.yuv`的形式

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
