## 简介

本项目用于LVC相关的crosscheck

## 安装依赖项

以下为我们目前使用的Dockerfile指令，仅供参考

```Dockerfile
FROM silkeh/clang:19 AS builder

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources
RUN apt update && \
    apt install -y --no-install-recommends ca-certificates git && \
    apt clean && \
    rm -r /etc/apt/sources.list.d

# VTM
ADD VVCSoftware_VTM-VTM-11.0.tar.bz2 ./
RUN cd VVCSoftware_VTM-VTM-11.0 && \
    find . -type f -exec sed -i 's/-Werror//g' {} + && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --config Release --parallel $($(nproc)-1) --target EncoderApp && \
    cmake --install build

# OpenCV
ADD opencv-4.10.0.tar.xz ./
RUN cd opencv-4.10.0 && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_LIST="imgproc" -DBUILD_SHARED_LIBS=OFF -DCV_TRACE=OFF -DCPU_BASELINE=AVX2 -DCPU_DISPATCH=AVX2 -DOPENCV_ENABLE_ALLOCATOR_STATS=OFF -DWITH_ADE=OFF -DWITH_DSHOW=OFF -DWITH_FFMPEG=OFF -DWITH_IMGCODEC_HDR=OFF -DWITH_IMGCODEC_PFM=OFF -DWITH_IMGCODEC_PXM=OFF -DWITH_IMGCODEC_SUNRASTER=OFF -DWITH_IPP=OFF -DWITH_ITT=OFF -DWITH_JASPER=OFF -DWITH_JPEG=OFF -DWITH_LAPACK=OFF -DWITH_OPENCL=OFF -DWITH_OPENEXR=OFF -DWITH_OPENJPEG=OFF -DWITH_PNG=OFF -DWITH_PROTOBUF=OFF -DWITH_TIFF=OFF -DWITH_WEBP=OFF && \
    make -C build -j$($(nproc)-1) && \
    make -C build install

# argparse
ADD argparse-3.1.tar.xz ./

# TLCT
RUN git clone --depth 1 https://github.com/lumina37/TLCT.git && \
    cd TLCT && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DTLCT_ENABLE_LTO=ON -DTLCT_HEADER_ONLY=ON -DTLCT_ARGPARSE_PATH=/argparse-3.1 && \
    cmake --build build --config Release --parallel $($(nproc)-1) --target tlct-bin

# MCA
RUN git clone --depth 1 https://github.com/lumina37/MCA.git && \
    cd MCA && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DMCA_ENABLE_LTO=ON -DTLCT_HEADER_ONLY=ON -DMCA_TLCT_PATH=/TLCT -DMCA_ARGPARSE_PATH=/argparse-3.1 && \
    cmake --build build --config Release --parallel $($(nproc)-1) --target mca-bin

# LVC-CC
RUN mkdir LVC-CC-Wrap && \
    cd LVC-CC-Wrap && \
    git clone --depth 1 https://github.com/lumina37/LVC-CC.git && \
    cd LVC-CC


FROM python:3.13-alpine AS prod

COPY --from=builder VVCSoftware_VTM-VTM-11.0/bin/EncoderAppStatic /usr/bin
COPY --from=builder TLCT/build/src/bin/tlct /usr/bin
COPY --from=builder MCA/build/src/bin/mca /usr/bin
COPY --from=builder LVC-CC-Wrap ./

RUN cd LVC-CC && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -U pip && \
    pip install .

WORKDIR /LVC-CC
CMD ["sh"]
```

## 运行脚本

### 配置文件`config.toml`

在当前目录下新建`config.toml`文件，并参考下面的注释填充`config.toml`中对应字段的内容

```toml
frames = 30  # 跑30帧
views = 5    # 跑5x5的视角

[cases]
vtm_types = ["AI", "RA"]  # 填VTM编码模式，填什么跑什么
seqs = ["Boys", "ExampleSeq"]  # 填序列名称，填什么跑什么

[path]
input = "/path/to/input"  # 修改该路径字段以指向input文件夹。input文件夹下应有下载解压后的yuv文件
output = "/path/to/output"  # 输出位置，随便设

[app]
encoder = "/path/to/EncoderAppStatic"  # 指向VTM-11.0的编码器EncoderApp
processor = "/path/to/mca"  # 指向预处理和逆处理工具的可执行文件
convertor = "/path/to/tlct"  # 指向多视角转换工具的可执行文件

[QP.anchor]
"Boys" = [48, 52]  # 序列名以及对应的需要跑的QP
"ExampleSeq" = [42, 44]  # 填什么跑什么，目前需要升序排序
```

### 配置input文件夹

在任意位置创建一个input文件夹，并将yuv转移进input文件夹

移入yuv后，input文件夹的目录结构应符合`${input}/${sequence_name}/xxx.yuv`的形式

例如：`/path/to/input/Boys/Boys_4080x3068_30fps_8bit.yuv`

yuv的文件名可随意设置

### 启动大全套渲染（含编解码与多视角转换）

**执行前请确保output文件夹有几个TB的空闲空间**

```shell
python cc-00-convert-anchor.py
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

以任务文件夹名`compose-Boys-f1-anchor-RA-QP52-8f7e`为例，`compose`是当前任务的类型，`Boys`为测试序列名，`f1`表明帧数量为1，`anchor`表明该任务链路仅包含VTM而不包含额外的编码工具（如MCA等），`RA`表明VVC编码使用random_access相关预设，`QP48`表明编码QP为48，`8f7e`为避免名称重复的hash。

各个yuv也使用了和目标文件夹相同的命名规则。
