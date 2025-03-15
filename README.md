# EGSVD LoRA 工具 / EGSVD LoRA Tools

[English](#english-version) | [中文](#中文版本)

## English Version

### Introduction
EGSVD LoRA Tools is a ComfyUI extension for converting and loading LoRA files with quantized SVD models. It provides two nodes that allow you to convert regular LoRAs to be compatible with quantized SVD models, and load them directly without pre-conversion.

### Features
- Convert standard LoRA files to SVDQ compatible format
- Real-time LoRA conversion and loading
- Support for multiple quantized model types
- Adjustable LoRA strength
- Support for different LoRA formats (ComfyUI, Diffusers, XLab)

### Installation
1. Make sure you have ComfyUI installed
2. Clone this repository into your ComfyUI custom_nodes directory:
   ```
   cd ComfyUI/custom_nodes
   git clone https://github.com/11dogzi/ComfyUI-ergouzi-SVDlora.git
   ```
3. Need to install first https://github.com/mit-han-lab/nunchaku And ensure that it can operate normally

### Usage

#### 2🐕SVDLoRAZHBC Node
This node converts a standard LoRA file to a format compatible with quantized SVD models and saves it to disk.

Parameters:
- `quant_model_type`: Type of quantized model
- `lora_path`: Path to source LoRA file
- `output_root`: Directory to save converted LoRA
- `lora_name`: Name for the converted LoRA file (optional)
- `lora_format`: Format of source LoRA file (auto, diffusers, comfyui, xlab)

#### 2🐕SVDLoRASSZH Node
This node performs real-time conversion and loading of LoRA files, without the need to convert and save in advance.

Parameters:
- `model`: Diffusion model to apply LoRA to
- `lora_name`: LoRA file to load
- `model_type`: Type of quantized model
- `lora_strength`: Intensity of LoRA effect
- `lora_format`: Format of source LoRA file (auto, comfyui, diffusers, xlab)

### Supported Model Types
- svdq-int4-flux.1-dev
- svdq-int4-flux.1-canny-dev
- svdq-int4-flux.1-depth-dev
- svdq-int4-flux.1-fill-dev
- svdq-int4-flux.1-schnell
- svdq-fp4-flux.1-dev
- svdq-fp4-flux.1-schnell

### Notes
- Make sure the quantized model is available in your ComfyUI models directory
- For best results, use LoRAs specifically trained for SVD models

---

## 中文版本

### 简介
EGSVD LoRA 工具是一个 ComfyUI 扩展，用于转换和加载与量化 SVD 模型兼容的 LoRA 文件。它提供了两个节点，允许您将常规 LoRA 转换为与量化 SVD 模型兼容的格式，并且无需预先转换即可直接加载它们。

### 特点
- 将标准 LoRA 文件转换为 SVDQ 兼容格式
- 实时 LoRA 转换和加载
- 支持多种量化模型类型
- 可调节的 LoRA 强度
- 支持不同的 LoRA 格式（ComfyUI、Diffusers、XLab）

### 安装
1. 确保已安装 ComfyUI
2. 将此仓库克隆到您的 ComfyUI custom_nodes 目录：
   ```
   cd ComfyUI/custom_nodes
   git clone https://github.com/11dogzi/ComfyUI-ergouzi-SVDlora.git
   ```
3. 需要先安装 https://github.com/mit-han-lab/nunchaku 并确保其能够正常运行

### 使用方法

#### 2🐕SVDLoRAZHBC 节点
此节点将标准 LoRA 文件转换为与量化 SVD 模型兼容的格式，并保存到磁盘。

参数：
- `quant_model_type`：量化模型类型
- `lora_path`：源 LoRA 文件路径
- `output_root`：保存转换后 LoRA 的目录
- `lora_name`：转换后 LoRA 文件的名称（可选）
- `lora_format`：源 LoRA 文件格式（auto、diffusers、comfyui、xlab）

#### 2🐕SVDLoRASSZH 节点
此节点执行 LoRA 文件的实时转换和加载，无需提前转换和保存。

参数：
- `model`：要应用 LoRA 的扩散模型
- `lora_name`：要加载的 LoRA 文件
- `model_type`：量化模型类型
- `lora_strength`：LoRA 效果强度
- `lora_format`：源 LoRA 文件格式（auto、comfyui、diffusers、xlab）

### 支持的模型类型
- svdq-int4-flux.1-dev
- svdq-int4-flux.1-canny-dev
- svdq-int4-flux.1-depth-dev
- svdq-int4-flux.1-fill-dev
- svdq-int4-flux.1-schnell
- svdq-fp4-flux.1-dev
- svdq-fp4-flux.1-schnell

### 注意事项
- 确保您的 ComfyUI 模型目录中有可用的量化模型
- 为获得最佳效果，请使用专门为 SVD 模型训练的 LoRA