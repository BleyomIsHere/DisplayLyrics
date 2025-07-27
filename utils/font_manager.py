import customtkinter as ctk

class FontManager:
    def __init__(self):
        self.fonts = {}

    def get(self, weight="Regular", size=14, italic=False):
        # Just two values are valid: 'normal' or 'bold'
        bold_weights = {"SemiBold", "Bold", "ExtraBold", "Black"}
        actual_weight = "bold" if weight in bold_weights else "normal"

        font_key = f"{weight}-{size}-{'italic' if italic else 'normal'}"
        if font_key not in self.fonts:
            self.fonts[font_key] = ctk.CTkFont(
                family="Inter",
                size=size,
                weight=actual_weight,
                slant="italic" if italic else "roman"
            )

        return self.fonts[font_key]
