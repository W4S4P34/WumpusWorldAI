class SceneBase:
    def __init__(self, screen=None):
        self.next = self
        self.screen = screen

    def ProcessInput(self, events, pressed_keys):
        print("Did not override this in the child class")

    def Update(self, deltatime):
        print("Did not override this in the child class")

    def Render(self):
        print("Did not override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)
