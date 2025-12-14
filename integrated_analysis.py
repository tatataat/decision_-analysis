import math
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import pandas as pd

def erlang_b(A, c):
    """
    Формула Эрланга B
    A - трафик в эрлангах
    c - количество обслуживающих устройств
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
        
        if prob <= target_probability:
            return c, prob
        
        c += 1
        
        # Защита от бесконечного цикла
        if c > 100:
            return None, 1.0

def calculate_traffic_parameters(avg_conversations_per_hour, avg_duration_minutes):
    """
    Вычисление параметров трафика
    """
    avg_duration_hours = avg_duration_minutes / 60
    traffic_erlangs = avg_conversations_per_hour * avg_duration_hours
    return traffic_erlangs

class ChatBotSimulator:
    def __init__(self, arrival_rate_per_hour=10, service_time_minutes=5, max_sessions=None):
        self.arrival_rate_per_hour = arrival_rate_per_hour
        self.service_time_minutes = service_time_minutes
        self.max_sessions = max_sessions
        self.reset_stats()
        
    def reset_stats(self):
        self.current_sessions = 0
        self.operator_calls = 0
        self.total_requests = 0
        self.session_history = []
        self.operator_call_times = []
    
    def simulate_period(self, hours=24):
        """
        Симуляция работы в течение заданного периода
        """
        self.reset_stats()
        
        total_minutes = hours * 60
        current_time = 0
        
        # Генерируем времена поступления запросов по процессу Пуассона
        inter_arrival_times = []
        for _ in range(int(self.arrival_rate_per_hour * hours * 3)):  # Запас запросов
            inter_arrival_time = random.expovariate(self.arrival_rate_per_hour / 60)
            inter_arrival_times.append(inter_arrival_time)
        
        request_idx = 0
        next_arrival_time = 0  # Начинаем сразу с первого запроса
        
        while current_time < total_minutes:
            # Обрабатываем все запросы, поступившие в этот момент
            while request_idx < len(inter_arrival_times) and next_arrival_time <= current_time:
                self.total_requests += 1
                
                if self.max_sessions is None or self.current_sessions < self.max_sessions:
                    # Чат-бот может обработать запрос
                    self.current_sessions += 1
                    
                    # Время завершения обслуживания (по экспоненциальному закону)
                    service_time = random.expovariate(1.0 / self.service_time_minutes)
                    end_time = current_time + service_time
                    self.session_history.append({
                        'start_time': current_time,
                        'end_time': end_time,
                        'handled_by_bot': True
                    })
                else:
                    # Чат-бот перегружен, вызываем оператора
                    self.operator_calls += 1
                
                # Переход к следующему запросу
                request_idx += 1
                if request_idx < len(inter_arrival_times):
                    next_arrival_time += inter_arrival_times[request_idx]
                else:
                    next_arrival_time = float('inf')
                    break
            
            # Обработка завершившихся сессий
            completed_sessions = [s for s in self.session_history if s['end_time'] <= current_time]
            for session in completed_sessions:
                self.session_history.remove(session)
                self.current_sessions -= 1
            
            current_time += 0.1  # Маленький шаг времени для точности
        
        # Обрабатываем оставшиеся сессии
        while self.session_history:
            current_time += 1
            completed_sessions = [s for s in self.session_history if s['end_time'] <= current_time]
            for session in completed_sessions:
                self.session_history.remove(session)
                self.current_sessions -= 1
        
        return self.get_statistics()
    
    def get_statistics(self):
        stats = {
            'total_requests': self.total_requests,
            'operator_calls': self.operator_calls,
            'requests_handled_by_bot': self.total_requests - self.operator_calls,
            'operator_call_probability': self.operator_calls / self.total_requests if self.total_requests > 0 else 0,
            'efficiency': (self.total_requests - self.operator_calls) / self.total_requests if self.total_requests > 0 else 0
        }
        return stats

def integrated_analysis():
    """
    Комплексный анализ с использованием обоих методов
    """
    print("Комплексный анализ влияния чат-бота на нагрузку оператора")
    print("="*70)
    
    # Параметры системы
    avg_conversations_per_hour = 10
    avg_duration_minutes = 5
    target_probability = 0.05  # 5%
    
    traffic = calculate_traffic_parameters(avg_conversations_per_hour, avg_duration_minutes)
    print(f"Параметры системы:")
    print(f"- Среднее количество обращений в час: {avg_conversations_per_hour}")
    print(f"- Средняя продолжительность сессии: {avg_duration_minutes} мин")
    print(f"- Трафик в эрлангах: {traffic:.2f}")
    print(f"- Целевая вероятность вызова оператора: {target_probability:.2%}")
    print()
    
    # Теоретический расчет по формуле Эрланга B
    print("1. Теоретический расчет (формула Эрланга B):")
    theoretical_sessions, theoretical_prob = find_sessions_for_probability(target_probability, traffic)
    print(f"   - Оптимальное количество сессий: {theoretical_sessions}")
    print(f"   - Теоретическая вероятность вызова оператора: {theoretical_prob:.4f}")
    print(f"   - Теоретическая эффективность: {(1-theoretical_prob):.2%}")
    print()
    
    # Симуляционный анализ
    print("2. Симуляционный анализ:")
    print("   Запуск многократных симуляций для проверки теоретических результатов...")
    
    simulation_runs = 20
    sim_results = []
    
    for max_sess in range(1, 15):
        total_stats = {'operator_call_probability': 0, 'efficiency': 0}
        
        for run in range(simulation_runs):
            simulator = ChatBotSimulator(
                arrival_rate_per_hour=avg_conversations_per_hour,
                service_time_minutes=avg_duration_minutes,
                max_sessions=max_sess
            )
            stats = simulator.simulate_period(hours=24)
            total_stats['operator_call_probability'] += stats['operator_call_probability']
            total_stats['efficiency'] += stats['efficiency']
        
        avg_operator_prob = total_stats['operator_call_probability'] / simulation_runs
        avg_efficiency = total_stats['efficiency'] / simulation_runs
        
        sim_results.append({
            'max_sessions': max_sess,
            'avg_operator_call_probability': avg_operator_prob,
            'avg_efficiency': avg_efficiency
        })
        
        if max_sess == theoretical_sessions:
            print(f"   - При {max_sess} сессиях (теор. оптимум):")
            print(f"     * Средняя вероятность вызова оператора: {avg_operator_prob:.4f}")
            print(f"     * Средняя эффективность: {avg_efficiency:.2%}")
    
    # Поиск оптимального значения по результатам симуляции
    sim_optimal = next((r for r in sim_results if r['avg_operator_call_probability'] <= target_probability), sim_results[-1])
    print(f"   - Симуляционный оптимум: {sim_optimal['max_sessions']} сессий")
    print(f"   - Симуляционная вероятность вызова оператора: {sim_optimal['avg_operator_call_probability']:.4f}")
    print()
    
    # Сравнение теории и симуляции
    print("3. Сравнение теоретических и симуляционных результатов:")
    comparison_df = pd.DataFrame(sim_results[:10])  # Первые 10 результатов для таблицы
    comparison_df['theoretical_prob'] = comparison_df['max_sessions'].apply(
        lambda x: erlang_b(traffic, x)
    )
    comparison_df['difference'] = abs(comparison_df['avg_operator_call_probability'] - comparison_df['theoretical_prob'])
    
    print(comparison_df[['max_sessions', 'theoretical_prob', 'avg_operator_call_probability', 'difference']].round(4))
    print()
    
    # Построение графиков
    plot_integrated_results(sim_results, theoretical_prob, target_probability)
    
    # Анализ нагрузки на оператора
    print("4. Анализ изменения нагрузки на оператора:")
    print(f"   - Без чат-бота: 100% нагрузки")
    print(f"   - С чат-ботом ({theoretical_sessions} сессий): {theoretical_prob:.2%} нагрузки")
    print(f"   - Снижение нагрузки: {(1-theoretical_prob)*100:.2f}%")
    print()
    
    # Вывод рекомендаций
    print("5. Рекомендации по внедрению чат-бота:")
    print(f"   - Рекомендуемое количество одновременно поддерживаемых сессий: {theoretical_sessions}")
    print(f"   - Ожидаемая вероятность вызова оператора: {theoretical_prob:.2%}")
    print(f"   - Ожидаемая эффективность автоматизации: {(1-theoretical_prob)*100:.2f}%")
    print(f"   - При таком числе сессий чат-бот будет самостоятельно обрабатывать {(1-theoretical_prob)*100:.2f}% запросов")

def plot_integrated_results(sim_results, theoretical_prob, target_probability):
    """
    Построение графиков интегрированного анализа
    """
    max_sessions = [r['max_sessions'] for r in sim_results]
    sim_probs = [r['avg_operator_call_probability'] for r in sim_results]
    sim_efficiencies = [r['avg_efficiency'] for r in sim_results]
    
    # Вычисляем теоретические значения для графика
    traffic = calculate_traffic_parameters(10, 5)
    theoretical_probs = [erlang_b(traffic, c) for c in max_sessions]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # График 1: Сравнение теоретической и симуляционной вероятностей
    ax1.plot(max_sessions, theoretical_probs, 'b-o', label='Теоретическая (Эрланг B)', linewidth=2)
    ax1.plot(max_sessions, sim_probs, 'r-s', label='Симуляционная', linewidth=2)
    ax1.axhline(y=target_probability, color='g', linestyle='--', label=f'Цель ({target_probability})', alpha=0.7)
    ax1.set_xlabel('Количество одновременных сессий')
    ax1.set_ylabel('Вероятность вызова оператора')
    ax1.set_title('Сравнение теоретической и симуляционной моделей')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # График 2: Эффективность системы
    ax2.plot(max_sessions, sim_efficiencies, 'g-^', label='Эффективность', linewidth=2)
    ax2.set_xlabel('Количество одновременных сессий')
    ax2.set_ylabel('Эффективность')
    ax2.set_title('Эффективность обработки запросов чат-ботом')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # График 3: Разница между теорией и практикой
    differences = [abs(t - s) for t, s in zip(theoretical_probs, sim_probs)]
    ax3.plot(max_sessions, differences, 'm-o', label='Разница (теория - симуляция)', linewidth=2)
    ax3.set_xlabel('Количество одновременных сессий')
    ax3.set_ylabel('Разница вероятностей')
    ax3.set_title('Различие между теоретическими и симуляционными результатами')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # График 4: Увеличение эффективности
    improvements = [(1-e)*100 for e in sim_probs]
    ax4.plot(max_sessions, improvements, 'c-d', label='% автоматизированных запросов', linewidth=2)
    ax4.set_xlabel('Количество одновременных сессий')
    ax4.set_ylabel('Процент автоматизированных запросов (%)')
    ax4.set_title('Уровень автоматизации в зависимости от числа сессий')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/workspace/integrated_analysis_results.png', dpi=300, bbox_inches='tight')
    print(f"\nГрафики комплексного анализа сохранены в файл: integrated_analysis_results.png")

if __name__ == "__main__":
    integrated_analysis()