import os
import tempfile
import time
from pathlib import Path
import folder_paths
from safetensors.torch import save_file
from nunchaku.lora.flux import comfyui2diffusers, convert_to_nunchaku_flux_lowrank_dict, detect_format, xlab2diffusers


class EGSVDloraSHZH:
    def __init__(self):
        self.cur_lora_name = "None"
        self.cur_model_type = ""
        self.temp_files = {}
        self.cache_dir = os.path.join(folder_paths.base_path, "temp", "svdlora_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def cleanup_old_cache(self):
        cache_files = []
        for f in os.listdir(self.cache_dir):
            if f.endswith('_converted.safetensors'):
                full_path = os.path.join(self.cache_dir, f)
                cache_files.append((os.path.getmtime(full_path), full_path))

        cache_files.sort(reverse=True)

        for _, file_path in cache_files[5:]:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete cache file: {file_path}, error: {str(e)}")

    def find_converted_lora(self, lora_path, key, save_to_lora_dir):
        try:
            lora_name, model_type = key.rsplit('_', 1)
            base_name = os.path.splitext(os.path.basename(lora_path))[0]
            lora_dir = os.path.dirname(lora_path)
            for file in os.listdir(lora_dir):
                try:
                    if (file.startswith(base_name) and 
                        model_type in file and 
                        file.endswith('_converted.safetensors')):
                        return os.path.join(lora_dir, file), "lora_dir"
                except UnicodeError:
                    continue
            if not save_to_lora_dir:
                converted_name = f"{base_name}_{model_type}_converted.safetensors"
                cache_path = os.path.join(self.cache_dir, converted_name)
                if os.path.exists(cache_path):
                    return cache_path, "cache"
            
        except Exception as e:
            print(f"Error while searching converted file: {str(e)}")
            
        return None, None

    @classmethod
    def INPUT_TYPES(cls):
        all_loras = folder_paths.get_filename_list("loras")
        filtered_loras = [
            lora for lora in all_loras 
            if not lora.endswith('_converted.safetensors')
        ]
        
        lora_name_list = [
            "None",
            *filtered_loras,
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
                "model_type": (base_model_types, {"default": "svdq-int4-flux.1-dev", "tooltip": "Select quantization model type"}),
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
                    {"default": "auto", "tooltip": "LoRA format, usually keep auto for automatic detection"},
                ),
                "save_to_lora_dir": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Whether to save the converted model to the LoRA directory"}
                ),
            }
        }

    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")
    FUNCTION = "convert_and_load_lora"
    TITLE = "Real time LoRA conversion loader"

    CATEGORY = "2🐕/SVDLoRA"
    DESCRIPTION = "Real time conversion and loading of LoRA, no need to convert and save in advance, suitable for SVDQ quantization models"

    def convert_and_load_lora(self, model, lora_name, model_type, lora_strength, lora_format="auto", save_to_lora_dir=False):
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
                
                key = f"{lora_name}_{model_type}"
                existing_path, location = self.find_converted_lora(lora_path, key, save_to_lora_dir)
                
                if existing_path:
                    temp_path = existing_path
                else:
                    if lora_format == "auto":
                        lora_format = detect_format(lora_path)
                        if lora_format == "svdquant":
                            lora_format = "diffusers"

                    base_model_path = f"models/diffusion_models/{model_type}/transformer_blocks.safetensors"
                    full_base_path = os.path.join(folder_paths.base_path, base_model_path)
                    
                    if not os.path.exists(full_base_path):
                        base_model_path = f"mit-han-lab/{model_type}/transformer_blocks.safetensors"

                    if lora_format == "comfyui":
                        input_lora = comfyui2diffusers(lora_path)
                    elif lora_format == "xlab":
                        input_lora = xlab2diffusers(lora_path)
                    elif lora_format == "diffusers":
                        input_lora = lora_path
                    else:
                        raise ValueError(f"Unsupported LoRA format: {lora_format}, supported formats: comfyui, diffusers, xlab")
                    state_dict = convert_to_nunchaku_flux_lowrank_dict(base_model_path, input_lora)
                    try:
                        base_name = os.path.splitext(os.path.basename(lora_name))[0]
                        converted_name = f"{base_name}_{model_type}_converted.safetensors"
                        
                        if save_to_lora_dir:
                            save_dir = os.path.dirname(lora_path)
                            temp_path = os.path.join(save_dir, converted_name)
                        else:
                            temp_path = os.path.join(self.cache_dir, converted_name)
                            self.cleanup_old_cache()
                        
                        temp_path = os.path.abspath(os.path.normpath(temp_path))
                        save_file(state_dict, temp_path)
                        
                        if not os.path.exists(temp_path):
                            raise Exception("Failed to save file")
                            
                    except Exception as e:
                        raise
                
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