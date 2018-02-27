from random import shuffle
import enum
import numpy as np
import abc


class PlayingCard(metaclass=abc.ABCMeta):
    """
    This class represents a standard class for all individual cards in a deck.
    """
    def __init__(self, suit):
        self.suit = suit
        if not isinstance(suit, Suits):
            raise TypeError

    @abc.abstractmethod
    def get_value(self):
        """
        :return: The value of the card, ranging from 2 to 14.
        """
        pass

    def get_suit(self):
        """
        :return: The suit of the card, either spade, diamond, clubs or hearts.
        """
        return self.suit

    @abc.abstractmethod
    def get_name(self):
        """
        :return: The name of the card, for instance "Jack" or "1" etc.
        """
        pass

    def __str__(self):
        return self.get_name() + " of " + str(self.get_suit())

    def __lt__(self, other):
        return self.get_value() < other.get_value()

    def __eq__(self, other):
        return self.get_value() == other.get_value() and self.get_suit() == other.get_suit()


class NumberedCard(PlayingCard):
    """
    Class representing the numbered card in a deck which inherits from the PlayingCard class.
    """
    def __init__(self, value, suit):
        self.value = value
        super().__init__(suit)

    def get_value(self):
        return self.value

    def get_name(self):
        return str(self.value)


class JackCard(PlayingCard):
    """
    Class representing the jack card in a deck which inherits from the PlayingCard class.
    """
    def get_value(self):
        return 11

    def get_name(self):
        return 'Jack'


class QueenCard(PlayingCard):
    """
    Class representing the queen card in a deck which inherits from the PlayingCard class.
    """
    def get_value(self):
        return 12

    def get_name(self):
        return 'Queen'


class KingCard(PlayingCard):
    """
    Class representing the king card in a deck which inherits from the PlayingCard class.
    """
    def get_value(self):
        return 13

    def get_name(self):
        return 'King'


class AceCard(PlayingCard):
    """
    Class representing the ace card in a deck which inherits from the PlayingCard class.
    """
    def get_value(self):
        return 14

    def get_name(self):
        return 'Ace'


class Suits(enum.IntEnum):
    """
    This class defines the values of the suits using enums.
    """
    hearts = 3
    spades = 2
    diamonds = 1
    clubs = 0

    def __str__(self):
        return '♣♦♠♥'[self.value]


class StandardDeck:
    """
    StandardDeck is a class which describes a deck which contains 52 individual cards.
    """
    def __init__(self):
        self.cards = []

        for color in Suits:
            for i in range(2, 11):

                self.cards.append(NumberedCard(i, color))

            self.cards.append(JackCard(color))

            self.cards.append(QueenCard(color))

            self.cards.append(KingCard(color))

            self.cards.append(AceCard(color))

    def shuffle(self):
        """
        This method shuffles the deck.

        :return: Shuffles the deck.
        """
        shuffle(self.cards)

    def take_top(self):
        """
        This method takes the top card and removes it from the deck.

        :return: the top_card of type PlayingCard
        """
        top_card = self.cards.pop(0)
        return top_card


class Hand:
    """
    The Hand class represents a hand of a player which contains cards. Cards can be added and removed from the hand
    as well as sort the cards in the hand. It can also evaluate which combination of cards gives the best pokerhand.
    """

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """
        :param card: An object of type PlayingCard
        :return: Nothing, it adds a card to the players Hand object
        """
        if isinstance(card, PlayingCard):
            self.cards.append(card)
        else:
            raise TypeError("Wrong kind of card!")

    def remove_card(self, index):
        """
        :param index: a list of indices of which cards should be thrown away
        :return: Removes one or multiple cards from Hand if possible
        """
        index.sort()
        index.reverse()
        if type(index) == list and len(index) > 0:
            if len(self.cards) - max(index) > 0:
                for i in index:
                    self.cards.pop(i)
            else:
                raise IndexError("Trying to remove a card that doesn't exist")

    def sort_hand(self):
        """
        Sorts the hand by suit and then by value.

        :return: Sorted cards in Hand.
        """
        self.cards.sort(key=lambda k: [k.get_suit().value, k.get_value()])

    def best_poker_hand_total(self, table_cards):
        """
        A simple method which collects all cards for a player, which includes the cards represented on the table in
        certain games.

        :param table_cards: Cards in a list representing tha cards on the table.
        :return: a list of all possible cards for a player.
        """
        total_cards = self.cards + table_cards
        return total_cards

    def best_poker_hand(self, table_cards):
        """
        This method evaluates which cards in Hand makes best possible combination of cards.

        :param table_cards: A list of cards represented on the table
        :return: A PokerHand which is fully comparable with other PokerHand's with the normal comparable operators.
        """
        total_cards = self.best_poker_hand_total(table_cards)
        value_cards, list, suit_cards = create_bins_for_cards(total_cards)
        cond, best_hand = straight_flush_test(total_cards, suit_cards, list, value_cards)
        if cond:
            return best_hand
        cond, best_hand = four_of_a_kind_test(list, value_cards)
        if cond:
            return best_hand
        cond, best_hand = full_house_test(list)
        if cond:
            return best_hand
        cond, best_hand = flush_test(total_cards, suit_cards, list)
        if cond:
            return best_hand
        cond, best_hand = straight_test(list, value_cards)
        if cond:
            return best_hand
        cond, best_hand = three_of_a_kind_test(list, value_cards)
        if cond:
            return best_hand
        cond, best_hand = two_pairs_test(list, value_cards)
        if cond:
            return best_hand
        cond, best_hand = one_pair_test(list)
        if cond:
            return best_hand
        cond, best_hand = high_card_test(list)
        if cond:
            return best_hand

    def __len__(self):
        return len(self.cards)


