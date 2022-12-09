import cocos #uses singleton 
from cocos.director import director
from pyglet.window import mouse
from cocos.scenes import *
from random import randint, shuffle
import pyglet

#Open the game
director.init(width=1024, height=576, caption="You Have To Match Them All!!")
director.window.pop_handlers()
director.window.set_location(400, 200)

class manageCard():

    multipleClick = []
    pairs = 0 #tracker of number of pairs

    def __init__(self):
        self.level1 = 6 # number of cards at the start of the game
        self.level2 = 12 #level 2 and onwards
        self.level3 = 20
        self.level4 = 24

        self.current_level = self.level3 #set the level

        path = "ext/pictures/" #all the card pictures
        files = [path + "minion100.png", path + "capman.png", path + "superman.png",
                 path + "pika.png", path + "herbert.png", path + "harry.png",
                 path + "charmander.png", path + "mew2.png", path + "penguin.png",
                 path + "adi.png", path + "tacocat.png", path + "koala.png"]

        listFile = []

        for i in range(self.current_level // 2): #randomize what card spawn in where!
            r = randint(0, len(files) - 1)
            if files[r] not in listFile:
                listFile.append(files[r])
                listFile.append(files[r])
            else:
                while files[r] in listFile:
                    r = randint(0, len(files) - 1)
                listFile.append(files[r])
                listFile.append(files[r])

        shuffle(listFile)

        positions = self.pos()

        for i, file in enumerate(listFile):
            card = CardLayer(file)
            card.spr.image_anchor_x = 0
            card.spr.image_anchor_y = 0
            card.spr.position = positions[i]
            card.back.position = card.spr.position
            SceneManager.game_scene.add(card)

    def pos(self): #positions of everything
        xx, yy = 0, 0
        if self.current_level == self.level1:
            xx, yy = 3, 2
        elif self.current_level == self.level2:
            xx, yy = 4, 3
        elif self.current_level == self.level3:
            xx, yy = 5, 4
        elif self.current_level == self.level4:
            xx, yy = 6, 4
        positions = []
        x_offset = 50
        y_offset = 50
        for x in range(xx):
            for y in range(yy):
                positions.append((x_offset, y_offset))
                y_offset += 120 #adjust this -- is this the reason game does not work on mac properly??
            x_offset += 120
            y_offset = 50

        return positions

    @staticmethod
    def flip_cards_back(dt): #flip the cards
        for card in manageCard.multipleClick:
            card.back.visible = True
        manageCard.multipleClick = []  # need to set this here also

    @staticmethod
    def remove_cards(dt): #remove the cards
        SceneManager.game_scene.remove(manageCard.multipleClick[0])
        SceneManager.game_scene.remove(manageCard.multipleClick[1])
        manageCard.multipleClick = [] # need to set this here also

    @staticmethod
    def check_cards(): #check the cards
        if len(manageCard.multipleClick) == 2:
            if manageCard.multipleClick[0].name == manageCard.multipleClick[1].name:
                manageCard.pairs += 1
                pyglet.clock.schedule_once(manageCard.remove_cards, 0.5)
            else:
                pyglet.clock.schedule_once(manageCard.flip_cards_back, 1.0)
        if manageCard.pairs == 10: #game condition to finish : must hardcode based on level and number of cards present
            manageCard.pairs = 0
            gameSet.game_finished = True
            SceneManager.change_scene(SceneManager.wining_scene) #win!

class CardLayer(cocos.layer.Layer): #the layer of cards 
    is_event_handler = True
    def __init__(self, image_path):
        super().__init__()
        self.clicked = False
        self.spr = cocos.sprite.Sprite(image_path, anchor=(0, 0))
        self.name = image_path.split("/")[2].split(".")[0]

        self.back = cocos.sprite.Sprite('ext/pictures/backk.png', anchor=(0, 0)) #card back image set

        self.add(self.spr)
        self.add(self.back)

    def touchCard(self, x, y):
        return x < self.spr.x + self.spr.width and x > self.spr.x and y < self.spr.y + self.spr.height and y > self.spr.y

    def on_mouse_press(self, x, y, button, modifiers): #handle the mouse press
        if button & mouse.LEFT:
            if self.touchCard(x, y) and len(manageCard.multipleClick) < 2:
                self.clicked = True
                self.back.visible = False
            else:
                self.clicked = False
        if self.clicked and self not in manageCard.multipleClick:
            manageCard.multipleClick.append(self)
            manageCard.check_cards()

class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super().__init__('Can You Guess Them All?')

        items = [] #all the items

        items.append(cocos.menu.MenuItem('Log in', self.on_new_game)) #menu
        items.append(cocos.menu.MenuItem('New Game', self.on_new_game))
        items.append(cocos.menu.MenuItem('Quit', self.on_quit))

        self.create_menu(items, cocos.menu.shake(), cocos.menu.shake_back())

    def on_new_game(self):
        SceneManager.change_scene(SceneManager.game_scene) #start of a new game

    def on_quit(self): #quit the game
        director.window.close()


# Back to main button
class Button(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, pos):
        super().__init__()
        self.spr = cocos.sprite.Sprite('ext/pictures/back_to_main.png') #return to the main menu

        self.spr.position = pos

        self.add(self.spr)

    def button_clicked(self, x, y): #clicked button
        return x > self.spr.x - (self.spr.width//2) and x < self.spr.x + (self.spr.width // 2) and \
               y > self.spr.y - (self.spr.height//2) and y < self.spr.y + (self.spr.height // 2)

    def on_mouse_press(self, x, y, button, modifiers): #when we press
        if button & mouse.LEFT:
            if self.button_clicked(x, y):
                SceneManager.change_scene(SceneManager.start_scene)

    def on_mouse_motion(self, x, y, dx, dy): #moving the mouse around
        if self.button_clicked(x, y):
            self.spr.scale = 1.2
        else:
            self.spr.scale = 1


# The Timer
class Timer(cocos.layer.Layer):

    current_time = ""
    time_start = None
    time_stop = None

    def __init__(self):
        super().__init__()
        self.label = cocos.text.Label("", font_name="Times New Roman", font_size=26,
                                 anchor_x="center", anchor_y="center")
        self.start_time = 0

        self.label.position = 874, 276
        self.add(self.label)

        Timer.time_start = self.run_scheduler
        Timer.time_stop = self.stop_scheduler

    def timer(self, dt):
        if gameSet.game_finished:
            self.stop_scheduler()
            self.start_time = 0
            gameSet.game_finished = False
        else:
            mins, secs = divmod(self.start_time, 60)
            time_format = '{:02d}:{:02d}'.format(mins, secs)
            Timer.current_time = time_format
            self.label.element.text = time_format
            self.start_time += 1

    def run_scheduler(self):
        self.schedule_interval(self.timer, 1.0)

    def stop_scheduler(self):
        self.unschedule(self.timer)

#End timer stuff

""" ALL THE SCENES """
class gameStart(cocos.scene.Scene): #start scene
    def __init__(self):
        super().__init__()

        menu = MainMenu()

        self.add(cocos.layer.ColorLayer(50, 50, 50, 180))
        self.add(menu)


class gameSet(cocos.scene.Scene): #set the game

    game_finished = False

    def __init__(self):
        super().__init__()

        self.add(cocos.layer.ColorLayer(50, 50, 50, 180))
        self.add(Button(pos=(874, 376)))
        self.add(Timer())

class gameWin(cocos.scene.Scene): #if you win (sometimes works)
    def __init__(self):
        super().__init__()

        self.add(cocos.layer.ColorLayer(50, 50, 50, 180))
        self.add(Button(pos=(512, 156)))

        self.add(cocos.text.Label("Your time was:", font_name="Times New Roman", font_size=26,
                                      anchor_x="center", anchor_y="center", position=(512,300)))

        self.score = cocos.text.Label("", font_name="Times New Roman", font_size=22,
                                     anchor_x="center", anchor_y="center", position=(512, 220))

        self.add(self.score)


    def on_exit(self):
        super().on_exit()


""" THE SCENE MANAGER """
class SceneManager: #RUN THE GAME IN ORDER

    start_scene = gameStart()
    game_scene = gameSet()
    wining_scene = gameWin()

    active_scene = start_scene

    @staticmethod
    def change_scene(scene):
        SceneManager.active_scene = scene
        if SceneManager.active_scene == SceneManager.game_scene:
            manageCard()
            Timer.time_start()
        elif SceneManager.active_scene == SceneManager.start_scene:
            for child in SceneManager.game_scene.get_children():
                if hasattr(child, 'name'):
                    child.kill()
        director.replace(FlipX3DTransition(SceneManager.active_scene, duration=2))


if __name__ == "__main__":
    director.run(SceneManager.active_scene)