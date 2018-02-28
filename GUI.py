#from PySide.QtCore import *
#from PySide.QtGui import *
#from PySide.QtSvg import *
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#from PyQt4.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
import sys
#import pycards as pc
from card_lib import *

# NOTE: This is just given as an example of how to use CardView.
# It is expected that you will need to adjust things to make a game out of it. 
# Some things can be removed, other things modified.


class TableScene(QGraphicsScene):
    """ A scene with a table cloth background """
    def __init__(self):
        super().__init__()
        self.tile = QPixmap('cards/table.png')
        self.setBackgroundBrush(QBrush(self.tile))


class CardItem(QGraphicsSvgItem):
    """ A simple overloaded QGraphicsSvgItem that also stores the card position """
    def __init__(self, renderer, position):
        super().__init__()
        self.setSharedRenderer(renderer)
        self.position = position


class CardView(QGraphicsView):
    """ A View widget that represents the table area displaying a players cards. """

    # Underscores indicate a private function/method!
    def __read_cards(): # Ignore the PyCharm warning on this line. It's correct.
        """
        Reads all the 52 cards from files.
        :return: Dictionary of SVG renderers
        """
        all_cards = dict() # Dictionaries let us have convenient mappings between cards and their images
        for suit_file, suit in zip('CDSH', range(4)): # Check the order of the suits here!!!
            for value_file, value in zip(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'], range(2, 15)):
                file = value_file + suit_file
                key = (value, suit)  # I'm choosing this tuple to be the key for this dictionary
                all_cards[key] = QSvgRenderer('cards/' + file + '.svg')
        return all_cards

    # We read all the card graphics as static class variables
    back_card = QSvgRenderer('cards/Red_Back_2.svg')
    all_cards = __read_cards()

    def __init__(self, cards_model, card_spacing=250, padding=10):
        """
        Initializes the view to display the content of the given model
        :param cards_model: A model that represents a set of cards.
        The model should have: data_changed, cards, clicked_position, flipped,
        :param card_spacing: Spacing between the visualized cards.
        :param padding: Padding of table area around the visualized cards.
        """
        self.scene = TableScene()
        super().__init__(self.scene)

        self.model = cards_model
        self.card_spacing = card_spacing
        self.padding = padding

        # Whenever the this window should update, it should call the "change_cards" method.
        # This can, for example, be done by connecting it to a signal.
        # The view can listen to changes:
        cards_model.data_changed.connect(self.change_cards)
        # It is completely optional if you want to do it this way, or have some overreaching Player/GameState
        # call the "change_cards" method instead. z

        # Add the cards the first time around to represent the initial state.
        self.change_cards()

    def change_cards(self):
        # Add the cards from scratch
        self.scene.clear()
        for i, card in enumerate(self.model.cards):
            # The ID of the card in the dictionary of images is a tuple with (value, suit), both integers
            # TODO: YOU MUST CORRECT THE EXPRESSION TO MATCH YOUR PLAYING CARDS!!!
            # TODO: See the __read_cards method for what mapping are used.
            graphics_key = (card.value, card.suit)
            renderer = self.back_card if self.model.flipped(i) else self.all_cards[graphics_key]
            c = CardItem(renderer, i)
            # Shadow effects are cool!
            shadow = QGraphicsDropShadowEffect(c)
            shadow.setBlurRadius(10.)
            shadow.setOffset(5, 5)
            shadow.setColor(QColor(0, 0, 0, 180)) # Semi-transparent black!
            c.setGraphicsEffect(shadow)
            # Place the cards on the default positions
            c.setPos(c.position * self.card_spacing, 0)
            # Sets the opacity of cards if they are marked.
            #c.setOpacity(0.5 if self.model.marked(c.position) else 1.0)
            self.scene.addItem(c)

        self.update_view()

    def update_view(self):
        scale_h = (self.viewport().height()-2*self.padding)/313
        print(scale_h)
        scale_w = (self.viewport().width()-2*self.padding)/313
        print(scale_w)
        self.resetTransform()
        self.scale(scale_h, scale_h)
        # Put the scene bounding box
        self.setSceneRect(-self.padding//scale_h, -self.padding//scale_h,
                          self.viewport().width()//scale_h, self.viewport().height()//scale_h)


    def resizeEvent(self, painter):
        # This method is called when the window is resized.
        # If the widget is resize, we gotta adjust the card sizes.
        # QGraphicsView automatically re-paints everything when we modify the scene.
        self.update_view()
        super().resizeEvent(painter)

    # # This is the Controller part of the GUI, handling input events that modify the Model
    # def mousePressEvent(self, event):
    #     # We can check which item, if any, that we clicked on by fetching the scene items (neat!)
    #     pos = self.mapToScene(event.pos())
    #     item = self.scene.itemAt(pos, self.transform())
    #     if item is not None:
    #         pass
    #         # Report back that the user clicked on the card at given position:
    #         # The model can choose to do whatever it wants with this information.
    #         #self.model.clicked_position(item.position)


    # You can remove these events if you don't need them.
    def mouseDoubleClickEvent(self, event):
        self.model.flip()  # Another possible event. Lets add it to the flip functionality for fun!


# We can extend this class to create a model, which updates the view whenever it has changed.
# NOTE: You do NOT have to do it this way.
# You might find it easier to make a Player-model, or a whole GameState-model instead.
# This is just to make a small demo that you can use. You are free to modify
class HandModel(Hand, QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        Hand.__init__(self)
        QObject.__init__(self)

        # Additional state needed by the UI, keeping track of the selected cards:
        self.marked_cards = [False]*len(self.cards)
        self.flipped_cards = True

    def flip(self):
        # Flips over the cards (to hide them)
        self.flipped_cards = not self.flipped_cards
        self.data_changed.emit()

    def marked(self, i):
        return self.marked_cards[i]

    def flipped(self, i):
        # This model only flips all or no cards, so we don't care about the index.
        # Might be different for other games though!
        return self.flipped_cards

    def clicked_position(self, i):
        # Mark the card as position "i" to be thrown away
        self.marked_cards[i] = not self.marked_cards[i]
        self.data_changed.emit()

    def add_card(self, card):
        super().add_card(card)
        self.data_changed.emit()


class buttons(QGraphicsView):
    """ A View widget that represents the table area displaying a players cards. """

    def __init__(self, button_model, button_spacing=50, padding=10):
        """
        Initializes the view to display the content of the given model
        :param cards_model: A model that represents a set of cards.
        The model should have: data_changed, cards, clicked_position, flipped,
        :param card_spacing: Spacing between the visualized cards.
        :param padding: Padding of table area around the visualized cards.
        """
        self.scene = TableScene()
        super().__init__(self.scene)
        self.model = button_model
        self.button_spacing = button_spacing
        self.padding = padding
        self.layout = QVBoxLayout()
        # Add the cards the first time around to represent the initial state.
        for i, button in enumerate(self.model):
            button.resize(100, 32)
            button.move(50, i*button_spacing)
            self.layout.addWidget(button)
            button.clicked.connect(pressed_button)
            #button.setPos(button.position * self.button_spacing, 0)
        self.update_view()

    def update_view(self):
        scale = (self.viewport().height()-2*self.padding)/313
        self.resetTransform()
        self.scale(scale, scale)
        # Put the scene bounding box
        self.setSceneRect(-self.padding//scale, -self.padding//scale,
                          self.viewport().width()//scale, self.viewport().height()//scale)

    def resizeEvent(self, painter):
        # This method is called when the window is resized.
        # If the widget is resize, we gotta adjust the card sizes.
        # QGraphicsView automatically re-paints everything when we modify the scene.
        self.update_view()
        super().resizeEvent(painter)


def pressed_button():
    print("You pressed a button!")

# Lets test it out
app = QApplication(sys.argv)

hand1 = HandModel()
hand1.add_card(NumberedCard(3, Suits.clubs))
hand1.add_card(NumberedCard(4, Suits.clubs))
hand2 = HandModel()
hand2.add_card(NumberedCard(7, Suits.clubs))
hand2.add_card(NumberedCard(6, Suits.clubs))

card_view1 = CardView(hand1)
card_view2 = CardView(hand2)
# card_view1.setMaximumSize(2000, 300)
# card_view1.setMinimumWidth(500)


# Creating a small demo window to work with, and put the card_view inside:
layout = QHBoxLayout()
button_box = QVBoxLayout()

button = [QPushButton("Check/Call"), QPushButton("Fold"), QPushButton("Raise")]
butt = buttons(button)
line_edit = QLineEdit("Amount: ")
button_box.addLayout(butt.layout)
button_box.addWidget(line_edit)
layout.addWidget(card_view1)
layout.addLayout(button_box)
layout.addWidget(card_view2)


game_view = QWidget()#QGroupBox("Texas Hold'em")
game_view.setLayout(layout)
game_view.setGeometry(300, 300, 1200, 550)
game_view.show()

app.exec_()