def straight_flush_test(cards, suit_cards, list, value_cards):
    """
    A method to evaluate if the player has a straight flush.

    :param cards: The cards available for the player to evaluate.
    :param suit_cards: A list of the suits the player has.
    :param list: A list which specifies which cards are in the Hand.
    :param value_cards: The values of the cards in Hand.
    :return: Returns True and a PokerHand object if the player has a straight flush, otherwise False and None.
    """
    hand_rank = PokerHandType.straight_flush.value
    straight_bool, straight = straight_test(list, value_cards)
    colour_bool, colour = flush_test(cards, suit_cards, list)
    if straight_bool and colour_bool:
        rank_value = straight.rank_value
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def four_of_a_kind_test(list, value_cards):
    """
    A method to evaluate if the player has four of a kind.

    :param list: A list which specifies which cards are in the Hand.
    :param value_cards: The values of the cards in Hand.
    :return: Returns True and a PokerHand object if the player has four of a kind, otherwise False and None.
    """
    if 4 in list:
        #print('You got four of a kind in {}:s'.format(kinds_of_values[list.index(4)]))
        hand_rank = PokerHandType.four_of_a_kind.value
        rank_value = ((list.index(4)+2, value_cards[-1]))
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def full_house_test(list):
    """
    A method to evaluate if the player has a full house.

    :param list: A list which specifies which cards are in the Hand.
    :return: Returns True and a PokerHand object if the player has a full house, otherwise False and None.
    """
    if 3 in list and 2 in list:
        temp_list = list.copy()
        temp_list.reverse()
        hand_rank = PokerHandType.full_house.value
        rank_value = ((len(temp_list)+1 - temp_list.index(3), len(temp_list)+1 - temp_list.index(2)))
        #print('You got a full house with {}:s over {}:s' .format(kinds_of_values[len(temp_list)-1 - temp_list.index(3)],
        #                                                         kinds_of_values[len(temp_list)-1 - temp_list.index(2)]))
        return True, PokerHand(hand_rank, rank_value)
    elif list.count(3) == 2:
        temp_list = list.copy()
        temp_list.reverse()
        hand_rank = PokerHandType.full_house.value
        rank_value = ((len(list)+1 - temp_list.index(3), list.index(3)+2))
        #print('You got a full house with {}:s over {}:s'.format(kinds_of_values[len(temp_list)-1 - temp_list.index(3)],
        #                                                         kinds_of_values[list.index(3)]))
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def flush_test(cards, suit_cards, list):
    """
    A method to evaluate if the player has a flush.

    :param cards: The cards available for the player to evaluate.
    :param suit_cards: A list of the suits the player has.
    :param list: A list which specifies which cards are in the Hand.
    :return: Returns True and a PokerHand object if the player has a flush, otherwise False and None.
    """
    if list.count(1) >= 5:
        v = []
        for suit in Suits:
            if suit_cards.count(suit) >= 5:
                for card in cards:
                    if card.get_suit() == suit:
                        v.append(card.get_value())
                #print('You got a flush')
                hand_rank = PokerHandType.flush.value
                rank_value = ((suit, v[-1]))
                return True, PokerHand(hand_rank, rank_value)
        return False, None
    else:
        return False, None


