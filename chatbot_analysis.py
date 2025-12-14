import math
import matplotlib.pyplot as plt
import numpy as np

def erlang_b(A, c):
    """
    Формула Эрланга B
    A - трафик в эрлангах (интенсивность поступления * среднее время обслуживания)
    c - количество обслуживающих устройств (в данном случае - количество поддерживаемых сессий)
    """
    if c == 0:
        return 1.0
    
    numerator = (A ** c) / math.factorial(c)
    denominator = sum([(A ** i) / math.factorial(i) for i in range(c + 1)])
    
    if denominator == 0:
        return 1.0
    
    return numerator / denominator

def find_sessions_for_probability(target_probability, traffic_intensity):
    """
    Найти количество сессий, при котором вероятность вызова оператора 
    не превышает заданного значения
    """
    c = 1
    while True:
        prob = erlang_b(traffic_intensity, c)
        print(f"Количество сессий: {c}, Вероятность вызова оператора: {prob:.4f}")
        
        if prob <= target_probability:
            return c
        
        c += 1
        
        # Защита от бесконечного цикла
        if c > 100:
            print("Превышено максимальное количество итераций")
            return None

def calculate_traffic_parameters(avg_conversations_per_hour, avg_duration_minutes):
    """
    Вычисление параметров трафика
    avg_conversations_per_hour - среднее количество разговоров в час
    avg_duration_minutes - средняя продолжительность разговора в минутах
    """
    # Переводим среднюю продолжительность в часы
    avg_duration_hours = avg_duration_minutes / 60
    
    # Трафик в эрлангах
    traffic_erlangs = avg_conversations_per_hour * avg_duration_hours
    
    return traffic_erlangs

def analyze_scenarios():
    """
    Анализ различных сценариев нагрузки
    """
    print("\nАнализ различных сценариев:")
    print("-" * 50)
    
    scenarios = [
        {"name": "Низкая нагрузка", "conversations": 5, "duration": 3},
        {"name": "Средняя нагрузка", "conversations": 10, "duration": 5},
        {"name": "Высокая нагрузка", "conversations": 20, "duration": 8},
        {"name": "Пиковая нагрузка", "conversations": 30, "duration": 10}
    ]
    
    results = []
    
    for scenario in scenarios:
        traffic = calculate_traffic_parameters(
            scenario["conversations"], 
            scenario["duration"]
        )
        
        optimal_sessions = find_sessions_for_probability(0.05, traffic)
        
        if optimal_sessions:
            final_prob = erlang_b(traffic, optimal_sessions)
            results.append({
                "scenario": scenario["name"],
                "traffic": traffic,
                "sessions": optimal_sessions,
                "probability": final_prob
            })
            
            print(f"\n{scenario['name']}:")
            print(f"  Трафик: {traffic:.2f} эрлангов")
            print(f"  Оптимальное количество сессий: {optimal_sessions}")
            print(f"  Фактическая вероятность вызова оператора: {final_prob:.4f}")
    
    return results

def plot_analysis(results):
    """
    Построение графиков анализа
    """
    if not results:
        print("Нет данных для построения графиков")
        return
    
    scenarios = [r["scenario"] for r in results]
    sessions = [r["sessions"] for r in results]
    probabilities = [r["probability"] for r in results]
    traffic = [r["traffic"] for r in results]
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # График количества сессий
    ax1.bar(scenarios, sessions, color='skyblue')
    ax1.set_title('Оптимальное количество сессий')
    ax1.set_ylabel('Количество сессий')
    ax1.tick_params(axis='x', rotation=45)
    
    # График вероятностей
    ax2.bar(scenarios, probabilities, color='lightgreen')
    ax2.set_title('Вероятность вызова оператора')
    ax2.set_ylabel('Вероятность')
    ax2.axhline(y=0.05, color='red', linestyle='--', label='Целевой уровень (0.05)')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    # График трафика
    ax3.bar(scenarios, traffic, color='orange')
    ax3.set_title('Трафик в эрлангах')
    ax3.set_ylabel('Трафик (эрланги)')
    ax3.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('/workspace/chatbot_analysis_results.png', dpi=300, bbox_inches='tight')
    print("\nГрафики сохранены в файл: chatbot_analysis_results.png")

def compare_efficiency(initial_operator_load, bot_handled_sessions, operator_called_probability):
    """
    Сравнение эффективности до и после внедрения чат-бота
    """
    print(f"\nАнализ эффективности:")
    print("-" * 30)
    
    # Операторская нагрузка после внедрения бота
    reduced_load = initial_operator_load * operator_called_probability
    
    print(f"Исходная нагрузка на оператора: 100%")
    print(f"Вероятность вызова оператора: {operator_called_probability:.2%}")
    print(f"Сниженная нагрузка на оператора: {reduced_load:.2%}")
    print(f"Экономия нагрузки: {(initial_operator_load - reduced_load):.2%}")
    
    return reduced_load

# Пример использования
if __name__ == "__main__":
    print("Анализ нагрузки чат-бота и определение количества поддерживаемых сессий")
    print("="*70)
    
    # Примерные параметры для туристического сайта
    avg_conversations_per_hour = 10  # Среднее количество обращений в час
    avg_duration_minutes = 5         # Средняя длительность сессии в минутах
    
    traffic = calculate_traffic_parameters(avg_conversations_per_hour, avg_duration_minutes)
    print(f"Трафик в эрлангах: {traffic:.2f}")
    
    target_prob = 0.05  # Целевая вероятность вызова оператора (5%)
    print(f"\nЦелевая вероятность вызова оператора: {target_prob}")
    
    optimal_sessions = find_sessions_for_probability(target_prob, traffic)
    
    if optimal_sessions:
        print(f"\nОптимальное количество одновременно поддерживаемых сессий: {optimal_sessions}")
        final_prob = erlang_b(traffic, optimal_sessions)
        print(f"Фактическая вероятность вызова оператора: {final_prob:.4f}")
        
        # Анализ эффективности
        compare_efficiency(1.0, optimal_sessions, final_prob)
    
    # Анализ различных сценариев
    results = analyze_scenarios()
    
    # Построение графиков
    try:
        plot_analysis(results)
    except ImportError:
        print("\nMatplotlib не установлен, пропускаем построение графиков")
    
    print(f"\nВывод:")
    print(f"При оптимальном количестве поддерживаемых сессий ({optimal_sessions}),")
    print(f"вероятность вызова оператора составляет {final_prob:.4f},")
    print(f"что ниже целевого значения {target_prob}.")
    print(f"Это позволяет значительно снизить нагрузку на операторов.")