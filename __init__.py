"""
ComfyUI-QwenClothingSelector

Custom nodes for Qwen-Image-Edit clothing/outfit edits in ComfyUI.

Build clean Qwen-Image-Edit prompts via toggles and presets — outfit swaps,
costume changes, fashion experiments — with identity-preservation guards
(face, hair, skin tone) baked into every output.

Output is a STRING that feeds into TextEncodeQwenImageEditPlus.

Pro pack with adult-content presets available separately — see README.

Copyright (c) 2026 Joe Fred Umlas
MIT License
"""

# Identity preservation block reused across nodes
IDENTITY_BLOCK = """

CRITICAL IDENTITY PRESERVATION (DO NOT CHANGE THESE):
- PRESERVE THE FACE EXACTLY AS-IS - same eyes, nose, mouth, expression
- PRESERVE HAIR EXACTLY AS-IS - same hairstyle, hair color, hair length, hair texture
- PRESERVE HEAD AND NECK EXACTLY AS-IS
- MATCH SKIN COLOR AND TONE EXACTLY from the original image
- DO NOT modify hair in any way

HD quality, detailed skin texture, photorealistic, no plastic skin, natural body shape, seamless blend."""


def _skin_block(skin_quality: str) -> str:
    if skin_quality == "Ultra Realistic":
        return "\n\nSkin: detailed pores, natural imperfections, subsurface scattering, no plastic look, moles, freckles."
    if skin_quality == "Realistic":
        return "\n\nSkin: natural texture, realistic tones, no airbrushing."
    return ""


# ==========================================================================
# QwenClothingToggles — checkbox builder for clothing category swaps
# ==========================================================================
class QwenClothingToggles:
    """Checkbox toggles for swapping/changing clothing categories."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "change_top": ("BOOLEAN", {"default": True, "label_on": "CHANGE TOP", "label_off": "keep top"}),
                "change_bottom": ("BOOLEAN", {"default": True, "label_on": "CHANGE BOTTOM", "label_off": "keep bottom"}),
                "change_shoes": ("BOOLEAN", {"default": False, "label_on": "CHANGE SHOES", "label_off": "keep shoes"}),
            },
            "optional": {
                "change_accessories": ("BOOLEAN", {"default": False, "label_on": "CHANGE ACCESSORIES", "label_off": "keep accessories"}),
                "target_style": (["Casual", "Formal", "Business", "Sports", "Vintage", "Streetwear", "Beach"], {"default": "Casual"}),
                "skin_quality": (["Ultra Realistic", "Realistic", "Fast"], {"default": "Realistic"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build_prompt"
    CATEGORY = "Qwen/ClothingEdit"

    STYLE_DESCRIPTIONS = {
        "Casual": "casual everyday clothing — t-shirt, jeans, comfortable",
        "Formal": "formal evening wear — elegant dress or suit, dressy",
        "Business": "business professional — blazer, dress shirt, slacks or pencil skirt",
        "Sports": "athletic wear — sports bra/tank top, leggings or shorts, athletic shoes",
        "Vintage": "vintage clothing — period-appropriate retro outfit",
        "Streetwear": "modern streetwear — hoodie, cargo pants, sneakers, urban style",
        "Beach": "beachwear — swimsuit or board shorts, summer vibe",
    }

    def build_prompt(self, change_top, change_bottom, change_shoes,
                     change_accessories=False, target_style="Casual",
                     skin_quality="Realistic"):
        base = "editorial_edit: Picture 1 is the base image. "
        style_desc = self.STYLE_DESCRIPTIONS.get(target_style, "casual clothing")

        change_items = []
        if change_top:
            change_items.append("upper clothing (shirt, top, jacket)")
        if change_bottom:
            change_items.append("lower clothing (pants, skirt, shorts)")
        if change_shoes:
            change_items.append("shoes/footwear")
        if change_accessories:
            change_items.append("accessories (jewelry, glasses, watch, bag)")

        if not change_items:
            instruction = "Enhance the image quality without changing clothing."
        else:
            instruction = (
                f"Replace the following with {style_desc}: {', '.join(change_items)}. "
                f"Outfit should look natural, well-fitted, and consistent with the rest of the image."
            )

        return (base + instruction + IDENTITY_BLOCK + _skin_block(skin_quality),)


# ==========================================================================
# QwenClothingSelector — dropdown of named outfit presets
# ==========================================================================
class QwenClothingSelector:
    """Dropdown selector for outfit presets."""

    PRESETS = {
        "Business Casual": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to business casual — "
            "a neat blouse or button-up shirt with chinos or slacks, polished shoes. "
            "Outfit should look professional but relaxed."
            + IDENTITY_BLOCK
        ),
        "Formal Evening": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to formal evening wear — "
            "an elegant dress or tailored suit, dressy shoes. "
            "Outfit should look refined, polished, and event-appropriate."
            + IDENTITY_BLOCK
        ),
        "Casual T-Shirt + Jeans": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to a casual t-shirt and jeans, "
            "with comfortable everyday shoes. Outfit should look natural and relaxed."
            + IDENTITY_BLOCK
        ),
        "Swimwear / Beach": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to swimwear appropriate for the beach — "
            "a swimsuit or board shorts. Outfit should look natural and beach-appropriate."
            + IDENTITY_BLOCK
        ),
        "Athletic / Workout": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to athletic workout wear — "
            "a fitted sports top or sports bra, leggings or athletic shorts, athletic shoes."
            + IDENTITY_BLOCK
        ),
        "Streetwear": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to modern streetwear — "
            "a graphic tee or hoodie, cargo pants or jeans, fashionable sneakers."
            + IDENTITY_BLOCK
        ),
        "Vintage 1950s": (
            "editorial_edit: Picture 1 is the base image. Change the person's outfit to 1950s vintage style — "
            "a fitted dress with full skirt, period-appropriate shoes."
            + IDENTITY_BLOCK
        ),
        "Remove Jacket/Outerwear Only": (
            "editorial_edit: Picture 1 is the base image. Remove only the outer layer (jacket, coat, cardigan, hoodie) "
            "from the person. Keep whatever clothing is underneath visible and unchanged."
            + IDENTITY_BLOCK
        ),
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"preset": (list(cls.PRESETS.keys()), {"default": "Casual T-Shirt + Jeans"})}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "select_preset"
    CATEGORY = "Qwen/ClothingEdit"

    def select_preset(self, preset):
        return (self.PRESETS[preset],)


# ==========================================================================
# QwenSkinQualityBooster — append a skin-quality block to an incoming prompt
# ==========================================================================
class QwenSkinQualityBooster:
    """Append a skin-quality directive to an existing prompt."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "skin_quality": (["Ultra Realistic", "Realistic", "Fast"], {"default": "Realistic"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "boost"
    CATEGORY = "Qwen/ClothingEdit"

    def boost(self, prompt, skin_quality):
        return (prompt + _skin_block(skin_quality),)


