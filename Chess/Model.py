from enum import Enum

class Game:
  """A chess game with game state information."""

  def __init__(self, positions=None):
    """Create a new game with default starting positions."""
    if positions is None:
      self._positions = self._init_positions()
    else:
      self._position = positions

    # true if white's turn
    self.turn = True

  def _init_positions(self):
    """Default starting positions."""
    result = dict()
    for file in range(8):
      result[1, file] = Pawn(Position(1, file), Colour.WHITE, False)
      result[6, file] = Pawn(Position(6, file), Colour.BLACK, False)

    return result

class Position:
  """Represent a position on the board."""
  def __init__(self, rank, file):
    """Create a new position with the given rank and file."""
    self._rank = rank
    self._file = file

  def get_rank(self):
    """Return this position's rank."""
    return self._rank

  def get_file(self):
    """Return this position's file."""
    return self._file

class Piece:
  """Represent a piece on the board."""
  def __init__(self, position, colour):
    """Initialise a new piece with the given position."""
    self._position = position
    self._colour = colour

  def move(self, position: Position):
    """(Abstract) move the piece to the new position.
    Parameters:
      position:  the position to move to

    Return True if a valid move and False otherwise.
    """
    pass

class Pawn(Piece):
  """A pawn piece."""
  def __init__(self, position: Position, colour, en_passant: bool):
    """Initialise a new pawn piece."""
    super().__init__(position, colour)
    self._en_passant = en_passant

  def move(self, position):
    # Check the given move is valid
    if self._position.get_rank() - position.get_rank() not in [1, 2]:
      return False # too far vertically
    # TODO
    self._position = position 
    return True

class Colour(Enum):
  WHITE = 0
  BLACK = 1

