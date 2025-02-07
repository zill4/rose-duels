from ursina import Entity, load_model, color, Vec3, destroy
from ursina.shaders import basic_lighting_shader, lit_with_shadows_shader
from constants import Board, BoardColors, Position, PieceRotation
from entities.pieces import piece_classes
from models import piece_models

def create_board(parent=None):
    """Create the chess board"""
    board_parent = Entity(parent=parent)
    
    # Create a darker base under the board
    base = Entity(
        parent=board_parent,
        model='cube',
        scale=(9, 0.5, 9),
        position=(3.5, -0.25, 3.5),
        color=color.rgb(0.1, 0.1, 0.1),  # Very dark base
        shader=lit_with_shadows_shader
    )
    
    # Create board squares with correct lighting
    for row in Board.ROWS:
        for col in Board.COLS:
            is_white = (row + col) % 2 == 0
            square = Entity(
                parent=board_parent,
                model='cube',
                collider='box',
                scale=(1, Board.THICKNESS, 1),
                position=(col, 0, row),
                color=BoardColors.WHITE if is_white else BoardColors.BLACK,
                shader=lit_with_shadows_shader
            )
            square.is_board_square = True
            square.grid_x = col
            square.grid_z = row
    
    return board_parent

def place_card_on_board(card, grid_x, grid_z, game_state):
    """Place a card and create corresponding piece on the board"""
    try:
        print(f"Placing card on board: {card}")
        print(f"Current player: {game_state.card_state.current_player}")
        
        # Create piece using card_data's piece type and properties
        piece = piece_classes[card.card_data.piece_type](
            is_black=card.card_data.is_black,
            grid_x=grid_x,
            grid_z=grid_z,
            model=load_model(piece_models[card.card_data.piece_type]['black' if card.card_data.is_black else 'white']),
            scale=piece_models[card.card_data.piece_type]['scale'],
            rotation=PieceRotation.BLACK if card.card_data.is_black else PieceRotation.WHITE,
            position=(grid_x, Position.GROUND_HEIGHT, grid_z),
            shader=basic_lighting_shader,
            double_sided=True,
            collider='box',  # For mouse interaction
            parent=game_state.board
        )
        
        # Force opacity and color settings after creation
        piece.alpha = 1.0
        piece.color = color.rgb(0.8, 0.1, 0.1) if card.card_data.is_black else color.white
        piece.collision = True
        piece.always_on_top = False  # Make sure it's not treated as UI
        
        # Enable mouse interaction explicitly
        piece.hovered = False
        piece.selected = False
        
        if piece:
            # Add to game state for update loop
            game_state.virtual_grid[grid_z][grid_x] = piece
            game_state.piece_entities.append(piece)
            
            # Create visual card on board
            is_black_turn = game_state.card_state.current_player == 'BLACK'
            card_rotation = (90, 180, 0) if is_black_turn else (90, 0, 0)
            
            board_card = Entity(
                parent=game_state.board,
                model='quad',
                texture=card.texture,
                scale=(0.8, 0.8),
                position=(grid_x, 0.01, grid_z),
                rotation=card_rotation,
                always_on_top=True
            )
            
            if not hasattr(game_state, 'board_cards'):
                game_state.board_cards = []
            game_state.board_cards.append(board_card)
            
            # Switch turns
            game_state.card_state.switch_turn()
            print(f"Turn switched to: {game_state.card_state.current_player}")
            
            return True
            
    except Exception as e:
        print(f"Error placing card: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_pieces(game_state, parent=None):
    """Create all chess pieces"""
    pieces_parent = Entity(parent=parent)
    
    for row in Board.ROWS:
        for col in Board.COLS:
            piece_type = Board.PIECE_POSITIONS[row][col]
            if piece_type:
                is_black = row < 4
                
                piece = piece_classes[piece_type](
                    parent=pieces_parent,
                    is_black=is_black,
                    grid_x=col,
                    grid_z=row,
                    model=load_model(piece_models[piece_type]['black' if is_black else 'white']),
                    scale=piece_models[piece_type]['scale'],
                    rotation=PieceRotation.BLACK if is_black else PieceRotation.WHITE,
                    position=(col, Position.GROUND_HEIGHT, row),
                    shader=basic_lighting_shader,
                    double_sided=True
                )
                
                game_state.virtual_grid[row][col] = piece
                game_state.piece_entities.append(piece)
    
    return pieces_parent 