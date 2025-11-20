from flask import Flask, send_from_directory, jsonify, request
import os
from game_engine import GameState

app = Flask(__name__, static_url_path='', static_folder='static')

# Global game state
game_state = GameState()
game_state.process_start_of_week() # Initialize first week

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(game_state.to_dict())

@app.route('/api/action', methods=['POST'])
def perform_action():
    global game_state
    data = request.json
    action_type = data.get('type')
    
    if action_type == 'hire_quant':
        success, message = game_state.hire_quant(data['name'], data['skill'], data['salary'])
        status = "ok" if success else "error"
        return jsonify({"status": status, "message": message, "state": game_state.to_dict()})
    elif action_type == 'start_research':
        game_state.start_research(data['style'], data['duration'])
    elif action_type == 'upgrade_infra':
        game_state.upgrade_infra(data['infra_type'])
    elif action_type == 'update_portfolio':
        game_state.update_portfolio(data['positions'])
    elif action_type == 'clear_event':
        game_state.clear_event()
    elif action_type == 'handle_infra_request':
        effect = data.get('effect', {})
        result = game_state.handle_infra_request(effect.get('type'), effect.get('infra'))
        return jsonify({"status": "ok", "message": result, "state": game_state.to_dict()})
    elif action_type == 'handle_reset_offer':
        decision = data.get('decision')
        message = game_state.handle_reset_offer(decision)
        return jsonify({"status": "ok", "message": message, "state": game_state.to_dict()})
    elif action_type == 'start_trivia_game':
        game_data = game_state.start_market_trivia()
        return jsonify({"status": "ok", "game_data": game_data})
    elif action_type == 'submit_trivia_game':
        result = game_state.submit_market_trivia(data.get('choice'))
        return jsonify({"status": "ok", "result": result, "state": game_state.to_dict()})
    elif action_type == 'start_mini_game':
        game_data = game_state.generate_sharpe_challenge()
        return jsonify({"status": "ok", "game_data": game_data})
    elif action_type == 'submit_mini_game':
        result = game_state.submit_sharpe_guess(data['guess'])
        return jsonify({"status": "ok", "result": result, "state": game_state.to_dict()})
    elif action_type == 'start_mm_game':
        game_data = game_state.start_market_making()
        return jsonify({"status": "ok", "game_data": game_data})
    elif action_type == 'submit_mm_action':
        result = game_state.submit_market_making(data['spread'])
        return jsonify({"status": "ok", "result": result, "state": game_state.to_dict()})
    elif action_type == 'save_game':
        save_name = data.get('name', 'savegame')
        game_state.save(save_name)
        return jsonify({"status": "ok", "message": f"Saved '{save_name}'", "state": game_state.to_dict()})
    elif action_type == 'list_saves':
        saves = GameState.list_saves()
        return jsonify({"status": "ok", "saves": saves})
    elif action_type == 'load_game':
        save_name = data.get('name', 'savegame')
        game_state = GameState.load(save_name)
        return jsonify({"status": "ok", "state": game_state.to_dict(), "message": f"Loaded '{save_name}'"})
    elif action_type == 'restart_game':
        game_state.restart()
        return jsonify({"status": "ok", "state": game_state.to_dict()})
    elif action_type == 'hire_infra':
        success, msg = game_state.hire_infra_specialist(data.get('name', ''), int(data.get('skill', 50)))
        state = game_state.to_dict()
        status = "ok" if success else "error"
        return jsonify({"status": status, "message": msg, "state": state})
    elif action_type == 'fire_staff':
        success, msg = game_state.fire_staff(data.get('staff_type'), data.get('name'))
        state = game_state.to_dict()
        status = "ok" if success else "error"
        return jsonify({"status": status, "message": msg, "state": state})
    
    return jsonify({"status": "ok", "state": game_state.to_dict()})

@app.route('/api/next_turn', methods=['POST'])
def next_turn():
    game_state.process_end_of_week()
    game_state.process_start_of_week()
    return jsonify({"status": "ok", "state": game_state.to_dict()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
