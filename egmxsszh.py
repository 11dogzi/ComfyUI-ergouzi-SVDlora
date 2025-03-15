import os
import tempfile

import folder_paths
from safetensors.torch import save_file

from nunchaku.lora.flux import comfyui2diffusers, convert_to_nunchaku_flux_lowrank_dict, detect_format, xlab2diffusers


class EGSVDloraSHZH:
    def __init__(self):
        self.cur_lora_name = "None"
        self.cur_model_type = ""
        self.temp_files = {}

    @classmethod
    def INPUT_TYPES(cls):
        lora_name_list = [
            "None",
            *folder_paths.get_filename_list("loras"),
        ]

        base_model_types = [
            "svdq-int4-flux.1-dev", 
            "svdq-int4-flux.1-canny-dev",
            "svdq-int4-flux.1-depth-dev", 
            "svdq-int4-flux.1-fill-dev",
            "svdq-int4-flux.1-schnell",
            "svdq-fp4-flux.1-dev",
            "svdq-fp4-flux.1-schnell",
        ]

        return {
            "required": {
                "model": ("MODEL", {"tooltip": "Diffusion model, LoRA will be applied to this model"}),
                "lora_name": (lora_name_list, {"tooltip": "Select the LoRA file to load"}),
                "model_type": (base_model_types, {"default": "svdq-int4-flux.1-dev", "tooltip": "Select the type of quantitative model"}),
                "lora_strength": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -100.0,
                        "max": 100.0,
                        "step": 0.01,
                        "tooltip": "LoRA intensity, can be negative",
                    },
                ),
            },
            "optional": {
                "lora_format": (
                    ["auto", "comfyui", "diffusers", "xlab"],
                    {"default": "auto", "tooltip": "LoRA format, usually maintained as auto auto auto detection"},
                ),
            }
        }

    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")
    FUNCTION = "convert_and_load_lora"
    TITLE = "Real time LoRA conversion loader"

    CATEGORY = "2🐕/SVDLoRA"
    DESCRIPTION = "Real time conversion and loading of LoRA, no need to convert and save in advance, suitable for SVDQ quantization models"

    def convert_and_load_lora(self, model, lora_name, model_type, lora_strength, lora_format="auto"):
        if lora_name == "None":
            model.model.diffusion_model.model.set_lora_strength(0)
            self.cur_lora_name = "None"
            return (model, "CLOSED LoRA")
        need_convert = (self.cur_lora_name != lora_name) or (self.cur_model_type != model_type)
        
        if need_convert:
            try:
                try:
                    lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
                except FileNotFoundError:
                    lora_path = lora_name
                if lora_format == "auto":
                    lora_format = detect_format(lora_path)
                base_model_path = f"models/diffusion_models/{model_type}/transformer_blocks.safetensors"
                full_base_path = os.path.join(folder_paths.base_path, base_model_path)
                
                if not os.path.exists(full_base_path):
                    base_model_path = f"mit-han-lab/{model_type}/transformer_blocks.safetensors"
                print(f"Converting LoRA: {lora_name}")
                print(f"Quantitative model type: {model_type}")
                print(f"Quantitative model path: {base_model_path}")
                if lora_format == "comfyui":
                    input_lora = comfyui2diffusers(lora_path)
                elif lora_format == "xlab":
                    input_lora = xlab2diffusers(lora_path)
                elif lora_format == "diffusers":
                    input_lora = lora_path
                else:
                    raise ValueError(f"Unsupported LoRA format: {lora_format}")
                state_dict = convert_to_nunchaku_flux_lowrank_dict(base_model_path, input_lora)
                key = f"{lora_name}_{model_type}"
                if key in self.temp_files and os.path.exists(self.temp_files[key]):
                    temp_path = self.temp_files[key]
                else:
                    temp_file = tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False)
                    temp_path = temp_file.name
                    self.temp_files[key] = temp_path
                    temp_file.close()
                    save_file(state_dict, temp_path)
                model.model.diffusion_model.model.update_lora_params(temp_path)
                self.cur_lora_name = lora_name
                self.cur_model_type = model_type
                model.model.diffusion_model.model.set_lora_strength(lora_strength)
                
                info = f"✅ Real time conversion and successful loading\nLoRA: {lora_name}\nModel type: {model_type}\nstrength: {lora_strength}"
                return (model, info)
                
            except Exception as e:
                error_info = f"❌ Conversion or loading failed\nLoRA: {lora_name}\nModel type: {model_type}\nerror: {str(e)}"
                print(error_info)
                model.model.diffusion_model.model.set_lora_strength(0)
                return (model, error_info)
        else:
            model.model.diffusion_model.model.set_lora_strength(lora_strength)
            info = f"✅ LoRA intensity has been adjusted\nLoRA: {lora_name}\nModel type: {model_type}\nstrength: {lora_strength}"
            return (model, info)
NODE_CLASS_MAPPINGS = {
    "EGSVDloraSHZH": EGSVDloraSHZH
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EGSVDloraSHZH": "2🐕SVDLoRASSZH"
} 