def straight_test(list, value_cards):
    """
    A method to evaluate if the player has a straight.

    :param list: A list which specifies which cards are in the Hand.
    :param value_cards: The values of the cards in Hand.
    :return: Returns True and a PokerHand object if the player has a straight, otherwise False and None.
    """
    if list.count(1) >= 5:
        temp_list = list.copy()
        temp_list.reverse()
        for i, c in enumerate(temp_list):  # Starting point (high card)
            # Check if we have the value - k in the set of cards:
            if c > 0 and i < len(temp_list)-4:
                found_straight = True
                for k in range(1, 5):
                    if temp_list[i+k] == 0:
                        found_straight = False
                if found_straight:
                    hand_rank = PokerHandType.straight.value
                    rank_value = ((len(temp_list)+1 - i, value_cards[-1]))
                    #print("rank_value straight: ",len(temp_list)+1 - i)
                    return True, PokerHand(hand_rank, rank_value)
        return False, None
    else:
        return False, None


def three_of_a_kind_test(list, value_cards):
    """
    A method to evaluate if the player has a three of a kind.

    :param list: A list which specifies which cards are in the Hand.
    :param value_cards: The values of the cards in Hand.
    :return: Returns True and a PokerHand object if the player has a three of a kind, otherwise False and None.
    """
    if 3 in list:
        temp_list = list.copy()
        temp_list.reverse()
        #print('You got three of a kind in {}:s'.format(kinds_of_values[list.index(3)]))
        hand_rank = PokerHandType.three_of_a_kind.value
        rank_value = ((len(temp_list)+1 - temp_list.index(3), value_cards[-1], value_cards[-2]))
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def two_pairs_test(list, value_cards):
    """
    A method to evaluate if the player has two pairs.

    :param list: A list which specifies which cards are in the Hand.
    :param value_cards: The values of the cards in Hand.
    :return: Returns True and a PokerHand object if the player has two pairs, otherwise False and None.
    """
    if 2 in list and list.count(2) > 1:
        values = np.array(list)
        searchval = 2
        ii = np.where(values == searchval)[0]
        a = int(ii[-1])
        b = int(ii[-2])
        #print('You got two pairs in {}:s over {}:s'.format(kinds_of_values[a],
        #                                                  kinds_of_values[b]))
        hand_rank = PokerHandType.two_pair.value
        rank_value = ((a+2, b+2, value_cards[-1]))
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def one_pair_test(list):
    """
    A method to evaluate if the player has a pair.

    :param list: A list which specifies which cards are in the Hand.
    :return: Returns True and a PokerHand object if the player has a pair, otherwise False and None.
    """
    if list.count(2) == 1:
        if list.count(1) > 0:
            values = np.array(list)
            searchval = 1
            ii = np.where(values == searchval)[0]
            a = int(ii[-1])+2
            b = int(ii[-2])+2
            c = int(ii[-3])+2
            rank_value = ((list.index(2)+2, ((a, b, c))))
        else:
            rank_value = ((list.index(2)+2))
        hand_rank = PokerHandType.pair.value
        return True, PokerHand(hand_rank, rank_value)
    else:
        return False, None


def high_card_test(list):
    """
    A method to evaluate what the highest card in players Hand is.

    :param list: A list which specifies which cards are in the Hand.
    :return: Returns True and a PokerHand object with the highest cards in the players Hand.
    """
    hand_rank = PokerHandType.high_card.value
    values = np.array(list)
    searchval = 1
    ii = np.where(values == searchval)[0]
    a = []
    for value in ii:
        a.append(value+2)
    a.reverse()
    rank_value = tuple(a)
    return True, PokerHand(hand_rank, rank_value)


def create_bins_for_cards(cards):
    """
    A method that creates bins for a Hand which is then used in best_poker_hand.

    :param cards: All cards available for a player.
    :return: Returns some lists of values and suits.
    """
    num_of_cards = len(cards)
    # Initialize the bins
    list = [0]*13
    suit_cards = [0]*num_of_cards
    i = 0
    value_cards = []
    # Fill the bins
    for v in cards:
        list[v.get_value()-2] += 1
        suit_cards[i] = v.get_suit().value
        value_cards.append(v.get_value())
        i += 1
    value_cards.sort()
    return value_cards, list, suit_cards


class PokerHandType(enum.IntEnum):
    """
    A PokerHandType class which specifies which kind of PokerHand is worth the most.
    """
    high_card = 0
    pair = 1
    two_pair = 2
    three_of_a_kind = 3
    straight = 4
    flush = 5
    full_house = 6
    four_of_a_kind = 7
    straight_flush = 8


class PokerHand:
    """
    Uses PokerHandType to create an PokerHand object. Overrides some comparable operators for easier comparisons.
    """
    # Använder PokerHandType för PokerHand objektet
    def __init__(self, hand_rank, rank_value):
        # Value of hand
        self.hand_rank = hand_rank
        # Value of e.g. the pair
        self.rank_value = rank_value

    def __lt__(self, hand2):
        return (self.hand_rank, self.rank_value) < (hand2.hand_rank, hand2.rank_value)