# ==========================================================================
# QwenStyleSelector — broad style/genre selector
# ==========================================================================
class QwenStyleSelector:
    """Append a global style directive: photorealistic / anime / stylized."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "style": (["Photorealistic", "Anime", "Stylized Illustration", "Comic Book", "Watercolor"], {"default": "Photorealistic"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "apply"
    CATEGORY = "Qwen/ClothingEdit"

    STYLE_BLOCKS = {
        "Photorealistic": "\n\nStyle: photorealistic, natural lighting, real photo quality.",
        "Anime": "\n\nStyle: anime art style, cel-shading, clean line art.",
        "Stylized Illustration": "\n\nStyle: stylized illustration, painterly, expressive.",
        "Comic Book": "\n\nStyle: comic book art, ink lines, bold colors.",
        "Watercolor": "\n\nStyle: watercolor painting, soft edges, organic brushwork.",
    }

    def apply(self, prompt, style):
        return (prompt + self.STYLE_BLOCKS.get(style, ""),)


# ==========================================================================
# Registration
# ==========================================================================
NODE_CLASS_MAPPINGS = {
    "QwenClothingToggles": QwenClothingToggles,
    "QwenClothingSelector": QwenClothingSelector,
    "QwenSkinQualityBooster": QwenSkinQualityBooster,
    "QwenStyleSelector": QwenStyleSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenClothingToggles": "Clothing Toggles (Top/Bottom/Shoes)",
    "QwenClothingSelector": "Outfit Preset Selector",
    "QwenSkinQualityBooster": "Skin Quality Booster",
    "QwenStyleSelector": "Style Selector",
}

# Optional: expose pro pack registrations if user has it installed
try:
    from .nsfw_presets import (
        NODE_CLASS_MAPPINGS as PRO_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS as PRO_DISPLAY_MAPPINGS,
    )
    NODE_CLASS_MAPPINGS.update(PRO_CLASS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(PRO_DISPLAY_MAPPINGS)
except ImportError:
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
