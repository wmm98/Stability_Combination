from PIL import Image
import rembg


class KeyPhoto:
    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)


if __name__ == '__main__':
    ph = KeyPhoto()
    ph.save_key_photo("0.png", "0_new.png")
    ph.save_key_photo("1.png", "1_new.png")
