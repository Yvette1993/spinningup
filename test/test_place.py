import gym
import cell_place_gym
from pynput import keyboard  # using module keyboard


class MainLoop:
    def __init__(self):
        self.env = gym.make('cell_place_env-v0')
        self.env.reset()

        self.exit_now = False

        self.counter = 0

        with keyboard.Listener(on_press=lambda k: self.on_keyboard_press(k),
                               on_release=lambda k: self.on_keyboard_release(k)) as listener:
            while not self.exit_now:
                self.env.render()


    def on_keyboard_press(self, key):
        print(f"Press : {key}")

    def on_keyboard_release(self, key):
        print(f"Release : {str(key)}")
        if str(key) == "'q'":
            self.exit_now = True

        if str(key) == "Key.space":
            success, done = self.env.step()
            self.counter += 1


if __name__ == '__main__':
    main = MainLoop()
