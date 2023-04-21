"""Estimate the strength of nnue eval.

requirements:
  chess
  pandas

installation:
  pip install chess
  pip install pandas
"""


import subprocess

import chess
import chess.pgn
import chess.engine
import pandas as pd

pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 800)


def nnue_eval(enginefn, epd):
    """Find the best move with highest eval.

    Run engine, setup position and send eval command.   
    Save eval and legal moves from the given epd. 
    """
    board = chess.Board(epd)
    epds, moves, scores = [], [], []

    engine = subprocess.Popen(enginefn, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True, bufsize=1,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    
    engine.stdin.write('uci\n')
    for eline in iter(engine.stdout.readline, ''):
        line = eline.strip()
        if 'uciok' in line:
            break

    engine.stdin.write('isready\n')
    for eline in iter(engine.stdout.readline, ''):
        line = eline.strip()
        if 'readyok' in line:
            break

    # Visit all moves and get the eval.    
    for move in board.legal_moves:
        b = board.copy()
        san_move = b.san(move)
        b.push(move)

        # If side to move is in check, don't evaluate.
        if b.is_check():
            continue

        fen = b.fen()
        engine.stdin.write(f'position fen {fen}\n')
        engine.stdin.write('eval\n')

        pawn_value_wpov = None
        for eline in iter(engine.stdout.readline, ''):
            line = eline.strip()

            # NNUE evaluation        +0.19 (white side)
            if 'NNUE evaluation' in line and not 'info string' in line:
                value = line.split('NNUE evaluation')[1]
                value = value.split('(white side)')[0].strip()
                pawn_value_wpov = float(value)

                epds.append(epd)
                moves.append(san_move)

                score = round(100*pawn_value_wpov)

                # Convert to spov.
                if b.turn == chess.BLACK:
                    score = -score
                score = -score  # move was pushed
                     
                scores.append(score)
                break
            
    engine.stdin.write('quit\n')
            
    df = pd.DataFrame({'epds': epds, 'moves': moves, 'scores': scores})
    df = df.sort_values(by=['scores'], ascending=[False])

    return  df


def main():
    max_games = 5
    movetimesec = 1
    pgnfn = r'F:\project\pgn\tatamast23.pgn'
    enginefn = r'F:\Chess\Engines\stockfish\stockfish_15.1_win_x64_popcnt\stockfish-windows-2022-x86-64-modern.exe'
    gcnt = 0

    engine = chess.engine.SimpleEngine.popen_uci(enginefn)

    alldf = []

    with open(pgnfn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            gcnt += 1
            print(f'game {gcnt}')

            wp = game.headers['White']
            bp = game.headers['Black']

            data = []

            for node in game.mainline():
                board = node.parent.board()
                gmove = node.move
                gmove_san = board.san(gmove)
                gply = board.ply()
                epd = board.epd()
                fmvn = board.fullmove_number

                gmove_is_check = True if '+' in gmove_san else False

                if board.is_check():
                    continue

                # Don't analyze moves below 20.
                if gply < 40:
                    continue

                legal_moves = board.legal_moves.count()

                # Analyze this board with the engine. Get all the legal moves evaluation.
                info = engine.analyse(board, chess.engine.Limit(time=movetimesec), multipv=legal_moves)
                epds, scores, moves = [], [], []
                top_move_is_tactical = False
                top1_move = None
                for i in range(min(legal_moves, board.legal_moves.count())):
                    score = info[i]['score'].relative.score(mate_score=32000)
                    pv = info[i]['pv']
                    move = pv[0]
                    san_move = board.san(move)

                    if i == 0:
                        top1_move = san_move

                    # Exclude tactical moves.
                    if i <= 5 and ('+' in san_move or 'x' in san_move or '=' in san_move):
                        top_move_is_tactical = True
                        break

                    epds.append(epd)
                    scores.append(score)
                    moves.append(san_move)

                if not top_move_is_tactical and not gmove_is_check:
                    top_df = pd.DataFrame({'epds': epds, 'moves': moves, 'scores': scores})
                    print(f'top_df:\n{top_df}\n')

                    nnue_df = nnue_eval(enginefn, epd)
                    nnue_df = nnue_df.reset_index(drop=True)
                    print(f'nnue_df:\n{nnue_df}\n')

                    print(f'game move:\n{gmove_san}\n')

                    # Get top nnue score based from top_df data.
                    top1_score = top_df['scores'].iloc[0]
                    top_nnue_move = nnue_df['moves'].iloc[0]
                    top_nnue_move_score_from_top_df = top_df.loc[top_df.moves == top_nnue_move]['scores'].iloc[0]

                    # Get actual score of game move based from top_df data.
                    gmove_score_from_top_df = top_df.loc[top_df.moves == gmove_san]['scores'].iloc[0]

                    print(board)
                    print()
                    print(epd)
                    print(f'top_1_score: {top1_score}, top_nnue_score: {top_nnue_move_score_from_top_df}, gmove_score: {gmove_score_from_top_df}')
                    print()

                    if board.turn == chess.WHITE:
                        data.append([gcnt, epd, fmvn, wp, gmove_san, gmove_score_from_top_df, top1_move, top1_score, top_nnue_move, top_nnue_move_score_from_top_df])
                    else:
                        data.append([gcnt, epd, fmvn, bp, gmove_san, gmove_score_from_top_df, top1_move, top1_score, top_nnue_move, top_nnue_move_score_from_top_df])

                    if abs(top1_score) > 500 and abs(gmove_score_from_top_df) > 500:
                        break

            # Save to dataframe.
            df = pd.DataFrame(data, columns=['GameNum', 'Epd', 'MoveNum', 'Name', 'GameMove', 'GameMoveScore', 'EngineMove', 'EngineScore', 'NNUEMove', 'NNUEScore'])
            alldf.append(df)

            if gcnt >= max_games:
                break

    engine.quit()

    # Save data to csv file. Print average error in cp.
    df = pd.concat(alldf, ignore_index=True)
    df.to_csv('data-1.csv', index=False)
    print(df)

    df_error = df.copy()

    df_error['HumanError'] = abs(df_error['EngineScore'] - df_error['GameMoveScore'])
    df_error['NNUEError'] = abs(df_error['EngineScore'] - df_error['NNUEScore'])
    print(df_error)

    average_human_error = df_error['HumanError'].mean().round()
    average_nnue_error = df_error['NNUEError'].mean().round()

    print(f'AveHumanError: {average_human_error}')
    print(f'AveNNUEError: {average_nnue_error}')


if __name__ == '__main__':
    main()
