# handlers/joke_handler.py

class JokeHandler:
    def __init__(self):
        self.jokes = [
            "Was macht ein Pirat am Computer? Er drückt die Enter-Taste.",
            "Warum können Elefanten nicht fliegen? Weil sie zu schwer für den Flugzeugmodus sind.",
            "Wie nennt man einen Bumerang, der nicht zurückkommt? Ein Stock.",
        ]

    async def get_top_joke(self):
        import random
        return self.jokes[random.randint(0, len(self.jokes)-1)]
