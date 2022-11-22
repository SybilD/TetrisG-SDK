# Project Title

An example for Tetris-SDK mapping algorithm.

## Description

### Title
Tetris-SDK: Efficient Convolution Layer Mapping with Adaptive Windows for Fast In Memory Computing

### Abstract
Shifted-and-Duplicated-Kernel (SDK) mapping is gaining popularity as it substantially accelerates convolution layers in Compute-In-Memory (CIM) architectures compared to conventional image-to-column (im2col) mapping. However, the state-of-the-art SDK algorithm, i.e., Variable-Window SDK (VW-SDK) lacks adaptability, leading to in-sufficient memory utilization and extra processing cycles. In this work, we propose Tetris-SDK, an enhanced strategy integrating a marginal-space mapping to increase CIM array utilization, an adjustable input channel partition to improve adaptation, and a square-inclined window slicing to decrease overall computing cycles. Compared with im2col, SDK and VM-SDK, Tetris-SDK speeds up a variety of CNN layers by up to $78.4\times$, $8\times$, and $1.3\times$, respectively.

## Getting Started

### Dependencies

* Python 3.x

### Installing

* Any IDE that can run Jupyter Notebook

### Executing program

* Download the file and open it in IDE
* Run cell by cell

```
cc_optimization_with_mo(image, kernel, ic, oc, ar, ac, pw_row, pw_col, pw_ic, pw_oc)
```


## Version History

* 0.2
    * Various bug fixes and optimizations
* 0.1
    * Initial Release
