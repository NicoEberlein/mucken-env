import os.path

import imageio
from PIL import Image
from pettingzoo.utils import BaseWrapper


class MuckenGifWrapper(BaseWrapper):

    def __init__(self, env, filename, scaling=1.0, path="gifs"):
        super().__init__(env)
        self.frames = []
        self.path = path
        self.filename = filename
        self.scaling = scaling
        self.is_active = env.render_mode == "rgb_array"
        self.fps = env.render_fps
        self.counter = 0

        os.makedirs(self.path, exist_ok=True)

    def step(self, action):
        super().step(action)

        if not self.is_active:
            return

        raw_frame = super().render()
        if raw_frame is not None:

            image_obj = Image.fromarray(raw_frame)

            new_width = int(image_obj.width * self.scaling)
            new_height = int(image_obj.height * self.scaling)

            resized_image = image_obj.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

            self.frames.append(resized_image)

    def close(self):
        super().close()
        if self.is_active:
            self._save_frames()

    def reset(self, seed=None, options=None):
        super().reset(seed, options)
        if self.is_active:
            self._save_frames()

    def _save_frames(self):
        if self.frames:
            full_path = os.path.join(self.path, f"{self.filename}_{self.counter}.gif")
            print(f"Saving frame to {full_path}")
            imageio.mimsave(full_path, self.frames, fps=self.fps)
            self.counter += 1
