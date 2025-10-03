# main.py
from analyzer import HypixelItemAnalyzer

def main():
    """Função principal para iniciar a aplicação."""
    MODEL_PATH = r"C:\Users\gabri\Desktop\aprendendo\hypixel\comercialhelper-20250925T190655Z-1-001\comercialhelper\MODEL-3, after 20\weights\best.pt"
    
    try:
        analyzer = HypixelItemAnalyzer(yolo_model_path=MODEL_PATH)
        analyzer.setup_keyboard_listeners()
        analyzer.start_realtime_analysis()
    except Exception as e:
        print(f"Ocorreu um erro fatal: {e}")
        # Opcional: Adicionar um input para manter a janela do terminal aberta
        input("Pressione Enter para sair.")

if __name__ == "__main__":
    main()