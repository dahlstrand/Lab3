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
            graphics_key = (card.get_value(), card.get_suit())
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
        scale_w = (self.viewport().width()-2*self.padding)/313
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
        self.flippable = True

    def flip(self):
        # Flips over the cards (to hide them)
        if self.flippable:
            self.flipped_cards = not self.flipped_cards
        self.data_changed.emit()

    def marked(self, i):
        return self.marked_cards[i]

    def flipped(self, i):
        # This model only flips all or no cards, so we don't care about the index.
        # Might be different for other games though!
        return self.flipped_cards

    def add_card(self, card):
        super().add_card(card)
        self.data_changed.emit()

    def empty_hand(self):
        super().remove_card(list(range(len(self.cards))))
        self.data_changed.emit()


class DealerModel(Hand, QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        Hand.__init__(self)
        QObject.__init__(self)

        # Additional state needed by the UI, keeping track of the selected cards:
        self.marked_cards = [False]*len(self.cards)
        self.flipped_cards = False

    def marked(self, i):
        return self.marked_cards[i]

    def flip(self):
        # Flips over the cards (to hide them)
        self.flipped_cards = self.flipped_cards
        self.data_changed.emit()

    def flipped(self, i):
        # This model only flips all or no cards, so we don't care about the index.
        # Might be different for other games though!
        return self.flipped_cards

    def add_card(self, card):
        super().add_card(card)
        self.data_changed.emit()

    def empty_dealer(self):
        super().remove_card(list(range(len(self.cards))))
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
            #button.clicked.connect(pressed_button)
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


class TexasHold(QObject):
    new_total = pyqtSignal()
    winner = pyqtSignal(str, )
    read_players = pyqtSignal()

    def __init__(self, player1="Player 1", player2="Player 2", money1=1000, money2=1000):
        super().__init__()
        self.read_players.emit()
        print(player1)
        print(player2)
        self.players = [player1, player2]
        self.money = [money1, money2]
        self.bet = 0
        self.pot = 0
        self.total = self.money + [0]
        self.which_player = 0
        self.player2_has_raised = 0

        self.deck = StandardDeck()
        self.deck.shuffle()

        self.hand1 = HandModel()
        self.hand2 = HandModel()
        self.dealer = DealerModel()
        self.hand1.add_card(self.deck.take_top())
        self.hand2.add_card(self.deck.take_top())
        self.hand1.add_card(self.deck.take_top())
        self.hand2.add_card(self.deck.take_top())

    def check_call_button(self):
        if self.which_player == 0:       # if player1 active
            if self.player2_has_raised == 1:
                self.player2_has_raised = 0
                self.total[0] -= self.bet
                self.pot += self.bet
                self.new_deal()
            else:
                self.change_player()
            self.new_total.emit()
        else:
            self.total[1] -= self.bet
            self.pot += self.bet
            self.new_deal()

    def fold_button(self):
        self.total[not self.which_player] += self.pot
        self.check_winner_game()
        self.new_total.emit()
        self.new_round()

    def raise_button(self):
        # print("Clicked raise")
        if self.which_player == 0:
            self.bet = self.total[2]
            self.total[0] -= self.bet
            self.pot += self.bet
        else:
            self.bet = self.total[2]-self.bet
            self.total[1] -= self.total[2]
            self.pot += self.bet
            self.player2_has_raised = 1
        self.change_player()

    def slider(self, value):
        # print("SLIDER: ")
        self.total[2] = value
        self.new_total.emit()

    def change_player(self):
        if not self.which_player:       # if player 1 active
            self.which_player = 1
            
        else:
            self.which_player = 0
        self.new_total.emit()

    def new_deal(self):
        # print("New round!")
        self.bet = 0
        if len(self.dealer) == 0:
            self.deck.take_top()
            for i in range(3):
                self.dealer.add_card(self.deck.take_top())
            self.which_player = 0
        elif 0 < len(self.dealer) < 5:
            self.deck.take_top()
            self.dealer.add_card(self.deck.take_top())
            self.which_player = 0
        else:
            self.winner_round()
            self.check_winner_game()
            self.new_round()
        self.new_total.emit()

    def new_round(self):
        self.pot = 0
        self.bet = 0
        self.deck = StandardDeck()
        self.deck.shuffle()
        self.which_player = 0
        self.player2_has_raised = 0
        self.dealer.empty_dealer()
        self.hand1.empty_hand()
        self.hand2.empty_hand()
        self.hand1.add_card(self.deck.take_top())
        self.hand2.add_card(self.deck.take_top())
        self.hand1.add_card(self.deck.take_top())
        self.hand2.add_card(self.deck.take_top())

    def winner_round(self):
        best_hand1 = self.hand1.best_poker_hand(self.dealer.cards)
        best_hand2 = self.hand2.best_poker_hand(self.dealer.cards)
        # print("I winner_round")
        if best_hand1 < best_hand2:
            # print("Hand 2 är bättre än 1")
            self.total[1] += self.pot
        elif best_hand2 < best_hand1:
            # print("Hand 1 är bättre än 2")
            self.total[0] += self.pot
        else:
            self.total[0] += self.pot/2
            self.total[1] += self.pot/2
        self.pot = 0

    def check_winner_game(self):
        if self.total[0] == 0:
            self.winner.emit(self.players[1] + " won!")
        elif self.total[1] == 0:
            self.winner.emit(self.players[0] + " won!")


class GameView(QWidget):

    def __init__(self, game_model):
        super().__init__()

        card_view1 = CardView(game_model.hand1)
        card_view2 = CardView(game_model.hand2)
        card_view3 = CardView(game_model.dealer)
        card_view1.setMaximumSize(card_view1.width()/2, 500)# self.viewport().height()-2*self.padding)/313
        card_view2.setMaximumSize(card_view2.viewport().width()/2, 500)

        # Creating a small demo window to work with, and put the card_view inside:

        self.labels = [QLabel(), QLabel(), QLabel()]

        layout = QHBoxLayout()
        button_box = QVBoxLayout()
        table_layout = QVBoxLayout()
        player1 = QVBoxLayout()
        player1.addWidget(QLabel(game_model.players[0]))
        player1.addWidget(card_view1)
        player1.addWidget(self.labels[0])
        player2 = QVBoxLayout()
        player2.addWidget(QLabel(game_model.players[1]))
        player2.addWidget(card_view2)
        player2.addWidget(self.labels[1])
        dealer = QVBoxLayout()
        dealer.addWidget(QLabel("Dealer"))
        dealer.addWidget(card_view3)

        button = [QPushButton("Check/Call"), QPushButton("Fold"), QPushButton("Raise")]
        butt = buttons(button)
        self.players_turn = QLabel()
        self.sld = QSlider(Qt.Horizontal)

        self.sld.setValue(0)
        # self.sld.setPageStep(50)

        button_box.addLayout(butt.layout)
        button_box.addWidget(self.players_turn)

        # sldLabel = #QLabel("bet: {}".format(1000))
        button_box.addWidget(self.labels[2])  # sldLabel)
        button_box.addWidget(self.sld)

        layout.addLayout(player1)
        layout.addLayout(button_box)
        layout.addLayout(player2)
        table_layout.addLayout(dealer)
        table_layout.addLayout(layout)

        self.setLayout(table_layout)
        self.setGeometry(300, 300, 1000, 550)
        self.setWindowTitle("Texas Hold'em")
        self.show()

        # Model!
        self.game = game_model
        self.update_labels()
        game_model.new_total.connect(self.update_labels)
        game_model.winner.connect(self.alert_winner)
        #game_model.read_players.connect(self.read_players)
        # game_model.read_players.connect(self.read_players)

        # controller
        def check_call_click():
            game_model.check_call_button()
        button[0].clicked.connect(check_call_click)

        def fold_click():
            game_model.fold_button()
        button[1].clicked.connect(fold_click)

        def raise_click():
            game_model.raise_button()
        button[2].clicked.connect(raise_click)

        def slider():
            game_model.slider(self.sld.value())
        self.sld.valueChanged.connect(slider)

    def update_labels(self):
        for i in range(len(self.labels)):
            self.labels[i].setText(str(self.game.total[i]))
        self.players_turn.setText("Player " + str(self.game.players[self.game.which_player]) + "'s turn.")

        if self.game.which_player == 0:
            if self.game.player2_has_raised == 0:
                self.sld.setMinimum(0)
                self.sld.setMaximum(min(self.game.total[0:2]))
            else:
                self.sld.setMinimum(self.game.bet)
                self.sld.setMaximum(self.game.bet)
        else:
            self.sld.setMinimum(self.game.bet)
            self.sld.setMaximum(min([self.game.bet + self.game.total[0], self.game.total[1]]))

    def alert_winner(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.exec()
        self.close()


class ReadPlayers(QDialog):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.text1 = QLabel("Enter the name of Player 1: ")
        self.name1 = QLineEdit()
        self.text2 = QLabel("Enter the amount of cash for Player 1: ")
        self.cash1 = QLineEdit()
        self.text3 = QLabel("Enter the name of Player 2: ")
        self.name2 = QLineEdit()
        self.text4 = QLabel("Enter the amount of cash for Player 2: ")
        self.cash2 = QLineEdit()

        layout.addWidget(self.text1)
        layout.addWidget(self.name1)
        layout.addWidget(self.text2)
        layout.addWidget(self.cash1)
        layout.addWidget(self.text3)
        layout.addWidget(self.name2)
        layout.addWidget(self.text4)
        layout.addWidget(self.cash2)

        # OK and Cancel buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_inputs(self):
        return self.name1.text(), int(self.cash1.text()), self.name2.text(), int(self.cash2.text())

    @staticmethod
    def getDateTime():
        dialog = ReadPlayers()
        result = dialog.exec_()
        inputs = dialog.get_inputs()
        return inputs


# Lets test it out


app = QApplication(sys.argv)
players_info = ReadPlayers.getDateTime()
game = TexasHold(players_info[0], players_info[2], players_info[1], players_info[3])
view = GameView(game)

app.exec_()
