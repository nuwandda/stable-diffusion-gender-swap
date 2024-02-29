import schemas as _schemas

import torch 
from diffusers import StableDiffusionImg2ImgPipeline
import os
# from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from utils import set_seed, age_and_gender
import numpy as np
from pkg_resources import parse_version


# Get the token from HuggingFace 
"""
Note: make sure .env exist and contains your token
"""
    
MODEL_PATH = os.getenv('MODEL_PATH')
if MODEL_PATH is None:
    MODEL_PATH = 'weights/realisticVisionV60B1_v20Novae.safetensors'
    

def create_pipeline(model_path):
    # Create the pipe 
    pipe = StableDiffusionImg2ImgPipeline.from_single_file(
        model_path, 
        revision="fp16", 
        torch_dtype=torch.float16
        )
    
    # pipe.load_lora_weights(pretrained_model_name_or_path_or_dict="weights/lora_disney.safetensors", adapter_name="disney")

    if torch.backends.mps.is_available():
        device = "mps"
    else: 
        device = "cuda" if torch.cuda.is_available() else "cpu"

    pipe.to(device)
    
    return pipe


pipe = create_pipeline(MODEL_PATH)


async def generate_image(imgPrompt: _schemas.ImageCreate) -> Image:
    generator = torch.Generator().manual_seed(set_seed()) if float(imgPrompt.seed) == -1 else torch.Generator().manual_seed(int(imgPrompt.seed))
    request_object_content = await imgPrompt.encoded_base_img.read()
    init_image = Image.open(BytesIO(request_object_content))
    aspect_ratio = init_image.width / init_image.height
    target_height = round(imgPrompt.img_width / aspect_ratio)
    
    # Resize the image
    if parse_version(Image.__version__) >= parse_version('9.5.0'):
        resized_image = init_image.resize((imgPrompt.img_width, target_height), Image.LANCZOS)
    else:
        resized_image = init_image.resize((imgPrompt.img_width, target_height), Image.ANTIALIAS)
    
    # Predict gender if necessary, then add it to the prompt
    if imgPrompt.current_gender == 'Undefined':
        gender_result, age_result = age_and_gender(np.array(resized_image))
    else:
        gender_result = imgPrompt.current_gender
        age_result = 20
    
    if gender_result == 'Multiple faces':
        return 'There should be single face in the image.'
    
    target_gender = 'female' if gender_result.lower() == 'male' else 'male'
    if age_result < 15:
        target_gender = 'girl' if gender_result.lower() == 'male' else 'boy'
    
    clothes = 'feminine' if gender_result.lower() == 'male' else 'masculine'

    final_prompt = """A realistic portrait of a {}, wearing {} clothes, rim lighting, 
    studio lighting, dslr, ultra quality, sharp focus, tack sharp, dof, 
    film grain, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, 
    high detailed skin, skin pores""".format(target_gender, clothes)
    negative_prompt = """nude, nsfw, disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w, nude, nsfw"""
    print('Final Prompt is: ', final_prompt)

    image: Image = pipe(final_prompt,
                                image=resized_image, strength=imgPrompt.strength,
                                negative_prompt=negative_prompt, 
                                guidance_scale=imgPrompt.guidance_scale, 
                                num_inference_steps=imgPrompt.num_inference_steps, 
                                generator = generator,
                                cross_attention_kwargs={"scale": imgPrompt.strength}
                                ).images[0]

    if not image.getbbox():
        image: Image = pipe(final_prompt,
                                    image=resized_image, strength=imgPrompt.strength + 0.1,
                                    negative_prompt=negative_prompt,
                                    guidance_scale=imgPrompt.guidance_scale, 
                                    num_inference_steps=imgPrompt.num_inference_steps, 
                                    generator = generator,
                                    cross_attention_kwargs={"scale": imgPrompt.strength}
                                    ).images[0]
    
    return image
        