# ComfyUI-QwenClothingSelector

Custom nodes for **Qwen-Image-Edit** clothing/outfit edits in ComfyUI.

Build clean Qwen-Image-Edit prompts via toggles and presets — outfit swaps, costume changes, fashion experiments — with identity-preservation guards (face, hair, skin tone) baked in.

Output is a `STRING` that feeds into `TextEncodeQwenImageEditPlus`.

---

## Why this exists

Hand-writing a Qwen-Image-Edit prompt is finicky:
- Has to start with `editorial_edit:` and reference "Picture 1"
- Has to explicitly preserve face, head, hair, skin tone — Qwen-Image-Edit will happily regenerate the entire masked region otherwise
- Each clothing-change scenario needs different keep/replace instructions

These nodes encapsulate all of that. Click toggles, get a clean prompt the encoder is happy with.

---

## Nodes

| Node | What it does |
|------|--------------|
| **Clothing Toggles** | Checkboxes for top / bottom / shoes / accessories + target style + skin quality. The everyday-driver node. |
| **Outfit Preset Selector** | Named outfit presets — Business Casual, Formal Evening, Streetwear, Swimwear, Athletic, Vintage 1950s, etc. |
| **Skin Quality Booster** | Appends a skin-quality directive (Ultra Realistic / Realistic / Fast) to an existing prompt. |
| **Style Selector** | Appends a global art-style directive — Photorealistic, Anime, Watercolor, etc. |

All nodes appear under the **Qwen/ClothingEdit** category in ComfyUI.

---

## Install

### Via ComfyUI-Manager (recommended once registered)
Search "QwenClothingSelector" in Manager → Install → Restart.

### Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xxchinenxx/ComfyUI-QwenClothingSelector.git
```
Restart ComfyUI. No additional Python dependencies.

---

## Usage

```
[Outfit Preset Selector] ──prompt──▶ [TextEncodeQwenImageEditPlus]
```

Or with toggles:

```
[Clothing Toggles] ──prompt──▶ [TextEncodeQwenImageEditPlus]
```

For full control:

```
[Outfit Preset Selector]──▶[Skin Quality Booster]──▶[Style Selector]──▶[Encoder]
```

---

## Identity preservation

Every prompt this pack builds includes:

```
CRITICAL IDENTITY PRESERVATION:
- PRESERVE THE FACE EXACTLY AS-IS
- PRESERVE HAIR EXACTLY AS-IS
- PRESERVE HEAD AND NECK EXACTLY AS-IS
- MATCH SKIN COLOR AND TONE EXACTLY
- DO NOT modify hair in any way
```

Combined with a body-mask upstream (e.g. `RMBG body − FaceSegment head`), this is what keeps the subject's face and hair intact across the edit.

---

## Pro Pack (adult content)

A separate **NSFW Pro Pack** adds explicit-content presets — full nudify, anatomical detail toggles, and editorial NSFW modes — as a drop-in `nsfw_presets.py` file.

Available on Patreon: *link coming soon*

---

## License

MIT — see `LICENSE` file.

Copyright © 2026 Joe Fred Umlas
