from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
import sys


class TableScene(QGraphicsScene):
    """ A scene with a table cloth background """
    def __init__(self):
        super().__init__()
        self.tile = QPixmap('cards/table.png')
        self.setBackgroundBrush(QBrush(self.tile))


class CardSvgItem(QGraphicsSvgItem):
    """ A simple overloaded QGraphicsSvgItem that also stores the card position """
    def __init__(self, renderer, id):
        super().__init__()
        self.setSharedRenderer(renderer)
        self.position = id


class CardView(QGraphicsView):
    # Underscores indicate a private function!
    def __read_cards(): # Ignore the PyCharm warning on this line. It's correct.
        """
        Reads all the 52 cards from files.
        :return: Dictionary of SVG renderers
        """
        all_cards = dict()
        for suit in 'HDSC':
            for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                file = value + suit
                all_cards[file] = QSvgRenderer('cards/' + file + '.svg')
        return all_cards

    # We read all the card graphics as static class variables:
    back_card = QSvgRenderer('cards/Red_Back_2.svg')
    all_cards = __read_cards()

    def __init__(self, player, card_spacing=250, padding=10):

        self.scene = TableScene()
        super().__init__(self.scene)

        self.card_spacing = card_spacing
        self.padding = padding

        self.player = player
        player.set_callback(self.change_cards)

        self.change_cards() # Add the cards the first time around to represent the initial state.

    def change_cards(self):
        # Add the cards from scratch:
        self.scene.clear()
        for i, c_ref in enumerate(self.player.cards):
            renderer = self.back_card if self.player.marked_cards[i] else self.all_cards[c_ref]

            c = CardSvgItem(renderer, i)
            self.scene.addItem(c)

        self.update_view()

    def update_view(self):
        for c in self.scene.items():
            # Lets have the cards take up almost the (current) full height
            card_height = c.boundingRect().bottom()
            scale = (self.height()-2*self.padding)/card_height

            c.setPos(c.position * self.card_spacing*scale, 0)
            c.setScale(scale)
            #c.setOpacity(0.5 if self.player.marked_cards[c.position] else 1.0)

        # Put the scene bounding box
        self.scene.setSceneRect(-self.padding, -self.padding, self.viewport().width(), self.viewport().height())

    def resizeEvent(self, painter):
        # If the widget is resize, we gotta adjust the card sizes.
        # QGraphicsView automatically re-paints everything when we modify the scene.
        self.update_view()
        super().resizeEvent(painter)

    # This is the Controller part of the GUI, handling input events that modify the Model
    def mousePressEvent(self, event):
        #item = self.scene.itemAt(event.pos()) # For PyQt4
        item = self.scene.itemAt(event.pos(), self.transform())
        if item is not None:
            # Report back that the Model that the user marked a given position:
            self.player.mark_position(item.position)


class Player:
    def __init__(self):
        # Lets use some hardcoded values for most of this to start with:
        self.cards = ['QS', 'AD', '7C']
        self.marked_cards = [False]*len(self.cards)
        self.credits = 100
        self.folded = False
        self.cb = None

    def set_callback(self, cb):
        # Instead of the sophisticated signal system, I have a simple callback here.
        # This only works if there is just one viewer!
        # But I want to reduce the complexity in this example to make it clear why things occur.
        self.cb = cb

    def active(self):
        return credits > 0 and not self.folded

    def mark_position(self, i):
        # Mark the card as position "i" to be thrown away
        self.marked_cards[i] = not self.marked_cards[i]
        if self.cb is not None: self.cb()

    def marked(self, id):
        return self.marked_cards[id]


# Lets test it out
qt_app = QApplication(sys.argv)
#qt_app = QApplication.instance()
p = Player()
card_view = CardView(p)
box = QHBoxLayout()
box.addWidget(card_view)
player_view = QGroupBox("Player 1")
player_view.setLayout(box)

player_view.show()

qt_app.exec_()
