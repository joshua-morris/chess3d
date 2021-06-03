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
    self.playing = True
    self.focused = None

  def is_playing(self):
    return self.playing

  def get_focused(self):
    return self.focused

  def set_focused(self, position):
    if self._positions.get(position) is not None:
      self.focused = position

  def unfocus(self):
    self.focused = None

  def _init_positions(self):
    """Default starting positions."""
    result = []
    for file in range(8):
      result.append(Pawn(Position(1, file), Colour.WHITE, False))
      result.append(Pawn(Position(6, file), Colour.BLACK, False))

    result.append(Rook(Position(0, 0), Colour.WHITE))
    result.append(Rook(Position(7, 0), Colour.WHITE))
    result.append(Rook(Position(0, 7), Colour.BLACK))
    result.append(Rook(Position(7, 7), Colour.BLACK))

    result.append(Knight(Position(1, 0), Colour.WHITE))
    result.append(Knight(Position(6, 0), Colour.WHITE))
    result.append(Knight(Position(1, 7), Colour.BLACK))
    result.append(Knight(Position(6, 7), Colour.BLACK))

    result.append(Bishop(Position(2, 0), Colour.WHITE))
    result.append(Bishop(Position(5, 0), Colour.WHITE))
    result.append(Bishop(Position(2, 7), Colour.BLACK))
    result.append(Bishop(Position(5, 7), Colour.BLACK))

    result.append(Queen(Position(3, 0), Colour.WHITE))
    result.append(Queen(Position(3, 7), Colour.BLACK))

    result.append(King(Position(4, 0), Colour.WHITE))
    result.append(King(Position(4, 7), Colour.BLACK))

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

class Rook(Piece):
  pass

class Knight(Piece):
  pass

class Bishop(Piece):
  pass

class Queen(Piece):
  pass

class King(Piece):
  pass

class Colour(Enum):
  WHITE = 0
  BLACK = 1

