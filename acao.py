import time
from pynput import mouse, keyboard

# --- Configuração ---
START_STOP_KEY = keyboard.Key.f10
EMERGENCY_STOP_KEY = keyboard.Key.esc

class ActionRecorder:
    def __init__(self):
        self.actions = []
        self.is_recording = False
        self.start_time = None
        self.running = True

        # Controladores para repetir as ações
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

    def _add_action(self, action_type, **kwargs):
        """Adiciona uma ação à lista, calculando o delay desde a última ação."""
        if not self.is_recording:
            return

        # Calcula o tempo desde a última ação
        delay = time.time() - self.start_time
        
        action = {'type': action_type, 'delay': delay}
        action.update(kwargs)
        
        self.actions.append(action)
        print(f"Ação gravada: {action}")
        
        # Reseta o tempo para o próximo delay
        self.start_time = time.time()

    # --- Funções de Gravação (Callbacks dos Listeners) ---
    
    def on_press(self, key):
        # Lógica para parar a repetição de emergência
        if not self.running or key == EMERGENCY_STOP_KEY:
            self.running = False
            return False # Para o listener

        # Lógica para iniciar/parar a gravação
        if key == START_STOP_KEY:
            self.toggle_recording()
            return # Não grava a tecla F10 em si

        self._add_action('key_press', key=key)

    def on_release(self, key):
        if not self.running:
            return False
        self._add_action('key_release', key=key)

    def on_move(self, x, y):
        self._add_action('mouse_move', pos=(x, y))

    def on_click(self, x, y, button, pressed):
        self._add_action('mouse_click', pos=(x, y), button=button, pressed=pressed)

    def on_scroll(self, x, y, dx, dy):
        self._add_action('mouse_scroll', pos=(x, y), scroll=(dx, dy))

    # --- Lógica Principal ---
    
    def toggle_recording(self):
        """Inicia ou para a gravação."""
        self.is_recording = not self.is_recording
        if self.is_recording:
            print("▶️  Gravação iniciada! Pressione F10 novamente para parar.")
            # Limpa ações antigas e começa a contar o tempo
            self.actions = []
            self.start_time = time.time()
        else:
            print("⏹️  Gravação parada.")
            # Retorna False para parar os listeners de gravação
            return False
            
    def record(self):
        """Inicia os listeners para gravar as ações."""
        # Usamos 'with' para garantir que os listeners sejam parados corretamente
        with mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as mouse_listener:
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as keyboard_listener:
                keyboard_listener.join()
                mouse_listener.stop() # Garante que o listener do mouse pare também

    def replay(self, repetitions):
        """Repete as ações gravadas."""
        if not self.actions:
            print("Nenhuma ação foi gravada.")
            return

        print("\nIniciando a repetição em 5 segundos... (Pressione 'Esc' a qualquer momento para parar)")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        print("🚀 Começando a repetição!")

        # Inicia um listener separado apenas para a tecla de emergência
        stop_listener = keyboard.Listener(on_press=self.on_press)
        stop_listener.start()

        for i in range(repetitions):
            if not self.running:
                print("Repetição parada pelo usuário.")
                break
            
            print(f"\n--- Repetição {i + 1} de {repetitions} ---")
            
            for action in self.actions:
                if not self.running:
                    break
                
                # Espera o tempo gravado entre as ações
                time.sleep(action['delay'])

                action_type = action['type']
                if action_type == 'mouse_move':
                    self.mouse_controller.position = action['pos']
                elif action_type == 'mouse_click':
                    self.mouse_controller.position = action['pos']
                    if action['pressed']:
                        self.mouse_controller.press(action['button'])
                    else:
                        self.mouse_controller.release(action['button'])
                elif action_type == 'mouse_scroll':
                    self.mouse_controller.position = action['pos']
                    self.mouse_controller.scroll(action['scroll'][0], action['scroll'][1])
                elif action_type == 'key_press':
                    self.keyboard_controller.press(action['key'])
                elif action_type == 'key_release':
                    self.keyboard_controller.release(action['key'])
        
        stop_listener.stop()
        print("\n✅ Repetição concluída.")


if __name__ == "__main__":
    recorder = ActionRecorder()

    print("Pressione a tecla F10 para começar a gravar sua ação.")
    print("Quando terminar, pressione F10 novamente para parar.")
    
    # Fase de gravação
    recorder.record()

    # Fase de repetição
    while True:
        try:
            num_repetitions = int(input("\nDigite o número de vezes que deseja repetir a ação: "))
            if num_repetitions > 0:
                break
            else:
                print("Por favor, digite um número maior que zero.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
            
    recorder.replay(num_repetitions)