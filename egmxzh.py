import subprocess
import os
import sys
from pathlib import Path
import glob
import folder_paths

class EGSVDloraZH:
    def __init__(self):
        pass

    @classmethod
    def get_lora_files(cls):
        try:
            lora_files = folder_paths.get_filename_list("loras")
            
            if not lora_files:
                return ["LoRA file not found"]
            
            return lora_files
        except Exception as e:
            print(f"Error obtaining LoRA file list: {str(e)}")
            return ["Failed to retrieve LoRA file"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "quant_model_type": (["svdq-int4-flux.1-dev", 
                                      "svdq-int4-flux.1-canny-dev",
                                      "svdq-int4-flux.1-depth-dev", 
                                      "svdq-int4-flux.1-fill-dev",
                                      "svdq-int4-flux.1-schnell",
                                      "svdq-fp4-flux.1-dev",
                                      "svdq-fp4-flux.1-schnell"], {
                    "default": "svdq-int4-flux.1-dev"
                }),
                "lora_path": (cls.get_lora_files(),),
                "output_root": ("STRING", {
                    "default": "models/loras/EGSVQZH",
                    "multiline": False
                }),
                "lora_name": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
            "optional": {
                "lora_format": (["auto", "diffusers", "comfyui", "xlab"], {
                    "default": "auto"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "convert_lora"
    CATEGORY = "2🐕/SVDLoRA"

    def convert_lora(self, quant_model_type, lora_path, output_root, lora_name, lora_format="auto"):
        try:
            os.makedirs(output_root, exist_ok=True)
            quant_path = f"models/diffusion_models/{quant_model_type}/transformer_blocks.safetensors"
            full_quant_path = os.path.join(folder_paths.base_path, quant_path)
            if not os.path.exists(full_quant_path):
                quant_path = f"mit-han-lab/{quant_model_type}/transformer_blocks.safetensors"
            
            full_lora_path = folder_paths.get_full_path("loras", lora_path)
            if full_lora_path is None:
                error_msg = f"LoRA file not found: {lora_path}"
                print(error_msg)
                return (error_msg,)
            print(f"Quantitative model type: {quant_model_type}")
            print(f"Quantitative model path: {quant_path}")
            print(f"LoRA path before conversion: {full_lora_path}")
            if not lora_name:
                base_name = os.path.splitext(os.path.basename(lora_path))[0]
                lora_name = f"{quant_model_type}-{base_name}"
            output_path = os.path.join(output_root, f"{lora_name}.safetensors")
            print(f"Converted model path: {output_path}")
            python = sys.executable
            cmd = [
                python, "-m", "nunchaku.lora.flux.convert",
                "--quant-path", quant_path,
                "--lora-path", full_lora_path,
                "--output-root", output_root,
                "--lora-name", lora_name,
                "--lora-format", lora_format
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            success_msg = f"Conversion successful！\nquantitative model: {quant_model_type}\nsource file: {full_lora_path}\ntarget file: {output_path}"
            print(success_msg)
            return_info = f"✅ Conversion successful\nquantitative model: {quant_model_type}\nsource file: {lora_path}\ntarget file: {output_path}"
            return (return_info,)
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ switch views\nquantitative model: {quant_model_type}\nsource file: {lora_path}\nerror message: {e.stderr}"
            print(f"switch views: {e.stderr}")
            return (error_msg,)
        except Exception as e:
            error_msg = f"❌ An error occurred\nquantitative model: {quant_model_type}\nsource file: {lora_path}\nerror message: {str(e)}"
            print(f"An error occurred: {str(e)}")
            return (error_msg,)

NODE_CLASS_MAPPINGS = {
    "EGSVDloraZH": EGSVDloraZH
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EGSVDloraZH": "2🐕SVDLoRAZHBC"
}